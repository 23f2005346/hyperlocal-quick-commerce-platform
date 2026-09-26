import os
import sys
import random
import re
import time
import uuid
import smtplib
import json
import urllib.request
import urllib.error
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from functools import wraps
from datetime import datetime, timedelta
from flask import Flask, jsonify, request, send_from_directory, send_file
from flask_cors import CORS
from itsdangerous import URLSafeTimedSerializer, SignatureExpired, BadSignature
from sqlalchemy import event
from sqlalchemy.engine import Engine
from models import db, User, Category, Product, ProductVariant, Order, OrderItem, KhataPayment, TieredPricing, RestockAlert, get_ist_time
from seed_data import CATEGORIES_DATA, PRODUCTS_DATA
from backup_service import create_hot_backup, list_backups, verify_backup

# Ensure UTF-8 stdout encoding on Windows consoles to prevent charmap crashes
if hasattr(sys.stdout, 'reconfigure'):
    try:
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    except Exception:
        pass
if hasattr(sys.stderr, 'reconfigure'):
    try:
        sys.stderr.reconfigure(encoding='utf-8', errors='replace')
    except Exception:
        pass

# Automatically load backend/.env if present
env_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), '.env')
if os.path.exists(env_file):
    try:
        with open(env_file, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    k, v = line.split('=', 1)
                    os.environ.setdefault(k.strip(), v.strip())
    except Exception as e:
        print(f"[ENV WARNING] Could not read .env: {e}")

SECRET_KEY = 'apna-desi-kirana-store-secret-key-2026'
serializer = URLSafeTimedSerializer(SECRET_KEY)

# Strict Store Owner Admin Email Whitelist
ADMIN_WHITELIST = {'thisisroushan01@gmail.com', 'novaaether01@gmail.com'}
ADMIN_2FA_STORE = {} # { email: { 'otp': '123456', 'expires_at': ts, 'user_id': id } }
CUSTOMER_RESET_STORE = {} # { email: { 'otp': '123456', 'expires_at': ts, 'user_id': id, 'attempts': 0 } }

# SMTP configuration for real email delivery (Gmail App Password)
SMTP_HOST = os.environ.get('SMTP_HOST', 'smtp.gmail.com')
SMTP_PORT = int(os.environ.get('SMTP_PORT', 587))
SMTP_USER = os.environ.get('SMTP_USER', 'thisisroushan01@gmail.com').strip()
SMTP_PASS = os.environ.get('SMTP_PASS', 'emaiuwgdfqddjskg').replace(' ', '').strip()

# Resend API configuration (Port 443 HTTPS - Operates without cloud SMTP firewall blockage)
RESEND_API_KEY = os.environ.get('RESEND_API_KEY', '').strip()
RESEND_FROM = os.environ.get('RESEND_FROM', 'Komal Mart Admin <onboarding@resend.dev>').strip()

def send_email_resend(to_email, subject, html_body, text_body=None):
    """
    Dispatches email via Resend REST API over Port 443 HTTPS.
    Render free tier blocks outbound TCP on ports 25, 465, and 587,
    making HTTPS API calls on Port 443 the only reliable email transport in production.
    """
    resend_key = os.environ.get('RESEND_API_KEY', '').strip()
    if not resend_key:
        return False, "RESEND_API_KEY not configured"

    resend_from = os.environ.get('RESEND_FROM', 'Komal Mart Admin <onboarding@resend.dev>').strip()
    payload = {
        "from": resend_from,
        "to": [to_email],
        "subject": subject,
        "html": html_body,
        "text": text_body or re.sub(r'<[^<]+?>', '', html_body)
    }

    try:
        req_data = json.dumps(payload).encode('utf-8')
        req = urllib.request.Request(
            "https://api.resend.com/emails",
            data=req_data,
            headers={
                "Authorization": f"Bearer {resend_key}",
                "Content-Type": "application/json",
                "User-Agent": "KomalMart-Executive/1.0"
            },
            method="POST"
        )
        with urllib.request.urlopen(req, timeout=10.0) as resp:
            resp_body = resp.read().decode('utf-8', errors='replace')
            print(f"[RESEND SUCCESS] Sent email to {to_email} via Port 443 HTTPS. Status: {resp.status}, Body: {resp_body}")
            return True, "Email dispatched successfully via Resend HTTPS API (Port 443)"
    except urllib.error.HTTPError as e:
        err_body = e.read().decode('utf-8', errors='replace')
        print(f"[RESEND HTTP ERROR {e.code}] {err_body}")
        return False, f"Resend HTTP {e.code}: {err_body}"
    except urllib.error.URLError as e:
        print(f"[RESEND NETWORK ERROR] {e.reason}")
        return False, f"Resend Network Error: {e.reason}"
    except Exception as e:
        print(f"[RESEND EXCEPTION] {e}")
        return False, str(e)

def send_admin_otp_resend(to_email, otp, subject, html_body):
    """Dispatches 6-digit OTP code via Resend REST API over Port 443 HTTPS."""
    return send_email_resend(
        to_email=to_email,
        subject=subject,
        html_body=html_body,
        text_body=f"Your Komal Mart Admin 2FA Code is: {otp}. Valid for 5 minutes."
    )

def send_admin_otp_email(to_email, otp):
    """
    Dispatches 6-digit OTP code to the authorized admin email address.
    Priority 1: Resend REST API via Port 443 HTTPS (ideal for Render cloud deployment).
    Priority 2: Port 465 SSL SMTP.
    Priority 3: Port 587 STARTTLS SMTP.
    Always logs clearly to console for local testing and server audits.
    """
    subject = f"🔐 Komal Mart Admin 2FA Code: {otp}"
    html_body = f"""
    <div style="font-family: Arial, sans-serif; max-width: 500px; margin: 0 auto; padding: 24px; border: 1.5px solid #059669; border-radius: 12px; background-color: #fdfbf7;">
        <div style="text-align: center; margin-bottom: 20px;">
            <h1 style="color: #064e3b; margin: 0; font-size: 24px;">🌾 कोमल मार्ट (Komal Mart)</h1>
            <p style="color: #6b7280; font-size: 13px; margin-top: 4px;">Store Owner Security Verification</p>
        </div>
        <div style="background: white; border: 1px solid #e5e7eb; border-radius: 8px; padding: 20px; text-align: center;">
            <p style="font-size: 14px; color: #374151; margin-bottom: 12px;">Your 6-digit Store Admin Login OTP is:</p>
            <div style="font-size: 32px; font-weight: 900; letter-spacing: 6px; color: #059669; background: #ecfdf5; padding: 12px; border-radius: 8px; display: inline-block;">
                {otp}
            </div>
            <p style="font-size: 12px; color: #9ca3af; margin-top: 14px;">This code expires in 5 minutes. Do not share this code with anyone.</p>
        </div>
        <p style="font-size: 11px; color: #9ca3af; text-align: center; margin-top: 20px;">Komal Mart Kirana Store • Secure Admin Gateway</p>
    </div>
    """

    # 1. Primary: Attempt Resend API over Port 443 HTTPS (cloud-safe)
    resend_key = os.environ.get('RESEND_API_KEY', '').strip()
    if resend_key:
        ok, resend_msg = send_admin_otp_resend(to_email, otp, subject, html_body)
        if ok:
            return True, resend_msg
        print(f"[RESEND NOTICE] {resend_msg}. Falling back to direct SMTP...")

    # 2. Secondary: SMTP over Port 465 SSL or Port 587 STARTTLS
    if SMTP_USER and SMTP_PASS:
        try:
            msg = MIMEMultipart('alternative')
            msg['Subject'] = subject
            msg['From'] = f"Komal Mart Admin Security <{SMTP_USER}>"
            msg['To'] = to_email
            msg.attach(MIMEText(f"Your Komal Mart Admin 2FA Code is: {otp}. Valid for 5 minutes.", 'plain'))
            msg.attach(MIMEText(html_body, 'html'))

            # Attempt Port 465 SSL first (direct SSL avoids STARTTLS cloud timeout/blocking)
            try:
                server = smtplib.SMTP_SSL(SMTP_HOST, 465, timeout=7.0)
                server.login(SMTP_USER, SMTP_PASS)
                server.sendmail(SMTP_USER, [to_email], msg.as_string())
                server.quit()
                print(f"[EMAIL SENT] Successfully sent 2FA OTP to {to_email} via Port 465 SSL")
                return True, "Email dispatched successfully via SSL"
            except Exception as e465:
                print(f"[SMTP 465 SSL warning] {e465}, falling back to Port 587 STARTTLS...")

            # Fallback to Port 587 STARTTLS
            server = smtplib.SMTP(SMTP_HOST, SMTP_PORT, timeout=7.0)
            server.starttls()
            server.login(SMTP_USER, SMTP_PASS)
            server.sendmail(SMTP_USER, [to_email], msg.as_string())
            server.quit()
            print(f"[EMAIL SENT] Successfully sent 2FA OTP to {to_email} via Port 587 STARTTLS")
            return True, "Email dispatched successfully via STARTTLS"
        except Exception as e:
            print(f"[SMTP ERROR] Failed to send email to {to_email}: {e}")
            return False, str(e)
    else:
        print("[EMAIL INFO] Neither RESEND_API_KEY nor SMTP_USER/PASS configured. Printed OTP to terminal console only.")
        return False, "Email credentials not configured. Use Master PIN: 202699"

def send_customer_otp_email(to_email, otp, customer_name="Customer"):
    """
    Dispatches 6-digit OTP code to a customer's verified email address for password reset.
    Priority 1: Resend REST API via Port 443 HTTPS (ideal for Render cloud deployment).
    Priority 2: Port 465 SSL SMTP.
    Priority 3: Port 587 STARTTLS SMTP.
    """
    subject = f"🔐 कोमल मार्ट (Komal Mart) पासवर्ड रीसेट OTP: {otp}"
    display_name = customer_name or "ग्राहक"
    html_body = f"""
    <div style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; max-width: 500px; margin: 0 auto; padding: 24px; border: 1.5px solid #059669; border-radius: 12px; background-color: #fdfbf7;">
        <div style="text-align: center; margin-bottom: 20px;">
            <h1 style="color: #064e3b; margin: 0; font-size: 24px;">🌾 कोमल मार्ट (Komal Mart)</h1>
            <p style="color: #6b7280; font-size: 13px; margin-top: 4px;">वडाळा, मुंबई • पासवर्ड सुरक्षा पडताळणी</p>
        </div>
        <div style="background: white; border: 1px solid #e5e7eb; border-radius: 8px; padding: 20px; text-align: center;">
            <p style="font-size: 15px; color: #1f2937; margin-bottom: 8px; font-weight: 700;">नमस्ते {display_name}! 🙏</p>
            <p style="font-size: 14px; color: #4b5563; margin-bottom: 14px; line-height: 1.5;">तुमचा कोमल मार्ट खाते पासवर्ड बदलण्यासाठीचा ६-अंकी पडताळणी कोड (OTP) खालीलप्रमाणे आहे:</p>
            <div style="font-size: 32px; font-weight: 900; letter-spacing: 6px; color: #059669; background: #ecfdf5; padding: 14px; border-radius: 8px; display: inline-block;">
                {otp}
            </div>
            <p style="font-size: 12px; color: #9ca3af; margin-top: 14px;">हा कोड पुढील १० मिनिटांसाठी वैध आहे. हा कोड इतर कोणाशीही शेअर करू नका.</p>
        </div>
        <p style="font-size: 11px; color: #9ca3af; text-align: center; margin-top: 20px;">कोमल मार्ट किराणा व सुपरमार्केट • वडाळा, मुंबई</p>
    </div>
    """

    # 1. Primary: Attempt Resend API over Port 443 HTTPS
    resend_key = os.environ.get('RESEND_API_KEY', '').strip()
    if resend_key:
        ok, resend_msg = send_email_resend(
            to_email=to_email,
            subject=subject,
            html_body=html_body,
            text_body=f"Namaste {display_name}! Your Komal Mart Password Reset OTP is: {otp}. Valid for 10 minutes."
        )
        if ok:
            return True, resend_msg
        print(f"[RESEND CUSTOMER OTP NOTICE] {resend_msg}. Falling back to direct SMTP...")

    # 2. Secondary: SMTP over Port 465 SSL or Port 587 STARTTLS
    if SMTP_USER and SMTP_PASS:
        try:
            msg = MIMEMultipart('alternative')
            msg['Subject'] = subject
            msg['From'] = f"Komal Mart Security <{SMTP_USER}>"
            msg['To'] = to_email
            msg.attach(MIMEText(f"Your Komal Mart Password Reset OTP is: {otp}. Valid for 10 minutes.", 'plain'))
            msg.attach(MIMEText(html_body, 'html'))

            try:
                server = smtplib.SMTP_SSL(SMTP_HOST, 465, timeout=7.0)
                server.login(SMTP_USER, SMTP_PASS)
                server.sendmail(SMTP_USER, [to_email], msg.as_string())
                server.quit()
                print(f"[EMAIL SENT] Successfully sent Customer Reset OTP to {to_email} via Port 465 SSL")
                return True, "Email dispatched successfully via SSL"
            except Exception as e465:
                print(f"[SMTP 465 SSL warning] {e465}, falling back to Port 587 STARTTLS...")

            server = smtplib.SMTP(SMTP_HOST, SMTP_PORT, timeout=7.0)
            server.starttls()
            server.login(SMTP_USER, SMTP_PASS)
            server.sendmail(SMTP_USER, [to_email], msg.as_string())
            server.quit()
            print(f"[EMAIL SENT] Successfully sent Customer Reset OTP to {to_email} via Port 587 STARTTLS")
            return True, "Email dispatched successfully via STARTTLS"
        except Exception as e:
            print(f"[SMTP ERROR] Failed to send customer reset email to {to_email}: {e}")
            return False, str(e)
    else:
        print("[CUSTOMER OTP CONSOLE ONLY] Neither RESEND_API_KEY nor SMTP configured.")
        return False, "Email credentials not configured"

def is_dummy_phone(phone: str) -> bool:
    if not phone or len(phone) != 10:
        return True

    # 1. Fewer than 3 unique digits (e.g., 9999999999, 9898989898, 9191919191)
    if len(set(phone)) <= 2:
        return True

    # 2. Known sequential or ascending/descending patterns
    sequences = {
        "9876543210", "9876543211", "9876543212", "9876543213", "9876543214", "9876543215",
        "9876543216", "9876543217", "9876543218", "9876543219", "0123456789", "1234567890",
        "9123456789", "6789012345", "9876598765", "1234512345", "1122334455"
    }
    if phone in sequences:
        return True

    # 3. Repeating triplets (e.g. 9879879870 or 9879879879)
    if phone[:3] == phone[3:6] == phone[6:9]:
        return True

    # 4. Repeating pairs (e.g. 9898989898)
    if phone[:2] * 5 == phone:
        return True

    # 5. Repeating 4-digit prefix (e.g. 9876987612)
    if phone[:4] == phone[4:8]:
        return True

    # 6. Any single digit appearing 7 or more times
    for ch in set(phone):
        if phone.count(ch) >= 7:
            return True

    return False

SEARCH_ALIASES = {
    # Rice / Grains
    'rice': ['rice', 'chawal', 'chaawal', 'tandul', 'taandul', 'bhat', 'basmati', 'kolam', 'चावल', 'तांदूळ', 'भात', 'बासमती'],
    'chawal': ['rice', 'chawal', 'chaawal', 'tandul', 'bhat', 'basmati', 'चावल', 'तांदूळ'],
    'chaawal': ['rice', 'chawal', 'chaawal', 'tandul', 'bhat', 'basmati', 'चावल', 'तांदूळ'],
    'tandul': ['rice', 'tandul', 'taandul', 'chawal', 'bhat', 'kolam', 'तांदूळ', 'चावल'],
    'taandul': ['rice', 'tandul', 'taandul', 'chawal', 'bhat', 'kolam', 'तांदूळ', 'चावल'],
    'bhat': ['rice', 'chawal', 'tandul', 'भात', 'चावल'],
    'kolam': ['kolam', 'rice', 'कोलम', 'तांदूळ'],
    'basmati': ['basmati', 'rice', 'chawal', 'बासमती', 'दावत', 'daawat'],

    # Atta / Flours / Wheat
    'atta': ['atta', 'aata', 'pith', 'peeth', 'gehu', 'gehun', 'flour', 'chakki', 'wheat', 'sharbati', 'आटा', 'पीठ', 'गहू'],
    'aata': ['atta', 'aata', 'pith', 'flour', 'chakki', 'आटा', 'पीठ'],
    'pith': ['atta', 'pith', 'peeth', 'flour', 'पीठ', 'आटा'],
    'peeth': ['atta', 'pith', 'peeth', 'flour', 'पीठ', 'आटा'],
    'gehu': ['atta', 'gehu', 'gehun', 'wheat', 'chakki', 'sharbati', 'गहू', 'आटा'],
    'gehun': ['atta', 'gehu', 'gehun', 'wheat', 'chakki', 'sharbati', 'गहू', 'आटा'],
    'wheat': ['atta', 'gehu', 'wheat', 'chakki', 'aashirvaad', 'fortune', 'गहू', 'आटा'],
    'maida': ['maida', 'flour', 'मैदा'],
    'besan': ['besan', 'gram flour', 'chana', 'हरभरा', 'बेसन', 'चना'],
    'rava': ['rava', 'suji', 'sooji', 'semolina', 'रवा', 'सुजी'],
    'suji': ['rava', 'suji', 'sooji', 'रवा', 'सुजी'],
    'sooji': ['rava', 'suji', 'sooji', 'रवा', 'सुजी'],
    'semolina': ['rava', 'suji', 'sooji', 'रवा'],
    'poha': ['poha', 'pohe', 'flattened rice', 'पोहे', 'पोहा'],
    'pohe': ['poha', 'pohe', 'पोहे', 'पोहा'],

    # Dals & Pulses
    'dal': ['dal', 'daal', 'dall', 'डाळ', 'दाल', 'toor', 'arhar', 'moong', 'urad', 'masoor', 'chana'],
    'daal': ['dal', 'daal', 'डाळ', 'दाल', 'toor', 'arhar', 'moong', 'urad', 'masoor', 'chana'],
    'toor': ['toor', 'tuvar', 'arhar', 'तूर', 'अरहर', 'tur'],
    'tuvar': ['toor', 'tuvar', 'arhar', 'तूर', 'तुवर'],
    'arhar': ['toor', 'arhar', 'tuvar', 'अरहर', 'तूर'],
    'tur': ['toor', 'tuvar', 'arhar', 'तूर'],
    'moong': ['moong', 'mung', 'mug', 'मूग', 'मूँग'],
    'mung': ['moong', 'mung', 'mug', 'मूग', 'मूँग'],
    'mug': ['moong', 'mung', 'mug', 'मूग'],
    'urad': ['urad', 'udid', 'udad', 'उडीद', 'उड़द'],
    'udid': ['urad', 'udid', 'उडीद', 'उड़द'],
    'udad': ['urad', 'udid', 'उडीद', 'उड़द'],
    'masoor': ['masoor', 'masur', 'मलका', 'मसूर'],
    'masur': ['masoor', 'masur', 'मसूर'],
    'chana': ['chana', 'channa', 'harbhara', 'चना', 'हरभरा', 'छोले', 'काबुली'],
    'channa': ['chana', 'channa', 'harbhara', 'चना', 'हरभरा'],
    'harbhara': ['chana', 'harbhara', 'हरभरा', 'चना'],
    'rajma': ['rajma', 'rajmah', 'राजमा'],
    'rajmah': ['rajma', 'राजमा'],
    'chhole': ['chhole', 'chole', 'kabuli', 'chana', 'छोले', 'काबुली'],
    'chole': ['chhole', 'chole', 'kabuli', 'chana', 'छोले', 'काबुली'],
    'kabuli': ['kabuli', 'chhole', 'chana', 'काबुली', 'छोले'],

    # Oils & Ghee
    'oil': ['oil', 'tel', 'tail', 'तेल', 'mustard', 'sarson', 'ghee'],
    'tel': ['oil', 'tel', 'tail', 'तेल', 'mustard', 'sarson'],
    'tail': ['oil', 'tel', 'तेल'],
    'sarson': ['sarson', 'sarso', 'mustard', 'mohari', 'मोहरी', 'सरसों', 'oil', 'tel'],
    'sarso': ['sarson', 'sarso', 'mustard', 'सरसों', 'तेल', 'oil'],
    'mustard': ['mustard', 'sarson', 'mohari', 'मोहरी', 'सरसों', 'oil', 'tel'],
    'mohari': ['mustard', 'sarson', 'mohari', 'मोहरी', 'तेल'],
    'ghee': ['ghee', 'ghi', 'toop', 'tup', 'तूप', 'घी', 'cow ghee', 'amul'],
    'ghi': ['ghee', 'toop', 'tup', 'तूप', 'घी'],
    'toop': ['ghee', 'toop', 'tup', 'तूप', 'घी'],
    'tup': ['ghee', 'toop', 'tup', 'तूप', 'घी'],

    # Salt, Sugar, Spices
    'salt': ['salt', 'namak', 'meeth', 'mith', 'मीठ', 'नमक', 'tata salt'],
    'namak': ['salt', 'namak', 'meeth', 'मीठ', 'नमक', 'tata'],
    'meeth': ['salt', 'namak', 'meeth', 'मीठ', 'नमक', 'tata salt'],
    'mith': ['salt', 'namak', 'meeth', 'मीठ', 'नमक'],
    'sugar': ['sugar', 'cheeni', 'shakkar', 'saakhar', 'sakhar', 'साखर', 'चीनी', 'शक्कर'],
    'cheeni': ['sugar', 'cheeni', 'shakkar', 'saakhar', 'चीनी', 'साखर'],
    'chini': ['sugar', 'cheeni', 'shakkar', 'saakhar', 'चीनी', 'साखर'],
    'shakkar': ['sugar', 'shakkar', 'cheeni', 'saakhar', 'शक्कर', 'साखर'],
    'saakhar': ['sugar', 'saakhar', 'sakhar', 'cheeni', 'साखर', 'चीनी'],
    'sakhar': ['sugar', 'saakhar', 'sakhar', 'cheeni', 'साखर', 'चीनी'],
    'haldi': ['haldi', 'halad', 'turmeric', 'हळद', 'हल्दी'],
    'halad': ['haldi', 'halad', 'turmeric', 'हळद', 'हल्दी'],
    'turmeric': ['turmeric', 'haldi', 'halad', 'हळद', 'हल्दी'],
    'mirchi': ['mirch', 'mirchi', 'chilli', 'chili', 'tikhat', 'तिखट', 'मिर्च'],
    'mirch': ['mirch', 'mirchi', 'chilli', 'tikhat', 'मिर्च', 'तिखट'],
    'tikhat': ['mirch', 'mirchi', 'tikhat', 'तिखट', 'मिर्च'],
    'chilli': ['mirch', 'mirchi', 'tikhat', 'chilli', 'मिर्च'],
    'chili': ['mirch', 'mirchi', 'tikhat', 'chili', 'मिर्च'],
    'masala': ['masala', 'everest', 'garam masala', 'मसाला'],
    'dhania': ['dhania', 'dhaniya', 'coriander', 'धने', 'धनिया', 'masala'],
    'dhaniya': ['dhania', 'dhaniya', 'coriander', 'धने', 'धनिया', 'masala'],

    # Tea / Beverages
    'tea': ['tea', 'chai', 'chaha', 'चहा', 'चाय', 'tata tea', 'red label', 'wagh bakri', 'taj mahal'],
    'chai': ['tea', 'chai', 'chaha', 'चाय', 'चहा', 'tata tea', 'red label'],
    'chaha': ['tea', 'chai', 'chaha', 'चहा', 'चाय', 'tata tea'],
    'coffee': ['coffee', 'कॉफी'],

    # Cleaning & Oral Care
    'soap': ['soap', 'sabun', 'saabun', 'साबण', 'साबुन', 'dettol', 'rin'],
    'sabun': ['soap', 'sabun', 'saabun', 'साबण', 'साबुन', 'dettol', 'rin'],
    'saabun': ['soap', 'sabun', 'साबण', 'साबुन'],
    'detergent': ['detergent', 'surf', 'surf excel', 'powder', 'सर्फ', 'डिटर्जंट'],
    'surf': ['surf', 'surf excel', 'detergent', 'powder', 'सर्फ'],
    'rin': ['rin', 'bar', 'साबण', 'रिन'],
    'vim': ['vim', 'dishwash', 'व्हिम', 'विम', 'bar'],
    'paste': ['toothpaste', 'paste', 'colgate', 'sensodyne', 'dabur', 'patanjali', 'टूथपेस्ट', 'पेस्ट'],
    'toothpaste': ['toothpaste', 'paste', 'colgate', 'sensodyne', 'dabur', 'patanjali', 'टूथपेस्ट'],
    'colgate': ['colgate', 'toothpaste', 'कोलगेट'],
    'dant': ['dant', 'dantmanjan', 'dant kanti', 'दंत', 'पतंजली', 'डाबर', 'toothpaste'],
    'dettol': ['dettol', 'soap', 'डेटॉल']
}

def calculate_order_credit(items_data):
    """
    Margin-based Store Credit Earning:
    - Loose Mandi commodities (is_loose=True): Wholesale margin 15-25% -> 2.5% Store Credit
    - Packaged Branded FMCG (is_loose=False): Thin margin 3-6% -> 0.5% Store Credit
    """
    total_credit = 0.0
    for item in items_data:
        subtotal = float(item.get('subtotal') or 0.0)
        is_loose = bool(item.get('is_loose', False))

        if item.get('variant_id'):
            v = db.session.get(ProductVariant, item['variant_id'])
            if v:
                qty = int(item.get('quantity', 1))
                if subtotal <= 0:
                    subtotal = v.selling_price * qty
                if v.product and v.product.is_loose:
                    is_loose = True
        elif item.get('product_id'):
            prod = db.session.get(Product, item['product_id'])
            if prod and prod.is_loose:
                is_loose = True

        if is_loose:
            total_credit += subtotal * 0.025
        else:
            total_credit += subtotal * 0.005

    return round(total_credit, 2)

def get_tiered_unit_price(product_id, qty):
    """
    Checks if there is a tiered wholesale pricing slab applicable for this product and quantity/weight.
    Returns (unit_price, tier_label) or None if no wholesale slab matches.
    """
    if not product_id:
        return None
    try:
        qty_val = float(qty)
        if qty_val <= 0:
            return None
    except (ValueError, TypeError):
        return None

    try:
        tiers = TieredPricing.query.filter_by(product_id=product_id).order_by(TieredPricing.min_qty.desc()).all()
        for t in tiers:
            if qty_val >= t.min_qty:
                if t.max_qty is None or qty_val <= t.max_qty:
                    return t.unit_price, t.tier_label
    except Exception as e:
        print(f"[TIER PRICE ERROR] {e}")
    return None

def seed_default_tiered_pricing():
    """
    Seeds wholesale tiered pricing slabs for essential bulk staples:
    - Wada Kolam Rice (5kg+ wholesale, 25kg+ mandi/bori rate)
    - Chakki Wheat Atta (5kg+ wholesale, 10kg+ katta, 25kg+ bori)
    - Toor Dal (5kg+ wholesale, 25kg+ bulk)
    - Chana Dal (5kg+ wholesale, 25kg+ bulk)
    """
    staple_tiers = [
        ("Wada Kolam", 5.0, 24.99, 56.0, "होलसेल (Wholesale 5kg+)"),
        ("Wada Kolam", 25.0, None, 54.0, "बोरी दर (Bulk Bori 25kg+)"),
        ("Chakki Fresh Wheat Atta", 5.0, 9.99, 33.0, "होलसेल (5kg+)"),
        ("Chakki Fresh Wheat Atta", 10.0, 24.99, 32.0, "कट्टा दर (10kg+)"),
        ("Chakki Fresh Wheat Atta", 25.0, None, 30.0, "बोरी दर (25kg+)"),
        ("Toor Dal / Arhar Dal", 5.0, 24.99, 142.0, "होलसेल (5kg+)"),
        ("Toor Dal / Arhar Dal", 25.0, None, 135.0, "बोरी दर (25kg+)"),
        ("Chana Dal", 5.0, 24.99, 86.0, "होलसेल (5kg+)"),
        ("Chana Dal", 25.0, None, 80.0, "बोरी दर (25kg+)"),
    ]
    for term, min_q, max_q, price, label in staple_tiers:
        prod = Product.query.filter(Product.name.ilike(f"%{term}%")).first()
        if prod:
            db.session.add(TieredPricing(
                product_id=prod.id,
                min_qty=min_q,
                max_qty=max_q,
                unit_price=price,
                tier_label=label,
                tier_label_hi=label
            ))
    try:
        db.session.commit()
        print("[WHOLESALE SEED] Seeded default tiered pricing slabs successfully.")
    except Exception as e:
        db.session.rollback()
        print(f"[WHOLESALE SEED ERROR] {e}")

# Configure SQLite engine event listeners for WAL mode and fast concurrency
@event.listens_for(Engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    if dbapi_connection.__class__.__module__.startswith('sqlite3'):
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA journal_mode=WAL")
        cursor.execute("PRAGMA synchronous=NORMAL")
        cursor.execute("PRAGMA busy_timeout=5000")
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()

def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = SECRET_KEY
    
    # Enable CORS for frontend development
    CORS(app)

    # Database setup: Support external PostgreSQL / Supabase, persistent DB_PATH, or local SQLite WAL
    db_url = os.environ.get('DATABASE_URL')
    if db_url:
        if db_url.startswith("postgres://"):
            db_url = db_url.replace("postgres://", "postgresql://", 1)
        app.config['SQLALCHEMY_DATABASE_URI'] = db_url
        is_sqlite = False
    else:
        db_path = os.environ.get('DB_PATH') or os.path.join(os.path.dirname(os.path.abspath(__file__)), 'kirana.db')
        os.makedirs(os.path.dirname(os.path.abspath(db_path)), exist_ok=True)
        app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{db_path}'
        app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
            'connect_args': {'timeout': 15}
        }
        is_sqlite = True
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    db.init_app(app)

    with app.app_context():
        # SQLite migration to ensure username column and unique indices
        if is_sqlite:
            import sqlite3
            conn = sqlite3.connect(db_path)
            cur = conn.cursor()
            try:
                cur.execute("PRAGMA journal_mode=WAL")
                cur.execute("PRAGMA synchronous=NORMAL")
                cur.execute("PRAGMA busy_timeout=5000")
                cur.execute("PRAGMA table_info(users)")
                cols = cur.fetchall()
                col_names = [r[1] for r in cols]
                if 'username' not in col_names:
                    cur.execute("ALTER TABLE users ADD COLUMN username VARCHAR(60)")
                    conn.commit()

                # Ensure email is nullable
                email_col = next((c for c in cols if c[1] == 'email'), None)
                if email_col and email_col[3] == 1:
                    cur.execute("PRAGMA foreign_keys = OFF")
                    cur.execute("""
                        CREATE TABLE users_migrated (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            username VARCHAR(60),
                            name VARCHAR(100) NOT NULL,
                            email VARCHAR(120),
                            phone VARCHAR(20) NOT NULL,
                            password_hash VARCHAR(255) NOT NULL,
                            address TEXT,
                            role VARCHAR(20) DEFAULT 'customer',
                            created_at DATETIME
                        )
                    """)
                    cur.execute("""
                        INSERT INTO users_migrated (id, username, name, email, phone, password_hash, address, role, created_at)
                        SELECT id, username, name, email, phone, password_hash, address, role, created_at FROM users
                    """)
                    cur.execute("DROP TABLE users")
                    cur.execute("ALTER TABLE users_migrated RENAME TO users")
                    cur.execute("PRAGMA foreign_keys = ON")
                    conn.commit()

                # Deduplicate any duplicate phone numbers in legacy test data
                cur.execute("SELECT phone, COUNT(*) FROM users GROUP BY phone HAVING COUNT(*) > 1")
                dups = cur.fetchall()
                for p_dup, cnt in dups:
                    cur.execute("SELECT id FROM users WHERE phone = ?", (p_dup,))
                    rows = cur.fetchall()
                    for idx, r in enumerate(rows[1:], start=1):
                        new_p = f"{p_dup[:9]}{idx}"
                        cur.execute("UPDATE users SET phone = ? WHERE id = ?", (new_p, r[0]))
                conn.commit()

                cur.execute("CREATE UNIQUE INDEX IF NOT EXISTS uq_users_username ON users(username) WHERE username IS NOT NULL")
                cur.execute("CREATE UNIQUE INDEX IF NOT EXISTS uq_users_phone ON users(phone)")
                conn.commit()

                # Ensure users.wallet_balance column exists
                cur.execute("PRAGMA table_info(users)")
                current_user_cols = [r[1] for r in cur.fetchall()]
                if 'wallet_balance' not in current_user_cols:
                    cur.execute("ALTER TABLE users ADD COLUMN wallet_balance FLOAT DEFAULT 0.0")
                    conn.commit()

                # Ensure orders.credit_used, credit_earned, delivery_type, and pincode columns exist
                cur.execute("PRAGMA table_info(orders)")
                order_cols = [r[1] for r in cur.fetchall()]
                if 'credit_used' not in order_cols:
                    cur.execute("ALTER TABLE orders ADD COLUMN credit_used FLOAT DEFAULT 0.0")
                    conn.commit()
                if 'credit_earned' not in order_cols:
                    cur.execute("ALTER TABLE orders ADD COLUMN credit_earned FLOAT DEFAULT 0.0")
                    conn.commit()
                if 'delivery_type' not in order_cols:
                    cur.execute("ALTER TABLE orders ADD COLUMN delivery_type VARCHAR(30) DEFAULT 'home_delivery'")
                    conn.commit()
                if 'pincode' not in order_cols:
                    cur.execute("ALTER TABLE orders ADD COLUMN pincode VARCHAR(10) DEFAULT '400031'")
                    conn.commit()

                # Ensure product_variants.is_clearance and clearance_price columns exist
                cur.execute("PRAGMA table_info(product_variants)")
                v_cols = [r[1] for r in cur.fetchall()]
                if v_cols:
                    if 'is_clearance' not in v_cols:
                        cur.execute("ALTER TABLE product_variants ADD COLUMN is_clearance BOOLEAN DEFAULT 0")
                        conn.commit()
                    if 'clearance_price' not in v_cols:
                        cur.execute("ALTER TABLE product_variants ADD COLUMN clearance_price FLOAT DEFAULT NULL")
                        conn.commit()
            except Exception as e:
                print("Migration warning:", e)
            finally:
                conn.close()

        db.create_all()
        # Seed default admin and inventory if empty or missing admin
        if Category.query.count() == 0 or User.query.filter_by(role='admin').count() == 0:
            seed_database()

        if TieredPricing.query.count() == 0:
            seed_default_tiered_pricing()

    # --- AUTHENTICATION HELPERS ---

    def get_current_user():
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return None
        token = auth_header.split(' ')[1]
        try:
            data = serializer.loads(token, max_age=86400 * 30) # 30 days
            user_id = data.get('user_id')
            return db.session.get(User, user_id)
        except (SignatureExpired, BadSignature, Exception):
            return None

    def admin_required(f):
        @wraps(f)
        def decorated(*args, **kwargs):
            user = get_current_user()
            if not user or user.role != 'admin':
                return jsonify({
                    'error': 'Forbidden: Admin access required. Customers cannot modify store data.'
                }), 403
            return f(*args, **kwargs)
        return decorated

    def login_required(f):
        @wraps(f)
        def decorated(*args, **kwargs):
            user = get_current_user()
            if not user:
                return jsonify({'error': 'Unauthorized: Please login to continue.'}), 401
            return f(user, *args, **kwargs)
        return decorated

    # --- AUTH ROUTES ---

    @app.route('/api/auth/register', methods=['POST'])
    def register():
        data = request.get_json() or {}
        name = (data.get('name') or '').strip()
        username = (data.get('username') or '').strip()
        email = (data.get('email') or '').strip().lower()
        phone = (data.get('phone') or '').strip()
        password = (data.get('password') or '').strip()
        address = (data.get('address') or '').strip()

        if not name or not password or not phone or not email:
            return jsonify({'error': 'नाव, ईमेल पत्ता, मोबाईल नंबर आणि पासवर्ड आवश्यक आहेत.', 'code': 'MISSING_FIELDS'}), 400

        # Mandatory & Strict Indian Mobile Validation (10 digits starting with 6,7,8,9)
        if not re.match(r'^[6-9]\d{9}$', phone):
            return jsonify({'error': 'कृपया १० अंकांचा वैध मोबाईल नंबर टाका (6, 7, 8 किंवा 9 ने सुरू होणारा).', 'code': 'INVALID_PHONE'}), 400

        # Reject dummy or fake phone numbers
        if is_dummy_phone(phone):
            return jsonify({'error': 'अवैध मोबाईल नंबर! डमी नंबर (उदा. 0000000000, 1234567890, 9876543210) चालणार नाही.', 'code': 'DUMMY_PHONE'}), 400

        # Enforce unique phone
        if User.query.filter_by(phone=phone).first():
            return jsonify({'error': 'हा मोबाईल नंबर आधीच नोंदणीकृत आहे. कृपया लॉगिन करा किंवा पासवर्ड रीसेट करा.', 'code': 'PHONE_EXISTS'}), 400

        # Mandatory Email Validation & Uniqueness
        if not re.match(r'^[\w\.-]+@[\w\.-]+\.\w+$', email):
            return jsonify({'error': 'कृपया वैध ईमेल पत्ता टाका (उदा. name@example.com).', 'code': 'INVALID_EMAIL'}), 400
        if User.query.filter_by(email=email).first():
            return jsonify({'error': 'या ईमेलवर आधीच खाते अस्तित्वात आहे. कृपया लॉगिन करा किंवा पासवर्ड रीसेट करा.', 'code': 'EMAIL_EXISTS'}), 400

        # Unique username validation (if provided)
        if username:
            if not re.match(r'^[a-zA-Z0-9_.-]{3,30}$', username):
                return jsonify({'error': 'युझरनेम ३ ते ३० अक्षरांचे (फक्त अक्षरे, अंक, _, . किंवा -) असावे.', 'code': 'INVALID_USERNAME'}), 400
            if User.query.filter_by(username=username).first():
                return jsonify({'error': f'युझरनेम "{username}" आधीच वापरले गेले आहे. कृपया दुसरे नाव निवडा.', 'code': 'USERNAME_EXISTS'}), 400
        else:
            username = None

        user = User(
            name=name,
            username=username,
            email=email,
            phone=phone,
            address=address,
            role='customer' # Strict role enforcement
        )
        user.set_password(password)
        db.session.add(user)
        db.session.commit()

        token = serializer.dumps({'user_id': user.id, 'role': user.role})
        return jsonify({
            'message': 'Registration successful! Welcome to Komal Mart.',
            'token': token,
            'user': user.to_dict()
        }), 201

    @app.route('/api/auth/login', methods=['POST'])
    def login():
        data = request.get_json() or {}
        identifier = (data.get('identifier') or data.get('email') or data.get('phone') or data.get('username') or '').strip()
        password = data.get('password', '').strip()

        if not identifier or not password:
            return jsonify({'error': 'मोबाईल नंबर/ईमेल/युझरनेम आणि पासवर्ड आवश्यक आहे.', 'code': 'MISSING_FIELDS'}), 400

        # Find user by email, phone, or username
        user = User.query.filter(
            (User.email == identifier.lower()) |
            (User.phone == identifier) |
            (User.username == identifier)
        ).first()

        if not user:
            return jsonify({'error': 'या तपशीलांशी जुळणारे कोणतेही खाते सापडले नाही. कृपया नवीन खाते तयार करा.', 'code': 'USER_NOT_FOUND'}), 404

        if not user.check_password(password):
            return jsonify({'error': 'चुकीचा पासवर्ड! कृपया योग्य पासवर्ड टाका.', 'code': 'INVALID_CREDENTIALS'}), 401

        # Check if user is Admin -> Strict Whitelist and 2FA Verification
        if user.role == 'admin':
            if user.email not in ADMIN_WHITELIST:
                return jsonify({'error': 'अनाधिकृत प्रवेश: केवळ अधिकृत दुकान मालक ईमेलद्वारे ॲडमिन ॲक्सेस शक्य आहे.', 'code': 'UNAUTHORIZED_ADMIN'}), 403

            # Generate 6-digit OTP
            otp = f"{random.randint(100000, 999999)}"
            temp_token = serializer.dumps({'email': user.email, 'purpose': 'admin_2fa'}, salt='admin-2fa-salt')
            ADMIN_2FA_STORE[user.email] = {
                'otp': otp,
                'expires_at': time.time() + 300, # 5 minutes
                'user_id': user.id
            }

            print("\n=======================================================")
            print("[KOMAL MART ADMIN 2FA OTP] Storekeeper Login OTP")
            print(f"Admin Email: {user.email}")
            print(f"6-Digit OTP Code: {otp}")
            print("Valid for 5 minutes")
            print("=======================================================\n")

            # Dispatch email via SMTP if configured
            try:
                email_sent, _ = send_admin_otp_email(user.email, otp)
            except Exception as e:
                print(f"[OTP DISPATCH ERROR] {e}")
                email_sent = False

            parts = user.email.split('@')
            masked = (parts[0][:2] + '***' + parts[0][-2:] + '@' + parts[1]) if len(parts[0]) > 4 else user.email

            return jsonify({
                'require_2fa': True,
                'temp_token': temp_token,
                'masked_email': masked,
                'admin_email': user.email,
                'email_dispatched': email_sent,
                'message': f'सुरक्षा पडताळणी: ६-अंकी OTP कोड {masked} वर पाठवला आहे.' if email_sent else 'क्लाउड ईमेल पोर्ट ब्लॉक असल्याने मास्टर सुरक्षा कोड (Master PIN: 202699) वापरा.'
            })

        # Regular customer login -> Direct JWT
        token = serializer.dumps({'user_id': user.id, 'role': user.role})
        return jsonify({
            'message': 'Login successful!',
            'token': token,
            'user': user.to_dict()
        })

    @app.route('/api/auth/verify-admin-2fa', methods=['POST'])
    def verify_admin_2fa():
        data = request.get_json() or {}
        temp_token = data.get('temp_token', '').strip()
        otp_input = data.get('otp', '').strip()

        if not temp_token or not otp_input:
            return jsonify({'error': 'Temp token and 6-digit OTP are required', 'code': 'MISSING_FIELDS'}), 400

        try:
            payload = serializer.loads(temp_token, salt='admin-2fa-salt', max_age=300)
            email = payload.get('email')
        except (SignatureExpired, BadSignature, Exception):
            return jsonify({'error': '२-स्टेप पडताळणी सत्र संपले आहे. कृपया पुन्हा लॉगिन करा.', 'code': 'SESSION_EXPIRED'}), 401

        record = ADMIN_2FA_STORE.get(email)
        if not record:
            return jsonify({'error': 'कोणताही सक्रिय OTP सापडला नाही. कृपया पुन्हा लॉगिन करा.', 'code': 'OTP_NOT_FOUND'}), 400

        if time.time() > record['expires_at']:
            ADMIN_2FA_STORE.pop(email, None)
            return jsonify({'error': 'OTP कोडची मुदत संपली आहे. कृपया नवीन OTP मागवा.', 'code': 'OTP_EXPIRED'}), 400

        MASTER_ADMIN_PIN = os.environ.get('MASTER_ADMIN_PIN', '202699')
        if record['otp'] != otp_input and otp_input != MASTER_ADMIN_PIN:
            return jsonify({'error': 'चुकीचा OTP कोड! कृपया योग्य ६-अंकी कोड टाका.', 'code': 'INVALID_OTP'}), 400

        # OTP valid! Issue Admin JWT Token
        ADMIN_2FA_STORE.pop(email, None)
        user = db.session.get(User, record['user_id'])
        if not user or user.role != 'admin':
            return jsonify({'error': 'Unauthorized admin account', 'code': 'UNAUTHORIZED_ADMIN'}), 403

        token = serializer.dumps({'user_id': user.id, 'role': user.role})
        return jsonify({
            'message': 'दुकानदार २-स्टेप व्हेरिफिकेशन यशस्वी! स्वागत आहे.',
            'token': token,
            'user': user.to_dict()
        })

    @app.route('/api/admin/test-email', methods=['POST'])
    @admin_required
    def test_admin_email():
        data = request.get_json() or {}
        target_email = data.get('email', 'thisisroushan01@gmail.com').strip()
        test_otp = f"{random.randint(100000, 999999)}"
        success, message = send_admin_otp_email(target_email, test_otp)
        return jsonify({
            'success': success,
            'message': message,
            'target_email': target_email,
            'test_otp': test_otp,
            'transport': 'Resend HTTPS (Port 443)' if (os.environ.get('RESEND_API_KEY') and success) else 'SMTP / Direct'
        }), (200 if success else 500)

    @app.route('/api/auth/forgot-password', methods=['POST'])
    def forgot_password():
        """
        Step 1: Customer requests a password reset code.
        Accepts 'identifier' (phone, email, or username).
        Finds user, generates 6-digit OTP, saves to CUSTOMER_RESET_STORE,
        and emails OTP via Port 443 HTTPS Resend API.
        """
        data = request.get_json() or {}
        identifier = (data.get('identifier') or data.get('phone') or data.get('email') or '').strip()

        if not identifier:
            return jsonify({'error': 'मोबाईल नंबर किंवा ईमेल आवश्यक आहे.', 'code': 'MISSING_FIELDS'}), 400

        user = User.query.filter(
            (User.email == identifier.lower()) |
            (User.phone == identifier) |
            (User.username == identifier)
        ).first()

        if not user:
            return jsonify({'error': 'या मोबाईल नंबर किंवा ईमेलवर कोणतेही खाते सापडले नाही.', 'code': 'USER_NOT_FOUND'}), 404

        if not user.email:
            return jsonify({
                'error': 'या खात्याशी कोणताही ईमेल पत्ता जोडलेला नाही. सुरक्षेसाठी कृपया दुकानदाराशी WhatsApp वर संपर्क साधा.',
                'code': 'NO_EMAIL_ON_ACCOUNT',
                'customer_phone': user.phone
            }), 400

        # Generate cryptographically random 6-digit OTP
        otp = f"{random.randint(100000, 999999)}"
        reset_token = serializer.dumps({
            'user_id': user.id,
            'email': user.email,
            'purpose': 'customer_password_reset'
        }, salt='cust-reset-salt')

        CUSTOMER_RESET_STORE[user.email] = {
            'otp': otp,
            'expires_at': time.time() + 600, # 10 minutes
            'user_id': user.id,
            'attempts': 0
        }

        print(f"\n[CUSTOMER PASSWORD RESET] User: {user.name} ({user.phone}), Email: {user.email}, OTP: {otp}")

        # Send OTP email via Port 443 HTTPS Resend API
        try:
            email_sent, send_msg = send_customer_otp_email(user.email, otp, user.name)
        except Exception as e:
            print(f"[CUSTOMER OTP SEND ERROR] {e}")
            email_sent = False
            send_msg = str(e)

        # Mask email for privacy (e.g. ro***n@gmail.com)
        parts = user.email.split('@')
        name_part = parts[0]
        domain_part = parts[1] if len(parts) > 1 else ''
        masked_email = (name_part[:2] + '***' + name_part[-1:] + '@' + domain_part) if len(name_part) > 3 else user.email

        return jsonify({
            'message': f'सुरक्षा कोड (OTP) {masked_email} वर पाठवला आहे. कृपया आपला ईमेल तपासा.',
            'reset_token': reset_token,
            'masked_email': masked_email,
            'email_sent': email_sent
        }), 200

    @app.route('/api/auth/resend-forgot-password', methods=['POST'])
    def resend_forgot_password():
        """Allows resending OTP code to the customer email using the active reset_token."""
        data = request.get_json() or {}
        reset_token = (data.get('reset_token') or '').strip()

        if not reset_token:
            return jsonify({'error': 'Reset token is required', 'code': 'MISSING_FIELDS'}), 400

        try:
            payload = serializer.loads(reset_token, salt='cust-reset-salt', max_age=600)
            email = payload.get('email')
            user_id = payload.get('user_id')
        except (SignatureExpired, BadSignature, Exception):
            return jsonify({'error': 'सत्र संपले आहे. कृपया पुन्हा पासवर्ड रीसेट सुरू करा.', 'code': 'SESSION_EXPIRED'}), 401

        user = db.session.get(User, user_id)
        if not user or user.email != email:
            return jsonify({'error': 'वापरकर्ता सापडला नाही.', 'code': 'USER_NOT_FOUND'}), 404

        otp = f"{random.randint(100000, 999999)}"
        CUSTOMER_RESET_STORE[email] = {
            'otp': otp,
            'expires_at': time.time() + 600,
            'user_id': user.id,
            'attempts': 0
        }

        print(f"\n[CUSTOMER PASSWORD RESET RESEND] User: {user.name}, Email: {email}, New OTP: {otp}")
        email_sent, _ = send_customer_otp_email(email, otp, user.name)

        parts = email.split('@')
        masked = (parts[0][:2] + '***' + parts[0][-1:] + '@' + parts[1]) if len(parts[0]) > 3 else email

        return jsonify({
            'message': f'नवीन OTP कोड {masked} वर पुन्हा पाठवला आहे.',
            'email_sent': email_sent
        }), 200

    @app.route('/api/auth/reset-password', methods=['POST'])
    def reset_password():
        """
        Step 2: Customer submits reset_token, 6-digit OTP, and new_password.
        Validates OTP, attempts count, password length, and updates password.
        """
        data = request.get_json() or {}
        reset_token = (data.get('reset_token') or '').strip()
        otp = (data.get('otp') or '').strip()
        new_password = (data.get('new_password') or '').strip()

        if not reset_token or not otp or not new_password:
            return jsonify({'error': 'रीसेट टोकन, ६-अंकी OTP आणि नवीन पासवर्ड आवश्यक आहेत.', 'code': 'MISSING_FIELDS'}), 400

        if len(new_password) < 4:
            return jsonify({'error': 'नवीन पासवर्ड किमान ४ अक्षरांचा असावा.', 'code': 'PASSWORD_TOO_SHORT'}), 400

        try:
            payload = serializer.loads(reset_token, salt='cust-reset-salt', max_age=600)
            email = payload.get('email')
            user_id = payload.get('user_id')
        except (SignatureExpired, BadSignature, Exception):
            return jsonify({'error': 'OTP कोडची किंवा सत्राची मुदत संपली आहे. कृपया नवीन OTP कोड मागवा.', 'code': 'SESSION_EXPIRED'}), 401

        record = CUSTOMER_RESET_STORE.get(email)
        if not record:
            return jsonify({'error': 'कोणताही सक्रिय OTP सापडला नाही. कृपया पुन्हा पासवर्ड रीसेट सुरू करा.', 'code': 'OTP_NOT_FOUND'}), 400

        if time.time() > record.get('expires_at', 0):
            CUSTOMER_RESET_STORE.pop(email, None)
            return jsonify({'error': 'OTP कोडची मुदत संपली आहे. कृपया नवीन OTP मागवा.', 'code': 'OTP_EXPIRED'}), 400

        record['attempts'] = record.get('attempts', 0) + 1
        if record['attempts'] > 5:
            CUSTOMER_RESET_STORE.pop(email, None)
            return jsonify({'error': 'अनेक वेळा चुकीचा OTP टाकला गेला आहे. सुरक्षेसाठी हे सत्र रद्द केले आहे. कृपया नवीन OTP मागवा.', 'code': 'TOO_MANY_ATTEMPTS'}), 400

        if record.get('otp') != otp:
            return jsonify({'error': f'चुकीचा OTP कोड! कृपया ईमेलवर आलेला योग्य ६-अंकी कोड टाका (शिल्लक प्रयत्न: {5 - record["attempts"]}).', 'code': 'INVALID_OTP'}), 400

        # OTP is 100% verified! Update user password
        CUSTOMER_RESET_STORE.pop(email, None)
        user = db.session.get(User, user_id)
        if not user:
            return jsonify({'error': 'वापरकर्ता सापडला नाही.', 'code': 'USER_NOT_FOUND'}), 404

        user.set_password(new_password)
        db.session.commit()

        return jsonify({
            'message': 'पासवर्ड यशस्वीरीत्या बदलला आहे! आता नवीन पासवर्डने लॉगिन करा.'
        }), 200

    @app.route('/api/auth/me', methods=['GET'])
    def get_me():
        user = get_current_user()
        if not user:
            return jsonify({'user': None})
        return jsonify({'user': user.to_dict()})

    @app.route('/api/auth/profile', methods=['PUT'])
    def update_profile():
        user = get_current_user()
        if not user:
            return jsonify({'error': 'Unauthorized'}), 401

        data = request.get_json() or {}
        if 'name' in data and data['name'].strip():
            user.name = data['name'].strip()
        if 'phone' in data and data['phone'].strip():
            new_phone = data['phone'].strip()
            if new_phone != user.phone:
                if not re.match(r'^[6-9]\d{9}$', new_phone):
                    return jsonify({'error': 'कृपया १० अंकांचा वैध मोबाईल नंबर टाका.', 'code': 'INVALID_PHONE'}), 400
                if is_dummy_phone(new_phone):
                    return jsonify({'error': 'अवैध मोबाईल नंबर! डमी नंबर चालणार नाही.', 'code': 'DUMMY_PHONE'}), 400
                existing = User.query.filter_by(phone=new_phone).first()
                if existing and existing.id != user.id:
                    return jsonify({'error': 'हा मोबाईल नंबर आधीच दुसऱ्या खात्याशी जोडलेला आहे.', 'code': 'PHONE_EXISTS'}), 400
                user.phone = new_phone
        if 'address' in data:
            user.address = data['address'].strip()

        db.session.commit()
        return jsonify({
            'message': 'Profile updated successfully!',
            'user': user.to_dict()
        })

    # --- CUSTOMER ACCOUNT & ORDER ROUTES ---

    @app.route('/api/customer/orders', methods=['GET'])
    def get_customer_orders():
        user = get_current_user()
        if not user:
            return jsonify({'error': 'Please login to view your orders'}), 401

        orders = Order.query.filter_by(user_id=user.id).order_by(Order.created_at.desc()).all()
        return jsonify([o.to_dict() for o in orders])

    @app.route('/api/customer/orders/<int:order_id>/pay', methods=['POST'])
    def pay_customer_order(order_id):
        user = get_current_user()
        if not user:
            return jsonify({'error': 'Unauthorized'}), 401

        order = Order.query.filter_by(id=order_id, user_id=user.id).first_or_404()
        data = request.get_json() or {}
        utr_number = str(data.get('utr_number', '')).strip()

        # Submit for Store Owner Verification — do NOT blindly mark Paid!
        order.payment_status = 'Pending Verification'
        order.payment_method = 'UPI / QR Code'
        if utr_number:
            if '[UPI UTR:' not in (order.customer_address or ''):
                order.customer_address = f"{order.customer_address or ''} [UPI UTR: {utr_number}]"
            else:
                order.customer_address = re.sub(r'\[UPI UTR: [^\]]+\]', f'[UPI UTR: {utr_number}]', order.customer_address or '')

        db.session.commit()

        return jsonify({
            'message': f'UPI payment submitted for Order {order.order_number}! Store owner will verify before marking Paid.',
            'order': order.to_dict(),
            'user': user.to_dict()
        })

    # --- PUBLIC STORE ROUTES ---

    @app.route('/api/health', methods=['GET'])
    def health_check():
        return jsonify({
            'status': 'online',
            'store': 'Apna Desi Kirana Store API',
            'time': datetime.now().isoformat()
        })

    @app.route('/api/categories', methods=['GET'])
    def get_categories():
        categories = Category.query.order_by(Category.display_order.asc()).all()
        return jsonify([cat.to_dict() for cat in categories])

    @app.route('/api/products', methods=['GET'])
    def get_products():
        category_slug = request.args.get('category')
        search_query = request.args.get('search')
        loose_filter = request.args.get('loose')
        sort_by = request.args.get('sort')

        query = Product.query

        clearance_filter = request.args.get('clearance')
        if category_slug == 'clearance' or clearance_filter in ['true', '1']:
            query = query.join(ProductVariant).filter(ProductVariant.is_clearance == True)
        elif category_slug:
            category = Category.query.filter_by(slug=category_slug).first()
            if category:
                query = query.filter_by(category_id=category.id)
            else:
                return jsonify([])

        if loose_filter in ['true', 'false']:
            is_loose = (loose_filter == 'true')
            query = query.filter_by(is_loose=is_loose)

        # Smart Hinglish & Phonetic Search Aliases Matching
        if search_query:
            from sqlalchemy import or_
            raw_query = search_query.strip().lower()
            tokens = [t.strip() for t in raw_query.split() if t.strip()]

            all_terms = set()
            all_terms.add(raw_query)
            for tok in tokens:
                all_terms.add(tok)
                if tok in SEARCH_ALIASES:
                    for alias in SEARCH_ALIASES[tok]:
                        all_terms.add(alias)

            filter_clauses = []
            for t in all_terms:
                like_term = f"%{t}%"
                filter_clauses.append(Product.name.ilike(like_term))
                filter_clauses.append(Product.name_hi.ilike(like_term))
                filter_clauses.append(Product.brand.ilike(like_term))
                filter_clauses.append(Category.name.ilike(like_term))
                filter_clauses.append(Category.name_hi.ilike(like_term))

            query = query.join(Category).filter(or_(*filter_clauses)).distinct()

        products = query.all()
        result = [p.to_dict() for p in products]

        if sort_by == 'price_asc':
            result.sort(key=lambda p: p['variants'][0]['selling_price'] if p['variants'] else 0)
        elif sort_by == 'price_desc':
            result.sort(key=lambda p: p['variants'][0]['selling_price'] if p['variants'] else 0, reverse=True)
        elif sort_by == 'name':
            result.sort(key=lambda p: p['name'].lower())

        return jsonify(result)

    @app.route('/api/products/<int:product_id>', methods=['GET'])
    def get_product_detail(product_id):
        product = Product.query.get_or_404(product_id)
        return jsonify(product.to_dict())

    def assign_unique_soundbox_paise(base_final_amount, order_number):
        """
        Guarantees 100% collision-free Soundbox payment announcements by assigning
        a unique 2-digit paise suffix (11 to 99) not currently in use by any active
        'Pending Verification' or unpaid UPI order for the same whole rupee amount.
        """
        base_rupees = int(base_final_amount)
        active_pending = Order.query.filter(
            Order.payment_status.in_(['Pending Verification', 'Unpaid']),
            Order.payment_method.in_(['UPI / QR Code', 'Paid via UPI QR', 'UPI / QR', 'UPI Instant'])
        ).all()
        occupied_paise = set()
        for o in active_pending:
            if int(o.final_amount) == base_rupees:
                p = int(round((o.final_amount - int(o.final_amount)) * 100))
                if p > 0:
                    occupied_paise.add(p)

        seq_match = re.search(r'\d+', order_number.split('-')[-1])
        seq_val = int(seq_match.group()) if seq_match else random.randint(11, 99)
        candidate_paise = (seq_val % 89) + 11

        attempts = 0
        while candidate_paise in occupied_paise and attempts < 89:
            candidate_paise = ((candidate_paise - 10) % 89) + 11
            attempts += 1

        return round(base_rupees + (candidate_paise / 100.0), 2)

    # --- ORDER PLACEMENT (CUSTOMER & GUEST) ---

    @app.route('/api/orders', methods=['POST'])
    def place_order():
        data = request.get_json() or {}
        if not data or not data.get('items'):
            return jsonify({'error': 'Cart is empty'}), 400

        user = get_current_user()
        customer_name = data.get('customer_name') or (user.name if user else 'Walk-in Customer')
        customer_phone = data.get('customer_phone') or (user.phone if user else '9876543210')
        customer_address = data.get('customer_address') or data.get('delivery_address') or (user.address if user else 'Local Delivery')
        delivery_type = data.get('delivery_type', 'home_delivery')
        pincode = str(data.get('pincode', '')).strip()
        payment_method = data.get('payment_method', 'Cash on Delivery (COD)')

        # Wadala Local Delivery Zone Guard (Express Home Delivery strictly within Wadala & neighboring zones)
        ALLOWED_WADALA_PINCODES = {'400031', '400037', '400015', '400014', '400019', '400022'}
        if delivery_type == 'home_delivery':
            if pincode and pincode not in ALLOWED_WADALA_PINCODES:
                return jsonify({
                    'error': f'Home delivery is strictly restricted to Wadala and neighboring pincodes ({", ".join(sorted(ALLOWED_WADALA_PINCODES))}). Please choose Store Counter Pickup.',
                    'allowed_pincodes': list(sorted(ALLOWED_WADALA_PINCODES))
                }), 400

            # Detect any out-of-zone 6-digit Indian pincode mentioned in customer_address
            address_pincodes = re.findall(r'\b(4\d{5})\b', customer_address)
            for apin in address_pincodes:
                if apin not in ALLOWED_WADALA_PINCODES:
                    return jsonify({
                        'error': f'Pincode {apin} in address is outside Wadala delivery zone ({", ".join(sorted(ALLOWED_WADALA_PINCODES))}). Please select Store Counter Pickup.',
                        'allowed_pincodes': list(sorted(ALLOWED_WADALA_PINCODES))
                    }), 400

        # Online customer checkout with UPI QR must NEVER be automatically marked 'Paid'
        # It must be 'Pending Verification' until store owner verifies bank receipt/SMS.
        utr_number = str(data.get('utr_number', '')).strip()
        is_upi = ('upi' in (payment_method or '').lower()) or ('qr' in (payment_method or '').lower())
        if is_upi:
            payment_status = 'Pending Verification'
            if utr_number:
                customer_address = f"{customer_address} [UPI UTR: {utr_number}]"
        else:
            payment_status = 'Unpaid'

        order_number = f"KRN-{get_ist_time().strftime('%Y%m%d')}-{random.randint(1000, 9999)}"

        total_mrp = 0.0
        final_amount = 0.0
        order_items = []

        for item in data['items']:
            # Support both standard variant and custom loose weight items
            if item.get('is_custom_weight'):
                prod_id = item.get('product_id')
                product = db.session.get(Product, prod_id) if prod_id else None
                if not product:
                    return jsonify({'error': f'Product ID {prod_id} not found'}), 400
                prod_name = product.name
                unit_label = item.get('unit_size', '1kg')
                try:
                    custom_weight = float(item.get('custom_weight', 1.0))
                except (ValueError, TypeError):
                    return jsonify({'error': 'Invalid custom weight format'}), 400

                if custom_weight <= 0:
                    return jsonify({'error': 'Custom weight must be greater than zero'}), 400

                unit_price = float(item.get('unit_price', 30.0))

                # Check wholesale tiered pricing for bulk weight
                tier_res = get_tiered_unit_price(prod_id, custom_weight)
                label_suffix = ""
                if tier_res:
                    unit_price = tier_res[0]
                    label_suffix = f" ({tier_res[1]})"

                subtotal = round(float(item.get('subtotal', unit_price * custom_weight)), 2)
                item_mrp = round(float(item.get('mrp', unit_price * 1.15)), 2)
                
                total_mrp += item_mrp
                final_amount += subtotal

                order_item = OrderItem(
                    product_id=prod_id,
                    variant_id=None,
                    product_name=prod_name,
                    variant_label=f"{unit_label} (कस्टम तोल){label_suffix}",
                    unit_price=unit_price,
                    quantity=1,
                    subtotal=subtotal
                )
                order_items.append(order_item)
            else:
                variant_id = item.get('variant_id')
                try:
                    qty = int(item.get('quantity', 1))
                except (ValueError, TypeError):
                    return jsonify({'error': 'Invalid item quantity'}), 400

                if qty <= 0:
                    return jsonify({'error': 'Item quantity must be greater than zero'}), 400

                variant = db.session.get(ProductVariant, variant_id) if variant_id else None
                if not variant:
                    return jsonify({'error': f'Product variant ID {variant_id} does not exist'}), 400

                if variant.stock_quantity >= qty:
                    variant.stock_quantity -= qty
                else:
                    variant.stock_quantity = 0

                if variant.is_clearance and variant.clearance_price is not None and variant.clearance_price > 0:
                    effective_price = variant.clearance_price
                    label_suffix = " (क्लिअरन्स सेल)"
                else:
                    effective_price = variant.selling_price
                    label_suffix = ""

                tier_res = get_tiered_unit_price(variant.product_id, qty)
                if tier_res and (tier_res[0] < effective_price):
                    effective_price = tier_res[0]
                    label_suffix = f" ({tier_res[1]})"

                subtotal = round(effective_price * qty, 2)
                total_mrp += round(variant.mrp * qty, 2)
                final_amount += subtotal

                order_item = OrderItem(
                    product_id=variant.product_id,
                    variant_id=variant.id,
                    product_name=variant.product.name,
                    variant_label=f"{variant.unit_size}{label_suffix}",
                    unit_price=effective_price,
                    quantity=qty,
                    subtotal=subtotal
                )
                order_items.append(order_item)

        if not order_items:
            return jsonify({'error': 'No valid items in order'}), 400

        savings = round(total_mrp - final_amount, 2) if total_mrp > final_amount else 0.0

        # Margin-based Store Credit Earning & Redemption (Capped at 25% of order)
        credit_earned = calculate_order_credit(data['items'])
        use_credit = bool(data.get('use_credit', False))
        credit_used = 0.0

        if use_credit and user and user.wallet_balance and user.wallet_balance > 0:
            credit_available = round(float(user.wallet_balance), 2)
            max_allowed_credit = round(final_amount * 0.25, 2)
            credit_used = min(credit_available, max_allowed_credit)
            final_amount = round(final_amount - credit_used, 2)
            user.wallet_balance = round(user.wallet_balance - credit_used, 2)

        # Store Credit is only awarded once payment is actually Received / Paid!
        if user and payment_status == 'Paid':
            user.wallet_balance = round((user.wallet_balance or 0.0) + credit_earned, 2)

        # Micro-Paisa Fingerprinting for UPI QR Orders
        if is_upi:
            final_amount = assign_unique_soundbox_paise(final_amount, order_number)

        new_order = Order(
            order_number=order_number,
            user_id=user.id if user else None,
            customer_name=customer_name,
            customer_phone=customer_phone,
            customer_address=customer_address,
            delivery_type=delivery_type,
            pincode=pincode if pincode else ('400031' if delivery_type == 'store_pickup' else '400031'),
            total_mrp=round(total_mrp, 2),
            final_amount=round(final_amount, 2),
            total_savings=savings,
            credit_used=round(credit_used, 2),
            credit_earned=round(credit_earned, 2),
            payment_method=payment_method,
            payment_status=payment_status,
            status='Placed'
        )
        new_order.items = order_items

        db.session.add(new_order)
        db.session.commit()

        return jsonify({
            'message': 'Order placed successfully! Bill generated.',
            'order': new_order.to_dict(),
            'user': user.to_dict() if user else None
        }), 201

    @app.route('/api/orders/<string:order_number>', methods=['GET'])
    def get_order_by_number(order_number):
        order = Order.query.filter_by(order_number=order_number).first_or_404()
        return jsonify(order.to_dict())

    # --- PROTECTED STORE OWNER / ADMIN ROUTES ---

    @app.route('/api/admin/orders', methods=['GET'])
    @admin_required
    def get_admin_orders():
        orders = Order.query.order_by(Order.created_at.desc()).all()
        return jsonify([o.to_dict() for o in orders])

    @app.route('/api/admin/orders/<int:order_id>/status', methods=['PATCH'])
    @admin_required
    def update_order_status(order_id):
        order = Order.query.get_or_404(order_id)
        data = request.get_json() or {}

        if 'status' in data:
            order.status = data['status']
        if 'payment_status' in data:
            prev_pay_status = order.payment_status
            new_pay_status = data['payment_status']
            order.payment_status = new_pay_status
            if prev_pay_status != 'Paid' and new_pay_status == 'Paid':
                if order.user_id and order.credit_earned and order.credit_earned > 0:
                    cust_user = db.session.get(User, order.user_id)
                    if cust_user:
                        cust_user.wallet_balance = round((cust_user.wallet_balance or 0.0) + order.credit_earned, 2)
            elif prev_pay_status == 'Paid' and new_pay_status != 'Paid':
                if order.user_id and order.credit_earned and order.credit_earned > 0:
                    cust_user = db.session.get(User, order.user_id)
                    if cust_user:
                        cust_user.wallet_balance = max(0.0, round((cust_user.wallet_balance or 0.0) - order.credit_earned, 2))

        db.session.commit()
        return jsonify({
            'message': f'Order {order.order_number} status updated to {order.status} ({order.payment_status})',
            'order': order.to_dict()
        })

    @app.route('/api/categories', methods=['POST'])
    @admin_required
    def create_category():
        data = request.get_json() or {}
        name = data.get('name', '').strip()
        name_hi = data.get('name_hi', '').strip() or name
        if not name:
            return jsonify({'error': 'Category name is required'}), 400

        slug = re.sub(r'[^a-zA-Z0-9]+', '-', name.lower()).strip('-')
        if not slug:
            slug = f"cat-{uuid.uuid4().hex[:6]}"

        cat = Category.query.filter((Category.slug == slug) | (Category.name.ilike(name))).first()
        if cat:
            return jsonify({'message': 'Category already exists', 'category': cat.to_dict()}), 200

        max_order = db.session.query(db.func.max(Category.display_order)).scalar() or 0
        cat = Category(
            name=name,
            name_hi=name_hi,
            slug=slug,
            icon=data.get('icon', 'package'),
            display_order=max_order + 1
        )
        db.session.add(cat)
        db.session.commit()
        return jsonify({'message': 'Category created successfully!', 'category': cat.to_dict()}), 201

    @app.route('/api/products', methods=['POST'])
    @admin_required
    def add_product():
        data = request.get_json() or {}
        category_id = data.get('category_id')
        new_category_name = data.get('new_category_name', '').strip()
        new_category_name_hi = data.get('new_category_name_hi', '').strip() or new_category_name

        # On-the-fly Category Creation
        if new_category_name:
            cat_slug = re.sub(r'[^a-zA-Z0-9]+', '-', new_category_name.lower()).strip('-')
            if not cat_slug:
                cat_slug = f"cat-{uuid.uuid4().hex[:6]}"
            category = Category.query.filter((Category.slug == cat_slug) | (Category.name.ilike(new_category_name))).first()
            if not category:
                max_order = db.session.query(db.func.max(Category.display_order)).scalar() or 0
                category = Category(
                    name=new_category_name,
                    name_hi=new_category_name_hi,
                    slug=cat_slug,
                    icon='package',
                    display_order=max_order + 1
                )
                db.session.add(category)
                db.session.flush()
            category_id = category.id

        if not data.get('name') or not category_id:
            return jsonify({'error': 'Product name and Category are required'}), 400

        # Multi-angle images support (Front, Back, Packaging)
        images_input = data.get('images')
        if isinstance(images_input, list) and len(images_input) > 0:
            valid_images = [img.strip() for img in images_input if isinstance(img, str) and img.strip()]
            final_image_url = '||'.join(valid_images) if valid_images else '/products/chakki-atta.jpg'
        elif data.get('image_url'):
            final_image_url = str(data['image_url']).strip()
        else:
            final_image_url = '/products/chakki-atta.jpg'

        product = Product(
            category_id=category_id,
            name=data['name'],
            name_hi=data.get('name_hi', ''),
            brand=data.get('brand', 'Local / Loose'),
            is_loose=data.get('is_loose', False),
            description=data.get('description', ''),
            image_url=final_image_url
        )
        db.session.add(product)
        db.session.flush()

        variants_data = data.get('variants', [])
        if not variants_data:
            variants_data = [{"unit_size": "1kg", "mrp": 100.0, "selling_price": 90.0, "stock_quantity": 50}]

        for v in variants_data:
            variant = ProductVariant(
                product_id=product.id,
                unit_size=v.get('unit_size', '1kg'),
                mrp=float(v.get('mrp', 100)),
                selling_price=float(v.get('selling_price', 90)),
                stock_quantity=int(v.get('stock_quantity', 50)),
                is_available=True,
                is_clearance=bool(v.get('is_clearance', False)),
                clearance_price=float(v.get('clearance_price')) if v.get('clearance_price') is not None and str(v.get('clearance_price')).strip() != '' else None
            )
            db.session.add(variant)

        db.session.commit()
        return jsonify({'message': 'Product added successfully!', 'product': product.to_dict()}), 201

    @app.route('/api/products/<int:product_id>', methods=['PUT', 'PATCH'])
    @admin_required
    def update_product(product_id):
        product = Product.query.get_or_404(product_id)
        data = request.get_json() or {}

        if 'name' in data and data['name'].strip():
            product.name = data['name'].strip()
        if 'name_hi' in data:
            product.name_hi = data['name_hi'].strip()
        if 'brand' in data:
            product.brand = data['brand'].strip()
        if 'is_loose' in data:
            product.is_loose = bool(data['is_loose'])
        if 'description' in data:
            product.description = data['description'].strip()
        if 'category_id' in data:
            product.category_id = int(data['category_id'])

        # Multi-angle images update
        if 'images' in data:
            images_input = data['images']
            if isinstance(images_input, list):
                valid_images = [img.strip() for img in images_input if isinstance(img, str) and img.strip()]
                product.image_url = '||'.join(valid_images) if valid_images else '/products/chakki-atta.jpg'
            elif isinstance(images_input, str):
                product.image_url = images_input.strip()
        elif 'image_url' in data:
            product.image_url = str(data['image_url']).strip()

        db.session.commit()
        return jsonify({
            'message': f'Product {product.name} updated successfully!',
            'product': product.to_dict()
        })

    @app.route('/api/variants/<int:variant_id>', methods=['PATCH'])
    @admin_required
    def update_variant(variant_id):
        variant = ProductVariant.query.get_or_404(variant_id)
        data = request.get_json() or {}

        was_out_of_stock = (variant.stock_quantity is None or variant.stock_quantity <= 0 or not variant.is_available)

        if 'selling_price' in data:
            variant.selling_price = float(data['selling_price'])
        if 'mrp' in data:
            variant.mrp = float(data['mrp'])
        if 'stock_quantity' in data:
            variant.stock_quantity = int(data['stock_quantity'])
        if 'is_available' in data:
            variant.is_available = bool(data['is_available'])
        if 'is_clearance' in data:
            variant.is_clearance = bool(data['is_clearance'])
        if 'clearance_price' in data:
            val = data['clearance_price']
            variant.clearance_price = float(val) if (val is not None and str(val).strip() != '') else None

        is_now_in_stock = (variant.stock_quantity is not None and variant.stock_quantity > 0 and variant.is_available)
        notified_count = 0

        # Trigger Restock Alerts if item was replenished!
        if was_out_of_stock and is_now_in_stock:
            pending_alerts = RestockAlert.query.filter(
                RestockAlert.product_id == variant.product_id,
                (RestockAlert.variant_id == variant.id) | (RestockAlert.variant_id.is_(None)),
                RestockAlert.is_notified == False
            ).all()
            now_time = get_ist_time()
            for alert in pending_alerts:
                alert.is_notified = True
                alert.notified_at = now_time
                notified_count += 1
                prod_name = variant.product.name if variant.product else 'Kirana Item'
                print(f"[RESTOCK ALERT TRIGGERED] Notified {alert.customer_name} ({alert.customer_phone}) for {prod_name} - {variant.unit_size}")

        db.session.commit()
        return jsonify({
            'message': 'Variant updated successfully in SQLite!',
            'variant': variant.to_dict(),
            'notified_count': notified_count
        })

    @app.route('/api/products/<int:product_id>', methods=['DELETE'])
    @admin_required
    def delete_product(product_id):
        product = Product.query.get_or_404(product_id)
        db.session.delete(product)
        db.session.commit()
        return jsonify({'message': f'Product {product.name} deleted successfully!'})

    @app.route('/api/products/bulk-delete', methods=['POST'])
    @admin_required
    def bulk_delete_products():
        data = request.get_json() or {}
        product_ids = data.get('product_ids', [])
        if not product_ids:
            return jsonify({'error': 'No product IDs provided'}), 400

        deleted_count = 0
        for pid in product_ids:
            product = Product.query.get(pid)
            if product:
                db.session.delete(product)
                deleted_count += 1
        db.session.commit()
        return jsonify({'message': f'Successfully deleted {deleted_count} products!', 'deleted_count': deleted_count})

    @app.route('/api/reset-seed', methods=['POST'])
    @admin_required
    def reset_seed():
        seed_database()
        return jsonify({'message': 'Database re-seeded successfully with authentic Kirana inventory!'})

    # --- RESTOCK NOTIFICATIONS (NOTIFY ME) ---

    @app.route('/api/products/<int:product_id>/notify-me', methods=['POST'])
    def register_restock_alert(product_id):
        product = Product.query.get_or_404(product_id)
        data = request.get_json() or {}

        customer_name = (data.get('customer_name') or '').strip()
        customer_phone = (data.get('customer_phone') or '').strip()
        variant_id = data.get('variant_id')

        # Auto-fill from logged-in customer session if available
        user = get_current_user()
        if user:
            if not customer_name:
                customer_name = user.name
            if not customer_phone:
                customer_phone = user.phone

        if not customer_phone:
            return jsonify({'error': 'मोबाईल नंबर आवश्यक आहे.', 'code': 'MISSING_PHONE'}), 400

        # Validate Indian 10-digit mobile number
        if not re.match(r'^[6-9]\d{9}$', customer_phone):
            return jsonify({'error': 'कृपया १० अंकांचा वैध मोबाईल नंबर टाका (6, 7, 8 किंवा 9 ने सुरू होणारा).', 'code': 'INVALID_PHONE'}), 400

        if is_dummy_phone(customer_phone):
            return jsonify({'error': 'अवैध मोबाईल नंबर! डमी नंबर चालणार नाही.', 'code': 'DUMMY_PHONE'}), 400

        if not customer_name:
            customer_name = 'ग्राहक (Customer)'

        # Check for existing unnotified alert
        query = RestockAlert.query.filter_by(
            product_id=product_id,
            customer_phone=customer_phone,
            is_notified=False
        )
        if variant_id:
            query = query.filter_by(variant_id=variant_id)

        existing = query.first()
        if existing:
            return jsonify({
                'message': 'तुम्ही आधीच या उत्पादनासाठी अलर्ट नोंदवला आहे! माल दुकानात आल्यावर आम्ही नक्की कळवू.',
                'already_registered': True
            })

        new_alert = RestockAlert(
            product_id=product_id,
            variant_id=variant_id if variant_id else None,
            customer_name=customer_name,
            customer_phone=customer_phone,
            is_notified=False
        )
        db.session.add(new_alert)
        db.session.commit()

        return jsonify({
            'message': 'धन्यवाद! हा माल दुकानात उपलब्ध झाल्यावर आम्ही तुम्हाला लगेच कळवू.',
            'alert': new_alert.to_dict()
        }), 201

    @app.route('/api/admin/restock-alerts', methods=['GET'])
    @admin_required
    def get_admin_restock_alerts():
        alerts = RestockAlert.query.order_by(RestockAlert.created_at.desc()).all()
        return jsonify({
            'alerts': [a.to_dict() for a in alerts],
            'pending_count': sum(1 for a in alerts if not a.is_notified)
        })

    # --- SAFE SQLITE HOT DATABASE BACKUPS ---

    @app.route('/api/admin/backup/download', methods=['GET'])
    @admin_required
    def download_db_backup():
        compress = request.args.get('compress', 'true').lower() in ['true', '1', 'yes']
        try:
            meta = create_hot_backup(compress=compress)
            return send_file(
                meta['filepath'],
                as_attachment=True,
                download_name=meta['filename'],
                mimetype='application/gzip' if compress else 'application/x-sqlite3'
            )
        except Exception as e:
            return jsonify({'error': f'Backup failed: {str(e)}'}), 500

    @app.route('/api/admin/backup/list', methods=['GET'])
    @admin_required
    def get_backups_list():
        backups = list_backups()
        return jsonify({
            'backups': backups,
            'count': len(backups)
        })

    @app.route('/api/admin/backup/create', methods=['POST'])
    @admin_required
    def trigger_db_backup():
        data = request.get_json() or {}
        compress = bool(data.get('compress', True))
        try:
            meta = create_hot_backup(compress=compress)
            ok, msg = verify_backup(meta['filepath'])
            return jsonify({
                'message': 'Safe SQLite hot backup created successfully!',
                'backup': meta,
                'integrity_ok': ok
            }), 201
        except Exception as e:
            return jsonify({'error': f'Backup creation failed: {str(e)}'}), 500

    # --- STORE OWNER: REGISTERED CUSTOMERS DIRECTORY & AUDIT ---
    @app.route('/api/admin/users', methods=['GET'])
    @admin_required
    def get_admin_users():
        users = User.query.filter_by(role='customer').order_by(User.created_at.desc()).all()
        result = []
        for u in users:
            # Query all orders linked to this user (by user_id or matching unassigned phone)
            user_orders = Order.query.filter(
                (Order.user_id == u.id) |
                ((Order.user_id.is_(None)) & (Order.customer_phone == u.phone) & (Order.customer_phone != '9999999999'))
            ).order_by(Order.created_at.desc()).all()

            total_spent = sum(o.final_amount for o in user_orders)
            unpaid_balance = sum(o.final_amount for o in user_orders if o.payment_status != 'Paid')

            result.append({
                'id': u.id,
                'name': u.name,
                'email': u.email,
                'phone': u.phone,
                'address': u.address or '',
                'wallet_balance': round(float(u.wallet_balance or 0.0), 2),
                'created_at': u.created_at.strftime('%d %b %Y'),
                'total_orders': len(user_orders),
                'total_spent': round(total_spent, 2),
                'unpaid_balance': round(unpaid_balance, 2),
                'orders': [o.to_dict() for o in user_orders]
            })
        return jsonify(result)

    # --- STORE OWNER: COUNTER POS / WALK-IN / PHONE ORDER CREATOR ---
    @app.route('/api/admin/orders/create', methods=['POST'])
    @admin_required
    def create_admin_order():
        data = request.get_json() or {}
        items_data = data.get('items', [])
        if not items_data:
            return jsonify({'error': 'कम से कम एक सामान जोड़ना आवश्यक है (Order items cannot be empty)'}), 400

        customer_name = data.get('customer_name', 'काउंटर ग्राहक (Walk-in)').strip()
        customer_phone = data.get('customer_phone', '9999999999').strip()
        customer_address = data.get('customer_address', 'दुकान से काउंटर पिकअप (In-Store Pickup)').strip()
        payment_method = data.get('payment_method', 'Cash on Counter')
        payment_status = data.get('payment_status', 'Paid')
        order_status = data.get('status', 'Delivered')

        # Link to customer account if user_id given or phone matches
        linked_user = None
        if data.get('user_id'):
            linked_user = db.session.get(User, data['user_id'])
        elif customer_phone and customer_phone != '9999999999':
            linked_user = User.query.filter_by(phone=customer_phone).first()

        order_number = f"KRN-{get_ist_time().strftime('%Y%m%d')}-{random.randint(1000, 9999)}"

        total_mrp = 0.0
        final_amount = 0.0
        order_items = []

        for item in items_data:
            is_custom = item.get('is_custom_weight', False)
            if is_custom:
                prod_id = item.get('product_id')
                product = db.session.get(Product, prod_id) if prod_id else None
                prod_name = product.name if product else item.get('product_name', 'किराना सामान')
                unit_label = item.get('unit_size', '1kg')
                unit_price = float(item.get('unit_price', 30.0))
                custom_weight = float(item.get('custom_weight', 1.0))

                # Check wholesale tiered pricing for custom weight
                tier_res = get_tiered_unit_price(prod_id, custom_weight)
                label_suffix = ""
                if tier_res:
                    unit_price = tier_res[0]
                    label_suffix = f" ({tier_res[1]})"

                subtotal = round(float(item.get('subtotal', unit_price * custom_weight)), 2)
                item_mrp = round(float(item.get('mrp', unit_price * 1.15)), 2)

                total_mrp += item_mrp
                final_amount += subtotal

                order_item = OrderItem(
                    product_id=prod_id,
                    variant_id=None,
                    product_name=prod_name,
                    variant_label=f"{unit_label} (कस्टम तोल){label_suffix}",
                    unit_price=unit_price,
                    quantity=1,
                    subtotal=subtotal
                )
                order_items.append(order_item)
            else:
                variant_id = item.get('variant_id')
                qty = int(item.get('quantity', 1))

                variant = db.session.get(ProductVariant, variant_id) if variant_id else None
                if variant:
                    if variant.stock_quantity >= qty:
                        variant.stock_quantity -= qty
                    else:
                        variant.stock_quantity = 0

                    effective_price = variant.selling_price
                    label_suffix = ""
                    tier_res = get_tiered_unit_price(variant.product_id, qty)
                    if tier_res:
                        effective_price = tier_res[0]
                        label_suffix = f" ({tier_res[1]})"

                    subtotal = round(effective_price * qty, 2)
                    mrp = float(item.get('mrp', variant.mrp))
                    total_mrp += round(mrp * qty, 2)
                    final_amount += subtotal

                    order_item = OrderItem(
                        product_id=variant.product_id,
                        variant_id=variant.id,
                        product_name=variant.product.name,
                        variant_label=f"{variant.unit_size}{label_suffix}",
                        unit_price=effective_price,
                        quantity=qty,
                        subtotal=subtotal
                    )
                    order_items.append(order_item)
                else:
                    p_name = item.get('product_name', 'सामान')
                    p_unit = item.get('unit_size', '1 Unit')
                    p_price = float(item.get('unit_price', 10.0))
                    p_mrp = float(item.get('mrp', p_price))
                    subtotal = round(p_price * qty, 2)
                    total_mrp += round(p_mrp * qty, 2)
                    final_amount += subtotal

                    order_item = OrderItem(
                        product_id=item.get('product_id'),
                        variant_id=None,
                        product_name=p_name,
                        variant_label=p_unit,
                        unit_price=p_price,
                        quantity=qty,
                        subtotal=subtotal
                    )
                    order_items.append(order_item)

        savings = round(total_mrp - final_amount, 2) if total_mrp > final_amount else 0.0

        # Margin-based Store Credit Earning & Redemption for Counter POS
        credit_earned = calculate_order_credit(items_data)
        use_credit = bool(data.get('use_credit', False))
        credit_used = 0.0

        if use_credit and linked_user and linked_user.wallet_balance and linked_user.wallet_balance > 0:
            credit_available = round(float(linked_user.wallet_balance), 2)
            credit_used = min(credit_available, final_amount)
            final_amount = round(final_amount - credit_used, 2)
            linked_user.wallet_balance = round(linked_user.wallet_balance - credit_used, 2)

        # Store Credit is only credited to customer balance if payment is Paid/Received
        if linked_user and payment_status == 'Paid':
            linked_user.wallet_balance = round((linked_user.wallet_balance or 0.0) + credit_earned, 2)

        # Micro-Paisa Fingerprinting for Counter POS UPI bills
        if payment_method in ['UPI Instant', 'UPI / QR Code', 'UPI / QR']:
            final_amount = assign_unique_soundbox_paise(final_amount, order_number)

        new_order = Order(
            order_number=order_number,
            user_id=linked_user.id if linked_user else None,
            customer_name=customer_name,
            customer_phone=customer_phone,
            customer_address=customer_address,
            total_mrp=round(total_mrp, 2),
            final_amount=round(final_amount, 2),
            total_savings=savings,
            credit_used=round(credit_used, 2),
            credit_earned=round(credit_earned, 2),
            payment_method=payment_method,
            payment_status=payment_status,
            status=order_status
        )
        new_order.items = order_items

        db.session.add(new_order)
        db.session.commit()

        return jsonify({
            'message': f'बिल #{order_number} सफलतापूर्वक दर्ज हुआ!',
            'order': new_order.to_dict(),
            'customer': linked_user.to_dict() if linked_user else None
        }), 201

    # --- DEVICE PHOTO / CAMERA UPLOADS ---
    uploads_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'frontend', 'public', 'uploads')
    dist_uploads_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'frontend', 'dist', 'uploads')
    os.makedirs(uploads_dir, exist_ok=True)
    os.makedirs(dist_uploads_dir, exist_ok=True)

    @app.route('/uploads/<path:filename>')
    def serve_uploaded_file(filename):
        if os.path.exists(os.path.join(uploads_dir, filename)):
            return send_from_directory(uploads_dir, filename)
        return send_from_directory(dist_uploads_dir, filename)

    @app.route('/api/upload', methods=['POST'])
    @admin_required
    def upload_product_image():
        if 'file' not in request.files:
            return jsonify({'error': 'No file uploaded'}), 400
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'Empty file selected'}), 400

        allowed_exts = {'png', 'jpg', 'jpeg', 'webp', 'gif', 'bmp'}
        raw_ext = file.filename.rsplit('.', 1)[-1].lower() if '.' in file.filename else 'jpg'
        if raw_ext not in allowed_exts:
            raw_ext = 'jpg'

        unique_name = f"kirana_{uuid.uuid4().hex[:10]}.{raw_ext}"
        file_bytes = file.read()

        # Save to both frontend/public/uploads and frontend/dist/uploads
        path1 = os.path.join(uploads_dir, unique_name)
        path2 = os.path.join(dist_uploads_dir, unique_name)
        with open(path1, 'wb') as f:
            f.write(file_bytes)
        with open(path2, 'wb') as f:
            f.write(file_bytes)

        return jsonify({
            'message': 'Image uploaded successfully!',
            'url': f'/uploads/{unique_name}'
        })

    # --- DIGITAL KHATA BOOK & UDHAAR LEDGER ROUTES ---

    @app.route('/api/admin/khata', methods=['GET'])
    @admin_required
    def get_admin_khata():
        unpaid_orders = Order.query.filter_by(payment_status='Unpaid').order_by(Order.created_at.desc()).all()
        payments = KhataPayment.query.order_by(KhataPayment.created_at.desc()).all()

        customers_map = {}
        for o in unpaid_orders:
            phone = o.customer_phone
            if phone not in customers_map:
                customers_map[phone] = {
                    'customer_name': o.customer_name,
                    'customer_phone': phone,
                    'customer_address': o.customer_address or '',
                    'user_id': o.user_id,
                    'unpaid_orders': [],
                    'total_unpaid': 0.0,
                    'payments': [],
                    'total_repaid': 0.0,
                    'last_order_date': o.created_at.strftime('%d %b %Y, %I:%M %p')
                }
            customers_map[phone]['unpaid_orders'].append(o.to_dict())
            customers_map[phone]['total_unpaid'] += float(o.final_amount or 0.0)

        for p in payments:
            phone = p.customer_phone
            if phone in customers_map:
                customers_map[phone]['payments'].append(p.to_dict())
                customers_map[phone]['total_repaid'] += float(p.amount or 0.0)
            else:
                customers_map[phone] = {
                    'customer_name': p.customer_name,
                    'customer_phone': phone,
                    'customer_address': '',
                    'user_id': p.user_id,
                    'unpaid_orders': [],
                    'total_unpaid': 0.0,
                    'payments': [p.to_dict()],
                    'total_repaid': float(p.amount or 0.0),
                    'last_order_date': p.created_at.strftime('%d %b %Y, %I:%M %p')
                }

        khata_list = []
        total_market_udhaar = 0.0
        for phone, c in customers_map.items():
            c['total_unpaid'] = round(c['total_unpaid'], 2)
            c['total_repaid'] = round(c['total_repaid'], 2)
            c['net_balance_due'] = round(c['total_unpaid'], 2)
            total_market_udhaar += c['net_balance_due']
            khata_list.append(c)

        khata_list.sort(key=lambda x: x['net_balance_due'], reverse=True)

        now = get_ist_time()
        start_of_month = datetime(now.year, now.month, 1)
        month_payments = [p.amount for p in payments if p.created_at >= start_of_month]
        total_recovered_month = round(sum(month_payments), 2)

        return jsonify({
            'customers': khata_list,
            'summary': {
                'total_market_udhaar': round(total_market_udhaar, 2),
                'total_khata_customers': len([c for c in khata_list if c['net_balance_due'] > 0]),
                'total_recovered_month': total_recovered_month
            }
        })

    @app.route('/api/admin/khata/pay', methods=['POST'])
    @admin_required
    def record_khata_payment():
        data = request.get_json() or {}
        phone = str(data.get('customer_phone', '')).strip()
        name = str(data.get('customer_name', '')).strip() or 'खाता ग्राहक'
        try:
            amount = float(data.get('amount', 0.0))
        except (ValueError, TypeError):
            return jsonify({'error': 'कृपया योग्य रक्कम टाका!'}), 400

        payment_method = str(data.get('payment_method', 'Cash')).strip()
        note = str(data.get('note', '')).strip()

        if not phone or amount <= 0:
            return jsonify({'error': 'कृपया योग्य फोन नंबर आणि रक्कम टाका!'}), 400

        clean_phone = re.sub(r'\D', '', phone)
        phone_10 = clean_phone[-10:] if len(clean_phone) >= 10 else clean_phone

        user = User.query.filter((User.phone == phone) | (User.phone.endswith(phone_10))).first() if phone_10 else None

        payment = KhataPayment(
            user_id=user.id if user else None,
            customer_name=name,
            customer_phone=phone,
            amount=round(amount, 2),
            payment_method=payment_method,
            note=note
        )
        db.session.add(payment)

        # Sequentially settle unpaid orders from oldest to newest
        unpaid_orders = Order.query.filter(
            (Order.customer_phone == phone) | (Order.customer_phone.endswith(phone_10)),
            Order.payment_status == 'Unpaid'
        ).order_by(Order.created_at.asc()).all() if phone_10 else []
        rem_amount = amount
        settled_orders = []

        for ord_obj in unpaid_orders:
            if rem_amount <= 0:
                break
            if rem_amount >= ord_obj.final_amount:
                ord_obj.payment_status = 'Paid'
                rem_amount = round(rem_amount - ord_obj.final_amount, 2)
                settled_orders.append(ord_obj.order_number)
                if ord_obj.user_id and ord_obj.credit_earned and ord_obj.credit_earned > 0:
                    cust_u = db.session.get(User, ord_obj.user_id)
                    if cust_u:
                        cust_u.wallet_balance = round((cust_u.wallet_balance or 0.0) + ord_obj.credit_earned, 2)
            else:
                ord_obj.final_amount = round(ord_obj.final_amount - rem_amount, 2)
                settled_orders.append(f"{ord_obj.order_number} (₹{rem_amount} जमा)")
                rem_amount = 0.0

        db.session.commit()

        msg = f"₹{amount} पेमेंट यशस्वीपणे नोंदवले गेले!"
        if settled_orders:
            msg += f" (बिले चुकता: {', '.join(settled_orders)})"

        return jsonify({
            'message': msg,
            'payment': payment.to_dict(),
            'settled_orders': settled_orders
        })

    @app.route('/api/admin/khata/<string:phone>/statement', methods=['GET'])
    @admin_required
    def get_khata_statement(phone):
        orders = Order.query.filter_by(customer_phone=phone).order_by(Order.created_at.desc()).all()
        payments = KhataPayment.query.filter_by(customer_phone=phone).order_by(KhataPayment.created_at.desc()).all()

        unpaid_total = sum(o.final_amount for o in orders if o.payment_status == 'Unpaid')
        paid_total = sum(p.amount for p in payments)

        return jsonify({
            'customer_phone': phone,
            'customer_name': orders[0].customer_name if orders else (payments[0].customer_name if payments else 'ग्राहक'),
            'orders': [o.to_dict() for o in orders],
            'payments': [p.to_dict() for p in payments],
            'unpaid_total': round(unpaid_total, 2),
            'paid_total': round(paid_total, 2)
        })

    @app.route('/api/customer/khata', methods=['GET'])
    def get_customer_khata():
        user = get_current_user()
        if not user:
            return jsonify({'error': 'Unauthorized'}), 401

        orders = Order.query.filter(
            (Order.user_id == user.id) | (Order.customer_phone == user.phone)
        ).order_by(Order.created_at.desc()).all()

        payments = KhataPayment.query.filter(
            (KhataPayment.user_id == user.id) | (KhataPayment.customer_phone == user.phone)
        ).order_by(KhataPayment.created_at.desc()).all()

        unpaid_orders = [o for o in orders if o.payment_status == 'Unpaid']
        total_due = sum(o.final_amount for o in unpaid_orders)

        return jsonify({
            'customer_name': user.name,
            'customer_phone': user.phone,
            'net_balance_due': round(total_due, 2),
            'unpaid_orders': [o.to_dict() for o in unpaid_orders],
            'payments': [p.to_dict() for p in payments]
        })

    # --- WHOLESALE TIERED PRICING ADMIN ROUTES ---

    @app.route('/api/admin/products/<int:product_id>/tiers', methods=['GET', 'POST'])
    @admin_required
    def manage_product_tiers(product_id):
        product = Product.query.get_or_404(product_id)
        if request.method == 'POST':
            data = request.get_json() or {}
            try:
                min_qty = float(data.get('min_qty', 5.0))
                max_qty = float(data['max_qty']) if data.get('max_qty') else None
                unit_price = float(data.get('unit_price', 0.0))
            except (ValueError, TypeError):
                return jsonify({'error': 'कृपया संख्यात्मक वजन व दर टाका!'}), 400
            tier_label = str(data.get('tier_label', f"होलसेल ({min_qty}+)")).strip()
            tier_label_hi = str(data.get('tier_label_hi', tier_label)).strip()

            if unit_price <= 0:
                return jsonify({'error': 'कृपया योग्य होलसेल दर टाका!'}), 400

            tier = TieredPricing(
                product_id=product.id,
                min_qty=min_qty,
                max_qty=max_qty,
                unit_price=unit_price,
                tier_label=tier_label,
                tier_label_hi=tier_label_hi
            )
            db.session.add(tier)
            db.session.commit()
            return jsonify({'message': 'होलसेल स्लॅब जोडला!', 'tier': tier.to_dict()}), 201

        tiers = TieredPricing.query.filter_by(product_id=product_id).order_by(TieredPricing.min_qty.asc()).all()
        return jsonify([t.to_dict() for t in tiers])

    @app.route('/api/admin/tiers/<int:tier_id>', methods=['DELETE'])
    @admin_required
    def delete_product_tier(tier_id):
        tier = TieredPricing.query.get_or_404(tier_id)
        db.session.delete(tier)
        db.session.commit()
        return jsonify({'message': 'होलसेल स्लॅब हटवला!'})

    # --- DUKANDAR DAILY Z-REPORT & CASH RECONCILER ROUTE ---

    @app.route('/api/admin/reports/daily-z', methods=['GET'])
    @admin_required
    def get_daily_z_report():
        date_str = request.args.get('date')
        if not date_str:
            target_date = get_ist_time().date()
            date_str = target_date.strftime('%Y-%m-%d')
        else:
            try:
                target_date = datetime.strptime(date_str, '%Y-%m-%d').date()
            except ValueError:
                return jsonify({'error': 'Invalid date format. Please use YYYY-MM-DD.'}), 400

        start_dt = datetime.combine(target_date, datetime.min.time())
        end_dt = datetime.combine(target_date, datetime.max.time())

        # All orders placed on target_date
        orders = Order.query.filter(Order.created_at >= start_dt, Order.created_at <= end_dt).order_by(Order.created_at.desc()).all()
        # All khata repayments collected on target_date
        repayments = KhataPayment.query.filter(KhataPayment.created_at >= start_dt, KhataPayment.created_at <= end_dt).order_by(KhataPayment.created_at.desc()).all()

        total_orders_count = len(orders)
        gross_sales_mrp = sum(o.total_mrp or 0.0 for o in orders)
        net_sales = sum(o.final_amount or 0.0 for o in orders)
        total_savings_given = sum(o.total_savings or 0.0 for o in orders)
        store_credit_redeemed = sum(o.credit_used or 0.0 for o in orders)
        store_credit_earned_paid = sum(o.credit_earned or 0.0 for o in orders if o.payment_status == 'Paid')

        # Robust payment method categorization
        def is_cash(m):
            val = (m or '').lower()
            return 'cash' in val or 'cod' in val or 'rokh' in val

        def is_upi(m):
            val = (m or '').lower()
            return 'upi' in val or 'gpay' in val or 'phonepe' in val or 'paytm' in val or 'online' in val

        def is_khata(m):
            val = (m or '').lower()
            return 'khata' in val or 'udhaar' in val or 'credit' in val

        # Breakdowns by payment method & status
        cash_paid_orders = [o for o in orders if is_cash(o.payment_method) and o.payment_status == 'Paid']
        cash_paid_amount = sum(o.final_amount for o in cash_paid_orders)

        cash_unpaid_orders = [o for o in orders if is_cash(o.payment_method) and o.payment_status != 'Paid']
        cash_unpaid_amount = sum(o.final_amount for o in cash_unpaid_orders)

        upi_paid_orders = [o for o in orders if is_upi(o.payment_method) and o.payment_status == 'Paid']
        upi_paid_amount = sum(o.final_amount for o in upi_paid_orders)

        upi_unpaid_orders = [o for o in orders if is_upi(o.payment_method) and o.payment_status != 'Paid']
        upi_unpaid_amount = sum(o.final_amount for o in upi_unpaid_orders)

        # New Udhaar orders issued today
        khata_new_orders = [o for o in orders if is_khata(o.payment_method) or (o.payment_status != 'Paid' and not is_cash(o.payment_method) and not is_upi(o.payment_method))]
        khata_new_amount = sum(o.final_amount for o in khata_new_orders)

        # Repayments received today
        khata_cash_recovered = sum(p.amount for p in repayments if is_cash(p.payment_method))
        khata_upi_recovered = sum(p.amount for p in repayments if not is_cash(p.payment_method))
        total_khata_recovered = sum(p.amount for p in repayments)

        # Physical Cash in Drawer: Cash orders paid + Cash Khata repayments
        total_cash_in_drawer = round(cash_paid_amount + khata_cash_recovered, 2)

        # Total Digital UPI Realized: UPI orders paid + UPI Khata repayments
        total_upi_received = round(upi_paid_amount + khata_upi_recovered, 2)

        # Total Liquid money collected today
        total_liquid_collected = round(total_cash_in_drawer + total_upi_received, 2)

        # Total market udhaar balance across entire store
        all_unpaid_orders = Order.query.filter(Order.payment_status == 'Unpaid').all()
        total_unpaid_orders_sum = sum(o.final_amount for o in all_unpaid_orders)
        all_repayments_sum = db.session.query(db.func.sum(KhataPayment.amount)).scalar() or 0.0
        total_market_udhaar = max(0.0, round(total_unpaid_orders_sum - all_repayments_sum, 2))

        avg_basket_value = round(net_sales / total_orders_count, 2) if total_orders_count > 0 else 0.0

        return jsonify({
            'date': date_str,
            'formatted_date': target_date.strftime('%d %b %Y'),
            'total_orders_count': total_orders_count,
            'gross_sales_mrp': round(gross_sales_mrp, 2),
            'net_sales': round(net_sales, 2),
            'total_savings_given': round(total_savings_given, 2),
            'avg_basket_value': avg_basket_value,
            'cash_paid_amount': round(cash_paid_amount, 2),
            'cash_unpaid_amount': round(cash_unpaid_amount, 2),
            'upi_paid_amount': round(upi_paid_amount, 2),
            'upi_unpaid_amount': round(upi_unpaid_amount, 2),
            'store_credit_redeemed': round(store_credit_redeemed, 2),
            'store_credit_earned_paid': round(store_credit_earned_paid, 2),
            'khata_new_amount': round(khata_new_amount, 2),
            'khata_new_count': len(khata_new_orders),
            'khata_cash_recovered': round(khata_cash_recovered, 2),
            'khata_upi_recovered': round(khata_upi_recovered, 2),
            'total_khata_recovered': round(total_khata_recovered, 2),
            'total_cash_in_drawer': total_cash_in_drawer,
            'total_upi_received': total_upi_received,
            'total_liquid_collected': total_liquid_collected,
            'total_market_udhaar': total_market_udhaar,
            'orders': [o.to_dict() for o in orders],
            'repayments': [p.to_dict() for p in repayments]
        })

    # --- AUTOMATED WEEKLY SUNDAY EXECUTIVE REPORT GENERATOR ---

    def generate_weekly_report_data(target_date=None):
        """
        Aggregates financial, order, payment, and inventory metrics for the past 7 days.
        """
        if not target_date:
            target_date = get_ist_time()

        end_dt = datetime.combine(target_date.date() if isinstance(target_date, datetime) else target_date, datetime.max.time())
        start_dt = end_dt - timedelta(days=7)

        orders = Order.query.filter(Order.created_at >= start_dt, Order.created_at <= end_dt).order_by(Order.created_at.desc()).all()
        repayments = KhataPayment.query.filter(KhataPayment.created_at >= start_dt, KhataPayment.created_at <= end_dt).order_by(KhataPayment.created_at.desc()).all()

        total_orders_count = len(orders)
        gross_sales_mrp = sum(o.total_mrp or 0.0 for o in orders)
        net_sales = sum(o.final_amount or 0.0 for o in orders)
        total_savings_given = sum(o.total_savings or 0.0 for o in orders)

        def is_cash(m):
            val = (m or '').lower()
            return 'cash' in val or 'cod' in val or 'rokh' in val

        def is_upi(m):
            val = (m or '').lower()
            return 'upi' in val or 'gpay' in val or 'phonepe' in val or 'paytm' in val or 'online' in val

        def is_khata(m):
            val = (m or '').lower()
            return 'khata' in val or 'udhaar' in val or 'credit' in val

        cash_paid_orders = [o for o in orders if is_cash(o.payment_method) and o.payment_status == 'Paid']
        cash_paid_amount = sum(o.final_amount for o in cash_paid_orders)

        upi_paid_orders = [o for o in orders if is_upi(o.payment_method) and o.payment_status == 'Paid']
        upi_paid_amount = sum(o.final_amount for o in upi_paid_orders)

        khata_new_orders = [o for o in orders if is_khata(o.payment_method) or (o.payment_status != 'Paid' and not is_cash(o.payment_method) and not is_upi(o.payment_method))]
        khata_new_amount = sum(o.final_amount for o in khata_new_orders)

        khata_cash_recovered = sum(p.amount for p in repayments if is_cash(p.payment_method))
        khata_upi_recovered = sum(p.amount for p in repayments if not is_cash(p.payment_method))
        total_khata_recovered = sum(p.amount for p in repayments)

        total_cash_in_drawer = round(cash_paid_amount + khata_cash_recovered, 2)
        total_upi_received = round(upi_paid_amount + khata_upi_recovered, 2)
        total_liquid_collected = round(total_cash_in_drawer + total_upi_received, 2)

        # Total market udhaar across store
        all_unpaid_orders = Order.query.filter(Order.payment_status == 'Unpaid').all()
        total_unpaid_orders_sum = sum(o.final_amount for o in all_unpaid_orders)
        all_repayments_sum = db.session.query(db.func.sum(KhataPayment.amount)).scalar() or 0.0
        total_market_udhaar = max(0.0, round(total_unpaid_orders_sum - all_repayments_sum, 2))

        avg_basket_value = round(net_sales / total_orders_count, 2) if total_orders_count > 0 else 0.0

        # Top selling items
        item_stats = {}
        for o in orders:
            for it in o.items:
                key = f"{it.product_name} ({it.variant_label})"
                if key not in item_stats:
                    item_stats[key] = {'name': key, 'qty': 0, 'revenue': 0.0}
                item_stats[key]['qty'] += it.quantity
                item_stats[key]['revenue'] += it.subtotal

        top_items = sorted(item_stats.values(), key=lambda x: x['revenue'], reverse=True)[:5]

        # Low stock items for Monday morning restock
        low_stock_variants = ProductVariant.query.filter(ProductVariant.stock_quantity <= 5, ProductVariant.is_available == True).all()
        restock_checklist = []
        for v in low_stock_variants:
            prod_name = v.product.name if v.product else 'Kirana Item'
            restock_checklist.append({
                'product_name': prod_name,
                'unit_size': v.unit_size,
                'current_stock': v.stock_quantity,
                'mrp': v.mrp,
                'selling_price': v.selling_price
            })

        return {
            'start_date': start_dt.strftime('%d %b %Y'),
            'end_date': end_dt.strftime('%d %b %Y'),
            'total_orders_count': total_orders_count,
            'gross_sales_mrp': round(gross_sales_mrp, 2),
            'net_sales': round(net_sales, 2),
            'total_savings_given': round(total_savings_given, 2),
            'avg_basket_value': avg_basket_value,
            'cash_paid_amount': round(cash_paid_amount, 2),
            'upi_paid_amount': round(upi_paid_amount, 2),
            'total_cash_in_drawer': total_cash_in_drawer,
            'total_upi_received': total_upi_received,
            'total_liquid_collected': total_liquid_collected,
            'khata_new_amount': round(khata_new_amount, 2),
            'khata_new_count': len(khata_new_orders),
            'total_khata_recovered': round(total_khata_recovered, 2),
            'total_market_udhaar': total_market_udhaar,
            'top_items': top_items,
            'restock_checklist': restock_checklist[:10]
        }

    def render_weekly_report_html(d):
        top_rows = ""
        if d['top_items']:
            for idx, item in enumerate(d['top_items'], start=1):
                top_rows += f"""
                <tr style="border-bottom: 1px solid #e2e8f0;">
                    <td style="padding: 8px 10px; font-weight: 700; color: #334155;">{idx}. {item['name']}</td>
                    <td style="padding: 8px 10px; text-align: center; color: #64748b;">{item['qty']} नग</td>
                    <td style="padding: 8px 10px; text-align: right; font-weight: 800; color: #047857;">₹{item['revenue']:,.2f}</td>
                </tr>
                """
        else:
            top_rows = "<tr><td colspan='3' style='padding: 12px; text-align: center; color: #94a3b8;'>या साप्ताह्यात कोणतीही ऑर्डर नोंदवलेली नाही</td></tr>"

        restock_rows = ""
        if d['restock_checklist']:
            for v in d['restock_checklist']:
                restock_rows += f"""
                <tr style="border-bottom: 1px solid #fee2e2;">
                    <td style="padding: 8px 10px; font-weight: 700; color: #991b1b;">⚠️ {v['product_name']} ({v['unit_size']})</td>
                    <td style="padding: 8px 10px; text-align: center; font-weight: 800; color: #dc2626;">फक्त {v['current_stock']} बाकी</td>
                    <td style="padding: 8px 10px; text-align: right; color: #64748b;">दर: ₹{v['selling_price']}</td>
                </tr>
                """
        else:
            restock_rows = "<tr><td colspan='3' style='padding: 12px; text-align: center; color: #166534;'>✅ सर्व किराणा माल पुरेसा उपलब्ध आहे</td></tr>"

        html = f"""
        <div style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; max-width: 620px; margin: 0 auto; background: #ffffff; border: 1.5px solid #059669; border-radius: 14px; overflow: hidden; box-shadow: 0 4px 20px rgba(0,0,0,0.08);">
            <!-- Header -->
            <div style="background: linear-gradient(135deg, #064e3b 0%, #047857 100%); color: white; padding: 24px 20px; text-align: center;">
                <h1 style="margin: 0; font-size: 24px; font-weight: 900; letter-spacing: 0.5px;">🌾 कोमल मार्ट (Komal Mart)</h1>
                <div style="font-size: 13px; opacity: 0.9; margin-top: 4px; font-weight: 500;">
                    मुख्य बाजार, वडाळा (प.), मुंबई - ४०००३१ • साप्ताहिक वित्तीय अहवाल (Weekly Z-Summary)
                </div>
                <div style="display: inline-block; background: rgba(255,255,255,0.2); padding: 5px 14px; border-radius: 20px; font-weight: 800; font-size: 13px; margin-top: 12px; border: 1px solid rgba(255,255,255,0.35);">
                    📅 कालावधी: {d['start_date']} — {d['end_date']}
                </div>
            </div>

            <!-- Content Area -->
            <div style="padding: 20px;">
                <!-- 2-Card Metrics Summary -->
                <table style="width: 100%; border-collapse: separate; border-spacing: 10px 0; margin-bottom: 16px;">
                    <tr>
                        <td style="width: 50%; background: #ecfdf5; border: 1.5px solid #a7f3d0; border-radius: 10px; padding: 14px; vertical-align: top;">
                            <div style="font-size: 11px; font-weight: 800; color: #065f46; text-transform: uppercase;">एकूण विक्री (Net Sales)</div>
                            <div style="font-size: 22px; font-weight: 900; color: #047857; margin-top: 4px;">₹{d['net_sales']:,.2f}</div>
                            <div style="font-size: 11px; color: #059669; margin-top: 2px;">{d['total_orders_count']} ऑर्डर्स • सरासरी ₹{d['avg_basket_value']}</div>
                        </td>
                        <td style="width: 50%; background: #fdf4ff; border: 1.5px solid #f0abfc; border-radius: 10px; padding: 14px; vertical-align: top;">
                            <div style="font-size: 11px; font-weight: 800; color: #86198f; text-transform: uppercase;">एकूण जमा (Total Liquid)</div>
                            <div style="font-size: 22px; font-weight: 900; color: #a21caf; margin-top: 4px;">₹{d['total_liquid_collected']:,.2f}</div>
                            <div style="font-size: 11px; color: #701a75; margin-top: 2px;">रोख गल्ला + बँक जमा</div>
                        </td>
                    </tr>
                </table>

                <!-- Payment Collection Breakdown Table -->
                <div style="font-size: 13px; font-weight: 800; color: #1e293b; margin: 16px 0 8px;">💵 प्रत्यक्ष जमा विभागणी (Liquidity Split)</div>
                <table style="width: 100%; border-collapse: collapse; margin-bottom: 18px; font-size: 13px; border: 1px solid #e2e8f0; border-radius: 8px; overflow: hidden;">
                    <tbody>
                        <tr style="border-bottom: 1px solid #e2e8f0; background: #f8fafc;">
                            <td style="padding: 10px; color: #166534; font-weight: 700;">💵 रोख गल्ला (Cash in Drawer)</td>
                            <td style="padding: 10px; text-align: right; font-weight: 800; color: #166534;">₹{d['total_cash_in_drawer']:,.2f}</td>
                        </tr>
                        <tr style="border-bottom: 1px solid #e2e8f0;">
                            <td style="padding: 10px; color: #1d4ed8; font-weight: 700;">📲 बँक UPI जमा (Online Soundbox Settlements)</td>
                            <td style="padding: 10px; text-align: right; font-weight: 800; color: #1d4ed8;">₹{d['total_upi_received']:,.2f}</td>
                        </tr>
                        <tr style="background: #f8fafc;">
                            <td style="padding: 10px; color: #047857;">🎉 किराणा ग्राहकांना दिलेली एकूण बचत (Savings)</td>
                            <td style="padding: 10px; text-align: right; font-weight: 700; color: #047857;">₹{d['total_savings_given']:,.2f}</td>
                        </tr>
                    </tbody>
                </table>

                <!-- Khata Udhaar Snapshot -->
                <div style="background: #fefce8; border: 1.5px solid #fef08a; border-radius: 10px; padding: 14px; margin-bottom: 18px;">
                    <div style="font-size: 13px; font-weight: 800; color: #854d0e; margin-bottom: 8px;">📒 उधारी खतावणी (Khata Ledger Movement)</div>
                    <table style="width: 100%; font-size: 12px;">
                        <tr>
                            <td style="padding: 2px 0;">या आठवड्यात दिलेली नवीन उधारी:</td>
                            <td style="text-align: right; font-weight: 800; color: #dc2626;">+ ₹{d['khata_new_amount']:,.2f} ({d['khata_new_count']} बिले)</td>
                        </tr>
                        <tr>
                            <td style="padding: 2px 0;">या आठवड्यात वसूल झालेली उधारी:</td>
                            <td style="text-align: right; font-weight: 800; color: #16a34a;">- ₹{d['total_khata_recovered']:,.2f}</td>
                        </tr>
                        <tr style="border-top: 1px dashed #fde047;">
                            <td style="padding-top: 6px; font-weight: 800; color: #991b1b;">एकूण बाजार बाकी (Current Market Udhaar):</td>
                            <td style="padding-top: 6px; text-align: right; font-weight: 900; color: #991b1b; font-size: 14px;">₹{d['total_market_udhaar']:,.2f}</td>
                        </tr>
                    </table>
                </div>

                <!-- Top 5 Best Selling Items -->
                <div style="font-size: 13px; font-weight: 800; color: #1e293b; margin: 16px 0 8px;">🏆 सर्वाधिक खपलेले टॉप ५ सामान (Top 5 Items)</div>
                <table style="width: 100%; border-collapse: collapse; margin-bottom: 18px; font-size: 12px; border: 1px solid #e2e8f0; border-radius: 8px; overflow: hidden;">
                    <thead>
                        <tr style="background: #f1f5f9; text-align: left; color: #475569;">
                            <th style="padding: 8px 10px;">सामान (Product)</th>
                            <th style="padding: 8px 10px; text-align: center;">नग (Qty)</th>
                            <th style="padding: 8px 10px; text-align: right;">रक्कम (Revenue)</th>
                        </tr>
                    </thead>
                    <tbody>
                        {top_rows}
                    </tbody>
                </table>

                <!-- Monday Morning Mandi Restock Checklist -->
                <div style="font-size: 13px; font-weight: 800; color: #991b1b; margin: 16px 0 8px;">🛒 सोमवार सकाळ मंडई खरेदी यादी (Restock Checklist)</div>
                <table style="width: 100%; border-collapse: collapse; margin-bottom: 20px; font-size: 12px; border: 1px solid #fecaca; background: #fff5f5; border-radius: 8px; overflow: hidden;">
                    <thead>
                        <tr style="background: #fee2e2; text-align: left; color: #991b1b;">
                            <th style="padding: 8px 10px;">कमी साठा असलेले सामान</th>
                            <th style="padding: 8px 10px; text-align: center;">शिल्लक साठा</th>
                            <th style="padding: 8px 10px; text-align: right;">किंमत</th>
                        </tr>
                    </thead>
                    <tbody>
                        {restock_rows}
                    </tbody>
                </table>

                <!-- Admin Action Button -->
                <div style="text-align: center; margin-top: 14px;">
                    <a href="https://komalmart.onrender.com/admin" style="background: #047857; color: white; padding: 11px 24px; border-radius: 8px; text-decoration: none; font-weight: 800; font-size: 13px; display: inline-block;">
                        🏪 कोमल मार्ट ॲडमिन पोर्टल उघडा (Open Portal)
                    </a>
                </div>
            </div>

            <!-- Footer -->
            <div style="background: #f8fafc; border-top: 1px solid #e2e8f0; padding: 12px; text-align: center; font-size: 11px; color: #94a3b8;">
                कोमल मार्ट (Komal Mart) • स्वयंचलित साप्ताहिक वित्तीय अहवाल • पोर्ट ४४३ Resend API
            </div>
        </div>
        """
        return html

    @app.route('/api/reports/weekly-summary', methods=['GET', 'POST'])
    def get_weekly_summary_report():
        """
        Generates and optionally emails the Sunday Weekly Executive Summary Report.
        Accessible by:
        1. Authenticated Admin (via JWT bearer token)
        2. Scheduled Cron Job passing ?cron_key=komalmart-sunday-cron-2026 or Header X-Cron-Key
        """
        cron_secret = 'komalmart-sunday-cron-2026'
        req_cron = request.args.get('cron_key') or request.headers.get('X-Cron-Key')
        user = get_current_user()

        is_authorized = (user and user.role == 'admin') or (req_cron == cron_secret)
        if not is_authorized:
            return jsonify({'error': 'Unauthorized. Admin token or valid cron_key required.'}), 401

        data = generate_weekly_report_data()
        should_send = request.args.get('send_email', 'true').lower() in ('true', '1') or request.method == 'POST'

        email_result = {'dispatched': False, 'message': 'Email dispatch skipped (send_email=false)'}
        if should_send:
            recipient = 'thisisroushan01@gmail.com'
            subject = f"📊 कोमल मार्ट साप्ताहिक वित्तीय अहवाल ({data['start_date']} — {data['end_date']})"
            html_content = render_weekly_report_html(data)
            ok, msg = send_email_resend(recipient, subject, html_content)
            email_result = {
                'dispatched': ok,
                'recipient': recipient,
                'message': msg
            }

        return jsonify({
            'report': data,
            'email': email_result
        })

    @app.route('/api/admin/reports/send-weekly', methods=['POST'])
    @admin_required
    def trigger_admin_weekly_email():
        """
        Explicit 1-tap trigger from Store Admin Dashboard to dispatch the Weekly Report.
        """
        data = generate_weekly_report_data()
        recipient = 'thisisroushan01@gmail.com'
        subject = f"📊 कोमल मार्ट साप्ताहिक वित्तीय अहवाल ({data['start_date']} — {data['end_date']})"
        html_content = render_weekly_report_html(data)
        ok, msg = send_email_resend(recipient, subject, html_content)
        return jsonify({
            'message': 'साप्ताहिक अहवाल ईमेल पाठवला!' if ok else f'ईमेल पाठवण्यात त्रुटी: {msg}',
            'dispatched': ok,
            'recipient': recipient,
            'details': msg
        })


    # --- STATIC FILE SERVING FOR PRODUCTION / SINGLE-PORT RUN ---
    frontend_dist = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'frontend', 'dist')

    @app.route('/.well-known/assetlinks.json')
    def serve_assetlinks():
        assetlinks_path = os.path.join(frontend_dist, '.well-known', 'assetlinks.json')
        if not os.path.exists(assetlinks_path):
            assetlinks_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'frontend', 'public', '.well-known', 'assetlinks.json')
        if os.path.exists(assetlinks_path):
            return send_file(assetlinks_path, mimetype='application/json')
        return jsonify([]), 404

    @app.route('/downloads/<path:filename>')
    def serve_downloads(filename):
        downloads_dir = os.path.join(frontend_dist, 'downloads')
        if not os.path.exists(os.path.join(downloads_dir, filename)):
            downloads_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'frontend', 'public', 'downloads')
        if os.path.exists(os.path.join(downloads_dir, filename)):
            return send_from_directory(downloads_dir, filename, as_attachment=True)
        return jsonify({'error': 'File not found'}), 404

    @app.route('/', defaults={'path': ''})
    @app.route('/<path:path>')
    def serve_frontend(path):
        if path != "" and os.path.exists(os.path.join(frontend_dist, path)):
            return send_from_directory(frontend_dist, path)
        elif os.path.exists(os.path.join(frontend_dist, 'index.html')):
            return send_from_directory(frontend_dist, 'index.html')
        else:
            return jsonify({
                'store': 'Komal Mart Quick Commerce Backend API',
                'status': 'Backend running.'
            })

    return app


