import os
import subprocess
from PIL import Image

def generate_icons():
    # 1. Base 512x512 Master SVG with rich aesthetics, depth, and vibrant colors
    svg_master = '''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 512 512" width="512" height="512">
  <defs>
    <!-- Background Gradient (Deep Forest Emerald to Radiant Jade) -->
    <linearGradient id="bgGrad" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#022c22"/>
      <stop offset="40%" stop-color="#064e3b"/>
      <stop offset="80%" stop-color="#047857"/>
      <stop offset="100%" stop-color="#059669"/>
    </linearGradient>

    <!-- Golden Kirana Wheat Gradient -->
    <linearGradient id="goldGrad" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#fde047"/>
      <stop offset="45%" stop-color="#fbbf24"/>
      <stop offset="85%" stop-color="#f59e0b"/>
      <stop offset="100%" stop-color="#d97706"/>
    </linearGradient>

    <!-- Organic Fresh Leaf Gradient -->
    <linearGradient id="leafGrad" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#a7f3d0"/>
      <stop offset="50%" stop-color="#34d399"/>
      <stop offset="100%" stop-color="#059669"/>
    </linearGradient>

    <!-- Shopping Bag Surface Gradient -->
    <linearGradient id="bagSurface" x1="0%" y1="0%" x2="0%" y2="100%">
      <stop offset="0%" stop-color="#ffffff"/>
      <stop offset="100%" stop-color="#f1f5f9"/>
    </linearGradient>

    <!-- Soft Ambient Drop Shadows -->
    <filter id="shadowDeep" x="-20%" y="-20%" width="140%" height="140%">
      <feDropShadow dx="0" dy="16" stdDeviation="20" flood-color="#011b14" flood-opacity="0.5"/>
    </filter>
    <filter id="badgeShadow" x="-20%" y="-20%" width="140%" height="140%">
      <feDropShadow dx="0" dy="6" stdDeviation="8" flood-color="#022c22" flood-opacity="0.35"/>
    </filter>
  </defs>

  <!-- Outer Rounded Squircle (Continuous Curvature) -->
  <rect width="512" height="512" rx="112" fill="url(#bgGrad)"/>

  <!-- Subtle Outer Rim Reflection -->
  <rect x="4" y="4" width="504" height="504" rx="108" fill="none" stroke="rgba(255,255,255,0.18)" stroke-width="4"/>

  <!-- Golden Subtle Ambient Arch (Aura) -->
  <circle cx="256" cy="275" r="165" fill="#10b981" opacity="0.12"/>

  <!-- SHOPPING BAG HANDLES -->
  <!-- Handle Back -->
  <path d="M198 190 C198 116, 314 116, 314 190" fill="none" stroke="#94a3b8" stroke-width="16" stroke-linecap="round"/>
  <!-- Handle Front Golden Accent -->
  <path d="M206 186 C206 124, 306 124, 306 186" fill="none" stroke="url(#goldGrad)" stroke-width="13" stroke-linecap="round" filter="url(#badgeShadow)"/>

  <!-- FRESH HARVEST ELEMENTS (Wheat & Fresh Leaf Rising Out of Bag) -->
  <!-- Left: Fresh Minty Leaf Sprig -->
  <g transform="translate(196, 172) rotate(-26)">
    <path d="M0 0 C-22 -38, 12 -65, 48 -48 C48 -22, 26 10, 0 0 Z" fill="url(#leafGrad)"/>
    <path d="M0 0 C16 -19, 32 -32, 48 -48" fill="none" stroke="#047857" stroke-width="2.5" stroke-linecap="round"/>
  </g>

  <!-- Right: Indian Desi Kirana Golden Wheat Sheaf -->
  <g transform="translate(316, 172) rotate(22)">
    <!-- Wheat Spine -->
    <path d="M0 0 L-6 -70" fill="none" stroke="url(#goldGrad)" stroke-width="3.5" stroke-linecap="round"/>
    <!-- Kernels -->
    <ellipse cx="-3" cy="-16" rx="8" ry="14" transform="rotate(32 -3 -16)" fill="url(#goldGrad)"/>
    <ellipse cx="-11" cy="-28" rx="8" ry="14" transform="rotate(-32 -11 -28)" fill="url(#goldGrad)"/>
    <ellipse cx="-5" cy="-44" rx="7" ry="13" transform="rotate(28 -5 -44)" fill="url(#goldGrad)"/>
    <ellipse cx="-12" cy="-54" rx="7" ry="13" transform="rotate(-28 -12 -54)" fill="url(#goldGrad)"/>
    <ellipse cx="-8" cy="-68" rx="6" ry="11" fill="url(#goldGrad)"/>
  </g>

  <!-- SHOPPING BAG BODY -->
  <g filter="url(#shadowDeep)">
    <path d="M148 198
             C148 186, 158 176, 170 176
             L342 176
             C354 176, 364 186, 364 198
             L382 396
             C384 412, 372 426, 356 426
             L156 426
             C140 426, 128 412, 130 396
             Z" fill="url(#bagSurface)"/>
  </g>

  <!-- Bag Fold Upper Rim -->
  <path d="M158 180 L354 180 L358 214 C358 220, 353 225, 347 225 L165 225 C159 225, 154 220, 154 214 Z" fill="#e2e8f0" opacity="0.6"/>

  <!-- CENTER EMBLEM: BOLD 'KM' MONOGRAM WITH LIGHTNING SPEED BADGE -->
  <g transform="translate(256, 318)">
    <!-- Stylized Modern Bold 'K' -->
    <!-- Vertical Spine -->
    <rect x="-44" y="-52" width="18" height="104" rx="9" fill="#064e3b"/>
    <!-- Diagonal Upper Arm -->
    <path d="M-28 -6 L14 -50 C20 -56, 30 -54, 35 -48 C40 -42, 38 -32, 32 -26 L-8 12 Z" fill="#047857"/>
    <!-- Diagonal Lower Arm -->
    <path d="M-18 4 L22 46 C27 52, 28 62, 22 68 C16 74, 6 74, 0 68 L-30 32 Z" fill="#059669"/>

    <!-- Quick Commerce Golden Lightning Badge (30-Min Fast Delivery) -->
    <g transform="translate(30, -6)" filter="url(#badgeShadow)">
      <circle cx="15" cy="15" r="23" fill="#ffffff"/>
      <circle cx="15" cy="15" r="20" fill="#fef3c7"/>
      <!-- Lightning Bolt -->
      <path d="M17 1 L6 16 L14 16 L12 30 L25 14 L16 14 Z" fill="url(#goldGrad)"/>
    </g>
  </g>

  <!-- BOTTOM PILL: KOMAL MART BRANDING -->
  <g transform="translate(256, 464)">
    <rect x="-96" y="-15" width="192" height="30" rx="15" fill="rgba(0,0,0,0.28)" stroke="rgba(255,255,255,0.18)" stroke-width="1.5"/>
    <text x="0" y="5" font-family="'Segoe UI', -apple-system, Roboto, sans-serif" font-size="13" font-weight="900" fill="#fef08a" text-anchor="middle" letter-spacing="2">KOMAL MART</text>
  </g>
</svg>'''

    # Save to frontend/public/favicon.svg
    public_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'frontend', 'public')
    svg_path = os.path.join(public_dir, 'favicon.svg')
    with open(svg_path, 'w', encoding='utf-8') as f:
        f.write(svg_master)
    print(f"Updated {svg_path}")

    # Render HTML wrapper for headless Edge to capture
    html_content = f'''<!DOCTYPE html>
<html>
<head>
  <style>
    body, html {{ margin: 0; padding: 0; background: transparent; overflow: hidden; }}
    svg {{ display: block; width: 512px; height: 512px; }}
  </style>
</head>
<body>
  {svg_master}
</body>
</html>'''

    temp_html = os.path.join(public_dir, 'temp_icon.html')
    temp_png = os.path.join(public_dir, 'temp_512.png')
    with open(temp_html, 'w', encoding='utf-8') as f:
        f.write(html_content)

    edge_bin = r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"
    if not os.path.exists(edge_bin):
        edge_bin = r"C:\Program Files\Google\Chrome\Application\chrome.exe"

    cmd = [
        edge_bin,
        "--headless",
        "--disable-gpu",
        "--default-background-color=00000000",
        f"--window-size=512,512",
        f"--screenshot={temp_png}",
        temp_html
    ]
    print(f"Executing: {' '.join(cmd)}")
    subprocess.run(cmd, check=True)

    if os.path.exists(temp_png):
        img = Image.open(temp_png).convert("RGBA")
        # Ensure 512x512 crop
        img_512 = img.crop((0, 0, 512, 512))

        # 1. pwa-512x512.png
        pwa_512 = os.path.join(public_dir, 'pwa-512x512.png')
        img_512.save(pwa_512, "PNG", optimize=True)
        print(f"Saved {pwa_512}")

        # 2. pwa-192x192.png
        pwa_192 = os.path.join(public_dir, 'pwa-192x192.png')
        img_192 = img_512.resize((192, 192), Image.Resampling.LANCZOS)
        img_192.save(pwa_192, "PNG", optimize=True)
        print(f"Saved {pwa_192}")

        # 3. apple-touch-icon.png (180x180)
        apple_icon = os.path.join(public_dir, 'apple-touch-icon.png')
        img_apple = img_512.resize((180, 180), Image.Resampling.LANCZOS)
        img_apple.save(apple_icon, "PNG", optimize=True)
        print(f"Saved {apple_icon}")

        # 4. pwa-maskable-512x512.png (Needs 20% safe-zone margin)
        # Background color #064e3b fills the whole 512x512, central logo fits in 80% circle
        maskable_bg = Image.new("RGBA", (512, 512), (6, 78, 59, 255))
        # Resize squircle to 410x410 and paste in center (offset 51, 51)
        scaled_icon = img_512.resize((410, 410), Image.Resampling.LANCZOS)
        maskable_bg.paste(scaled_icon, (51, 51), scaled_icon)
        maskable_path = os.path.join(public_dir, 'pwa-maskable-512x512.png')
        maskable_bg.save(maskable_path, "PNG", optimize=True)
        print(f"Saved {maskable_path}")

        # Clean up temporary files
        if os.path.exists(temp_html):
            os.remove(temp_html)
        if os.path.exists(temp_png):
            os.remove(temp_png)
        print("All high-resolution crisp app icons successfully generated!")

if __name__ == '__main__':
    generate_icons()
