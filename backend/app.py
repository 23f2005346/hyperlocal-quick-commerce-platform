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
import urllib.parse
import base64
import hashlib
import hmac
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from functools import wraps
from datetime import datetime, timedelta
from flask import Flask, jsonify, request, send_from_directory, send_file, Response
from flask_cors import CORS
from itsdangerous import URLSafeTimedSerializer, SignatureExpired, BadSignature
from sqlalchemy import event
from sqlalchemy.engine import Engine
from models import db, User, Category, Product, ProductVariant, Order, OrderItem, KhataPayment, TieredPricing, RestockAlert, SupportTicket, get_ist_time
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
CUSTOMER_RESET_STORE = {} # { reset_key: { 'otp': '123456', 'expires_at': ts, 'user_id': id, 'attempts': 0, 'channel': 'sms'|'email' } }
REGISTRATION_OTP_STORE = {} # { phone: { 'otp': '123456', 'expires_at': ts, 'attempts': 0, 'last_sent': ts } }
RESET_RATE_LIMIT_STORE = {} # { key: [timestamps] }
RESET_COOLDOWN_STORE = {}   # { key: last_request_timestamp }
LOGIN_ATTEMPTS_STORE = {}   # { key: { 'attempts': int, 'locked_until': ts, 'first_attempt': ts } }
AI_SCAN_RATE_LIMIT_STORE = {} # { key: [timestamps] }

def check_ai_scan_rate_limit(client_ip: str, max_scans: int = 10, window_sec: int = 3600):
    """
    Sliding window rate limit for AI handwritten list image scanning:
    Allows max 10 image scan operations per IP/account per hour.
    Guards Gemini Vision API quota and prevents abusive spam.
    """
    now = time.time()
    history = [t for t in AI_SCAN_RATE_LIMIT_STORE.get(client_ip, []) if now - t < window_sec]
    if len(history) >= max_scans:
        wait_sec = int(window_sec - (now - history[0]))
        return False, wait_sec
    history.append(now)
    AI_SCAN_RATE_LIMIT_STORE[client_ip] = history
    return True, 0

# Lightweight In-Memory AI Metrics Buffer (Last 200 operations for 2-3 day testing telemetry)
AI_USAGE_METRICS = [] # [ { timestamp, ist_time, mode: 'photo'|'voice'|'text', image_count, engine, latency_ms, items_count, matched_count, quota_error: bool, error_msg } ]

def record_ai_metric(mode: str, engine: str, latency_ms: int, items_count: int = 0, matched_count: int = 0, image_count: int = 0, quota_error: bool = False, error_msg: str = None):
    try:
        now_ts = time.time()
        ist_str = datetime.fromtimestamp(now_ts).strftime('%d %b %Y, %I:%M:%S %p')
        metric = {
            'timestamp': now_ts,
            'ist_time': ist_str,
            'mode': mode,
            'engine': engine,
            'latency_ms': latency_ms,
            'items_count': items_count,
            'matched_count': matched_count,
            'image_count': image_count,
            'quota_error': quota_error,
            'error_msg': error_msg
        }
        AI_USAGE_METRICS.append(metric)
        if len(AI_USAGE_METRICS) > 200:
            AI_USAGE_METRICS.pop(0)
    except Exception as e:
        print(f"[AI METRIC LOGGING ERROR] {e}")

def check_login_rate_limit(key):
    """
    Blocks more than 5 failed login attempts within 15 minutes per IP/identifier.
    Returns (is_allowed, wait_seconds).
    """
    now = time.time()
    record = LOGIN_ATTEMPTS_STORE.get(key)
    if not record:
        return True, 0

    locked_until = record.get('locked_until', 0)
    if now < locked_until:
        return False, int(locked_until - now)

    # If 15 minutes passed since first attempt, reset tracking
    if now - record.get('first_attempt', 0) > 900:
        LOGIN_ATTEMPTS_STORE.pop(key, None)
        return True, 0

    return True, 0

def record_login_failure(key):
    now = time.time()
    record = LOGIN_ATTEMPTS_STORE.get(key)
    if not record or (now - record.get('first_attempt', 0) > 900):
        LOGIN_ATTEMPTS_STORE[key] = {
            'attempts': 1,
            'locked_until': 0,
            'first_attempt': now
        }
    else:
        record['attempts'] += 1
        if record['attempts'] >= 5:
            record['locked_until'] = now + 900 # 15-minute lock

def record_login_success(key):
    LOGIN_ATTEMPTS_STORE.pop(key, None)

FAST2SMS_API_KEY = os.environ.get('FAST2SMS_API_KEY', '').strip()

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
 
def check_reset_rate_limit(account_key: str, client_ip: str):
    """
    Guards Resend free-tier quota (100 emails/day) and prevents spam.
    - Cooldown: 60 seconds minimum between requests for the same account.
    - Hourly Account Cap: Maximum 3 OTP requests per account per hour.
    - Hourly IP Cap: Maximum 8 OTP requests per IP per hour.
    Returns (allowed: bool, wait_seconds: int, error_code: str)
    """
    now = time.time()
    account_key = str(account_key)
    # 1. Cooldown check (60s)
    last_req = RESET_COOLDOWN_STORE.get(account_key, 0)
    if now - last_req < 60:
        return False, int(60 - (now - last_req)), 'COOLDOWN_ACTIVE'

    # 2. Account rate limit (last 1 hour = 3600s)
    user_history = [t for t in RESET_RATE_LIMIT_STORE.get(account_key, []) if now - t < 3600]
    if len(user_history) >= 3:
        return False, int(3600 - (now - user_history[0])), 'ACCOUNT_RATE_LIMIT'

    # 3. IP rate limit
    ip_history = [t for t in RESET_RATE_LIMIT_STORE.get(client_ip, []) if now - t < 3600]
    if len(ip_history) >= 8:
        return False, int(3600 - (now - ip_history[0])), 'IP_RATE_LIMIT'

    # Record attempt
    user_history.append(now)
    RESET_RATE_LIMIT_STORE[account_key] = user_history
    RESET_COOLDOWN_STORE[account_key] = now
    ip_history.append(now)
    RESET_RATE_LIMIT_STORE[client_ip] = ip_history

    return True, 0, None
def send_fast2sms_otp(phone: str, otp: str):
    """
    DISPATCH GUARD: External SMS calls disabled to strictly protect Fast2SMS wallet balance.
    Prints OTP to server console / dev logs without incurring any charges.
    """
    clean_phone = re.sub(r'\D', '', str(phone))
    if len(clean_phone) == 12 and clean_phone.startswith('91'):
        clean_phone = clean_phone[2:]

    print(f"\n[FAST2SMS GUARD ACTIVE - 0 COST] Verification Code for {clean_phone}: {otp}")
    print("[FAST2SMS GUARD] External API call halted to preserve wallet balance.\n")
    return True, "OTP generated (Balance protected)"

def get_fast2sms_balance():
    """Fetches remaining wallet balance and SMS credits from Fast2SMS."""
    api_key = os.environ.get('FAST2SMS_API_KEY', '').strip()
    if not api_key:
        return {'configured': False, 'wallet': '0.00', 'sms_count': 0}
    try:
        req = urllib.request.Request(
            "https://www.fast2sms.com/dev/wallet",
            headers={
                "authorization": api_key,
                "User-Agent": "KomalMart/1.0"
            }
        )
        with urllib.request.urlopen(req, timeout=8.0) as resp:
            data = json.loads(resp.read().decode('utf-8', errors='replace'))
            if data.get('return') is True:
                return {
                    'configured': True,
                    'wallet': str(data.get('wallet', '0.00')),
                    'sms_count': int(data.get('sms_count', 0))
                }
    except Exception as e:
        print(f"[FAST2SMS WALLET ERROR] {e}")
    return {'configured': True, 'wallet': 'Error', 'sms_count': 0}