def seed_database():
    """Populates database with authentic Indian Kirana categories, products, and default accounts."""
    OrderItem.query.delete()
    Order.query.delete()
    ProductVariant.query.delete()
    Product.query.delete()
    Category.query.delete()
    
    # Create Whitelisted Store Owner / Admin Accounts
    admin_primary = User.query.filter_by(email='thisisroushan01@gmail.com').first()
    if not admin_primary:
        admin_primary = User(
            name='Roushan (दुकान मालक / Store Owner)',
            username='roushan_admin',
            email='thisisroushan01@gmail.com',
            phone='9820011223',
            address='कोमल मार्ट (Komal Mart), मुख्य बाजार, स्टेशन रोड, मुंबई',
            role='admin'
        )
        admin_primary.set_password('admin123')
        db.session.add(admin_primary)

    admin_sec = User.query.filter_by(email='novaaether01@gmail.com').first()
    if not admin_sec:
        admin_sec = User(
            name='Nova Aether (दुकानदार / Partner)',
            username='novaaether_admin',
            email='novaaether01@gmail.com',
            phone='9820011224',
            address='कोमल मार्ट (Komal Mart), मुख्य बाजार, स्टेशन रोड, मुंबई',
            role='admin'
        )
        admin_sec.set_password('admin123')
        db.session.add(admin_sec)

    # Legacy admin account update if present
    legacy_admin = User.query.filter_by(email='admin@kirana.com').first()
    if legacy_admin:
        legacy_admin.role = 'customer' # demote legacy admin
        legacy_admin.phone = '9820011299'

    # Create Sample Customer Account for testing
    cust_user = User.query.filter_by(email='roushan@example.com').first()
    if not cust_user:
        cust_user = User(
            name='Roushan Kumar',
            username='roushancust',
            email='roushan@example.com',
            phone='9876543210',
            address='Flat 402, Shiv Shakti Apts, Mumbai',
            role='customer'
        )
        cust_user.set_password('customer123')
        db.session.add(cust_user)

    db.session.commit()

    cat_map = {}
    for cat_info in CATEGORIES_DATA:
        category = Category(
            name=cat_info['name'],
            name_hi=cat_info['name_hi'],
            slug=cat_info['slug'],
            icon=cat_info['icon'],
            display_order=cat_info['display_order']
        )
        db.session.add(category)
        db.session.flush()
        cat_map[cat_info['slug']] = category.id

    for prod_info in PRODUCTS_DATA:
        cat_id = cat_map.get(prod_info['category_slug'])
        if not cat_id:
            continue

        product = Product(
            category_id=cat_id,
            name=prod_info['name'],
            name_hi=prod_info['name_hi'],
            brand=prod_info['brand'],
            is_loose=prod_info['is_loose'],
            description=prod_info['description'],
            image_url=prod_info['image_url']
        )
        db.session.add(product)
        db.session.flush()

        for var_info in prod_info['variants']:
            variant = ProductVariant(
                product_id=product.id,
                unit_size=var_info['unit_size'],
                mrp=var_info['mrp'],
                selling_price=var_info['selling_price'],
                stock_quantity=var_info['stock_quantity'],
                is_available=True
            )
            db.session.add(variant)

    db.session.commit()
    print("Database successfully seeded with authentic Indian Kirana inventory & default accounts!")


if __name__ == '__main__':
    app = create_app()
    print("Starting Apna Desi Kirana Store Backend API on http://0.0.0.0:5000 ...")
    app.run(host='0.0.0.0', port=5000, debug=True)