SEARCH_ALIASES = {
    # Rice / Grains
    'rice': ['rice', 'chawal', 'chaawal', 'tandul', 'taandul', 'tandur', 'bhat', 'basmati', 'kolam', 'चावल', 'तांदूळ', 'भात', 'बासमती'],
    'chawal': ['rice', 'chawal', 'chaawal', 'tandul', 'taandul', 'tandur', 'bhat', 'basmati', 'चावल', 'तांदूळ'],
    'chaawal': ['rice', 'chawal', 'chaawal', 'tandul', 'taandul', 'tandur', 'bhat', 'basmati', 'चावल', 'तांदूळ'],
    'tandul': ['rice', 'tandul', 'taandul', 'tandur', 'chawal', 'bhat', 'kolam', 'तांदूळ', 'चावल'],
    'taandul': ['rice', 'tandul', 'taandul', 'tandur', 'chawal', 'bhat', 'kolam', 'तांदूळ', 'चावल'],
    'tandur': ['rice', 'tandul', 'taandul', 'tandur', 'chawal', 'bhat', 'kolam', 'तांदूळ', 'चावल'],
    'bhat': ['rice', 'chawal', 'tandul', 'tandur', 'भात', 'चावल'],
    'kolam': ['kolam', 'rice', 'कोलम', 'तांदूळ'],
    'basmati': ['basmati', 'rice', 'chawal', 'बासमती', 'दावत', 'daawat'],

    # Whole Wheat Grains (अखंड गहू / गेहूं दाना)
    'wheat': ['wheat', 'gehu', 'gehun', 'gahu', 'अखंड गहू', 'गहू', 'गेहूं', 'wheat grain'],
    'gehu': ['gehu', 'gehun', 'wheat', 'gahu', 'अखंड गहू', 'गहू', 'गेहूं', 'wheat grain'],
    'gehun': ['gehu', 'gehun', 'wheat', 'gahu', 'अखंड गहू', 'गहू', 'गेहूं', 'wheat grain'],
    'gahu': ['gahu', 'gehu', 'gehun', 'wheat', 'अखंड गहू', 'गहू', 'गेहूं', 'wheat grain'],
    'lokwan': ['lokwan', 'लोकवन'],
    'sharbati': ['sharbati', 'शरबती', 'सीहोर'],
    'tukdi': ['tukdi', 'तुकडी', 'bhalia', 'भालिया'],

    # Atta / Flours (पीठ / आटा)
    'atta': ['atta', 'aata', 'pith', 'peeth', 'flour', 'chakki', 'aashirvaad', 'fortune', 'आटा', 'पीठ'],
    'aata': ['atta', 'aata', 'pith', 'peeth', 'flour', 'chakki', 'आटा', 'पीठ'],
    'pith': ['atta', 'pith', 'peeth', 'flour', 'पीठ', 'आटा'],
    'peeth': ['atta', 'pith', 'peeth', 'flour', 'पीठ', 'आटा'],
    'chakki': ['chakki', 'atta', 'aata', 'चक्की', 'आटा'],
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
    'sugar': ['sugar', 'chini', 'cheeni', 'shakkar', 'saakhar', 'sakhar', 'madhur', 'साखर', 'चीनी', 'शक्कर'],
    'cheeni': ['sugar', 'chini', 'cheeni', 'shakkar', 'saakhar', 'sakhar', 'madhur', 'चीनी', 'साखर', 'शक्कर'],
    'chini': ['sugar', 'chini', 'cheeni', 'shakkar', 'saakhar', 'sakhar', 'madhur', 'चीनी', 'साखर', 'शक्कर'],
    'shakkar': ['sugar', 'shakkar', 'chini', 'cheeni', 'saakhar', 'sakhar', 'madhur', 'शक्कर', 'साखर', 'चीनी'],
    'saakhar': ['sugar', 'saakhar', 'sakhar', 'chini', 'cheeni', 'shakkar', 'madhur', 'साखर', 'चीनी'],
    'sakhar': ['sugar', 'saakhar', 'sakhar', 'chini', 'cheeni', 'shakkar', 'madhur', 'साखर', 'चीनी'],
    'madhur': ['madhur', 'sugar', 'sakhar', 'chini', 'cheeni', 'साखर', 'चीनी'],
    'haldi': ['haldi', 'halad', 'turmeric', 'हळद', 'हल्दी'],
    'halad': ['haldi', 'halad', 'turmeric', 'हळद', 'हल्दी'],
    'turmeric': ['turmeric', 'haldi', 'halad', 'हळद', 'हल्दी'],
    'mirchi': ['mirch', 'mirchi', 'chilli', 'chili', 'tikhat', 'तिखट', 'मिर्च'],
    'mirch': ['mirch', 'mirchi', 'chilli', 'tikhat', 'मिर्च', 'तिखट'],
    'tikhat': ['mirch', 'mirchi', 'tikhat', 'तिखट', 'मिर्च'],
    'chilli': ['mirch', 'mirchi', 'tikhat', 'chilli', 'मिर्च'],
    'chili': ['mirch', 'mirchi', 'tikhat', 'chili', 'मिर्च'],
    'masala': ['masala', 'everest', 'garam masala', 'मसाला', 'खडा मसाला'],
    'garam masala': ['garam masala', 'khada masala', 'मिश्र खडा गरम मसाला', 'गरम मसाला', 'masala', 'everest'],
    'jeera': ['jeera', 'jira', 'zeera', 'cumin', 'जिरं', 'जीरा', 'खड़ा जीरा'],
    'jira': ['jeera', 'jira', 'zeera', 'cumin', 'जिरं', 'जीरा', 'खड़ा जीरा'],
    'zeera': ['jeera', 'jira', 'zeera', 'cumin', 'जिरं', 'जीरा'],
    'kali mirch': ['kali mirch', 'kalimirch', 'black pepper', 'pepper', 'काळी मिरी', 'काली मिर्च', 'मिरी'],
    'miri': ['kali mirch', 'kalimirch', 'black pepper', 'काळी मिरी', 'काली मिर्च', 'मिरी'],
    'elaichi': ['elaichi', 'elachi', 'cardamom', 'velchi', 'वेलची', 'इलायची', 'छोटी इलायची'],
    'velchi': ['elaichi', 'elachi', 'cardamom', 'velchi', 'वेलची', 'इलायची'],
    'soyabean': ['soyabean', 'soya', 'soya dana', 'सोयाबीन', 'सोयाबीन दाना'],
    'soya': ['soyabean', 'soya', 'soya dana', 'सोयाबीन', 'सोयाबीन दाना'],
    'pisai': ['pisai', 'pisva', 'pisun', 'dalne', 'daloon', 'dalwan', 'chakki pisai', 'दळण', 'पिसाई'],
    'dalne': ['pisai', 'dalne', 'daloon', 'chakki pisai', 'दळण', 'पिसाई'],
    'chakki pisai': ['chakki pisai', 'pisai', 'dalne', 'दळण', 'पिसाई'],
    'dhania': ['dhania', 'dhaniya', 'coriander', 'धने', 'धनिया', 'dhana powder', 'masala'],
    'dhaniya': ['dhania', 'dhaniya', 'coriander', 'धने', 'धनिया', 'dhana powder', 'masala'],

    # Tea / Beverages
    'tea': ['tea', 'chai', 'chaha', 'चहा', 'चाय', 'tata tea', 'red label', 'wagh bakri', 'taj mahal'],
    'chai': ['tea', 'chai', 'chaha', 'चाय', 'चहा', 'tata tea', 'red label'],
    'chaha': ['tea', 'chai', 'chaha', 'चहा', 'चाय', 'tata tea'],
    'coffee': ['coffee', 'कॉफी'],

    # Cleaning & Oral Care
    'soap': ['soap', 'sabun', 'saabun', 'साबण', 'साबुन', 'dettol', 'lux', 'lifebuoy', 'margo', 'moti', 'rin'],
    'sabun': ['soap', 'sabun', 'saabun', 'साबण', 'साबुन', 'dettol', 'lux', 'lifebuoy', 'margo', 'moti', 'rin'],
    'saabun': ['soap', 'sabun', 'साबण', 'साबुन'],
    'lux': ['lux', 'soap', 'लक्स'],
    'lifebuoy': ['lifebuoy', 'soap', 'लाइफबॉय'],
    'margo': ['margo', 'neem soap', 'मार्गो'],
    'moti': ['moti', 'sandal soap', 'मोती'],
    'detergent': ['detergent', 'surf', 'surf excel', 'powder', 'सर्फ', 'डिटर्जंट'],
    'surf': ['surf', 'surf excel', 'detergent', 'powder', 'सर्फ'],
    'rin': ['rin', 'bar', 'साबण', 'रिन'],
    'vim': ['vim', 'dishwash', 'व्हिम', 'विम', 'bar'],
    'paste': ['toothpaste', 'paste', 'colgate', 'sensodyne', 'dabur', 'patanjali', 'टूथपेस्ट', 'पेस्ट'],
    'toothpaste': ['toothpaste', 'paste', 'colgate', 'sensodyne', 'dabur', 'patanjali', 'टूथपेस्ट'],
    'colgate': ['colgate', 'toothpaste', 'कोलगेट'],
    'dant': ['dant', 'dantmanjan', 'dant kanti', 'दंत', 'पतंजली', 'डाबर', 'toothpaste'],
    'dettol': ['dettol', 'soap', 'डेटॉल'],

    # Dry Fruits
    'badam': ['badam', 'almond', 'almonds', 'बदाम', 'california badam'],
    'almond': ['badam', 'almond', 'almonds', 'बदाम'],
    'kaju': ['kaju', 'cashew', 'cashews', 'काजू', 'goa kaju'],
    'cashew': ['kaju', 'cashew', 'cashews', 'काजू'],
    'kishmish': ['kishmish', 'raisin', 'raisins', 'bedana', 'मनुका', 'बेदाणा', 'किशमिश'],
    'makhana': ['makhana', 'foxnut', 'foxnuts', 'मखाना', 'phool makhana'],
    'akhrot': ['akhrot', 'walnut', 'walnuts', 'अक्रोड'],
    'pista': ['pista', 'pistachio', 'पिस्ता'],

    # Biscuits & Bakery
    'parle': ['parle-g', 'parle g', 'parleg', 'parle', 'पारले', 'पारले-जी'],
    'parle g': ['parle-g', 'parle g', 'parleg', 'पारले-जी'],
    'good day': ['good day', 'goodday', 'गुड डे'],
    'marie': ['marie gold', 'marie', 'मेरी गोल्ड'],
    'krackjack': ['krackjack', 'krack jack', 'क्रॅकजॅक'],
    'monaco': ['monaco', 'मोनाको'],
    'bourbon': ['bourbon', 'बॉर्बन'],
    'toast': ['toast', 'rusk', 'टोस्ट', 'रस्क'],
    'rusk': ['toast', 'rusk', 'टोस्ट', 'रस्क'],

    # Beverages & Cold Drinks
    'thums up': ['thums up', 'thumsup', 'thumbs up', 'थम्स अप'],
    'thumsup': ['thums up', 'thumsup', 'thumbs up', 'थम्स अप'],
    'sprite': ['sprite', 'स्प्राइट'],
    'coke': ['coca-cola', 'coca cola', 'coke', 'कोका-कोला'],
    'coca cola': ['coca-cola', 'coca cola', 'coke', 'कोका-कोला'],
    'maaza': ['maaza', 'माझा', 'mango juice'],
    'bisleri': ['bisleri', 'water', 'पाणी', 'बिसलेरी'],

    # Specific Oils & Grains
    'gemini': ['gemini', 'जेमिनी', 'sunflower oil', 'सूर्यफूल तेल'],
    'priya': ['priya', 'प्रिया', 'groundnut oil', 'शेंगदाणा तेल'],
    'palmolein': ['palmolein', 'palm oil', 'पामोलिन'],
    'lokwan': ['lokwan', 'लोकवन', 'लोकवन अखंड गहू'],
    'sharbati': ['sharbati', 'शरबती', 'सीहोर शरबती'],
    'tukdi': ['tukdi', 'bhalia', 'तुकडी', 'भालिया'],
    'kolam': ['wada kolam', 'surti kolam', 'kolam', 'कोलम'],
    'sabudana': ['sabudana', 'साबुदाणा'],
    'kurmura': ['kurmura', 'murmura', 'चुरमुरे', 'कुरमुरे'],
    'gud': ['gud', 'jaggery', 'gul', 'गूळ', 'गुड']
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

def parse_unit_weight_in_kg(unit_size):
    """
    Parses unit strings (e.g. '500g', '1kg', '2kg', '5kg', '30kg Bori', '250g', '100g', '1L', '5L', '500ml')
    into standardized weight/volume in kg or liters.
    Returns None for fixed cash denomination packs ('₹10 Pouch') or non-weight units.
    """
    if not unit_size:
        return None
    s = str(unit_size).strip().lower()
    if '₹' in s or 'rs' in s or 'pack of' in s or 'sachet' in s or 'bar' in s or 'tube' in s:
        return None

    # Match kg / kilo
    m_kg = re.search(r'(\d+(?:\.\d+)?)\s*(?:kg|kilo|किलो|कि\.ग्रॅ)', s)
    if m_kg:
        try:
            return float(m_kg.group(1))
        except (ValueError, TypeError):
            pass

    # Match g / gm / gram
    m_g = re.search(r'(\d+(?:\.\d+)?)\s*(?:g|gm|gms|gram|grams|ग्रॅम|ग्राम)', s)
    if m_g:
        try:
            return float(m_g.group(1)) / 1000.0
        except (ValueError, TypeError):
            pass

    # Match liter / L
    m_l = re.search(r'(\d+(?:\.\d+)?)\s*(?:l|litre|liter|लीटर|लिटर)', s)
    if m_l:
        try:
            return float(m_l.group(1))
        except (ValueError, TypeError):
            pass

    # Match ml
    m_ml = re.search(r'(\d+(?:\.\d+)?)\s*(?:ml|मि\.ली)', s)
    if m_ml:
        try:
            return float(m_ml.group(1)) / 1000.0
        except (ValueError, TypeError):
            pass

    return None

def call_gemini_order_parser(raw_text, catalog_snapshot, language='mr', audio_data=None, mime_type='audio/webm', images_data=None):
    """
    Parses natural language grocery order text, recorded audio, or uploaded handwritten list photos
    (Hindi, Marathi, English, or mixed) against the active Komal Mart catalog using Google Gemini AI Studio API.
    Implements a resilient model fallback cascade:
    1. gemini-flash-lite-latest (fastest, lowest token overhead)
    2. gemini-flash-latest
    3. gemini-3.8-flash (flagship multimodal speed and accuracy)
    4. gemini-3.7-flash / gemini-3.6-flash / gemini-3.5-flash
    """
    api_key = os.environ.get('GEMINI_API_KEY', '').strip()
    if not api_key:
        return False, None, "GEMINI_API_KEY not configured"

    models_to_try = [
        'gemini-flash-lite-latest',
        'gemini-flash-latest',
        'gemini-3.8-flash',
        'gemini-3.7-flash',
        'gemini-3.6-flash',
        'gemini-3.5-flash',
        'gemini-3.5-flash-lite',
        'gemini-2.5-flash',
        'gemini-2.5-flash-lite'
    ]

    if raw_text:
        raw_text = raw_text.translate(str.maketrans('०१२३४५६७८९', '0123456789'))

    system_instruction = (
        "You are Komal, the intelligent grocery order parsing assistant for Komal Mart (कोमल मार्ट), "
        "a hyperlocal neighborhood general store (kirana) in Wadala, Mumbai.\n"
        "Your task: Parse customer spoken, typed, or photographed handwritten grocery order lists "
        "(in Marathi, Hindi, English, or Hinglish) and accurately match each requested grocery commodity "
        "to the provided Komal Mart catalog snapshot.\n\n"
        "Rules & Invariants:\n"
        "1. Quantities, Vernacular Units & Compound Fractions:\n"
        "   - 'aadha kilo' / 'ardha kilo' / 'half kg' -> 0.5 kg or 500g\n"
        "   - 'pav kilo' / 'paav' / 'quarter kg' -> 0.25 kg or 250g\n"
        "   - 'paun kilo' / 'pauna kilo' / 'paune' / 'paavne ek' / 'पाऊण' / 'पावणा' / 'पावना' / 'पौना' / 'पौने' / 'पन किलो' / 'पान किलो' / 'पोन किलो' / 'pan kilo' -> 0.75 kg or 750g\n"
        "   - 'dedh kilo' / 'deedh' -> 1.5 kg\n"
        "   - 'sawa kilo' -> 1.25 kg\n"
        "   - 'dhai kilo' -> 2.5 kg\n"
        "   - 'sawa X' / 'sawwa X' -> (X + 0.25) kg (e.g. 'sawa 8 kilo' = 8.25 kg, 'sawa 2' = 2.25 kg)\n"
        "   - 'sadhe X' / 'saade X' -> (X + 0.50) kg (e.g. 'sadhe 3 kilo' = 3.5 kg, 'sadhe 4 kilo' = 4.5 kg, 'sadhe 5' = 5.5 kg)\n"
        "   - 'paune X' / 'paawne X' -> (X - 0.25) kg (e.g. 'paune 6 kilo' / 'paune 6' = 5.75 kg, 'paune 8 kilo' = 7.75 kg, 'paune 5' = 4.75 kg)\n"
        "   - 'ek packet' / 'don packet' -> 1 or 2 packet/units\n"
        "2. Rupee-Budget Purchases (e.g. '10 rupaye ka masala', '10 ki elaichi', '50 ka jira', '60 ki kali mirch'):\n"
        "   - Customers frequently buy spices by rupee amounts rather than weight: e.g. '10 rupaye ka', '10 ki', '50 ka', '60 ki', '20 ka'.\n"
        "   - When customer states a rupee amount for a spice or grocery item:\n"
        "     a) Match the variant with that exact rupee price (e.g., '₹10 Counter Pouch', '₹20 Counter Pouch', '₹50 Pouch', '₹60 Pouch') with quantity = 1 and match_status = 'matched'. NEVER mark ambiguous when an exact rupee pouch exists!\n"
        "     b) If no exact pouch variant exists, select the loose or smallest pack with proportional quantity matching that rupee budget.\n"
        "3. Whole Wheat Chakki Pisai & Soyabean Grain Mix Service:\n"
        "   - When customer orders whole wheat with grinding/milling (e.g. '10 kilo gehu pisai karke dena', 'gehu dalwa ke bhejna', 'gehu pisai ke sath', 'pisai karke'):\n"
        "     a) Match the Whole Wheat Grain (Lokwan or Sharbati Whole Wheat Grain) for the stated weight (e.g. 10 kg).\n"
        "     b) Add the 'Chakki Pisai Grinding Service' line item with quantity matching the wheat weight (quantity = 10, unit_price = 7.0, line_total = 70.0).\n"
        "   - If customer asks to add/mix soyabean into the wheat (e.g. 'usme 100 gram / 200 gram soyabean mix kar dena' or 'soyabean dal dena'):\n"
        "     Match 'Whole Soyabean Grain for Flour Mixing' with the requested quantity (e.g. 100g or 200g pack).\n"
        "4. Accurate Variant Multiplier Matching (CRITICAL - NEVER USE FRACTIONAL PACK MULTIPLIERS):\n"
        "   - When customer asks for a specific total weight or count (e.g. '2 kilo aata', '3 kilo chini', '4 kilo chawal', '5 kilo chakki atta', '6 kilo gehun', '500g toor daal', '250g haldi'):\n"
        "     a) For LOOSE staple commodities (is_loose is true, like loose atta, sugar, rice, dal, besan, poha, maida):\n"
        "        When ordered in whole integer kilograms (1kg, 2kg, 3kg, 4kg, 5kg, 10kg, etc.), ALWAYS choose the base 1KG VARIANT and set quantity equal to that integer weight (e.g. 5kg chakki atta -> base 1kg variant with quantity = 5; 2kg sugar -> base 1kg variant with quantity = 2).\n"
        "        This ensures the counter stepper matches the exact kilograms the customer ordered (5 for 5kg, 2 for 2kg) across all loose products identically!\n"
        "     b) For BRANDED packaged goods (is_loose is false, e.g. Aashirvaad 5kg bag, Fortune 5L can) or small packaged spices/pouches (e.g. 250g haldi, 500g dal):\n"
        "        If an exact pack size matches that amount, match that EXACT variant with quantity = 1.\n"
        "     c) If no single variant matches that exact weight:\n"
        "        Choose the standard BASE 1KG VARIANT and set quantity equal to that weight in integer kgs (e.g. quantity = 3 for 3 kilo, quantity = 4 for 4 kilo).\n"
        "        NEVER pick a 2kg or 5kg variant and set a fractional quantity like 1.5 or 0.8! Always use integer multiples of the 1kg variant!\n"
        "     d) For half-kg fractions (e.g. '1.5 kilo', '2.5 kilo'): if a 500g variant exists, use it (quantity = 3 or 5), or use 1kg variant with 1.5. NEVER assign 1.5 to a 2kg variant!\n"
        "     e) Packaged FMCG & Bathing Soaps (e.g. 'ek dettol sabun', '2 lux', '3 lifebuoy', 'dettol ka 4 pack', 'lux ka 4+1 pack'):\n"
        "        - If customer asks for single bars or count: choose the SINGLE BAR variant (e.g. '75g Single Bar' or '100g Bar') with quantity = count (1, 2, 3).\n"
        "        - If customer asks for a pack/multipack: choose the MULTIPACK variant (e.g. 'Pack of 4 x 75g' or 'Pack of 4') with quantity = number of packs.\n"
        "     Set match_status to 'matched'. NEVER set match_status to 'ambiguous' when customer explicitly specified a weight or count!\n"
        "5. Spoken Corrections, Quantity Updates & Removals (CRITICAL):\n"
        "   - Customers often correct themselves while reciting a monthly list: e.g. '5 kg toor daal, 2 kilo aata, 3 kilo chini... oh wait can you do aata 12kg, 2 kilo nahi' or 'chini mat lena / chini cancel'.\n"
        "   - Quantity Updates / Corrections: When customer updates an item's quantity (e.g. 'aata 12kg, 2 kilo nahi' or 'pehla 2 kilo bola tha ab 12 kilo kardo'): use ONLY the final corrected quantity (12kg, NOT 2kg)! Emit only ONE entry for that commodity with quantity=12.\n"
        "   - Item Cancellations / Negations: When customer cancels or removes an item (e.g. 'X nahi chahiye', 'X mat lo', 'X cancel', 'X nako', 'hata do', 'remove X'): do NOT include X in the items array! Exclude canceled items completely.\n"
        "   - Deduplicate stuttered speech & repeated numbers: If speech recognition repeats a number or word (e.g., '9 9 kilo maida', '5 5 kg chawal', 'sugar... 2 kilo chini'), treat it as a single quantity ('9 kilo maida', '5 kg chawal', '2 kilo chini'). NEVER add or multiply duplicated stuttered numbers! Emit only ONE entry for that commodity with the intended quantity.\n"
        "6. Handwritten Slip / Photo Invariants (CRITICAL FOR VISION SCANS):\n"
        "   - Crossed-out / Struck-through Items: If any word or line on a handwritten paper slip is struck through, crossed out with a pen line (e.g., ~~साखर~~ or scribbled over), EXCLUDE it completely. Do not include canceled items in the items array.\n"
        "   - Ignore Customer Handwritten Prices: Customers often write estimated prices or previous bill amounts next to items (e.g., 'चावल 60', 'तेल ₹140', 'दाल 120'). IGNORE any handwritten currency numbers or estimated rupee prices completely! Extract ONLY the commodity name and requested weight or quantity. Prices are assigned strictly by the store catalog.\n"
        "   - Multi-Page / Multi-Photo Slips: When multiple images are provided, combine all items across all pages into a single consolidated grocery list without repeating headers.\n"
        "   - Irrelevant or Unreadable Photos: If the attached image does NOT contain a readable grocery or shopping list (e.g., random selfie, vehicle, meme, scenery, or completely illegible/blank photo), set transcript to 'या फोटोमध्ये किराणा सामानाची यादी आढळली नाही.' and return an EMPTY items array: [] with summary_text explaining that a clear photo of the grocery list is needed.\n"
        "7. Kirana Commodity & Grain Disambiguation (CRITICAL):\n"
        "   - 'wheat' / 'gehun' / 'gahu' / 'whole wheat' refers to WHOLE GRAIN WHEAT ('गहू' / 'Sharbati Whole Wheat Grain' or 'Lokwan Whole Wheat Grain'), NOT wheat flour.\n"
        "   - 'atta' / 'aata' / 'pith' / 'peeth' / 'chakki atta' / 'flour' refers to WHEAT FLOUR ('आटा' / 'पीठ' / 'Chakki Fresh Wheat Atta').\n"
        "   - When a customer orders BOTH wheat grain and flour (e.g., '6 kilo wheat and 3 kilo aata'), they are TWO DISTINCT items: match wheat to Whole Wheat Grain and aata to Wheat Atta. NEVER combine or drop either.\n"
        "   - 'tandur' / 'tandul' / 'taandul' / 'chawal' / 'chaawal' -> Rice ('तांदूळ' / 'चावल'). ('tandur' is vernacular Mumbai/Marathi spoken pronunciation for 'tandul').\n"
        "   - 'chini' / 'cheeni' / 'sakhar' / 'saakhar' / 'sugar' / 'shakkar' -> Sugar ('साखर' / 'चीनी'). Match to Madhur Sugar or Loose White Sugar.\n"
        "   - 'jeera' / 'jira' / 'cumin' / 'जिरं' / 'जीरा' -> Whole Jeera / Cumin Seeds.\n"
        "   - 'kali mirch' / 'miri' / 'black pepper' / 'काळी मिरी' / 'काली मिर्च' -> Whole Kali Mirch / Black Pepper.\n"
        "   - 'elaichi' / 'elachi' / 'velchi' / 'cardamom' / 'वेलची' / 'इलायची' -> Green Cardamom / Chhoti Elaichi.\n"
        "   - 'masala' / 'garam masala' / 'khada masala' -> Desi Khada Garam Masala or Everest Garam Masala.\n"
        "   - 'soyabean' / 'soya dana' / 'सोयाबीन' -> Whole Soyabean Grain for Flour Mixing.\n"
        "   - 'pisai' / 'dalwan' / 'chakki pisai' -> Chakki Pisai Grinding Service.\n"
        "8. Customer Preferences & Ambiguity Rules:\n"
        "   - If customer asks for 'sasta wala' / 'swasta' / 'kam daam' / 'regular': choose the variant with the lowest price.\n"
        "   - If customer asks for 'mehnga wala' / 'accha' / 'premium' / 'gavran' / 'unpolished': choose the higher quality/price variant.\n"
        "   - STRICT AMBIGUITY RULE: ONLY set match_status to 'ambiguous' if the customer named a commodity WITHOUT stating ANY quantity, weight, rupee amount, or size at all (e.g. customer literally said only 'aata' or 'oil' with zero quantity). If any quantity or rupee budget was stated, it is NEVER ambiguous!\n"
        "9. Out-of-Stock / Unavailable Items:\n"
        "   - If an item is not found in the catalog or has stock_quantity <= 0, set match_status to 'unavailable'. Preserve the customer's grocery item name in 'product_name' and 'query_term'. If there is a similar item in the same category, suggest it in 'suggested_alternative'.\n"
        "10. Exact Match:\n"
        "   - If product and variant are identified, set match_status to 'matched'.\n"
        "11. Output Format: Return strictly JSON matching the required schema with summary_text in Marathi, Hindi, and English.\n"
        "12. Long-Form Monthly Kirana Lists (20 to 30+ Items):\n"
        "   - Real household customers write or recite long 20 to 30 item ration lists in a single turn.\n"
        "   - You MUST parse every single commodity written across the entire list. Never stop or truncate after a few items.\n"
        "   - Support full grocery baskets: flours, rice, dals, oils, ghee, sugar, tea, spices, bath soaps, dish soaps, detergents, toothpastes, dry fruits, snacks."
    )

    if images_data and len(images_data) > 0:
        customer_input_desc = (
            f"Customer Handwritten Grocery List ({len(images_data)} image(s) attached):\n"
            "Carefully examine the attached photo(s) of handwritten or printed grocery list slips (in Marathi, Hindi, or English). "
            "Transcribe all readable grocery items and their written quantities verbatim into the 'transcript' field. "
            "Match every item accurately to the Komal Mart catalog snapshot."
        )
    elif audio_data and not raw_text:
        customer_input_desc = "Customer Order Speech (Audio Recording Attached):\nListen to the customer's spoken grocery recitation in audio. Transcribe the customer's spoken words into the 'transcript' field (in the language spoken: Marathi, Hindi, or English), and match all items to the catalog snapshot."
    elif audio_data and raw_text:
        customer_input_desc = f"Customer Order Speech Transcript:\n\"{raw_text}\"\n(Raw audio recording is also attached for acoustic clarity. Transcribe full speech into 'transcript' field if any words were omitted.)"
    else:
        customer_input_desc = f"Customer Order Speech/Text:\n\"{raw_text}\""

    prompt = f"""Catalog Snapshot:
{json.dumps(catalog_snapshot, ensure_ascii=False)}

{customer_input_desc}

Return JSON matching this exact structure:
{{
  "transcript": "string (verbatim customer speech or transcribed handwritten list)",
  "items": [
    {{
      "query_term": "string (what customer called it)",
      "product_id": 1,
      "variant_id": 101,
      "product_name": "string",
      "unit_size": "string",
      "quantity": 1,
      "price": 45.0,
      "match_status": "matched",
      "options": [],
      "suggested_alternative": null
    }}
  ],
  "summary_text_mr": "string (1 brief natural Marathi sentence)",
  "summary_text_hi": "string (1 brief natural Hindi sentence)",
  "summary_text_en": "string (1 brief natural English sentence)"
}}
"""

    last_error = None
    for model in models_to_try:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={api_key}"
        parts = [
            {"text": system_instruction},
            {"text": prompt}
        ]
        if audio_data:
            parts.append({
                "inlineData": {
                    "mimeType": mime_type or "audio/webm",
                    "data": audio_data
                }
            })
        if images_data:
            for img_obj in images_data:
                if isinstance(img_obj, dict) and img_obj.get('data'):
                    parts.append({
                        "inlineData": {
                            "mimeType": img_obj.get('mimeType', 'image/jpeg'),
                            "data": img_obj.get('data')
                        }
                    })

        payload = {
            "contents": [
                {
                    "parts": parts
                }
            ],
            "generationConfig": {
                "responseMimeType": "application/json",
                "temperature": 0.1
            }
        }
        try:
            req_data = json.dumps(payload).encode('utf-8')
            req = urllib.request.Request(url, data=req_data, headers={'Content-Type': 'application/json'})
            with urllib.request.urlopen(req, timeout=18) as response:
                result_raw = json.loads(response.read().decode('utf-8'))
                candidates = result_raw.get('candidates', [])
                if candidates and 'content' in candidates[0]:
                    text_out = candidates[0]['content']['parts'][0]['text']
                    data = json.loads(text_out)
                    return True, data, model
        except urllib.error.HTTPError as he:
            last_error = f"HTTP {he.code}: {he.reason}"
            print(f"[GEMINI CASCADE WARNING] Model {model} failed with {last_error}. Trying next model...")
            continue
        except Exception as e:
            last_error = str(e)
            print(f"[GEMINI CASCADE WARNING] Model {model} exception: {e}. Trying next model...")
            continue

    return False, None, last_error or "All cascade models failed"

def call_google_regional_tts(text, language='mr'):
    """
    Synthesizes natural, high-fidelity regional speech (Marathi / Hindi / English)
    using Google's regional voice synthesis engine.
    Produces authentic Indian regional accents, consumes zero Gemini API tokens,
    and returns universal MP3 audio (audio/mpeg).
    """
    if not text:
        return False, None, "No text provided"

    clean_lang = (language or 'mr').lower().strip()
    if clean_lang in ('hi', 'hin', 'hindi'):
        tl = 'hi'
    elif clean_lang in ('en', 'eng', 'english', 'en-in'):
        tl = 'en-IN'
    elif clean_lang in ('mr', 'mar', 'marathi'):
        tl = 'mr'
    else:
        tl = 'mr'

    try:
        clean_text = text.strip()
        if len(clean_text) <= 160:
            chunks = [clean_text]
        else:
            chunks = [c.strip() for c in re.split(r'[,।\n]', clean_text) if c.strip()]
            if not chunks:
                chunks = [clean_text[:160]]

        combined = bytearray()
        for ch in chunks[:6]:
            if not ch:
                continue
            q = urllib.parse.quote(ch[:160])
            url = f"https://translate.google.com/translate_tts?ie=UTF-8&tl={tl}&client=tw-ob&q={q}"
            req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'})
            with urllib.request.urlopen(req, timeout=5) as resp:
                data = resp.read()
                if data:
                    combined.extend(data)

        if len(combined) > 200:
            b64 = base64.b64encode(combined).decode('utf-8')
            return True, b64, 'audio/mpeg'
    except Exception as e:
        print(f"[GOOGLE REGIONAL TTS ERROR] {e}")

    return False, None, "Regional TTS failed"

def call_gemini_tts(text, voice='Kore', language='mr'):
    """
    Synthesizes natural, high-fidelity regional speech (Marathi / Hindi / English):
    1. Google Regional Voice Engine (default: instant ~250ms, zero-token, authentic Marathi/Hindi/English MP3)
    2. Gemini Studio Audio (optional: enabled via ENABLE_GEMINI_STUDIO_TTS=1)
    """
    # Check optional Gemini Studio TTS flag
    if os.environ.get('ENABLE_GEMINI_STUDIO_TTS', '0') == '1':
        api_key = os.environ.get('GEMINI_API_KEY', '').strip()
        if api_key and text:
            models = ['gemini-3.8-flash', 'gemini-3.7-flash', 'gemini-3.6-flash', 'gemini-3.5-flash', 'gemini-2.5-flash', 'gemini-2.0-flash']
            payload = {
                "contents": [{"parts": [{"text": text.strip()}]}],
                "generationConfig": {
                    "responseModalities": ["AUDIO"],
                    "speechConfig": {
                        "voiceConfig": {
                            "prebuiltVoiceConfig": {
                                "voiceName": voice or "Kore"
                            }
                        }
                    }
                }
            }
            req_data = json.dumps(payload).encode('utf-8')
            for m in models:
                url = f"https://generativelanguage.googleapis.com/v1beta/models/{m}:generateContent?key={api_key}"
                try:
                    req = urllib.request.Request(url, data=req_data, headers={'Content-Type': 'application/json'})
                    with urllib.request.urlopen(req, timeout=3) as resp:
                        res = json.loads(resp.read().decode('utf-8'))
                        candidates = res.get('candidates', [])
                        if candidates and 'content' in candidates[0]:
                            parts = candidates[0]['content'].get('parts', [])
                            for part in parts:
                                if 'inlineData' in part:
                                    audio_b64 = part['inlineData'].get('data')
                                    mime = part['inlineData'].get('mimeType', 'audio/wav')
                                    if audio_b64:
                                        return True, audio_b64, mime
                except urllib.error.HTTPError as he:
                    if he.code == 429:
                        break
                    continue
                except Exception:
                    continue

    # Instant Regional Voice Engine: Guaranteed zero-token, authentic regional pronunciation
    ok, b64, mime_or_err = call_google_regional_tts(text, language=language)
    if ok and b64:
        return True, b64, mime_or_err

    return False, None, "All TTS models failed"


def fallback_heuristic_order_parser(raw_text, all_products):
    """
    Offline heuristic rule-based Kirana order parser.
    Splits phrases and extracts quantities and products using SEARCH_ALIASES and Devanagari rules.
    Used when Gemini API hits daily rate limits or is offline.
    """
    items = []
    phrases = re.split(r'[,;|\n]+|\s+(?:आणि|ani|aur|और|तसेच|व|and)\s+', raw_text, flags=re.IGNORECASE)

    vernacular_nums = {
        'aadha': 0.5, 'adha': 0.5, 'ardha': 0.5, 'aradha': 0.5, 'half': 0.5, 'अर्धा': 0.5, 'आधा': 0.5,
        'pav': 0.25, 'paav': 0.25, 'paw': 0.25, 'pao': 0.25, 'quarter': 0.25, 'पाव': 0.25,
        'paun': 0.75, 'pauna': 0.75, 'paune': 0.75, 'पाऊण': 0.75, 'पावणा': 0.75, 'पावना': 0.75, 'पौना': 0.75, 'पौने': 0.75,
        'dedh': 1.5, 'deedh': 1.5, 'dhed': 1.5, 'dheed': 1.5, 'दीड': 1.5, 'डेढ़': 1.5,
        'dhai': 2.5, 'dhaee': 2.5, 'dhaai': 2.5, 'अडीच': 2.5, 'ढाई': 2.5,
        'sawa': 1.25, 'sawwa': 1.25, 'सव्वा': 1.25, 'सवा': 1.25,
        'saade': 0.5, 'sadhe': 0.5,
        'ek': 1, 'do': 2, 'teen': 3, 'char': 4, 'paanch': 5, 'panch': 5, 'don': 2,
        'एक': 1, 'दोन': 2, 'तीन': 3, 'चार': 4, 'पाच': 5, 'सहा': 6, 'सात': 7, 'आठ': 8, 'नऊ': 9, 'दहा': 10
    }

    for p in phrases:
        p_clean = p.strip()
        if not p_clean or len(p_clean) < 2:
            continue

        qty = 1.0

        # Check compound fractions (paune 6 -> 5.75, sawa 8 -> 8.25, sadhe 3 -> 3.5)
        paune_m = re.search(r'(?:paune|paawne|पौने|पावणे)\s*(\d+(?:\.\d+)?)', p_clean, flags=re.IGNORECASE)
        sawa_m = re.search(r'(?:sawa|sawwa|सवा|सव्वा)\s*(\d+(?:\.\d+)?)', p_clean, flags=re.IGNORECASE)
        sadhe_m = re.search(r'(?:sadhe|saade|साढ़े|साडे)\s*(\d+(?:\.\d+)?)', p_clean, flags=re.IGNORECASE)
        rupee_m = re.search(r'(?:₹|rs\.?|रु\.?)\s*(\d+)|(\d+)\s*(?:rupaye|rupayee|rs|rupee|रुपये|रूपये|रु|₹|की|का|ki|ka)', p_clean, flags=re.IGNORECASE)

        rupee_budget = None
        if rupee_m:
            try:
                rupee_budget = int(rupee_m.group(1) or rupee_m.group(2))
            except (ValueError, TypeError):
                pass

        if paune_m:
            try:
                qty = max(0.25, float(paune_m.group(1)) - 0.25)
            except ValueError:
                qty = 0.75
        elif sawa_m:
            try:
                qty = float(sawa_m.group(1)) + 0.25
            except ValueError:
                qty = 1.25
        elif sadhe_m:
            try:
                qty = float(sadhe_m.group(1)) + 0.50
            except ValueError:
                qty = 3.5
        elif rupee_budget:
            qty = 1.0
        # Standalone vernacular fractions (paun kilo, aadha kilo, pav kilo, etc.)
        elif re.search(r'(?:paun|pauna|paune|पाऊण|पावणा|पावना|पौना|पौने|पन|पान|पोन)\s*(?:kilo|kg|किलो)?', p_clean, flags=re.IGNORECASE):
            qty = 0.75
        elif re.search(r'(?:aadha|ardha|half|आधा|अर्धा)\s*(?:kilo|kg|किलो)?', p_clean, flags=re.IGNORECASE):
            qty = 0.5
        elif re.search(r'(?:pav|paav|quarter|पाव)\s*(?:kilo|kg|किलो)?', p_clean, flags=re.IGNORECASE):
            qty = 0.25
        elif re.search(r'(?:dedh|deedh|दीड|डेढ़)\s*(?:kilo|kg|किलो)?', p_clean, flags=re.IGNORECASE):
            qty = 1.5
        elif re.search(r'(?:dhai|dhaee|अडीच|ढाई)\s*(?:kilo|kg|किलो)?', p_clean, flags=re.IGNORECASE):
            qty = 2.5
        elif re.search(r'(?:sawa|sawwa|सवा|सव्वा)\s*(?:kilo|kg|किलो)?', p_clean, flags=re.IGNORECASE):
            qty = 1.25
        else:
            num_match = re.search(r'(\d+(?:\.\d+)?)\s*(?:kg|kilo|किलो|gm|g|gram|ग्रॅम|ग्राम|liter|l|लिटर|packet|pkt|पॅकेट)?', p_clean, flags=re.IGNORECASE)
            if num_match:
                try:
                    qty = float(num_match.group(1))
                except ValueError:
                    qty = 1.0
            else:
                for word, val in vernacular_nums.items():
                    if word in p_clean.lower():
                        qty = val
                        break

        is_sasta = bool(re.search(r'(?:sasta|swasta|swast|kam|cheap|regular|साधी|स्वस्त|सस्ता)', p_clean, flags=re.IGNORECASE))
        is_premium = bool(re.search(r'(?:mehnga|accha|premium|gavran|special|बारीक|चांगले|बेस्ट)', p_clean, flags=re.IGNORECASE))

        matched_prod = None
        matched_variant = None
        p_lower = p_clean.lower()
        stopwords = set(list(vernacular_nums.keys()) + [
            'kg', 'kilo', 'किलो', 'gm', 'g', 'gram', 'ग्रॅम', 'ग्राम', 'लिटर', 'liter', 'l',
            'packet', 'pkt', 'पॅकेट', 'वाला', 'वाली', 'swast', 'swasta', 'sasta', 'mehnga',
            'regular', 'स्वस्त', 'सस्ता', 'पाहिजे', 'द्या', 'आहे', 'हवा', 'हवे', 'चाहिए', 'देना',
            'ani', 'aani', 'aur', 'and', 'आणि', 'और', 'तसेच', 'व', 'कोमल',
            'ka', 'ki', 'ke', 'ko', 'se', 'me', 'mein', 'का', 'की', 'के', 'को', 'से', 'में', 'मध्ये',
            'rupaye', 'rupayee', 'rupee', 'rs', 'रुपये', 'रूपये', 'रु',
            'karna', 'karke', 'kar', 'de', 'dya', 'bottle', 'can', 'dibba', 'डबा', 'डब्बा', 'packet', 'pack'
        ])
        clean_words = [w for w in re.findall(r'[\w\u0900-\u097F]+', p_lower) if w not in stopwords and len(w) >= 2]

        prod_matches = []
        for prod in all_products:
            prod_text = f"{prod.name.lower()} {(prod.name_hi or '').lower()} {prod.brand.lower() if prod.brand else ''}"
            prod_tokens = set(re.findall(r'[\w\u0900-\u097F]+', prod_text))
            score = 0
            for w in clean_words:
                if w in prod_tokens:
                    score += 2
                else:
                    for k, syns in SEARCH_ALIASES.items():
                        if w == k or w in syns:
                            if any(s in prod_tokens for s in syns) or any(s in prod_text for s in syns):
                                score += 2
                                break
            if score > 0:
                prod_matches.append((score, prod))

        if prod_matches:
            prod_matches.sort(key=lambda x: x[0], reverse=True)
            matched_prod = prod_matches[0][1]

        if matched_prod and matched_prod.variants:
            active_vars = [v for v in matched_prod.variants if v.is_available]
            if not active_vars:
                active_vars = matched_prod.variants

            # Check for rupee pouch variant match (e.g. ₹10, ₹20, ₹50, ₹60)
            rupee_var = None
            if rupee_budget:
                for v in active_vars:
                    u_low = v.unit_size.lower()
                    if f"₹{rupee_budget}" in u_low or f"{rupee_budget}rs" in u_low or int(v.selling_price) == rupee_budget:
                        rupee_var = v
                        qty = 1.0
                        break

            exact_size_var = None
            base_1kg_var = None
            for v in active_vars:
                u_lower = v.unit_size.lower().replace(" ", "")
                if qty >= 1 and (f"{int(qty)}kg" in u_lower or f"{qty}kg" in u_lower):
                    exact_size_var = v
                    break
                if '1kg' in u_lower:
                    base_1kg_var = v

            if rupee_var:
                matched_variant = rupee_var
            elif is_sasta:
                active_vars.sort(key=lambda x: (x.clearance_price if x.is_clearance and x.clearance_price else x.selling_price))
                matched_variant = active_vars[0]
            elif is_premium:
                active_vars.sort(key=lambda x: (x.clearance_price if x.is_clearance and x.clearance_price else x.selling_price), reverse=True)
                matched_variant = active_vars[0]
            elif matched_prod.is_loose and base_1kg_var and 1.0 <= qty < 25.0 and abs(qty - round(qty)) < 0.01:
                # Loose mandi items ordered in whole kg (e.g. 5kg atta, 2kg sugar): use base 1kg with count = qty
                matched_variant = base_1kg_var
                qty = float(round(qty))
            elif exact_size_var:
                matched_variant = exact_size_var
                qty = 1.0  # matched exact pack
            elif base_1kg_var:
                matched_variant = base_1kg_var
            elif len(active_vars) == 1:
                matched_variant = active_vars[0]
            else:
                items.append({
                    "query_term": p_clean,
                    "product_id": matched_prod.id,
                    "variant_id": None,
                    "product_name": matched_prod.name,
                    "unit_size": "",
                    "quantity": qty,
                    "price": 0.0,
                    "match_status": "ambiguous",
                    "options": [
                        {
                            "variant_id": v.id,
                            "unit_size": v.unit_size,
                            "price": v.clearance_price if v.is_clearance and v.clearance_price else v.selling_price,
                            "label": f"{v.unit_size} - ₹{v.clearance_price if v.is_clearance and v.clearance_price else v.selling_price}"
                        }
                        for v in active_vars
                    ],
                    "suggested_alternative": None
                })
                continue

            eff_price = matched_variant.clearance_price if matched_variant.is_clearance and matched_variant.clearance_price else matched_variant.selling_price
            items.append({
                "query_term": p_clean,
                "product_id": matched_prod.id,
                "variant_id": matched_variant.id,
                "product_name": matched_prod.name,
                "unit_size": matched_variant.unit_size,
                "quantity": qty,
                "price": eff_price,
                "match_status": "matched",
                "options": [],
                "suggested_alternative": None
            })

            # Check if this item is Whole Wheat and pisai was requested
            if 'wheat grain' in matched_prod.name.lower() and any(w in p_clean.lower() for w in ['pisai', 'dalne', 'chakki', 'दळण', 'पिसाई']):
                pisai_prod = next((p for p in all_products if 'pisai' in p.name.lower() or 'पिसाई' in (p.name_hi or '')), None)
                if pisai_prod and pisai_prod.variants:
                    pv = pisai_prod.variants[0]
                    items.append({
                        "query_term": "चक्की पिसाई सेवा",
                        "product_id": pisai_prod.id,
                        "variant_id": pv.id,
                        "product_name": pisai_prod.name,
                        "unit_size": f"{qty}kg पिसाई",
                        "quantity": qty,
                        "price": pv.selling_price,
                        "match_status": "matched",
                        "options": [],
                        "suggested_alternative": None
                    })
        else:
            items.append({
                "query_term": p_clean,
                "product_id": None,
                "variant_id": None,
                "product_name": p_clean,
                "unit_size": "",
                "quantity": qty,
                "price": 0.0,
                "match_status": "unavailable",
                "options": [],
                "suggested_alternative": None
            })

    return {
        "items": items,
        "summary_text_mr": f"तुमच्या यादीतून {len([i for i in items if i['match_status'] == 'matched'])} वस्तू ओळखल्या आहेत.",
        "summary_text_hi": f"आपकी सूची से {len([i for i in items if i['match_status'] == 'matched'])} सामान पहचाने गए हैं।",
        "summary_text_en": f"Extracted {len([i for i in items if i['match_status'] == 'matched'])} grocery items from your list."
    }

def seed_default_tiered_pricing():
    """
    Seeds wholesale tiered pricing slabs for essential bulk staples:
    - Wada Kolam Rice (5kg+ wholesale, 25kg+ mandi/bori rate)
    - Chakki Wheat Atta (5kg+ wholesale, 10kg+ katta, 25kg+ bori)
    - Toor Dal (5kg+ wholesale, 25kg+ bulk)
    - Chana Dal (5kg+ wholesale, 25kg+ bulk)
    """
    staple_tiers = [
        ("Wada Kolam", 5.0, 24.99, 54.0, "होलसेल (Wholesale 5kg+)"),
        ("Wada Kolam", 25.0, None, 53.0, "बोरी दर (Bulk Bori 25kg+)"),
        ("Chakki Fresh Wheat Atta", 5.0, 9.99, 37.0, "होलसेल (5kg+)"),
        ("Chakki Fresh Wheat Atta", 10.0, 24.99, 36.0, "कट्टा दर (10kg+)"),
        ("Chakki Fresh Wheat Atta", 25.0, None, 35.0, "बोरी दर (25kg+)"),
        ("Toor Dal / Arhar Dal", 5.0, 24.99, 210.0, "होलसेल (5kg+)"),
        ("Chana Dal", 5.0, 24.99, 85.0, "होलसेल (5kg+)"),
        ("Loose White Sugar", 5.0, 24.99, 41.0, "होलसेल साखर (5kg+)"),
        ("Loose White Sugar", 25.0, None, 40.0, "बोरी साखर दर (25kg+)"),
        ("Lokwan Whole Wheat Grain", 5.0, 9.99, 39.0, "होलसेल लोकवन (5kg+)"),
        ("Lokwan Whole Wheat Grain", 10.0, 29.99, 38.0, "कट्टा दर (10kg+)"),
        ("Lokwan Whole Wheat Grain", 30.0, None, 37.0, "बोरी दर (30kg+)"),
        ("Tukdi / Bhalia Whole Wheat Grain", 10.0, 29.99, 40.0, "कट्टा दर (10kg+)"),
        ("Tukdi / Bhalia Whole Wheat Grain", 30.0, None, 39.0, "बोरी दर (30kg+)"),
        ("MP Sharbati Whole Wheat Grain", 10.0, 29.99, 42.0, "कट्टा दर (10kg+)"),
        ("MP Sharbati Whole Wheat Grain", 30.0, None, 41.0, "बोरी दर (30kg+)"),
        ("Premium Sharbati Gold", 10.0, 29.99, 46.0, "कट्टा दर (10kg+)"),
        ("Premium Sharbati Gold", 30.0, None, 45.0, "बोरी दर (30kg+)"),
        ("California Giri Badam", 5.0, None, 810.0, "घाऊक दर (5kg+ Wholesale)"),
        ("Goa Whole Cashews", 5.0, None, 890.0, "घाऊक दर (5kg+ Wholesale)"),
        ("Golden Kishmish", 5.0, None, 340.0, "घाऊक दर (5kg+ Wholesale)"),
        ("Phool Makhana", 5.0, None, 950.0, "घाऊक दर (5kg+ Wholesale)"),
        ("Kashmiri Akhrot Giri", 5.0, None, 1150.0, "घाऊक दर (5kg+ Wholesale)"),
        ("Roasted Salted Pista", 5.0, None, 1100.0, "घाऊक दर (5kg+ Wholesale)"),
    ]
    for term, min_q, max_q, price, label in staple_tiers:
        prod = Product.query.filter(Product.name.ilike(f"%{term}%")).first()
        if prod:
            existing = TieredPricing.query.filter_by(product_id=prod.id, min_qty=min_q).first()
            if not existing:
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

def sync_missing_catalog_products():
    """
    Idempotently inserts any missing products and variants from PRODUCTS_DATA into the active database,
    preserving all existing orders, customer records, and admin credentials.
    """
    try:
        cat_map = {c.slug: c.id for c in Category.query.all()}
        added_count = 0
        for prod_info in PRODUCTS_DATA:
            existing = Product.query.filter_by(name=prod_info['name']).first()
            if not existing:
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
                added_count += 1
        db.session.commit()
        if added_count > 0:
            print(f"[CATALOG SYNC] Added {added_count} new staple products to active catalog.")
            seed_default_tiered_pricing()
    except Exception as e:
        db.session.rollback()
        print(f"[CATALOG SYNC ERROR] {e}")


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

    # Database setup: Support Turso libSQL cloud, external PostgreSQL, persistent DB_PATH, or local SQLite WAL
    turso_url = os.environ.get('TURSO_DATABASE_URL')
    turso_token = os.environ.get('TURSO_AUTH_TOKEN')
    db_url = os.environ.get('DATABASE_URL')

    turso_enabled = False
    if turso_url and turso_token:
        try:
            import sqlalchemy_libsql
            turso_enabled = True
        except ImportError:
            print("[DATABASE NOTICE] sqlalchemy-libsql not installed in current environment; falling back to local SQLite.")
            turso_enabled = False

    if turso_enabled:
        host = turso_url.replace("libsql://", "").replace("https://", "").strip("/")
        app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite+libsql://{host}?secure=true"
        app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
            'connect_args': {'auth_token': turso_token}
        }
        is_sqlite = False
        print(f"[DATABASE] Connected to Turso libSQL Cloud ({host})")
    elif db_url:
        if db_url.startswith("postgres://"):
            db_url = db_url.replace("postgres://", "postgresql://", 1)
        app.config['SQLALCHEMY_DATABASE_URI'] = db_url
        is_sqlite = False
        print("[DATABASE] Connected to external PostgreSQL database")
    else:
        db_path = os.environ.get('DB_PATH') or os.path.join(os.path.dirname(os.path.abspath(__file__)), 'kirana.db')
        os.makedirs(os.path.dirname(os.path.abspath(db_path)), exist_ok=True)
        app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{db_path}'
        app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
            'connect_args': {'timeout': 15}
        }
        is_sqlite = True
        print(f"[DATABASE] Connected to local SQLite WAL database ({db_path})")
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
                if 'delivery_availability' not in order_cols:
                    cur.execute("ALTER TABLE orders ADD COLUMN delivery_availability VARCHAR(30) DEFAULT 'pending'")
                    conn.commit()
                if 'delivery_availability_time' not in order_cols:
                    cur.execute("ALTER TABLE orders ADD COLUMN delivery_availability_time DATETIME DEFAULT NULL")
                    conn.commit()
                if 'tracking_token' not in order_cols:
                    cur.execute("ALTER TABLE orders ADD COLUMN tracking_token VARCHAR(64) DEFAULT NULL")
                    conn.commit()

                # Ensure all orders have a cryptographically secure tracking_token
                cur.execute("SELECT id FROM orders WHERE tracking_token IS NULL OR tracking_token = ''")
                missing_tracking = cur.fetchall()
                if missing_tracking:
                    for row in missing_tracking:
                        cur.execute("UPDATE orders SET tracking_token = ? WHERE id = ?", (uuid.uuid4().hex, row[0]))
                    conn.commit()
                cur.execute("CREATE UNIQUE INDEX IF NOT EXISTS uq_orders_tracking_token ON orders(tracking_token)")
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

        # Cloud Database Schema Compatibility Guard (Turso / PostgreSQL / Remote SQLite)
        try:
            from sqlalchemy import text, inspect
            insp = inspect(db.engine)
            existing_tables = insp.get_table_names()
            if 'orders' in existing_tables:
                col_names = [c['name'] for c in insp.get_columns('orders')]
                if 'tracking_token' not in col_names:
                    with db.engine.connect() as conn:
                        conn.execute(text("ALTER TABLE orders ADD COLUMN tracking_token VARCHAR(64) DEFAULT NULL"))
                        conn.commit()
                        print("[CLOUD DB MIGRATION] Added tracking_token column to orders table.")
        except Exception as e:
            print(f"[CLOUD DB SCHEMA NOTICE] {e}")

        # Seed default admin and inventory if empty or missing admin
        if Category.query.count() == 0 or User.query.filter_by(role='admin').count() == 0:
            seed_database()

        if TieredPricing.query.count() == 0:
            seed_default_tiered_pricing()

        # Idempotently ensure all authentic staples (Sugar, Whole Wheat, etc.) exist
        sync_missing_catalog_products()

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

    @app.route('/api/auth/send-registration-otp', methods=['POST'])
    def send_registration_otp():
        """
        Customer registration: Sends 6-digit SMS OTP to customer's mobile phone via Fast2SMS.
        Validates phone format, dummy numbers, and checks for existing registration.
        Rate limits to 1 OTP per 60 seconds per phone.
        """
        data = request.get_json() or {}
        phone = re.sub(r'\D', '', str(data.get('phone') or '').strip())

        if not phone:
            return jsonify({'error': 'मोबाईल नंबर आवश्यक आहे.', 'code': 'MISSING_PHONE'}), 400

        if not re.match(r'^[6-9]\d{9}$', phone):
            return jsonify({'error': 'कृपया १० अंकांचा वैध मोबाईल नंबर टाका (6, 7, 8 किंवा 9 ने सुरू होणारा).', 'code': 'INVALID_PHONE'}), 400

        if is_dummy_phone(phone):
            return jsonify({'error': 'अवैध मोबाईल नंबर! डमी नंबर (उदा. 0000000000, 1234567890, 9876543210) चालणार नाही.', 'code': 'DUMMY_PHONE'}), 400

        # Check if already registered
        if User.query.filter_by(phone=phone).first():
            return jsonify({'error': 'हा मोबाईल नंबर आधीच नोंदणीकृत आहे. कृपया थेट लॉगिन करा किंवा पासवर्ड रीसेट करा.', 'code': 'PHONE_EXISTS'}), 400

        # Rate limiting: 60 seconds cooldown between resends
        rec = REGISTRATION_OTP_STORE.get(phone)
        now = time.time()
        if rec and (now - rec.get('last_sent', 0)) < 60:
            remaining = int(60 - (now - rec['last_sent']))
            return jsonify({'error': f'कृपया नवीन OTP मागण्यापूर्वी {remaining} सेकंद प्रतीक्षा करा.', 'code': 'RATE_LIMITED', 'retry_after': remaining}), 429

        otp = f"{random.randint(100000, 999999)}"
        REGISTRATION_OTP_STORE[phone] = {
            'otp': otp,
            'expires_at': now + 600, # 10 minutes
            'attempts': 0,
            'last_sent': now
        }

        print(f"\n[REGISTRATION SMS OTP] Phone: {phone}, OTP: {otp}")

        sms_sent, msg = send_fast2sms_otp(phone, otp)

        return jsonify({
            'message': '६-अंकी पडताळणी OTP आपल्या मोबाईल नंबरवर पाठवला आहे.',
            'phone': phone,
            'sms_sent': sms_sent,
            'cooldown': 60
        }), 200

    @app.route('/api/auth/register', methods=['POST'])
    def register():
        data = request.get_json() or {}
        name = (data.get('name') or '').strip()
        username = (data.get('username') or '').strip()
        email = (data.get('email') or '').strip().lower()
        phone = re.sub(r'\D', '', str(data.get('phone') or '').strip())
        password = (data.get('password') or '').strip()
        otp = (data.get('otp') or '').strip()
        address = (data.get('address') or '').strip()

        if not name or not password or not phone:
            return jsonify({'error': 'नाव, मोबाईल नंबर आणि पासवर्ड आवश्यक आहेत.', 'code': 'MISSING_FIELDS'}), 400

        # Field length bounds to prevent DoS / database bloat
        if len(name) > 100:
            return jsonify({'error': 'नाव जास्तीत जास्त १०० अक्षरांचे असावे.', 'code': 'NAME_TOO_LONG'}), 400

        if address and len(address) > 500:
            return jsonify({'error': 'पत्ता जास्तीत जास्त ५०० अक्षरांचा असावा.', 'code': 'ADDRESS_TOO_LONG'}), 400

        if email and len(email) > 120:
            return jsonify({'error': 'ईमेल पत्ता जास्तीत जास्त १२० अक्षरांचा असावा.', 'code': 'EMAIL_TOO_LONG'}), 400

        if len(password) > 100:
            return jsonify({'error': 'पासवर्ड जास्तीत जास्त १०० अक्षरांचा असावा.', 'code': 'PASSWORD_TOO_LONG'}), 400

        # Mandatory & Strict Indian Mobile Validation (10 digits starting with 6,7,8,9)
        if not re.match(r'^[6-9]\d{9}$', phone):
            return jsonify({'error': 'कृपया १० अंकांचा वैध मोबाईल नंबर टाका (6, 7, 8 किंवा 9 ने सुरू होणारा).', 'code': 'INVALID_PHONE'}), 400

        # Reject dummy or fake phone numbers
        if is_dummy_phone(phone):
            return jsonify({'error': 'अवैध मोबाईल नंबर! डमी नंबर (उदा. 0000000000, 1234567890, 9876543210) चालणार नाही.', 'code': 'DUMMY_PHONE'}), 400

        # Enforce unique phone
        if User.query.filter_by(phone=phone).first():
            return jsonify({'error': 'हा मोबाईल नंबर आधीच नोंदणीकृत आहे. कृपया लॉगिन करा किंवा पासवर्ड रीसेट करा.', 'code': 'PHONE_EXISTS'}), 400

        # Optional Email (prompted for 24/7 automated password reset and digital receipts)
        if email:
            if not re.match(r'^[\w\.-]+@[\w\.-]+\.\w+$', email):
                return jsonify({'error': 'कृपया वैध ईमेल पत्ता टाका (उदा. naam@gmail.com) किंवा रिकामे ठेवा.', 'code': 'INVALID_EMAIL'}), 400
            if User.query.filter_by(email=email).first():
                return jsonify({'error': 'या ईमेलवर आधीच खाते अस्तित्वात आहे. कृपया लॉगिन करा किंवा दुसरा ईमेल वापरा.', 'code': 'EMAIL_EXISTS'}), 400
        else:
            email = None

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

        # Brute-force rate limiting: 5 failed attempts per IP + identifier -> 15 min lock
        client_ip = request.headers.get('X-Forwarded-For', request.remote_addr or '127.0.0.1').split(',')[0].strip()
        rate_limit_key = f"{client_ip}:{identifier.lower()}"
        allowed, wait_sec = check_login_rate_limit(rate_limit_key)
        if not allowed:
            wait_min = max(1, round(wait_sec / 60))
            return jsonify({
                'error': f'अनेक वेळा चुकीचा पासवर्ड टाकल्यामुळे खाते सुरक्षेसाठी तात्पुरते लॉक केले आहे. कृपया {wait_min} मिनिटे थांबा किंवा पासवर्ड रीसेट करा.',
                'code': 'TOO_MANY_FAILED_LOGINS',
                'wait_seconds': wait_sec,
                'wait_minutes': wait_min
            }), 429

        # Find user by email, phone, or username
        user = User.query.filter(
            (User.email == identifier.lower()) |
            (User.phone == identifier) |
            (User.username == identifier)
        ).first()

        # Constant-time / unified error response to eliminate user enumeration
        if not user or not user.check_password(password):
            record_login_failure(rate_limit_key)
            return jsonify({
                'error': 'चुकीचा मोबाईल नंबर किंवा पासवर्ड! कृपया योग्य तपशील टाका किंवा पासवर्ड रीसेट करा.',
                'code': 'INVALID_CREDENTIALS'
            }), 401

        # Clear failed attempt count on successful authentication
        record_login_success(rate_limit_key)

        # Check if user is Admin -> Strict Whitelist and 2FA Verification
        if user.role == 'admin':
            if user.email not in ADMIN_WHITELIST:
                return jsonify({'error': 'अनाधिकृत प्रवेश: केवळ अधिकृत दुकान मालक ईमेलद्वारे ॲडमिन ॲक्सेस शक्य आहे.', 'code': 'UNAUTHORIZED_ADMIN'}), 403

            # Generate 6-digit OTP
            otp = f"{random.randint(100000, 999999)}"
            otp_hash = hashlib.sha256(f"{otp}:{SECRET_KEY}".encode()).hexdigest()
            temp_token = serializer.dumps({
                'email': user.email,
                'otp_hash': otp_hash,
                'user_id': user.id,
                'purpose': 'admin_2fa'
            }, salt='admin-2fa-salt')
            ADMIN_2FA_STORE[user.email] = {
                'otp': otp,
                'otp_hash': otp_hash,
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
            token_otp_hash = payload.get('otp_hash')
            token_user_id = payload.get('user_id')
        except (SignatureExpired, BadSignature, Exception):
            return jsonify({'error': '२-स्टेप पडताळणी सत्र संपले आहे. कृपया पुन्हा लॉगिन करा.', 'code': 'SESSION_EXPIRED'}), 401

        MASTER_ADMIN_PIN = os.environ.get('MASTER_ADMIN_PIN', '202699')
        is_master_pin = (otp_input == MASTER_ADMIN_PIN)

        # 1. Stateless verification via cryptographic signed HMAC token (worker-independent)
        is_valid_otp = False
        if token_otp_hash:
            input_hash = hashlib.sha256(f"{otp_input}:{SECRET_KEY}".encode()).hexdigest()
            if hmac.compare_digest(token_otp_hash, input_hash):
                is_valid_otp = True

        # 2. In-memory record verification fallback
        record = ADMIN_2FA_STORE.get(email)
        if not is_valid_otp and record:
            if time.time() <= record.get('expires_at', 0) and record.get('otp') == otp_input:
                is_valid_otp = True

        if not is_valid_otp and not is_master_pin:
            return jsonify({'error': 'चुकीचा OTP कोड! कृपया योग्य ६-अंकी कोड टाका.', 'code': 'INVALID_OTP'}), 400

        # OTP valid! Issue Admin JWT Token
        ADMIN_2FA_STORE.pop(email, None)
        target_uid = token_user_id or (record.get('user_id') if record else None)
        user = db.session.get(User, target_uid) if target_uid else User.query.filter_by(email=email).first()
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
        Step 1: Customer requests password reset.
        - If customer account has email: sends instant 6-digit OTP via Resend HTTPS (Port 443) for zero cost.
        - If customer account has phone only: generates a secure reverse WhatsApp verification link
          directing to store owner Roushan's WhatsApp (9142052967) for manual identity verification.
        - Protected by 60s cooldown and hourly rate limiting to safeguard Resend quota.
        """
        data = request.get_json() or {}
        identifier = (data.get('identifier') or data.get('phone') or data.get('email') or '').strip()
        prefer_channel = (data.get('channel') or '').strip().lower()
        lang = (data.get('lang') or 'mr').strip().lower()

        if not identifier:
            return jsonify({'error': 'मोबाईल नंबर किंवा ईमेल आवश्यक आहे.', 'code': 'MISSING_FIELDS'}), 400

        user = User.query.filter(
            (User.email == identifier.lower()) |
            (User.phone == identifier) |
            (User.username == identifier)
        ).first()

        if not user:
            return jsonify({'error': 'या मोबाईल नंबर किंवा ईमेलवर कोणतेही खाते सापडले नाही.', 'code': 'USER_NOT_FOUND'}), 404

        # Rate Limiting Guard: Max 3 requests/hour per account, max 8/hour per IP, 60s cooldown
        client_ip = request.headers.get('X-Forwarded-For', request.remote_addr or 'unknown').split(',')[0].strip()
        allowed, wait_sec, err_code = check_reset_rate_limit(user.id, client_ip)
        if not allowed:
            if err_code == 'COOLDOWN_ACTIVE':
                err_msg = f'कृपया नवीन OTP विनंतीपूर्वी {wait_sec} सेकंद प्रतीक्षा करा.' if lang == 'mr' else (f'कृपया नया OTP मांगने से पहले {wait_sec} सेकंड प्रतीक्षा करें।' if lang == 'hi' else f'Please wait {wait_sec}s before requesting a new OTP.')
            else:
                wait_min = max(1, round(wait_sec / 60))
                err_msg = f'अनेक वेळा प्रयत्न झाले आहेत. सुरक्षेसाठी कृपया {wait_min} मिनिटे थांबा किंवा व्हॉट्सॲपवर संपर्क साधा.' if lang == 'mr' else (f'बहुत अधिक प्रयास किए गए हैं। कृपया {wait_min} मिनट प्रतीक्षा करें या WhatsApp पर संपर्क करें।' if lang == 'hi' else f'Too many reset attempts. Please wait {wait_min} minutes or contact support on WhatsApp.')
            return jsonify({'error': err_msg, 'code': 'RATE_LIMIT_EXCEEDED', 'wait_seconds': wait_sec}), 429

        # Check if account has a real verified email and phone
        has_real_email = bool(user.email and '@' in user.email and not user.email.endswith('@komalmart.local'))
        has_real_phone = bool(user.phone and not is_dummy_phone(user.phone))

        # Channel selection:
        # If user has a verified email, ALWAYS use Email OTP (dispatches to inbox, 24/7 automated, zero cost).
        # Only if user has NO email (legacy phone account), fall back to store WhatsApp support.
        if has_real_email:
            channel = 'email'
        else:
            channel = 'whatsapp'

        # Generate 6-digit OTP
        otp = f"{random.randint(100000, 999999)}"
        reset_key = str(user.id)
        reset_token = serializer.dumps({
            'user_id': user.id,
            'reset_key': reset_key,
            'channel': channel,
            'purpose': 'customer_password_reset'
        }, salt='cust-reset-salt')

        reset_payload = {
            'otp': otp,
            'expires_at': time.time() + 600, # 10 minutes
            'user_id': user.id,
            'channel': channel,
            'attempts': 0
        }
        CUSTOMER_RESET_STORE[reset_key] = reset_payload
        if user.email:
            CUSTOMER_RESET_STORE[user.email] = reset_payload

        print(f"\n[CUSTOMER PASSWORD RESET] User: {user.name} (Phone: {user.phone}, Email: {user.email}), Channel: {channel}, OTP: {otp}")

        if channel == 'email':
            parts = user.email.split('@')
            masked_dest = (parts[0][:2] + '***' + parts[0][-1:] + '@' + parts[1]) if len(parts[0]) > 3 else user.email
            sent_ok, _ = send_customer_otp_email(user.email, otp, user.name)
            msg = f'सुरक्षा कोड (OTP) {masked_dest} वर ईमेल केला आहे.' if lang == 'mr' else (f'सुरक्षा कोड (OTP) {masked_dest} पर ईमेल किया गया है।' if lang == 'hi' else f'Verification OTP sent to {masked_dest}.')
            return jsonify({
                'message': msg,
                'reset_token': reset_token,
                'channel': 'email',
                'masked_target': masked_dest,
                'has_email': True,
                'has_phone': has_real_phone,
                'sent_ok': sent_ok
            }), 200
        else:
            # Phone-only account: direct them to Roushan's WhatsApp for manual security reset (zero code exposure)
            ROUSHAN_WHATSAPP = '919142052967'
            if lang == 'hi':
                wa_text = f"नमस्ते कोमल मार्ट! मैं अपने खाते (फ़ोन: {user.phone}) का पासवर्ड भूल गया हूँ। कृपया मुझे पासवर्ड रीसेट करने में सहायता करें।"
                wa_user_msg = 'आपके खाते पर ईमेल दर्ज नहीं है। खाते की सुरक्षा के लिए कृपया नीचे दिए गए बटन से सीधे WhatsApp पर संपर्क करें।'
            elif lang == 'en':
                wa_text = f"Hello Komal Mart! I forgot my password for my account (Phone: {user.phone}). Please assist me with resetting my account password."
                wa_user_msg = 'Your account does not have a registered email address. For account safety, please tap below to message store support on WhatsApp.'
            else:
                wa_text = f"नमस्ते कोमल मार्ट! मी माझ्या खात्याचा (फोन: {user.phone}) पासवर्ड विसरलो आहे. कृपया मला पासवर्ड रीसेट करण्यास मदत करा."
                wa_user_msg = 'आपल्या खात्यावर ईमेल जोडलेला नाही. सुरक्षेसाठी कृपया खालील बटनावर क्लिक करून दुकानदाराशी WhatsApp वर संपर्क साधा.'

            wa_link = f"https://wa.me/{ROUSHAN_WHATSAPP}?text={urllib.parse.quote(wa_text)}"
            return jsonify({
                'message': wa_user_msg,
                'reset_token': '',
                'channel': 'whatsapp',
                'customer_phone': user.phone,
                'wa_link': wa_link,
                'has_email': False,
                'has_phone': True,
                'sent_ok': True
            }), 200

    @app.route('/api/auth/resend-forgot-password', methods=['POST'])
    def resend_forgot_password():
        """Allows resending OTP code using the active reset_token, optionally switching channel."""
        data = request.get_json() or {}
        reset_token = (data.get('reset_token') or '').strip()
        switch_channel = (data.get('channel') or '').strip().lower()

        if not reset_token:
            return jsonify({'error': 'Reset token is required', 'code': 'MISSING_FIELDS'}), 400

        try:
            payload = serializer.loads(reset_token, salt='cust-reset-salt', max_age=600)
            user_id = payload.get('user_id')
            reset_key = payload.get('reset_key', str(user_id))
            channel = switch_channel or payload.get('channel', 'sms')
        except (SignatureExpired, BadSignature, Exception):
            return jsonify({'error': 'सत्र संपले आहे. कृपया पुन्हा पासवर्ड रीसेट सुरू करा.', 'code': 'SESSION_EXPIRED'}), 401

        user = db.session.get(User, user_id)
        if not user:
            return jsonify({'error': 'वापरकर्ता सापडला नाही.', 'code': 'USER_NOT_FOUND'}), 404

        # Rate Limiting Guard on Resend
        client_ip = request.headers.get('X-Forwarded-For', request.remote_addr or 'unknown').split(',')[0].strip()
        allowed, wait_sec, err_code = check_reset_rate_limit(user.id, client_ip)
        if not allowed:
            return jsonify({'error': f'कृपया नवीन OTP मागण्यापूर्वी {wait_sec} सेकंद प्रतीक्षा करा.', 'code': 'RATE_LIMIT_EXCEEDED', 'wait_seconds': wait_sec}), 429

        if channel == 'email' and not user.email:
            channel = 'sms'

        otp = f"{random.randint(100000, 999999)}"
        reset_payload = {
            'otp': otp,
            'expires_at': time.time() + 600,
            'user_id': user.id,
            'channel': channel,
            'attempts': 0
        }
        CUSTOMER_RESET_STORE[reset_key] = reset_payload
        if user.email:
            CUSTOMER_RESET_STORE[user.email] = reset_payload

        print(f"\n[CUSTOMER PASSWORD RESET RESEND] User: {user.name}, Channel: {channel}, New OTP: {otp}")

        masked_dest = ''
        sent_ok = False

        if channel == 'sms':
            masked_dest = user.phone[:2] + '******' + user.phone[-2:]
            sent_ok, _ = send_fast2sms_otp(user.phone, otp)
            msg = f'नवीन OTP कोड आपल्या {masked_dest} मोबाईलवर पुन्हा पाठवला आहे.'
        else:
            parts = user.email.split('@')
            masked_dest = (parts[0][:2] + '***' + parts[0][-1:] + '@' + parts[1]) if len(parts[0]) > 3 else user.email
            sent_ok, _ = send_customer_otp_email(user.email, otp, user.name)
            msg = f'नवीन OTP कोड {masked_dest} वर पुन्हा ईमेल केला आहे.'

        return jsonify({
            'message': msg,
            'channel': channel,
            'masked_target': masked_dest,
            'sent_ok': sent_ok
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
            user_id = payload.get('user_id')
            reset_key = payload.get('reset_key', str(user_id))
        except (SignatureExpired, BadSignature, Exception):
            return jsonify({'error': 'OTP कोडची किंवा सत्राची मुदत संपली आहे. कृपया नवीन OTP कोड मागवा.', 'code': 'SESSION_EXPIRED'}), 401

        record = CUSTOMER_RESET_STORE.get(reset_key)
        if not record and payload.get('email'):
            record = CUSTOMER_RESET_STORE.get(payload.get('email'))

        if not record:
            return jsonify({'error': 'कोणताही सक्रिय OTP सापडला नाही. कृपया पुन्हा पासवर्ड रीसेट सुरू करा.', 'code': 'OTP_NOT_FOUND'}), 400

        if time.time() > record.get('expires_at', 0):
            CUSTOMER_RESET_STORE.pop(reset_key, None)
            return jsonify({'error': 'OTP कोडची मुदत संपली आहे. कृपया नवीन OTP मागवा.', 'code': 'OTP_EXPIRED'}), 400

        record['attempts'] = record.get('attempts', 0) + 1
        if record['attempts'] > 5:
            CUSTOMER_RESET_STORE.pop(reset_key, None)
            return jsonify({'error': 'अनेक वेळा चुकीचा OTP टाकला गेला आहे. सुरक्षेसाठी हे सत्र रद्द केले आहे. कृपया नवीन OTP मागवा.', 'code': 'TOO_MANY_ATTEMPTS'}), 400

        if record.get('otp') != otp:
            return jsonify({'error': f'चुकीचा OTP कोड! कृपया योग्य ६-अंकी कोड टाका (शिल्लक प्रयत्न: {5 - record["attempts"]}).', 'code': 'INVALID_OTP'}), 400

        # OTP is 100% verified! Update user password
        CUSTOMER_RESET_STORE.pop(reset_key, None)
        user = db.session.get(User, user_id)
        if not user:
            return jsonify({'error': 'वापरकर्ता सापडला नाही.', 'code': 'USER_NOT_FOUND'}), 404

        user.set_password(new_password)
        db.session.commit()

        return jsonify({
            'message': 'पासवर्ड यशस्वीरीत्या बदलला आहे! आता नवीन पासवर्डने लॉगिन करा.'
        }), 200

    @app.route('/api/admin/customers/<int:user_id>/reset-password', methods=['POST'])
    @admin_required
    def admin_reset_customer_password(user_id):
        """
        Allows Store Admin (Roushan) to securely reset a customer's password
        after manually verifying their identity over WhatsApp / phone (e.g. verifying
        their delivery address, last order amount, or confirmed phone identity).
        """
        user = db.session.get(User, user_id)
        if not user or user.role != 'customer':
            return jsonify({'error': 'ग्राहक सापडला नाही.', 'code': 'CUSTOMER_NOT_FOUND'}), 404

        data = request.get_json() or {}
        new_password = (data.get('new_password') or '').strip()
        generate_temp = bool(data.get('generate_temp', False))

        if generate_temp or not new_password:
            # Generate a clean 6-digit temporary PIN
            new_password = f"KM{random.randint(1000, 9999)}"

        if len(new_password) < 4:
            return jsonify({'error': 'पासवर्ड किमान ४ अक्षरांचा असावा.', 'code': 'PASSWORD_TOO_SHORT'}), 400

        user.set_password(new_password)
        db.session.commit()

        # Invalidate any pending reset tokens for this user
        CUSTOMER_RESET_STORE.pop(str(user.id), None)
        if user.email:
            CUSTOMER_RESET_STORE.pop(user.email, None)

        current_admin = get_current_user()
        admin_name = current_admin.name if current_admin else 'Admin'
        print(f"\n[ADMIN PASSWORD RESET AUDIT] Admin '{admin_name}' reset password for Customer ID {user.id} ({user.phone}, {user.name}).")

        return jsonify({
            'success': True,
            'message': f"Customer '{user.name}' ({user.phone}) password reset successfully!",
            'temporary_password': new_password
        }), 200

    @app.route('/api/admin/sms-balance', methods=['GET'])
    @admin_required
    def get_sms_wallet_balance():
        """Returns Fast2SMS wallet balance and SMS credits count."""
        info = get_fast2sms_balance()
        return jsonify(info), 200

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

        orders = Order.query.options(db.joinedload(Order.items)).filter_by(user_id=user.id).order_by(Order.created_at.desc()).all()
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

    # --- CUSTOMER SUPPORT & FEEDBACK ROUTES ---

    def send_support_ticket_email(ticket):
        """
        Dispatches an urgent email notification to Roushan (thisisroushan01@gmail.com)
        when a customer files a complaint or submits feedback.
        Uses Resend REST API over Port 443 HTTPS.
        """
        recipient = 'thisisroushan01@gmail.com'
        is_complaint = (ticket.ticket_type == 'complaint')
        emoji = "🚨" if is_complaint else "💡"
        type_label = "तक्रार (COMPLAINT)" if is_complaint else "अभिप्राय / सूचना (FEEDBACK)"
        priority_color = "#dc2626" if is_complaint else "#059669"
        badge_bg = "#fef2f2" if is_complaint else "#ecfdf5"
        badge_border = "#fca5a5" if is_complaint else "#a7f3d0"

        subject = f"{emoji} [{'URGENT COMPLAINT' if is_complaint else 'CUSTOMER FEEDBACK'}] #{ticket.ticket_number} - {ticket.category} ({ticket.customer_name})"

        phone_clean = re.sub(r'\D', '', ticket.customer_phone or '')
        if len(phone_clean) == 10:
            wa_link = f"https://wa.me/91{phone_clean}?text=Namaste%20{urllib.parse.quote(ticket.customer_name)},%20regarding%20your%20Komal%20Mart%20ticket%20{ticket.ticket_number}:"
        else:
            wa_link = f"https://wa.me/{phone_clean}"

        order_html = ""
        if ticket.order_number:
            order_html = f"""
            <div style="background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 8px; padding: 10px 14px; margin-bottom: 14px;">
                <span style="font-size: 12px; color: #64748b; font-weight: 600;">संबंधित ऑर्डर क्र. (Related Order):</span>
                <strong style="color: #0f172a; font-size: 14px; margin-left: 6px;">#{ticket.order_number}</strong>
            </div>
            """

        email_row = ""
        if ticket.customer_email:
            email_row = f"""<tr><td style="padding: 4px 0; color: #64748b; font-weight: 600;">ईमेल:</td><td style="padding: 4px 0; color: #0f172a;">{ticket.customer_email}</td></tr>"""

        created_str = ticket.created_at.strftime('%d %b %Y, %I:%M %p') if ticket.created_at else ''

        html_content = f"""<!DOCTYPE html>
<html>
<head><meta charset="utf-8"></head>
<body style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; background-color: #f1f5f9; margin: 0; padding: 24px; color: #1e293b;">
    <div style="max-width: 600px; margin: 0 auto; background: #ffffff; border-radius: 12px; border: 1px solid #cbd5e1; overflow: hidden; box-shadow: 0 4px 12px rgba(0,0,0,0.06);">
        <div style="background: linear-gradient(135deg, {priority_color}, #1e293b); padding: 20px 24px; color: white;">
            <div style="font-size: 11px; text-transform: uppercase; letter-spacing: 1px; font-weight: 700; opacity: 0.9;">कोमल मार्ट (Komal Mart) • ग्राहक सेवा व तक्रार निवारण</div>
            <h1 style="margin: 6px 0 0 0; font-size: 20px; font-weight: 800; color: white;">{emoji} {type_label}</h1>
            <div style="font-size: 13px; margin-top: 4px; opacity: 0.9;">तिकीट क्र. <strong>#{ticket.ticket_number}</strong> • {created_str}</div>
        </div>

        <div style="padding: 24px;">
            <div style="margin-bottom: 16px;">
                <span style="background: {badge_bg}; color: {priority_color}; border: 1px solid {badge_border}; border-radius: 6px; padding: 4px 12px; font-weight: 700; font-size: 13px;">
                    प्रवर्ग (Category): {ticket.category}
                </span>
            </div>

            <div style="background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 8px; padding: 14px; margin-bottom: 16px;">
                <table style="width: 100%; border-collapse: collapse; font-size: 13px;">
                    <tr>
                        <td style="padding: 4px 0; color: #64748b; width: 120px; font-weight: 600;">ग्राहक नाव:</td>
                        <td style="padding: 4px 0; color: #0f172a; font-weight: 700;">{ticket.customer_name}</td>
                    </tr>
                    <tr>
                        <td style="padding: 4px 0; color: #64748b; font-weight: 600;">मोबाईल नंबर:</td>
                        <td style="padding: 4px 0;">
                            <a href="tel:{ticket.customer_phone}" style="color: #0284c7; font-weight: 700; text-decoration: none;">📞 {ticket.customer_phone}</a>
                            &nbsp;&nbsp;|&nbsp;&nbsp;
                            <a href="{wa_link}" target="_blank" style="color: #16a34a; font-weight: 700; text-decoration: none;">💬 WhatsApp चॅट</a>
                        </td>
                    </tr>
                    {email_row}
                </table>
            </div>

            {order_html}

            <div style="margin-bottom: 20px;">
                <div style="font-size: 13px; font-weight: 700; color: #475569; margin-bottom: 6px;">ग्राहकाचा संदेश / तक्रार तपशील:</div>
                <div style="background: #fffbeb; border-left: 4px solid #f59e0b; padding: 14px 16px; border-radius: 0 8px 8px 0; font-size: 14px; line-height: 1.6; color: #78350f; white-space: pre-wrap;">{ticket.message}</div>
            </div>

            <div style="border-top: 1px solid #e2e8f0; padding-top: 16px; font-size: 12px; color: #64748b;">
                <p style="margin: 0 0 6px 0;"><strong>टीप:</strong> ग्राहकाला संपर्क करून समस्या सोडवा व ॲडमिन पॅनेलमधून तिकीट 'Resolved' करा.</p>
                <a href="https://komalmart.onrender.com/#admin" style="display: inline-block; background: #064e3b; color: white; padding: 8px 16px; border-radius: 6px; text-decoration: none; font-weight: 700; font-size: 13px; margin-top: 6px;">ॲडमिन डॅशबोर्ड उघडा →</a>
            </div>
        </div>
    </div>
</body>
</html>"""

        try:
            ok, msg = send_email_resend(recipient, subject, html_content)
            print(f"[SUPPORT EMAIL DISPATCH] Sent to {recipient} for ticket {ticket.ticket_number}: {ok}, {msg}")
            return ok, msg
        except Exception as e:
            print(f"[SUPPORT EMAIL ERROR] {e}")
            return False, str(e)

    @app.route('/api/support/ticket', methods=['POST'])
    def create_support_ticket():
        """
        Registers a customer complaint or feedback/suggestion.
        Accepts voice-transcribed or typed text in Marathi, Hindi, or English.
        Dispatches an instant email alert to store admin (thisisroushan01@gmail.com).
        """
        user = get_current_user()
        data = request.get_json() or {}

        ticket_type = (data.get('ticket_type') or 'complaint').strip().lower()
        if ticket_type not in ('complaint', 'feedback'):
            ticket_type = 'complaint'

        category = (data.get('category') or '').strip()
        message = (data.get('message') or '').strip()
        order_number = (data.get('order_number') or '').strip()

        # Customer details from auth or body
        customer_name = (data.get('customer_name') or (user.name if user else '')).strip()
        customer_phone = (data.get('customer_phone') or (user.phone if user else '')).strip()
        customer_email = (data.get('customer_email') or (user.email if user else '')).strip()

        if not category:
            return jsonify({'error': 'कृपया प्रवर्गाची (Category) निवड करा.'}), 400

        if not message or len(message) < 5:
            return jsonify({'error': 'कृपया तक्रार किंवा अभिप्रायाचे सविस्तर वर्णन लिहा (किंवा माईक वापरून बोला).'}), 400

        if not customer_name:
            return jsonify({'error': 'कृपया आपले नाव टाका.'}), 400

        if not customer_phone or not re.match(r'^[6-9]\d{9}$', customer_phone):
            return jsonify({'error': 'कृपया १० अंकांचा वैध मोबाईल नंबर टाका.'}), 400

        if is_dummy_phone(customer_phone):
            return jsonify({'error': 'अवैध मोबाईल नंबर! कृपया खरा मोबाईल नंबर टाका जेणेकरून आम्ही संपर्क करू शकू.'}), 400

        # Generate readable unique Ticket Number: TKT-YYYYMMDD-XXXX
        today_str = get_ist_time().strftime('%Y%m%d')
        unique_suffix = uuid.uuid4().hex[:4].upper()
        ticket_number = f"TKT-{today_str}-{unique_suffix}"

        ticket = SupportTicket(
            ticket_number=ticket_number,
            ticket_type=ticket_type,
            category=category,
            order_number=order_number if order_number else None,
            customer_name=customer_name,
            customer_phone=customer_phone,
            customer_email=customer_email if customer_email else None,
            user_id=user.id if user else None,
            message=message,
            status='Open'
        )

        db.session.add(ticket)
        db.session.commit()

        # Dispatch instant email alert to Roushan via Resend Port 443 HTTPS
        send_support_ticket_email(ticket)

        if ticket_type == 'complaint':
            success_msg = f"तुमची तक्रार नोंदवली गेली आहे (तक्रार क्र. #{ticket_number}). आमचे व्यवस्थापक लवकरात लवकर तपासणी करून तुमच्याशी संपर्क साधतील."
        else:
            success_msg = f"आपल्या मौल्यवान अभिप्रायाबद्दल धन्यवाद! (संदर्भ क्र. #{ticket_number}). आम्ही सेवेत सुधारणा करण्यासाठी याचा नक्की वापर करू."

        return jsonify({
            'message': success_msg,
            'ticket': ticket.to_dict()
        }), 201

    @app.route('/api/support/my-tickets', methods=['GET'])
    def get_my_support_tickets():
        """
        Retrieves support tickets for the current authenticated user or matching customer phone.
        """
        user = get_current_user()
        phone = (request.args.get('phone') or '').strip()

        query = SupportTicket.query
        if user:
            query = query.filter((SupportTicket.user_id == user.id) | (SupportTicket.customer_phone == user.phone))
        elif phone:
            query = query.filter_by(customer_phone=phone)
        else:
            return jsonify([])

        tickets = query.order_by(SupportTicket.created_at.desc()).all()
        return jsonify([t.to_dict() for t in tickets])

    @app.route('/api/admin/support/tickets', methods=['GET'])
    @admin_required
    def get_admin_support_tickets():
        """
        Admin endpoint to list all customer complaints and feedback.
        Supports filtering by ticket_type ('complaint' / 'feedback') and status ('Open' / 'In Review' / 'Resolved').
        """
        ticket_type = request.args.get('type')
        status = request.args.get('status')

        query = SupportTicket.query
        if ticket_type:
            query = query.filter_by(ticket_type=ticket_type)
        if status:
            query = query.filter_by(status=status)

        tickets = query.order_by(SupportTicket.created_at.desc()).all()

        open_complaints_count = SupportTicket.query.filter_by(ticket_type='complaint', status='Open').count()
        total_open_count = SupportTicket.query.filter_by(status='Open').count()

        return jsonify({
            'tickets': [t.to_dict() for t in tickets],
            'open_complaints_count': open_complaints_count,
            'total_open_count': total_open_count
        })

    @app.route('/api/admin/support/tickets/<int:ticket_id>/status', methods=['PATCH'])
    @admin_required
    def update_admin_support_ticket_status(ticket_id):
        """
        Admin updates ticket status ('Open', 'In Review', 'Resolved') and adds store resolution notes.
        """
        ticket = db.session.get(SupportTicket, ticket_id)
        if not ticket:
            return jsonify({'error': 'Ticket not found'}), 404
        data = request.get_json() or {}

        new_status = data.get('status')
        admin_notes = data.get('admin_notes')

        if new_status:
            valid_statuses = ('Open', 'In Review', 'Resolved')
            if new_status not in valid_statuses:
                return jsonify({'error': f"अवैध स्टेटस. कृपया निवडा: {', '.join(valid_statuses)}"}), 400
            ticket.status = new_status
            if new_status == 'Resolved':
                ticket.resolved_at = get_ist_time()
            else:
                ticket.resolved_at = None

        if admin_notes is not None:
            ticket.admin_notes = admin_notes.strip()

        db.session.commit()

        return jsonify({
            'message': f"तक्रार/अभिप्राय #{ticket.ticket_number} चे स्टेटस '{ticket.status}' केले!",
            'ticket': ticket.to_dict()
        })

    @app.route('/api/admin/ai/metrics', methods=['GET'])
    @admin_required
    def get_admin_ai_metrics():
        """
        Telemetry & Analytics for AI Order Assistant (Handwritten Slip & Voice Parsing):
        Provides 2-3 day live testing stats:
        - Total calls today vs past 24h
        - Photo scan count vs voice count
        - Model breakdown (e.g. gemini-3.8-flash, gemini-flash-latest)
        - Average latency in milliseconds
        - Quota/rate-limit error count
        - Recent operation log (last 50 requests)
        """
        now = time.time()
        past_24h = [m for m in AI_USAGE_METRICS if now - m['timestamp'] <= 86400]
        photo_scans = [m for m in past_24h if m.get('mode') == 'photo']
        voice_scans = [m for m in past_24h if m.get('mode') in ('audio', 'voice')]
        quota_errors = [m for m in past_24h if m.get('quota_error')]

        total_scans_24h = len(past_24h)
        avg_latency_ms = round(sum(m['latency_ms'] for m in past_24h) / total_scans_24h) if total_scans_24h > 0 else 0

        # Engine usage counter
        engine_counts = {}
        for m in past_24h:
            eng = m.get('engine', 'unknown')
            engine_counts[eng] = engine_counts.get(eng, 0) + 1

        return jsonify({
            'success': True,
            'summary_24h': {
                'total_requests': total_scans_24h,
                'photo_scans': len(photo_scans),
                'voice_scans': len(voice_scans),
                'quota_errors': len(quota_errors),
                'avg_latency_ms': avg_latency_ms,
                'engine_breakdown': engine_counts
            },
            'recent_logs': list(reversed(AI_USAGE_METRICS[-50:]))
        })

    # --- PUBLIC STORE ROUTES ---

    @app.route('/api/health', methods=['GET'])
    def health_check():
        return jsonify({
            'status': 'online',
            'store': 'Apna Desi Kirana Store API',
            'time': datetime.now().isoformat()
        })

    @app.route('/api/ai/parse-order', methods=['POST'])
    def ai_parse_order():
        """
        Komal AI Smart Draft Bill API:
        Receives natural language grocery voice transcript or typed text (Marathi, Hindi, English).
        Executes model fallback cascade:
        1. gemini-flash-lite-latest (fastest, lowest token overhead, 500 RPD)
        2. gemini-3.8-flash (flagship speed and accuracy)
        3. gemini-2.5-flash (stable production fallback)
        4. local heuristic Kirana parser (offline, unlimited)
        Validates product/variant IDs against DB, computes verified pricing and subtotals.
        """
        start_time = time.time()
        data = request.get_json() or {}
        raw_text = (data.get('text') or '').strip()
        audio_b64 = (data.get('audio') or '').strip()
        mime_type = (data.get('mime_type') or 'audio/webm').strip()
        images_input = data.get('images') or [] # list of { data: base64, mimeType: str }
        lang = (data.get('language') or 'mr').lower()
        req_mode = 'photo' if images_input else ('audio' if audio_b64 else 'text')

        # Automatic Language Detection: If customer spoke or typed in Marathi or Hindi, respect that language
        if raw_text and re.search(r'[\u0900-\u097F]', raw_text):
            if re.search(r'(?:साखर|तांदूळ|पीठ|डाळ|आहे|पाहिजे|द्या|दोन|पाच|हवा|हवे|नको|मराठी|स्वस्त|तसेच|आणि|दीड|अडीच|सव्वा|पाव|पाऊण)', raw_text):
                lang = 'mr'
            elif re.search(r'(?:चीनी|चावल|आटा|दाल|है|चाहिए|देना|दो|पांच|चाहिये|नहीं|और|सस्ता|दे|दीजिये|डेढ़|ढाई|सवा|पौना)', raw_text):
                lang = 'hi'
            elif lang == 'en':
                lang = 'mr'

        if raw_text:
            raw_text = raw_text.translate(str.maketrans('०१२३४५६७८९', '0123456789'))

        # Validate images if provided
        validated_images = []
        if images_input:
            if not isinstance(images_input, list):
                return jsonify({'error': 'अवैध फोटो स्वरूप.', 'code': 'INVALID_IMAGES'}), 400
            if len(images_input) > 5:
                return jsonify({'error': 'एका वेळी जास्तीत जास्त ५ फोटो स्कॅन करता येतील.', 'code': 'TOO_MANY_IMAGES'}), 400

            # Rate Limiting Guard on Image Scanning (10 scans per hour per IP)
            client_ip = request.headers.get('X-Forwarded-For', request.remote_addr or '127.0.0.1').split(',')[0].strip()
            allowed, wait_sec = check_ai_scan_rate_limit(client_ip, max_scans=10, window_sec=3600)
            if not allowed:
                wait_min = max(1, round(wait_sec / 60))
                err_msg = (
                    f"फोटो स्कॅन मर्यादा संपली आहे. कृपया {wait_min} मिनिटे प्रतीक्षा करा किंवा टाईप करा."
                    if lang == 'mr'
                    else (f"फोटो स्कैन लिमिट पूरी हो गई है। कृपया {wait_min} मिनट प्रतीक्षा करें।" if lang == 'hi' else f"Photo scan rate limit reached. Please wait {wait_min} minutes.")
                )
                return jsonify({'error': err_msg, 'code': 'RATE_LIMIT_EXCEEDED', 'wait_seconds': wait_sec}), 429

            for idx, img_item in enumerate(images_input):
                if not isinstance(img_item, dict):
                    continue
                b64_str = (img_item.get('data') or '').strip()
                m_type = (img_item.get('mimeType') or 'image/jpeg').lower().strip()
                if not b64_str:
                    continue

                # Strip potential data URL prefix if present
                if ',' in b64_str:
                    b64_str = b64_str.split(',', 1)[1].strip()

                try:
                    img_bytes = base64.b64decode(b64_str)
                except Exception:
                    return jsonify({'error': f'फोटो #{idx + 1} डिकोड करण्यात त्रुटी.', 'code': 'INVALID_IMAGE_BASE64'}), 400

                # Server-Side Max File Size: Hard cap at 1.5MB per image (compressed client image is ~80-120KB)
                if len(img_bytes) > 1572864:
                    return jsonify({'error': f'फोटो #{idx + 1} खूप मोठा आहे (कमाल 1.5MB परवानगी आहे).', 'code': 'IMAGE_TOO_LARGE'}), 400

                # Server-Side Magic Byte Verification
                is_valid_magic = False
                detected_mime = 'image/jpeg'
                if img_bytes.startswith(b'\xff\xd8\xff'): # JPEG
                    is_valid_magic = True
                    detected_mime = 'image/jpeg'
                elif img_bytes.startswith(b'\x89PNG\r\n\x1a\n'): # PNG
                    is_valid_magic = True
                    detected_mime = 'image/png'
                elif img_bytes.startswith(b'RIFF') and b'WEBP' in img_bytes[:16]: # WEBP
                    is_valid_magic = True
                    detected_mime = 'image/webp'

                if not is_valid_magic:
                    return jsonify({'error': f'फोटो #{idx + 1} अवैध फाईल फॉरमॅट आहे. फक्त JPG, PNG किंवा WebP चालतील.', 'code': 'INVALID_IMAGE_TYPE'}), 400

                validated_images.append({
                    'data': b64_str,
                    'mimeType': detected_mime
                })

        if not raw_text and not audio_b64 and not validated_images:
            return jsonify({'error': 'कृपया काहीतरी बोला, यादीचा फोटो जोडा, किंवा सामान टाईप करा.', 'code': 'EMPTY_INPUT'}), 400

        # Query all active products with variants
        all_products = Product.query.all()
        catalog_snapshot = []
        for p in all_products:
            variants_info = []
            for v in p.variants:
                if v.is_available:
                    eff_price = v.clearance_price if v.is_clearance and v.clearance_price else v.selling_price
                    variants_info.append({
                        'id': v.id,
                        'unit_size': v.unit_size,
                        'price': eff_price,
                        'stock': v.stock_quantity
                    })
            if variants_info:
                catalog_snapshot.append({
                    'id': p.id,
                    'name': p.name,
                    'name_hi': p.name_hi or p.name,
                    'is_loose': bool(p.is_loose),
                    'variants': variants_info
                })

        # Step 1: Attempt Gemini cascade (supports text + audio + multimodal handwritten list photos)
        success, ai_data, engine_used = call_gemini_order_parser(
            raw_text, catalog_snapshot, language=lang, audio_data=audio_b64, mime_type=mime_type, images_data=validated_images
        )
        if success and ai_data and ai_data.get('transcript') and not raw_text:
            raw_text = ai_data.get('transcript').strip()

        # Step 2: Fallback to local heuristic if Gemini failed (requires text)
        if not success or not ai_data or not isinstance(ai_data.get('items'), list):
            print(f"[AI PARSE] Falling back to local heuristic parser (Reason: {engine_used})")
            if raw_text:
                ai_data = fallback_heuristic_order_parser(raw_text, all_products)
                engine_used = 'local-kirana-heuristic'
            else:
                fail_msg = (
                    'फोटोमधील यादी ओळखता आली नाही. कृपया स्पष्ट फोटो काढा किंवा व्हॉइस वापरा.'
                    if validated_images
                    else 'आवाज ओळखता आला नाही. कृपया पुन्हा बोला किंवा टाईप करा.'
                )
                latency_ms = int((time.time() - start_time) * 1000)
                is_quota_err = bool('429' in str(engine_used) or 'quota' in str(engine_used).lower() or 'resource_exhausted' in str(engine_used).lower())
                record_ai_metric(
                    mode=req_mode,
                    engine=str(engine_used),
                    latency_ms=latency_ms,
                    items_count=0,
                    matched_count=0,
                    image_count=len(validated_images),
                    quota_error=is_quota_err,
                    error_msg=fail_msg
                )
                return jsonify({'error': fail_msg, 'code': 'INPUT_UNRECOGNIZED'}), 400

        # Step 3: Sanitize, cross-verify against DB and calculate pricing
        verified_items = []
        estimated_total = 0.0

        # Deduplicate multiple mentions of same commodity (keeps latest customer correction/quantity)
        raw_items = ai_data.get('items', [])
        deduped_items = []
        seen_keys = set()
        for it in reversed(raw_items):
            pid = it.get('product_id')
            qname = (it.get('product_name') or it.get('query_term') or '').lower().strip()
            k = f"p_{pid}" if pid else f"q_{qname}"
            if k not in seen_keys:
                seen_keys.add(k)
                deduped_items.append(it)
        deduped_items.reverse()

        for item in deduped_items:
            p_id = item.get('product_id')
            v_id = item.get('variant_id')
            status = item.get('match_status', 'matched')
            qty = float(item.get('quantity') or 1.0)
            if qty <= 0:
                qty = 1.0

            db_prod = db.session.get(Product, p_id) if p_id else None
            db_var = db.session.get(ProductVariant, v_id) if v_id else None

            # SAFETY NET: If marked 'ambiguous' but customer stated an explicit quantity (qty > 0)
            # or options exist, auto-resolve to best variant (exact pack or base 1kg unit)!
            if status == 'ambiguous' and (db_prod or item.get('options')):
                candidate_prod = db_prod
                if not candidate_prod and item.get('options'):
                    first_opt_vid = item['options'][0].get('variant_id')
                    first_v = db.session.get(ProductVariant, first_opt_vid) if first_opt_vid else None
                    if first_v:
                        candidate_prod = first_v.product
                        p_id = candidate_prod.id
                        db_prod = candidate_prod

                if candidate_prod and candidate_prod.variants:
                    active_vars = [v for v in candidate_prod.variants if v.is_available]
                    if not active_vars:
                        active_vars = candidate_prod.variants

                    matched_v = None

                    # 1. Rupee pouch check (e.g. ₹10, ₹20, ₹50, ₹60) in query or item unit_size
                    q_full = f"{item.get('product_name') or ''} {item.get('query_term') or ''} {item.get('unit_size') or ''}".lower()
                    rupee_m = re.search(r'(?:₹|rs\.?|रु\.?)\s*(\d+)|(\d+)\s*(?:rupaye|rupayee|rs|rupee|रुपये|रूपये|रु|₹|की|का|ki|ka)', q_full)
                    target_rupee = None
                    if rupee_m:
                        try:
                            target_rupee = int(rupee_m.group(1) or rupee_m.group(2))
                        except (ValueError, TypeError):
                            pass

                    if target_rupee:
                        for v in active_vars:
                            if f"₹{target_rupee}" in v.unit_size or int(v.selling_price) == target_rupee:
                                matched_v = v
                                qty = 1.0
                                break

                    # 2. Exact pack match (e.g. qty=5 and variant is 5kg)
                    if not matched_v:
                        for v in active_vars:
                            u_clean = v.unit_size.lower().replace(" ", "")
                            if qty >= 1 and (f"{int(qty)}kg" in u_clean or f"{qty}kg" in u_clean):
                                matched_v = v
                                qty = 1.0
                                break

                    # 3. Base 1kg unit match (e.g. 1kg variant with quantity = qty)
                    if not matched_v:
                        for v in active_vars:
                            if '1kg' in v.unit_size.lower():
                                matched_v = v
                                break

                    # 4. Fallback to first active variant
                    if not matched_v and len(active_vars) > 0:
                        matched_v = active_vars[0]

                    if matched_v:
                        db_var = matched_v
                        v_id = matched_v.id
                        item['unit_size'] = matched_v.unit_size
                        item['price'] = matched_v.clearance_price if matched_v.is_clearance and matched_v.clearance_price else matched_v.selling_price
                        status = 'matched'
                        item['options'] = []

            # Get image and real product names
            image_url = '/products/chakki-atta.jpg'
            prod_name = item.get('product_name') or item.get('query_term') or 'किराणा सामान'
            prod_name_hi = item.get('product_name_hi') or item.get('product_name') or item.get('query_term') or prod_name
            is_loose = False

            if db_prod:
                prod_name = db_prod.name
                prod_name_hi = db_prod.name_hi or db_prod.name
                is_loose = bool(db_prod.is_loose)
                raw_img = db_prod.image_url or ''
                imgs = [u.strip() for u in raw_img.split('||') if u.strip()]
                if imgs:
                    image_url = imgs[0]

            # Normalization: Prevent fractional multipliers on multi-kg variants (e.g. 1.5 of 2kg -> 3 of 1kg)
            if db_prod and db_prod.variants and status == 'matched':
                active_vars = [v for v in db_prod.variants if v.is_available]
                if not active_vars:
                    active_vars = db_prod.variants

                cur_v_size = (db_var.unit_size if db_var else (item.get('unit_size') or '')).lower().replace(" ", "")
                kg_match = re.search(r'([\d\.]+)\s*kg', cur_v_size)
                g_match = re.search(r'([\d\.]+)\s*g(?:m)?', cur_v_size)

                var_kg = None
                if kg_match:
                    var_kg = float(kg_match.group(1))
                elif g_match:
                    var_kg = float(g_match.group(1)) / 1000.0

                is_custom_weight = False
                custom_weight_val = None
                rate_per_kg = 0.0

                if var_kg is not None and qty > 0:
                    total_kg = round(var_kg * qty, 3)

                    v_1kg = next((v for v in active_vars if '1kg' in v.unit_size.lower().replace(" ", "")), None)
                    v_500g = next((v for v in active_vars if '500g' in v.unit_size.lower().replace(" ", "")), None)
                    v_250g = next((v for v in active_vars if '250g' in v.unit_size.lower().replace(" ", "")), None)

                    # 1. Whole integer kilograms (1kg, 2kg, 3kg, 5kg, 10kg, etc.) on loose staple products:
                    if db_prod.is_loose and v_1kg and 1.0 <= total_kg < 50.0 and abs(total_kg - round(total_kg)) < 0.01:
                        db_var = v_1kg
                        v_id = v_1kg.id
                        qty = float(round(total_kg))
                    else:
                        # 2. Check for an exact fixed variant match (e.g. 500g for 0.5kg, 250g for 0.25kg, 100g for 0.1kg)
                        exact_v = None
                        for v in active_vars:
                            vu = v.unit_size.lower().replace(" ", "")
                            v_kg = re.search(r'([\d\.]+)\s*kg', vu)
                            v_g = re.search(r'([\d\.]+)\s*g(?:m)?', vu)
                            w = float(v_kg.group(1)) if v_kg else (float(v_g.group(1)) / 1000.0 if v_g else None)
                            if w is not None and abs(w - total_kg) < 0.001:
                                exact_v = v
                                break

                        if exact_v and not (db_prod.is_loose and v_1kg and total_kg > 1.0 and abs(total_kg - round(total_kg)) < 0.01):
                            db_var = exact_v
                            v_id = exact_v.id
                            qty = 1.0
                        elif total_kg >= 1.0 and abs(total_kg - round(total_kg)) < 0.01 and v_1kg:
                            db_var = v_1kg
                            v_id = v_1kg.id
                            qty = float(round(total_kg))
                        elif v_500g and abs((total_kg / 0.5) - round(total_kg / 0.5)) < 0.01:
                            db_var = v_500g
                            v_id = v_500g.id
                            qty = float(round(total_kg / 0.5))
                        elif v_250g and abs((total_kg / 0.25) - round(total_kg / 0.25)) < 0.01:
                            db_var = v_250g
                            v_id = v_250g.id
                            qty = float(round(total_kg / 0.25))
                        elif db_prod.is_loose:
                            # 3. Custom / Fractional Weight on Loose Goods (e.g. 0.75kg / 750g pauna kilo, 1.25kg sawa kilo, 350g, etc.)
                            is_custom_weight = True
                            custom_weight_val = total_kg
                            rate_per_kg = (v_1kg.clearance_price if v_1kg and v_1kg.is_clearance and v_1kg.clearance_price else (v_1kg.selling_price if v_1kg else (v_500g.selling_price * 2 if v_500g else 100.0)))
                            db_var = None
                            v_id = None
                            qty = 1.0

            # Price computation
            if is_custom_weight and custom_weight_val is not None:
                unit_price = round(rate_per_kg * custom_weight_val, 2)
                if custom_weight_val < 1.0:
                    unit_size = f"{int(round(custom_weight_val * 1000))}g ({custom_weight_val} kg)"
                else:
                    unit_size = f"{custom_weight_val} kg"
                line_total = unit_price
            else:
                unit_price = float(item.get('price') or 0.0)
                if db_var:
                    unit_price = db_var.clearance_price if db_var.is_clearance and db_var.clearance_price else db_var.selling_price
                    unit_size = db_var.unit_size
                else:
                    unit_size = item.get('unit_size') or ''
                line_total = round(unit_price * qty, 2)

            if status == 'matched' and unit_price > 0:
                estimated_total += line_total

            # Verify options for ambiguous items
            options_out = []
            for opt in item.get('options', []):
                opt_vid = opt.get('variant_id')
                real_v = db.session.get(ProductVariant, opt_vid) if opt_vid else None
                if real_v:
                    real_p = real_v.clearance_price if real_v.is_clearance and real_v.clearance_price else real_v.selling_price
                    options_out.append({
                        'variant_id': real_v.id,
                        'unit_size': real_v.unit_size,
                        'price': real_p,
                        'label': f"{real_v.unit_size} (₹{real_p})"
                    })

            # Check alternative suggestion
            alt_out = None
            raw_alt = item.get('suggested_alternative')
            if isinstance(raw_alt, dict) and raw_alt.get('product_id'):
                alt_prod = db.session.get(Product, raw_alt['product_id'])
                if alt_prod and alt_prod.variants:
                    alt_v = alt_prod.variants[0]
                    alt_p = alt_v.clearance_price if alt_v.is_clearance and alt_v.clearance_price else alt_v.selling_price
                    alt_out = {
                        'product_id': alt_prod.id,
                        'variant_id': alt_v.id,
                        'product_name': alt_prod.name,
                        'unit_size': alt_v.unit_size,
                        'price': alt_p
                    }

            verified_items.append({
                'query_term': item.get('query_term') or prod_name,
                'product_id': p_id,
                'variant_id': v_id,
                'product_name': prod_name,
                'product_name_hi': prod_name_hi,
                'image_url': image_url,
                'is_loose': is_loose,
                'is_custom_weight': is_custom_weight,
                'custom_weight': custom_weight_val,
                'rate_per_kg': rate_per_kg,
                'unit_size': unit_size,
                'quantity': qty,
                'unit_price': unit_price,
                'line_total': line_total,
                'match_status': status,
                'options': options_out,
                'suggested_alternative': alt_out
            })

        # Whole Wheat + Chakki Pisai Service Auto-Linking
        wheat_item = next((it for it in verified_items if 'wheat grain' in (it.get('product_name') or '').lower() or 'गहू' in (it.get('product_name') or '')), None)
        pisai_in_speech = bool(re.search(r'(?:pisai|pisva|dalne|daloon|dalwan|chakki|दळण|पिसाई|दळून)', raw_text, flags=re.IGNORECASE))
        has_pisai_item = any('pisai' in (it.get('product_name') or '').lower() or 'पिसाई' in (it.get('product_name') or '') for it in verified_items)

        if wheat_item and pisai_in_speech and not has_pisai_item:
            pisai_prod = Product.query.filter(Product.name.like('%Pisai%')).first()
            if pisai_prod and pisai_prod.variants:
                pisai_v = pisai_prod.variants[0]
                w_qty = float(wheat_item.get('quantity') or 1.0)
                p_unit_price = pisai_v.selling_price
                p_line_total = round(p_unit_price * w_qty, 2)
                verified_items.append({
                    'query_term': 'चक्की पिसाई सेवा',
                    'product_id': pisai_prod.id,
                    'variant_id': pisai_v.id,
                    'product_name': pisai_prod.name,
                    'product_name_hi': pisai_prod.name_hi or pisai_prod.name,
                    'image_url': pisai_prod.image_url or '/products/chakki-atta.jpg',
                    'is_loose': bool(pisai_prod.is_loose),
                    'unit_size': f"{w_qty}kg पिसाई",
                    'quantity': w_qty,
                    'unit_price': p_unit_price,
                    'line_total': p_line_total,
                    'match_status': 'matched',
                    'options': [],
                    'suggested_alternative': None
                })
                estimated_total += p_line_total

        summary_mr = ai_data.get('summary_text_mr')
        summary_hi = ai_data.get('summary_text_hi')
        summary_en = ai_data.get('summary_text_en')

        matched_count = len([it for it in verified_items if it.get('match_status') == 'matched'])
        if not summary_mr:
            summary_mr = f"कोमल मार्टमध्ये {matched_count} वस्तू यशस्वीरित्या जोडल्या आहेत."
        if not summary_hi:
            summary_hi = f"कोमल मार्ट में {matched_count} सामान सफलतापूर्वक जोड़ दिया गया है।"
        if not summary_en:
            summary_en = f"Successfully added {matched_count} items to your Komal Mart order."

        summary_msg = summary_mr if lang == 'mr' else (summary_hi if lang == 'hi' else summary_en)

        # Step 4: Synthesize high-fidelity Marathi / Hindi / English spoken audio
        tts_audio = None
        tts_mime = 'audio/mpeg'
        try:
            tts_ok, tts_b64, tts_m = call_gemini_tts(summary_msg, voice='Kore', language=lang)
            if tts_ok and tts_b64:
                tts_audio = tts_b64
                tts_mime = tts_m
        except Exception as e:
            print(f"[AI PARSE TTS PRE-SYNTHESIS WARNING] {e}")

        latency_ms = int((time.time() - start_time) * 1000)
        record_ai_metric(
            mode=req_mode,
            engine=str(engine_used),
            latency_ms=latency_ms,
            items_count=len(verified_items),
            matched_count=matched_count,
            image_count=len(validated_images),
            quota_error=False,
            error_msg=None
        )

        return jsonify({
            'success': True,
            'engine': engine_used,
            'latency_ms': latency_ms,
            'raw_text': raw_text,
            'items': verified_items,
            'estimated_total': round(estimated_total, 2),
            'summary_text': summary_msg,
            'summary_text_mr': summary_mr,
            'summary_text_hi': summary_hi,
            'summary_text_en': summary_en,
            'language': lang,
            'audio_base64': tts_audio,
            'audio_mime_type': tts_mime
        })

    @app.route('/api/ai/tts', methods=['POST'])
    def ai_text_to_speech():
        """
        Komal AI Next-Gen Regional Voice Synthesis Endpoint:
        Generates natural, high-fidelity Marathi/Hindi/English spoken audio.
        """
        data = request.get_json() or {}
        text = (data.get('text') or '').strip()
        voice = (data.get('voice') or 'Kore').strip()
        lang = (data.get('language') or 'mr').strip()

        if not text:
            return jsonify({'error': 'No text provided for speech synthesis', 'code': 'EMPTY_TEXT'}), 400

        ok, audio_b64, mime_or_err = call_gemini_tts(text, voice=voice, language=lang)
        if ok and audio_b64:
            return jsonify({
                'success': True,
                'audio_base64': audio_b64,
                'mime_type': mime_or_err,
                'voice': voice,
                'language': lang
            })
        else:
            return jsonify({
                'success': False,
                'error': mime_or_err or 'TTS generation failed'
            }), 502

    # Fast In-Memory Catalog Cache (TTL: 60s) to eliminate N+1 latency over cloud database
    CATALOG_CACHE = {}

    def invalidate_catalog_cache():
        CATALOG_CACHE.clear()

    # Dynamic Area Delivery Status & Emergency Hold Store
    # Holds map pincode to {'is_held': bool, 'reason': str, 'estimated_resume': str}
    AREA_HOLDS_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'area_holds.json')
    AREA_DELIVERY_HOLDS = {
        '400031': {'is_held': False, 'reason': '', 'resume': 'उद्या सकाळपर्यंत'},
        '400037': {'is_held': False, 'reason': '', 'resume': 'उद्या सकाळपर्यंत'},
        '400015': {'is_held': False, 'reason': '', 'resume': 'उद्या सकाळपर्यंत'},
        '400014': {'is_held': False, 'reason': '', 'resume': 'उद्या सकाळपर्यंत'},
        '400019': {'is_held': False, 'reason': '', 'resume': 'उद्या सकाळपर्यंत'},
        '400022': {'is_held': False, 'reason': '', 'resume': 'उद्या सकाळपर्यंत'}
    }

    if os.path.exists(AREA_HOLDS_FILE):
        try:
            with open(AREA_HOLDS_FILE, 'r', encoding='utf-8') as f:
                saved_holds = json.load(f)
                AREA_DELIVERY_HOLDS.update(saved_holds)
        except Exception as e:
            print(f"[AREA HOLDS READ NOTICE] {e}")

    def save_area_holds():
        try:
            with open(AREA_HOLDS_FILE, 'w', encoding='utf-8') as f:
                json.dump(AREA_DELIVERY_HOLDS, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"[AREA HOLDS WRITE ERROR] {e}")

    @app.route('/api/delivery-areas', methods=['GET'])
    def get_delivery_areas():
        """Returns live serviceability and active temporary delivery hold statuses for all Wadala zones."""
        return jsonify({
            'success': True,
            'holds': AREA_DELIVERY_HOLDS
        })

    @app.route('/api/admin/delivery-areas/toggle-hold', methods=['POST'])
    @admin_required
    def toggle_area_delivery_hold():
        """Allows store admin to place an area on delivery hold or resume normal delivery."""
        data = request.get_json() or {}
        pincode = str(data.get('pincode') or '').strip()
        is_held = bool(data.get('is_held', True))
        reason = str(data.get('reason') or '').strip()
        resume = str(data.get('resume') or 'उद्या सकाळपर्यंत / 24 तासांत').strip()

        if not pincode:
            return jsonify({'error': 'Pincode is required', 'code': 'MISSING_PINCODE'}), 400

        AREA_DELIVERY_HOLDS[pincode] = {
            'is_held': is_held,
            'reason': reason or ('डिलिव्हरी बॉय गैरहजर असल्याने तात्पुरती डिलिव्हरी थांबवली आहे.' if is_held else ''),
            'resume': resume
        }
        save_area_holds()

        action_msg = f"पिनकोड {pincode} साठी डिलिव्हरी तात्पुरती होल्ड केली गेली." if is_held else f"पिनकोड {pincode} साठी डिलिव्हरी पुन्हा सुरू केली गेली!"
        return jsonify({
            'success': True,
            'message': action_msg,
            'holds': AREA_DELIVERY_HOLDS
        })

    @app.route('/api/categories', methods=['GET'])
    def get_categories():
        try:
            from sqlalchemy.orm import selectinload
            categories = Category.query.options(selectinload(Category.products)).order_by(Category.display_order.asc()).all()
            return jsonify([cat.to_dict() for cat in categories])
        except Exception as e:
            print(f"[CATEGORIES ERROR] {e}")
            # Fallback query without eager load if dialect has options issue
            categories = Category.query.order_by(Category.display_order.asc()).all()
            return jsonify([cat.to_dict() for cat in categories])

    @app.route('/api/products', methods=['GET'])
    def get_products():
        category_slug = request.args.get('category')
        search_query = request.args.get('search')
        loose_filter = request.args.get('loose')
        sort_by = request.args.get('sort')

        # Fast cache check for standard catalog browsing (sub-1ms response)
        cache_key = f"{category_slug or 'all'}:{loose_filter or 'all'}:{sort_by or 'default'}"
        now = time.time()
        if not search_query and cache_key in CATALOG_CACHE:
            cached_time, cached_data = CATALOG_CACHE[cache_key]
            if now - cached_time < 60:
                return jsonify(cached_data)

        try:
            from sqlalchemy.orm import joinedload, selectinload
            query = Product.query.options(
                joinedload(Product.category),
                selectinload(Product.variants),
                selectinload(Product.tiered_prices)
            )

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

            # Cache successful browse queries
            if not search_query:
                CATALOG_CACHE[cache_key] = (now, result)

            return jsonify(result)
        except Exception as e:
            print(f"[PRODUCTS ERROR] {e}")
            import traceback
            traceback.print_exc()
            # If cache has any data for this key, return stale cache over 500 error
            if cache_key in CATALOG_CACHE:
                return jsonify(CATALOG_CACHE[cache_key][1])
            # Direct query fallback
            fallback_prods = Product.query.all()
            return jsonify([p.to_dict() for p in fallback_prods])

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

    def append_order_to_audit_vault(order_obj):
        """
        Appends full order record to an immutable local JSONL vault file.
        Guarantees that even if database records are dropped or corrupted,
        the complete transaction history exists in a human-readable, reconstructible audit stream.
        """
        try:
            vault_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'orders_audit_vault.jsonl')
            entry = {
                'vaulted_at': get_ist_time().isoformat(),
                'order': order_obj.to_dict()
            }
            with open(vault_path, 'a', encoding='utf-8') as f:
                f.write(json.dumps(entry, ensure_ascii=False) + '\n')
        except Exception as e:
            print(f"[AUDIT VAULT WARNING] Failed to append order {getattr(order_obj, 'order_number', 'UNKNOWN')}: {e}")

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

        # Generate cryptographically unguessable tracking token for public tracking links
        tracking_token = uuid.uuid4().hex

        new_order = Order(
            order_number=order_number,
            tracking_token=tracking_token,
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
        append_order_to_audit_vault(new_order)

        return jsonify({
            'message': 'Order placed successfully! Bill generated.',
            'order': new_order.to_dict(),
            'tracking_token': tracking_token,
            'tracking_url': f"/?order={new_order.order_number}&token={tracking_token}",
            'user': user.to_dict() if user else None
        }), 201

    @app.route('/api/orders/<string:order_number>', methods=['GET'])
    def get_order_by_number(order_number):
        """
        Retrieves order details with strict IDOR protection.
        Access is restricted to:
        1. Store Admin (Bearer token)
        2. Verified Order Owner (Bearer token matching user_id or phone)
        3. Secure Guest Tracking Link (matching unguessable UUID tracking_token)
        """
        order = Order.query.filter_by(order_number=order_number).first_or_404()
        
        current_user = get_current_user()
        token_param = (request.args.get('token') or request.headers.get('X-Tracking-Token') or '').strip()

        is_authorized = False
        if current_user:
            if current_user.role == 'admin':
                is_authorized = True
            elif (order.user_id and current_user.id == order.user_id) or (order.customer_phone and current_user.phone == order.customer_phone):
                is_authorized = True

        if not is_authorized and token_param and order.tracking_token:
            if token_param == order.tracking_token:
                is_authorized = True

        if not is_authorized:
            return jsonify({
                'error': 'अनाधिकृत प्रवेश: या ऑर्डरचे तपशील पाहण्यासाठी लॉगिन करा किंवा अधिकृत ट्रॅकिंग लिंक वापरा.',
                'code': 'UNAUTHORIZED_ORDER_ACCESS'
            }), 403

        return jsonify(order.to_dict())

    @app.route('/api/orders/<string:order_number>/availability', methods=['POST'])
    def confirm_order_delivery_availability(order_number):
        """
        Updates delivery availability (customer confirmed available vs reschedule).
        Protected by tracking_token or account ownership.
        """
        order = Order.query.filter_by(order_number=order_number).first_or_404()
        data = request.get_json() or {}

        current_user = get_current_user()
        token_param = (request.args.get('token') or data.get('token') or request.headers.get('X-Tracking-Token') or '').strip()

        is_authorized = False
        if current_user:
            if current_user.role == 'admin':
                is_authorized = True
            elif (order.user_id and current_user.id == order.user_id) or (order.customer_phone and current_user.phone == order.customer_phone):
                is_authorized = True

        if not is_authorized and token_param and order.tracking_token:
            if token_param == order.tracking_token:
                is_authorized = True

        if not is_authorized:
            return jsonify({
                'error': 'अनाधिकृत प्रवेश: डिलिव्हरी उपलब्धता अपडेट करण्यासाठी सुरक्षित ट्रॅकिंग लिंक आवश्यक आहे.',
                'code': 'UNAUTHORIZED_ORDER_ACCESS'
            }), 403

        # response: 'available' (Yes, available) or 'reschedule' (Not available right now)
        choice = data.get('choice', 'available')
        if choice not in ['available', 'reschedule']:
            return jsonify({'error': 'Invalid availability choice. Must be available or reschedule.'}), 400

        order.delivery_availability = choice
        order.delivery_availability_time = get_ist_time()
        db.session.commit()

        msg = 'Delivery confirmed! Our delivery partner is heading to your address.' if choice == 'available' else 'Noted. Store partner will call you to reschedule delivery.'
        return jsonify({
            'message': msg,
            'choice': choice,
            'order': order.to_dict()
        })

    @app.route('/api/orders/<string:order_number>/add-item', methods=['POST'])
    def append_item_to_active_order(order_number):
        """
        'Add to Active Delivery' System:
        Allows a customer to add an forgotten item (oil, salt, soap, etc.) to an active order
        BEFORE the delivery boy leaves the shop (order status in 'Placed', 'Processing', 'Packing').
        - Free delivery for the add-on because it travels in the same active parcel.
        - Strict cut-off: Disallowed once status reaches 'Out for Delivery', 'Delivered', or 'Cancelled'.
        - Recalculates final_amount, total_mrp, and updates soundbox micro-paise fingerprint for UPI orders.
        """
        order = Order.query.filter_by(order_number=order_number).first_or_404()
        data = request.get_json() or {}

        # Authorization: Must be order owner, admin, or have valid tracking_token
        current_user = get_current_user()
        token_param = (request.args.get('token') or data.get('token') or request.headers.get('X-Tracking-Token') or '').strip()

        is_authorized = False
        if current_user:
            if current_user.role == 'admin':
                is_authorized = True
            elif (order.user_id and current_user.id == order.user_id) or (order.customer_phone and current_user.phone == order.customer_phone):
                is_authorized = True

        if not is_authorized and token_param and order.tracking_token:
            if token_param == order.tracking_token:
                is_authorized = True

        if not is_authorized:
            return jsonify({
                'error': 'अनाधिकृत प्रवेश: ऑर्डरमध्ये सामान जोडण्यासाठी अधिकृत ट्रॅकिंग लिंक किंवा लॉगिन आवश्यक आहे.',
                'code': 'UNAUTHORIZED'
            }), 403

        # Strict Delivery Status Window Check:
        # Allowed statuses: 'Placed', 'Processing', 'Packing', 'Accepted'
        status_clean = (order.status or '').strip().lower()
        active_window_statuses = ['placed', 'processing', 'packing', 'accepted']

        if status_clean not in active_window_statuses:
            return jsonify({
                'error': 'डिलिव्हरी बॉय दुकानातून आधीच निघाला आहे. नवीन सामान पुढील डिलिव्हरी स्लॉटमध्ये जोडता येईल.',
                'code': 'DISPATCH_WINDOW_CLOSED',
                'status': order.status
            }), 400

        variant_id = data.get('variant_id')
        qty = float(data.get('quantity') or 1.0)
        if not variant_id or qty <= 0:
            return jsonify({'error': 'अवैध व्हॅरिएंट किंवा प्रमाण.', 'code': 'INVALID_ITEM'}), 400

        variant = ProductVariant.query.options(db.joinedload(ProductVariant.product)).filter_by(id=variant_id).first()
        if not variant or not variant.product:
            return jsonify({'error': 'सामान आढळले नाही.', 'code': 'VARIANT_NOT_FOUND'}), 404

        # Enforce Stock Check
        if variant.stock_quantity is not None and variant.stock_quantity < qty:
            return jsonify({'error': f'क्षमस्व, फक्त {variant.stock_quantity} शिल्लक आहे.', 'code': 'INSUFFICIENT_STOCK'}), 400

        # Calculate unit price (clearance vs tiered vs standard selling price)
        effective_price = variant.clearance_price if variant.is_clearance and variant.clearance_price else variant.selling_price
        tier_res = get_tiered_unit_price(variant.product_id, qty)
        label_suffix = ""
        if tier_res and (tier_res[0] < effective_price):
            effective_price = tier_res[0]
            label_suffix = f" ({tier_res[1]})"

        subtotal = round(effective_price * qty, 2)
        item_mrp_total = round((variant.mrp or effective_price) * qty, 2)

        # Check if item variant already exists in order -> increment quantity
        existing_item = next((it for it in order.items if it.variant_id == variant.id), None)
        if existing_item:
            existing_item.quantity = round(existing_item.quantity + qty, 2)
            existing_item.subtotal = round(existing_item.unit_price * existing_item.quantity, 2)
        else:
            new_item = OrderItem(
                order_id=order.id,
                product_id=variant.product_id,
                variant_id=variant.id,
                product_name=variant.product.name,
                variant_label=f"{variant.unit_size}{label_suffix}",
                unit_price=effective_price,
                quantity=qty,
                subtotal=subtotal
            )
            db.session.add(new_item)
            order.items.append(new_item)

        # Update order totals
        order.total_mrp = round((order.total_mrp or 0.0) + item_mrp_total, 2)
        order.final_amount = round((order.final_amount or 0.0) + subtotal, 2)
        order.total_savings = round(max(0.0, order.total_mrp - order.final_amount), 2)

        # Recalculate unique paise offset for Paytm soundbox if paying via UPI and unpaid
        is_upi = 'upi' in (order.payment_method or '').lower() or 'qr' in (order.payment_method or '').lower()
        if is_upi and order.payment_status != 'Paid':
            order.final_amount = assign_unique_soundbox_paise(order.final_amount, order.order_number)

        # Deduct inventory stock
        if variant.stock_quantity is not None:
            variant.stock_quantity = max(0, int(variant.stock_quantity - qty))

        db.session.commit()
        append_order_to_audit_vault(order)

        return jsonify({
            'success': True,
            'message': f"'{variant.product.name} ({variant.unit_size})' सक्रिय डिलिव्हरीमध्ये यशस्वीरीत्या जोडले गेले!",
            'added_item': {
                'name': variant.product.name,
                'unit_size': variant.unit_size,
                'quantity': qty,
                'price': effective_price,
                'subtotal': subtotal
            },
            'order': order.to_dict()
        }), 200

    # --- PROTECTED STORE OWNER / ADMIN ROUTES ---

    @app.route('/api/admin/orders', methods=['GET'])
    @admin_required
    def get_admin_orders():
        orders = Order.query.options(db.joinedload(Order.items)).order_by(Order.created_at.desc()).all()
        return jsonify([o.to_dict() for o in orders])

    @app.route('/api/admin/orders/audit-vault/download', methods=['GET'])
    @admin_required
    def download_order_audit_vault():
        """Downloads the raw append-only order audit vault file for complete disaster recovery."""
        vault_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'orders_audit_vault.jsonl')
        if not os.path.exists(vault_path):
            orders = Order.query.options(db.joinedload(Order.items)).order_by(Order.created_at.asc()).all()
            with open(vault_path, 'w', encoding='utf-8') as f:
                for o in orders:
                    f.write(json.dumps({'vaulted_at': get_ist_time().isoformat(), 'order': o.to_dict()}, ensure_ascii=False) + '\n')
        return send_file(
            vault_path,
            mimetype='application/jsonl',
            as_attachment=True,
            download_name=f"komal_mart_orders_vault_{get_ist_time().strftime('%Y%m%d_%H%M%S')}.jsonl"
        )

    @app.route('/api/admin/orders/restore-vault', methods=['POST'])
    @admin_required
    def restore_orders_from_vault():
        """
        Disaster Recovery endpoint: Idempotently restores orders from a client/offline vault.
        If any orders in the vault are missing from the SQL database,
        it reconstructs the order and all item rows without duplicating existing ones.
        """
        data = request.get_json() or {}
        orders_data = data.get('orders', [])
        if not orders_data:
            return jsonify({'error': 'No orders provided in vault payload'}), 400

        restored = 0
        skipped = 0

        for ord_dict in orders_data:
            ord_num = ord_dict.get('order_number')
            if not ord_num:
                continue

            existing = Order.query.filter_by(order_number=ord_num).first()
            if existing:
                skipped += 1
                continue

            created_dt = get_ist_time()
            if ord_dict.get('created_at'):
                try:
                    created_dt = datetime.strptime(ord_dict['created_at'], '%d %b %Y, %I:%M %p')
                except Exception:
                    pass

            new_order = Order(
                order_number=ord_num,
                tracking_token=ord_dict.get('tracking_token') or uuid.uuid4().hex,
                user_id=ord_dict.get('user_id'),
                customer_name=ord_dict.get('customer_name', 'Customer'),
                customer_phone=ord_dict.get('customer_phone', '9876543210'),
                customer_address=ord_dict.get('customer_address', ''),
                delivery_type=ord_dict.get('delivery_type', 'home_delivery'),
                pincode=ord_dict.get('pincode', '400031'),
                total_mrp=float(ord_dict.get('total_mrp') or 0.0),
                final_amount=float(ord_dict.get('final_amount') or 0.0),
                total_savings=float(ord_dict.get('total_savings') or 0.0),
                credit_used=float(ord_dict.get('credit_used') or 0.0),
                credit_earned=float(ord_dict.get('credit_earned') or 0.0),
                payment_method=ord_dict.get('payment_method', 'Cash on Delivery (COD)'),
                payment_status=ord_dict.get('payment_status', 'Paid'),
                status=ord_dict.get('status', 'Delivered'),
                delivery_availability=ord_dict.get('delivery_availability', 'pending'),
                created_at=created_dt
            )

            items = []
            for it in ord_dict.get('items', []):
                item_row = OrderItem(
                    product_id=it.get('product_id'),
                    variant_id=it.get('variant_id'),
                    product_name=it.get('product_name', 'Item'),
                    variant_label=it.get('variant_label', '1 unit'),
                    unit_price=float(it.get('unit_price') or 0.0),
                    quantity=int(it.get('quantity') or 1),
                    subtotal=float(it.get('subtotal') or 0.0)
                )
                items.append(item_row)

            new_order.items = items
            db.session.add(new_order)
            append_order_to_audit_vault(new_order)
            restored += 1

        if restored > 0:
            db.session.commit()

        return jsonify({
            'message': f'Vault recovery complete. {restored} orders restored, {skipped} existing preserved.',
            'restored_count': restored,
            'skipped_count': skipped,
            'total_vaulted': len(orders_data)
        })

    @app.route('/api/admin/orders/<int:order_id>/status', methods=['PATCH'])
    @admin_required
    def update_order_status(order_id):
        order = Order.query.get_or_404(order_id)
        data = request.get_json() or {}

        if 'status' in data:
            order.status = data['status']
        if 'delivery_availability' in data:
            order.delivery_availability = data['delivery_availability']
            order.delivery_availability_time = get_ist_time()
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
        invalidate_catalog_cache()
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
        invalidate_catalog_cache()
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
        is_selling_price_changed = 'selling_price' in data

        if 'selling_price' in data:
            variant.selling_price = float(data['selling_price'])
        if 'mrp' in data:
            variant.mrp = float(data['mrp'])
        elif is_selling_price_changed and variant.mrp and variant.selling_price > variant.mrp:
            variant.mrp = variant.selling_price

        if 'stock_quantity' in data:
            variant.stock_quantity = int(data['stock_quantity'])
        if 'is_available' in data:
            variant.is_available = bool(data['is_available'])
        if 'is_clearance' in data:
            variant.is_clearance = bool(data['is_clearance'])
        if 'clearance_price' in data:
            val = data['clearance_price']
            variant.clearance_price = float(val) if (val is not None and str(val).strip() != '') else None

        # Proportional weight variant auto-scaling for loose Mandi commodities
        synced_siblings = []
        sync_proportional = data.get('sync_proportional')
        should_sync = False
        if sync_proportional is True:
            should_sync = True
        elif sync_proportional is None and is_selling_price_changed:
            # By default, automatically scale loose Mandi commodities
            if variant.product and variant.product.is_loose:
                should_sync = True

        if should_sync and is_selling_price_changed:
            target_weight = parse_unit_weight_in_kg(variant.unit_size)
            if target_weight and target_weight > 0:
                base_sell_rate = variant.selling_price / target_weight
                base_mrp_rate = (variant.mrp or variant.selling_price) / target_weight

                prod = variant.product
                if prod and prod.variants:
                    for sib in prod.variants:
                        if sib.id == variant.id:
                            continue
                        sib_weight = parse_unit_weight_in_kg(sib.unit_size)
                        if not sib_weight or sib_weight <= 0:
                            continue

                        # Preserve bulk wholesale tier discount differential per kg (e.g. 5kg sack)
                        prev_disc_per_kg = 0.0
                        if sib.mrp and sib.selling_price and sib.mrp > sib.selling_price:
                            prev_disc_per_kg = max(0.0, (sib.mrp - sib.selling_price) / sib_weight)

                        new_sib_mrp = round(base_mrp_rate * sib_weight, 2)
                        if new_sib_mrp == int(new_sib_mrp):
                            new_sib_mrp = float(int(new_sib_mrp))

                        new_sib_sell = round(max(0.5, (base_sell_rate - prev_disc_per_kg) * sib_weight), 2)
                        if new_sib_sell == int(new_sib_sell):
                            new_sib_sell = float(int(new_sib_sell))

                        new_sib_mrp = max(new_sib_mrp, new_sib_sell)

                        sib.selling_price = new_sib_sell
                        sib.mrp = new_sib_mrp
                        synced_siblings.append(sib)

                    # Sync bulk TieredPricing slab rates if defined
                    if prod.tiered_prices:
                        for tp in prod.tiered_prices:
                            matching_sib = next((s for s in prod.variants if parse_unit_weight_in_kg(s.unit_size) == tp.min_qty), None)
                            if matching_sib:
                                tp.unit_price = round(matching_sib.selling_price / tp.min_qty, 2)
                            else:
                                tp_disc = max(0.0, base_sell_rate - (tp.unit_price if tp.unit_price else base_sell_rate))
                                tp.unit_price = round(max(0.5, base_sell_rate - tp_disc), 2)

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
        invalidate_catalog_cache()
        msg = 'Variant updated successfully in SQLite!'
        if synced_siblings:
            msg = f'Variant and {len(synced_siblings)} sibling weight variants updated proportionally!'
        return jsonify({
            'message': msg,
            'variant': variant.to_dict(),
            'sibling_variants': [s.to_dict() for s in synced_siblings],
            'notified_count': notified_count
        })

    @app.route('/api/products/<int:product_id>', methods=['DELETE'])
    @admin_required
    def delete_product(product_id):
        product = Product.query.get_or_404(product_id)
        db.session.delete(product)
        db.session.commit()
        invalidate_catalog_cache()
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
        invalidate_catalog_cache()
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

    @app.route('/api/admin/export/orders.csv', methods=['GET'])
    @admin_required
    def export_orders_csv():
        """Exports all store orders to a clean CSV spreadsheet."""
        import csv
        import io

        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow([
            'Order ID', 'Order Number', 'Date (IST)', 'Customer Name', 'Phone',
            'Delivery Address', 'Pincode', 'Item Count', 'Total MRP (₹)', 'Final Amount (₹)',
            'Total Savings (₹)', 'Payment Method', 'Payment Status', 'Order Status', 'Delivery Availability'
        ])

        orders = Order.query.order_by(Order.created_at.desc()).all()
        for o in orders:
            writer.writerow([
                o.id,
                o.order_number,
                o.created_at.strftime('%Y-%m-%d %H:%M:%S') if o.created_at else '',
                o.customer_name or (o.customer.name if o.customer else 'Counter'),
                o.customer_phone or (o.customer.phone if o.customer else ''),
                (o.customer_address or '').replace('\n', ' ').replace('\r', ''),
                o.pincode or '400031',
                len(o.items) if o.items else 0,
                f"{o.total_mrp:.2f}" if o.total_mrp is not None else '0.00',
                f"{o.final_amount:.2f}",
                f"{o.total_savings:.2f}" if o.total_savings is not None else '0.00',
                o.payment_method or 'Cash on Delivery',
                o.payment_status or 'Unpaid',
                o.status or 'Placed',
                o.delivery_availability or 'pending'
            ])

        output.seek(0)
        today = datetime.now().strftime('%Y%m%d')
        return Response(
            output.getvalue(),
            mimetype='text/csv; charset=utf-8',
            headers={'Content-Disposition': f'attachment; filename=komalmart_orders_{today}.csv'}
        )

    @app.route('/api/admin/export/customers.csv', methods=['GET'])
    @admin_required
    def export_customers_csv():
        """Exports customer directory & Khata ledger balances to CSV."""
        import csv
        import io

        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow([
            'Customer ID', 'Full Name', 'Phone', 'Email', 'Delivery Address',
            'Total Orders', 'Total Spent (₹)', 'Outstanding Khata Debt (₹)', 'Joined Date'
        ])

        customers = User.query.filter_by(role='customer').order_by(User.name.asc()).all()
        for c in customers:
            orders = Order.query.filter((Order.user_id == c.id) | (Order.customer_phone == c.phone)).all()
            total_orders = len(orders)
            total_spent = sum(o.final_amount for o in orders if o.payment_status == 'Paid')
            unpaid_khata = sum(o.final_amount for o in orders if o.payment_status == 'Unpaid')
            writer.writerow([
                c.id,
                c.name,
                c.phone,
                c.email or '',
                (c.address or '').replace('\n', ' ').replace('\r', ''),
                total_orders,
                f"{total_spent:.2f}",
                f"{unpaid_khata:.2f}",
                c.created_at.strftime('%Y-%m-%d') if hasattr(c, 'created_at') and c.created_at else ''
            ])

        output.seek(0)
        today = datetime.now().strftime('%Y%m%d')
        return Response(
            output.getvalue(),
            mimetype='text/csv; charset=utf-8',
            headers={'Content-Disposition': f'attachment; filename=komalmart_khata_customers_{today}.csv'}
        )

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
            status=order_status,
            tracking_token=uuid.uuid4().hex
        )
        new_order.items = order_items

        db.session.add(new_order)
        db.session.commit()
        append_order_to_audit_vault(new_order)

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

    @app.route('/api/admin/batch-ingest-photos', methods=['POST'])
    @admin_required
    def trigger_batch_photo_ingest():
        """
        Scans backend/batch_photos directory, extracts product name, price, and units,
        copies image assets to frontend/public/products, and upserts them into DB.
        Accepts JSON: { dry_run: bool, dir: string }
        """
        from batch_ingest_images import ingest_batch_photos
        data = request.get_json(silent=True) or {}
        dry_run = bool(data.get('dry_run', False))
        custom_dir = data.get('dir', 'backend/batch_photos')

        try:
            result = ingest_batch_photos(batch_dir=custom_dir, dry_run=dry_run, verbose=False, app_instance=app)
            return jsonify(result)
        except Exception as e:
            return jsonify({'success': False, 'error': str(e)}), 500



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
    RestockAlert.query.delete()
    TieredPricing.query.delete()
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
    seed_default_tiered_pricing()
    print("Database successfully seeded with authentic Indian Kirana inventory & default accounts!")


if __name__ == '__main__':
    app = create_app()
    print("Starting Apna Desi Kirana Store Backend API on http://0.0.0.0:5000 ...")
    app.run(host='0.0.0.0', port=5000, debug=True)
