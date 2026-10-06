<template>
  <div class="kirana-app">
    <!-- Language Selection Onboarding Modal (Shown on First Visit) -->
    <div class="modal-overlay" v-if="showLangModal">
      <div class="modal-card lang-onboarding-card">
        <div class="lang-onboarding-header">
          <div class="store-logo-lg">🌾</div>
          <h2 class="lang-modal-title">आपली भाषा निवडा</h2>
          <p class="lang-modal-sub">भाषा चुनें • Choose your language</p>
        </div>

        <div class="lang-selection-grid">
          <button
            class="lang-choice-btn"
            :class="{ selected: currentLang === 'mr' }"
            @click="currentLang = 'mr'"
          >
            <span class="flag-icon">🇮🇳</span>
            <div class="lang-btn-text">
              <strong>मराठी</strong>
              <small>Maharashtra / Mumbai (मराठी)</small>
            </div>
            <span class="check-mark" v-if="currentLang === 'mr'">✓</span>
          </button>

          <button
            class="lang-choice-btn"
            :class="{ selected: currentLang === 'hi' }"
            @click="currentLang = 'hi'"
          >
            <span class="flag-icon">🇮🇳</span>
            <div class="lang-btn-text">
              <strong>हिंदी</strong>
              <small>Hindi (हिंदी)</small>
            </div>
            <span class="check-mark" v-if="currentLang === 'hi'">✓</span>
          </button>

          <button
            class="lang-choice-btn"
            :class="{ selected: currentLang === 'en' }"
            @click="currentLang = 'en'"
          >
            <span class="flag-icon">🇬🇧</span>
            <div class="lang-btn-text">
              <strong>English</strong>
              <small>English (Default)</small>
            </div>
            <span class="check-mark" v-if="currentLang === 'en'">✓</span>
          </button>
        </div>

        <button class="lang-proceed-btn" @click="selectLanguage(currentLang)">
          {{ currentLang === 'mr' ? 'पुढे चला ➔ (Start Shopping)' : (currentLang === 'hi' ? 'आगे बढ़ें ➔' : 'Proceed ➔') }}
        </button>
      </div>
    </div>

    <!-- Top Announcement Bar (Hidden for Store Admin) -->
    <div class="top-announcement" v-if="!isAdminLoggedIn">
      <div style="display: flex; align-items: center; gap: 16px; flex-wrap: wrap;">
        <span>🌾 <strong>{{ t('store_name_full') }}</strong> — {{ t('tagline_announcement') }}</span>
        <span style="display: inline-flex; align-items: center; gap: 6px;">🛵 {{ t('delivery_announcement') }}</span>
      </div>
      <div style="display: flex; align-items: center; gap: 16px;">
        <span>📞 {{ t('helpline_label') }}: <strong>91420-52967</strong></span>
        <!-- Header Language Switcher Dropdown -->
        <div class="lang-dropdown-pill">
          <button class="lang-pill-btn" @click="toggleLangDropdown">
            🌐 {{ currentLang === 'mr' ? 'मराठी' : (currentLang === 'hi' ? 'हिंदी' : 'English') }} ▾
          </button>
          <div class="lang-dropdown-menu" v-if="showLangDropdown">
            <button :class="{ active: currentLang === 'mr' }" @click="selectLanguage('mr'); showLangDropdown = false">
              🇮🇳 मराठी
            </button>
            <button :class="{ active: currentLang === 'hi' }" @click="selectLanguage('hi'); showLangDropdown = false">
              🇮🇳 हिंदी
            </button>
            <button :class="{ active: currentLang === 'en' }" @click="selectLanguage('en'); showLangDropdown = false">
              🇬🇧 English
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- PWA Install Banner -->
    <div v-if="showInstallBanner && !isAppInstalled" class="pwa-install-banner">
      <div class="pwa-banner-inner">
        <div class="pwa-banner-left">
          <div class="pwa-app-icon" style="overflow: hidden; padding: 0;">
            <img src="/favicon.svg" alt="Komal Mart" style="width: 100%; height: 100%; object-fit: cover; border-radius: 8px;" />
          </div>
          <div class="pwa-banner-info">
            <strong class="pwa-banner-title">{{ t('pwa_install_title') }}</strong>
            <span class="pwa-banner-sub">{{ t('pwa_install_sub') }}</span>
          </div>
        </div>
        <div class="pwa-banner-right">
          <button class="pwa-btn-qr" @click="showQRModal = true" title="Scan with Phone">
            📱 Phone QR
          </button>
          <button class="pwa-btn-install" @click="triggerInstall">
            📲 {{ t('pwa_install_btn') }}
          </button>
          <button class="pwa-btn-dismiss" @click="dismissInstallBanner" title="Dismiss">
            ✕
          </button>
        </div>
      </div>
    </div>

    <!-- Main Navigation Header -->
    <header class="kirana-header">
      <div class="header-container">
        <!-- Logo & Store Branding -->
        <div class="store-brand" @click="resetFilters">
          <div class="store-logo" style="overflow: hidden; padding: 0;">
            <img src="/favicon.svg" alt="Komal Mart" style="width: 100%; height: 100%; object-fit: cover; border-radius: 10px;" />
          </div>
          <div class="brand-text">
            <div style="display: flex; align-items: center; gap: 6px;">
              <h1>{{ t('store_title') }}</h1>
              <span class="mobile-delivery-tag" style="display: inline-flex; align-items: center; font-size: 0.68rem; font-weight: 800; color: #047857; background: #ecfdf5; padding: 2px 6px; border-radius: 4px; border: 1px solid #a7f3d0;">⚡ {{ currentLang === 'en' ? 'Fast Wadala' : (currentLang === 'mr' ? 'जलद वडाळा' : 'तेज़ वडाला') }}</span>
            </div>
            <p class="desktop-only">{{ t('store_subtitle') }}</p>
          </div>
        </div>

        <!-- Search Bar -->
        <div class="search-bar-wrap" v-if="!isAdminLoggedIn || adminActiveTab === 'storefront'">
          <span class="search-icon">🔍</span>
          <input
            type="text"
            v-model="searchQuery"
            @input="debounceFetchProducts"
            :placeholder="t('search_placeholder')"
            class="search-input"
          />
          <button
            v-if="searchQuery"
            type="button"
            class="search-clear-btn"
            @click="clearSearch"
            title="Clear search"
          >
            ✕
          </button>
          <!-- 1-Tap Mic Voice Order Trigger in Search Bar -->
          <button
            type="button"
            class="search-mic-ai-btn"
            @click="openAiModalByRole"
            :title="isAdminLoggedIn && !adminPreviewAsCustomer ? '👑 कोमल AI दुकानदार सहाय्यक (Store Control)' : (tAi('ai_modal_title') + ' (बोलून सामान मागवा)')"
          >
            🎙️
          </button>
        </div>

        <!-- Header Actions: User Profile / Login & Cart -->
        <div class="header-actions">
          <!-- ADMIN CONTROLS (IF LOGGED IN AS ADMIN) -->
          <template v-if="isAdminLoggedIn">
            <button
              v-if="adminActiveTab !== 'storefront'"
              type="button"
              class="user-btn"
              @click="switchAdminTab('storefront')"
              style="background: #ecfdf5; border-color: #6ee7b7; color: #064e3b; font-weight: 800;"
              title="दुकानदार व्ह्यू (Storefront View)"
            >
              🏪 <span>{{ currentLang === 'mr' ? 'दुकानदार व्ह्यू' : 'Storefront' }}</span>
            </button>
            <button
              v-else
              type="button"
              class="user-btn"
              @click="switchAdminTab('orders')"
              style="background: #eff6ff; border-color: #93c5fd; color: #1e40af; font-weight: 800;"
              title="ईआरपी ऑर्डर्स (Orders ERP)"
            >
              🧾 <span>{{ currentLang === 'mr' ? 'ऑर्डर्स लेजर' : 'Orders ERP' }}</span>
            </button>
            <span style="font-size: 0.88rem; font-weight: 800; color: #064e3b; background: #ecfdf5; padding: 6px 14px; border-radius: 20px; border: 1px solid #a7f3d0;" class="desktop-only">
              👑 {{ t('admin_badge') }}
            </span>
            <button class="user-btn user-logout-btn" @click="logout" style="padding: 7px 10px; color: #dc2626; border-color: #fecaca; background: #fff1f2;">
              🚪 {{ t('logout') }}
            </button>
          </template>

          <!-- CUSTOMER OR GUEST CONTROLS -->
          <template v-else>
            <!-- Mobile Language Dropdown Pill (Replaces bulky top banner on phone) -->
            <div class="lang-dropdown-pill mobile-only-inline" style="position: relative;">
              <button class="lang-pill-btn" @click="toggleLangDropdown" style="padding: 5px 8px; font-size: 0.78rem;">
                🌐 {{ currentLang === 'mr' ? 'मराठी' : (currentLang === 'hi' ? 'हिंदी' : 'EN') }} ▾
              </button>
              <div class="lang-dropdown-menu" v-if="showLangDropdown" style="position: absolute; top: 100%; right: 0; z-index: 100;">
                <button :class="{ active: currentLang === 'mr' }" @click="selectLanguage('mr'); showLangDropdown = false">
                  🇮🇳 मराठी
                </button>
                <button :class="{ active: currentLang === 'hi' }" @click="selectLanguage('hi'); showLangDropdown = false">
                  🇮🇳 हिंदी
                </button>
                <button :class="{ active: currentLang === 'en' }" @click="selectLanguage('en'); showLangDropdown = false">
                  🇬🇧 English
                </button>
              </div>
            </div>

            <!-- Install App Button on Mobile & Desktop Header -->
            <button v-if="!isAppInstalled" class="pwa-header-btn" @click="triggerInstall" :title="t('pwa_install_btn')" style="padding: 6px 10px; font-size: 0.78rem; font-weight: 800; background: #ecfdf5; color: #064e3b; border: 1.5px solid #a7f3d0; border-radius: 8px;">
              📲 <span>{{ currentLang === 'mr' ? 'ॲप' : (currentLang === 'hi' ? 'ऐप' : 'App') }}</span>
            </button>

            <!-- Logged in Customer -->
            <div v-if="currentUser" style="display: flex; align-items: center; gap: 6px;">
              <button class="store-credit-header-badge" @click="openAccountModal" :title="t('store_credit_balance')">
                💳 <strong>₹{{ (currentUser.wallet_balance || 0).toFixed(2) }}</strong>
              </button>
              <button class="user-btn" @click="openAccountModal" :title="t('account')">
                👤 <span class="desktop-only">{{ t('greeting') }}, </span><strong>{{ currentUser.name.split(' ')[0] }}</strong>
              </button>
              <button class="user-btn user-logout-btn" @click="logout" :title="t('logout')" style="padding: 7px 10px; color: #dc2626; border-color: #fecaca; background: #fff1f2;">
                🚪<span class="desktop-only" style="margin-left: 4px;">{{ t('logout') }}</span>
              </button>
            </div>

            <!-- Guest / Not Logged In -->
            <button v-else class="user-btn" @click="openAuthModal('login')">
              👤 {{ t('login_btn') }}
            </button>

            <!-- QR Code Button to Open on Phone (Desktop Only) -->
            <button class="qr-header-btn desktop-only" @click="showQRModal = true" title="Scan to open on Phone">
              📱 <span>Scan on Phone</span>
            </button>

            <!-- Shopping Cart (Only for Desktop Header; Mobile uses Bottom Bar) -->
            <button class="cart-btn desktop-only" @click="isCartOpen = true">
              🛒 <span>{{ t('cart_bag') }}</span>
              <span class="cart-badge">{{ cartTotalQuantity }}</span>
              <span v-if="cartTotalAmount > 0">₹{{ cartTotalAmount }}</span>
            </button>
          </template>
        </div>
      </div>
    </header>

    <!-- DUKANDAR STOREKEEPER COMMAND DOCK (Shown on Storefront when logged in as Admin) -->
    <div class="dukandar-top-dock" v-if="isAdminLoggedIn && adminActiveTab === 'storefront'">
      <div class="dukandar-dock-inner">
        <div class="dukandar-dock-left">
          <div class="dukandar-mode-pill">
            <span class="dukandar-mode-dot"></span>
            <span class="dukandar-mode-title">👑 {{ currentLang === 'mr' ? 'दुकानदार मोड' : (currentLang === 'hi' ? 'दुकानदार मोड' : 'Dukandar Mode') }}</span>
          </div>

          <div class="dukandar-dock-tabs">
            <button
              type="button"
              class="dukandar-dock-tab"
              :class="{ active: adminActiveTab === 'storefront' }"
              @click="switchAdminTab('storefront')"
            >
              🏪 {{ currentLang === 'mr' ? 'दुकान' : (currentLang === 'hi' ? 'दुकान' : 'Store') }}
            </button>
            <button
              type="button"
              class="dukandar-dock-tab"
              :class="{ active: adminActiveTab === 'pos' }"
              @click="switchAdminTab('pos')"
            >
              ⚡ POS
            </button>
            <button
              type="button"
              class="dukandar-dock-tab"
              :class="{ active: adminActiveTab === 'orders' }"
              @click="switchAdminTab('orders')"
            >
              🧾 {{ currentLang === 'mr' ? 'ऑर्डर्स' : (currentLang === 'hi' ? 'ऑर्डर्स' : 'Orders') }}
              <span v-if="unpaidAdminOrders.length > 0" class="dock-badge-danger">
                {{ unpaidAdminOrders.length }}
              </span>
            </button>
            <button
              type="button"
              class="dukandar-dock-tab"
              :class="{ active: adminActiveTab === 'khata' }"
              @click="switchAdminTab('khata')"
            >
              📒 {{ currentLang === 'mr' ? 'खाता' : (currentLang === 'hi' ? 'खाता' : 'Khata') }}
              <span v-if="adminKhataSummary.total_market_udhaar > 0" class="dock-badge-warning">
                ₹
              </span>
            </button>
            <button
              type="button"
              class="dukandar-dock-tab desktop-only"
              :class="{ active: adminActiveTab === 'zreport' }"
              @click="switchAdminTab('zreport')"
            >
              📊 Z-Report
            </button>
            <button
              type="button"
              class="dukandar-dock-tab desktop-only"
              :class="{ active: adminActiveTab === 'inventory' }"
              @click="switchAdminTab('inventory')"
            >
              📋 {{ currentLang === 'mr' ? 'ईआरपी यादी' : (currentLang === 'hi' ? 'ईआरपी सूची' : 'ERP Table') }}
            </button>
          </div>
        </div>

        <div class="dukandar-dock-right">
          <!-- Customer View Preview Toggle -->
          <button
            type="button"
            class="dukandar-preview-toggle-btn"
            :class="{ active: adminPreviewAsCustomer }"
            @click="adminPreviewAsCustomer = !adminPreviewAsCustomer"
            :title="adminPreviewAsCustomer ? 'Exit Customer Preview' : 'Preview store exactly as customers see it'"
          >
            <span v-if="adminPreviewAsCustomer">👁️ {{ currentLang === 'mr' ? 'ग्राहक दृश्य चालू' : (currentLang === 'hi' ? 'ग्राहक दृश्य चालू' : 'Customer View (ON)') }}</span>
            <span v-else>👁️ {{ currentLang === 'mr' ? 'ग्राहक दृश्य' : (currentLang === 'hi' ? 'ग्राहक दृश्य' : 'Customer Preview') }}</span>
          </button>

          <button
            type="button"
            class="dukandar-quick-action-btn primary"
            @click="showAddProductModal = true; addProductMode = 'quick';"
            title="Add new product to catalog"
          >
            ➕ {{ t('admin_add_product') }}
          </button>

          <button
            type="button"
            class="dukandar-quick-action-btn"
            @click="openDukandarAiModal"
            title="Komal AI Dukandar Assistant (Store Control)"
          >
            🎙️ AI Assistant
          </button>
        </div>
      </div>

      <!-- Preview Banner when preview mode is ON -->
      <div v-if="adminPreviewAsCustomer" class="dukandar-preview-banner">
        <span>👁️ {{ currentLang === 'mr' ? 'तुम्ही सध्या "ग्राहक दृश्य" पाहत आहात — सर्व संपादने (Edit buttons) तात्पुरती लपवली आहेत.' : (currentLang === 'hi' ? 'आप वर्तमान में "ग्राहक दृश्य" देख रहे हैं — सभी एडिट विकल्प छुपा दिए गए हैं।' : 'You are currently previewing as a Customer — all inline edit buttons are hidden.') }}</span>
        <button type="button" class="preview-exit-btn" @click="adminPreviewAsCustomer = false">
          ✏️ {{ currentLang === 'mr' ? 'संपादने चालू करा' : (currentLang === 'hi' ? 'एडिट चालू करें' : 'Exit Preview') }}
        </button>
      </div>
    </div>

    <!-- Category Bar (Visible for customer store view & admin storefront view) -->
    <nav class="category-nav" v-if="!isAdminLoggedIn || adminActiveTab === 'storefront'">
      <div class="category-scroll">
        <button
          class="category-pill"
          :class="{ active: selectedCategorySlug === '' }"
          @click="selectCategory('')"
        >
          🌟 {{ t('cat_all') }}
        </button>
        <button
          v-if="adminAllowClearancePublic"
          class="category-pill clearance-pill"
          :class="{ active: selectedCategorySlug === 'clearance' }"
          @click="selectCategory('clearance')"
          style="border-color: #fca5a5; color: #dc2626; font-weight: 800; background: #fff5f5;"
        >
          💥 {{ currentLang === 'en' ? 'Special Offers' : (currentLang === 'mr' ? 'विशेष सवलत' : 'विशेष छूट') }}
        </button>
        <button
          v-for="cat in categories"
          :key="cat.id"
          class="category-pill"
          :class="{ active: selectedCategorySlug === cat.slug }"
          @click="selectCategory(cat.slug)"
        >
          {{ getCategoryEmoji(cat.slug) }} {{ getLocalizedCategoryName(cat, currentLang) }} ({{ cat.product_count }})
        </button>
      </div>
    </nav>

    <!-- Toast Notification -->
    <div
      v-if="toastMessage"
      style="position: fixed; bottom: 28px; left: 50%; transform: translateX(-50%); z-index: 100; background: #1c1917; color: #fffbeb; padding: 12px 26px; border-radius: 30px; box-shadow: 0 12px 28px rgba(0,0,0,0.35); font-weight: 700; font-size: 0.95rem; border: 1.5px solid #d97706;"
    >
      {{ toastMessage }}
    </div>

    <!-- ======================================================== -->
    <!-- VIEW 1: CUSTOMER STORE VIEW / DUKANDAR STOREFRONT        -->
    <!-- ======================================================== -->
    <main class="main-layout" v-if="!isAdminLoggedIn || adminActiveTab === 'storefront'">
      <!-- Sleek Mobile-Only Quick Strip (Replaces bulky marketing cards on phone) -->
      <div class="mobile-app-quick-strip">
        <div class="quick-strip-left">
          <span>⚡</span>
          <span>{{ currentLang === 'en' ? 'Fast Wadala Delivery • Free on ₹500+' : (currentLang === 'mr' ? 'जलद वडाळा डिलिव्हरी • ₹५००+ वर मोफत' : 'तेज़ वडाला डिलीवरी • ₹500+ पर फ्री') }}</span>
        </div>
        <button
          type="button"
          class="quick-strip-btn"
          @click="showMonthlyParchaModal = true"
        >
          📝 {{ currentLang === 'en' ? 'Monthly Ration' : (currentLang === 'mr' ? 'महिन्याचा किराणा' : 'महीने का राशन') }}
        </button>
      </div>

      <!-- Desi Kirana Hero Promotional Banner -->
      <section class="hero-promo-banner desktop-only">
        <div class="hero-content-grid">
          <div class="hero-text">
            <h2>🌾 {{ t('hero_title') }}</h2>
            <p>{{ t('hero_desc') }}</p>
            <div class="hero-perks">
              <div class="hero-perk-item">
                <svg viewBox="0 0 24 24" width="15" height="15" fill="none" stroke="#064e3b" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><path d="m16 16 3-8 3 8c-.87.65-1.92 1-3 1s-2.13-.35-3-1Z"/><path d="m2 16 3-8 3 8c-.87.65-1.92 1-3 1s-2.13-.35-3-1Z"/><path d="M7 21h10"/><path d="M12 3v18"/><path d="M3 7h2c2 0 5-1 7-2 2 1 5 2 7 2h2"/></svg>
                <span>{{ t('hero_perk_weight') }}</span>
              </div>
              <div class="hero-perk-item">
                <svg viewBox="0 0 24 24" width="15" height="15" fill="none" stroke="#064e3b" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><polygon points="13 2 3 14 12 14 11 22 21 10 12 10 13 2"/></svg>
                <span>{{ t('hero_perk_delivery') }}</span>
              </div>
              <div class="hero-perk-item">
                <svg viewBox="0 0 24 24" width="15" height="15" fill="none" stroke="#064e3b" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><path d="M4 19.5v-15A2.5 2.5 0 0 1 6.5 2H20v20H6.5a2.5 2.5 0 0 1-2.5-2.5Z"/><path d="M6 6h10"/><path d="M6 10h10"/></svg>
                <span>{{ t('hero_perk_khata') }}</span>
              </div>
              <div class="hero-perk-item">
                <svg viewBox="0 0 24 24" width="15" height="15" fill="none" stroke="#064e3b" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/><polyline points="9 12 11 14 15 10"/></svg>
                <span>{{ t('hero_perk_brands') }}</span>
              </div>
            </div>
            <div class="hero-action-row">
              <button class="hero-cta-btn" @click="openMonthlyParchaModal">
                📝 {{ t('hero_cta') }}
              </button>
            </div>
          </div>

          <!-- Hero Right-Side Visual Showcase Card -->
          <div class="hero-showcase-card">
            <div class="hero-showcase-header">
              <span class="hero-showcase-badge">🌾 {{ currentLang === 'mr' ? 'थेट घाऊक मंडी भाव' : (currentLang === 'hi' ? 'सीधा थोक मंडी रेट' : 'Direct Wholesale Mandi') }}</span>
              <span class="hero-showcase-sub">✓ {{ currentLang === 'mr' ? '१००% शुद्धता' : (currentLang === 'hi' ? '100% शुद्धता' : '100% Pure') }}</span>
            </div>
            <div class="hero-showcase-imgs">
              <div class="hero-showcase-item">
                <img src="/products/chakki-atta-loose.jpg" alt="Chakki Atta" class="hero-showcase-thumb" />
                <span class="hero-showcase-title">{{ currentLang === 'mr' ? 'चक्कीचे गव्हाचे पीठ' : (currentLang === 'hi' ? 'चक्की का ताज़ा आटा' : 'Fresh Chakki Atta') }}</span>
                <span class="hero-showcase-rate">₹38/kg</span>
              </div>
              <div class="hero-showcase-item">
                <img src="/products/toor-daal-gavran.jpg" alt="Toor Dal" class="hero-showcase-thumb" />
                <span class="hero-showcase-title">{{ currentLang === 'mr' ? 'गावरान तूर डाळ' : (currentLang === 'hi' ? 'गावरान अरहर / तूर दाल' : 'Gavran Toor Dal') }}</span>
                <span class="hero-showcase-rate">₹190/kg</span>
              </div>
            </div>
            <div class="hero-showcase-badge-bar">
              <span>⚖️ {{ currentLang === 'mr' ? 'सरकारी वजन प्रमाणित' : (currentLang === 'hi' ? 'सरकारी काँटा प्रमाणित' : 'Govt Scale Certified') }}</span>
              <span>⚡ {{ currentLang === 'mr' ? 'जलद घरपोच डिलिव्हरी' : (currentLang === 'hi' ? 'तेज़ होम डिलीवरी' : 'Fast Home Delivery') }}</span>
            </div>
          </div>
        </div>
      </section>

      <!-- 4 Trust & Value Pillars Section -->
      <section class="trust-pillars-section desktop-only">
        <div class="pillar-card">
          <div class="pillar-icon-wrap">
            <svg viewBox="0 0 24 24" width="22" height="22" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><path d="m16 16 3-8 3 8c-.87.65-1.92 1-3 1s-2.13-.35-3-1Z"/><path d="m2 16 3-8 3 8c-.87.65-1.92 1-3 1s-2.13-.35-3-1Z"/><path d="M7 21h10"/><path d="M12 3v18"/><path d="M3 7h2c2 0 5-1 7-2 2 1 5 2 7 2h2"/></svg>
          </div>
          <div class="pillar-content">
            <h4 class="pillar-title">{{ t('pillar_scale_title') }}</h4>
            <p class="pillar-desc">{{ t('pillar_scale_desc') }}</p>
          </div>
        </div>

        <div class="pillar-card">
          <div class="pillar-icon-wrap">
            <svg viewBox="0 0 24 24" width="22" height="22" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><line x1="12" y1="1" x2="12" y2="23"/><path d="M17 5H9.5a3.5 3.5 0 0 0 0 7h5a3.5 3.5 0 0 1 0 7H6"/></svg>
          </div>
          <div class="pillar-content">
            <h4 class="pillar-title">{{ t('pillar_rates_title') }}</h4>
            <p class="pillar-desc">{{ t('pillar_rates_desc') }}</p>
          </div>
        </div>

        <div class="pillar-card">
          <div class="pillar-icon-wrap">
            <svg viewBox="0 0 24 24" width="22" height="22" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><path d="M4 19.5v-15A2.5 2.5 0 0 1 6.5 2H20v20H6.5a2.5 2.5 0 0 1-2.5-2.5Z"/><path d="M6 6h10"/><path d="M6 10h10"/></svg>
          </div>
          <div class="pillar-content">
            <h4 class="pillar-title">{{ t('pillar_khata_title') }}</h4>
            <p class="pillar-desc">{{ t('pillar_khata_desc') }}</p>
          </div>
        </div>

        <div class="pillar-card">
          <div class="pillar-icon-wrap">
            <svg viewBox="0 0 24 24" width="22" height="22" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><polygon points="13 2 3 14 12 14 11 22 21 10 12 10 13 2"/></svg>
          </div>
          <div class="pillar-content">
            <h4 class="pillar-title">{{ t('pillar_speed_title') }}</h4>
            <p class="pillar-desc">{{ t('pillar_speed_desc') }}</p>
          </div>
        </div>
      </section>

      <!-- 🌾 1-TAP REPEAT LAST MONTH'S RATION BANNER -->
      <div
        v-if="currentUser && lastDeliveredCustomerOrder"
        class="repeat-ration-banner"
        style="margin: 0 0 16px 0; background: linear-gradient(135deg, #ecfdf5 0%, #f0fdf4 100%); border: 1.5px solid #10b981; border-radius: 12px; padding: 12px 16px; display: flex; align-items: center; justify-content: space-between; gap: 12px; flex-wrap: wrap; box-shadow: 0 2px 8px rgba(16, 185, 129, 0.08);"
      >
        <div style="display: flex; align-items: center; gap: 12px; min-width: 240px;">
          <div style="font-size: 1.8rem; background: white; width: 44px; height: 44px; border-radius: 50%; display: flex; align-items: center; justify-content: center; box-shadow: 0 2px 6px rgba(0,0,0,0.06); flex-shrink: 0;">
            🌾
          </div>
          <div>
            <div style="font-size: 0.96rem; font-weight: 800; color: #064e3b; display: flex; align-items: center; gap: 6px;">
              <span>{{ currentLang === 'en' ? "Repeat Last Month's Ration" : (currentLang === 'mr' ? 'मागील महिन्याचे रेशन पुन्हा मागवा' : 'पिछले महीने का राशन दोबारा मंगाएं') }}</span>
              <span style="font-size: 0.7rem; background: #059669; color: white; padding: 2px 6px; border-radius: 10px; font-weight: 700;">1-Tap</span>
            </div>
            <div style="font-size: 0.8rem; color: #047857; margin-top: 2px;">
              {{ currentLang === 'en'
                  ? `Order #${lastDeliveredCustomerOrder.order_number} (${lastDeliveredCustomerOrder.items?.length || 0} staples, ₹${lastDeliveredCustomerOrder.final_amount}) • Tap to fill cart instantly!`
                  : (currentLang === 'mr'
                      ? `ऑर्डर #${lastDeliveredCustomerOrder.order_number} (${lastDeliveredCustomerOrder.items?.length || 0} वस्तू, ₹${lastDeliveredCustomerOrder.final_amount}) • एका क्लिकमध्ये कार्टमध्ये भरा!`
                      : `ऑर्डर #${lastDeliveredCustomerOrder.order_number} (${lastDeliveredCustomerOrder.items?.length || 0} सामान, ₹${lastDeliveredCustomerOrder.final_amount}) • एक क्लिक में कार्ट में भरें!`)
              }}
            </div>
          </div>
        </div>

        <div style="display: flex; gap: 8px; align-items: center;">
          <button
            @click="reorderEntireBill(lastDeliveredCustomerOrder)"
            style="background: #047857; color: white; border: none; padding: 8px 16px; border-radius: 8px; font-weight: 800; font-size: 0.85rem; cursor: pointer; display: inline-flex; align-items: center; gap: 6px; box-shadow: 0 2px 6px rgba(4, 120, 87, 0.2);"
          >
            🛒 {{ currentLang === 'en' ? 'Add All to Cart' : (currentLang === 'mr' ? 'सर्व वस्तू कार्टमध्ये जोडा' : 'सभी सामान कार्ट में जोड़ें') }}
          </button>
          <button
            @click="viewOrderReceipt(lastDeliveredCustomerOrder)"
            style="background: white; border: 1px solid #a7f3d0; color: #047857; padding: 8px 12px; border-radius: 8px; font-weight: 700; font-size: 0.82rem; cursor: pointer;"
            title="View Previous Bill"
          >
            🧾 {{ currentLang === 'en' ? 'View Bill' : (currentLang === 'mr' ? 'पर्चा पहा' : 'पर्चा देखें') }}
          </button>
        </div>
      </div>

      <!-- Secondary Filter Row -->
      <div class="filter-row">
        <div class="sub-filter-group">
          <button
            class="filter-btn"
            :class="{ active: looseFilter === 'all' }"
            @click="setLooseFilter('all')"
          >
            {{ t('filter_all') }}
          </button>
          <button
            class="filter-btn"
            :class="{ active: looseFilter === 'true' }"
            @click="setLooseFilter('true')"
          >
            🌾 {{ t('filter_loose') }}
          </button>
          <button
            class="filter-btn"
            :class="{ active: looseFilter === 'false' }"
            @click="setLooseFilter('false')"
          >
            📦 {{ t('filter_packed') }}
          </button>
        </div>

        <div style="display: flex; align-items: center; gap: 8px;">
          <span style="font-size: 0.84rem; color: #57534e; font-weight: 700;">{{ t('sort_label') }}</span>
          <select v-model="sortBy" @change="fetchProducts" class="sort-select">
            <option value="">{{ t('sort_featured') }}</option>
            <option value="price_asc">{{ t('sort_price_asc') }}</option>
            <option value="price_desc">{{ t('sort_price_desc') }}</option>
            <option value="name">{{ t('sort_name') }}</option>
          </select>
        </div>
      </div>

      <!-- Loading Skeleton State -->
      <div v-if="loading" class="products-grid">
        <div v-for="i in 8" :key="i" class="product-card skeleton-card">
          <div class="skeleton-thumb"></div>
          <div class="skeleton-info">
            <div class="skeleton-line skeleton-title"></div>
            <div class="skeleton-line skeleton-sub"></div>
            <div class="skeleton-line skeleton-price"></div>
            <div class="skeleton-btn"></div>
          </div>
        </div>
      </div>

      <!-- Empty State -->
      <div v-else-if="products.length === 0" style="text-align: center; padding: 70px 20px; background: white; border-radius: 14px; border: 1.5px dashed #d6cfc7;">
        <div style="font-size: 3.5rem; margin-bottom: 14px;">🔍</div>
        <h3 style="font-size: 1.3rem; font-weight: 800; color: #1c1917;">{{ currentLang === 'mr' ? 'कोणतेही सामान सापडले नाही' : (currentLang === 'hi' ? 'कोई सामान नहीं मिला' : 'No items found') }}</h3>
        <p style="color: #78716c; font-size: 0.95rem; margin-top: 4px;">
          {{ currentLang === 'mr' ? 'कृपया दुसरे नाव शोधा किंवा फिल्टर रीसेट करा.' : (currentLang === 'hi' ? 'कृपया कोई दूसरा नाम खोजें या फ़िल्टर रीसेट करें।' : 'Please search with another keyword or reset filters.') }}
        </p>
        <button
          @click="resetFilters"
          style="margin-top: 18px; padding: 10px 22px; background: #047857; color: white; border: none; border-radius: 10px; font-weight: 800; cursor: pointer;"
        >
          {{ t('cat_all') }}
        </button>
      </div>

      <!-- Products Grid -->
      <div v-else class="products-grid">
        <div v-for="prod in products" :key="prod.id" class="product-card" :class="{ 'is-out-of-stock': getActiveVariant(prod) && !getActiveVariant(prod).is_available }">
          <!-- Product Photo (Verified Local Images) -->
          <div class="product-thumb-wrap" @click="openQuickView(prod)">
            <img
              :src="getProductCardImage(prod)"
              :alt="prod.name"
              class="product-thumb"
              loading="lazy"
              @error="handleImageFallback($event)"
            />
            <span v-if="prod.is_loose" class="loose-badge">🌾 {{ t('badge_loose') }}</span>
            <span v-else class="packed-badge">📦 {{ t('badge_packed') }}</span>
            <span class="brand-badge" v-if="prod.brand && prod.brand !== 'Loose / Desi Mandi' && prod.brand !== 'Local / Mandi' && prod.brand !== 'Loose / Local'">{{ prod.brand }}</span>
            <span v-if="hasClearanceVariant(prod)" class="clearance-badge" style="position: absolute; top: 8px; right: 8px; background: #dc2626; color: white; padding: 2px 7px; border-radius: 6px; font-size: 0.72rem; font-weight: 900; z-index: 2; box-shadow: 0 2px 6px rgba(220,38,38,0.4);">
              🔥 {{ currentLang === 'en' ? 'Clearance' : 'सेल' }}
            </span>
            <span v-if="getActiveVariant(prod) && !getActiveVariant(prod).is_available" class="stock-out-badge">
              🚫 {{ t('out_of_stock') }}
            </span>
            <div class="quick-view-overlay">
              <span>👁️ {{ t('view_details_btn') }}</span>
            </div>
          </div>

          <!-- Product Details -->
          <div class="product-info">
            <h3 class="product-title" @click="openQuickView(prod)">{{ getLocalizedProductName(prod, currentLang) }}</h3>
            <div class="product-sub-title">{{ currentLang === 'en' ? (prod.name_hi || '') : prod.name }}</div>
            <p class="product-desc">{{ prod.description }}</p>

            <!-- Wholesale Tier Badges -->
            <div v-if="prod.tiered_prices && prod.tiered_prices.length > 0" class="wholesale-tier-badge">
              🏷️ <strong style="color: #065f46;">{{ t('wholesale_label') }}:</strong>
              <span v-for="tp in prod.tiered_prices" :key="tp.id" class="wholesale-tier-chip">
                {{ tp.min_qty }}kg+ @ ₹{{ tp.unit_price }}/kg
              </span>
            </div>

            <!-- DUKANDAR CARD OVERLAY (Visible for admin on storefront when preview is off) -->
            <div class="dukandar-card-strip" v-if="isAdminLoggedIn && !adminPreviewAsCustomer && getActiveVariant(prod)">
              <div class="dukandar-card-stock-pill" :class="{
                'stock-good': getActiveVariant(prod).is_available && (getActiveVariant(prod).stock_quantity || 0) > 5,
                'stock-low': getActiveVariant(prod).is_available && (getActiveVariant(prod).stock_quantity || 0) <= 5 && (getActiveVariant(prod).stock_quantity || 0) > 0,
                'stock-none': !getActiveVariant(prod).is_available || (getActiveVariant(prod).stock_quantity || 0) <= 0
              }">
                <span v-if="getActiveVariant(prod).is_available && (getActiveVariant(prod).stock_quantity || 0) > 0">
                  📦 {{ currentLang === 'mr' ? 'शिल्लक' : (currentLang === 'hi' ? 'स्टॉक' : 'Stock') }}: <strong>{{ getActiveVariant(prod).stock_quantity }}</strong>
                </span>
                <span v-else>
                  🔴 <strong>{{ currentLang === 'mr' ? 'स्टॉक संपला' : (currentLang === 'hi' ? 'स्टॉक खत्म' : 'Out of Stock') }}</strong> (0)
                </span>
              </div>

              <div class="dukandar-card-actions">
                <button
                  type="button"
                  class="dukandar-btn-edit"
                  @click.stop="openQuickPriceEdit(prod, getActiveVariant(prod))"
                  :title="currentLang === 'mr' ? 'किंमत व स्टॉक बदला' : 'Edit Price & Stock'"
                >
                  ✏️ {{ currentLang === 'mr' ? 'बदला' : (currentLang === 'hi' ? 'बदलें' : 'Edit') }}
                </button>

                <button
                  type="button"
                  class="dukandar-btn-photos"
                  @click.stop="openEditPhotosModal(prod)"
                  :title="currentLang === 'mr' ? 'फोटो बदला (3-Angle Photos)' : (currentLang === 'hi' ? 'फोटो बदलें (3-Angle Photos)' : 'Edit Photos')"
                >
                  📸 {{ currentLang === 'mr' ? 'फोटो' : 'Photo' }}
                </button>

                <button
                  type="button"
                  class="dukandar-btn-toggle"
                  :class="{ 'is-in-stock': getActiveVariant(prod).is_available }"
                  @click.stop="toggleVariantStock(getActiveVariant(prod))"
                  :title="getActiveVariant(prod).is_available ? 'Make Out of Stock' : 'Make In Stock'"
                >
                  {{ getActiveVariant(prod).is_available ? '🟢 चालू' : '🔴 बंद' }}
                </button>

                <button
                  type="button"
                  class="dukandar-btn-plus10"
                  @click.stop="quickRestockVariant(getActiveVariant(prod), 10)"
                  title="+10 Stock"
                >
                  +10
                </button>
              </div>
            </div>

            <!-- Unit Variant Selector & Loose Custom Weight Option -->
            <div class="variants-wrap" v-if="prod.variants && prod.variants.length > 0">
              <div class="variant-label-title">{{ t('weight_select_label') }}</div>
              <div class="variant-options">
                <button
                  v-for="v in prod.variants"
                  :key="v.id"
                  class="variant-chip"
                  :class="{ selected: selectedVariants[prod.id] === v.id && !customWeightMode[prod.id] }"
                  @click="selectVariant(prod.id, v.id)"
                >
                  {{ v.unit_size }}
                </button>
                <!-- Custom Weight Option for Loose Items (Chakki Atta, Dals, Rice, Maida, Besan, Oils) -->
                <button
                  v-if="isLooseProduct(prod)"
                  class="variant-chip custom-chip"
                  :class="{ selected: customWeightMode[prod.id] }"
                  @click="enableCustomWeight(prod)"
                >
                  ⚖️ {{ t('custom_weight_btn') }}
                </button>
              </div>
            </div>

            <!-- MODE A: CUSTOM WEIGHT ENTRY FOR LOOSE COMMODITIES -->
            <div v-if="customWeightMode[prod.id]" class="custom-weight-box">
              <div class="custom-weight-header">
                <span>⚖️ {{ t('enter_custom_weight') }}</span>
                <span class="custom-rate-badge">{{ t('per_kg_rate') }}: ₹{{ getEffectivePerKgRate(prod, customWeightInputs[prod.id]) }}/kg</span>
              </div>
              <div v-if="getMatchingTierInfo(prod, customWeightInputs[prod.id])" style="background: #ecfdf5; border: 1px solid #6ee7b7; border-radius: 6px; padding: 4px 8px; font-size: 0.78rem; color: #064e3b; font-weight: 700; margin-bottom: 6px;">
                🎉 {{ getMatchingTierInfo(prod, customWeightInputs[prod.id]).tier_label }} लागू झाला: ₹{{ getEffectivePerKgRate(prod, customWeightInputs[prod.id]) }}/kg!
              </div>
              <div class="custom-input-group">
                <button
                  type="button"
                  class="weight-stepper-btn"
                  @click="adjustCustomWeight(prod.id, -0.5)"
                  title="- 0.5 kg"
                >
                  -0.5
                </button>
                <input
                  type="number"
                  step="0.25"
                  min="0.25"
                  max="100"
                  v-model.number="customWeightInputs[prod.id]"
                  class="custom-weight-input"
                  placeholder="उदा: 4.5, 2, 1.75"
                />
                <span class="custom-unit-label">kg</span>
                <button
                  type="button"
                  class="weight-stepper-btn"
                  @click="adjustCustomWeight(prod.id, 0.5)"
                  title="+ 0.5 kg"
                >
                  +0.5
                </button>
                <button
                  type="button"
                  class="weight-stepper-btn"
                  @click="adjustCustomWeight(prod.id, 1.0)"
                  title="+ 1.0 kg"
                >
                  +1.0
                </button>
              </div>
              <div class="quick-weights">
                <span class="quick-chip" @click="setQuickCustomWeight(prod.id, 1.5)">1.5kg</span>
                <span class="quick-chip" @click="setQuickCustomWeight(prod.id, 2.5)">2.5kg</span>
                <span class="quick-chip" @click="setQuickCustomWeight(prod.id, 5)">5kg (होलसेल)</span>
                <span class="quick-chip" @click="setQuickCustomWeight(prod.id, 10)">10kg</span>
                <span class="quick-chip" @click="setQuickCustomWeight(prod.id, 25)">25kg (बोरी)</span>
              </div>
              <div class="custom-price-calc">
                <span>{{ t('custom_total_label') }} (₹{{ getEffectivePerKgRate(prod, customWeightInputs[prod.id]) }}/kg × {{ customWeightInputs[prod.id] || 0 }}):</span>
                <strong class="custom-total-val">₹{{ getCustomWeightPrice(prod) }}</strong>
              </div>
              <button
                class="add-to-cart-btn custom-add-btn"
                @click="addCustomWeightItemToCart(prod)"
                :disabled="!customWeightInputs[prod.id] || customWeightInputs[prod.id] <= 0"
              >
                🛒 {{ customWeightInputs[prod.id] || 0 }} kg {{ t('add_custom_btn') }}
              </button>
            </div>

            <!-- MODE B: STANDARD PACKET / FIXED VARIANT DISPLAY -->
            <template v-else>
              <!-- Price Row (Authentic Kirana MRP / Authentic Clearance Markdown) -->
              <div class="price-row" v-if="getActiveVariant(prod)">
                <template v-if="adminAllowClearancePublic && getActiveVariant(prod).is_clearance && getActiveVariant(prod).clearance_price">
                  <span class="selling-price" style="color: #dc2626; font-weight: 900;">₹{{ getActiveVariant(prod).clearance_price }}</span>
                  <span style="font-size: 0.82rem; text-decoration: line-through; color: #94a3b8; margin-left: 6px;">₹{{ getActiveVariant(prod).mrp }}</span>
                  <span style="font-size: 0.72rem; font-weight: 800; background: #fee2e2; color: #b91c1c; padding: 2px 6px; border-radius: 4px; margin-left: 6px;">
                    💥 {{ currentLang === 'en' ? 'Special Offer' : (currentLang === 'mr' ? 'विशेष सवलत' : 'विशेष छूट') }}
                  </span>
                </template>
                <template v-else>
                  <span class="selling-price">₹{{ getActiveVariant(prod).selling_price }}</span>
                </template>
              </div>

              <!-- Add to Cart or Quantity Controls -->
              <div v-if="getActiveVariant(prod)">
                <div v-if="!getActiveVariant(prod).is_available" class="out-of-stock-action-wrap">
                  <button class="add-to-cart-btn btn-out-of-stock" disabled>
                    🚫 {{ t('out_of_stock') }}
                  </button>
                  <button
                    type="button"
                    class="btn-notify-me"
                    @click.stop="openNotifyModal(prod, getActiveVariant(prod))"
                    style="margin-top: 6px; width: 100%; background: #ecfdf5; border: 1.5px solid #059669; color: #065f46; font-weight: 700; font-size: 0.82rem; padding: 7px 10px; border-radius: 8px; cursor: pointer; display: flex; align-items: center; justify-content: center; gap: 6px; transition: all 0.2s ease;"
                  >
                    {{ t('notify_me_btn') }}
                  </button>
                </div>
                <div v-else-if="getCartItemQuantity(prod.id, getActiveVariant(prod).id) === 0">
                  <button
                    class="add-to-cart-btn"
                    @click="addToCart(prod, getActiveVariant(prod))"
                  >
                    + {{ t('add_to_cart') }}
                  </button>
                </div>
                <div v-else class="qty-control-row">
                  <button
                    class="qty-btn"
                    @click="decreaseQuantity(getActiveVariant(prod).id)"
                  >
                    -
                  </button>
                  <span class="qty-display">
                    {{ getCartItemQuantity(prod.id, getActiveVariant(prod).id) }}
                  </span>
                  <button
                    class="qty-btn"
                    @click="increaseQuantity(getActiveVariant(prod).id)"
                  >
                    +
                  </button>
                </div>
              </div>
            </template>
          </div>
        </div>
      </div>

      <!-- Footer with Authentic Store Details, GST, FSSAI & Contact Details -->
      <footer style="margin-top: 60px; padding: 32px 20px 24px 20px; border-top: 1.5px solid var(--border); background: #fdfbf7; color: var(--text-subtle); font-size: 0.88rem;">
        <div style="max-width: 900px; margin: 0 auto; text-align: center;">
          <h4 style="font-size: 1.15rem; font-weight: 900; color: #064e3b; margin: 0 0 6px 0;">
            🌾 Komal Enterprises / Komal Mart
          </h4>
          <p style="margin: 0 0 8px 0; color: #334155; font-size: 0.84rem; line-height: 1.5;">
            📍 <strong>Address:</strong> 1st Floor, GRD 6, Vitthal Rukhmai CHS, B.B. Khandekar Marg, Nr. Ram Mandir, Wadala (W), Mumbai - 400031
          </p>

          <div style="display: flex; justify-content: center; flex-wrap: wrap; gap: 14px; margin: 10px 0; font-size: 0.82rem; color: #1e293b;">
            <span style="background: white; border: 1px solid #cbd5e1; padding: 4px 10px; border-radius: 6px;">
              🏛️ <strong>GSTIN:</strong> 27ACOPU3896J1ZK
            </span>
            <span style="background: white; border: 1px solid #cbd5e1; padding: 4px 10px; border-radius: 6px;">
              🛡️ <strong>FSSAI NO:</strong> 11521003000327
            </span>
            <span style="background: white; border: 1px solid #cbd5e1; padding: 4px 10px; border-radius: 6px;">
              ✉️ <strong>Email:</strong> binkteshsingh0820@gmail.com
            </span>
          </div>

          <div style="display: flex; justify-content: center; flex-wrap: wrap; gap: 12px; margin: 12px 0; font-size: 0.84rem;">
            <span>📞 <strong>Binktesh Kumar (Shop Owner):</strong> <a href="tel:9987602693" style="color: #059669; font-weight: 700; text-decoration: none;">9987602693</a></span>
            <span>•</span>
            <span>📞 <strong>Binktesh Kumar (Shop Owner):</strong> <a href="tel:8369795519" style="color: #059669; font-weight: 700; text-decoration: none;">8369795519</a></span>
            <span>•</span>
            <span>📞 <strong>Hareram Kumar:</strong> <a href="tel:7045311406" style="color: #059669; font-weight: 700; text-decoration: none;">7045311406</a></span>
            <span>•</span>
            <span>📲 <strong>WhatsApp Helpline:</strong> <a href="https://wa.me/919142052967" target="_blank" style="color: #16a34a; font-weight: 700; text-decoration: none;">91420-52967</a></span>
          </div>

          <p style="margin-top: 14px; font-size: 0.8rem; color: #94a3b8;">
            Komal Mart • Pure Kirana, Fresh Chakki Atta, Dals, Spices & Grains • Hyperlocal doorstep delivery across Wadala, Dadar, Matunga, Sewri & Sion.
          </p>

          <p style="margin-top: 10px;">
            <a href="javascript:void(0)" @click="openAuthModal('admin')" style="color: #d97706; font-weight: 700; text-decoration: none; font-size: 0.82rem;">
              🔐 Store Owner / Admin Portal Access
            </a>
          </p>
        </div>
      </footer>
    </main>

    <!-- ======================================================== -->
    <!-- VIEW 2: DUKANDAR / STORE OWNER ADMIN DASHBOARD           -->
    <!-- ======================================================== -->
    <section class="main-layout" v-if="isAdminLoggedIn && adminActiveTab !== 'storefront'">
      <div class="admin-dashboard-card">
        <div id="admin-tab-content-anchor"></div>
        <div class="admin-top-bar">
          <div class="admin-title-wrap">
            <h2 style="font-size: 1.35rem; font-weight: 900; color: #0f172a; display: flex; align-items: center; gap: 8px; margin: 0;">
              🏪 {{ t('admin_panel_title') }}
            </h2>
            <p style="color: var(--text-muted); font-size: 0.82rem; margin: 2px 0 0;" class="desktop-only">
              {{ t('admin_panel_desc') }}
            </p>
          </div>
          <div class="admin-header-actions">
            <button
              @click="showAddProductModal = true; addProductMode = 'quick';"
              class="admin-action-chip admin-chip-primary"
            >
              ➕ {{ t('admin_add_product') }}
            </button>
            <button
              @click="showBatchIngestModal = true"
              class="admin-action-chip admin-chip-amber"
              title="Zero-token automated inventory import from camera/phone photos"
            >
              ⚡ {{ currentLang === 'en' ? 'Batch Photos' : (currentLang === 'mr' ? 'बॅच फोटो' : 'बैच फोटो') }}
            </button>
            <button
              @click="downloadDatabaseBackup"
              class="admin-action-chip admin-chip-blue"
              title="Download crash-safe hot SQLite WAL database snapshot (.db.gz)"
            >
              💾 {{ currentLang === 'en' ? 'Backup' : (currentLang === 'mr' ? 'बॅकअप' : 'बैकअप') }}
            </button>
            <button
              @click="confirmResetSeed"
              class="admin-action-chip admin-chip-red desktop-only"
              title="Reset to default authentic Indian Kirana catalog"
            >
              🔄 {{ currentLang === 'en' ? 'Reset' : (currentLang === 'mr' ? 'रीसेट' : 'रीसेट') }}
            </button>
          </div>
        </div>

        <!-- COMPACT MOBILE KPI METRIC STRIP (Height: 38px instead of 180px!) -->
        <div class="admin-mobile-kpi-bar">
          <div class="kpi-mini-pill" @click="switchAdminTab('inventory')">
            <span class="kpi-mini-icon">📦</span>
            <div class="kpi-mini-data">
              <span class="kpi-mini-val">{{ products.length }}</span>
              <span class="kpi-mini-lbl">{{ currentLang === 'mr' ? 'सामान' : 'Items' }}</span>
            </div>
          </div>
          <div class="kpi-mini-pill" @click="switchAdminTab('orders')">
            <span class="kpi-mini-icon">🧾</span>
            <div class="kpi-mini-data">
              <span class="kpi-mini-val">{{ isAdminOrdersLoading ? '...' : adminOrders.length }}</span>
              <span class="kpi-mini-lbl">{{ currentLang === 'mr' ? 'ऑर्डर्स' : 'Orders' }}</span>
            </div>
          </div>
          <div class="kpi-mini-pill kpi-mini-danger" @click="switchAdminTab('khata')">
            <span class="kpi-mini-icon">🔴</span>
            <div class="kpi-mini-data">
              <span class="kpi-mini-val">{{ isAdminOrdersLoading ? '...' : unpaidAdminOrders.length }}</span>
              <span class="kpi-mini-lbl">{{ currentLang === 'mr' ? 'बाकी' : 'Khata' }}</span>
            </div>
          </div>
          <div class="kpi-mini-pill kpi-mini-success" @click="switchAdminTab('orders')">
            <span class="kpi-mini-icon">🟢</span>
            <div class="kpi-mini-data">
              <span class="kpi-mini-val">{{ isAdminOrdersLoading ? '...' : paidAdminOrders.length }}</span>
              <span class="kpi-mini-lbl">{{ currentLang === 'mr' ? 'चुकता' : 'Paid' }}</span>
            </div>
          </div>
          <button
            type="button"
            class="kpi-mini-expand-btn"
            @click="showMobileExpandedStats = !showMobileExpandedStats"
            :title="showMobileExpandedStats ? 'Hide full stats' : 'Show full stats'"
          >
            {{ showMobileExpandedStats ? '▲' : '▼' }}
          </button>
        </div>

        <!-- Store Overview KPI Cards (Desktop always, Mobile when expanded) -->
        <div class="admin-stats-grid" :class="{ 'mobile-stats-hidden': !showMobileExpandedStats }">
          <div class="stat-card">
            <div class="stat-icon">📦</div>
            <div class="stat-content">
              <span class="stat-label">{{ currentLang === 'mr' ? 'एकूण सामान' : (currentLang === 'hi' ? 'कुल सामान' : 'Total Products') }}</span>
              <strong class="stat-val">{{ products.length }}</strong>
            </div>
          </div>
          <div class="stat-card">
            <div class="stat-icon">🧾</div>
            <div class="stat-content">
              <span class="stat-label">{{ currentLang === 'mr' ? 'एकूण ऑर्डर्स' : (currentLang === 'hi' ? 'कुल ऑर्डर' : 'Total Orders') }}</span>
              <strong class="stat-val">{{ isAdminOrdersLoading ? '⏳' : adminOrders.length }}</strong>
            </div>
          </div>
          <div class="stat-card stat-card-danger">
            <div class="stat-icon">🔴</div>
            <div class="stat-content">
              <span class="stat-label">{{ currentLang === 'mr' ? 'बाकी उधारी' : (currentLang === 'hi' ? 'बाकी उधारी' : 'Unpaid Khata') }}</span>
              <strong class="stat-val">{{ isAdminOrdersLoading ? '⏳' : unpaidAdminOrders.length }}</strong>
            </div>
          </div>
          <div class="stat-card stat-card-success">
            <div class="stat-icon">🟢</div>
            <div class="stat-content">
              <span class="stat-label">{{ currentLang === 'mr' ? 'चुकता ऑर्डर्स' : (currentLang === 'hi' ? 'चुकता ऑर्डर' : 'Paid Orders') }}</span>
              <strong class="stat-val">{{ isAdminOrdersLoading ? '⏳' : paidAdminOrders.length }}</strong>
            </div>
          </div>
          <div class="stat-card" style="border-left: 4px solid #8b5cf6; cursor: pointer;" @click="fetchAiMetrics" title="Click to refresh 24h AI Scans & Quota telemetry">
            <div class="stat-icon">⚡</div>
            <div class="stat-content">
              <span class="stat-label">AI Scans (24h)</span>
              <strong class="stat-val" style="color: #6d28d9; font-size: 1.05rem;">
                {{ aiTelemetry.summary_24h.total_requests }} reqs
                <span style="font-size: 0.72rem; color: #64748b; font-weight: normal;">
                  (📷 {{ aiTelemetry.summary_24h.photo_scans }} | 🎙️ {{ aiTelemetry.summary_24h.voice_scans }} | {{ aiTelemetry.summary_24h.avg_latency_ms }}ms)
                </span>
              </strong>
            </div>
          </div>
        </div>

        <!-- Modern Admin Sub-Navigation Tabs -->
        <div class="admin-nav-tabs">
          <button
            class="admin-nav-tab-btn"
            :class="{ active: adminActiveTab === 'storefront' }"
            @click="switchAdminTab('storefront')"
            style="background: #ecfdf5; border-color: #6ee7b7; color: #064e3b; font-weight: 800;"
          >
            🏪 {{ currentLang === 'mr' ? 'दुकानदार व्ह्यू' : (currentLang === 'hi' ? 'दुकानदार दृश्य' : 'Storefront') }}
          </button>
          <button
            class="admin-nav-tab-btn"
            :class="{ active: adminActiveTab === 'inventory' }"
            @click="switchAdminTab('inventory')"
          >
            📋 {{ t('admin_tab_inventory') }}
          </button>
          <button
            class="admin-nav-tab-btn"
            :class="{ active: adminActiveTab === 'pos' }"
            @click="switchAdminTab('pos')"
          >
            {{ t('admin_tab_pos') }}
          </button>
          <button
            class="admin-nav-tab-btn"
            :class="{ active: adminActiveTab === 'orders' }"
            @click="switchAdminTab('orders')"
          >
            🧾 {{ t('admin_tab_orders') }}
            <span v-if="unpaidAdminOrders.length > 0" class="tab-badge-danger" style="margin-left: 4px;">
              {{ unpaidAdminOrders.length }}
            </span>
          </button>
          <button
            class="admin-nav-tab-btn"
            :class="{ active: adminActiveTab === 'customers' }"
            @click="switchAdminTab('customers')"
          >
            {{ t('admin_tab_customers') }}
            <span v-if="khataCustomersCount > 0" class="tab-badge-warning" style="margin-left: 4px;">
              {{ khataCustomersCount }}
            </span>
          </button>
          <button
            class="admin-nav-tab-btn"
            :class="{ active: adminActiveTab === 'khata' }"
            @click="switchAdminTab('khata')"
          >
            {{ t('admin_tab_khata') }}
            <span v-if="adminKhataSummary.total_market_udhaar > 0" class="tab-badge-danger" style="margin-left: 4px;">
              ₹{{ adminKhataSummary.total_market_udhaar }}
            </span>
          </button>
          <button
            class="admin-nav-tab-btn"
            :class="{ active: adminActiveTab === 'zreport' }"
            @click="switchAdminTab('zreport')"
          >
            {{ t('admin_tab_zreport') }}
          </button>
          <button
            class="admin-nav-tab-btn"
            :class="{ active: adminActiveTab === 'restock' }"
            @click="switchAdminTab('restock')"
          >
            {{ t('admin_tab_restock') }}
            <span v-if="pendingRestockCount > 0" class="tab-badge-warning" style="margin-left: 4px;">
              {{ pendingRestockCount }}
            </span>
          </button>
          <button
            class="admin-nav-tab-btn"
            :class="{ active: adminActiveTab === 'support' }"
            @click="switchAdminTab('support')"
          >
            {{ t('admin_tab_support') }}
            <span v-if="adminOpenComplaintsCount > 0" class="tab-badge-danger" style="margin-left: 4px;">
              {{ adminOpenComplaintsCount }}
            </span>
          </button>
          <button
            class="admin-nav-tab-btn"
            :class="{ active: adminActiveTab === 'zones' }"
            @click="switchAdminTab('zones')"
          >
            🛵 {{ currentLang === 'en' ? 'Delivery Zones' : (currentLang === 'mr' ? 'डिलिव्हरी परिसर' : 'डिलीवरी क्षेत्र') }}
            <span v-if="Object.values(areaDeliveryHolds).filter(h => h.is_held).length > 0" class="tab-badge-warning" style="margin-left: 4px;">
              {{ Object.values(areaDeliveryHolds).filter(h => h.is_held).length }} Hold
            </span>
          </button>
        </div>

        <!-- TAB 1: INVENTORY & QUICK PRICE CHANGER -->
        <div v-if="adminActiveTab === 'inventory'">
          <!-- MODERN RESPONSIVE INVENTORY TOOLBAR -->
          <div class="admin-inv-toolbar">
            <div class="admin-inv-search-box">
              <span class="admin-inv-search-icon">🔍</span>
              <input
                type="text"
                v-model="adminSearch"
                :placeholder="currentLang === 'en' ? 'Search & filter items...' : (currentLang === 'mr' ? 'सामान शोधा / फिल्टर...' : 'सामान खोजें / फिल्टर...')"
                class="admin-inv-search-input"
              />
              <button
                v-if="adminSearch"
                type="button"
                class="admin-inv-search-clear"
                @click="adminSearch = ''"
                title="Clear search"
              >✕</button>
            </div>

            <div class="admin-inv-actions-cluster">
              <button
                v-if="selectedAdminProductIds.length > 0"
                @click="bulkDeleteSelectedProducts"
                class="admin-bulk-delete-btn"
                title="Delete selected products"
              >
                🗑️ {{ selectedAdminProductIds.length }}
              </button>

              <!-- Master Clearance Public Toggle Pill -->
              <label class="admin-inv-pill-toggle admin-pill-sale" title="Toggle whether customers see clearance deals on the storefront">
                <input
                  type="checkbox"
                  :checked="adminAllowClearancePublic"
                  @change="e => togglePublicClearance(e.target.checked)"
                />
                <span>🏷️ {{ currentLang === 'en' ? 'Public Sale' : (currentLang === 'mr' ? 'ग्राहकांना सेल' : 'ग्राहकों को सेल') }}</span>
              </label>

              <!-- Select All Toggle Pill -->
              <label class="admin-inv-pill-toggle admin-pill-select-all" title="Select / Deselect all products">
                <input
                  type="checkbox"
                  :checked="filteredAdminProducts.length > 0 && selectedAdminProductIds.length === filteredAdminProducts.length"
                  @change="toggleSelectAllProducts"
                />
                <span>{{ currentLang === 'en' ? 'All' : (currentLang === 'mr' ? 'सर्व' : 'सभी') }}</span>
              </label>

              <span class="admin-inv-count-badge">
                <strong>{{ filteredAdminProducts.length }}</strong>
              </span>
            </div>
          </div>

          <!-- Admin Category Filter Pills -->
          <div class="admin-cat-filter-scroll">
            <button
              type="button"
              class="admin-cat-pill"
              :class="{ active: adminCategoryFilter === '' }"
              @click="adminCategoryFilter = ''"
            >
              🌟 {{ currentLang === 'en' ? 'All' : (currentLang === 'mr' ? 'सर्व' : 'सभी') }} ({{ products.length }})
            </button>
            <button
              v-for="cat in categories"
              :key="'admin-cat-' + cat.id"
              type="button"
              class="admin-cat-pill"
              :class="{ active: adminCategoryFilter === cat.id }"
              @click="adminCategoryFilter = (adminCategoryFilter === cat.id ? '' : cat.id)"
            >
              {{ currentLang === 'mr' ? (cat.name_hi || cat.name) : cat.name }} ({{ products.filter(p => p.category_id === cat.id).length }})
            </button>
          </div>

          <!-- DESKTOP DATA TABLE -->
          <div class="admin-table-wrap desktop-table-view">
            <table class="admin-table">
              <thead>
                <tr>
                  <th style="width: 36px; text-align: center;">
                    <input
                      type="checkbox"
                      :checked="filteredAdminProducts.length > 0 && selectedAdminProductIds.length === filteredAdminProducts.length"
                      @change="toggleSelectAllProducts"
                      style="width: 16px; height: 16px; accent-color: #ef4444; cursor: pointer;"
                      title="Select all products"
                    />
                  </th>
                  <th style="width: 56px; text-align: center;">{{ currentLang === 'mr' ? 'फोटो' : (currentLang === 'hi' ? 'फोटो' : 'Photo') }}</th>
                  <th>{{ currentLang === 'mr' ? 'सामान' : (currentLang === 'hi' ? 'सामान' : 'Product') }}</th>
                  <th>{{ currentLang === 'mr' ? 'प्रकार' : (currentLang === 'hi' ? 'प्रकार' : 'Type') }}</th>
                  <th>{{ currentLang === 'mr' ? 'ब्रँड' : (currentLang === 'hi' ? 'ब्रांड' : 'Brand') }}</th>
                  <th>{{ currentLang === 'mr' ? 'वजन/युनिट' : (currentLang === 'hi' ? 'वजन/यूनिट' : 'Size') }}</th>
                  <th>MRP (₹)</th>
                  <th>{{ currentLang === 'mr' ? 'दुकान दर (₹)' : (currentLang === 'hi' ? 'दुकान दर (₹)' : 'Rate (₹)') }}</th>
                  <th>{{ currentLang === 'mr' ? '🔥 क्लिअरन्स सेल' : (currentLang === 'hi' ? '🔥 क्लीयरेंस सेल' : '🔥 Clearance') }}</th>
                  <th>{{ currentLang === 'mr' ? 'स्टॉक संख्या' : (currentLang === 'hi' ? 'स्टॉक संख्या' : 'Stock Qty') }}</th>
                  <th>{{ t('stock_status_header') }}</th>
                  <th>{{ currentLang === 'mr' ? 'कृती (Action)' : (currentLang === 'hi' ? 'कार्रवाई' : 'Action') }}</th>
                </tr>
              </thead>
              <tbody>
                <template v-for="prod in filteredAdminProducts" :key="prod.id">
                  <tr v-for="(v, vIdx) in prod.variants" :key="v.id">
                    <td v-if="vIdx === 0" :rowspan="prod.variants.length" style="text-align: center; vertical-align: middle;">
                      <input
                        type="checkbox"
                        :checked="selectedAdminProductIds.includes(prod.id)"
                        @change="toggleProductSelection(prod.id)"
                        style="width: 17px; height: 17px; accent-color: #ef4444; cursor: pointer;"
                      />
                    </td>
                    <td v-if="vIdx === 0" :rowspan="prod.variants.length" style="text-align: center; vertical-align: middle; width: 56px;">
                      <div class="admin-prod-thumb-wrap" @click="openEditPhotosModal(prod)" title="Click to view/edit photo">
                        <img
                          :src="prod.image_url || '/products/chakki-atta.jpg'"
                          :alt="prod.name"
                          class="admin-prod-thumb"
                          loading="lazy"
                          @error="handleImageFallback($event)"
                        />
                      </div>
                    </td>
                    <td>
                      <strong>{{ prod.name }}</strong>
                      <div style="font-size: 0.8rem; color: #c2410c; font-family: var(--font-hindi);">
                        {{ prod.name_hi }}
                      </div>
                    </td>
                    <td>
                      <span v-if="prod.is_loose" style="background: #fffbeb; color: #b45309; padding: 2px 7px; border-radius: 4px; font-size: 0.76rem; font-weight: 800;">
                        {{ currentLang === 'en' ? 'Loose' : 'खुला' }}
                      </span>
                      <span v-else style="background: #eff6ff; color: #1d4ed8; padding: 2px 7px; border-radius: 4px; font-size: 0.76rem; font-weight: 800;">
                        {{ currentLang === 'en' ? 'Packed' : 'पैकेट' }}
                      </span>
                    </td>
                    <td style="font-size: 0.84rem; color: var(--text-muted);">{{ prod.brand }}</td>
                    <td style="font-weight: 700;">{{ v.unit_size }}</td>
                    <td>
                      <input
                        type="number"
                        v-model.number="v.mrp"
                        class="admin-inline-input"
                      />
                    </td>
                    <td>
                      <input
                        type="number"
                        v-model.number="v.selling_price"
                        class="admin-inline-input"
                        style="color: #047857; font-weight: 800;"
                      />
                    </td>
                    <td>
                      <div style="display: flex; flex-direction: column; gap: 4px;">
                        <label style="display: inline-flex; align-items: center; gap: 4px; font-size: 0.74rem; font-weight: 800; color: #dc2626; cursor: pointer;">
                          <input type="checkbox" v-model="v.is_clearance" style="accent-color: #dc2626;" />
                          <span>{{ currentLang === 'en' ? 'Active' : 'सेल चालू' }}</span>
                        </label>
                        <input
                          v-if="v.is_clearance"
                          type="number"
                          v-model.number="v.clearance_price"
                          placeholder="सेल दर"
                          class="admin-inline-input"
                          style="width: 70px; color: #dc2626; font-weight: 800; border-color: #fca5a5; background: #fff5f5;"
                          title="क्लिअरन्स सेल दर (Clearance Sale Price)"
                        />
                      </div>
                    </td>
                    <td>
                      <div class="admin-stock-cell">
                        <input
                          type="number"
                          v-model.number="v.stock_quantity"
                          class="admin-inline-input"
                          style="width: 65px;"
                        />
                        <button
                          type="button"
                          class="admin-quick-add-pill"
                          @click="quickRestockVariant(v, 10)"
                          title="1-Tap +10 Restock"
                        >
                          +10
                        </button>
                        <span v-if="v.stock_quantity <= 5" class="low-stock-alert" :title="t('low_stock_pill')">
                          ⚠️ {{ t('low_stock_pill') }} ({{ v.stock_quantity }})
                        </span>
                      </div>
                    </td>
                    <td>
                      <button
                        type="button"
                        class="stock-toggle-pill"
                        :class="(v.is_in_stock !== false && v.is_available) ? 'stock-in' : 'stock-out'"
                        @click="toggleVariantStock(v)"
                        :title="currentLang === 'en' ? 'Click to toggle stock status' : ((v.is_in_stock !== false && v.is_available) ? 'क्लिक करून आउट-ऑफ-स्टॉक करा' : 'क्लिक करून इन-स्टॉक करा')"
                      >
                        <span class="stock-dot"></span>
                        {{ (v.is_in_stock !== false && v.is_available) ? t('in_stock_btn') : t('out_of_stock_btn') }}
                      </button>
                    </td>
                    <td>
                      <div style="display: flex; gap: 6px; align-items: center;">
                        <button
                          type="button"
                          class="save-chip-btn photo-edit-btn"
                          style="background: #e0f2fe; color: #0369a1; border-color: #bae6fd;"
                          @click="openEditPhotosModal(prod)"
                          :title="currentLang === 'en' ? 'Change / Add 3-angle photos' : 'सामान के 3-अँगल फोटो बदलें / जोड़ें'"
                        >
                          📸 {{ currentLang === 'en' ? 'Photos' : 'फोटो' }} ({{ prod.images ? prod.images.length : 1 }})
                        </button>
                        <button
                          class="save-chip-btn"
                          @click="saveVariantPrice(v)"
                          :title="currentLang === 'en' ? 'Save changed price to SQLite' : 'बदलेली किंमत सेव्ह करा'"
                        >
                          💾 {{ currentLang === 'en' ? 'Save' : (currentLang === 'mr' ? 'सेव्ह करा' : 'सेव करें') }}
                        </button>
                        <button
                          class="delete-product-btn"
                          @click="deleteAdminProduct(prod.id, prod.name)"
                          :title="currentLang === 'en' ? 'Delete this item from store' : 'इस सामान को दुकान से हटाएं'"
                        >
                          🗑️
                        </button>
                      </div>
                    </td>
                  </tr>
                </template>
              </tbody>
            </table>
          </div>

          <!-- MOBILE NATIVE INVENTORY CARD LIST (PHONE FRIENDLY) -->
          <div class="admin-mobile-inventory-list">
            <div v-for="prod in filteredAdminProducts" :key="'mob-' + prod.id" class="admin-mob-item-card">
              <div class="admin-mob-card-head">
                <div style="display: flex; align-items: center; gap: 10px; min-width: 0; flex: 1;">
                  <input
                    type="checkbox"
                    :checked="selectedAdminProductIds.includes(prod.id)"
                    @change="toggleProductSelection(prod.id)"
                    style="width: 18px; height: 18px; accent-color: #ef4444; cursor: pointer; flex-shrink: 0;"
                  />
                  <div class="admin-mob-thumb-box" @click="openEditPhotosModal(prod)" title="Click to view/edit photos">
                    <img
                      :src="prod.image_url || '/products/chakki-atta.jpg'"
                      :alt="prod.name"
                      class="admin-mob-thumb-img"
                      loading="lazy"
                      @error="handleImageFallback($event)"
                    />
                  </div>
                  <div style="min-width: 0; flex: 1;">
                    <div class="admin-mob-name">{{ prod.name }}</div>
                    <div class="admin-mob-sub">
                      <span class="admin-mob-hi">{{ prod.name_hi }}</span>
                      <span v-if="prod.brand" class="admin-mob-brand">• {{ prod.brand }}</span>
                    </div>
                  </div>
                </div>
                <div class="admin-mob-head-actions">
                  <span :class="prod.is_loose ? 'mob-tag-loose' : 'mob-tag-packed'">
                    {{ prod.is_loose ? (currentLang === 'en' ? 'Loose' : 'खुला') : (currentLang === 'en' ? 'Packed' : 'पॅकेट') }}
                  </span>
                  <button
                    type="button"
                    class="photo-edit-btn-mini"
                    @click="openEditPhotosModal(prod)"
                    title="Photos"
                  >
                    📸
                  </button>
                  <button
                    class="delete-product-btn-mini"
                    @click="deleteAdminProduct(prod.id, prod.name)"
                    title="Delete item"
                  >
                    🗑️
                  </button>
                </div>
              </div>

              <!-- Product Variants on Mobile (Ultra-Compact Dukandar Card) -->
              <div class="admin-mob-variant-list">
                <div v-for="v in prod.variants" :key="'mob-v-' + v.id" class="admin-mob-variant-compact">
                  <!-- Row 1: Unit Size, Stock Pill, Low Stock, Restock Chips & Clearance -->
                  <div class="mob-v-top-row">
                    <div class="mob-v-badge-group">
                      <span class="mob-v-unit-badge">{{ v.unit_size }}</span>
                      <button
                        type="button"
                        class="stock-toggle-pill-compact"
                        :class="(v.is_in_stock !== false && v.is_available) ? 'stock-in' : 'stock-out'"
                        @click="toggleVariantStock(v)"
                        :title="(v.is_in_stock !== false && v.is_available) ? t('in_stock_btn') : t('out_of_stock_btn')"
                      >
                        <span class="stock-dot"></span>
                        {{ (v.is_in_stock !== false && v.is_available) ? t('in_stock_btn') : t('out_of_stock_btn') }}
                      </button>
                      <span v-if="v.stock_quantity <= 5" class="mob-v-low-stock-badge" :title="t('low_stock_pill')">
                        ⚠️ {{ v.stock_quantity }}
                      </span>
                    </div>

                    <div class="mob-v-meta-actions">
                      <label class="mob-v-sale-toggle" :class="{ active: v.is_clearance }" title="Toggle clearance discount">
                        <input type="checkbox" v-model="v.is_clearance" />
                        <span>🏷️ सेल</span>
                      </label>
                      <button
                        type="button"
                        class="mob-restock-btn"
                        @click="quickRestockVariant(v, 10)"
                        title="Add +10 stock"
                      >+10</button>
                      <button
                        type="button"
                        class="mob-restock-btn"
                        @click="quickRestockVariant(v, 50)"
                        title="Add +50 stock"
                      >+50</button>
                    </div>
                  </div>

                  <!-- Row 2: MRP, Rate (Emerald), Stock, Sale Price (if active), 1-Tap Save -->
                  <div class="mob-v-inputs-strip">
                    <div class="mob-input-col">
                      <label class="mob-input-lbl">MRP</label>
                      <div class="mob-input-field">
                        <span class="currency">₹</span>
                        <input type="number" v-model.number="v.mrp" class="mob-raw-input" />
                      </div>
                    </div>

                    <div class="mob-input-col rate-col">
                      <label class="mob-input-lbl rate-lbl">Rate</label>
                      <div class="mob-input-field rate-field">
                        <span class="currency">₹</span>
                        <input type="number" v-model.number="v.selling_price" class="mob-raw-input rate-input" />
                      </div>
                    </div>

                    <div class="mob-input-col">
                      <label class="mob-input-lbl">Stock</label>
                      <div class="mob-input-field">
                        <input type="number" v-model.number="v.stock_quantity" class="mob-raw-input" />
                      </div>
                    </div>

                    <div v-if="v.is_clearance" class="mob-input-col sale-col">
                      <label class="mob-input-lbl sale-lbl">सेल दर</label>
                      <div class="mob-input-field sale-field">
                        <span class="currency">₹</span>
                        <input type="number" v-model.number="v.clearance_price" placeholder="दर" class="mob-raw-input sale-input" />
                      </div>
                    </div>

                    <button
                      type="button"
                      class="mob-save-action-btn"
                      @click="saveVariantPrice(v)"
                      title="Save price to database"
                    >
                      💾
                    </button>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <!-- Dukandar Mobile Floating Action Button (1-Tap Add Item) -->
          <button
            type="button"
            class="admin-mobile-fab"
            @click="showAddProductModal = true; addProductMode = 'quick';"
            title="सामान जोडा"
          >
            <span class="admin-fab-icon">➕</span>
            <span class="admin-fab-text">{{ currentLang === 'mr' ? 'सामान जोडा' : (currentLang === 'hi' ? 'सामान जोड़ें' : 'Add Item') }}</span>
          </button>
        </div>

        <!-- TAB 2: COUNTER BILLING (POS & PHONE ORDER CREATOR) -->
        <div v-if="adminActiveTab === 'pos'" style="margin-top: 14px;">
          <div class="pos-container">
            <!-- Left Column: Customer & Item Builder -->
            <div class="pos-card">
              <div class="pos-card-title" style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 8px;">
                <span>⚡ {{ currentLang === 'en' ? 'New Counter Bill (POS)' : (currentLang === 'mr' ? 'नवीन काउंटर बिल (POS)' : 'नया काउंटर बिल (POS)') }}</span>
                <button
                  type="button"
                  @click="posCustomerDetailsOpen = !posCustomerDetailsOpen"
                  style="background: #eff6ff; color: #1d4ed8; border: 1.5px solid #bfdbfe; font-size: 0.78rem; font-weight: 800; padding: 4px 10px; border-radius: 8px; cursor: pointer; display: inline-flex; align-items: center; gap: 4px;"
                >
                  {{ posCustomerDetailsOpen ? '▲ ' + (currentLang === 'en' ? 'Minimize Customer Info' : 'माहिती लपवा') : '▼ 👤 ' + (counterOrder.customer_name ? counterOrder.customer_name : (currentLang === 'en' ? 'Customer Info / Khata' : (currentLang === 'mr' ? 'ग्राहक खाते / माहिती' : 'ग्राहक खाता / जानकारी'))) }}
                </button>
              </div>

              <!-- Quick Walk-in Summary Banner when collapsed -->
              <div v-if="!posCustomerDetailsOpen" style="background: #f8fafc; border: 1px dashed #cbd5e1; border-radius: 8px; padding: 8px 12px; margin-bottom: 12px; display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 6px; font-size: 0.84rem;">
                <div>
                  <strong>👤 {{ counterOrder.customer_name || (currentLang === 'en' ? 'Walk-in Customer' : 'काउंटर रोख ग्राहक') }}</strong>
                  <span style="color: var(--text-muted); margin-left: 6px;">(📞 {{ counterOrder.customer_phone || '9876543210' }} • 💵 {{ counterOrder.payment_method }})</span>
                </div>
                <button type="button" @click="posCustomerDetailsOpen = true" style="background: none; border: none; color: #2563eb; font-weight: 700; cursor: pointer; text-decoration: underline; font-size: 0.82rem;">
                  ✏️ {{ currentLang === 'en' ? 'Change' : (currentLang === 'mr' ? 'बदला' : 'बदलें') }}
                </button>
              </div>

              <!-- Customer Info (Full Form) -->
              <div v-show="posCustomerDetailsOpen" class="pos-form-grid" style="margin-bottom: 14px;">
                <!-- Select Existing Customer -->
                <div class="pos-input-group" style="grid-column: 1 / -1;">
                  <label class="pos-label">{{ currentLang === 'en' ? 'Select Registered Customer (or type new name below)' : (currentLang === 'mr' ? 'नोंदणीकृत ग्राहक निवडा (किंवा खाली नवीन नाव लिहा)' : 'पंजीकृत ग्राहक चुनें (या नीचे नया नाम लिखें)') }}</label>
                  <select
                    class="pos-select"
                    @change="(e) => {
                      const selId = e.target.value;
                      const cust = adminCustomers.find(c => c.id == selId);
                      selectRegisteredCustomerForPos(cust);
                    }"
                  >
                    <option value="">-- {{ currentLang === 'en' ? 'Search / Select Registered Customer' : (currentLang === 'mr' ? 'नोंदणीकृत ग्राहक शोधा / निवडा' : 'पंजीकृत ग्राहक खोजें / चुनें') }} --</option>
                    <option v-for="c in adminCustomers" :key="c.id" :value="c.id">
                      {{ c.name }} (📞 {{ c.phone }}) {{ c.unpaid_balance > 0 ? (currentLang === 'en' ? `[🔴 Due ₹${c.unpaid_balance}]` : `[🔴 बाकी ₹${c.unpaid_balance}]`) : '' }}
                    </option>
                  </select>
                </div>

                <!-- POS Customer Store Credit Info & Redemption -->
                <div v-if="selectedPosCustomer" class="pos-credit-card" style="grid-column: 1 / -1;">
                  <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 8px;">
                    <div>
                      <span style="font-weight: 800; color: #92400e; font-size: 0.88rem;">💳 {{ t('store_credit_balance') }}:</span>
                      <strong style="color: #065f46; font-size: 1.05rem; margin-left: 6px;">₹{{ (selectedPosCustomer.wallet_balance || 0).toFixed(2) }}</strong>
                    </div>
                    <label v-if="(selectedPosCustomer.wallet_balance || 0) > 0" style="display: flex; align-items: center; gap: 6px; cursor: pointer; font-weight: 800; color: #047857; font-size: 0.86rem;">
                      <input type="checkbox" v-model="posUseStoreCredit" style="width: 16px; height: 16px; accent-color: #059669;" />
                      <span>{{ t('use_store_credit') }} (-₹{{ posAppliedCredit.toFixed(2) }})</span>
                    </label>
                    <span v-else style="font-size: 0.76rem; color: #b45309;">({{ currentLang === 'en' ? 'Balance is 0' : (currentLang === 'mr' ? 'शिल्लक ० आहे' : 'शेष ० है') }})</span>
                  </div>
                </div>

                <div class="pos-input-group">
                  <label class="pos-label">{{ currentLang === 'en' ? 'Customer Name *' : (currentLang === 'mr' ? 'ग्राहकाचे नाव *' : 'ग्राहक का नाम *') }}</label>
                  <input
                    type="text"
                    v-model="counterOrder.customer_name"
                    @input="onPosCustomerManualEdit"
                    class="pos-input"
                    :placeholder="currentLang === 'en' ? 'e.g. Ramesh Hotel / Rahul Patil' : (currentLang === 'mr' ? 'उदा. रमेश हॉटेल / राहुल पाटील' : 'उदा. रमेश होटल / राहुल पाटिल')"
                  />
                </div>

                <div class="pos-input-group">
                  <label class="pos-label">{{ currentLang === 'en' ? 'Mobile Number *' : (currentLang === 'mr' ? 'मोबाईल नंबर *' : 'मोबाइल नंबर *') }}</label>
                  <input
                    type="text"
                    v-model="counterOrder.customer_phone"
                    @input="onPosCustomerManualEdit"
                    class="pos-input"
                    placeholder="9876543210"
                  />
                </div>

                <div class="pos-input-group" style="grid-column: 1 / -1;">
                  <label class="pos-label">{{ currentLang === 'en' ? 'Address / Delivery Location' : (currentLang === 'mr' ? 'पत्ता / डिलिव्हरी ठिकाण' : 'पता / डिलीवरी स्थान') }}</label>
                  <input
                    type="text"
                    v-model="counterOrder.customer_address"
                    class="pos-input"
                    :placeholder="currentLang === 'en' ? 'Counter / Hotel / Home address' : (currentLang === 'mr' ? 'दुकान काउंटर / टेबल / हॉटेल पत्ता' : 'दुकान काउंटर / टेबल / होटल पता')"
                  />
                </div>
              </div>

              <!-- Order & Payment Type -->
              <div class="pos-type-grid">
                <div class="pos-input-group">
                  <label class="pos-label">{{ currentLang === 'en' ? 'Order Type' : (currentLang === 'mr' ? 'ऑर्डर प्रकार' : 'ऑर्डर प्रकार') }}</label>
                  <select v-model="counterOrder.order_type" class="pos-select">
                    <option value="counter">{{ currentLang === 'en' ? '🏬 In-Store / Counter' : (currentLang === 'mr' ? '🏬 दुकानातून घेतला (In-Store)' : '🏬 दुकान से लिया (In-Store)') }}</option>
                    <option value="delivery">{{ currentLang === 'en' ? '🚚 Home Delivery' : (currentLang === 'mr' ? '🚚 होम डिलिव्हरी (Home Delivery)' : '🚚 होम डिलीवरी (Home Delivery)') }}</option>
                    <option value="restaurant">{{ currentLang === 'en' ? '🍽️ Hotel / Commercial Supply' : (currentLang === 'mr' ? '🍽️ हॉटेल/रेस्टॉरंट सप्लाय (Commercial)' : '🍽️ होटल/रेस्टोरेंट सप्लाई (Commercial)') }}</option>
                  </select>
                </div>

                <div class="pos-input-group">
                  <label class="pos-label">{{ currentLang === 'en' ? 'Payment Method' : (currentLang === 'mr' ? 'भुगतान पद्धत' : 'भुगतान माध्यम') }}</label>
                  <select v-model="counterOrder.payment_method" class="pos-select">
                    <option value="Cash on Counter">{{ currentLang === 'en' ? '💵 Cash' : (currentLang === 'mr' ? '💵 रोख नकद (Cash)' : '💵 नकद (Cash)') }}</option>
                    <option value="UPI Instant">{{ currentLang === 'en' ? '📱 Online UPI (GPay/PhonePe)' : (currentLang === 'mr' ? '📱 ऑनलाइन UPI (GPay/PhonePe)' : '📱 ऑनलाइन UPI (GPay/PhonePe)') }}</option>
                    <option value="Kirana Khata (Credit)">{{ currentLang === 'en' ? '🔴 Monthly Khata Credit' : (currentLang === 'mr' ? '🔴 मासिक उधारी खाते (Credit)' : '🔴 मासिक उधारी खाता (Credit)') }}</option>
                  </select>
                </div>

                <div class="pos-input-group" style="grid-column: 1 / -1;">
                  <label class="pos-label">{{ currentLang === 'en' ? 'Payment Status' : (currentLang === 'mr' ? 'पेमेंट स्थिती' : 'पेमेंट स्थिति') }}</label>
                  <div class="pos-type-chips">
                    <button
                      type="button"
                      class="pos-type-chip"
                      :class="{ active: counterOrder.payment_status === 'Paid' }"
                      @click="counterOrder.payment_status = 'Paid'"
                    >
                      🟢 {{ currentLang === 'en' ? 'Paid' : 'चुकता (Paid)' }}
                    </button>
                    <button
                      type="button"
                      class="pos-type-chip"
                      :class="{ active: counterOrder.payment_status === 'Unpaid' }"
                      @click="counterOrder.payment_status = 'Unpaid'"
                      style="color: #b91c1c;"
                    >
                      🔴 {{ currentLang === 'en' ? 'Unpaid / Khata' : 'बाकी उधारी (Unpaid / Khata)' }}
                    </button>
                  </div>
                </div>
              </div>

              <!-- Item Selector -->
              <div class="pos-item-selector">
                <div style="font-weight: 800; font-size: 0.95rem; color: #064e3b; margin-bottom: 10px;">
                  🛒 {{ currentLang === 'en' ? 'Select & Add Items' : (currentLang === 'mr' ? 'सामान निवडा व जोडा' : 'सामान चुनें व जोड़ें') }}
                </div>

                <div class="pos-input-group">
                  <label class="pos-label">{{ currentLang === 'en' ? 'Search Product' : (currentLang === 'mr' ? 'सामान शोधा (Product Name)' : 'सामान खोजें (Product Name)') }}</label>
                  <select
                    class="pos-select"
                    v-model="posSelectedProduct"
                    @change="onPosProductSelect(posSelectedProduct)"
                  >
                    <option :value="null">-- {{ currentLang === 'en' ? 'Select Product...' : (currentLang === 'mr' ? 'सामान निवडा...' : 'सामान चुनें...') }} --</option>
                    <option v-for="p in products" :key="p.id" :value="p">
                      {{ getLocalizedTitle(p) }} {{ p.brand ? `(${p.brand})` : '' }} - {{ p.is_loose ? (currentLang === 'en' ? 'Loose' : (currentLang === 'mr' ? 'मोकळा (Loose)' : 'खुला (Loose)')) : (currentLang === 'en' ? 'Packed' : (currentLang === 'mr' ? 'पॅक (Packed)' : 'पैकेट (Packed)')) }}
                    </option>
                  </select>
                </div>

                <!-- If Product Selected -->
                <div v-if="posSelectedProduct" style="margin-top: 12px; background: white; padding: 12px; border-radius: 8px; border: 1px solid var(--border);">
                  <!-- Loose Custom Weight Mode -->
                  <div v-if="posSelectedProduct.is_loose || isLooseProduct(posSelectedProduct)">
                    <div style="font-size: 0.82rem; color: #059669; font-weight: 800; margin-bottom: 6px;">
                      🌾 {{ currentLang === 'en' ? 'Loose Mandi Commodity (Custom kg)' : (currentLang === 'mr' ? 'मोकळा माल (Loose Mandi Commodity - Custom kg)' : 'खुला राशन (Loose Mandi Commodity - Custom kg)') }}
                    </div>
                    <div style="display: flex; gap: 10px; align-items: flex-end; flex-wrap: wrap;">
                      <div class="pos-input-group" style="flex: 1; min-width: 120px;">
                        <label class="pos-label">{{ currentLang === 'en' ? 'Weight (kg)' : 'वजन (किलो / kg)' }}</label>
                        <input
                          type="number"
                          step="0.25"
                          min="0.25"
                          v-model.number="posCustomWeight"
                          @input="updatePosTierRate"
                          class="pos-input"
                        />
                      </div>
                      <div class="pos-input-group" style="flex: 1; min-width: 120px;">
                        <label class="pos-label">{{ currentLang === 'en' ? 'Rate (₹ per kg)' : (currentLang === 'mr' ? 'दर (₹ प्रति किलो)' : 'दर (₹ प्रति किलो)') }}</label>
                        <input
                          type="number"
                          v-model.number="posCustomRate"
                          class="pos-input"
                        />
                      </div>
                    </div>
                    <div v-if="getMatchingTierInfo(posSelectedProduct, posCustomWeight)" style="margin-top: 6px; font-size: 0.8rem; color: #047857; font-weight: 800;">
                      🏷️ {{ getMatchingTierInfo(posSelectedProduct, posCustomWeight).tier_label }} {{ currentLang === 'en' ? 'applied!' : (currentLang === 'mr' ? 'लागू झाला!' : 'लागू हुआ!') }} (₹{{ posCustomRate }}/kg)
                    </div>
                    <!-- Quick Weight Chips -->
                    <div class="pos-type-chips" style="margin-top: 8px;">
                      <button type="button" class="pos-type-chip" @click="posCustomWeight = 1.0; updatePosTierRate();">1 kg</button>
                      <button type="button" class="pos-type-chip" @click="posCustomWeight = 2.0; updatePosTierRate();">2 kg</button>
                      <button type="button" class="pos-type-chip" @click="posCustomWeight = 2.5; updatePosTierRate();">2.5 kg</button>
                      <button type="button" class="pos-type-chip" @click="posCustomWeight = 5.0; updatePosTierRate();">5 kg ({{ currentLang === 'en' ? 'Wholesale' : 'होलसेल' }})</button>
                      <button type="button" class="pos-type-chip" @click="posCustomWeight = 10.0; updatePosTierRate();">10 kg</button>
                      <button type="button" class="pos-type-chip" @click="posCustomWeight = 25.0; updatePosTierRate();">25 kg {{ currentLang === 'en' ? 'Sack' : 'बोरी' }}</button>
                    </div>
                  </div>

                  <!-- Packaged Product Mode -->
                  <div v-else>
                    <div style="display: flex; gap: 10px; align-items: flex-end; flex-wrap: wrap;">
                      <div class="pos-input-group" style="flex: 1.5; min-width: 150px;">
                        <label class="pos-label">{{ currentLang === 'en' ? 'Pack / Variant' : (currentLang === 'mr' ? 'पॅक / वजन प्रकार' : 'पैक / वजन प्रकार') }}</label>
                        <select
                          v-model="posSelectedVariant"
                          class="pos-select"
                          @change="posCustomRate = posSelectedVariant.selling_price; updatePosTierRate();"
                        >
                          <option v-for="v in posSelectedProduct.variants" :key="v.id" :value="v">
                            {{ v.unit_size }} - ₹{{ v.selling_price }} (MRP ₹{{ v.mrp }})
                          </option>
                        </select>
                      </div>
                      <div class="pos-input-group" style="flex: 1; min-width: 90px;">
                        <label class="pos-label">{{ currentLang === 'en' ? 'Quantity' : (currentLang === 'mr' ? 'नग (Quantity)' : 'नग (Quantity)') }}</label>
                        <input
                          type="number"
                          min="1"
                          v-model.number="posQuantity"
                          @input="updatePosTierRate"
                          class="pos-input"
                        />
                      </div>
                      <div class="pos-input-group" style="flex: 1; min-width: 110px;">
                        <label class="pos-label">{{ currentLang === 'en' ? 'Unit Rate (₹)' : (currentLang === 'mr' ? 'दर (₹ Unit Rate)' : 'दर (₹ Unit Rate)') }}</label>
                        <input
                          type="number"
                          v-model.number="posCustomRate"
                          class="pos-input"
                        />
                      </div>
                    </div>
                    <div v-if="getMatchingTierInfo(posSelectedProduct, posQuantity)" style="margin-top: 6px; font-size: 0.8rem; color: #047857; font-weight: 800;">
                      🏷️ {{ getMatchingTierInfo(posSelectedProduct, posQuantity).tier_label }} {{ currentLang === 'en' ? 'applied!' : (currentLang === 'mr' ? 'लागू झाला!' : 'लागू हुआ!') }} (₹{{ posCustomRate }}/unit)
                    </div>
                  </div>

                  <!-- Add Item Button -->
                  <button
                    type="button"
                    @click="addPosItem"
                    style="margin-top: 12px; width: 100%; padding: 10px; background: #065f46; color: white; border: none; border-radius: 8px; font-weight: 800; cursor: pointer;"
                  >
                    ➕ {{ currentLang === 'en' ? 'Add to Bill' : (currentLang === 'mr' ? 'बिलात जोडा (Add to Bill)' : 'बिल में जोड़ें (Add to Bill)') }}
                  </button>
                </div>
              </div>
            </div>

            <!-- Right Column: Current Bill Summary & Quick Actions -->
            <div class="pos-card" style="display: flex; flex-direction: column;">
              <div class="pos-card-title">
                <span>🧾 {{ currentLang === 'en' ? 'Current Bill Parcha' : (currentLang === 'mr' ? 'चालू बिलाची यादी (Current Bill Parcha)' : 'चालू बिल सूची (Current Bill Parcha)') }}</span>
                <span style="font-size: 0.82rem; color: #047857; margin-left: auto;">
                  {{ counterOrder.items.length }} {{ currentLang === 'en' ? 'items' : 'सामान' }}
                </span>
              </div>

              <!-- Bill Items Table -->
              <div style="flex: 1; max-height: 380px; overflow-y: auto;">
                <div v-if="counterOrder.items.length === 0" style="text-align: center; padding: 40px 10px; color: var(--text-muted);">
                  <div style="font-size: 2.5rem; margin-bottom: 8px;">🛒</div>
                  <p>{{ currentLang === 'en' ? 'No items in the bill yet. Add items from the left.' : (currentLang === 'mr' ? 'बिलात कोणतेही सामान जोडलेले नाही. डावीकडून सामान जोडा.' : 'बिल में कोई सामान नहीं है। बाईं ओर से सामान जोड़ें।') }}</p>
                </div>

                <table v-else class="pos-item-table">
                  <thead>
                    <tr>
                      <th>Item Description</th>
                      <th>Weight / Pack</th>
                      <th>Rate (₹)</th>
                      <th>Qty</th>
                      <th>Amount (₹)</th>
                      <th></th>
                    </tr>
                  </thead>
                  <tbody>
                    <tr v-for="(it, idx) in counterOrder.items" :key="idx">
                      <td><strong>{{ it.product_name }}</strong></td>
                      <td>{{ it.unit_size }}</td>
                      <td>₹{{ it.unit_price }}</td>
                      <td>{{ it.quantity }}</td>
                      <td><strong>₹{{ it.subtotal }}</strong></td>
                      <td>
                        <button
                          type="button"
                          @click="removePosItem(idx)"
                          style="background: none; border: none; color: #ef4444; font-size: 1rem; cursor: pointer;"
                          :title="currentLang === 'en' ? 'Remove' : 'काढून टाका'"
                        >
                          ✕
                        </button>
                      </td>
                    </tr>
                  </tbody>
                </table>
              </div>

              <!-- Bill Totals -->
              <div class="pos-bill-summary" v-if="counterOrder.items.length > 0">
                <div class="pos-bill-row">
                  <span>{{ currentLang === 'en' ? 'MRP Total:' : (currentLang === 'mr' ? 'एकूण एमआरपी (MRP Total):' : 'कुल एमआरपी (MRP Total):') }}</span>
                  <span>₹{{ counterOrderTotals.mrp }}</span>
                </div>
                <div class="pos-bill-row" style="color: #047857; font-weight: 700;">
                  <span>{{ currentLang === 'en' ? 'Store Savings (Discount):' : (currentLang === 'mr' ? 'किराणा बचत (Discount):' : 'किराना बचत (Discount):') }}</span>
                  <span>-₹{{ counterOrderTotals.savings }}</span>
                </div>
                <div v-if="posUseStoreCredit && posAppliedCredit > 0" class="pos-bill-row" style="color: #047857; font-weight: 700;">
                  <span>💳 {{ t('store_credit_applied') }}:</span>
                  <span>-₹{{ posAppliedCredit.toFixed(2) }}</span>
                </div>
                <div class="pos-bill-total">
                  <span>{{ currentLang === 'en' ? 'Total Payable:' : (currentLang === 'mr' ? 'एकूण देय रक्कम:' : 'कुल देय राशि:') }}</span>
                  <span>₹{{ posFinalPayable }}</span>
                </div>
                <div v-if="posEstimatedCredit > 0" class="store-credit-earn-note" style="margin-top: 6px;">
                  💳 {{ currentLang === 'en' ? 'Customer will earn on this bill:' : (currentLang === 'mr' ? 'या बिलावर ग्राहक मिळवेल:' : 'इस बिल पर ग्राहक कमाएगा:') }} <strong>+₹{{ posEstimatedCredit.toFixed(2) }}</strong>
                </div>
              </div>

              <!-- Action Buttons -->
              <div class="pos-actions" v-if="counterOrder.items.length > 0">
                <button
                  type="button"
                  class="pos-btn-primary"
                  :disabled="isPosSubmitting"
                  @click="submitCounterOrder('print')"
                >
                  🖨️ {{ currentLang === 'en' ? 'Save & Print Invoice' : (currentLang === 'mr' ? 'सेव्ह व प्रिंट पावती' : 'सेव व प्रिंट बिल') }}
                </button>

                <button
                  type="button"
                  class="pos-btn-whatsapp"
                  :disabled="isPosSubmitting"
                  @click="submitCounterOrder('whatsapp')"
                >
                  📲 {{ currentLang === 'en' ? 'Save & WhatsApp' : (currentLang === 'mr' ? 'सेव्ह व WhatsApp' : 'सेव व WhatsApp') }}
                </button>

                <button
                  type="button"
                  @click="counterOrder.items = []"
                  style="padding: 10px; background: #f1f5f9; color: var(--text-muted); border: 1px solid var(--border); border-radius: 8px; font-weight: 700; cursor: pointer;"
                  :title="currentLang === 'en' ? 'Clear bill' : 'बिल रिकामे करा'"
                >
                  🗑️
                </button>
              </div>
            </div>
          </div>

          <!-- Floating Mobile POS Action Bar (Always visible over bottom nav when items in bill) -->
          <div class="pos-mobile-floating-bar" v-if="counterOrder.items.length > 0">
            <div class="pos-mob-float-left">
              <span class="pos-mob-float-count">🛒 {{ counterOrder.items.length }} {{ currentLang === 'en' ? 'items' : 'सामान' }}</span>
              <span class="pos-mob-float-total">₹{{ posFinalPayable }}</span>
            </div>
            <div class="pos-mob-float-actions">
              <button
                type="button"
                class="pos-mob-float-btn btn-print"
                :disabled="isPosSubmitting"
                @click="submitCounterOrder('print')"
              >
                🖨️ {{ currentLang === 'en' ? 'Print' : 'पावती' }}
              </button>
              <button
                type="button"
                class="pos-mob-float-btn btn-wa"
                :disabled="isPosSubmitting"
                @click="submitCounterOrder('whatsapp')"
              >
                📲 WA
              </button>
            </div>
          </div>
        </div>

        <!-- TAB 3: ORDERS & KHATA LEDGER -->
        <div v-if="adminActiveTab === 'orders'" style="margin-top: 14px;">
          <!-- Instant Search & Soundbox Paise Reconciler Bar -->
          <div style="background: white; border: 1.5px solid var(--border); border-radius: 12px; padding: 12px 16px; margin-bottom: 12px; display: flex; align-items: center; justify-content: space-between; gap: 12px; flex-wrap: wrap;">
            <div style="flex: 1; min-width: 260px; display: flex; align-items: center; gap: 8px;">
              <span style="font-size: 1.1rem;">🔍</span>
              <input
                type="text"
                v-model="adminOrderSearch"
                :placeholder="currentLang === 'en' ? 'Search Order #, phone, customer, or Soundbox paise (e.g. .37 or 37)...' : (currentLang === 'mr' ? 'ऑर्डर नं, फोन, ग्राहक किंवा साऊंडबॉक्स पैसे शोधा (उदा. .३७ किंवा ३७)...' : 'ऑर्डर नं, फोन, ग्राहक या साउंडबॉक्स पैसे खोजें (उदा. .37 या 37)...')"
                style="flex: 1; padding: 8px 12px; border: 1.5px solid #cbd5e1; border-radius: 8px; font-size: 0.88rem;"
              />
              <button
                v-if="adminOrderSearch"
                type="button"
                @click="adminOrderSearch = ''"
                style="background: #f1f5f9; border: 1px solid #cbd5e1; padding: 6px 10px; border-radius: 6px; font-size: 0.8rem; cursor: pointer;"
              >
                ✕
              </button>
            </div>
            <div style="display: flex; align-items: center; gap: 8px; flex-wrap: wrap;">
              <span v-if="isAdminOrdersSyncing" style="background: #e0f2fe; border: 1px solid #7dd3fc; color: #0369a1; padding: 4px 8px; border-radius: 6px; font-weight: 700; font-size: 0.78rem;">
                🔄 Syncing cloud...
              </span>
              <span v-else style="background: #ecfdf5; border: 1px solid #a7f3d0; color: #065f46; padding: 4px 8px; border-radius: 6px; font-weight: 700; font-size: 0.78rem;" title="Immutable dual-tier local order vault protects all orders from data loss">
                🛡️ Vault Active ({{ adminOrders.length }})
              </span>
              <button
                type="button"
                @click="downloadAdminOrderVault"
                class="btn-secondary"
                style="padding: 5px 10px; font-size: 0.78rem; font-weight: 700; border-radius: 6px; cursor: pointer; display: inline-flex; align-items: center; gap: 4px; background: #f8fafc; border: 1.5px solid #cbd5e1;"
                title="Download complete immutable order vault backup (JSON) to keep on your phone or PC"
              >
                📥 {{ currentLang === 'en' ? 'Vault JSON' : (currentLang === 'mr' ? 'व्हॉल्ट JSON' : 'वॉल्ट JSON') }}
              </button>
              <button
                type="button"
                @click="restoreAdminOrderVault"
                class="btn-secondary"
                style="padding: 5px 10px; font-size: 0.78rem; font-weight: 700; border-radius: 6px; cursor: pointer; display: inline-flex; align-items: center; gap: 4px; background: #fef3c7; border: 1.5px solid #fde68a; color: #92400e;"
                title="Disaster Recovery: 1-Click restore any missing orders from local vault to database"
              >
                🔄 {{ currentLang === 'en' ? 'Restore Vault' : (currentLang === 'mr' ? 'व्हॉल्ट रिस्टोअर' : 'वॉल्ट रिस्टोर') }}
              </button>
              <button
                type="button"
                @click="downloadAdminExport('orders.csv')"
                class="btn-secondary"
                style="padding: 5px 10px; font-size: 0.78rem; font-weight: 700; border-radius: 6px; cursor: pointer; display: inline-flex; align-items: center; gap: 4px;"
                title="Export all orders to Excel / CSV"
              >
                📊 {{ currentLang === 'en' ? 'Orders CSV' : (currentLang === 'mr' ? 'ऑर्डर्स CSV' : 'ऑर्डर CSV') }}
              </button>
              <button
                type="button"
                @click="downloadAdminExport('customers.csv')"
                class="btn-secondary"
                style="padding: 5px 10px; font-size: 0.78rem; font-weight: 700; border-radius: 6px; cursor: pointer; display: inline-flex; align-items: center; gap: 4px;"
                title="Export customer khata ledger to CSV"
              >
                👥 {{ currentLang === 'en' ? 'Khata CSV' : (currentLang === 'mr' ? 'खातेदार CSV' : 'खातेदार CSV') }}
              </button>
              <button
                type="button"
                @click="downloadAdminExport('database')"
                style="background: #064e3b; color: white; border: none; padding: 5px 11px; font-size: 0.78rem; font-weight: 800; border-radius: 6px; cursor: pointer; display: inline-flex; align-items: center; gap: 4px;"
                title="Download full SQLite database backup"
              >
                💾 {{ currentLang === 'en' ? 'Backup DB' : (currentLang === 'mr' ? 'बॅकअप DB' : 'बैकअप DB') }}
              </button>
            </div>
          </div>

          <!-- Filter Row for Admin Orders -->
          <div class="admin-orders-filter-row">
            <button
              :class="{ active: adminOrderFilter === 'all' }"
              @click="adminOrderFilter = 'all'"
            >
              {{ currentLang === 'en' ? 'All Orders' : (currentLang === 'mr' ? 'सर्व ऑर्डर्स' : 'सभी ऑर्डर') }} ({{ isAdminOrdersLoading ? '...' : adminOrders.length }})
            </button>
            <button
              :class="{ active: adminOrderFilter === 'pending' }"
              @click="adminOrderFilter = 'pending'"
              style="color: #b45309; font-weight: 800; background: #fef3c7; border: 1px solid #fde68a;"
            >
              ⏳ {{ currentLang === 'en' ? 'Verify UPI' : (currentLang === 'mr' ? 'UPI पडताळणी' : 'UPI सत्यापन') }} ({{ isAdminOrdersLoading ? '...' : pendingVerificationAdminOrders.length }})
            </button>
            <button
              :class="{ active: adminOrderFilter === 'unpaid' }"
              @click="adminOrderFilter = 'unpaid'"
              style="color: #b91c1c; font-weight: 800;"
            >
              🔴 {{ currentLang === 'en' ? 'Unpaid / Khata' : (currentLang === 'mr' ? 'बाकी / उधारी' : 'बाकी / उधारी') }} ({{ isAdminOrdersLoading ? '...' : unpaidAdminOrders.length }})
            </button>
            <button
              :class="{ active: adminOrderFilter === 'paid' }"
              @click="adminOrderFilter = 'paid'"
              style="color: #15803d; font-weight: 800;"
            >
              🟢 {{ currentLang === 'en' ? 'Paid' : (currentLang === 'mr' ? 'चुकता' : 'चुकता') }} ({{ isAdminOrdersLoading ? '...' : paidAdminOrders.length }})
            </button>
            <button
              :class="{ active: adminOrderFilter === 'cod' }"
              @click="adminOrderFilter = 'cod'"
            >
              💵 {{ currentLang === 'en' ? 'Cash COD' : (currentLang === 'mr' ? 'नकद COD' : 'नकद COD') }} ({{ isAdminOrdersLoading ? '...' : codAdminOrders.length }})
            </button>
            <button
              :class="{ active: adminOrderFilter === 'upi' }"
              @click="adminOrderFilter = 'upi'"
            >
              📱 {{ currentLang === 'en' ? 'UPI QR' : 'UPI QR' }} ({{ isAdminOrdersLoading ? '...' : upiAdminOrders.length }})
            </button>
          </div>

          <!-- Batch Select & Print Action Bar -->
          <div class="admin-batch-toolbar" v-if="displayedAdminOrders.length > 0">
            <label class="batch-select-all-label">
              <input
                type="checkbox"
                :checked="isAllDisplayedOrdersSelected"
                @change="toggleSelectAllOrders"
                class="batch-checkbox"
              />
              <span>{{ t('select_all_orders') }}</span>
            </label>

            <div style="display: flex; gap: 10px; align-items: center; flex-wrap: wrap;">
              <span class="selected-count-badge" v-if="selectedAdminOrderIds.length > 0">
                ✓ {{ selectedAdminOrderIds.length }} {{ t('selected_orders_count') }}
              </span>
              <button
                class="batch-print-btn"
                :disabled="selectedAdminOrderIds.length === 0"
                @click="openBatchPrintModal"
              >
                {{ t('admin_batch_print_btn') }} ({{ selectedAdminOrderIds.length }})
              </button>
            </div>
          </div>

          <!-- Loading state while fetching orders from cloud -->
          <div v-if="isAdminOrdersLoading" style="text-align: center; padding: 48px 20px; color: #065f46; background: #f0fdf4; border-radius: 12px; border: 1.5px solid #a7f3d0; font-weight: 700;">
            <div style="font-size: 1.8rem; margin-bottom: 8px;">🔄</div>
            <div>{{ currentLang === 'en' ? 'Loading orders from cloud database...' : (currentLang === 'mr' ? 'क्लाउड डेटाबेसमधून ऑर्डर्स लोड होत आहेत...' : 'क्लाउड डेटाबेस से ऑर्डर लोड हो रहे हैं...') }}</div>
          </div>
          <div v-else-if="displayedAdminOrders.length === 0" style="text-align: center; padding: 40px 20px; color: var(--text-muted); background: white; border-radius: 12px; border: 1px dashed var(--border);">
            {{ currentLang === 'en' ? 'No orders found matching this filter.' : (currentLang === 'mr' ? 'या फिल्टरमध्ये कोणतीही ऑर्डर सापडली नाही.' : 'इस फ़िल्टर में कोई ऑर्डर नहीं मिला।') }}
          </div>
          <div v-else style="display: flex; flex-direction: column; gap: 16px;">
            <div
              v-for="ord in displayedAdminOrders"
              :key="ord.id"
              class="admin-order-ticket"
            >
              <div class="admin-order-ticket-header">
                <div class="admin-order-ticket-id">
                  <input
                    type="checkbox"
                    :value="ord.id"
                    v-model="selectedAdminOrderIds"
                    class="order-select-checkbox"
                    :title="currentLang === 'en' ? 'Select this invoice' : 'या ऑर्डरचा पर्चा निवडा'"
                  />
                  <div>
                    <span style="font-weight: 900; color: #064e3b; font-size: 1.05rem;">
                      {{ ord.order_number }}
                    </span>
                    <span style="margin-left: 8px; font-size: 0.8rem; color: var(--text-subtle);">
                      {{ ord.created_at }}
                    </span>
                    <!-- Soundbox Micro-Paise Match Badge -->
                    <span
                      v-if="isUpiMethod(ord.payment_method)"
                      style="margin-left: 8px; background: #ecfdf5; border: 1.5px solid #6ee7b7; color: #065f46; font-size: 0.78rem; font-weight: 900; padding: 2px 8px; border-radius: 6px; display: inline-flex; align-items: center; gap: 4px;"
                      :title="'Soundbox Paise Identifier: .' + getSoundboxPaise(ord.final_amount)"
                    >
                      🔊 साऊंडबॉक्स: .{{ getSoundboxPaise(ord.final_amount) }}
                    </span>
                    <!-- Customer Delivery Availability Badge -->
                    <span
                      v-if="ord.delivery_availability === 'available'"
                      style="margin-left: 8px; background: #dcfce7; border: 1.5px solid #86efac; color: #166534; font-size: 0.78rem; font-weight: 900; padding: 2px 8px; border-radius: 6px; display: inline-flex; align-items: center; gap: 4px;"
                      title="Customer clicked: Yes, I am available for delivery!"
                    >
                      🟢 {{ currentLang === 'en' ? 'Available (Confirmed)' : (currentLang === 'mr' ? 'ग्राहक उपलब्ध (सहमती)' : 'ग्राहक उपलब्ध (सहमति)') }}
                    </span>
                    <span
                      v-else-if="ord.delivery_availability === 'reschedule'"
                      style="margin-left: 8px; background: #fef3c7; border: 1.5px solid #fde047; color: #854d0e; font-size: 0.78rem; font-weight: 900; padding: 2px 8px; border-radius: 6px; display: inline-flex; align-items: center; gap: 4px;"
                      title="Customer requested to reschedule delivery"
                    >
                      ⏳ {{ currentLang === 'en' ? 'Reschedule Requested' : (currentLang === 'mr' ? 'वेळ बदला (Reschedule)' : 'रीशेड्यूल (बाद में भेजें)') }}
                    </span>
                    <span
                      v-else-if="ord.status === 'Out for Delivery'"
                      style="margin-left: 8px; background: #f1f5f9; border: 1.5px solid #cbd5e1; color: #475569; font-size: 0.78rem; font-weight: 800; padding: 2px 8px; border-radius: 6px; display: inline-flex; align-items: center; gap: 4px;"
                      title="Awaiting customer confirmation via WhatsApp link"
                    >
                      📲 {{ currentLang === 'en' ? 'Avail. Link Sent' : (currentLang === 'mr' ? 'उपलब्धता लिंक पाठवली' : 'उपलब्धता लिंक भेजी') }}
                    </span>
                  </div>
                </div>
                <div class="admin-order-ticket-amount" style="text-align: right;">
                  <div>₹{{ ord.final_amount }}</div>
                  <div v-if="ord.payment_status === 'Partially Paid'" style="font-size: 0.76rem; color: #b91c1c; font-weight: 800;">
                    (₹{{ ord.balance_due || (ord.final_amount - (ord.amount_paid || 0)) }} बाकी)
                  </div>
                </div>
              </div>

              <div class="admin-order-ticket-controls">
                <div class="admin-order-status-group">
                  <!-- Delivery Status Dropdown -->
                  <select
                    v-model="ord.status"
                    @change="updateAdminOrderStatus(ord)"
                    class="admin-order-select"
                  >
                    <option value="Placed">{{ currentLang === 'en' ? 'Placed' : (currentLang === 'mr' ? 'Placed (नोंदवली)' : 'Placed (ऑर्डर दर्ज)') }}</option>
                    <option value="Packed">{{ currentLang === 'en' ? 'Packed' : (currentLang === 'mr' ? 'Packed (पॅक तयार)' : 'Packed (पैक तैयार)') }}</option>
                    <option value="Out for Delivery">{{ currentLang === 'en' ? 'Out for Delivery' : (currentLang === 'mr' ? 'Out for Delivery (निघाले)' : 'Out for Delivery (रास्ते में)') }}</option>
                    <option value="Delivered">{{ currentLang === 'en' ? 'Delivered' : (currentLang === 'mr' ? 'Delivered (दिले)' : 'Delivered (सफलतापूर्वक दिया)') }}</option>
                  </select>

                  <!-- Payment Status Dropdown -->
                  <select
                    v-model="ord.payment_status"
                    @change="updateAdminOrderStatus(ord)"
                    class="admin-order-select"
                    :style="ord.payment_status === 'Paid' ? 'color: #14532d; background: #dcfce7;' : (ord.payment_status === 'Partially Paid' ? 'color: #854d0e; background: #fef9c3;' : (ord.payment_status === 'Pending Verification' ? 'color: #92400e; background: #fef3c7;' : (ord.payment_status === 'Payment Failed' ? 'color: #c2410c; background: #ffedd5;' : 'color: #991b1b; background: #fee2e2;')))"
                  >
                    <option value="Paid">{{ currentLang === 'en' ? '🟢 Paid' : (currentLang === 'mr' ? '🟢 चुकता (Paid)' : '🟢 चुकता (Paid)') }}</option>
                    <option value="Partially Paid">{{ currentLang === 'en' ? '🟡 Partially Paid' : (currentLang === 'mr' ? '🟡 अर्धवट भरले (Partially Paid)' : '🟡 आंशिक भुगतान (Partially Paid)') }}</option>
                    <option value="Pending Verification">{{ currentLang === 'en' ? '⏳ Pending Verification' : (currentLang === 'mr' ? '⏳ UPI पडताळणी बाकी' : '⏳ UPI सत्यापन बाकी') }}</option>
                    <option value="Payment Failed">{{ currentLang === 'en' ? '⚠️ Payment Failed / Stuck' : (currentLang === 'mr' ? '⚠️ पेमेंट अयशस्वी / अडकले' : '⚠️ पेमेंट विफल / अटका') }}</option>
                    <option value="Unpaid">{{ currentLang === 'en' ? '🔴 Unpaid Khata' : (currentLang === 'mr' ? '🔴 बाकी उधारी (Unpaid)' : '🔴 बाकी उधारी (Unpaid)') }}</option>
                  </select>
                </div>

                <!-- 1-Click Mark as Paid / Verify Button -->
                <button
                  v-if="ord.payment_status !== 'Paid'"
                  @click="markOrderAsPaid(ord)"
                  class="admin-mark-paid-btn"
                  :style="ord.payment_status === 'Pending Verification' ? 'background: #059669; color: white;' : (ord.payment_status === 'Partially Paid' ? 'background: #d97706; color: white;' : '')"
                  :title="ord.payment_status === 'Pending Verification' ? 'Verify bank SMS/App and mark as Paid' : (ord.payment_status === 'Partially Paid' ? 'Collect remaining balance and mark as Paid' : 'Mark order as paid upon cash receipt')"
                >
                  <span v-if="ord.payment_status === 'Pending Verification'">
                    ✅ {{ currentLang === 'en' ? 'Verify & Mark Paid' : (currentLang === 'mr' ? 'UPI तपासून चुकता करा' : 'UPI चेक कर चुकता करें') }}
                  </span>
                  <span v-else-if="ord.payment_status === 'Partially Paid'">
                    ✅ {{ currentLang === 'en' ? `Collect ₹${ord.balance_due || (ord.final_amount - (ord.amount_paid || 0))} & Mark Paid` : (currentLang === 'mr' ? `बाकी ₹${ord.balance_due || (ord.final_amount - (ord.amount_paid || 0))} जमा करून चुकता करा` : `बाकी ₹${ord.balance_due || (ord.final_amount - (ord.amount_paid || 0))} जमा कर चुकता करें`) }}
                  </span>
                  <span v-else>
                    ✅ {{ currentLang === 'en' ? 'Mark Paid' : (currentLang === 'mr' ? 'रोख मिळाली (Mark Paid)' : 'नकद मिला (Mark Paid)') }}
                  </span>
                </button>
              </div>

              <div style="display: flex; justify-content: space-between; margin-top: 12px; font-size: 0.88rem; color: var(--text-main); flex-wrap: wrap; gap: 10px;">
                <div>
                  <strong>{{ currentLang === 'en' ? 'Customer:' : (currentLang === 'mr' ? 'ग्राहक:' : 'ग्राहक:') }}</strong> {{ ord.customer_name }} (<a :href="'tel:' + ord.customer_phone" class="phone-call-pill" title="Call Customer directly">📞 {{ ord.customer_phone }}</a>)<br />
                  <strong>{{ currentLang === 'en' ? 'Address:' : (currentLang === 'mr' ? 'पत्ता:' : 'पता:') }}</strong> {{ ord.customer_address }}
                </div>
                <div style="text-align: right;">
                  <strong>{{ currentLang === 'en' ? 'Payment Method:' : (currentLang === 'mr' ? 'पेमेंट पद्धत:' : 'भुगतान तरीका:') }}</strong> {{ ord.payment_method }}<br />
                  <span style="color: #047857; font-weight: 800;">{{ currentLang === 'en' ? 'Store Savings:' : (currentLang === 'mr' ? 'किराणा बचत:' : 'किराना बचत:') }} ₹{{ ord.total_savings }}</span>
                </div>
              </div>

              <!-- Order Items Preview -->
              <div style="margin-top: 12px; background: white; padding: 10px 14px; border-radius: 8px; border: 1px solid var(--border); font-size: 0.84rem;">
                <strong>{{ currentLang === 'en' ? 'Items List:' : (currentLang === 'mr' ? 'सामान सूची:' : 'सामान सूची:') }}</strong>
                <span v-for="(it, idx) in ord.items" :key="idx" style="margin-left: 8px; color: var(--text-muted);">
                  {{ it.product_name }} ({{ it.variant_label }}) × {{ it.quantity }} = ₹{{ it.subtotal }}{{ idx < ord.items.length - 1 ? ' | ' : '' }}
                </span>
              </div>

              <!-- Admin Action Buttons: View Full Invoice, Direct Print, Call, WhatsApp -->
              <div class="admin-order-action-bar">
                <a
                  :href="'tel:' + ord.customer_phone"
                  class="admin-action-btn"
                  style="background: #eff6ff; border-color: #bfdbfe; color: #1d4ed8; font-weight: 800; text-decoration: none; display: inline-flex; align-items: center; justify-content: center; gap: 4px;"
                  title="Call customer directly from phone"
                >
                  📞 {{ currentLang === 'en' ? 'Call' : 'कॉल' }}
                </a>
                <button
                  class="admin-action-btn view-bill-btn"
                  @click="viewOrderReceipt(ord)"
                >
                  {{ t('admin_view_bill') }}
                </button>
                <button
                  class="admin-action-btn print-bill-btn"
                  @click="printSingleOrder(ord)"
                >
                  {{ t('admin_print_direct') }}
                </button>
                <button
                  type="button"
                  class="admin-action-btn"
                  style="background: #ecfdf5; border-color: #a7f3d0; color: #047857; font-weight: 800;"
                  @click="downloadOrderPdf(ord)"
                >
                  📥 PDF
                </button>
                
                <!-- WhatsApp Status Menu -->
                <div class="whatsapp-status-dropdown-wrap" style="position: relative;">
                  <button
                    type="button"
                    class="admin-action-btn whatsapp-bill-btn"
                    @click="toggleWhatsAppOrderMenu(ord.id)"
                  >
                    📲 WhatsApp ▾
                  </button>
                  <div v-if="activeWhatsAppOrderMenuId === ord.id" class="whatsapp-status-popover">
                    <button type="button" @click="sendAdminWhatsAppStatus(ord, 'confirmed'); activeWhatsAppOrderMenuId = null">
                      📦 {{ currentLang === 'en' ? 'Order Confirmed' : 'ऑर्डर कन्फर्म झाली' }}
                    </button>
                    <button type="button" @click="sendAdminWhatsAppStatus(ord, 'out_for_delivery'); activeWhatsAppOrderMenuId = null">
                      🛵 {{ currentLang === 'en' ? 'Out for Delivery' : 'डिलिव्हरी निघाली' }}
                    </button>
                    <button type="button" @click="sendAdminWhatsAppStatus(ord, 'delivered'); activeWhatsAppOrderMenuId = null">
                      ✅ {{ currentLang === 'en' ? 'Delivered' : 'डिलिव्हरी पूर्ण झाली' }}
                    </button>
                    <button type="button" @click="sendAdminWhatsAppStatus(ord, 'verified'); activeWhatsAppOrderMenuId = null" v-if="ord.payment_status === 'Paid'">
                      🟢 {{ currentLang === 'en' ? 'Payment Verified' : 'पेमेंट पडताळणी झाली' }}
                    </button>
                    <button type="button" @click="sendAdminWhatsAppStatus(ord, 'payment_failed'); activeWhatsAppOrderMenuId = null" style="color: #b45309; font-weight: 700; border-top: 1px solid #fed7aa; background: #fffbeb;">
                      ⚠️ {{ currentLang === 'en' ? 'Payment Not Received / Stuck' : (currentLang === 'mr' ? 'पेमेंट मिळाले नाही / अडकले' : 'पेमेंट नहीं मिला / अटका') }}
                    </button>
                    <button type="button" @click="shareOrderOnWhatsApp(ord); activeWhatsAppOrderMenuId = null" style="border-top: 1px solid #e2e8f0; font-weight: 800; color: #064e3b;">
                      📄 {{ t('admin_whatsapp_direct') }} (Full Bill)
                    </button>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- TAB 4: REGISTERED CUSTOMERS DIRECTORY & KHATA AUDIT -->
        <div v-if="adminActiveTab === 'customers'" style="margin-top: 14px;">
          <!-- Top KPI Strip for Customers -->
          <div class="customer-stats-strip">
            <div class="customer-card-box">
              <div style="font-size: 0.82rem; color: var(--text-muted); font-weight: 700;">
                👥 {{ currentLang === 'en' ? 'Total Registered Customers' : (currentLang === 'mr' ? 'एकूण नोंदणीकृत ग्राहक' : 'कुल पंजीकृत ग्राहक') }}
              </div>
              <div style="font-size: 1.6rem; font-weight: 900; color: #064e3b; margin-top: 4px;">
                {{ adminCustomers.length }}
              </div>
            </div>

            <div class="customer-card-box">
              <div style="font-size: 0.82rem; color: var(--text-muted); font-weight: 700;">
                🔴 {{ currentLang === 'en' ? 'Customers with Khata Dues' : (currentLang === 'mr' ? 'उधारी असलेले ग्राहक' : 'उधारी वाले ग्राहक') }}
              </div>
              <div style="font-size: 1.6rem; font-weight: 900; color: #dc2626; margin-top: 4px;">
                {{ khataCustomersCount }}
              </div>
            </div>

            <div class="customer-card-box">
              <div style="font-size: 0.82rem; color: var(--text-muted); font-weight: 700;">
                💰 {{ currentLang === 'en' ? 'Total Market Outstanding Credit' : (currentLang === 'mr' ? 'बाजारातील एकूण बाकी उधारी' : 'बाजार में कुल बाकी उधारी') }}
              </div>
              <div style="font-size: 1.6rem; font-weight: 900; color: #b91c1c; margin-top: 4px;">
                ₹{{ totalKhataOutstanding }}
              </div>
            </div>
          </div>

          <!-- Customer Filter Bar -->
          <div class="customer-directory-header">
            <input
              type="text"
              v-model="customerSearch"
              :placeholder="currentLang === 'en' ? 'Search customers by name or phone...' : (currentLang === 'mr' ? 'नाव किंवा फोन नंबरने ग्राहक शोधा...' : 'नाम या फोन नंबर से ग्राहक खोजें...')"
              style="padding: 9px 16px; border: 1.5px solid var(--border); border-radius: 10px; font-size: 0.9rem; min-width: 320px;"
            />
            <span style="font-size: 0.88rem; color: var(--text-muted);">
              {{ currentLang === 'en' ? 'Shown Customers:' : (currentLang === 'mr' ? 'दाखवलेले ग्राहक:' : 'दिखाए गए ग्राहक:') }} <strong>{{ filteredAdminCustomers.length }}</strong>
            </span>
          </div>

          <!-- Customers Table (Desktop / PC View) -->
          <div class="admin-table-wrap desktop-table-view" style="margin-top: 14px;">
            <table class="admin-table">
              <thead>
                <tr>
                  <th>{{ currentLang === 'en' ? 'Customer Name' : (currentLang === 'mr' ? 'ग्राहक नाव' : 'ग्राहक नाम') }}</th>
                  <th>{{ currentLang === 'en' ? 'Mobile Number' : (currentLang === 'mr' ? 'मोबाईल नंबर' : 'मोबाइल नंबर') }}</th>
                  <th>{{ currentLang === 'en' ? 'Registration Date' : (currentLang === 'mr' ? 'नोंदणी दिनांक' : 'रजिस्टर दिनांक') }}</th>
                  <th>{{ currentLang === 'en' ? 'Total Orders' : (currentLang === 'mr' ? 'एकूण ऑर्डर्स' : 'कुल ऑर्डर') }}</th>
                  <th>{{ currentLang === 'en' ? 'Total Spent' : (currentLang === 'mr' ? 'एकूण खरेदी' : 'कुल खरीदारी') }}</th>
                  <th>{{ t('store_credit') }}</th>
                  <th>{{ currentLang === 'en' ? 'Khata Status' : (currentLang === 'mr' ? 'उधारी स्थिती' : 'उधारी स्थिति') }}</th>
                  <th>{{ currentLang === 'en' ? 'Action' : (currentLang === 'mr' ? 'कृती (Action)' : 'कार्रवाई (Action)') }}</th>
                </tr>
              </thead>
              <tbody>
                <tr v-if="filteredAdminCustomers.length === 0">
                  <td colspan="8" style="text-align: center; padding: 30px; color: var(--text-muted);">
                    {{ currentLang === 'en' ? 'No customers found.' : (currentLang === 'mr' ? 'कोणताही ग्राहक सापडला नाही.' : 'कोई ग्राहक नहीं मिला।') }}
                  </td>
                </tr>
                <tr v-for="c in filteredAdminCustomers" :key="c.id">
                  <td>
                    <strong>{{ c.name }}</strong>
                    <div style="font-size: 0.76rem; color: var(--text-subtle);">{{ c.email }}</div>
                  </td>
                  <td>
                    <a :href="'tel:' + c.phone" class="phone-call-pill" title="Click to call customer">
                      📞 {{ c.phone }}
                    </a>
                  </td>
                  <td>{{ c.created_at }}</td>
                  <td><strong>{{ c.total_orders }}</strong></td>
                  <td><strong>₹{{ c.total_spent }}</strong></td>
                  <td><strong style="color: #047857; font-weight: 800;">₹{{ (c.wallet_balance || 0).toFixed(2) }}</strong></td>
                  <td>
                    <span v-if="c.unpaid_balance > 0" class="cust-balance-danger">
                      🔴 ₹{{ c.unpaid_balance }} {{ currentLang === 'en' ? 'Due' : 'बाकी' }}
                    </span>
                    <span v-else class="cust-balance-success">
                      🟢 ₹0 {{ currentLang === 'en' ? 'Settled' : 'चुकता' }}
                    </span>
                  </td>
                  <td>
                    <button
                      type="button"
                      @click="openCustomerAudit(c)"
                      style="background: #065f46; color: white; border: none; padding: 6px 12px; border-radius: 6px; font-weight: 700; font-size: 0.8rem; cursor: pointer; display: flex; align-items: center; gap: 5px;"
                      :title="currentLang === 'en' ? 'View customer past bills and purchase history' : 'ग्राहकाची मागील सर्व बिले व खरेदी इतिहास पहा'"
                    >
                      🧾 {{ currentLang === 'en' ? 'See Past Bills' : (currentLang === 'mr' ? 'जुनी बिले पहा' : 'पुराने बिल देखें') }}
                    </button>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>

          <!-- Mobile Customer Directory Cards (Phone Screens <= 768px) -->
          <div class="admin-mobile-customer-list">
            <div v-if="filteredAdminCustomers.length === 0" style="text-align: center; padding: 30px; color: var(--text-muted); background: white; border-radius: 12px; border: 1px dashed var(--border);">
              {{ currentLang === 'en' ? 'No customers found.' : (currentLang === 'mr' ? 'कोणताही ग्राहक सापडला नाही.' : 'कोई ग्राहक नहीं मिला।') }}
            </div>
            <div
              v-for="c in filteredAdminCustomers"
              :key="'mob-cust-' + c.id"
              class="admin-mob-item-card"
            >
              <div class="admin-mob-card-head">
                <div>
                  <div class="admin-mob-name">{{ c.name }}</div>
                  <div style="font-size: 0.74rem; color: var(--text-muted);">{{ c.email || 'Mobile Account' }} • Joined {{ c.created_at }}</div>
                </div>
                <div>
                  <span v-if="c.unpaid_balance > 0" class="cust-balance-danger">
                    🔴 ₹{{ c.unpaid_balance }} Due
                  </span>
                  <span v-else class="cust-balance-success">
                    🟢 Settled
                  </span>
                </div>
              </div>

              <!-- Stats Pill Grid -->
              <div style="display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 6px; margin: 8px 0; background: #f8fafc; padding: 8px 10px; border-radius: 8px;">
                <div style="font-size: 0.78rem;">
                  <span style="color: var(--text-muted); display: block;">Orders:</span>
                  <strong>{{ c.total_orders }}</strong>
                </div>
                <div style="font-size: 0.78rem;">
                  <span style="color: var(--text-muted); display: block;">Spent:</span>
                  <strong>₹{{ c.total_spent }}</strong>
                </div>
                <div style="font-size: 0.78rem;">
                  <span style="color: var(--text-muted); display: block;">Credit:</span>
                  <strong style="color: #047857;">₹{{ (c.wallet_balance || 0).toFixed(2) }}</strong>
                </div>
              </div>

              <!-- Mobile Actions Bar: 1-Tap Call, Past Bills & Settle -->
              <div style="display: flex; gap: 8px; margin-top: 10px; flex-wrap: wrap;">
                <a
                  :href="'tel:' + c.phone"
                  class="admin-action-btn"
                  style="flex: 1; min-width: 130px; background: #eff6ff; border-color: #bfdbfe; color: #1d4ed8; font-weight: 800; text-decoration: none; display: flex; align-items: center; justify-content: center; gap: 4px; padding: 8px;"
                  title="Call Customer"
                >
                  📞 {{ currentLang === 'en' ? 'Call' : 'कॉल' }} ({{ c.phone }})
                </a>
                <button
                  type="button"
                  @click="openCustomerAudit(c)"
                  class="admin-action-btn"
                  style="flex: 1; min-width: 120px; background: #065f46; color: white; border: none; font-weight: 800; padding: 8px;"
                >
                  🧾 {{ currentLang === 'en' ? 'Past Bills' : (currentLang === 'mr' ? 'जुनी बिले' : 'पुराने बिल') }}
                </button>
                <button
                  v-if="c.unpaid_balance > 0"
                  type="button"
                  @click="openKhataPayForCustomer(c)"
                  class="admin-action-btn"
                  style="background: #ecfdf5; border-color: #86efac; color: #047857; font-weight: 800; padding: 8px 12px;"
                >
                  💰 {{ currentLang === 'en' ? 'Settle' : 'जमा' }}
                </button>
              </div>
            </div>
          </div>
        </div>

        <!-- TAB 5: DIGITAL KHATA BOOK & UDHAAR LEDGER -->
        <div v-if="adminActiveTab === 'khata'">
          <!-- Top Khata Stat KPI Cards -->
          <div class="admin-stats-grid" style="margin-top: 18px;">
            <div class="stat-card stat-card-danger">
              <div class="stat-icon">🔴</div>
              <div class="stat-content">
                <span class="stat-label">{{ t('admin_khata_market_udhaar') }}</span>
                <strong class="stat-val">₹{{ adminKhataSummary.total_market_udhaar }}</strong>
              </div>
            </div>
            <div class="stat-card">
              <div class="stat-icon">👥</div>
              <div class="stat-content">
                <span class="stat-label">{{ t('admin_khata_customers') }}</span>
                <strong class="stat-val">{{ adminKhataSummary.total_khata_customers }}</strong>
              </div>
            </div>
            <div class="stat-card stat-card-success">
              <div class="stat-icon">🟢</div>
              <div class="stat-content">
                <span class="stat-label">{{ t('admin_khata_recovered_month') }}</span>
                <strong class="stat-val">₹{{ adminKhataSummary.total_recovered_month }}</strong>
              </div>
            </div>
          </div>

          <!-- Khata Filter & Search Bar -->
          <div style="margin-top: 18px; display: flex; justify-content: space-between; align-items: center; gap: 12px; flex-wrap: wrap;">
            <div style="display: flex; align-items: center; gap: 10px; flex: 1; max-width: 420px;">
              <input
                type="text"
                v-model="khataSearch"
                :placeholder="t('admin_khata_search_placeholder')"
                style="width: 100%; padding: 10px 14px; border: 1.5px solid var(--border); border-radius: 8px; font-size: 0.9rem;"
              />
            </div>
            <button
              @click="loadAdminKhata"
              style="background: #065f46; color: white; border: none; padding: 10px 16px; border-radius: 8px; font-weight: 700; cursor: pointer; display: flex; align-items: center; gap: 6px;"
            >
              {{ t('admin_khata_refresh') }}
            </button>
          </div>

          <!-- Khata Table (Desktop / PC View) -->
          <div class="admin-table-wrap desktop-table-view" style="margin-top: 14px;">
            <table class="admin-table">
              <thead>
                <tr>
                  <th>{{ t('admin_khata_col_name') }}</th>
                  <th>{{ t('admin_khata_col_phone') }}</th>
                  <th>{{ t('admin_khata_col_bills') }}</th>
                  <th>{{ t('admin_khata_col_last_purchase') }}</th>
                  <th>{{ t('admin_khata_col_net_due') }}</th>
                  <th>{{ t('admin_khata_col_actions') }}</th>
                </tr>
              </thead>
              <tbody>
                <tr v-if="filteredKhataList.length === 0">
                  <td colspan="6" style="text-align: center; padding: 36px; color: var(--text-muted);">
                    {{ khataLoading ? (currentLang === 'en' ? 'Loading ledger...' : (currentLang === 'mr' ? 'खाते बही लोड होत आहे...' : 'खाता बही लोड हो रही है...')) : (currentLang === 'en' ? 'Zero dues outstanding! All bills are settled. 🎉' : (currentLang === 'mr' ? 'कोणतीही उधारी बाकी नाही! सर्व बिले चुकता आहेत. 🎉' : 'कोई उधारी बाकी नहीं है! सभी बिल चुकता हैं। 🎉')) }}
                  </td>
                </tr>
                <tr v-for="c in filteredKhataList" :key="c.customer_phone">
                  <td>
                    <strong>{{ c.customer_name }}</strong>
                    <div v-if="c.customer_address" style="font-size: 0.74rem; color: var(--text-subtle);">📍 {{ c.customer_address }}</div>
                  </td>
                  <td>
                    <a :href="'tel:' + c.customer_phone" class="phone-call-pill" title="Click to call customer">
                      📞 {{ c.customer_phone }}
                    </a>
                  </td>
                  <td>
                    <span class="status-badge unpaid" style="font-size: 0.76rem;">
                      {{ c.unpaid_orders.length }} {{ t('admin_khata_bills_due_suffix') }}
                    </span>
                  </td>
                  <td><small>{{ c.last_order_date }}</small></td>
                  <td>
                    <strong style="color: #dc2626; font-size: 1.1rem; font-weight: 900;">
                      ₹{{ c.net_balance_due }}
                    </strong>
                  </td>
                  <td>
                    <div style="display: flex; gap: 6px; flex-wrap: wrap;">
                      <button
                        type="button"
                        @click="openKhataPay(c)"
                        style="background: #059669; color: white; border: none; padding: 6px 12px; border-radius: 6px; font-weight: 700; font-size: 0.78rem; cursor: pointer; display: flex; align-items: center; gap: 4px;"
                        :title="currentLang === 'en' ? 'Deposit Payment' : 'पेमेंट जमा करा'"
                      >
                        {{ t('admin_khata_btn_pay') }}
                      </button>
                      <button
                        type="button"
                        @click="sendKhataWhatsAppReminder(c)"
                        style="background: #25d366; color: white; border: none; padding: 6px 12px; border-radius: 6px; font-weight: 700; font-size: 0.78rem; cursor: pointer; display: flex; align-items: center; gap: 4px;"
                        :title="currentLang === 'en' ? 'Send WhatsApp Reminder' : 'WhatsApp वर स्मरणपत्र पाठवा'"
                      >
                        {{ t('admin_khata_btn_remind') }}
                      </button>
                      <button
                        type="button"
                        @click="openKhataStatement(c.customer_phone)"
                        style="background: #f1f5f9; color: #1e293b; border: 1px solid #cbd5e1; padding: 6px 10px; border-radius: 6px; font-weight: 700; font-size: 0.78rem; cursor: pointer;"
                        :title="currentLang === 'en' ? 'View Full Statement' : 'संपूर्ण खाते बही स्टेटमेंट पहा'"
                      >
                        {{ t('admin_khata_btn_statement') }}
                      </button>
                    </div>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>

          <!-- Mobile Khata Cards (Phone Screens <= 768px) -->
          <div class="admin-mobile-khata-list">
            <div v-if="filteredKhataList.length === 0" style="text-align: center; padding: 30px; color: var(--text-muted); background: white; border-radius: 12px; border: 1px dashed var(--border);">
              {{ khataLoading ? 'Loading ledger...' : 'Zero dues outstanding! All bills are settled. 🎉' }}
            </div>
            <div
              v-for="c in filteredKhataList"
              :key="'mob-khata-' + c.customer_phone"
              class="admin-mob-item-card"
            >
              <div class="admin-mob-card-head">
                <div>
                  <div class="admin-mob-name">{{ c.customer_name }}</div>
                  <div style="font-size: 0.74rem; color: var(--text-muted);" v-if="c.customer_address">📍 {{ c.customer_address }}</div>
                  <div style="font-size: 0.72rem; color: #64748b; margin-top: 2px;">
                    Last bill: {{ c.last_order_date }} • {{ c.unpaid_orders.length }} bills due
                  </div>
                </div>
                <div style="text-align: right;">
                  <span style="font-size: 0.72rem; color: #991b1b; font-weight: 700; display: block;">Net Due</span>
                  <strong style="color: #dc2626; font-size: 1.25rem; font-weight: 900;">
                    ₹{{ c.net_balance_due }}
                  </strong>
                </div>
              </div>

              <!-- Mobile Actions: 1-Tap Call, Pay, WhatsApp Reminder & Statement -->
              <div style="display: flex; gap: 8px; margin-top: 10px; flex-wrap: wrap;">
                <a
                  :href="'tel:' + c.customer_phone"
                  class="admin-action-btn"
                  style="flex: 1; min-width: 125px; background: #eff6ff; border-color: #bfdbfe; color: #1d4ed8; font-weight: 800; text-decoration: none; display: flex; align-items: center; justify-content: center; gap: 4px; padding: 8px;"
                  title="Call Customer"
                >
                  📞 {{ currentLang === 'en' ? 'Call' : 'कॉल' }} ({{ c.customer_phone }})
                </a>
                <button
                  type="button"
                  @click="openKhataPay(c)"
                  class="admin-action-btn"
                  style="background: #059669; color: white; border: none; font-weight: 800; padding: 8px 12px;"
                >
                  💰 {{ t('admin_khata_btn_pay') }}
                </button>
                <button
                  type="button"
                  @click="sendKhataWhatsAppReminder(c)"
                  class="admin-action-btn"
                  style="background: #25d366; color: white; border: none; font-weight: 800; padding: 8px 10px;"
                  title="WhatsApp Reminder"
                >
                  📲 {{ t('admin_khata_btn_remind') }}
                </button>
                <button
                  type="button"
                  @click="openKhataStatement(c.customer_phone)"
                  class="admin-action-btn"
                  style="background: #f1f5f9; color: #1e293b; border: 1px solid #cbd5e1; font-weight: 700; padding: 8px 10px;"
                  title="View Statement"
                >
                  📋
                </button>
              </div>
            </div>
          </div>
        </div>

        <!-- TAB 6: DUKANDAR DAILY Z-REPORT & CASH RECONCILER -->
        <div v-if="adminActiveTab === 'zreport'" style="margin-top: 14px;">
          <!-- Top Control Header: Date Selector & Actions -->
          <div style="background: white; border: 1.5px solid var(--border); border-radius: 12px; padding: 16px; display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 12px;">
            <div style="display: flex; align-items: center; gap: 10px; flex-wrap: wrap;">
              <span style="font-weight: 800; color: #064e3b; font-size: 0.95rem;">
                {{ currentLang === 'en' ? '📅 Select Date:' : (currentLang === 'mr' ? '📅 तारीख निवडा:' : '📅 तारीख चुनें:') }}
              </span>
              <input
                type="date"
                v-model="zReportDate"
                @change="loadDailyZReport"
                style="padding: 6px 12px; border: 1.5px solid #cbd5e1; border-radius: 8px; font-weight: 700; font-size: 0.9rem;"
              />
              <button
                type="button"
                @click="setZReportQuickDate(0)"
                style="padding: 6px 12px; background: #ecfdf5; border: 1px solid #a7f3d0; color: #065f46; border-radius: 8px; font-weight: 800; font-size: 0.82rem; cursor: pointer;"
              >
                {{ currentLang === 'en' ? 'Today' : 'आज (Today)' }}
              </button>
              <button
                type="button"
                @click="setZReportQuickDate(-1)"
                style="padding: 6px 12px; background: #f8fafc; border: 1px solid #cbd5e1; color: #475569; border-radius: 8px; font-weight: 800; font-size: 0.82rem; cursor: pointer;"
              >
                {{ currentLang === 'en' ? 'Yesterday' : (currentLang === 'mr' ? 'काल (Yesterday)' : 'कल (Yesterday)') }}
              </button>
            </div>

            <div style="display: flex; gap: 8px; flex-wrap: wrap;">
              <button
                type="button"
                @click="sendSundayWeeklyReportEmail"
                :disabled="sendingWeeklyEmail"
                style="background: #0284c7; color: white; border: none; padding: 8px 14px; border-radius: 8px; font-weight: 800; font-size: 0.84rem; cursor: pointer; display: flex; align-items: center; gap: 6px; box-shadow: 0 2px 6px rgba(2,132,199,0.3);"
              >
                <span v-if="sendingWeeklyEmail">⏳ {{ currentLang === 'en' ? 'Sending...' : 'पाठवत आहे...' }}</span>
                <span v-else>📧 {{ currentLang === 'en' ? 'Email Weekly Digest' : (currentLang === 'mr' ? 'साप्ताहिक अहवाल ईमेल पाठवा' : 'साप्ताहिक रिपोर्ट ईमेल भेजें') }}</span>
              </button>
              <button
                type="button"
                @click="shareDailyZReportWhatsApp"
                style="background: #25d366; color: white; border: none; padding: 8px 14px; border-radius: 8px; font-weight: 800; font-size: 0.84rem; cursor: pointer; display: flex; align-items: center; gap: 6px;"
              >
                {{ currentLang === 'en' ? '📲 WhatsApp Z-Report' : (currentLang === 'mr' ? '📲 WhatsApp हिशोब पाठवा' : '📲 WhatsApp हिसाब भेजें') }}
              </button>
              <button
                type="button"
                @click="downloadZReportPdf"
                style="background: #047857; color: white; border: none; padding: 8px 14px; border-radius: 8px; font-weight: 800; font-size: 0.84rem; cursor: pointer; display: flex; align-items: center; gap: 6px;"
              >
                {{ currentLang === 'en' ? '📥 Download PDF' : (currentLang === 'mr' ? '📥 PDF डाऊनलोड' : '📥 PDF डाउनलोड') }}
              </button>
              <button
                type="button"
                @click="printZReport"
                style="background: #1c1917; color: white; border: none; padding: 8px 14px; border-radius: 8px; font-weight: 800; font-size: 0.84rem; cursor: pointer; display: flex; align-items: center; gap: 6px;"
              >
                {{ currentLang === 'en' ? '🖨️ Print Report' : (currentLang === 'mr' ? '🖨️ प्रिंट करा' : '🖨️ प्रिंट करें') }}
              </button>
            </div>
          </div>

          <!-- Printable Z-Report Body (ERP-Grade Accounting Statement) -->
          <div id="printable-z-report" style="margin-top: 16px; background: white; border: 2px solid #064e3b; border-radius: 12px; padding: 24px; box-shadow: 0 4px 16px rgba(0,0,0,0.06); color: #0f172a; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;">
            <!-- Formal Wadala Shop Letterhead -->
            <div style="border-bottom: 2.5px solid #064e3b; padding-bottom: 14px; margin-bottom: 18px; display: flex; justify-content: space-between; align-items: flex-start; flex-wrap: wrap; gap: 12px;">
              <div>
                <h1 style="margin: 0; color: #064e3b; font-size: 1.55rem; font-weight: 900; letter-spacing: 0.5px;">
                  🌾 कोमल मार्ट (KOMAL MART)
                </h1>
                <div style="font-size: 0.86rem; font-weight: 700; color: #1e293b; margin-top: 3px;">
                  1st Floor, GRD 6, Vitthal Rukhmai CHS, B.B. Khandekar Marg, Nr. Ram Mandir, Wadala (W), Mumbai - 400031
                </div>
                <div style="font-size: 0.8rem; color: #475569; margin-top: 3px;">
                  <strong>GSTIN:</strong> 27ACOPU3896J1ZK • <strong>FSSAI:</strong> 11521003000327 • <strong>Phone:</strong> 9987602693 / 8369795519
                </div>
              </div>
              <div style="text-align: right;">
                <div style="background: #ecfdf5; border: 1.5px solid #059669; color: #064e3b; font-weight: 900; padding: 6px 14px; border-radius: 8px; font-size: 0.88rem; display: inline-block;">
                  KM-ZREP-{{ (zReportDate || '').replace(/-/g, '') }}
                </div>
                <div style="font-size: 0.84rem; font-weight: 800; color: #0f172a; margin-top: 5px;">
                  📅 तारीख: {{ zReport.formatted_date || zReportDate }}
                </div>
                <div style="font-size: 0.72rem; color: #64748b; margin-top: 2px;">
                  मुद्रण: {{ zReportCurrentPrintTime }}
                </div>
              </div>
            </div>

            <!-- SECTION 1: FINANCIAL LIQUIDITY POSITION (Cash & Bank Position) -->
            <div style="margin-bottom: 20px;">
              <div style="font-size: 0.95rem; font-weight: 900; color: #064e3b; margin-bottom: 8px; text-transform: uppercase; letter-spacing: 0.5px; border-left: 4px solid #059669; padding-left: 8px;">
                १. दैनिक रोख व डिजिटल जमा ताळेबंद (Liquidity Position)
              </div>
              <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(240px, 1fr)); gap: 12px;">
                <!-- 1. Physical Cash in Drawer -->
                <div style="background: #f8fafc; border: 1.5px solid #cbd5e1; border-radius: 8px; padding: 12px;">
                  <div style="font-size: 0.78rem; font-weight: 800; color: #166534; display: flex; align-items: center; gap: 5px;">
                    💵 प्रत्यक्ष रोख गल्ला (Cash in Drawer)
                  </div>
                  <div style="font-size: 1.6rem; font-weight: 900; color: #15803d; margin: 4px 0;">
                    ₹{{ zReport.total_cash_in_drawer }}
                  </div>
                  <div style="font-size: 0.75rem; color: #334155; border-top: 1px dashed #cbd5e1; padding-top: 4px; display: flex; flex-direction: column; gap: 2px;">
                    <div style="display: flex; justify-content: space-between;">
                      <span>रोख विक्री (Cash Orders):</span>
                      <strong>₹{{ zReport.cash_paid_amount }}</strong>
                    </div>
                    <div style="display: flex; justify-content: space-between;">
                      <span>उधारी वसुली रोख (Cash Khata):</span>
                      <strong>₹{{ zReport.khata_cash_recovered }}</strong>
                    </div>
                  </div>
                </div>

                <!-- 2. Bank UPI Settlements -->
                <div style="background: #f8fafc; border: 1.5px solid #cbd5e1; border-radius: 8px; padding: 12px;">
                  <div style="font-size: 0.78rem; font-weight: 800; color: #1e40af; display: flex; align-items: center; gap: 5px;">
                    📲 बँक जमा (UPI Soundbox Settlements)
                  </div>
                  <div style="font-size: 1.6rem; font-weight: 900; color: #1d4ed8; margin: 4px 0;">
                    ₹{{ zReport.total_upi_received }}
                  </div>
                  <div style="font-size: 0.75rem; color: #334155; border-top: 1px dashed #cbd5e1; padding-top: 4px; display: flex; flex-direction: column; gap: 2px;">
                    <div style="display: flex; justify-content: space-between;">
                      <span>ऑनलाइन UPI विक्री:</span>
                      <strong>₹{{ zReport.upi_paid_amount }}</strong>
                    </div>
                    <div style="display: flex; justify-content: space-between;">
                      <span>उधारी वसुली UPI:</span>
                      <strong>₹{{ zReport.khata_upi_recovered }}</strong>
                    </div>
                  </div>
                </div>

                <!-- 3. Total Liquid Collected -->
                <div style="background: #ecfdf5; border: 1.5px solid #059669; border-radius: 8px; padding: 12px;">
                  <div style="font-size: 0.78rem; font-weight: 800; color: #064e3b; display: flex; align-items: center; gap: 5px;">
                    ✨ एकूण प्रत्यक्ष रोख + बँक जमा (Total Liquid)
                  </div>
                  <div style="font-size: 1.6rem; font-weight: 900; color: #047857; margin: 4px 0;">
                    ₹{{ zReport.total_liquid_collected }}
                  </div>
                  <div style="font-size: 0.75rem; color: #065f46; border-top: 1px dashed #a7f3d0; padding-top: 4px; display: flex; flex-direction: column; gap: 2px;">
                    <div style="display: flex; justify-content: space-between;">
                      <span>रोख गल्ला + बँक जमा:</span>
                      <strong>₹{{ zReport.total_cash_in_drawer }} + ₹{{ zReport.total_upi_received }}</strong>
                    </div>
                    <div style="display: flex; justify-content: space-between;">
                      <span>वापरलेले स्टोअर क्रेडिट:</span>
                      <strong>₹{{ zReport.store_credit_redeemed }}</strong>
                    </div>
                  </div>
                </div>
              </div>
            </div>

            <!-- SECTION 2 & 3: SALES PERFORMANCE & KHATA LEDGER TABLES -->
            <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); gap: 14px; margin-bottom: 20px;">
              <!-- Sales Performance -->
              <div style="border: 1.5px solid #e2e8f0; border-radius: 8px; overflow: hidden;">
                <div style="background: #f1f5f9; padding: 8px 12px; font-weight: 800; font-size: 0.85rem; color: #1e293b; border-bottom: 1.5px solid #e2e8f0;">
                  🛒 २. विक्री व ऑर्डर कामगिरी (Sales Ledger)
                </div>
                <div style="padding: 10px 12px; display: flex; flex-direction: column; gap: 6px; font-size: 0.82rem;">
                  <div style="display: flex; justify-content: space-between;">
                    <span>एकूण ऑर्डर्स संख्या:</span>
                    <strong>{{ zReport.total_orders_count }} बिले</strong>
                  </div>
                  <div style="display: flex; justify-content: space-between;">
                    <span>निव्वळ विक्री रक्कम (Net Billed):</span>
                    <strong style="color: #047857; font-size: 0.95rem;">₹{{ zReport.net_sales }}</strong>
                  </div>
                  <div style="display: flex; justify-content: space-between; color: #64748b;">
                    <span>मूळ छापील एमआरपी बेरीज:</span>
                    <span>₹{{ zReport.gross_sales_mrp }}</span>
                  </div>
                  <div style="display: flex; justify-content: space-between; color: #059669;">
                    <span>ग्राहकांना दिलेली एकूण बचत (Discounts):</span>
                    <strong>- ₹{{ zReport.total_savings_given }}</strong>
                  </div>
                  <div style="display: flex; justify-content: space-between; border-top: 1px dashed #e2e8f0; padding-top: 4px;">
                    <span>सरासरी बिल मूल्य (AOV):</span>
                    <strong>₹{{ zReport.avg_basket_value }}</strong>
                  </div>
                </div>
              </div>

              <!-- Khata Movement -->
              <div style="border: 1.5px solid #fef08a; background: #fffdf5; border-radius: 8px; overflow: hidden;">
                <div style="background: #fef9c3; padding: 8px 12px; font-weight: 800; font-size: 0.85rem; color: #854d0e; border-bottom: 1.5px solid #fef08a;">
                  📒 ३. उधारी खतावणी हिशोब (Khata Udhaar Ledger)
                </div>
                <div style="padding: 10px 12px; display: flex; flex-direction: column; gap: 6px; font-size: 0.82rem;">
                  <div style="display: flex; justify-content: space-between; color: #dc2626;">
                    <span>आज दिलेली नवीन उधारी:</span>
                    <strong>+ ₹{{ zReport.khata_new_amount }} ({{ zReport.khata_new_count }} बिले)</strong>
                  </div>
                  <div style="display: flex; justify-content: space-between; color: #16a34a;">
                    <span>आज वसूल झालेली उधारी:</span>
                    <strong>- ₹{{ zReport.total_khata_recovered }}</strong>
                  </div>
                  <div style="display: flex; justify-content: space-between; border-top: 1px dashed #fef08a; padding-top: 6px; font-weight: 900; color: #991b1b; font-size: 0.92rem;">
                    <span>एकूण बाजार बाकी (Market Outstanding):</span>
                    <span>₹{{ zReport.total_market_udhaar }}</span>
                  </div>
                </div>
              </div>
            </div>

            <!-- SECTION 4: ITEMIZED TRANSACTIONS AUDIT TABLE -->
            <div style="margin-bottom: 22px;">
              <div style="font-size: 0.95rem; font-weight: 900; color: #064e3b; margin-bottom: 8px; text-transform: uppercase; letter-spacing: 0.5px; border-left: 4px solid #059669; padding-left: 8px;">
                ४. या दिवसाचे सर्व व्यवहार व ऑर्डर्स (Itemized Audit Register - {{ zReport.orders?.length || 0 }})
              </div>
              <div v-if="!zReport.orders || zReport.orders.length === 0" style="text-align: center; padding: 24px; color: #64748b; font-size: 0.85rem; background: #f8fafc; border-radius: 8px; border: 1px dashed #cbd5e1;">
                या तारखेला कोणतीही ऑर्डर नोंदवलेली नाही.
              </div>
              <div v-else style="overflow-x: auto; border: 1px solid #cbd5e1; border-radius: 8px;">
                <table style="width: 100%; border-collapse: collapse; font-size: 0.78rem; text-align: left;">
                  <thead>
                    <tr style="background: #f1f5f9; border-bottom: 1.5px solid #cbd5e1; color: #334155;">
                      <th style="padding: 8px 10px;">पर्चा क्र.</th>
                      <th style="padding: 8px 10px;">वेळ</th>
                      <th style="padding: 8px 10px;">ग्राहक व फोन</th>
                      <th style="padding: 8px 10px;">प्रकार</th>
                      <th style="padding: 8px 10px;">सामान तपशील</th>
                      <th style="padding: 8px 10px;">पेमेंट पद्धत</th>
                      <th style="padding: 8px 10px; text-align: right;">रक्कम</th>
                      <th style="padding: 8px 10px; text-align: center;">स्थिती</th>
                    </tr>
                  </thead>
                  <tbody>
                    <tr v-for="ord in zReport.orders" :key="ord.id" style="border-bottom: 1px solid #e2e8f0;">
                      <td style="padding: 7px 10px; font-weight: 800; color: #064e3b;">{{ ord.order_number }}</td>
                      <td style="padding: 7px 10px; color: #64748b; white-space: nowrap;">{{ ord.created_at }}</td>
                      <td style="padding: 7px 10px;">
                        <strong>{{ ord.customer_name }}</strong><br />
                        <span style="font-size: 0.7rem; color: #64748b;">{{ ord.customer_phone }}</span>
                      </td>
                      <td style="padding: 7px 10px;">
                        <span :style="ord.delivery_type === 'store_pickup' || ord.delivery_type === 'counter_pickup' ? 'background: #fef3c7; color: #92400e; padding: 2px 6px; border-radius: 4px; font-weight: 700;' : 'background: #eff6ff; color: #1d4ed8; padding: 2px 6px; border-radius: 4px; font-weight: 700;'">
                          {{ ord.delivery_type === 'store_pickup' || ord.delivery_type === 'counter_pickup' ? 'काऊंटर' : 'डिलिव्हरी' }}
                        </span>
                      </td>
                      <td style="padding: 7px 10px; color: #475569; max-width: 220px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap;" :title="ord.items.map(it => `${it.product_name} (${it.variant_label}) x${it.quantity}`).join(', ')">
                        {{ ord.items.map(it => `${it.product_name} (${it.variant_label}) x${it.quantity}`).join(', ') }}
                      </td>
                      <td style="padding: 7px 10px; font-weight: 600;">
                        {{ ord.payment_method }}
                        <span v-if="isUpiMethod(ord.payment_method)" style="color: #059669; font-weight: 800;">
                          (.{{ getSoundboxPaise(ord.final_amount) }})
                        </span>
                      </td>
                      <td style="padding: 7px 10px; text-align: right; font-weight: 900; color: #0f172a;">₹{{ ord.final_amount }}</td>
                      <td style="padding: 7px 10px; text-align: center;">
                        <span :style="ord.payment_status === 'Paid' ? 'background: #dcfce7; color: #166534; padding: 2px 6px; border-radius: 4px; font-weight: 800;' : 'background: #fee2e2; color: #991b1b; padding: 2px 6px; border-radius: 4px; font-weight: 800;'">
                          {{ ord.payment_status === 'Paid' ? 'चुकता' : 'बाकी' }}
                        </span>
                      </td>
                    </tr>
                  </tbody>
                </table>
              </div>
            </div>

            <!-- SECTION 5: FORMAL DUKANDAR AUDIT SIGNOFF BLOCK -->
            <div style="border-top: 2px dashed #94a3b8; padding-top: 18px; margin-top: 24px; display: flex; justify-content: space-between; align-items: flex-end; flex-wrap: wrap; gap: 16px;">
              <div style="text-align: center; width: 180px;">
                <div style="border-bottom: 1.5px solid #475569; height: 35px; margin-bottom: 6px;"></div>
                <div style="font-weight: 800; font-size: 0.8rem; color: #1e293b;">✍️ काऊंटर तपासनीस</div>
                <div style="font-size: 0.72rem; color: #64748b;">Cashier / Counter Clerk</div>
              </div>

              <div style="text-align: center; border: 2px solid #059669; border-radius: 8px; padding: 8px 16px; background: #f0fdf4;">
                <div style="font-size: 0.82rem; font-weight: 900; color: #064e3b; text-transform: uppercase;">
                  कोमल मार्ट अधिकृत तपासणी
                </div>
                <div style="font-size: 0.72rem; color: #047857; font-weight: 700;">
                  Verified Store Financial Audit • Wadala
                </div>
              </div>

              <div style="text-align: center; width: 180px;">
                <div style="border-bottom: 1.5px solid #475569; height: 35px; margin-bottom: 6px;"></div>
                <div style="font-weight: 800; font-size: 0.8rem; color: #1e293b;">✍️ मुख्य दुकान मालक</div>
                <div style="font-size: 0.72rem; color: #64748b;">Store Proprietor Signature</div>
              </div>
            </div>
          </div>
        </div>

        <!-- TAB 7: RESTOCK ALERTS & CUSTOMER DEMAND INTELLIGENCE -->
        <div v-if="adminActiveTab === 'restock'" style="margin-top: 14px;">
          <div style="background: white; border: 1.5px solid var(--border); border-radius: 12px; padding: 20px;">
            <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 12px; border-bottom: 1.5px solid var(--border); padding-bottom: 14px; margin-bottom: 18px;">
              <div>
                <h3 style="font-size: 1.25rem; font-weight: 900; color: #064e3b; margin: 0; display: flex; align-items: center; gap: 8px;">
                  🔔 {{ currentLang === 'en' ? 'Customer Restock Requests & Mandi Demand' : (currentLang === 'mr' ? 'ग्राहक मागणी व रिस्टॉक सूचना' : 'ग्राहक मांग व रिस्टॉक सूचनाएं') }}
                </h3>
                <p style="font-size: 0.85rem; color: var(--text-muted); margin: 4px 0 0 0;">
                  {{ currentLang === 'en' ? 'Customers waiting for out-of-stock items. When you restock in Price Editor, notifications trigger automatically.' : (currentLang === 'mr' ? 'स्टॉक संपलेल्या सामानासाठी ग्राहकांची मागणी. तुम्ही प्राईस एडिटरमध्ये स्टॉक वाढवताच ग्राहकांना सूचना मिळते.' : 'स्टॉक समाप्त सामान के लिए ग्राहकों की मांग। जैसे ही आप स्टॉक बढ़ाते हैं, ग्राहकों को अलर्ट चला जाता है।') }}
                </p>
              </div>
              <div style="display: flex; gap: 10px; align-items: center;">
                <span class="tab-badge-warning" style="padding: 6px 12px; font-size: 0.88rem; font-weight: 800;">
                  {{ pendingRestockCount }} {{ currentLang === 'en' ? 'Pending Alerts' : (currentLang === 'mr' ? 'प्रलंबित मागण्या' : 'लंबित मांग') }}
                </span>
                <button
                  type="button"
                  @click="loadRestockAlerts"
                  class="btn-secondary"
                  style="padding: 8px 14px; font-size: 0.84rem; font-weight: 700; border-radius: 8px; cursor: pointer;"
                >
                  🔄 {{ currentLang === 'en' ? 'Refresh' : 'रीफ्रेश' }}
                </button>
              </div>
            </div>

            <!-- Empty State -->
            <div v-if="restockAlertsList.length === 0" style="text-align: center; padding: 40px 20px; color: var(--text-muted);">
              <div style="font-size: 2.5rem; margin-bottom: 10px;">✨</div>
              <div style="font-weight: 800; font-size: 1.1rem; color: #334155;">
                {{ currentLang === 'en' ? 'No pending restock requests!' : (currentLang === 'mr' ? 'सध्या कोणतीही प्रलंबित रिस्टॉक मागणी नाही!' : 'फ़िलहाल कोई लंबित रिस्टॉक मांग नहीं है!') }}
              </div>
              <div style="font-size: 0.85rem; margin-top: 4px;">
                {{ currentLang === 'en' ? 'All products are currently adequately stocked or waiting customer alerts will appear here.' : (currentLang === 'mr' ? 'सर्व उत्पादने पुरेशा प्रमाणात उपलब्ध आहेत किंवा ग्राहकांची मागणी येथे दिसेल.' : 'सभी उत्पाद पर्याप्त स्टॉक में हैं या ग्राहकों की मांग यहाँ दिखेगी।') }}
              </div>
            </div>

            <!-- Table -->
            <div v-else class="orders-table-wrapper" style="overflow-x: auto;">
              <table class="admin-orders-table" style="width: 100%; border-collapse: collapse;">
                <thead>
                  <tr style="background: #f8fafc; border-bottom: 2px solid #e2e8f0; text-align: left; font-size: 0.82rem; color: #475569;">
                    <th style="padding: 12px 14px;">{{ currentLang === 'en' ? 'Customer' : (currentLang === 'mr' ? 'ग्राहक' : 'ग्राहक') }}</th>
                    <th style="padding: 12px 14px;">{{ currentLang === 'en' ? 'Phone' : (currentLang === 'mr' ? 'मोबाईल' : 'मोबाइल') }}</th>
                    <th style="padding: 12px 14px;">{{ currentLang === 'en' ? 'Product Requested' : (currentLang === 'mr' ? 'मागितलेले सामान' : 'मांगा गया सामान') }}</th>
                    <th style="padding: 12px 14px;">{{ currentLang === 'en' ? 'Pack / Size' : (currentLang === 'mr' ? 'वजन / पॅक' : 'वजन / पैक') }}</th>
                    <th style="padding: 12px 14px;">{{ currentLang === 'en' ? 'Requested On' : (currentLang === 'mr' ? 'नोंदवलेली तारीख' : 'दर्ज तारीख') }}</th>
                    <th style="padding: 12px 14px;">{{ currentLang === 'en' ? 'Status' : (currentLang === 'mr' ? 'स्थिती' : 'स्थिति') }}</th>
                    <th style="padding: 12px 14px; text-align: center;">{{ currentLang === 'en' ? 'Action' : (currentLang === 'mr' ? 'कृती' : 'कार्रवाई') }}</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="alert in restockAlertsList" :key="alert.id" style="border-bottom: 1px solid #f1f5f9; font-size: 0.88rem;">
                    <td style="padding: 12px 14px; font-weight: 800; color: #1e293b;">{{ alert.customer_name }}</td>
                    <td style="padding: 12px 14px; font-weight: 700; color: #065f46;">📞 {{ alert.customer_phone }}</td>
                    <td style="padding: 12px 14px; font-weight: 700;">{{ alert.product_name }}</td>
                    <td style="padding: 12px 14px;">
                      <span v-if="alert.variant_label" style="background: #f1f5f9; padding: 2px 8px; border-radius: 6px; font-weight: 700; font-size: 0.8rem;">
                        {{ alert.variant_label }}
                      </span>
                      <span v-else style="color: #64748b;">-</span>
                    </td>
                    <td style="padding: 12px 14px; color: #64748b; font-size: 0.82rem;">{{ alert.created_at }}</td>
                    <td style="padding: 12px 14px;">
                      <span v-if="alert.is_notified" style="background: #dcfce7; color: #15803d; padding: 4px 8px; border-radius: 6px; font-weight: 800; font-size: 0.78rem;">
                        ✅ {{ currentLang === 'en' ? 'Restocked & Notified' : (currentLang === 'mr' ? 'कळवले आहे' : 'सूचित किया गया') }}
                      </span>
                      <span v-else style="background: #fef3c7; color: #92400e; padding: 4px 8px; border-radius: 6px; font-weight: 800; font-size: 0.78rem;">
                        ⏳ {{ currentLang === 'en' ? 'Waiting / Pending' : (currentLang === 'mr' ? 'प्रलंबित' : 'प्रतीक्षारत') }}
                      </span>
                    </td>
                    <td style="padding: 12px 14px; text-align: center;">
                      <a
                        :href="`https://wa.me/91${alert.customer_phone}?text=${encodeURIComponent(`नमस्ते ${alert.customer_name}! कोमल मार्ट (Komal Mart) वर तुम्ही विचारलेले सामान '${alert.product_name}' आता उपलब्ध आहे. लगेच ऑर्डर करण्यासाठी संपर्क करा.`)}`"
                        target="_blank"
                        style="background: #25d366; color: white; text-decoration: none; padding: 6px 10px; border-radius: 6px; font-weight: 800; font-size: 0.78rem; display: inline-flex; align-items: center; gap: 4px;"
                      >
                        📲 WhatsApp
                      </a>
                    </td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>
        </div>

        <!-- TAB 8: CUSTOMER COMPLAINTS & FEEDBACK TICKETS -->
        <div v-if="adminActiveTab === 'support'" style="margin-top: 14px;">
          <div style="background: white; border: 1.5px solid var(--border); border-radius: 12px; padding: 20px;">
            <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 12px; border-bottom: 1.5px solid var(--border); padding-bottom: 14px; margin-bottom: 18px;">
              <div>
                <h3 style="font-size: 1.25rem; font-weight: 900; color: #064e3b; margin: 0; display: flex; align-items: center; gap: 8px;">
                  💬 {{ currentLang === 'en' ? 'Customer Complaints & Feedback Center' : (currentLang === 'mr' ? 'ग्राहक तक्रार व अभिप्राय निवारण केंद्र' : 'ग्राहक शिकायत व सुझाव निवारण केंद्र') }}
                </h3>
                <p style="font-size: 0.85rem; color: var(--text-muted); margin: 4px 0 0 0;">
                  {{ currentLang === 'en' ? 'Review and resolve incoming customer complaints, feedback, and delivery issues.' : (currentLang === 'mr' ? 'ग्राहकांच्या तक्रारी व सूचना तपासा, ग्राहकांशी त्वरित संपर्क करा व समस्या सोडवा.' : 'ग्राहकों की शिकायतें व सुझाव देखें, तुरंत संपर्क करें और समाधान करें।') }}
                </p>
              </div>
              <div style="display: flex; gap: 10px; align-items: center;">
                <span v-if="adminOpenComplaintsCount > 0" class="tab-badge-danger" style="padding: 6px 12px; font-size: 0.88rem; font-weight: 800;">
                  🚨 {{ adminOpenComplaintsCount }} {{ currentLang === 'en' ? 'Urgent Complaints' : (currentLang === 'mr' ? 'तातडीच्या तक्रारी' : 'गंभीर शिकायतें') }}
                </span>
                <button
                  type="button"
                  @click="loadAdminSupportTickets"
                  class="btn-secondary"
                  style="padding: 8px 14px; font-size: 0.84rem; font-weight: 700; border-radius: 8px; cursor: pointer;"
                >
                  🔄 {{ currentLang === 'en' ? 'Refresh' : 'रीफ्रेश' }}
                </button>
              </div>
            </div>

            <!-- Filter Segmented Tabs -->
            <div style="display: flex; gap: 8px; margin-bottom: 16px; overflow-x: auto; padding-bottom: 4px;">
              <button
                type="button"
                class="account-tab-btn"
                :class="{ active: adminSupportFilter === 'all' }"
                @click="adminSupportFilter = 'all'"
              >
                {{ currentLang === 'en' ? 'All Tickets' : (currentLang === 'mr' ? 'सर्व नोंदी' : 'सभी रिकॉर्ड') }} ({{ adminSupportTickets.length }})
              </button>
              <button
                type="button"
                class="account-tab-btn"
                :class="{ active: adminSupportFilter === 'complaint' }"
                @click="adminSupportFilter = 'complaint'"
              >
                🚨 {{ currentLang === 'en' ? 'Complaints Only' : (currentLang === 'mr' ? 'फक्त तक्रारी' : 'केवल शिकायतें') }}
              </button>
              <button
                type="button"
                class="account-tab-btn"
                :class="{ active: adminSupportFilter === 'feedback' }"
                @click="adminSupportFilter = 'feedback'"
              >
                💡 {{ currentLang === 'en' ? 'Feedback Only' : (currentLang === 'mr' ? 'फक्त अभिप्राय' : 'केवल सुझाव') }}
              </button>
              <button
                type="button"
                class="account-tab-btn"
                :class="{ active: adminSupportFilter === 'open' }"
                @click="adminSupportFilter = 'open'"
              >
                ⏳ {{ currentLang === 'en' ? 'Pending Open' : (currentLang === 'mr' ? 'पेंडिंग (Open)' : 'लंबित (Open)') }}
              </button>
            </div>

            <!-- Empty State -->
            <div v-if="filteredAdminSupportTickets.length === 0" style="text-align: center; padding: 40px 20px; color: var(--text-muted);">
              <div style="font-size: 2.5rem; margin-bottom: 10px;">✨</div>
              <div style="font-weight: 800; font-size: 1.1rem; color: #334155;">
                {{ currentLang === 'en' ? 'No tickets match the selected filter!' : (currentLang === 'mr' ? 'निवडलेल्या फिल्टरनुसार कोणतीही नोंद नाही.' : 'चुने गए फ़िल्टर के अनुसार कोई रिकॉर्ड नहीं है।') }}
              </div>
            </div>

            <!-- Tickets List -->
            <div v-else style="display: flex; flex-direction: column; gap: 14px;">
              <div
                v-for="tkt in filteredAdminSupportTickets"
                :key="tkt.id"
                style="border: 1.5px solid #e2e8f0; border-radius: 10px; padding: 16px; background: #ffffff; box-shadow: 0 1px 4px rgba(0,0,0,0.04);"
                :style="tkt.ticket_type === 'complaint' && tkt.status === 'Open' ? 'border-left: 5px solid #dc2626;' : ''"
              >
                <div style="display: flex; justify-content: space-between; align-items: flex-start; flex-wrap: wrap; gap: 10px; margin-bottom: 10px;">
                  <div>
                    <div style="display: flex; align-items: center; gap: 8px;">
                      <span style="font-size: 1.1rem;">{{ tkt.ticket_type === 'complaint' ? '🚨' : '💡' }}</span>
                      <strong style="font-size: 1rem; color: #0f172a;">#{{ tkt.ticket_number }}</strong>
                      <span
                        class="ticket-badge"
                        :class="{
                          'ticket-badge-open': tkt.status === 'Open',
                          'ticket-badge-in-review': tkt.status === 'In Review',
                          'ticket-badge-resolved': tkt.status === 'Resolved'
                        }"
                      >
                        {{ tkt.status }}
                      </span>
                    </div>
                    <div style="font-size: 0.78rem; color: var(--text-subtle); margin-top: 2px;">
                      {{ tkt.created_at }}
                      <span v-if="tkt.order_number" style="margin-left: 8px; font-weight: 700; color: #0284c7;">
                        • {{ currentLang === 'en' ? 'Order' : 'ऑर्डर' }} #{{ tkt.order_number }}
                      </span>
                    </div>
                  </div>

                  <!-- Customer Contact Quick Actions -->
                  <div style="display: flex; gap: 8px; align-items: center; flex-wrap: wrap;">
                    <a
                      :href="'tel:' + tkt.customer_phone"
                      class="phone-call-pill"
                      style="text-decoration: none;"
                      title="Call customer"
                    >
                      📞 {{ tkt.customer_phone }} ({{ tkt.customer_name }})
                    </a>
                    <a
                      :href="'https://wa.me/91' + tkt.customer_phone.replace(/\D/g, '') + '?text=' + encodeURIComponent('नमस्ते ' + tkt.customer_name + ', कोमल मार्टकडून आपल्या तक्रार/अभिप्राय #' + tkt.ticket_number + ' संदर्भात:')"
                      target="_blank"
                      style="display: inline-flex; align-items: center; gap: 4px; background: #16a34a; color: white; padding: 4px 10px; border-radius: 20px; font-size: 0.78rem; font-weight: 700; text-decoration: none;"
                    >
                      💬 WhatsApp
                    </a>
                  </div>
                </div>

                <!-- Category & Message -->
                <div style="background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 8px; padding: 12px; margin-bottom: 12px;">
                  <div style="font-size: 0.8rem; font-weight: 800; color: #475569; margin-bottom: 4px;">
                    {{ currentLang === 'en' ? 'Category:' : 'प्रवर्ग:' }} {{ tkt.category }}
                  </div>
                  <div style="font-size: 0.88rem; color: #1e293b; line-height: 1.5; white-space: pre-wrap;">
                    {{ tkt.message }}
                  </div>
                </div>

                <!-- Admin Status Update & Notes inline form -->
                <div style="display: flex; gap: 10px; align-items: center; flex-wrap: wrap; background: #f1f5f9; padding: 10px 12px; border-radius: 8px;">
                  <div style="display: flex; align-items: center; gap: 6px;">
                    <label style="font-size: 0.8rem; font-weight: 700; color: #334155;">{{ currentLang === 'en' ? 'Status:' : 'स्थिती:' }}</label>
                    <select
                      v-model="tkt.status"
                      style="padding: 4px 8px; border-radius: 6px; border: 1px solid #cbd5e1; font-size: 0.8rem; font-weight: 700;"
                    >
                      <option value="Open">Open (पेंडिंग)</option>
                      <option value="In Review">In Review (तपासणी सुरू)</option>
                      <option value="Resolved">Resolved (निवारण झाले)</option>
                    </select>
                  </div>
                  <div style="flex: 1; min-width: 200px;">
                    <input
                      type="text"
                      v-model="tkt.admin_notes"
                      :placeholder="currentLang === 'en' ? 'Resolution note / explanation to customer...' : 'निवारण टीप / उत्तर...'"
                      style="width: 100%; padding: 5px 10px; border-radius: 6px; border: 1px solid #cbd5e1; font-size: 0.8rem;"
                    />
                  </div>
                  <button
                    type="button"
                    @click="updateTicketByAdmin(tkt)"
                    style="background: #064e3b; color: white; border: none; padding: 6px 14px; border-radius: 6px; font-size: 0.8rem; font-weight: 700; cursor: pointer;"
                  >
                    💾 {{ currentLang === 'en' ? 'Save Status' : 'जतन करा' }}
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- TAB 9: HYPERLOCAL DELIVERY ZONES & EMERGENCY HOLD CONTROLLER -->
        <div v-if="adminActiveTab === 'zones'" style="margin-top: 14px;">
          <div style="background: white; border: 1.5px solid var(--border); border-radius: 12px; padding: 20px;">
            <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 12px; border-bottom: 1.5px solid var(--border); padding-bottom: 14px; margin-bottom: 18px;">
              <div>
                <h3 style="font-size: 1.25rem; font-weight: 900; color: #064e3b; margin: 0; display: flex; align-items: center; gap: 8px;">
                  🛵 {{ currentLang === 'en' ? 'Hyperlocal Delivery Zones & Area Hold Controller' : (currentLang === 'mr' ? 'परिसर डिलिव्हरी व तात्पुरती होल्ड नियंत्रण' : 'क्षेत्रीय डिलीवरी व अस्थायी होल्ड नियंत्रण') }}
                </h3>
                <p style="font-size: 0.85rem; color: var(--text-muted); margin: 4px 0 0 0;">
                  {{ currentLang === 'en' 
                    ? 'If a delivery rider is absent or weather/distance issues occur, place specific areas on temporary hold. Customers can still place orders safely (notified that delivery will occur tomorrow).'
                    : (currentLang === 'mr'
                      ? 'डिलिव्हरी बॉय गैरहजर असल्यास किंवा दूरच्या भागात अडचण आल्यास संबंधित परिसर होल्डवर ठेवा. ग्राहक ऑर्डर नोंदवू शकतील, पण त्यांना उद्या डिलिव्हरी होईल असा स्पष्ट निरोप दिसेल.'
                      : 'यदि डिलीवरी बॉय अनुपस्थित है या किसी दूर के क्षेत्र में समस्या है, तो उस क्षेत्र को होल्ड पर रखें। ग्राहक ऑर्डर दे सकेंगे लेकिन उन्हें कल डिलीवरी की सूचना मिलेगी।') }}
                </p>
              </div>
              <button
                type="button"
                @click="fetchAreaDeliveryHolds"
                class="btn-secondary"
                style="padding: 8px 14px; font-size: 0.84rem; font-weight: 700; border-radius: 8px; cursor: pointer;"
              >
                🔄 {{ currentLang === 'en' ? 'Refresh Status' : 'रीफ्रेश' }}
              </button>
            </div>

            <!-- Areas Grid -->
            <div style="display: grid; grid-template-columns: repeat(auto-fill, minmax(320px, 1fr)); gap: 16px;">
              <div
                v-for="area in WADALA_SERVICEABLE_AREAS"
                :key="area.pincode"
                style="border: 2px solid; border-radius: 12px; padding: 16px; background: #ffffff; transition: all 0.2s;"
                :style="areaDeliveryHolds[area.pincode]?.is_held 
                  ? 'border-color: #f59e0b; background: #fffdf5;' 
                  : 'border-color: #10b981; background: #f0fdf4;'"
              >
                <div style="display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 10px;">
                  <div>
                    <span style="font-size: 0.78rem; font-weight: 900; padding: 2px 8px; border-radius: 4px;"
                      :style="areaDeliveryHolds[area.pincode]?.is_held ? 'background: #fef3c7; color: #b45309;' : 'background: #d1fae5; color: #065f46;'"
                    >
                      PIN: {{ area.pincode }}
                    </span>
                    <h4 style="margin: 6px 0 0 0; font-size: 0.98rem; font-weight: 800; color: #1e293b;">
                      {{ currentLang === 'en' ? area.name_en : (currentLang === 'mr' ? area.name_mr : area.name_hi) }}
                    </h4>
                  </div>
                  <span style="font-size: 1.4rem;">
                    {{ areaDeliveryHolds[area.pincode]?.is_held ? '⏳' : '🟢' }}
                  </span>
                </div>

                <!-- Status indicator -->
                <div style="font-size: 0.82rem; margin-bottom: 12px;">
                  <strong :style="areaDeliveryHolds[area.pincode]?.is_held ? 'color: #b45309;' : 'color: #047857;'">
                    {{ areaDeliveryHolds[area.pincode]?.is_held 
                      ? '⚠️ डिलिव्हरी तात्पुरती पुढील वेळेसाठी राखीव (Held)' 
                      : '✅ सुरळीत डिलिव्हरी सुरू (Normal Active)' }}
                  </strong>
                  <div v-if="areaDeliveryHolds[area.pincode]?.is_held" style="font-size: 0.76rem; color: #78350f; margin-top: 4px;">
                    पुन्हा सुरू होण्याची वेळ: <strong>{{ areaDeliveryHolds[area.pincode]?.resume || 'उद्या सकाळपर्यंत' }}</strong>
                  </div>
                </div>

                <!-- 1-Click Action Button -->
                <div style="display: flex; gap: 8px;">
                  <button
                    v-if="!areaDeliveryHolds[area.pincode]?.is_held"
                    type="button"
                    :disabled="isAreaHoldToggling"
                    @click="toggleAdminAreaHold(area.pincode, true, 'डिलिव्हरी बॉय गैरहजर असल्याने तात्पुरती डिलिव्हरी थांबवली आहे.')"
                    style="flex: 1; background: #fffbeb; border: 1.5px solid #d97706; color: #b45309; padding: 8px 12px; border-radius: 8px; font-weight: 800; font-size: 0.82rem; cursor: pointer;"
                  >
                    ⏸️ डिलिव्हरी तात्पुरती होल्ड करा
                  </button>
                  <button
                    v-else
                    type="button"
                    :disabled="isAreaHoldToggling"
                    @click="toggleAdminAreaHold(area.pincode, false)"
                    style="flex: 1; background: #059669; border: 1.5px solid #059669; color: white; padding: 8px 12px; border-radius: 8px; font-weight: 800; font-size: 0.82rem; cursor: pointer;"
                  >
                    ▶️ डिलिव्हरी पुन्हा पूर्ववत करा (Resume)
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>

    <!-- ======================================================== -->
    <!-- CUSTOMER PAST BILLS & PURCHASE HISTORY MODAL            -->
    <!-- ======================================================== -->
    <div class="audit-modal-backdrop" v-if="activeAuditedCustomer" @click.self="activeAuditedCustomer = null">
      <div class="audit-modal-content">
        <div style="display: flex; justify-content: space-between; align-items: center; border-bottom: 2px solid var(--border); padding-bottom: 12px;">
          <div>
            <h3 style="font-size: 1.3rem; font-weight: 900; color: #064e3b; margin: 0; display: flex; align-items: center; gap: 8px;">
              👥 {{ activeAuditedCustomer.name }} — {{ currentLang === 'en' ? 'Purchase History & Past Bills' : (currentLang === 'mr' ? 'खरेदी इतिहास व जुनी बिले' : 'खरीदारी इतिहास व पुराने बिल') }}
            </h3>
            <div style="font-size: 0.84rem; color: var(--text-muted); margin-top: 4px;">
              <a :href="'tel:' + activeAuditedCustomer.phone" class="phone-call-pill" title="Click to call customer">📞 {{ activeAuditedCustomer.phone }}</a> | ✉️ {{ activeAuditedCustomer.email || (currentLang === 'en' ? 'No email registered' : (currentLang === 'mr' ? 'ईमेल नोंदवलेला नाही' : 'ईमेल दर्ज नहीं')) }} | 📍 {{ activeAuditedCustomer.address || (currentLang === 'en' ? 'No address registered' : (currentLang === 'mr' ? 'पत्ता नोंदवलेला नाही' : 'पता दर्ज नहीं')) }}
            </div>
          </div>
          <button class="close-btn" @click="activeAuditedCustomer = null">✕</button>
        </div>

        <!-- Khata Alert & WhatsApp Button -->
        <div style="margin-top: 16px; padding: 14px 18px; border-radius: 10px; display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 10px;"
          :style="activeAuditedCustomer.unpaid_balance > 0 ? 'background: #fef2f2; border: 1.5px solid #fecaca;' : 'background: #f0fdf4; border: 1.5px solid #bbf7d0;'">
          <div>
            <div style="font-size: 0.84rem; font-weight: 800;" :style="activeAuditedCustomer.unpaid_balance > 0 ? 'color: #991b1b;' : 'color: #166534;'">
              {{ activeAuditedCustomer.unpaid_balance > 0 ? (currentLang === 'en' ? '⚠️ Current Outstanding Khata Dues:' : (currentLang === 'mr' ? '⚠️ चालू बाकी उधारी रक्कम:' : '⚠️ चालू बकाया उधारी रकम:')) : (currentLang === 'en' ? '✅ All Bills Settled:' : (currentLang === 'mr' ? '✅ सर्व रकमा पूर्ण चुकता आहेत:' : '✅ सभी बिल चुकता हैं:')) }}
            </div>
            <div style="font-size: 1.5rem; font-weight: 900; margin-top: 2px;" :style="activeAuditedCustomer.unpaid_balance > 0 ? 'color: #dc2626;' : 'color: #15803d;'">
              ₹{{ activeAuditedCustomer.unpaid_balance }}
            </div>
          </div>

          <div style="display: flex; gap: 8px;">
            <button
              v-if="activeAuditedCustomer.unpaid_balance > 0"
              type="button"
              @click="sendKhataReminderWhatsApp(activeAuditedCustomer)"
              class="pos-btn-whatsapp"
              style="padding: 8px 14px; font-size: 0.85rem;"
            >
              📲 {{ currentLang === 'en' ? 'Send Udhaar Reminder' : (currentLang === 'mr' ? 'उधारी रिमाइंडर पाठवा' : 'उधारी रिमाइंडर भेजें') }}
            </button>
          </div>
        </div>

        <!-- Orders Timeline & Proof -->
        <div style="margin-top: 20px;">
          <h4 style="font-size: 1rem; font-weight: 800; color: var(--text-main); margin-bottom: 10px;">
            📦 {{ currentLang === 'en' ? 'Customer Purchase Order History' : (currentLang === 'mr' ? 'खरेदी केलेल्या सर्व ऑर्डर्सचा इतिहास' : 'खरीदे गए सभी ऑर्डर का इतिहास') }} ({{ activeAuditedCustomer.orders.length }})
          </h4>

          <div v-if="activeAuditedCustomer.orders.length === 0" style="padding: 20px; text-align: center; color: var(--text-muted);">
            {{ currentLang === 'en' ? 'This customer has not placed any orders yet.' : (currentLang === 'mr' ? 'या ग्राहकाने अद्याप कोणतीही ऑर्डर केलेली नाही.' : 'इस ग्राहक ने अभी तक कोई ऑर्डर नहीं किया है।') }}
          </div>

          <div v-else style="display: flex; flex-direction: column; gap: 12px;">
            <div
              v-for="ord in activeAuditedCustomer.orders"
              :key="ord.id"
              style="border: 1.5px solid var(--border); border-radius: 10px; padding: 14px; background: #f8fafc;"
            >
              <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 8px;">
                <div>
                  <span style="font-weight: 800; color: #064e3b; font-size: 0.95rem;">
                    📄 {{ ord.order_number }}
                  </span>
                  <span style="margin-left: 10px; font-size: 0.8rem; color: var(--text-muted);">
                    📅 {{ ord.created_at }}
                  </span>
                </div>

                <div style="display: flex; align-items: center; gap: 8px; flex-wrap: wrap;">
                  <!-- Status Select -->
                  <select
                    v-model="ord.status"
                    @change="updateAdminOrderStatus(ord)"
                    style="padding: 4px 8px; border-radius: 6px; border: 1px solid var(--border); font-weight: 700; font-size: 0.8rem;"
                  >
                    <option value="Placed">{{ currentLang === 'en' ? 'Placed' : (currentLang === 'mr' ? 'Placed (नोंदवली)' : 'Placed (ऑर्डर दर्ज)') }}</option>
                    <option value="Packed">{{ currentLang === 'en' ? 'Packed' : (currentLang === 'mr' ? 'Packed (पॅक)' : 'Packed (पैक तैयार)') }}</option>
                    <option value="Out for Delivery">{{ currentLang === 'en' ? 'Out for Delivery' : (currentLang === 'mr' ? 'Out for Delivery (निघाले)' : 'Out for Delivery (रास्ते में)') }}</option>
                    <option value="Delivered">{{ currentLang === 'en' ? 'Delivered' : (currentLang === 'mr' ? 'Delivered (दिले)' : 'Delivered (सफलतापूर्वक दिया)') }}</option>
                  </select>

                  <!-- Payment Status Select -->
                  <select
                    v-model="ord.payment_status"
                    @change="updateAdminOrderStatus(ord)"
                    style="padding: 4px 8px; border-radius: 6px; border: 1px solid var(--border); font-weight: 800; font-size: 0.8rem;"
                    :style="ord.payment_status === 'Paid' ? 'color: #14532d; background: #dcfce7;' : 'color: #991b1b; background: #fee2e2;'"
                  >
                    <option value="Paid">{{ currentLang === 'en' ? '🟢 Paid' : (currentLang === 'mr' ? '🟢 चुकता (Paid)' : '🟢 चुकता (Paid)') }}</option>
                    <option value="Unpaid">{{ currentLang === 'en' ? '🔴 Unpaid Khata' : (currentLang === 'mr' ? '🔴 बाकी उधारी (Unpaid)' : '🔴 बाकी उधारी (Unpaid)') }}</option>
                  </select>

                  <button
                    v-if="ord.payment_status !== 'Paid'"
                    @click="markOrderAsPaid(ord); activeAuditedCustomer.unpaid_balance = Math.max(0, activeAuditedCustomer.unpaid_balance - ord.final_amount);"
                    class="admin-mark-paid-btn"
                    style="padding: 4px 10px; font-size: 0.78rem;"
                  >
                    ✅ {{ currentLang === 'en' ? 'Mark Cash Paid' : (currentLang === 'mr' ? 'रोख मिळाली' : 'नकद मिला') }}
                  </button>

                  <strong style="font-size: 1.1rem; color: #1c1917; margin-left: 6px;">
                    ₹{{ ord.final_amount }}
                  </strong>
                </div>
              </div>

              <!-- Itemized List Proof -->
              <div style="margin-top: 10px; background: white; padding: 8px 12px; border-radius: 6px; border: 1px solid var(--border); font-size: 0.82rem;">
                <strong>{{ currentLang === 'en' ? 'Item Details:' : (currentLang === 'mr' ? 'सामान तपशील:' : 'सामग्री विवरण:') }}</strong>
                <span v-for="(it, idx) in ord.items" :key="idx" style="margin-left: 6px; color: var(--text-muted);">
                  {{ it.product_name }} ({{ it.variant_label }}) × {{ it.quantity }} = ₹{{ it.subtotal }}{{ idx < ord.items.length - 1 ? ' | ' : '' }}
                </span>
              </div>

              <!-- Action button: View receipt / WhatsApp -->
              <div style="margin-top: 10px; display: flex; gap: 8px;">
                <button
                  type="button"
                  @click="viewOrderReceipt(ord)"
                  class="admin-action-btn view-bill-btn"
                  style="font-size: 0.78rem; padding: 4px 10px;"
                >
                  🧾 {{ t('admin_view_bill') }}
                </button>
                <button
                  type="button"
                  @click="shareOrderOnWhatsApp(ord)"
                  class="admin-action-btn whatsapp-bill-btn"
                  style="font-size: 0.78rem; padding: 4px 10px;"
                >
                  📲 {{ t('admin_whatsapp_direct') }}
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- KHATA RECORD PAYMENT MODAL -->
    <div class="audit-modal-backdrop" v-if="showKhataPayModal" @click.self="showKhataPayModal = false">
      <div class="modal-card" style="max-width: 480px; width: 95%;">
        <div style="display: flex; justify-content: space-between; align-items: center; border-bottom: 2px solid var(--border); padding-bottom: 10px; margin-bottom: 16px;">
          <h3 style="font-size: 1.25rem; font-weight: 900; color: #064e3b; margin: 0; display: flex; align-items: center; gap: 8px;">
            💰 {{ currentLang === 'en' ? 'Deposit Khata Repayment' : (currentLang === 'mr' ? 'उधारी रक्कम जमा करा' : 'उधारी रकम जमा करें') }}
          </h3>
          <button class="close-btn" @click="showKhataPayModal = false">✕</button>
        </div>

        <div v-if="activeKhataCustomer" style="background: #fef2f2; border: 1.5px solid #fecaca; border-radius: 10px; padding: 12px 16px; margin-bottom: 16px;">
          <div style="display: flex; justify-content: space-between; align-items: center;">
            <div>
              <strong>{{ activeKhataCustomer.customer_name }}</strong>
              <div style="font-size: 0.8rem; color: #64748b;">📞 {{ activeKhataCustomer.customer_phone }}</div>
            </div>
            <div style="text-align: right;">
              <span style="font-size: 0.75rem; color: #991b1b; font-weight: 700;">{{ currentLang === 'en' ? 'Net Due Balance:' : (currentLang === 'mr' ? 'एकूण येणे बाकी:' : 'कुल बकाया:') }}</span>
              <div style="font-size: 1.25rem; font-weight: 900; color: #dc2626;">₹{{ activeKhataCustomer.net_balance_due }}</div>
            </div>
          </div>
        </div>

        <form @submit.prevent="submitKhataPayment">
          <div style="margin-bottom: 14px;">
            <label style="display: block; font-weight: 700; font-size: 0.88rem; margin-bottom: 6px;">
              {{ currentLang === 'en' ? 'Amount to Deposit (₹) *' : (currentLang === 'mr' ? 'जमा करावयाची रक्कम (₹) *' : 'जमा करने की रकम (₹) *') }}
            </label>
            <input
              type="number"
              step="1"
              min="1"
              v-model.number="khataPayForm.amount"
              required
              class="pos-input"
              style="font-size: 1.15rem; font-weight: 800;"
            />
          </div>

          <div style="margin-bottom: 14px;">
            <label style="display: block; font-weight: 700; font-size: 0.88rem; margin-bottom: 6px;">
              {{ currentLang === 'en' ? 'Payment Method' : (currentLang === 'mr' ? 'पेमेंट पद्धत' : 'भुगतान माध्यम') }}
            </label>
            <select v-model="khataPayForm.payment_method" class="pos-select">
              <option value="Cash">{{ currentLang === 'en' ? '💵 Cash' : (currentLang === 'mr' ? '💵 रोख (Cash)' : '💵 नकद (Cash)') }}</option>
              <option value="UPI">{{ currentLang === 'en' ? '📱 PhonePe / Google Pay / UPI' : '📱 फोन पे / गुगल पे / UPI' }}</option>
              <option value="Bank Transfer">{{ currentLang === 'en' ? '🏦 Bank Transfer (NEFT/IMPS)' : (currentLang === 'mr' ? '🏦 बँक ट्रान्सफर (NEFT/IMPS)' : '🏦 बैंक ट्रांसफर (NEFT/IMPS)') }}</option>
              <option value="Cheque">{{ currentLang === 'en' ? '📜 Cheque' : (currentLang === 'mr' ? '📜 चेक (Cheque)' : '📜 चेक (Cheque)') }}</option>
            </select>
          </div>

          <div style="margin-bottom: 18px;">
            <label style="display: block; font-weight: 700; font-size: 0.88rem; margin-bottom: 6px;">
              {{ currentLang === 'en' ? 'Note / Reference (Optional)' : (currentLang === 'mr' ? 'टीप / पावती संदर्भ (पर्यायी)' : 'नोट / संदर्भ') }}
            </label>
            <input
              type="text"
              v-model="khataPayForm.note"
              :placeholder="currentLang === 'en' ? 'e.g. Month bill partial payment' : (currentLang === 'mr' ? 'उदा. माहे सप्टेंबर बिल आंशिक पेमेंट' : 'उदा. सितम्बर बिल आंशिक भुगतान')"
              class="pos-input"
            />
          </div>

          <div style="display: flex; gap: 10px;">
            <button
              type="submit"
              :disabled="isSubmittingKhataPay"
              style="flex: 1; padding: 12px; background: #059669; color: white; border: none; border-radius: 8px; font-weight: 800; font-size: 0.95rem; cursor: pointer;"
            >
              {{ isSubmittingKhataPay ? (currentLang === 'en' ? 'Recording...' : (currentLang === 'mr' ? 'नोंद होत आहे...' : 'दर्ज हो रहा है...')) : (currentLang === 'en' ? '✅ Deposit Payment & Settle Bills' : (currentLang === 'mr' ? '✅ पेमेंट जमा करा व बिले चुकता करा' : '✅ भुगतान जमा करें व बिल चुकता करें')) }}
            </button>
            <button
              type="button"
              @click="showKhataPayModal = false"
              style="padding: 12px 18px; background: #e2e8f0; color: #334155; border: none; border-radius: 8px; font-weight: 700; cursor: pointer;"
            >
              {{ currentLang === 'en' ? 'Cancel' : (currentLang === 'mr' ? 'रद्द' : 'रद्द करें') }}
            </button>
          </div>
        </form>
      </div>
    </div>

    <!-- KHATA STATEMENT MODAL -->
    <div class="audit-modal-backdrop" v-if="showKhataStatementModal" @click.self="showKhataStatementModal = false">
      <div class="audit-modal-content">
        <div style="display: flex; justify-content: space-between; align-items: center; border-bottom: 2px solid var(--border); padding-bottom: 12px;">
          <div>
            <h3 style="font-size: 1.3rem; font-weight: 900; color: #064e3b; margin: 0; display: flex; align-items: center; gap: 8px;">
              📒 {{ activeKhataStatement?.customer_name }} — {{ currentLang === 'en' ? 'Khata Ledger Statement' : (currentLang === 'mr' ? 'खाते बही स्टेटमेंट' : 'खाता बही स्टेटमेंट') }}
            </h3>
            <div style="font-size: 0.84rem; color: var(--text-muted); margin-top: 4px;">
              <a :href="'tel:' + activeKhataStatement?.customer_phone" class="phone-call-pill" title="Click to call customer">📞 {{ activeKhataStatement?.customer_phone }}</a> | {{ currentLang === 'en' ? 'Total Due:' : (currentLang === 'mr' ? 'एकूण बाकी:' : 'कुल बकाया:') }} <strong style="color: #dc2626;">₹{{ activeKhataStatement?.unpaid_total }}</strong> | {{ currentLang === 'en' ? 'Total Paid:' : (currentLang === 'mr' ? 'एकूण भरलेली रक्कम:' : 'कुल भुगतान:') }} <strong style="color: #059669;">₹{{ activeKhataStatement?.paid_total }}</strong>
            </div>
          </div>
          <button class="close-btn" @click="showKhataStatementModal = false">✕</button>
        </div>

        <div v-if="khataStatementLoading" style="text-align: center; padding: 30px;">
          {{ currentLang === 'en' ? 'Loading statement...' : (currentLang === 'mr' ? 'स्टेटमेंट लोड होत आहे...' : 'स्टेटमेंट लोड हो रहा है...') }}
        </div>
        <div v-else style="margin-top: 16px;">
          <h4 style="font-size: 1rem; font-weight: 800; color: #1e293b; margin-bottom: 10px;">📋 {{ currentLang === 'en' ? 'All Orders & Invoices' : (currentLang === 'mr' ? 'सर्व ऑर्डर्स व बिले' : 'सभी ऑर्डर व बिल') }}</h4>
          <div class="admin-table-wrap">
            <table class="admin-table">
              <thead>
                <tr>
                  <th>{{ currentLang === 'en' ? 'Bill No.' : (currentLang === 'mr' ? 'बिल क्र.' : 'बिल नं.') }}</th>
                  <th>{{ currentLang === 'en' ? 'Date' : (currentLang === 'mr' ? 'दिनांक' : 'दिनांक') }}</th>
                  <th>{{ currentLang === 'en' ? 'Amount' : (currentLang === 'mr' ? 'रक्कम' : 'रकम') }}</th>
                  <th>{{ currentLang === 'en' ? 'Status' : (currentLang === 'mr' ? 'स्थिती' : 'स्थिति') }}</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="ord in activeKhataStatement?.orders" :key="ord.id">
                  <td><strong>{{ ord.order_number }}</strong></td>
                  <td>{{ ord.created_at }}</td>
                  <td><strong>₹{{ ord.final_amount }}</strong></td>
                  <td>
                    <span class="pay-badge" :class="ord.payment_status === 'Paid' ? 'paid' : 'unpaid'">
                      {{ ord.payment_status === 'Paid' ? (currentLang === 'en' ? '🟢 Paid' : '🟢 चुकता') : (currentLang === 'en' ? '🔴 Due' : (currentLang === 'mr' ? '🔴 बाकी' : '🔴 बकाया')) }}
                    </span>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>

          <h4 style="font-size: 1rem; font-weight: 800; color: #1e293b; margin: 20px 0 10px;">💰 {{ currentLang === 'en' ? 'Repayments History' : (currentLang === 'mr' ? 'जमा केलेल्या रकमा (Repayments History)' : 'जमा की गई रकमें (Repayments History)') }}</h4>
          <div class="admin-table-wrap">
            <table class="admin-table">
              <thead>
                <tr>
                  <th>{{ currentLang === 'en' ? 'Date' : (currentLang === 'mr' ? 'दिनांक' : 'दिनांक') }}</th>
                  <th>{{ currentLang === 'en' ? 'Deposit Amount' : (currentLang === 'mr' ? 'जमा रक्कम' : 'जमा रकम') }}</th>
                  <th>{{ currentLang === 'en' ? 'Method' : (currentLang === 'mr' ? 'माध्यम' : 'माध्यम') }}</th>
                  <th>{{ currentLang === 'en' ? 'Note' : (currentLang === 'mr' ? 'टीप' : 'नोट') }}</th>
                </tr>
              </thead>
              <tbody>
                <tr v-if="!activeKhataStatement?.payments || activeKhataStatement?.payments.length === 0">
                  <td colspan="4" style="text-align: center; color: var(--text-muted); padding: 18px;">{{ currentLang === 'en' ? 'No repayments recorded yet.' : (currentLang === 'mr' ? 'अद्याप कोणतीही रक्कम जमा केलेली नाही.' : 'अभी तक कोई रकम जमा नहीं की गई है।') }}</td>
                </tr>
                <tr v-for="p in activeKhataStatement?.payments" :key="p.id">
                  <td>{{ p.created_at }}</td>
                  <td><strong style="color: #059669;">+₹{{ p.amount }}</strong></td>
                  <td>{{ p.payment_method }}</td>
                  <td>{{ p.note || '-' }}</td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>

    <!-- ======================================================== -->
    <!-- VIEW 3: CUSTOMER ACCOUNT & ORDERS MODAL                  -->
    <!-- ======================================================== -->
    <div class="modal-overlay" v-if="showAccountModal" @click.self="showAccountModal = false">
      <div class="modal-card" style="max-width: 620px;">
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 16px;">
          <h3 style="font-size: 1.3rem; font-weight: 900; color: #064e3b; display: flex; align-items: center; gap: 8px;">
            👤 {{ t('my_account') }}
          </h3>
          <div style="display: flex; align-items: center; gap: 8px;">
            <button
              class="account-modal-logout-btn"
              @click="logout"
              style="background: #fee2e2; color: #dc2626; border: 1px solid #fca5a5; padding: 6px 12px; border-radius: 8px; font-weight: 800; font-size: 0.82rem; cursor: pointer; display: flex; align-items: center; gap: 4px;"
            >
              🚪 {{ t('logout') }}
            </button>
            <button class="close-btn" @click="showAccountModal = false">✕</button>
          </div>
        </div>

        <!-- Store Credit Balance Card -->
        <div class="store-credit-account-card">
          <div class="credit-card-left">
            <div class="credit-card-label">💳 {{ t('store_credit') }}</div>
            <div class="credit-card-balance">₹{{ (currentUser?.wallet_balance || 0).toFixed(2) }}</div>
            <div class="credit-card-sub">{{ t('store_credit_rule') }}</div>
          </div>
          <div class="credit-card-right">
            <span class="credit-card-chip">2.5% Loose • 0.5% FMCG</span>
          </div>
        </div>

        <div class="account-tabs">
          <button
            class="account-tab-btn"
            :class="{ active: customerActiveTab === 'orders' }"
            @click="customerActiveTab = 'orders'"
          >
            📦 {{ t('tab_my_orders') }}
          </button>
          <button
            class="account-tab-btn"
            :class="{ active: customerActiveTab === 'khata' }"
            @click="customerActiveTab = 'khata'; loadCustomerKhata();"
          >
            📒 {{ currentLang === 'en' ? 'My Khata' : (currentLang === 'mr' ? 'माझे खाते' : 'मेरा खाता') }}
            <span v-if="customerKhataData && customerKhataData.net_balance_due > 0" class="tab-badge-danger" style="margin-left: 4px;">
              ₹{{ customerKhataData.net_balance_due }}
            </span>
          </button>
          <button
            class="account-tab-btn"
            :class="{ active: customerActiveTab === 'profile' }"
            @click="customerActiveTab = 'profile'"
          >
            ⚙️ {{ t('tab_my_profile') }}
          </button>
          <button
            class="account-tab-btn"
            :class="{ active: customerActiveTab === 'language' }"
            @click="customerActiveTab = 'language'"
          >
            🌐 {{ t('select_language') }}
          </button>
          <button
            class="account-tab-btn"
            :class="{ active: customerActiveTab === 'support' }"
            @click="customerActiveTab = 'support'; loadCustomerSupportTickets();"
          >
            💬 {{ t('tab_help_feedback') }}
            <span v-if="openSupportTicketsCount > 0" class="tab-badge-danger" style="margin-left: 4px;">
              {{ openSupportTicketsCount }}
            </span>
          </button>
        </div>

        <!-- CUSTOMER TAB 1: MY ORDERS -->
        <div v-if="customerActiveTab === 'orders'">
          <div v-if="customerOrdersLoading" style="text-align: center; padding: 30px;">
            {{ currentLang === 'en' ? 'Loading orders...' : (currentLang === 'mr' ? 'ऑर्डर्स लोड होत आहेत...' : 'ऑर्डर लोड हो रहे हैं...') }}
          </div>
          <div v-else-if="customerOrders.length === 0" style="text-align: center; padding: 40px 20px; color: var(--text-muted);">
            <div style="font-size: 2.5rem; margin-bottom: 8px;">🧺</div>
            <p style="font-weight: 700;">{{ currentLang === 'en' ? 'You have not placed any orders yet.' : (currentLang === 'mr' ? 'तुम्ही अद्याप कोणतीही ऑर्डर केलेली नाही.' : 'आपने अभी तक कोई ऑर्डर नहीं दिया है।') }}</p>
          </div>
          <div v-else style="display: flex; flex-direction: column; gap: 14px;">
            <div
              v-for="ord in customerOrders"
              :key="ord.id"
              style="border: 1.5px solid var(--border); border-radius: 12px; padding: 16px; background: #fdfbf7;"
            >
              <div style="display: flex; justify-content: space-between; align-items: center; border-bottom: 1px solid var(--border); padding-bottom: 10px;">
                <div>
                  <strong style="color: #064e3b; font-size: 0.95rem;">{{ ord.order_number }}</strong>
                  <div style="font-size: 0.78rem; color: var(--text-subtle);">{{ ord.created_at }}</div>
                </div>
                <div style="text-align: right;">
                  <span style="font-weight: 900; font-size: 1.1rem; color: #1c1917;">₹{{ ord.final_amount }}</span>
                  <div v-if="ord.credit_used > 0" style="font-size: 0.74rem; color: #047857; font-weight: 700;">
                    💳 {{ currentLang === 'en' ? 'Discount:' : (currentLang === 'mr' ? 'सूट:' : 'छूट:') }} -₹{{ ord.credit_used }}
                  </div>
                  <div v-if="ord.credit_earned > 0" style="font-size: 0.74rem; font-weight: 700;">
                    <span v-if="ord.payment_status === 'Paid'" style="color: #059669;">
                      🎉 {{ currentLang === 'en' ? 'Credit Earned:' : 'क्रेडिट जमा:' }} +₹{{ ord.credit_earned }}
                    </span>
                    <span v-else style="color: #d97706;">
                      ⏳ +₹{{ ord.credit_earned }} {{ currentLang === 'en' ? '(Unlocked on full payment)' : (currentLang === 'mr' ? '(पेमेंट झाल्यावर मिळेल)' : '(पेमेंट पर अनलॉक होगा)') }}
                    </span>
                  </div>
                </div>
              </div>

              <!-- Flipkart-Style Live Availability Banner if Out for Delivery -->
              <div
                v-if="ord.status === 'Out for Delivery'"
                style="margin-top: 12px; background: #ecfdf5; border: 1.5px solid #6ee7b7; border-radius: 10px; padding: 12px; display: flex; flex-direction: column; gap: 8px;"
              >
                <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 6px;">
                  <span style="font-weight: 800; color: #065f46; font-size: 0.88rem; display: flex; align-items: center; gap: 6px;">
                    🛵💨 <strong>{{ currentLang === 'en' ? 'Delivery Boy is nearby! Are you available?' : (currentLang === 'mr' ? 'डिलिव्हरी पार्टनर निघत आहे! तुम्ही घरी आहात का?' : 'डिलीवरी बॉय निकलने वाला है! क्या आप घर पर हैं?') }}</strong>
                  </span>
                  <span v-if="ord.delivery_availability === 'available'" style="font-size: 0.8rem; font-weight: 900; color: #15803d; background: #dcfce7; padding: 3px 8px; border-radius: 6px;">
                    🟢 {{ currentLang === 'en' ? 'Confirmed: Available' : (currentLang === 'mr' ? 'कन्फर्म: उपलब्ध' : 'कन्फर्म: उपलब्ध') }}
                  </span>
                  <span v-else-if="ord.delivery_availability === 'reschedule'" style="font-size: 0.8rem; font-weight: 900; color: #b45309; background: #fef3c7; padding: 3px 8px; border-radius: 6px;">
                    ⏳ {{ currentLang === 'en' ? 'Reschedule Requested' : (currentLang === 'mr' ? 'नंतर पाठवण्याची विनंती' : 'बाद में भेजने का अनुरोध') }}
                  </span>
                </div>
                <div v-if="ord.delivery_availability !== 'available'" style="display: flex; gap: 8px; flex-wrap: wrap; margin-top: 2px;">
                  <button
                    type="button"
                    @click="confirmOrderAvailability(ord.order_number, 'available')"
                    style="flex: 1; min-width: 140px; background: #059669; color: white; border: none; padding: 8px 12px; border-radius: 8px; font-weight: 800; font-size: 0.84rem; cursor: pointer; display: flex; align-items: center; justify-content: center; gap: 6px;"
                  >
                    {{ t('delivery_avail_confirm_btn') }}
                  </button>
                  <button
                    type="button"
                    @click="confirmOrderAvailability(ord.order_number, 'reschedule')"
                    style="background: #f1f5f9; color: #475569; border: 1.5px solid #cbd5e1; padding: 8px 12px; border-radius: 8px; font-weight: 700; font-size: 0.82rem; cursor: pointer;"
                  >
                    {{ t('delivery_avail_reschedule_btn') }}
                  </button>
                </div>
                <div v-else style="font-size: 0.78rem; color: #047857; font-weight: 700;">
                  ✨ {{ currentLang === 'en' ? 'Thank you! Your order is being expedited to your address.' : (currentLang === 'mr' ? 'धन्यवाद! डिलिव्हरी पार्टनर तात्काळ आपल्या पत्त्यावर पोहोचत आहे.' : 'धन्यवाद! डिलीवरी पार्टनर तुरंत आपके पते पर पहुँच रहा है।') }}
                </div>
              </div>

              <!-- Active Delivery Add-on Banner (Plugs "Bhaiya, ek tel bhejwa dena" Margin Leak) -->
              <div
                v-if="canAddToActiveOrder(ord)"
                style="margin-top: 12px; background: #f0fdf4; border: 1.5px dashed #16a34a; border-radius: 10px; padding: 12px; display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 10px;"
              >
                <div style="flex: 1; min-width: 220px;">
                  <div style="font-weight: 900; color: #166534; font-size: 0.9rem; display: flex; align-items: center; gap: 6px;">
                    ⚡ <span>{{ t('active_addon_title') }}</span>
                  </div>
                  <div style="font-size: 0.78rem; color: #15803d; margin-top: 3px;">
                    {{ t('active_addon_sub') }}
                  </div>
                </div>
                <button
                  type="button"
                  @click="openAddActiveItemModal(ord)"
                  style="background: #16a34a; color: white; border: none; padding: 8px 14px; border-radius: 8px; font-weight: 800; font-size: 0.84rem; cursor: pointer; display: flex; align-items: center; gap: 6px; box-shadow: 0 2px 6px rgba(22, 163, 74, 0.25); white-space: nowrap;"
                >
                  <span>➕</span>
                  <span>{{ t('active_addon_btn') }}</span>
                </button>
              </div>

              <!-- Statuses Row -->
              <div style="display: flex; justify-content: space-between; align-items: center; margin-top: 10px; font-size: 0.85rem;">
                <div style="display: flex; gap: 8px; align-items: center;">
                  <span class="status-badge" :class="ord.status.toLowerCase().replace(/\s+/g, '')">
                    📦 {{ ord.status }}
                  </span>
                  <span class="pay-badge" :class="ord.payment_status === 'Paid' ? 'paid' : (ord.payment_status === 'Partially Paid' ? 'warning' : (ord.payment_status === 'Pending Verification' ? 'pending' : (ord.payment_status === 'Payment Failed' ? 'warning' : 'unpaid')))">
                    <template v-if="ord.payment_status === 'Paid'">
                      {{ currentLang === 'en' ? '🟢 Paid' : (currentLang === 'mr' ? '🟢 चुकता (Paid)' : '🟢 चुकता (Paid)') }}
                    </template>
                    <template v-else-if="ord.payment_status === 'Partially Paid'">
                      🟡 {{ currentLang === 'en' ? `Partially Paid (₹${ord.balance_due || (ord.final_amount - (ord.amount_paid || 0))} Due)` : (currentLang === 'mr' ? `🟡 अर्धवट भरले (₹${ord.balance_due || (ord.final_amount - (ord.amount_paid || 0))} बाकी)` : `🟡 आंशिक भुगतान (₹${ord.balance_due || (ord.final_amount - (ord.amount_paid || 0))} शेष)`) }}
                    </template>
                    <template v-else-if="ord.payment_status === 'Pending Verification'">
                      ⏳ {{ t('status_pending_verification') }}
                    </template>
                    <template v-else-if="ord.payment_status === 'Payment Failed'">
                      ⚠️ {{ currentLang === 'en' ? 'Payment Unreceived / Failed' : (currentLang === 'mr' ? 'पेमेंट मिळाले नाही / अडकले' : 'पेमेंट प्राप्त नहीं हुआ / अटका') }}
                    </template>
                    <template v-else>
                      {{ currentLang === 'en' ? '🔴 Unpaid Khata' : (currentLang === 'mr' ? '🔴 बाकी उधारी (Unpaid)' : '🔴 बाकी उधारी (Unpaid)') }}
                    </template>
                  </span>
                </div>

                <div style="display: flex; gap: 8px; flex-wrap: wrap;">
                  <button
                    v-if="canAddToActiveOrder(ord)"
                    @click="openAddActiveItemModal(ord)"
                    style="background: #ecfdf5; border: 1px solid #10b981; color: #047857; padding: 5px 12px; border-radius: 6px; font-size: 0.8rem; font-weight: 800; cursor: pointer; display: inline-flex; align-items: center; gap: 4px;"
                  >
                    ⚡ {{ t('active_addon_btn') }}
                  </button>
                  <button
                    v-if="ord.payment_status === 'Unpaid' || ord.payment_status === 'Payment Failed' || ord.payment_status === 'Partially Paid'"
                    @click="openUpiPayForCustomerOrder(ord)"
                    style="background: #047857; color: white; border: none; padding: 5px 12px; border-radius: 6px; font-size: 0.8rem; font-weight: 800; cursor: pointer;"
                  >
                    💳 {{ ord.payment_status === 'Partially Paid' ? (currentLang === 'en' ? `Pay Balance ₹${ord.balance_due || (ord.final_amount - (ord.amount_paid || 0))}` : (currentLang === 'mr' ? `उर्वरित ₹${ord.balance_due || (ord.final_amount - (ord.amount_paid || 0))} UPI ने भरा` : `बाकी ₹${ord.balance_due || (ord.final_amount - (ord.amount_paid || 0))} UPI से भरें`)) : (currentLang === 'en' ? 'Pay via UPI' : (currentLang === 'mr' ? 'UPI ने भरा' : 'UPI से भुगतान करें')) }}
                  </button>
                  <button
                    v-else-if="ord.payment_status === 'Pending Verification'"
                    @click="openUpiPayForCustomerOrder(ord)"
                    style="background: #d97706; color: white; border: none; padding: 5px 12px; border-radius: 6px; font-size: 0.8rem; font-weight: 800; cursor: pointer;"
                  >
                    📝 {{ currentLang === 'en' ? 'Update UTR' : (currentLang === 'mr' ? 'UTR बदला' : 'UTR अपडेट करें') }}
                  </button>
                  <button
                    @click="viewOrderReceipt(ord)"
                    style="background: white; border: 1px solid var(--border); padding: 5px 12px; border-radius: 6px; font-size: 0.8rem; font-weight: 700; cursor: pointer;"
                  >
                    🧾 {{ currentLang === 'en' ? 'View Bill' : (currentLang === 'mr' ? 'पर्चा पहा' : 'पर्चा देखें') }}
                  </button>
                  <button
                    @click="downloadOrderPdf(ord)"
                    style="background: #ecfdf5; border: 1px solid #a7f3d0; color: #047857; padding: 5px 12px; border-radius: 6px; font-size: 0.8rem; font-weight: 800; cursor: pointer;"
                  >
                    📥 {{ currentLang === 'en' ? 'PDF Bill' : 'PDF बिल' }}
                  </button>
                  <button
                    @click="reorderEntireBill(ord)"
                    style="background: #059669; color: white; border: none; padding: 5px 12px; border-radius: 6px; font-size: 0.8rem; font-weight: 800; cursor: pointer; display: inline-flex; align-items: center; gap: 4px;"
                    :title="currentLang === 'en' ? 'Add all items from this order to active cart' : 'या बिलातील सर्व सामान पुन्हा कार्टमध्ये जोडा'"
                  >
                    🛒 {{ currentLang === 'en' ? 'Re-order' : (currentLang === 'mr' ? 'पुन्हा मागवा' : 'दोबारा मंगाएं') }}
                  </button>
                </div>
              </div>

              <!-- Items preview -->
              <div style="margin-top: 10px; font-size: 0.8rem; color: var(--text-muted); background: white; padding: 8px 12px; border-radius: 6px; border: 1px solid var(--border);">
                <span v-for="(it, i) in ord.items" :key="i">
                  {{ it.product_name }} ({{ it.variant_label }}) × {{ it.quantity }}{{ i < ord.items.length - 1 ? ', ' : '' }}
                </span>
              </div>
            </div>
          </div>
        </div>

        <!-- CUSTOMER TAB 2: PROFILE & DELIVERY ADDRESS -->
        <div v-if="customerActiveTab === 'profile'">
          <form @submit.prevent="updateCustomerProfile">
            <div class="form-group">
              <label class="form-label">{{ currentLang === 'en' ? 'Full Name *' : (currentLang === 'mr' ? 'पूर्ण नाव (Full Name) *' : 'पूरा नाम (Full Name) *') }}</label>
              <input type="text" v-model="profileForm.name" required class="form-input" />
            </div>
            <div class="form-group">
              <label class="form-label">{{ currentLang === 'en' ? 'Email ID (For OTP & Digital Receipts)' : (currentLang === 'mr' ? 'ईमेल (OTP व डिजिटल बिलांसाठी)' : 'ईमेल (OTP व डिजिटल बिल के लिए)') }}</label>
              <input type="email" v-model="profileForm.email" class="form-input" :placeholder="currentLang === 'en' ? 'e.g. name@gmail.com' : 'उदा. name@gmail.com'" />
            </div>
            <div class="form-group">
              <label class="form-label">{{ currentLang === 'en' ? 'Mobile / WhatsApp Number *' : (currentLang === 'mr' ? 'मोबाईल नंबर (Phone Number) *' : 'मोबाइल नंबर (Phone Number) *') }}</label>
              <input type="tel" v-model="profileForm.phone" required class="form-input" />
            </div>
            <div class="form-group">
              <label class="form-label">{{ currentLang === 'en' ? 'Default Delivery Address *' : (currentLang === 'mr' ? 'डिफॉल्ट डिलिव्हरी पत्ता (Delivery Address) *' : 'डिफ़ॉल्ट डिलीवरी का पता (Delivery Address) *') }}</label>
              <textarea v-model="profileForm.address" rows="3" required class="form-input" :placeholder="currentLang === 'en' ? 'House / Flat No., Building, Street, Landmark, Pincode' : (currentLang === 'mr' ? 'घर क्र., इमारत, रस्ता, लँडमार्क' : 'मकान नं, बिल्डिंग, गली, मोहल्ला / लैंडमार्क')"></textarea>
            </div>
            <button type="submit" class="checkout-btn">
              💾 {{ currentLang === 'en' ? 'Save Address & Settings' : (currentLang === 'mr' ? 'पत्ता व सेटिंग्ज सेव्ह करा' : 'पता व सेटिंग्स सेव करें') }}
            </button>
          </form>

          <div style="margin-top: 18px; padding-top: 14px; border-top: 1px dashed var(--border); text-align: center;">
            <button
              type="button"
              @click="logout"
              style="background: #fff1f2; color: #e11d48; border: 1.5px solid #fecdd3; padding: 10px 16px; border-radius: 8px; font-weight: 800; font-size: 0.92rem; width: 100%; cursor: pointer; display: flex; align-items: center; justify-content: center; gap: 8px;"
            >
              🚪 {{ t('logout') }}
            </button>
          </div>
        </div>

        <!-- CUSTOMER TAB 3: LANGUAGE PREFERENCE -->
        <div v-if="customerActiveTab === 'language'" style="padding: 10px 0;">
          <h4 style="font-size: 1rem; font-weight: 800; margin-bottom: 6px; color: #064e3b;">
            {{ t('select_language') }}
          </h4>
          <p style="font-size: 0.82rem; color: var(--text-muted); margin-bottom: 14px;">
            {{ currentLang === 'mr' ? 'आपली पसंतीची भाषा निवडा. संपूर्ण ॲप त्वरित बदलले जाईल.' : (currentLang === 'hi' ? 'अपनी पसंदीदा भाषा चुनें। पूरा ऐप तुरंत बदल जाएगा।' : 'Choose your preferred language. The entire app will update immediately.') }}
          </p>

          <div class="lang-account-grid">
            <button
              class="lang-choice-btn"
              :class="{ selected: currentLang === 'mr' }"
              @click="selectLanguage('mr')"
            >
              <span class="flag-icon">🇮🇳</span>
              <div class="lang-btn-text">
                <strong>मराठी</strong>
                <small>Maharashtra / Mumbai (मराठी)</small>
              </div>
              <span class="check-mark" v-if="currentLang === 'mr'">✓</span>
            </button>

            <button
              class="lang-choice-btn"
              :class="{ selected: currentLang === 'hi' }"
              @click="selectLanguage('hi')"
            >
              <span class="flag-icon">🇮🇳</span>
              <div class="lang-btn-text">
                <strong>हिंदी</strong>
                <small>Hindi (हिंदी)</small>
              </div>
              <span class="check-mark" v-if="currentLang === 'hi'">✓</span>
            </button>

            <button
              class="lang-choice-btn"
              :class="{ selected: currentLang === 'en' }"
              @click="selectLanguage('en')"
            >
              <span class="flag-icon">🇬🇧</span>
              <div class="lang-btn-text">
                <strong>English</strong>
                <small>English (Default)</small>
              </div>
              <span class="check-mark" v-if="currentLang === 'en'">✓</span>
            </button>
          </div>
        </div>

        <!-- CUSTOMER TAB 4: MY KHATA -->
        <div v-if="customerActiveTab === 'khata'">
          <div v-if="customerKhataLoading" style="text-align: center; padding: 30px;">
            {{ currentLang === 'en' ? 'Loading khata account...' : (currentLang === 'mr' ? 'खाते लोड होत आहे...' : 'खाता लोड हो रहा है...') }}
          </div>
          <div v-else>
            <!-- Khata Balance Card -->
            <div style="background: #fef2f2; border: 1.5px solid #fecaca; border-radius: 12px; padding: 16px; margin-bottom: 16px; display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 10px;">
              <div>
                <span style="font-size: 0.82rem; color: #991b1b; font-weight: 800;">
                  {{ currentLang === 'en' ? 'Net Outstanding Khata Dues:' : (currentLang === 'mr' ? 'एकूण बाकी उधारी रक्कम (Net Balance Due):' : 'कुल बकाया उधारी रकम (Net Balance Due):') }}
                </span>
                <div style="font-size: 1.7rem; font-weight: 900; color: #dc2626; margin-top: 2px;">
                  ₹{{ customerKhataData ? customerKhataData.net_balance_due : 0 }}
                </div>
              </div>
              <button
                v-if="customerKhataData && customerKhataData.unpaid_orders.length > 0"
                @click="openUpiPayForCustomerOrder(customerKhataData.unpaid_orders[0])"
                style="background: #047857; color: white; border: none; padding: 8px 16px; border-radius: 8px; font-weight: 800; cursor: pointer;"
              >
                💳 {{ currentLang === 'en' ? 'Pay via UPI' : (currentLang === 'mr' ? 'UPI ने भरा' : 'UPI से भरें') }}
              </button>
            </div>

            <!-- Unpaid Orders List -->
            <div v-if="!customerKhataData || customerKhataData.unpaid_orders.length === 0" style="text-align: center; padding: 30px 10px; color: var(--text-muted);">
              <div style="font-size: 2rem; margin-bottom: 6px;">🎉</div>
              <strong>{{ currentLang === 'en' ? 'Your account is completely clear! No dues pending.' : (currentLang === 'mr' ? 'तुमचे खाते पूर्णपणे चुकता आहे! कोणतीही बाकी नाही.' : 'आपका खाता पूरी तरह चुकता है! कोई बकाया नहीं।') }}</strong>
            </div>
            <div v-else style="display: flex; flex-direction: column; gap: 10px;">
              <h4 style="font-size: 0.95rem; font-weight: 800; color: #1e293b; margin: 4px 0 2px;">📋 {{ currentLang === 'en' ? 'Unpaid Invoices' : (currentLang === 'mr' ? 'बाकी राहिलेली बिले' : 'बकाया बिल') }}</h4>
              <div
                v-for="ord in customerKhataData.unpaid_orders"
                :key="ord.id"
                style="border: 1px solid var(--border); border-radius: 8px; padding: 12px; background: white; display: flex; justify-content: space-between; align-items: center;"
              >
                <div>
                  <strong style="color: #064e3b;">{{ ord.order_number }}</strong>
                  <div style="font-size: 0.76rem; color: var(--text-subtle);">{{ ord.created_at }}</div>
                </div>
                <div style="text-align: right;">
                  <strong style="color: #dc2626; font-size: 1.05rem;">₹{{ ord.final_amount }}</strong>
                  <div style="margin-top: 4px;">
                    <button
                      @click="openUpiPayForCustomerOrder(ord)"
                      style="background: #059669; color: white; border: none; padding: 4px 10px; border-radius: 5px; font-size: 0.75rem; font-weight: 800; cursor: pointer;"
                    >
                      {{ currentLang === 'en' ? 'Pay Now' : (currentLang === 'mr' ? 'चुकता करा' : 'चुकता करें') }}
                    </button>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- CUSTOMER TAB 5: HELP & FEEDBACK / COMPLAINTS -->
        <div v-if="customerActiveTab === 'support'">
          <!-- Mode Switcher: Complaint vs Feedback -->
          <div class="support-type-toggle">
            <button
              type="button"
              class="support-type-btn"
              :class="{ active: supportTicketType === 'complaint', complaint: true }"
              @click="supportTicketType = 'complaint'"
            >
              <span>🚨</span>
              <span>{{ t('support_complaint') }}</span>
            </button>
            <button
              type="button"
              class="support-type-btn"
              :class="{ active: supportTicketType === 'feedback', feedback: true }"
              @click="supportTicketType = 'feedback'"
            >
              <span>💡</span>
              <span>{{ t('support_feedback') }}</span>
            </button>
          </div>

          <!-- Description banner based on active mode -->
          <p style="font-size: 0.82rem; color: var(--text-muted); margin: -8px 0 14px 4px;">
            {{ supportTicketType === 'complaint' ? t('support_complaint_desc') : t('support_feedback_desc') }}
          </p>

          <!-- Success Confirmation Banner -->
          <div v-if="supportSuccessTicket" class="support-success-card">
            <span style="font-size: 1.8rem; line-height: 1;">✅</span>
            <div style="flex: 1;">
              <div style="font-weight: 800; font-size: 0.95rem; color: #065f46; margin-bottom: 4px;">
                {{ supportSuccessTicket.ticket_type === 'complaint' ? (currentLang === 'mr' ? 'तक्रार यशस्वीरीत्या नोंदवली गेली!' : (currentLang === 'hi' ? 'शिकायत सफलतापूर्वक दर्ज हो गई!' : 'Complaint registered successfully!')) : (currentLang === 'mr' ? 'अभिप्राय यशस्वीरीत्या पाठवला!' : (currentLang === 'hi' ? 'सुझाव सफलतापूर्वक भेज दिया गया!' : 'Feedback submitted successfully!')) }}
              </div>
              <div style="font-size: 0.84rem; color: #047857; margin-bottom: 6px;">
                <strong>{{ currentLang === 'en' ? 'Ticket ID:' : (currentLang === 'mr' ? 'तिकीट क्र.:' : 'टिकट नं.:') }}</strong> #{{ supportSuccessTicket.ticket_number }}
              </div>
              <div style="font-size: 0.8rem; color: #065f46; line-height: 1.4;">
                {{ supportSuccessTicket.ticket_type === 'complaint' ? (currentLang === 'mr' ? 'आमचे दुकान व्यवस्थापक या तक्रारीची लवकरात लवकर तपासणी करून आपल्याशी संपर्क साधतील.' : (currentLang === 'hi' ? 'हमारे स्टोर मैनेजर इस शिकायत की शीघ्र जांच करके आपसे संपर्क करेंगे।' : 'Our store manager will review this urgently and reach out.')) : (currentLang === 'mr' ? 'आपल्या बहुमूल्य अभिप्रायाबद्दल मनःपूर्वक धन्यवाद.' : (currentLang === 'hi' ? 'आपके बहुमूल्य सुझाव के लिए धन्यवाद।' : 'Thank you for helping us improve Komal Mart.')) }}
              </div>
              <div style="margin-top: 10px;">
                <button
                  type="button"
                  @click="resetSupportForm"
                  style="background: #059669; color: white; border: none; padding: 6px 14px; border-radius: 6px; font-size: 0.8rem; font-weight: 700; cursor: pointer;"
                >
                  + {{ currentLang === 'en' ? 'Submit Another' : (currentLang === 'mr' ? 'नवीन नोंदवा' : 'नया दर्ज करें') }}
                </button>
              </div>
            </div>
          </div>

          <!-- Ticket Form -->
          <form v-if="!supportSuccessTicket" @submit.prevent="submitSupportTicket">
            <!-- Category Selection -->
            <div class="form-group">
              <label class="form-label">{{ t('support_select_category') }}</label>
              <select v-model="supportCategory" required class="form-input" style="cursor: pointer;">
                <option value="" disabled>{{ currentLang === 'mr' ? '-- निवडा --' : (currentLang === 'hi' ? '-- चुनें --' : '-- Select --') }}</option>
                <template v-if="supportTicketType === 'complaint'">
                  <option :value="t('support_category_delivery_delayed')">{{ t('support_category_delivery_delayed') }}</option>
                  <option :value="t('support_category_delivery_boy')">{{ t('support_category_delivery_boy') }}</option>
                  <option :value="t('support_category_missing_items')">{{ t('support_category_missing_items') }}</option>
                  <option :value="t('support_category_damaged_items')">{{ t('support_category_damaged_items') }}</option>
                  <option :value="t('support_category_billing')">{{ t('support_category_billing') }}</option>
                  <option :value="t('support_category_app_issue')">{{ t('support_category_app_issue') }}</option>
                  <option :value="t('support_category_other_complaint')">{{ t('support_category_other_complaint') }}</option>
                </template>
                <template v-else>
                  <option :value="t('support_category_new_product')">{{ t('support_category_new_product') }}</option>
                  <option :value="t('support_category_pricing')">{{ t('support_category_pricing') }}</option>
                  <option :value="t('support_category_packaging')">{{ t('support_category_packaging') }}</option>
                  <option :value="t('support_category_praise')">{{ t('support_category_praise') }}</option>
                  <option :value="t('support_category_general_suggestion')">{{ t('support_category_general_suggestion') }}</option>
                </template>
              </select>
            </div>

            <!-- Optional Related Order -->
            <div class="form-group" v-if="customerOrders && customerOrders.length > 0">
              <label class="form-label">{{ t('support_related_order') }}</label>
              <select v-model="supportOrderNumber" class="form-input" style="cursor: pointer;">
                <option value="">{{ t('support_no_related_order') }}</option>
                <option v-for="ord in customerOrders" :key="ord.id" :value="ord.order_number">
                  #{{ ord.order_number }} (₹{{ ord.final_amount }} — {{ ord.created_at }})
                </option>
              </select>
            </div>

            <!-- Message with Mic speech-to-text -->
            <div class="form-group">
              <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 6px;">
                <label class="form-label" style="margin-bottom: 0;">{{ t('support_message_label') }}</label>
                <span v-if="isSupportRecording" style="font-size: 0.75rem; color: #dc2626; font-weight: 800; display: flex; align-items: center; gap: 4px;">
                  <span style="display: inline-block; width: 8px; height: 8px; border-radius: 50%; background: #dc2626; animation: pulse-red 1s infinite;"></span>
                  {{ t('support_mic_listening') }}
                </span>
              </div>
              <div class="support-textarea-wrap">
                <textarea
                  v-model="supportMessage"
                  rows="4"
                  required
                  class="form-input"
                  :placeholder="t('support_message_placeholder')"
                  style="resize: vertical; padding-right: 110px; min-height: 100px;"
                ></textarea>
                <button
                  type="button"
                  class="support-mic-btn"
                  :class="{ recording: isSupportRecording }"
                  @click="toggleSupportVoiceInput"
                  :title="isSupportRecording ? 'बोलणे थांबवा' : 'माईक दाबून बोला'"
                >
                  <span>{{ isSupportRecording ? '⏹️' : '🎙️' }}</span>
                  <span>{{ isSupportRecording ? (currentLang === 'en' ? 'Stop' : 'थांबवा') : t('support_mic_btn') }}</span>
                </button>
              </div>
              <div style="display: flex; justify-content: space-between; align-items: center; margin-top: 4px;">
                <span style="font-size: 0.72rem; color: var(--text-subtle);">
                  {{ currentLang === 'mr' ? '💡 तुम्ही मराठी, हिंदी किंवा इंग्रजीत बोलू शकता.' : (currentLang === 'hi' ? '💡 आप हिंदी, मराठी या अंग्रेजी में बोल सकते हैं।' : '💡 You can speak in Marathi, Hindi, or English.') }}
                </span>
                <button
                  v-if="supportMessage"
                  type="button"
                  @click="supportMessage = ''"
                  style="background: none; border: none; font-size: 0.72rem; color: var(--text-muted); cursor: pointer; text-decoration: underline;"
                >
                  {{ currentLang === 'en' ? 'Clear text' : 'मजकूर पुसा' }}
                </button>
              </div>
            </div>

            <!-- Submit Button -->
            <button
              type="submit"
              class="btn-primary"
              :disabled="supportSubmitting"
              style="width: 100%; padding: 12px; font-size: 0.95rem; font-weight: 800; display: flex; align-items: center; justify-content: center; gap: 8px; border-radius: 8px; margin-top: 8px;"
              :style="supportTicketType === 'complaint' ? 'background: #dc2626;' : 'background: #059669;'"
            >
              <span>{{ supportSubmitting ? t('support_submitting') : (supportTicketType === 'complaint' ? t('support_submit_complaint') : t('support_submit_feedback')) }}</span>
            </button>
          </form>

          <!-- Customer Previous Tickets History -->
          <div style="margin-top: 24px; border-top: 1.5px solid var(--border); padding-top: 18px;">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px;">
              <h4 style="font-size: 0.95rem; font-weight: 800; color: #1e293b; margin: 0; display: flex; align-items: center; gap: 6px;">
                📋 {{ t('support_history_title') }}
              </h4>
              <button
                type="button"
                @click="loadCustomerSupportTickets"
                style="background: none; border: none; font-size: 0.78rem; font-weight: 700; color: #059669; cursor: pointer;"
              >
                🔄 {{ currentLang === 'en' ? 'Refresh' : 'रीफ्रेश' }}
              </button>
            </div>

            <div v-if="supportTicketsLoading" style="text-align: center; padding: 20px; color: var(--text-muted); font-size: 0.85rem;">
              {{ currentLang === 'en' ? 'Loading tickets...' : (currentLang === 'mr' ? 'तिकीट माहिती लोड होत आहे...' : 'टिकट लोड हो रहे हैं...') }}
            </div>
            <div v-else-if="supportTicketsList.length === 0" style="text-align: center; padding: 20px; color: var(--text-muted); font-size: 0.84rem; background: #f8fafc; border-radius: 8px;">
              {{ t('support_no_history') }}
            </div>
            <div v-else style="display: flex; flex-direction: column; gap: 10px;">
              <div v-for="tkt in supportTicketsList" :key="tkt.id" class="ticket-card">
                <div style="display: flex; justify-content: space-between; align-items: flex-start; gap: 8px; margin-bottom: 6px;">
                  <div>
                    <span style="font-weight: 800; font-size: 0.88rem; color: #0f172a;">
                      {{ tkt.ticket_type === 'complaint' ? '🚨' : '💡' }} #{{ tkt.ticket_number }}
                    </span>
                    <div style="font-size: 0.74rem; color: var(--text-subtle);">{{ tkt.created_at }}</div>
                  </div>
                  <span
                    class="ticket-badge"
                    :class="{
                      'ticket-badge-open': tkt.status === 'Open',
                      'ticket-badge-in-review': tkt.status === 'In Review',
                      'ticket-badge-resolved': tkt.status === 'Resolved'
                    }"
                  >
                    {{ tkt.status === 'Open' ? t('support_status_open') : (tkt.status === 'In Review' ? t('support_status_in_review') : t('support_status_resolved')) }}
                  </span>
                </div>

                <div style="font-size: 0.8rem; font-weight: 700; color: #334155; margin-bottom: 4px;">
                  {{ tkt.category }}
                  <span v-if="tkt.order_number" style="color: #64748b; font-weight: normal; margin-left: 6px;">
                    ({{ currentLang === 'en' ? 'Order' : 'ऑर्डर' }} #{{ tkt.order_number }})
                  </span>
                </div>

                <p style="font-size: 0.82rem; color: #475569; margin: 0 0 6px 0; background: #f8fafc; padding: 8px 10px; border-radius: 6px; white-space: pre-wrap;">
                  {{ tkt.message }}
                </p>

                <!-- Store Resolution / Admin Notes if present -->
                <div v-if="tkt.admin_notes" style="background: #ecfdf5; border-left: 3px solid #10b981; padding: 6px 10px; border-radius: 0 6px 6px 0; font-size: 0.78rem; color: #065f46;">
                  <strong>{{ t('support_admin_response') }}</strong> {{ tkt.admin_notes }}
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- ======================================================== -->
    <!-- AUTH MODAL: LOGIN / REGISTER / ADMIN LOGIN               -->
    <!-- ======================================================== -->
    <div class="modal-overlay" v-if="showAuthModal" @click.self="showAuthModal = false">
      <div class="modal-card" style="max-width: 460px;">
        <!-- Auth Modal Header with In-Modal 3-Language Selector -->
        <div class="auth-modal-header">
          <div class="auth-title-wrap">
            <h3 style="font-size: 1.22rem; font-weight: 900; color: #064e3b; margin: 0;">
              {{ getAuthModalTitle() }}
            </h3>
          </div>
          <div class="auth-header-controls">
            <!-- In-Modal Language Segmented Pills -->
            <div class="modal-lang-pills">
              <button
                type="button"
                class="modal-lang-pill"
                :class="{ active: currentLang === 'mr' }"
                @click="selectLanguage('mr')"
                title="मराठी"
              >
                मराठी
              </button>
              <button
                type="button"
                class="modal-lang-pill"
                :class="{ active: currentLang === 'hi' }"
                @click="selectLanguage('hi')"
                title="हिंदी"
              >
                हिंदी
              </button>
              <button
                type="button"
                class="modal-lang-pill"
                :class="{ active: currentLang === 'en' }"
                @click="selectLanguage('en')"
                title="English"
              >
                EN
              </button>
            </div>
            <button class="close-btn" @click="showAuthModal = false">✕</button>
          </div>
        </div>

        <!-- Auth Tabs (Only for Customer Login/Register) -->
        <div class="account-tabs" v-if="authMode !== 'admin' && !admin2faState.active && authMode !== 'reset_password'">
          <button
            class="account-tab-btn"
            :class="{ active: authMode === 'login' }"
            @click="authMode = 'login'"
          >
            {{ t('auth_tab_login') }}
          </button>
          <button
            class="account-tab-btn"
            :class="{ active: authMode === 'register' }"
            @click="authMode = 'register'"
          >
            {{ t('auth_tab_register') }}
          </button>
        </div>

        <!-- Error Alert -->
        <div v-if="authError" style="background: #fee2e2; color: #991b1b; padding: 10px 14px; border-radius: 8px; font-size: 0.85rem; font-weight: 700; margin-bottom: 14px; border: 1px solid #fecaca;">
          {{ authError }}
        </div>

        <!-- VIEW A: ADMIN 2-STEP VERIFICATION (OTP SCREEN) -->
        <div v-if="admin2faState.active" style="text-align: center;">
          <div style="font-size: 2.8rem; margin-bottom: 8px;">🔐</div>
          <p style="font-size: 0.92rem; color: #374151; margin-bottom: 6px;">
            {{ t('auth_admin_2fa_notice') }}
          </p>
          <div style="background: #f1f5f9; padding: 8px 12px; border-radius: 8px; font-weight: 800; color: #064e3b; margin-bottom: 8px; font-size: 0.95rem;">
            ✉️ {{ admin2faState.masked_email || admin2faState.admin_email }}
          </div>

          <!-- Master PIN notice if cloud email is blocked -->
          <div v-if="admin2faState.email_dispatched === false" style="background: #eff6ff; border: 1.5px solid #bfdbfe; border-radius: 8px; padding: 12px 14px; margin-bottom: 14px; font-size: 0.84rem; color: #1e40af; text-align: left; line-height: 1.5;">
            💡 <strong>{{ currentLang === 'mr' ? 'क्लाउड सर्व्हर मास्टर कोड (Master PIN):' : (currentLang === 'hi' ? 'क्लाउड सर्वर मास्टर कोड (Master PIN):' : 'Cloud Server Master PIN:') }}</strong><br />
            {{ currentLang === 'mr' ? 'क्लाउड सर्व्हरवर ईमेल पोर्ट ब्लॉक असल्याने त्वरित प्रवेशासाठी मास्टर कोड वापरा:' : (currentLang === 'hi' ? 'क्लाउड सर्वर पर ईमेल पोर्ट बंद होने के कारण त्वरित एक्सेस हेतु मास्टर कोड डालें:' : 'Render free tier restricts outbound SMTP. Enter Store Owner PIN to verify immediately:') }}
            <div style="font-size: 1.25rem; font-weight: 900; letter-spacing: 4px; color: #047857; margin-top: 6px; text-align: center; background: white; padding: 6px; border-radius: 6px; border: 1px dashed #6ee7b7;">
              202699
            </div>
          </div>
          <p v-else style="font-size: 0.78rem; color: var(--text-muted); margin-bottom: 14px;">
            {{ t('auth_admin_2fa_email_hint') }}
          </p>

          <form @submit.prevent="handleVerifyAdmin2Fa">
            <div class="form-group">
              <label class="form-label" style="text-align: left;">{{ t('auth_admin_otp_label') }}</label>
              <input
                type="text"
                v-model="admin2faState.otp"
                required
                maxlength="6"
                pattern="[0-9]{6}"
                class="form-input"
                placeholder="123456"
                style="font-size: 1.6rem; letter-spacing: 8px; text-align: center; font-weight: 900; color: #064e3b;"
                autofocus
              />
            </div>

            <button type="submit" class="checkout-btn" :disabled="authSubmitting">
              {{ authSubmitting ? t('auth_btn_submitting') : t('auth_admin_verify_btn') }}
            </button>
          </form>

          <p style="margin-top: 14px; font-size: 0.82rem; color: var(--text-muted);">
            <a href="javascript:void(0)" @click="admin2faState.active = false" style="color: #047857; font-weight: 700; text-decoration: none;">
              {{ t('auth_back_to_login') }}
            </a>
          </p>
        </div>

        <!-- VIEW B: FORGOT / RESET PASSWORD FORM -->
        <!-- VIEW B: FORGOT / RESET PASSWORD FORM (2-STEP EMAIL OTP) -->
        <div v-else-if="authMode === 'reset_password'">
          <!-- Step 1: Request OTP -->
          <div v-if="resetStep === 1">
            <div style="background: #f0fdf4; border: 1px solid #bbf7d0; padding: 10px 14px; border-radius: 8px; font-size: 0.84rem; color: #166534; margin-bottom: 14px; line-height: 1.45;">
              {{ currentLang === 'en' ? 'ℹ️ Enter your registered mobile number or email. You can verify instantly via WhatsApp or Email OTP to reset your password.' : (currentLang === 'mr' ? 'ℹ️ आपला नोंदणीकृत मोबाईल नंबर किंवा ईमेल टाका. पासवर्ड रीसेट करण्यासाठी आपण WhatsApp किंवा ईमेल OTP द्वारे त्वरित पडताळणी करू शकता.' : 'ℹ️ अपना पंजीकृत मोबाइल नंबर या ईमेल दर्ज करें। पासवर्ड रीसेट करने के लिए आप WhatsApp या ईमेल OTP द्वारा तुरंत सत्यापन कर सकते हैं।') }}
            </div>

            <form @submit.prevent="handleRequestResetOtp()">
              <div class="form-group">
                <label class="form-label">{{ t('auth_reset_identifier_label') }}</label>
                <input
                  type="text"
                  v-model="resetIdentifier"
                  required
                  class="form-input"
                  :placeholder="currentLang === 'en' ? 'e.g. 9820011223 or rahul@gmail.com' : 'उदा. 9820011223 किंवा rahul@gmail.com'"
                  autofocus
                />
                <span style="font-size: 0.72rem; color: var(--text-muted);">
                  {{ currentLang === 'en' ? 'Enter your 10-digit phone number or registered email address' : (currentLang === 'mr' ? 'आपला १०-अंकी फोन नंबर किंवा नोंदणीकृत ईमेल पत्ता टाका' : 'अपना 10-अंकीय फोन नंबर या पंजीकृत ईमेल दर्ज करें') }}
                </span>
              </div>

              <button type="submit" class="checkout-btn" :disabled="authSubmitting">
                {{ authSubmitting ? t('auth_btn_submitting') : (currentLang === 'en' ? '🔐 Continue to Reset Password' : (currentLang === 'mr' ? '🔐 पासवर्ड रीसेट सुरू करा' : '🔐 पासवर्ड रीसेट शुरू करें')) }}
              </button>
            </form>
          </div>

          <!-- Step 2: Verify OTP & Set New Password -->
          <div v-else-if="resetStep === 2">
            <!-- Channel: WhatsApp Store Support (For Legacy Phone Accounts Without Email) -->
            <div v-if="resetChannel === 'whatsapp'" style="background: #fffbeb; border: 1.5px solid #fef3c7; padding: 16px; border-radius: 10px; margin-bottom: 16px; text-align: center;">
              <div style="font-size: 2rem; margin-bottom: 6px;">🏪</div>
              <p style="font-size: 0.92rem; color: #92400e; font-weight: 800; margin: 0 0 6px 0;">
                {{ currentLang === 'en' ? 'Store Security Verification' : (currentLang === 'mr' ? 'दुकानदार सुरक्षा पडताळणी' : 'दुकानदार सुरक्षा सत्यापन') }}
              </p>
              <p style="font-size: 0.82rem; color: #4b5563; margin: 0 0 14px 0; line-height: 1.45;">
                <template v-if="resetHasEmail">
                  {{ currentLang === 'en' ? 'Email delivery is currently unavailable. For your account safety, please message our store on WhatsApp to reset your password.' : (currentLang === 'mr' ? 'ईमेल डिलिव्हरी सध्या उपलब्ध नाही. खात्याच्या सुरक्षेसाठी, कृपया पासवर्ड रीसेट करण्यासाठी आमच्या दुकानदाराशी WhatsApp वर संपर्क साधा.' : 'ईमेल सेवा फ़िलहाल अनुपलब्ध है। खाते की सुरक्षा के लिए, कृपया पासवर्ड रीसेट करने हेतु हमारे दुकानदार से WhatsApp पर संपर्क करें।') }}
                </template>
                <template v-else>
                  {{ currentLang === 'en' ? 'Your account does not have a registered email address. For your account safety, please message our store on WhatsApp to reset your password.' : (currentLang === 'mr' ? 'तुमच्या खात्याशी ईमेल जोडलेला नाही. खात्याच्या सुरक्षेसाठी, कृपया पासवर्ड रीसेट करण्यासाठी आमच्या दुकानदाराशी WhatsApp वर संपर्क साधा.' : 'आपके खाते से कोई ईमेल नहीं जुड़ा है। खाते की सुरक्षा के लिए, कृपया पासवर्ड रीसेट करने हेतु हमारे दुकानदार से WhatsApp पर संपर्क करें।') }}
                </template>
              </p>
              <a
                v-if="resetWaLink"
                :href="resetWaLink"
                target="_blank"
                style="display: inline-flex; align-items: center; justify-content: center; gap: 8px; background: #25d366; color: white; padding: 10px 18px; border-radius: 8px; text-decoration: none; font-weight: 800; font-size: 0.9rem; box-shadow: 0 2px 6px rgba(37,211,102,0.3);"
              >
                📲 {{ currentLang === 'en' ? 'Message Komal Mart on WhatsApp' : (currentLang === 'mr' ? 'WhatsApp वर दुकानदाराशी संपर्क साधा' : 'WhatsApp पर दुकानदार से संपर्क करें') }}
              </a>
            </div>

            <!-- Channel: Automated Email OTP via Resend -->
            <div v-else style="background: #ecfdf5; border: 1.5px solid #a7f3d0; padding: 14px; border-radius: 8px; margin-bottom: 16px; text-align: center;">
              <div style="font-size: 1.8rem; margin-bottom: 4px;">📩</div>
              <p style="font-size: 0.88rem; color: #065f46; font-weight: 800; margin: 0 0 4px 0;">
                {{ t('auth_reset_notice_step2') }}
              </p>
              <div style="display: inline-block; background: white; border: 1px dashed #059669; padding: 4px 12px; border-radius: 6px; font-size: 0.9rem; font-weight: 800; color: #047857; margin-top: 4px;">
                ✉️ {{ resetMaskedTarget || resetMaskedEmail }}
              </div>
            </div>

            <!-- Form: Active only for Email OTP -->
            <form v-if="resetChannel === 'email'" @submit.prevent="handleVerifyAndResetPassword">
              <div class="form-group">
                <label class="form-label">{{ t('auth_reset_otp_label') }}</label>
                <input
                  type="text"
                  v-model="resetOtp"
                  required
                  maxlength="6"
                  pattern="[0-9]{6}"
                  class="form-input"
                  placeholder="123456"
                  style="font-size: 1.5rem; letter-spacing: 6px; text-align: center; font-weight: 900; color: #064e3b;"
                  autofocus
                />
              </div>

              <div class="form-group">
                <label class="form-label">{{ t('auth_reset_new_pwd_label') }}</label>
                <input
                  type="password"
                  v-model="resetNewPassword"
                  required
                  minlength="4"
                  class="form-input"
                  :placeholder="t('auth_register_password_ph')"
                />
              </div>

              <div class="form-group">
                <label class="form-label">{{ t('auth_reset_confirm_pwd_label') }}</label>
                <input
                  type="password"
                  v-model="resetConfirmPassword"
                  required
                  minlength="4"
                  class="form-input"
                  :placeholder="t('auth_register_password_ph')"
                />
              </div>

              <button type="submit" class="checkout-btn" :disabled="authSubmitting">
                {{ authSubmitting ? t('auth_btn_submitting') : t('auth_reset_btn') }}
              </button>

              <div style="display: flex; justify-content: space-between; align-items: center; margin-top: 12px; font-size: 0.8rem;">
                <button
                  type="button"
                  @click="handleResendResetOtp()"
                  :disabled="authSubmitting"
                  style="background: none; border: none; color: #047857; font-weight: 700; cursor: pointer; text-decoration: underline; padding: 0;"
                >
                  {{ t('auth_reset_resend_btn') }}
                </button>
                <button
                  type="button"
                  @click="resetStep = 1; authError = '';"
                  style="background: none; border: none; color: #64748b; font-weight: 600; cursor: pointer; padding: 0;"
                >
                  ← {{ currentLang === 'en' ? 'Change Phone / Email' : (currentLang === 'mr' ? 'नंबर / ईमेल बदला' : 'नंबर / ईमेल बदलें') }}
                </button>
              </div>
            </form>

            <div v-else style="text-align: center; margin-top: 12px;">
              <button
                type="button"
                @click="resetStep = 1; authError = '';"
                style="background: none; border: none; color: #64748b; font-weight: 700; font-size: 0.82rem; cursor: pointer;"
              >
                ← {{ currentLang === 'en' ? 'Back' : (currentLang === 'mr' ? 'मागे जा' : 'वापस जाएं') }}
              </button>
            </div>
          </div>

          <p style="margin-top: 14px; font-size: 0.82rem; text-align: center; color: var(--text-muted);">
            <a href="javascript:void(0)" @click="authMode = 'login'; authError = ''; resetStep = 1;" style="color: #047857; font-weight: 700; text-decoration: none;">
              {{ t('auth_back_to_login') }}
            </a>
          </p>
        </div>

        <!-- VIEW C: LOGIN FORM (CUSTOMER & ADMIN) -->
        <form v-else-if="authMode === 'login' || authMode === 'admin'" @submit.prevent="handleLogin">
          <!-- Admin Whitelist Banner -->
          <div v-if="authMode === 'admin'" style="background: #fffbeb; border: 1.5px solid #fef3c7; padding: 10px 14px; border-radius: 8px; font-size: 0.82rem; color: #92400e; margin-bottom: 14px;">
            {{ t('auth_admin_security_info') }}
          </div>

          <div class="form-group">
            <label class="form-label">
              {{ authMode === 'admin' ? t('auth_input_admin_email') : t('auth_input_identifier') }}
            </label>
            <input
              type="text"
              v-model="authForm.identifier"
              required
              class="form-input"
              :placeholder="authMode === 'admin' ? (currentLang === 'en' ? 'Enter admin email' : (currentLang === 'mr' ? 'अधिकृत ॲडमिन ईमेल टाका' : 'अधिकृत एडमिन ईमेल दर्ज करें')) : (currentLang === 'mr' ? '9876543299 किंवा email@example.com' : (currentLang === 'hi' ? '9876543299 या email@example.com' : '9876543299 or email@example.com'))"
            />
          </div>

          <div class="form-group">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 4px;">
              <label class="form-label" style="margin-bottom: 0;">{{ t('auth_input_password') }}</label>
              <a
                v-if="authMode !== 'admin'"
                href="javascript:void(0)"
                @click="authMode = 'reset_password'; authError = '';"
                style="font-size: 0.78rem; color: #047857; font-weight: 700; text-decoration: none;"
              >
                {{ t('auth_forgot_password') }}
              </a>
            </div>
            <input
              type="password"
              v-model="authForm.password"
              required
              class="form-input"
              :placeholder="authMode === 'admin' ? (currentLang === 'en' ? 'Enter password' : (currentLang === 'mr' ? 'पासवर्ड टाका' : 'पासवर्ड दर्ज करें')) : t('auth_register_password_ph')"
            />
          </div>

          <button type="submit" class="checkout-btn" :disabled="authSubmitting">
            {{ authSubmitting ? t('auth_btn_submitting') : (authMode === 'admin' ? t('auth_btn_admin_login') : t('auth_btn_login')) }}
          </button>

          <p v-if="authMode === 'login'" style="margin-top: 14px; font-size: 0.82rem; text-align: center; color: var(--text-muted);">
            <a href="javascript:void(0)" @click="openAuthModal('admin')" style="color: #d97706; font-weight: 700; text-decoration: none;">
              🔐 {{ currentLang === 'mr' ? 'दुकानदार / ॲडमिन पोर्टल लॉगिन' : (currentLang === 'hi' ? 'दुकानदार / एडमिन पोर्टल लॉगिन' : 'Store Owner / Admin Portal Access') }}
            </a>
          </p>
          <p v-else-if="authMode === 'admin'" style="margin-top: 14px; font-size: 0.82rem; text-align: center; color: var(--text-muted);">
            <a href="javascript:void(0)" @click="openAuthModal('login')" style="color: #047857; font-weight: 700; text-decoration: none;">
              👤 {{ currentLang === 'mr' ? 'ग्राहक लॉगिनकडे परत जा' : (currentLang === 'hi' ? 'ग्राहक लॉगिन पर वापस जाएं' : 'Back to Customer Login') }}
            </a>
          </p>
        </form>

        <!-- VIEW D: REGISTER FORM (CUSTOMER) -->
        <form v-else @submit.prevent="handleRegister">
          <div class="form-group">
            <label class="form-label">{{ t('auth_register_name') }}</label>
            <input type="text" v-model="registerForm.name" required class="form-input" :placeholder="t('auth_register_name_ph')" />
          </div>

          <div class="form-group">
            <label class="form-label">{{ t('auth_register_username') }}</label>
            <input type="text" v-model="registerForm.username" pattern="[a-zA-Z0-9_.-]{3,30}" class="form-input" :placeholder="t('auth_register_username_ph')" />
          </div>

          <div class="form-group">
            <label class="form-label">{{ t('auth_register_phone') }} <span style="color: #dc2626;">*</span></label>
            <input
              type="tel"
              v-model="registerForm.phone"
              required
              maxlength="10"
              pattern="[6-9][0-9]{9}"
              class="form-input"
              :placeholder="t('auth_register_phone_ph')"
            />
            <span style="font-size: 0.72rem; color: var(--text-muted);">{{ t('auth_register_phone_hint') }}</span>
          </div>

          <div class="form-group">
            <label class="form-label">
              {{ t('auth_register_email') }} <span style="font-size: 0.76rem; color: #64748b; font-weight: 600;">({{ currentLang === 'en' ? 'Optional' : (currentLang === 'mr' ? 'ऐच्छिक' : 'ऐच्छिक') }})</span>
            </label>
            <input type="email" v-model="registerForm.email" class="form-input" placeholder="naam@gmail.com" />
            <span style="font-size: 0.72rem; color: #047857; font-weight: 600;">
              {{ currentLang === 'en' ? '💡 Tip: Adding an email enables instant 24/7 automated password reset (Email OTP) & digital receipts.' : (currentLang === 'mr' ? '💡 टीप: २४/७ त्वरित पासवर्ड रीसेट (ईमेल OTP) आणि बिलासाठी ईमेल जोडणे फायद्याचे ठरेल.' : '💡 सुझाव: 24/7 तत्काल पासवर्ड रीसेट (ईमेल OTP) और बिल के लिए ईमेल जोड़ना सुविधाजनक रहेगा।') }}
            </span>
          </div>

          <div class="form-group">
            <label class="form-label">{{ t('auth_register_password') }}</label>
            <input type="password" v-model="registerForm.password" required minlength="4" class="form-input" :placeholder="t('auth_register_password_ph')" />
          </div>

          <div class="form-group">
            <label class="form-label">{{ t('auth_register_address') }}</label>
            <textarea v-model="registerForm.address" rows="2" class="form-input" :placeholder="t('auth_register_address_ph')"></textarea>
          </div>

          <button type="submit" class="checkout-btn" :disabled="authSubmitting">
            {{ authSubmitting ? t('auth_btn_submitting') : t('auth_btn_register') }}
          </button>
        </form>
      </div>
    </div>

    <!-- ======================================================== -->
    <!-- SLIDING CART DRAWER                                      -->
    <!-- ======================================================== -->
    <div class="cart-drawer-overlay" v-if="isCartOpen" @click.self="isCartOpen = false">
      <div class="cart-drawer">
        <div class="cart-header">
          <h2 style="font-size: 1.2rem; font-weight: 900; color: #064e3b; display: flex; align-items: center; gap: 8px;">
            🛒 {{ t('cart_title') }}
          </h2>
          <button class="close-btn" @click="isCartOpen = false">✕</button>
        </div>

        <!-- Free Delivery Progress Meter -->
        <div class="free-delivery-meter" v-if="cart.length > 0">
          <div class="meter-text-row">
            <span v-if="Number(cartTotalAmount) < DELIVERY_FREE_THRESHOLD">
              🛵 {{ t('free_delivery_need') }} <strong>₹{{ (DELIVERY_FREE_THRESHOLD - Number(cartTotalAmount)).toFixed(2) }}</strong> {{ t('free_delivery_reach') }} <strong>{{ t('free_delivery_text') }}</strong>
            </span>
            <span v-else style="color: #064e3b; font-weight: 800;">
              🎉 {{ t('free_delivery_success') }}
            </span>
            <span class="meter-pct-badge">{{ Math.min(100, Math.round((Number(cartTotalAmount) / DELIVERY_FREE_THRESHOLD) * 100)) }}%</span>
          </div>
          <div class="meter-track">
            <div
              class="meter-bar"
              :class="{ completed: Number(cartTotalAmount) >= DELIVERY_FREE_THRESHOLD }"
              :style="{ width: Math.min(100, Math.round((Number(cartTotalAmount) / DELIVERY_FREE_THRESHOLD) * 100)) + '%' }"
            ></div>
          </div>
        </div>

        <!-- Smart Add-ons for Free Delivery -->
        <div class="cart-addons-section" v-if="cart.length > 0 && Number(cartTotalAmount) < DELIVERY_FREE_THRESHOLD && smartAddons.length > 0">
          <div class="cart-addons-header">
            <span class="addons-title">{{ t('free_delivery_addons_title') }}</span>
            <span class="addons-fee-tag">₹{{ DELIVERY_STANDARD_FEE }} {{ t('delivery_charge_label') }}</span>
          </div>
          <p class="addons-subtext">
            {{ t('under_threshold_warning') }}
          </p>
          <div class="cart-addons-slider">
            <div
              v-for="addon in smartAddons"
              :key="addon.id"
              class="addon-chip-card"
            >
              <img
                :src="addon.image_url"
                :alt="addon.name"
                class="addon-chip-img"
                @error="handleImageFallback($event)"
              />
              <div class="addon-chip-info">
                <div class="addon-chip-name">{{ getLocalizedProductName(addon, currentLang) }}</div>
                <div class="addon-chip-unit" v-if="addon.variants && addon.variants[0]">{{ addon.variants[0].unit_size }}</div>
                <div class="addon-chip-pricing">
                  <span class="addon-chip-price">₹{{ addon.variants[0].selling_price }}</span>
                  <span class="addon-chip-mrp" v-if="addon.variants[0].mrp > addon.variants[0].selling_price">₹{{ addon.variants[0].mrp }}</span>
                </div>
              </div>
              <button
                class="addon-quick-add-btn"
                @click="addToCart(addon, addon.variants[0])"
                :title="currentLang === 'en' ? 'Add to cart' : (currentLang === 'mr' ? 'थैलीत जोडा' : 'थैली में जोड़ें')"
              >
                + {{ currentLang === 'mr' ? 'जोडा' : (currentLang === 'hi' ? 'जोड़ें' : 'Add') }}
              </button>
            </div>
          </div>
        </div>

        <!-- Empty Cart -->
        <div v-if="cart.length === 0" style="flex: 1; display: flex; flex-direction: column; align-items: center; justify-content: center; padding: 30px; text-align: center;">
          <div style="font-size: 3.5rem; margin-bottom: 12px;">🧺</div>
          <h4 style="font-size: 1.15rem; font-weight: 800;">{{ t('cart_empty_title') }}</h4>
          <p style="color: var(--text-subtle); font-size: 0.9rem; margin-top: 4px;">
            {{ t('cart_empty_desc') }}
          </p>
          <button
            @click="isCartOpen = false"
            style="margin-top: 18px; padding: 10px 22px; background: #047857; color: white; border: none; border-radius: 10px; font-weight: 800; cursor: pointer;"
          >
            {{ t('start_shopping') }}
          </button>
        </div>

        <!-- Cart Items List -->
        <div v-else class="cart-items-list">
          <div v-for="item in cart" :key="item.is_custom_weight ? item.id : item.variant.id" class="cart-item">
            <!-- If custom weight item -->
            <template v-if="item.is_custom_weight">
              <div style="flex: 1;">
                <h4 style="font-size: 0.92rem; font-weight: 800; color: #1c1917;">{{ item.product.name }}</h4>
                <div style="font-size: 0.8rem; color: #b45309; font-weight: 700;">
                  🌾 {{ item.custom_unit_size }} @ ₹{{ item.unit_price }}/kg
                </div>
                <div style="font-size: 0.9rem; font-weight: 800; color: #047857; margin-top: 4px;">
                  {{ t('custom_total_label') }} <strong>₹{{ item.subtotal.toFixed(2) }}</strong>
                  <span v-if="item.quantity > 1" style="font-size: 0.78rem; color: var(--text-muted);">
                    ({{ item.quantity }}x)
                  </span>
                </div>
              </div>
              <div class="qty-control-row">
                <button class="qty-btn" @click="decreaseQuantity(item.id)">-</button>
                <span class="qty-display">{{ item.quantity }}</span>
                <button class="qty-btn" @click="increaseQuantity(item.id)">+</button>
              </div>
            </template>

            <!-- Standard variant item -->
            <template v-else>
              <div style="flex: 1;">
                <h4 style="font-size: 0.92rem; font-weight: 800; color: #1c1917;">{{ item.product.name }}</h4>
                <div style="font-size: 0.8rem; color: #c2410c; font-weight: 600;">{{ item.variant.unit_size }}</div>
                <div style="font-size: 0.9rem; font-weight: 800; color: #047857; margin-top: 4px;">
                  <template v-if="adminAllowClearancePublic && item.variant.is_clearance && item.variant.clearance_price">
                    <span style="color: #dc2626;">₹{{ item.variant.clearance_price }}</span> <span style="font-size: 0.78rem; text-decoration: line-through; color: #94a3b8;">₹{{ item.variant.mrp }}</span> × {{ item.quantity }} =
                    <strong style="color: #dc2626;">₹{{ (item.variant.clearance_price * item.quantity).toFixed(2) }}</strong>
                    <span style="font-size: 0.7rem; background: #fee2e2; color: #b91c1c; padding: 1px 5px; border-radius: 4px; margin-left: 4px;">💥 ऑफर</span>
                  </template>
                  <template v-else>
                    ₹{{ item.variant.selling_price }} × {{ item.quantity }} =
                    <strong>₹{{ (item.variant.selling_price * item.quantity).toFixed(2) }}</strong>
                  </template>
                </div>
              </div>
              <div class="qty-control-row">
                <button class="qty-btn" @click="decreaseQuantity(item.variant.id)">-</button>
                <span class="qty-display">{{ item.quantity }}</span>
                <button class="qty-btn" @click="increaseQuantity(item.variant.id)">+</button>
              </div>
            </template>
          </div>
        </div>

        <!-- Cart Footer -->
        <div class="cart-footer" v-if="cart.length > 0">
          <div class="bill-summary">
            <div class="bill-row">
              <span>{{ t('mrp_total') }}</span>
              <span>₹{{ cartTotalMrp }}</span>
            </div>
            <div class="bill-row savings">
              <span>{{ t('kirana_savings') }}</span>
              <span>- ₹{{ cartTotalSavings }}</span>
            </div>
            <div class="bill-row delivery-row">
              <span>{{ t('delivery_charge_label') }}</span>
              <span v-if="deliveryFee === 0" style="color: #059669; font-weight: 800;">
                {{ t('delivery_free_badge') }}
              </span>
              <span v-else style="font-weight: 800; color: #b45309;">
                ₹{{ deliveryFee.toFixed(2) }}
              </span>
            </div>
            <div class="bill-row total">
              <span>{{ t('payable_amount') }}</span>
              <span>₹{{ cartPayableWithDelivery }}</span>
            </div>
            <div v-if="estimatedEarnedCredit > 0" class="store-credit-earn-note">
              💳 {{ t('you_will_earn_credit') }} <strong>₹{{ estimatedEarnedCredit.toFixed(2) }} {{ t('store_credit') }}</strong>
            </div>
          </div>

          <button class="checkout-btn" @click="openCheckoutModal">
            📝 {{ t('proceed_checkout') }} (₹{{ cartPayableWithDelivery }})
          </button>
        </div>
      </div>
    </div>

    <!-- ======================================================== -->
    <!-- CHECKOUT MODAL                                           -->
    <!-- ======================================================== -->
    <div class="modal-overlay" v-if="showCheckoutModal" @click.self="showCheckoutModal = false">
      <div class="modal-card">
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 16px;">
          <h3 style="font-size: 1.25rem; font-weight: 900; color: #064e3b;">
            📝 {{ t('checkout_title') }}
          </h3>
          <button class="close-btn" @click="showCheckoutModal = false">✕</button>
        </div>

        <form @submit.prevent="submitOrder">
          <div class="form-group">
            <label class="form-label">{{ t('cust_name_label') }}</label>
            <input type="text" v-model="customerForm.name" required class="form-input" />
          </div>

          <div class="form-group">
            <label class="form-label">{{ t('cust_phone_label') }}</label>
            <input type="tel" v-model="customerForm.phone" required pattern="[0-9]{10}" class="form-input" />
          </div>

          <!-- Delivery Mode: Express Home Delivery vs Store Pickup -->
          <div class="form-group" style="margin-bottom: 14px;">
            <label class="form-label" style="font-weight: 800; color: #064e3b; margin-bottom: 8px; display: block;">
              🛵 {{ currentLang === 'en' ? 'Choose Fulfillment Mode:' : (currentLang === 'mr' ? 'डिलिव्हरी प्रकार निवडा:' : 'डिलीवरी का प्रकार चुनें:') }}
            </label>
            <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 8px;">
              <button
                type="button"
                @click="customerForm.deliveryType = 'home_delivery'"
                :style="customerForm.deliveryType === 'home_delivery' ? 'background: #ecfdf5; border: 2px solid #059669; color: #064e3b; font-weight: 900;' : 'background: #f8fafc; border: 1.5px solid #cbd5e1; color: #64748b; font-weight: 700;'"
                style="padding: 10px 8px; border-radius: 10px; cursor: pointer; font-size: 0.84rem; text-align: center; transition: all 0.2s;"
              >
                {{ t('delivery_type_home') }}
              </button>
              <button
                type="button"
                @click="customerForm.deliveryType = 'store_pickup'"
                :style="customerForm.deliveryType === 'store_pickup' ? 'background: #ecfdf5; border: 2px solid #059669; color: #064e3b; font-weight: 900;' : 'background: #f8fafc; border: 1.5px solid #cbd5e1; color: #64748b; font-weight: 700;'"
                style="padding: 10px 8px; border-radius: 10px; cursor: pointer; font-size: 0.84rem; text-align: center; transition: all 0.2s;"
              >
                {{ t('delivery_type_pickup') }}
              </button>
            </div>
          </div>

          <template v-if="customerForm.deliveryType === 'home_delivery'">
            <!-- Wadala Area & Pincode Selector -->
            <div class="form-group" style="margin-bottom: 12px;">
              <label class="form-label" style="font-weight: 800; color: #064e3b;">
                📍 {{ t('delivery_zone_title') }} <span style="color: #ef4444;">*</span>
              </label>
              <select v-model="customerForm.pincode" class="form-input" style="font-weight: 700;">
                <option v-for="area in WADALA_SERVICEABLE_AREAS" :key="area.pincode" :value="area.pincode">
                  {{ areaDeliveryHolds[area.pincode]?.is_held ? '⏳ ' : '' }}{{ currentLang === 'en' ? area.name_en : (currentLang === 'mr' ? area.name_mr : area.name_hi) }}{{ areaDeliveryHolds[area.pincode]?.is_held ? ' (तात्पुरती होल्ड / Delayed)' : '' }}
                </option>
                <option value="other">{{ currentLang === 'en' ? 'Other Pincode (Outside Wadala Zone)' : (currentLang === 'mr' ? 'इतर पिनकोड (वडाळा परिसराबाहेर)' : 'अन्य पिनकोड (वडाला क्षेत्र से बाहर)') }}</option>
              </select>
            </div>

            <!-- Soft Area Hold Alert (Customer can still order, but knows it will be delivered tomorrow/next schedule) -->
            <div v-if="activeSelectedAreaHold" style="background: #fffbeb; border: 1.5px solid #fde68a; border-radius: 10px; padding: 12px 14px; margin-bottom: 14px;">
              <div style="display: flex; align-items: flex-start; gap: 8px;">
                <span style="font-size: 1.3rem; line-height: 1;">🛵⏳</span>
                <div>
                  <div style="font-weight: 900; color: #92400e; font-size: 0.88rem; margin-bottom: 2px;">
                    {{ currentLang === 'en' ? 'Temporary Delivery Delay in this Area' : (currentLang === 'mr' ? 'या परिसरातील डिलिव्हरी तात्पुरती पुढील वेळेसाठी राखीव' : 'इस क्षेत्र में डिलीवरी अस्थायी रूप से होल्ड पर है') }}
                  </div>
                  <p style="margin: 0; font-size: 0.8rem; color: #78350f; line-height: 1.45;">
                    {{ currentLang === 'en' 
                      ? 'Due to a temporary delivery staff shortage, orders for this area will be dispatched by tomorrow morning. You can still place your order now, and we will safely reserve your items!'
                      : (currentLang === 'mr'
                        ? 'डिलिव्हरी बॉयच्या तात्पुरत्या अडचणीमुळे या भागातील डिलिव्हरी ' + (activeSelectedAreaHold.resume || 'उद्या सकाळपर्यंत') + ' नियोजित केली जाईल. आपण आताच ऑर्डर नोंदवू शकता, आपले सर्व सामान सुरक्षित बाजूला ठेवले जाईल!'
                        : 'डिलीवरी स्टाफ की अस्थायी कमी के कारण इस क्षेत्र की डिलीवरी ' + (activeSelectedAreaHold.resume || 'कल सुबह तक') + ' की जाएगी। आप अभी ऑर्डर बुक कर सकते हैं, आपका सामान सुरक्षित पैक रहेगा!') }}
                  </p>
                  <div style="margin-top: 8px; display: flex; gap: 8px; flex-wrap: wrap;">
                    <span style="background: #fef3c7; border: 1px dashed #d97706; padding: 2px 8px; border-radius: 4px; font-size: 0.75rem; font-weight: 800; color: #b45309;">
                      ✅ {{ currentLang === 'en' ? 'Order will be safely held & dispatched tomorrow' : (currentLang === 'mr' ? 'ऑर्डर सुरक्षित ठेवून उद्या पोहोचवली जाईल' : 'ऑर्डर सुरक्षित रखकर कल डिलीवर होगी') }}
                    </span>
                    <button
                      type="button"
                      @click="customerForm.deliveryType = 'store_pickup'"
                      style="background: #059669; color: white; border: none; padding: 3px 8px; border-radius: 4px; font-weight: 800; font-size: 0.74rem; cursor: pointer;"
                    >
                      🏬 {{ currentLang === 'en' ? 'Pick up from Wadala Shop Today' : (currentLang === 'mr' ? 'आजच दुकानातून पिकअप करा' : 'आज दुकान से ले जाएं') }}
                    </button>
                  </div>
                </div>
              </div>
            </div>

            <!-- Warning if not serviceable -->
            <div v-if="!isPincodeServiceable" style="background: #fef2f2; border: 1.5px solid #fecaca; border-radius: 10px; padding: 12px; margin-bottom: 14px;">
              <div style="color: #991b1b; font-weight: 800; font-size: 0.86rem; line-height: 1.45;">
                {{ t('delivery_pincode_error') }}
              </div>
              <button
                type="button"
                @click="customerForm.deliveryType = 'store_pickup'"
                style="margin-top: 8px; background: #059669; color: white; border: none; padding: 6px 12px; border-radius: 6px; font-weight: 800; font-size: 0.82rem; cursor: pointer;"
              >
                🏬 {{ currentLang === 'en' ? 'Switch to Store Pickup (Free)' : (currentLang === 'mr' ? 'दुकान पिकअप निवडा (मोफत)' : 'दुकान पिकअप चुनें (मुफ़्त)') }}
              </button>
            </div>

            <div class="form-group">
              <label class="form-label">{{ t('cust_address_label') }}</label>
              <textarea v-model="customerForm.address" required rows="2" class="form-input" placeholder="मकान नं, बिल्डिंग, गल्ली, लँडमार्क"></textarea>
            </div>

            <!-- Delivery Slot Selector -->
            <div class="form-group">
              <label class="form-label">⏰ {{ t('delivery_slot_title') }}</label>
              <div class="delivery-slots-grid">
                <div
                  v-for="slot in deliverySlotOptions"
                  :key="slot.id"
                  class="delivery-slot-card"
                  :class="{ 
                    active: customerForm.deliverySlot === slot.id || customerForm.deliverySlot === slot.label,
                    'urgent-card': slot.id === 'urgent' || slot.id === 'instant'
                  }"
                  @click="customerForm.deliverySlot = slot.id"
                >
                  <div class="slot-icon">{{ slot.icon }}</div>
                  <div class="slot-details">
                    <div class="slot-label">{{ slot.title }}</div>
                    <div class="slot-desc">{{ slot.desc }}</div>
                  </div>
                  <div class="slot-check-icon" v-if="customerForm.deliverySlot === slot.id || customerForm.deliverySlot === slot.label">✓</div>
                </div>
              </div>

              <!-- Accidental Click / Priority Notice for Urgent 30-min Delivery -->
              <div
                v-if="isUrgentDelivery"
                class="urgent-express-callout"
              >
                <div class="urgent-express-callout-header">
                  <span class="urgent-bolt">⚡</span>
                  <strong>{{ currentLang === 'en' ? 'Urgent Express Surcharge Notice' : (currentLang === 'mr' ? 'तातडीची एक्सप्रेस डिलिव्हरी सूचना' : 'ज़रूरी एक्सप्रेस डिलीवरी सूचना') }}</strong>
                </div>
                <p class="urgent-express-callout-text">
                  {{ currentLang === 'en'
                    ? 'Under 30-minute delivery requires dedicated immediate dispatch and carries an express priority fee of ₹50.'
                    : (currentLang === 'mr'
                      ? '३० मिनिटांच्या आत तातडीच्या डिलिव्हरीसाठी विशेष रायडरची सोय केली जाते, यासाठी ₹५० एक्सप्रेस प्राधान्य शुल्क आकारले जाईल.'
                      : '30 मिनट के भीतर तुरंत डिलीवरी के लिए विशेष राइडर भेजा जाता है, इसके लिए ₹50 एक्सप्रेस प्राथमिकता शुल्क लगेगा।')
                  }}
                </p>
                <button
                  type="button"
                  class="urgent-express-switch-btn"
                  @click="customerForm.deliverySlot = 'standard'"
                >
                  {{ currentLang === 'en'
                    ? '← Switch to Standard Delivery (Free on ₹500+)'
                    : (currentLang === 'mr'
                      ? '← प्रमाणित डिलिव्हरीत बदला (₹५००+ वर मोफत)'
                      : '← सामान्य स्टैंडर्ड डिलीवरी चुनें (₹500+ पर मुफ़्त)')
                  }}
                </button>
              </div>
            </div>
          </template>

          <template v-else>
            <!-- Store Pickup Info Box -->
            <div style="background: #f0fdf4; border: 1.5px solid #bbf7d0; border-radius: 12px; padding: 14px; margin-bottom: 16px;">
              <div style="font-weight: 900; color: #166534; font-size: 0.95rem; margin-bottom: 4px; display: flex; align-items: center; gap: 6px;">
                🏬 {{ currentLang === 'en' ? 'Store Counter Pickup (Free)' : (currentLang === 'mr' ? 'दुकान काउंटरवरून स्वतः उचलणे (मोफत)' : 'दुकान काउंटर से स्वयं पिकअप (मुफ़्त)') }}
              </div>
              <div style="font-size: 0.86rem; color: #1e293b; font-weight: 700; margin-bottom: 4px;">
                📍 {{ t('pickup_store_address') }}
              </div>
              <div style="font-size: 0.8rem; color: #475569; line-height: 1.4;">
                ⏱️ {{ t('pickup_note') }}
              </div>
            </div>
          </template>

          <div class="form-group">
            <label class="form-label">{{ t('payment_method_label') }}</label>
            <select v-model="customerForm.paymentMethod" class="form-input">
              <option value="Cash on Delivery (COD)">💵 {{ t('pay_cod') }}</option>
              <option value="UPI / QR Code">📱 {{ t('pay_upi') }}</option>
            </select>
          </div>

          <!-- COD Notice -->
          <div v-if="customerForm.paymentMethod === 'Cash on Delivery (COD)'" class="payment-notice-banner cod-banner">
            <div style="font-weight: 800; color: #92400e; font-size: 0.88rem; margin-bottom: 2px;">
              💵 {{ t('cod_notice_title') }}
            </div>
            <div style="font-size: 0.8rem; color: #78350f;">
              {{ t('cod_notice_desc') }}
            </div>
          </div>

          <!-- Shop Owner UPI QR Code Display -->
          <!-- Shop Owner UPI Payment Guidance -->
          <div v-if="customerForm.paymentMethod === 'UPI / QR Code'" class="upi-qr-card" style="background: #f0fdf4; border: 1.5px solid #86efac; border-radius: 12px; padding: 14px; text-align: center;">
            <div style="font-size: 2rem; margin-bottom: 4px;">📱</div>
            <h4 style="color: #065f46; font-size: 1rem; font-weight: 800; margin: 0 0 6px;">
              {{ currentLang === 'en' ? 'Pay via UPI (GPay • PhonePe • Paytm • BHIM)' : (currentLang === 'mr' ? 'UPI द्वारे पेमेंट (GPay • PhonePe • Paytm • BHIM)' : 'UPI द्वारा भुगतान (GPay • PhonePe • Paytm • BHIM)') }}
            </h4>
            <p style="font-size: 0.82rem; color: #166534; margin: 0 0 8px; line-height: 1.4;">
              {{ currentLang === 'en' ? 'Click below to place order. Your unique order ticket and 1-tap UPI payment screen will open immediately.' : (currentLang === 'mr' ? 'खाली क्लिक करून ऑर्डर नोंदवा. तुमचा नंबर व १-टॅप UPI पेमेंट स्क्रीन त्वरित उघडेल.' : 'नीचे क्लिक करके ऑर्डर दर्ज करें। आपका बिल नंबर और १-टैप UPI पेमेंट स्क्रीन तुरंत खुलेगी।') }}
            </p>
            <div style="background: white; border: 1px dashed #10b981; border-radius: 8px; padding: 6px 10px; font-size: 0.82rem; color: #047857; font-weight: 700;">
              ✨ {{ currentLang === 'en' ? 'Instant Soundbox & SMS Verification at Shop Counter' : (currentLang === 'mr' ? 'दुकान काऊंटरवर त्वरित साऊंडबॉक्स व SMS पडताळणी' : 'दुकान काउंटर पर त्वरित साउंडबॉक्स व SMS सत्यापन') }}
            </div>
          </div>

          <!-- Store Credit Redemption Box (If Logged In & Has Balance) -->
          <div v-if="currentUser && (currentUser.wallet_balance || 0) > 0" class="store-credit-checkout-box">
            <label class="store-credit-toggle">
              <span class="store-credit-toggle-label">
                <input type="checkbox" v-model="useStoreCredit" />
                <span>💳 {{ t('use_store_credit') }}</span>
              </span>
              <span class="store-credit-avail">
                {{ t('store_credit_balance') }}: ₹{{ (currentUser.wallet_balance || 0).toFixed(2) }}
              </span>
            </label>
            <div v-if="useStoreCredit && appliedCreditAmount > 0" class="store-credit-applied-row">
              <span>{{ t('store_credit_applied') }}:</span>
              <span>- ₹{{ appliedCreditAmount.toFixed(2) }}</span>
            </div>
          </div>

          <div style="background: #ecfdf5; border: 1.5px solid #a7f3d0; border-radius: 10px; padding: 14px; margin-bottom: 18px;">
            <div style="display: flex; justify-content: space-between; font-size: 0.88rem; color: var(--text-muted); margin-bottom: 6px;">
              <span>{{ t('cart_bag') }}:</span>
              <span>₹{{ cartTotalAmount }}</span>
            </div>
            <div style="display: flex; justify-content: space-between; font-size: 0.88rem; margin-bottom: 6px;">
              <span>{{ t('delivery_charge_label') }}:</span>
              <span v-if="deliveryFee === 0" style="color: #059669; font-weight: 800;">{{ t('delivery_free_badge') }}</span>
              <span v-else style="font-weight: 700; color: #b45309;">₹{{ deliveryFee.toFixed(2) }}</span>
            </div>
            <div v-if="useStoreCredit && appliedCreditAmount > 0" style="display: flex; justify-content: space-between; font-size: 0.88rem; color: #047857; font-weight: 800; margin-bottom: 6px;">
              <span>💳 {{ t('store_credit_applied') }}:</span>
              <span>- ₹{{ appliedCreditAmount.toFixed(2) }}</span>
            </div>
            <div style="display: flex; justify-content: space-between; font-weight: 900; color: #064e3b; font-size: 1.15rem; border-top: 1px dashed #a7f3d0; padding-top: 8px; margin-top: 4px;">
              <span>{{ t('payable_amount') }}:</span>
              <span>₹{{ finalPayableAmount }}</span>
            </div>
            <div style="font-size: 0.84rem; color: #047857; font-weight: 700; margin-top: 4px;">
              🎉 {{ t('order_savings_text') }}: ₹{{ cartTotalSavings }}!
            </div>
            <div v-if="estimatedEarnedCredit > 0" class="store-credit-earn-note" style="margin-top: 6px;">
              💳 {{ t('you_will_earn_credit') }} <strong>₹{{ estimatedEarnedCredit.toFixed(2) }} {{ t('store_credit') }}</strong>
            </div>
          </div>

          <button
            type="submit"
            :disabled="orderSubmitting || !isPincodeServiceable"
            class="checkout-btn"
            :style="!isPincodeServiceable ? 'opacity: 0.6; cursor: not-allowed;' : ''"
          >
            <span v-if="!isPincodeServiceable">🚫 {{ currentLang === 'en' ? 'Delivery Unavailable Outside Wadala' : (currentLang === 'mr' ? 'वडाळा परिसराबाहेर डिलिव्हरी अनुपलब्ध' : 'वडाला क्षेत्र से बाहर डिलीवरी अनुपलब्ध') }}</span>
            <span v-else-if="orderSubmitting">{{ t('placing_order') }}</span>
            <span v-else-if="customerForm.paymentMethod === 'UPI / QR Code'">📲 {{ currentLang === 'en' ? 'Place Order & Pay via UPI' : (currentLang === 'mr' ? 'ऑर्डर नोंदवा आणि UPI ने पे करा' : 'ऑर्डर दर्ज करें और UPI पे करें') }} (₹{{ finalPayableAmount }})</span>
            <span v-else>✅ {{ t('place_order_btn') }} (₹{{ finalPayableAmount }})</span>
          </button>
        </form>
      </div>
    </div>

    <!-- ======================================================== -->
    <!-- 1-TAP DELIVERY AVAILABILITY CONFIRMATION MODAL           -->
    <!-- ======================================================== -->
    <div class="modal-overlay" v-if="showDeliveryCheckModal && deliveryCheckOrder" @click.self="showDeliveryCheckModal = false">
      <div class="modal-card" style="max-width: 440px; text-align: center; padding: 24px;">
        <div style="font-size: 3rem; margin-bottom: 8px;">🛵💨</div>
        <h3 style="font-size: 1.25rem; font-weight: 900; color: #064e3b; margin: 0 0 8px;">
          {{ currentLang === 'en' ? 'Delivery Availability Check' : (currentLang === 'mr' ? 'डिलिव्हरी उपलब्धता पडताळणी' : 'डिलीवरी उपलब्धता पुष्टि') }}
        </h3>
        <p style="font-size: 0.9rem; color: #475569; margin: 0 0 16px; line-height: 1.4;">
          {{ currentLang === 'en'
            ? `Hello ${deliveryCheckOrder.customer_name}! Your order #${deliveryCheckOrder.order_number} (₹${deliveryCheckOrder.final_amount}) is out for delivery. Are you available at your address?`
            : (currentLang === 'mr'
              ? `नमस्ते ${deliveryCheckOrder.customer_name}! तुमचा ऑर्डर #${deliveryCheckOrder.order_number} (₹${deliveryCheckOrder.final_amount}) डिलिव्हरीसाठी निघाला आहे. तुम्ही घरी उपलब्ध आहात का?`
              : `नमस्ते ${deliveryCheckOrder.customer_name}! आपका ऑर्डर #${deliveryCheckOrder.order_number} (₹${deliveryCheckOrder.final_amount}) डिलीवरी के लिए निकल चुका है। क्या आप घर पर उपलब्ध हैं?`)
          }}
        </p>

        <!-- Current Status Banner if already answered -->
        <div v-if="deliveryCheckOrder.delivery_availability === 'available'" style="background: #dcfce7; border: 1.5px solid #86efac; border-radius: 10px; padding: 12px; margin-bottom: 16px;">
          <div style="font-weight: 900; color: #166534; font-size: 0.95rem;">
            🟢 {{ currentLang === 'en' ? 'Availability Confirmed!' : (currentLang === 'mr' ? 'उपलब्धता नोंदवली!' : 'उपलब्धता दर्ज!') }}
          </div>
          <div style="font-size: 0.82rem; color: #15803d; margin-top: 4px;">
            {{ currentLang === 'en' ? 'Our delivery boy is on the way to your doorstep.' : (currentLang === 'mr' ? 'डिलिव्हरी पार्टनर तात्काळ आपल्या पत्त्यावर पोहोचत आहे.' : 'हमारा डिलीवरी पार्टनर आपके पते पर पहुँच रहा है।') }}
          </div>
        </div>
        <div v-else-if="deliveryCheckOrder.delivery_availability === 'reschedule'" style="background: #fef3c7; border: 1.5px solid #fde047; border-radius: 10px; padding: 12px; margin-bottom: 16px;">
          <div style="font-weight: 900; color: #854d0e; font-size: 0.95rem;">
            ⏳ {{ currentLang === 'en' ? 'Reschedule Requested' : (currentLang === 'mr' ? 'नंतर पाठवण्याची नोंद' : 'बाद में भेजने का अनुरोध दर्ज') }}
          </div>
          <div style="font-size: 0.82rem; color: #a16207; margin-top: 4px;">
            {{ currentLang === 'en' ? 'Store will call you shortly to arrange a convenient delivery time.' : (currentLang === 'mr' ? 'दुकानदार लवकरच कॉल करून नवीन वेळ ठरवतील.' : 'स्टोर टीम कॉल करके सुविधानुसार समय तय करेगी।') }}
          </div>
        </div>

        <!-- Active Delivery Add-on Banner in Delivery Check Modal -->
        <div
          v-if="canAddToActiveOrder(deliveryCheckOrder)"
          style="background: #f0fdf4; border: 1.5px dashed #16a34a; border-radius: 12px; padding: 12px; margin-bottom: 16px; text-align: left;"
        >
          <div style="font-weight: 900; color: #166534; font-size: 0.9rem; display: flex; align-items: center; gap: 6px;">
            ⚡ <span>{{ t('active_addon_title') }}</span>
          </div>
          <div style="font-size: 0.8rem; color: #15803d; margin: 4px 0 10px;">
            {{ t('active_addon_sub') }}
          </div>
          <button
            type="button"
            @click="openAddActiveItemModal(deliveryCheckOrder)"
            style="width: 100%; background: #16a34a; color: white; border: none; padding: 10px; border-radius: 8px; font-weight: 800; font-size: 0.88rem; cursor: pointer; display: flex; align-items: center; justify-content: center; gap: 6px; box-shadow: 0 2px 6px rgba(22, 163, 74, 0.25);"
          >
            <span>➕</span>
            <span>{{ t('active_addon_btn') }}</span>
          </button>
        </div>

        <!-- 1-Tap Action Buttons -->
        <div style="display: flex; flex-direction: column; gap: 10px;">
          <button
            type="button"
            :disabled="deliveryCheckSubmitting"
            @click="confirmOrderAvailability(deliveryCheckOrder.order_number, 'available')"
            style="background: #059669; color: white; border: none; padding: 14px 18px; border-radius: 12px; font-weight: 900; font-size: 1rem; cursor: pointer; display: flex; align-items: center; justify-content: center; gap: 8px; box-shadow: 0 4px 12px rgba(5, 150, 105, 0.25);"
          >
            <span>{{ deliveryCheckSubmitting ? '⏳ ...' : '✅' }}</span>
            <span>{{ t('delivery_avail_confirm_btn') }}</span>
          </button>
          <button
            type="button"
            :disabled="deliveryCheckSubmitting"
            @click="confirmOrderAvailability(deliveryCheckOrder.order_number, 'reschedule')"
            style="background: #f8fafc; color: #475569; border: 1.5px solid #cbd5e1; padding: 12px 18px; border-radius: 12px; font-weight: 700; font-size: 0.9rem; cursor: pointer;"
          >
            {{ t('delivery_avail_reschedule_btn') }}
          </button>
        </div>

        <div style="margin-top: 16px; border-top: 1px solid #f1f5f9; padding-top: 12px; display: flex; justify-content: space-between; align-items: center; font-size: 0.8rem; color: #64748b;">
          <span>📞 Store Helpline: <a href="tel:9142052967" style="color: #059669; font-weight: 700; text-decoration: none;">91420-52967</a></span>
          <button type="button" @click="showDeliveryCheckModal = false" style="background: none; border: none; color: #94a3b8; font-weight: 700; cursor: pointer;">
            ✕ {{ currentLang === 'en' ? 'Close' : 'बंद' }}
          </button>
        </div>
      </div>
    </div>

    <!-- ======================================================== -->
    <!-- DESI KIRANA PRINTABLE PARCHA (BILL) MODAL                -->
    <!-- ======================================================== -->
    <div class="modal-overlay" v-if="lastOrderReceipt" @click.self="lastOrderReceipt = null">
      <div class="modal-card printable-area" style="max-width: 480px;">
        <div class="no-print" style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px;">
          <span style="font-size: 0.88rem; font-weight: 800; color: #047857;">✅ {{ t('parcha_generated_title') }}</span>
          <button class="close-btn" @click="lastOrderReceipt = null">✕</button>
        </div>

        <!-- Active Delivery Add-on Banner in Parcha Modal -->
        <div
          class="no-print"
          v-if="canAddToActiveOrder(lastOrderReceipt)"
          style="background: #f0fdf4; border: 1.5px dashed #16a34a; border-radius: 12px; padding: 12px 14px; margin-bottom: 12px; display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 10px;"
        >
          <div style="flex: 1; min-width: 200px;">
            <div style="font-weight: 900; color: #166534; font-size: 0.9rem; display: flex; align-items: center; gap: 6px;">
              ⚡ <span>{{ t('active_addon_title') }}</span>
            </div>
            <div style="font-size: 0.78rem; color: #15803d; margin-top: 3px;">
              {{ t('active_addon_sub') }}
            </div>
          </div>
          <button
            type="button"
            @click="openAddActiveItemModal(lastOrderReceipt)"
            style="background: #16a34a; color: white; border: none; padding: 8px 16px; border-radius: 8px; font-weight: 800; font-size: 0.85rem; cursor: pointer; display: flex; align-items: center; gap: 6px; box-shadow: 0 2px 6px rgba(22, 163, 74, 0.25);"
          >
            <span>➕</span>
            <span>{{ t('active_addon_btn') }}</span>
          </button>
        </div>

        <div class="parcha-receipt" id="printable-parcha-slip">
          <div class="parcha-header">
            <h3 style="margin: 0; font-size: 1.22rem; font-weight: 900; color: #064e3b;">
              🌾 कोमल एंटरप्रायझेस / कोमल मार्ट (Komal Enterprises)
            </h3>
            <p style="font-size: 0.74rem; margin: 3px 0; color: #1e293b; line-height: 1.4;">
              📍 1st Floor, GRD 6, Vitthal Rukhmai CHS, B.B. Khandekar Marg, Nr. Ram Mandir, Wadala (W), Mumbai - 400031
            </p>
            <p style="font-size: 0.72rem; margin: 2px 0; color: #44403c;">
              <strong>GSTIN:</strong> 27ACOPU3896J1ZK • <strong>FSSAI:</strong> 11521003000327
            </p>
            <p style="font-size: 0.72rem; margin: 2px 0; color: #065f46; font-weight: 700;">
              📞 दुकान / शॉप मालक: 9987602693 / 8369795519 • व्यवस्थापक: 7045311406 • WhatsApp: 91420-52967
            </p>
            <p style="font-size: 0.85rem; font-weight: bold; margin-top: 6px; border-top: 1px dashed #cbd5e1; padding-top: 4px;">
              {{ t('parcha_invoice_title') }}
            </p>
            <div style="display: flex; justify-content: space-between; font-size: 0.76rem; margin-top: 6px;">
              <span>पर्चा नं: <strong>{{ lastOrderReceipt.order_number }}</strong></span>
              <span>दिनांक: {{ lastOrderReceipt.created_at }}</span>
            </div>
          </div>

          <div style="font-size: 0.82rem; margin-bottom: 10px; border-bottom: 1.5px dashed #78716c; padding-bottom: 6px;">
            <div><strong>ग्राहक:</strong> {{ lastOrderReceipt.customer_name }}</div>
            <div><strong>फोन:</strong> {{ lastOrderReceipt.customer_phone }}</div>
            <div><strong>पता:</strong> {{ lastOrderReceipt.customer_address }}</div>
            <div>
              <strong>भुगतान:</strong> {{ lastOrderReceipt.payment_method }}
              ({{ lastOrderReceipt.payment_status === 'Paid' ? '🟢 चुकता (Paid)' : (lastOrderReceipt.payment_status === 'Partially Paid' ? '🟡 अर्धवट भरले (Partially Paid)' : (lastOrderReceipt.payment_status === 'Pending Verification' ? '⏳ UPI सत्यापन बाकी (Store Verification Pending)' : '🔴 बाकी उधारी')) }})
            </div>
          </div>

          <table class="parcha-table">
            <thead>
              <tr>
                <th>Item Description</th>
                <th>Qty</th>
                <th>Rate (₹)</th>
                <th style="text-align: right;">Amount (₹)</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="(it, i) in lastOrderReceipt.items" :key="i">
                <td>
                  <strong>{{ it.product_name }}</strong><br />
                  <span style="font-size: 0.72rem; color: #57534e;">{{ it.variant_label }}</span>
                </td>
                <td>{{ it.quantity }}</td>
                <td>{{ it.unit_price }}</td>
                <td style="text-align: right; font-weight: bold;">{{ it.subtotal.toFixed(2) }}</td>
              </tr>
            </tbody>
          </table>

          <div style="border-top: 1.5px dashed #78716c; padding-top: 8px; font-size: 0.88rem;">
            <div style="display: flex; justify-content: space-between;">
              <span>{{ t('mrp_total') }}:</span>
              <span>₹{{ lastOrderReceipt.total_mrp }}</span>
            </div>
            <div style="display: flex; justify-content: space-between; color: #047857; font-weight: bold;">
              <span>{{ t('kirana_savings') }}:</span>
              <span>- ₹{{ lastOrderReceipt.total_savings }}</span>
            </div>
            <div v-if="lastOrderReceipt.credit_used > 0" style="display: flex; justify-content: space-between; color: #047857; font-weight: bold;">
              <span>💳 {{ t('store_credit_applied') }}:</span>
              <span>- ₹{{ lastOrderReceipt.credit_used }}</span>
            </div>
            <div style="display: flex; justify-content: space-between; font-size: 1.2rem; font-weight: 900; margin-top: 6px; border-top: 2px solid #000; padding-top: 4px;">
              <span>{{ t('payable_amount') }}:</span>
              <span>₹{{ lastOrderReceipt.final_amount }}</span>
            </div>
            <!-- Advance Paid & Doorstep Balance Due Breakdown -->
            <div v-if="lastOrderReceipt.amount_paid > 0 && lastOrderReceipt.balance_due > 0" style="margin-top: 8px; background: #fffbeb; border: 1.5px solid #f59e0b; border-radius: 8px; padding: 10px;">
              <div style="display: flex; justify-content: space-between; color: #047857; font-weight: 700; font-size: 0.95rem;">
                <span>आधी जमा (Advance Paid):</span>
                <span>- ₹{{ lastOrderReceipt.amount_paid }}</span>
              </div>
              <div style="display: flex; justify-content: space-between; color: #b91c1c; font-weight: 900; font-size: 1.15rem; margin-top: 4px; border-top: 1px dashed #d97706; padding-top: 4px;">
                <span>बाकी देय (To Collect at Doorstep):</span>
                <span>₹{{ lastOrderReceipt.balance_due }}</span>
              </div>
              <div style="margin-top: 6px; font-size: 0.8rem; color: #92400e; font-weight: 700;">
                ⚠️ डिलिव्हरी पार्टनर सूचना: ग्राहकाकडून ₹{{ lastOrderReceipt.balance_due }} रोख किंवा UPI ने घ्यावे!
              </div>
            </div>
            <div v-if="lastOrderReceipt.credit_earned > 0 && lastOrderReceipt.payment_status === 'Paid'" style="margin-top: 6px; background: #ecfdf5; padding: 6px 10px; border-radius: 6px; font-size: 0.82rem; color: #064e3b; font-weight: bold; text-align: center;">
              🎉 {{ t('store_credit_earned') }}: +₹{{ lastOrderReceipt.credit_earned }}!
            </div>
            <div v-else-if="lastOrderReceipt.credit_earned > 0" style="margin-top: 6px; background: #fffbeb; padding: 6px 10px; border-radius: 6px; font-size: 0.82rem; color: #b45309; font-weight: bold; text-align: center; border: 1px dashed #f59e0b;">
              ⏳ {{ currentLang === 'en' ? `₹${lastOrderReceipt.credit_earned} Store Credit (Will be credited to wallet upon full payment)` : (currentLang === 'mr' ? `₹${lastOrderReceipt.credit_earned} स्टोअर क्रेडिट (पेमेंट चुकता झाल्यावर वॉलेटमध्ये जमा होईल)` : `₹${lastOrderReceipt.credit_earned} स्टोर क्रेडिट (पेमेंट पूरा होने पर वॉलेट में जुड़ेगा)`) }}
            </div>
          </div>

          <div style="text-align: center; font-size: 0.78rem; margin-top: 16px; border-top: 1.5px dashed #78716c; padding-top: 8px;">
            <div style="font-weight: 700;">🙏 {{ t('parcha_visit_again') }} 🙏</div>
            <div style="font-size: 0.7rem; color: #78716c; margin-top: 3px;">
              Komal Mart • Wadala, Mumbai | Helpline: 91420-52967
            </div>
          </div>
        </div>

        <div class="no-print" style="display: flex; gap: 10px; margin-top: 16px; flex-wrap: wrap;">
          <button
            @click="shareOrderOnWhatsApp(lastOrderReceipt)"
            class="whatsapp-share-btn"
          >
            📲 {{ t('parcha_send_whatsapp') }}
          </button>
          <button
            @click="printParcha"
            style="flex: 1; min-width: 130px; padding: 11px; background: #1c1917; color: white; border: none; border-radius: 10px; font-weight: 800; cursor: pointer; display: flex; align-items: center; justify-content: center; gap: 6px;"
          >
            🖨️ {{ t('parcha_print_btn') }}
          </button>
          <button
            type="button"
            @click="downloadOrderPdf(lastOrderReceipt)"
            style="flex: 1; min-width: 130px; padding: 11px; background: #047857; color: white; border: none; border-radius: 10px; font-weight: 800; cursor: pointer; display: flex; align-items: center; justify-content: center; gap: 6px;"
          >
            📥 {{ t('parcha_pdf_btn') || 'PDF बिल' }}
          </button>
          <button
            v-if="canAddToActiveOrder(lastOrderReceipt)"
            @click="openAddActiveItemModal(lastOrderReceipt)"
            style="padding: 11px 16px; background: #ecfdf5; border: 1.5px solid #10b981; color: #047857; border-radius: 10px; font-weight: 800; cursor: pointer; display: flex; align-items: center; justify-content: center; gap: 6px;"
          >
            ⚡ {{ t('active_addon_btn') }}
          </button>
          <button
            @click="lastOrderReceipt = null"
            style="padding: 11px 18px; background: #e7e2d9; color: #1c1917; border: none; border-radius: 10px; font-weight: 800; cursor: pointer;"
          >
            {{ t('parcha_close_btn') }}
          </button>
        </div>
      </div>
    </div>

    <!-- ======================================================== -->
    <!-- ADD ITEM TO ACTIVE DELIVERY MODAL                        -->
    <!-- (Plugs "Bhaiya, ek tel bhejwa dena" Kirana Margin Leak)  -->
    <!-- ======================================================== -->
    <div class="modal-overlay" v-if="showAddActiveItemModal && activeOrderForAddon" @click.self="showAddActiveItemModal = false">
      <div class="modal-card" style="max-width: 520px; width: 95%; max-height: 90vh; display: flex; flex-direction: column; padding: 20px; border-radius: 16px;">
        <!-- Modal Header -->
        <div style="display: flex; justify-content: space-between; align-items: flex-start; border-bottom: 1px solid var(--border); padding-bottom: 12px; margin-bottom: 12px;">
          <div>
            <div style="display: flex; align-items: center; gap: 8px;">
              <span style="font-size: 1.4rem;">⚡</span>
              <h3 style="font-size: 1.15rem; font-weight: 900; color: #064e3b; margin: 0;">
                {{ t('active_addon_title') }}
              </h3>
            </div>
            <p style="font-size: 0.8rem; color: #166534; margin: 4px 0 0; font-weight: 700;">
              📦 {{ currentLang === 'en' ? 'Order' : 'ऑर्डर' }} #{{ activeOrderForAddon.order_number }} • 
              <span style="background: #dcfce7; color: #15803d; padding: 2px 8px; border-radius: 6px; font-weight: 800;">
                {{ t('active_addon_free_badge') }}
              </span>
            </p>
          </div>
          <button
            type="button"
            class="close-btn"
            @click="showAddActiveItemModal = false"
            style="background: #f1f5f9; border: none; width: 32px; height: 32px; border-radius: 50%; font-size: 1rem; cursor: pointer; color: #475569;"
          >
            ✕
          </button>
        </div>

        <!-- Success Toast Alert inside Modal -->
        <div
          v-if="addonSuccessItem"
          style="background: #ecfdf5; border: 1.5px solid #6ee7b7; border-radius: 10px; padding: 10px 14px; margin-bottom: 12px; display: flex; justify-content: space-between; align-items: center; gap: 10px;"
        >
          <div style="font-size: 0.84rem; color: #065f46; font-weight: 700;">
            🎉 <strong>{{ addonSuccessItem.name }} ({{ addonSuccessItem.unit_size }})</strong> 
            {{ currentLang === 'en' ? 'successfully added to active delivery!' : (currentLang === 'mr' ? 'चालू डिलिव्हरीमध्ये जोडले गेले!' : 'चालू डिलीवरी में जुड़ गया!') }}
            <div style="font-size: 0.76rem; color: #047857; margin-top: 2px;">
              {{ currentLang === 'en' ? 'Updated Total Bill:' : (currentLang === 'mr' ? 'नवीन एकूण बिल:' : 'अपडेटेड कुल बिल:') }} <strong>₹{{ activeOrderForAddon.final_amount }}</strong>
            </div>
          </div>
          <button
            type="button"
            @click="addonSuccessItem = null"
            style="background: #10b981; color: white; border: none; padding: 5px 10px; border-radius: 6px; font-size: 0.76rem; font-weight: 800; cursor: pointer;"
          >
            ✓ OK
          </button>
        </div>

        <!-- Search Bar -->
        <div style="position: relative; margin-bottom: 10px;">
          <input
            type="text"
            v-model="addonSearchQuery"
            :placeholder="t('active_addon_search')"
            style="width: 100%; padding: 10px 36px 10px 14px; border: 1.5px solid var(--border); border-radius: 10px; font-size: 0.9rem; outline: none; box-sizing: border-box;"
          />
          <button
            v-if="addonSearchQuery"
            type="button"
            @click="addonSearchQuery = ''"
            style="position: absolute; right: 10px; top: 50%; transform: translateY(-50%); background: none; border: none; color: #94a3b8; font-size: 1rem; cursor: pointer;"
          >
            ✕
          </button>
        </div>

        <!-- Quick Filter Pills for Common Pantry Forgetful Items -->
        <div style="display: flex; gap: 6px; overflow-x: auto; padding-bottom: 8px; margin-bottom: 8px; scrollbar-width: none;">
          <button
            v-for="chip in quickAddonChips"
            :key="chip.tag"
            type="button"
            @click="setAddonQuickChip(chip.tag)"
            :style="{
              background: addonSearchQuery === chip.tag ? '#059669' : '#f8fafc',
              color: addonSearchQuery === chip.tag ? '#ffffff' : '#334155',
              border: addonSearchQuery === chip.tag ? '1px solid #059669' : '1px solid #cbd5e1',
              padding: '4px 10px',
              borderRadius: '20px',
              fontSize: '0.76rem',
              fontWeight: '700',
              cursor: 'pointer',
              whiteSpace: 'nowrap'
            }"
          >
            {{ chip.icon }} {{ chip.label[currentLang] || chip.label.en }}
          </button>
        </div>

        <!-- Scrollable Product List -->
        <div style="flex: 1; overflow-y: auto; display: flex; flex-direction: column; gap: 10px; padding-right: 4px; min-height: 220px; max-height: 48vh;">
          <div v-if="addonFilteredProducts.length === 0" style="text-align: center; padding: 30px 10px; color: var(--text-muted);">
            <div style="font-size: 2rem; margin-bottom: 6px;">🔍</div>
            <p style="font-weight: 700; font-size: 0.9rem; margin: 0;">
              {{ currentLang === 'en' ? 'No matching products found.' : (currentLang === 'mr' ? 'कोणतेही उत्पादन आढळले नाही.' : 'कोई उत्पाद नहीं मिला।') }}
            </p>
          </div>

          <div
            v-for="prod in addonFilteredProducts"
            :key="prod.id"
            style="border: 1px solid var(--border); border-radius: 10px; padding: 10px; display: flex; align-items: center; justify-content: space-between; gap: 10px; background: white;"
          >
            <!-- Product Info & Thumb -->
            <div style="display: flex; align-items: center; gap: 10px; min-width: 0; flex: 1;">
              <img
                :src="prod.image_url || (prod.images && prod.images[0]) || '/products/chakki-atta.jpg'"
                :alt="prod.name"
                style="width: 48px; height: 48px; object-fit: contain; border-radius: 6px; border: 1px solid #f1f5f9; background: #fff; flex-shrink: 0;"
                loading="lazy"
              />
              <div style="min-width: 0;">
                <h4 style="margin: 0; font-size: 0.88rem; font-weight: 800; color: #1c1917; white-space: nowrap; overflow: hidden; text-overflow: ellipsis;">
                  {{ getLocalizedProductName(prod, currentLang) }}
                </h4>

                <!-- Variant Selector -->
                <div v-if="prod.variants && prod.variants.length > 1" style="margin-top: 4px;">
                  <select
                    :value="getAddonSelectedVariant(prod)?.id"
                    @change="onAddonVariantChange(prod, $event.target.value)"
                    style="font-size: 0.74rem; font-weight: 700; padding: 2px 6px; border: 1px solid #cbd5e1; border-radius: 6px; background: #f8fafc; color: #334155; outline: none;"
                  >
                    <option v-for="v in prod.variants" :key="v.id" :value="v.id">
                      {{ v.unit_size }} — ₹{{ v.selling_price }}
                    </option>
                  </select>
                </div>
                <div v-else-if="prod.variants && prod.variants[0]" style="font-size: 0.75rem; color: #64748b; margin-top: 2px;">
                  {{ prod.variants[0].unit_size }} • <strong style="color: #065f46;">₹{{ prod.variants[0].selling_price }}</strong>
                </div>
              </div>
            </div>

            <!-- Price & Add Stepper / Button -->
            <div style="display: flex; align-items: center; gap: 8px; flex-shrink: 0;">
              <!-- Quantity Stepper -->
              <div style="display: inline-flex; align-items: center; border: 1px solid #cbd5e1; border-radius: 6px; overflow: hidden; background: #f8fafc;">
                <button
                  type="button"
                  @click="changeAddonQuantity(prod, -1)"
                  style="border: none; background: transparent; padding: 4px 8px; font-weight: 800; font-size: 0.85rem; cursor: pointer; color: #475569;"
                >
                  −
                </button>
                <span style="font-size: 0.82rem; font-weight: 800; min-width: 20px; text-align: center; color: #1c1917;">
                  {{ getAddonQuantity(prod) }}
                </span>
                <button
                  type="button"
                  @click="changeAddonQuantity(prod, 1)"
                  style="border: none; background: transparent; padding: 4px 8px; font-weight: 800; font-size: 0.85rem; cursor: pointer; color: #475569;"
                >
                  +
                </button>
              </div>

              <!-- Submit Button -->
              <button
                type="button"
                :disabled="addonSubmitting"
                @click="submitAddItemToActiveOrder(prod)"
                style="background: #059669; color: white; border: none; padding: 7px 12px; border-radius: 8px; font-weight: 800; font-size: 0.8rem; cursor: pointer; display: flex; align-items: center; gap: 4px; box-shadow: 0 2px 6px rgba(5, 150, 105, 0.25);"
              >
                <span>{{ addonSubmitting ? '⏳' : '➕' }}</span>
                <span>₹{{ Math.round((getAddonSelectedVariant(prod)?.selling_price || 0) * getAddonQuantity(prod)) }}</span>
              </button>
            </div>
          </div>
        </div>

        <!-- Modal Footer: Order Summary & Done Button -->
        <div style="margin-top: 14px; border-top: 1px solid var(--border); padding-top: 12px; display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 10px;">
          <div>
            <div style="font-size: 0.78rem; color: #64748b;">
              {{ currentLang === 'en' ? 'Current Order Bill:' : (currentLang === 'mr' ? 'सध्याचे एकूण बिल:' : 'वर्तमान कुल बिल:') }}
            </div>
            <div style="font-weight: 900; font-size: 1.15rem; color: #064e3b;">
              ₹{{ activeOrderForAddon.final_amount }}
            </div>
          </div>
          <button
            type="button"
            @click="showAddActiveItemModal = false"
            style="background: #1c1917; color: white; border: none; padding: 9px 18px; border-radius: 10px; font-weight: 800; font-size: 0.86rem; cursor: pointer;"
          >
            ✓ {{ t('active_addon_done') }}
          </button>
        </div>
      </div>
    </div>

    <!-- ======================================================== -->
    <!-- BATCH PRINT SLIPS MODAL (A4 MULTI-SLIP FITTING)          -->
    <!-- ======================================================== -->
    <div class="modal-overlay" v-if="showBatchPrintModal" @click.self="showBatchPrintModal = false">
      <div class="modal-card batch-modal-card">
        <div class="batch-modal-header no-print">
          <div>
            <h3 style="font-size: 1.25rem; font-weight: 900; color: #064e3b; display: flex; align-items: center; gap: 8px;">
              {{ t('batch_print_title') }}
            </h3>
            <p style="font-size: 0.82rem; color: var(--text-muted); margin-top: 2px;">
              {{ selectedBatchOrders.length }} {{ t('selected_orders_count') }} • A4 शीट वर २ किंवा ४ पर्चे कटिंग लाईनसह
            </p>
          </div>

          <div style="display: flex; align-items: center; gap: 10px; flex-wrap: wrap;">
            <!-- Layout Selector -->
            <div class="batch-layout-selector">
              <span style="font-size: 0.82rem; font-weight: 700; color: var(--text-main);">{{ t('slips_per_page') }}</span>
              <select v-model="batchPrintLayout" class="batch-select">
                <option value="auto">{{ t('layout_auto') }}</option>
                <option value="two">{{ t('layout_two') }}</option>
                <option value="four">{{ t('layout_four') }}</option>
              </select>
            </div>

            <button class="batch-trigger-print-btn" @click="triggerBatchPrint">
              {{ t('print_or_pdf_btn') }}
            </button>

            <button class="close-btn" @click="showBatchPrintModal = false">✕</button>
          </div>
        </div>

        <!-- Scrollable Sheet Preview in Modal -->
        <div class="batch-printable-area" :class="resolvedBatchLayoutClass">
          <div
            v-for="(pageOrders, pageIdx) in chunkedBatchOrders"
            :key="pageIdx"
            class="batch-page-container"
          >
            <div class="batch-page-sheet">
              <div
                v-for="slip in pageOrders"
                :key="slip.id"
                class="batch-slip-card"
              >
                <!-- Slip Header -->
                <div class="slip-header">
                  <div class="slip-store-title">{{ t('store_name_full') }}</div>
                  <div class="slip-store-sub">मेन बाजार, स्टेशन रोड • मो. 91420-52967</div>
                  <div class="slip-meta-row">
                    <span>बिल नं: <strong>{{ slip.order_number }}</strong></span>
                    <span>{{ slip.created_at }}</span>
                  </div>
                </div>

                <!-- Customer Details -->
                <div class="slip-cust-box">
                  <div class="slip-cust-line">
                    <strong>ग्राहक:</strong> {{ slip.customer_name }} | 📞 {{ slip.customer_phone }}
                  </div>
                  <div class="slip-cust-line">
                    <strong>पत्ता:</strong> {{ slip.customer_address }}
                  </div>
                  <div class="slip-cust-line">
                    <strong>भुगतान:</strong> {{ slip.payment_method }}
                    <span class="slip-badge" :class="slip.payment_status === 'Paid' ? 'slip-paid' : 'slip-unpaid'">
                      {{ slip.payment_status === 'Paid' ? '🟢 चुकता' : '🔴 बाकी उधारी' }}
                    </span>
                  </div>
                </div>

                <!-- Items Table -->
                <table class="slip-table">
                  <thead>
                    <tr>
                      <th style="text-align: left;">Item Description</th>
                      <th style="text-align: center;">Qty</th>
                      <th style="text-align: right;">Amount (₹)</th>
                    </tr>
                  </thead>
                  <tbody>
                    <tr v-for="(it, i) in slip.items" :key="i">
                      <td>
                        <span class="slip-item-name">{{ it.product_name }}</span>
                        <span v-if="it.variant_label" class="slip-item-variant">{{ it.variant_label }}</span>
                      </td>
                      <td style="text-align: center; font-weight: 700;">{{ it.quantity }}</td>
                      <td style="text-align: right; font-weight: 800;">{{ it.subtotal.toFixed(2) }}</td>
                    </tr>
                  </tbody>
                </table>

                <!-- Slip Calculation Summary -->
                <div class="slip-footer">
                  <div class="slip-calc-row">
                    <span style="color: #047857; font-weight: 700;">बचत: ₹{{ slip.total_savings }}</span>
                    <span class="slip-total-amount">देय: <strong>₹{{ slip.final_amount }}</strong></span>
                  </div>
                </div>

                <!-- Scissor Cut Marker -->
                <div class="slip-cut-divider">
                  <span>{{ t('cut_line_text') }}</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- ======================================================== -->
    <!-- ADD PRODUCT MODAL (ADMIN FEATURE)                        -->
    <!-- ======================================================== -->
    <div class="modal-overlay" v-if="showAddProductModal" @click.self="showAddProductModal = false">
      <div class="modal-card" style="max-width: 620px;">
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 14px;">
          <h3 style="font-size: 1.25rem; font-weight: 900; color: #064e3b; margin: 0; display: flex; align-items: center; gap: 8px;">
            <span>➕</span> {{ currentLang === 'mr' ? 'नवीन सामान जोडा (Add Product)' : (currentLang === 'hi' ? 'नया किराना सामान जोड़ें (Add Product)' : 'Add New Kirana Product') }}
          </h3>
          <button class="close-btn" @click="showAddProductModal = false">✕</button>
        </div>

        <!-- Mode Toggle: In-Shop Quick Add vs Full Detailed Form -->
        <div class="admin-modal-mode-switch">
          <button
            type="button"
            class="mode-switch-btn"
            :class="{ active: addProductMode === 'quick' }"
            @click="addProductMode = 'quick'"
          >
            ⚡ {{ currentLang === 'mr' ? 'झटपट इन-शॉप जोडा (Quick Add)' : (currentLang === 'hi' ? 'झटपट दुकान में जोड़ें (Quick Add)' : '⚡ Quick In-Shop Add') }}
          </button>
          <button
            type="button"
            class="mode-switch-btn"
            :class="{ active: addProductMode === 'full' }"
            @click="addProductMode = 'full'"
          >
            ⚙️ {{ currentLang === 'mr' ? 'सविस्तर फॉर्म (Full Form)' : (currentLang === 'hi' ? 'विस्तृत फॉर्म (Full Form)' : '⚙️ Full Detailed Form') }}
          </button>
        </div>

        <!-- QUICK IN-SHOP ADD VIEW -->
        <div v-if="addProductMode === 'quick'" class="quick-add-container">
          <!-- 1. Big Mandi Loose vs Packaged Tiles -->
          <div class="quick-type-selector">
            <button
              type="button"
              class="quick-type-tile"
              :class="{ selected: newProductForm.is_loose }"
              @click="newProductForm.is_loose = true"
            >
              <span class="quick-tile-icon">🌾</span>
              <div class="quick-tile-text">
                <strong>{{ currentLang === 'mr' ? 'सुट्टे किराणा (Loose Mandi)' : (currentLang === 'hi' ? 'खुला राशन (Loose Mandi)' : 'Loose Mandi') }}</strong>
                <small>{{ currentLang === 'mr' ? 'डाळी, तांदूळ, गहू, साखर' : 'दालें, चावल, आटा, चीनी' }}</small>
              </div>
            </button>
            <button
              type="button"
              class="quick-type-tile"
              :class="{ selected: !newProductForm.is_loose }"
              @click="newProductForm.is_loose = false"
            >
              <span class="quick-tile-icon">📦</span>
              <div class="quick-tile-text">
                <strong>{{ currentLang === 'mr' ? 'पाकीटबंद (Packaged)' : (currentLang === 'hi' ? 'पैकेटबंद (Packaged)' : 'Packaged FMCG') }}</strong>
                <small>{{ currentLang === 'mr' ? 'तेल, साबण, बिस्कीट, मीठ' : 'तेल, साबुन, बिस्किट, नमक' }}</small>
              </div>
            </button>
          </div>

          <!-- 2. Fast Camera Shutter Box + Thumbnail -->
          <div class="quick-camera-strip">
            <div class="quick-camera-box">
              <label class="quick-camera-btn">
                <span style="font-size: 1.4rem;">📷</span>
                <span>{{ currentLang === 'mr' ? 'कॅमेरा फोटो काढा' : (currentLang === 'hi' ? 'कैमरा फोटो खींचें' : 'Take Camera Photo') }}</span>
                <input
                  type="file"
                  accept="image/*"
                  capture="environment"
                  style="display: none;"
                  @change="handleFileUpload($event, 'new', 'front')"
                />
              </label>
              <label class="quick-gallery-btn">
                <span>📁 गॅलरी/फाइल</span>
                <input
                  type="file"
                  accept="image/*"
                  style="display: none;"
                  @change="handleFileUpload($event, 'new', 'front')"
                />
              </label>
            </div>
            <div class="quick-photo-preview" v-if="newProductForm.image_front">
              <img :src="newProductForm.image_front" alt="Preview" @error="handleImageFallback($event)" />
            </div>
          </div>

          <!-- 3. Quick Commodity 1-Tap Autofill Chips -->
          <div class="quick-chips-section">
            <span class="quick-section-sub">⚡ {{ currentLang === 'mr' ? '१-टॅप किराणा निवडा (Quick Autofill):' : (currentLang === 'hi' ? '१-टैप किराना चुनें (Quick Autofill):' : '1-Tap Fast Presets:') }}</span>
            <div class="quick-chips-scroll">
              <button
                v-for="(qc, qcIdx) in quickCommodities"
                :key="'qc-' + qcIdx"
                type="button"
                class="quick-item-chip"
                @click="selectQuickCommodity(qc)"
              >
                {{ qc.name_hi }}
              </button>
            </div>
          </div>

          <!-- 4. Category Selector Chips -->
          <div class="quick-cat-section">
            <label class="quick-field-label">{{ currentLang === 'mr' ? 'सामान श्रेणी (Category):' : 'कैटेगरी:' }}</label>
            <div class="quick-cat-chips">
              <button
                v-for="cat in categories"
                :key="'qcat-' + cat.id"
                type="button"
                class="quick-cat-btn"
                :class="{ active: newProductForm.category_id === cat.id && !newProductForm.is_new_category }"
                @click="newProductForm.category_id = cat.id; newProductForm.is_new_category = false;"
              >
                {{ currentLang === 'mr' ? (cat.name_hi || cat.name) : cat.name }}
              </button>
            </div>
          </div>

          <!-- 5. Name Inputs (Marathi/Hindi + English) -->
          <div class="quick-inputs-grid">
            <div>
              <label class="quick-field-label">{{ currentLang === 'mr' ? 'सामान नाव (मराठी/हिंदी) *' : (currentLang === 'hi' ? 'सामान का नाम (हिंदी) *' : 'Local / Hindi Name *') }}</label>
              <input
                type="text"
                v-model="newProductForm.name_hi"
                required
                class="form-input quick-input-lg"
                :placeholder="currentLang === 'mr' ? 'उदा. तूर डाळ' : 'उदा. तूर दाल'"
                @input="syncQuickName"
              />
            </div>
            <div>
              <label class="quick-field-label">{{ currentLang === 'mr' ? 'इंग्रजी नाव (English) *' : 'अंग्रेजी नाम (English) *' }}</label>
              <input
                type="text"
                v-model="newProductForm.name"
                required
                class="form-input quick-input-lg"
                placeholder="e.g. Toor Dal Gavran"
              />
            </div>
          </div>

          <!-- 6. Unit Size Pills & Rate Input -->
          <div class="quick-pricing-card">
            <div>
              <label class="quick-field-label">{{ currentLang === 'mr' ? 'वजन / पॅक साइज:' : (currentLang === 'hi' ? 'वजन / पैक साइज:' : 'Unit Size:') }}</label>
              <div class="quick-unit-pills">
                <button
                  v-for="u in ['500g', '1kg', '2kg', '5kg', '1L', '500ml', '250g', '100g']"
                  :key="'u-' + u"
                  type="button"
                  class="quick-unit-pill"
                  :class="{ active: newProductForm.unit_size === u }"
                  @click="newProductForm.unit_size = u"
                >
                  {{ u }}
                </button>
              </div>
            </div>

            <div class="quick-rate-row">
              <div style="flex: 1;">
                <label class="quick-field-label" style="color: #047857; font-weight: 900;">
                  💰 {{ currentLang === 'mr' ? 'दुकान विक्री दर (₹):' : (currentLang === 'hi' ? 'दुकान बिक्री दर (₹):' : 'Selling Rate (₹):') }}
                </label>
                <div class="quick-rate-input-wrap">
                  <span class="quick-currency">₹</span>
                  <input
                    type="number"
                    v-model.number="newProductForm.selling_price"
                    class="quick-rate-input"
                    placeholder="190"
                    @input="syncQuickPrice"
                  />
                </div>
              </div>
              <div style="flex: 1;">
                <label class="quick-field-label" style="color: var(--text-muted);">
                  MRP (₹) <small>({{ currentLang === 'mr' ? 'ऑटो-सिंक' : 'ऑटो-सिंक' }})</small>:
                </label>
                <div class="quick-rate-input-wrap mrp-wrap">
                  <span class="quick-currency">₹</span>
                  <input
                    type="number"
                    v-model.number="newProductForm.mrp"
                    class="quick-rate-input"
                    placeholder="190"
                  />
                </div>
              </div>
            </div>
          </div>

          <!-- 7. Big 1-Tap Save Button -->
          <button
            type="button"
            class="quick-submit-btn"
            @click="submitNewProduct"
            :disabled="!newProductForm.name || !newProductForm.selling_price"
          >
            ✅ {{ currentLang === 'mr' ? 'दुकानात सामान जोडा (Save to Store)' : (currentLang === 'hi' ? 'दुकान में सामान जोड़ें (Save to Store)' : 'Save Product to Kirana Store') }}
          </button>
        </div>

        <!-- FULL DETAILED FORM VIEW (PRESERVES ALL ADVANCED OPTIONS) -->
        <form v-else @submit.prevent="submitNewProduct">
          <div class="form-group">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 6px;">
              <label class="form-label" style="margin-bottom: 0;">{{ currentLang === 'en' ? 'Category *' : (currentLang === 'mr' ? 'सामान श्रेणी (Category) *' : 'कैटेगरी (Category) *') }}</label>
              <div style="display: flex; gap: 4px;">
                <button
                  type="button"
                  @click="newProductForm.is_new_category = false"
                  :style="!newProductForm.is_new_category ? 'background: #065f46; color: white;' : 'background: #f1f5f9; color: var(--text-muted);'"
                  style="border: none; padding: 3px 8px; border-radius: 4px; font-size: 0.72rem; font-weight: 700; cursor: pointer;"
                >
                  📁 {{ currentLang === 'en' ? 'Existing' : (currentLang === 'mr' ? 'अस्तित्वात असलेली' : 'मौजूदा') }}
                </button>
                <button
                  type="button"
                  @click="newProductForm.is_new_category = true"
                  :style="newProductForm.is_new_category ? 'background: #d97706; color: white;' : 'background: #f1f5f9; color: var(--text-muted);'"
                  style="border: none; padding: 3px 8px; border-radius: 4px; font-size: 0.72rem; font-weight: 700; cursor: pointer;"
                >
                  ➕ {{ currentLang === 'en' ? 'Create New' : (currentLang === 'mr' ? 'नवीन श्रेणी बनवा' : 'नई कैटेगरी') }}
                </button>
              </div>
            </div>

            <!-- Existing Category Dropdown -->
            <select
              v-if="!newProductForm.is_new_category"
              v-model.number="newProductForm.category_id"
              required
              class="form-input"
            >
              <option v-for="cat in categories" :key="cat.id" :value="cat.id">
                {{ cat.name }} ({{ cat.name_hi }})
              </option>
            </select>

            <!-- New Custom Category Inputs -->
            <div v-else style="background: #fffbeb; border: 1.5px solid #fef3c7; padding: 12px; border-radius: 8px;">
              <div style="font-size: 0.82rem; font-weight: 800; color: #92400e; margin-bottom: 8px;">
                ✨ {{ currentLang === 'en' ? 'Create new category directly (creates a new catalog aisle)' : (currentLang === 'mr' ? 'नवीन श्रेणी थेट तयार करा (कॅटलॉगमध्ये नवीन विभाग बनेल)' : 'नई कैटेगरी बनाएं (स्टोर में अलग सेक्शन बनेगा)') }}
              </div>
              <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 8px;">
                <div>
                  <label style="font-size: 0.74rem; font-weight: 700; color: #78350f;">{{ currentLang === 'en' ? 'English Name *' : (currentLang === 'mr' ? 'इंग्रजी नाव (English) *' : 'अंग्रेजी नाम (English) *') }}</label>
                  <input
                    type="text"
                    v-model="newProductForm.new_category_name"
                    required
                    class="form-input"
                    :placeholder="currentLang === 'en' ? 'e.g. Dry Fruits & Nuts' : 'उदा. Dry Fruits & Nuts'"
                    style="margin-top: 2px;"
                  />
                </div>
                <div>
                  <label style="font-size: 0.74rem; font-weight: 700; color: #78350f;">{{ currentLang === 'en' ? 'Marathi / Hindi Name' : (currentLang === 'mr' ? 'मराठी नाव' : 'हिंदी नाम') }}</label>
                  <input
                    type="text"
                    v-model="newProductForm.new_category_name_hi"
                    class="form-input"
                    placeholder="उदा. सुका मेवा व मेवे"
                    style="margin-top: 2px;"
                  />
                </div>
              </div>
            </div>
          </div>

          <div class="form-group">
            <label class="form-label">{{ currentLang === 'en' ? 'English Name *' : (currentLang === 'mr' ? 'इंग्रजी नाव (English Name) *' : 'अंग्रेजी नाम (English Name) *') }}</label>
            <input type="text" v-model="newProductForm.name" required class="form-input" placeholder="e.g. Masoor Dal Malka" />
          </div>

          <div class="form-group">
            <label class="form-label">{{ currentLang === 'en' ? 'Regional / Local Name *' : (currentLang === 'mr' ? 'मराठी/हिंदी नाव (Local Name) *' : 'हिंदी नाम (Hindi Name) *') }}</label>
            <input type="text" v-model="newProductForm.name_hi" required class="form-input" :placeholder="currentLang === 'en' ? 'e.g. Malaka Masoor Dal' : (currentLang === 'mr' ? 'उदा. मलका मसूर डाळ' : 'जैसे: मलका मसूर दाल')" />
          </div>

          <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 12px;">
            <div class="form-group">
              <label class="form-label">{{ currentLang === 'en' ? 'Brand' : (currentLang === 'mr' ? 'ब्रँड (Brand)' : 'ब्रांड (Brand)') }}</label>
              <input type="text" v-model="newProductForm.brand" class="form-input" placeholder="e.g. Tata, Local, Loose" />
            </div>
            <div class="form-group">
              <label class="form-label">{{ currentLang === 'en' ? 'Type' : (currentLang === 'mr' ? 'प्रकार (Type)' : 'प्रकार (Type)') }}</label>
              <select v-model="newProductForm.is_loose" class="form-input">
                <option :value="true">{{ currentLang === 'en' ? '🌾 Loose / Bulk' : (currentLang === 'mr' ? '🌾 सुट्टे किराणा (Loose)' : '🌾 खुला राशन (Loose)') }}</option>
                <option :value="false">{{ currentLang === 'en' ? '📦 Packaged' : (currentLang === 'mr' ? '📦 पाकीटबंद (Packaged)' : '📦 पैकेट (Packaged)') }}</option>
              </select>
            </div>
          </div>

          <div class="form-group">
            <label class="form-label">{{ currentLang === 'en' ? 'Description' : (currentLang === 'mr' ? 'विवरण (Description)' : 'विवरण (Description)') }}</label>
            <textarea v-model="newProductForm.description" rows="2" class="form-input"></textarea>
          </div>

          <!-- 3-ANGLE PRODUCT PHOTOS SECTION -->
          <div style="background: #f0fdf4; border: 1.5px solid #86efac; padding: 14px; border-radius: 10px; margin-bottom: 16px;">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
              <span style="font-weight: 800; font-size: 0.9rem; color: #065f46;">📸 {{ currentLang === 'en' ? '3-Angle Product Photos' : (currentLang === 'mr' ? '३-अँगल सामान फोटो (Product Photos)' : '३-एंगल प्रोडक्ट फोटो (Product Photos)') }}</span>
              <span style="font-size: 0.72rem; color: #047857;">{{ currentLang === 'en' ? '1-tap preset or enter URL' : (currentLang === 'mr' ? '१-टॅप प्रिसेट किंवा URL टाका' : '१-टैप प्रीसेट या URL डालें') }}</span>
            </div>

            <!-- 1-Tap Presets Bar -->
            <div style="margin-bottom: 10px;">
              <span style="font-size: 0.72rem; font-weight: 700; color: #374151; display: block; margin-bottom: 4px;">⚡ {{ currentLang === 'en' ? 'Quick Presets:' : (currentLang === 'mr' ? 'झटपट किराना प्रिसेट्स:' : 'झटपट किराना प्रीसेट्स:') }}</span>
              <div style="display: flex; gap: 6px; flex-wrap: wrap;">
                <button
                  v-for="(preset, pIdx) in kiranaImagePresets"
                  :key="pIdx"
                  type="button"
                  class="photo-preset-btn"
                  @click="applyImagePresetToNew(preset)"
                >
                  {{ preset.label }}
                </button>
              </div>
            </div>

            <!-- 3 Image Slots with Live Camera, Device Upload & Previews -->
            <div style="display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 10px;">
              <!-- Angle 1: Front -->
              <div class="photo-slot-card">
                <div style="display: flex; justify-content: space-between; align-items: center;">
                  <label class="photo-slot-label">📸 १. Front (मुख्य) *</label>
                  <button
                    v-if="newProductForm.image_front"
                    type="button"
                    class="photo-remove-btn"
                    @click="clearSlot('new', 'front')"
                    title="फोटो काढा"
                  >✕</button>
                </div>
                <div class="photo-slot-preview">
                  <span v-if="uploadingSlot === 'new_front'" style="font-size: 0.72rem; color: #047857; font-weight: 700;">
                    ⏳ अपलोड होत आहे...
                  </span>
                  <img
                    v-else-if="newProductForm.image_front"
                    :src="newProductForm.image_front"
                    @error="handleImageFallback($event)"
                    alt="Front"
                  />
                  <span v-else class="photo-slot-placeholder">फोटो जोडा</span>
                </div>
                <!-- Device / Camera Upload Buttons -->
                <div class="photo-upload-actions">
                  <label class="photo-action-btn camera-btn" title="फोनचा कॅमेरा उघडा">
                    📷 कॅमेरा
                    <input
                      type="file"
                      accept="image/*"
                      capture="environment"
                      style="display: none;"
                      @change="handleFileUpload($event, 'new', 'front')"
                    />
                  </label>
                  <label class="photo-action-btn" title="फोन किंवा लॅपटॉपमधून निवडा">
                    📁 फाइल/गॅलरी
                    <input
                      type="file"
                      accept="image/*"
                      style="display: none;"
                      @change="handleFileUpload($event, 'new', 'front')"
                    />
                  </label>
                </div>
                <input
                  type="text"
                  v-model="newProductForm.image_front"
                  class="form-input photo-slot-input"
                  placeholder="किंवा URL टाका"
                  required
                />
              </div>

              <!-- Angle 2: Back / Ingredients -->
              <div class="photo-slot-card">
                <div style="display: flex; justify-content: space-between; align-items: center;">
                  <label class="photo-slot-label">🏷️ २. Back (घटक/माहिती)</label>
                  <button
                    v-if="newProductForm.image_back"
                    type="button"
                    class="photo-remove-btn"
                    @click="clearSlot('new', 'back')"
                    title="फोटो काढा"
                  >✕</button>
                </div>
                <div class="photo-slot-preview">
                  <span v-if="uploadingSlot === 'new_back'" style="font-size: 0.72rem; color: #047857; font-weight: 700;">
                    ⏳ अपलोड होत आहे...
                  </span>
                  <img
                    v-else-if="newProductForm.image_back"
                    :src="newProductForm.image_back"
                    @error="handleImageFallback($event)"
                    alt="Back"
                  />
                  <span v-else class="photo-slot-placeholder">ऐच्छिक (Optional)</span>
                </div>
                <!-- Device / Camera Upload Buttons -->
                <div class="photo-upload-actions">
                  <label class="photo-action-btn camera-btn" title="मागील बाजूचा फोटो काढा">
                    📷 कॅमेरा
                    <input
                      type="file"
                      accept="image/*"
                      capture="environment"
                      style="display: none;"
                      @change="handleFileUpload($event, 'new', 'back')"
                    />
                  </label>
                  <label class="photo-action-btn" title="फोन किंवा लॅपटॉपमधून निवडा">
                    📁 फाइल/गॅलरी
                    <input
                      type="file"
                      accept="image/*"
                      style="display: none;"
                      @change="handleFileUpload($event, 'new', 'back')"
                    />
                  </label>
                </div>
                <input
                  type="text"
                  v-model="newProductForm.image_back"
                  class="form-input photo-slot-input"
                  placeholder="किंवा URL टाका"
                />
              </div>

              <!-- Angle 3: Pack / Texture -->
              <div class="photo-slot-card">
                <div style="display: flex; justify-content: space-between; align-items: center;">
                  <label class="photo-slot-label">📦 ३. Pack (पोत/पोते)</label>
                  <button
                    v-if="newProductForm.image_pack"
                    type="button"
                    class="photo-remove-btn"
                    @click="clearSlot('new', 'pack')"
                    title="फोटो काढा"
                  >✕</button>
                </div>
                <div class="photo-slot-preview">
                  <span v-if="uploadingSlot === 'new_pack'" style="font-size: 0.72rem; color: #047857; font-weight: 700;">
                    ⏳ अपलोड होत आहे...
                  </span>
                  <img
                    v-else-if="newProductForm.image_pack"
                    :src="newProductForm.image_pack"
                    @error="handleImageFallback($event)"
                    alt="Pack"
                  />
                  <span v-else class="photo-slot-placeholder">ऐच्छिक (Optional)</span>
                </div>
                <!-- Device / Camera Upload Buttons -->
                <div class="photo-upload-actions">
                  <label class="photo-action-btn camera-btn" title="पोत/पोत्याचा फोटो काढा">
                    📷 कॅमेरा
                    <input
                      type="file"
                      accept="image/*"
                      capture="environment"
                      style="display: none;"
                      @change="handleFileUpload($event, 'new', 'pack')"
                    />
                  </label>
                  <label class="photo-action-btn" title="फोन किंवा लॅपटॉपमधून निवडा">
                    📁 फाइल/गॅलरी
                    <input
                      type="file"
                      accept="image/*"
                      style="display: none;"
                      @change="handleFileUpload($event, 'new', 'pack')"
                    />
                  </label>
                </div>
                <input
                  type="text"
                  v-model="newProductForm.image_pack"
                  class="form-input photo-slot-input"
                  placeholder="किंवा URL टाका"
                />
              </div>
            </div>
          </div>

          <div style="background: #fdfbf7; border: 1.5px solid var(--border); padding: 14px; border-radius: 10px; margin-bottom: 16px;">
            <div style="font-weight: 800; font-size: 0.88rem; margin-bottom: 8px;">डिफ़ॉल्ट वजन व दर (First Variant):</div>
            <div style="display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 8px;">
              <div>
                <label style="font-size: 0.72rem; font-weight: 700;">वजन</label>
                <input type="text" v-model="newProductForm.unit_size" class="form-input" placeholder="1kg" />
              </div>
              <div>
                <label style="font-size: 0.72rem; font-weight: 700;">MRP (₹)</label>
                <input type="number" v-model.number="newProductForm.mrp" class="form-input" placeholder="120" />
              </div>
              <div>
                <label style="font-size: 0.72rem; font-weight: 700;">बिक्री दर (₹)</label>
                <input type="number" v-model.number="newProductForm.selling_price" class="form-input" placeholder="105" />
              </div>
            </div>
          </div>

          <button type="submit" class="checkout-btn">
            ✅ स्टोर में नया सामान जोड़ें
          </button>
        </form>
      </div>
    </div>

    <!-- ======================================================== -->
    <!-- BATCH PHOTO INGESTION PIPELINE MODAL                     -->
    <!-- ======================================================== -->
    <div class="modal-overlay" v-if="showBatchIngestModal" @click.self="showBatchIngestModal = false">
      <div class="modal-card" style="max-width: 680px;">
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 14px;">
          <h3 style="font-size: 1.25rem; font-weight: 900; color: #064e3b; margin: 0; display: flex; align-items: center; gap: 8px;">
            <span>⚡</span> {{ currentLang === 'mr' ? 'बॅच फोटो व किंमत आयात (Batch Ingest)' : (currentLang === 'hi' ? 'बैच फोटो और दाम आयात (Batch Ingest)' : 'Batch Photo & Price Ingestion') }}
          </h3>
          <button class="close-btn" @click="showBatchIngestModal = false">✕</button>
        </div>

        <div class="batch-ingest-guide">
          <div class="batch-guide-icon">📸</div>
          <div class="batch-guide-content">
            <strong>{{ currentLang === 'mr' ? 'झिरो-टोकन ऑफलाइन फोटो आयात:' : 'जीरो-टोकन ऑफलाइन फोटो आयात:' }}</strong>
            <p style="margin: 4px 0 0; font-size: 0.82rem; color: #4b5563;">
              {{ currentLang === 'mr' ? 'मोबाईलने काढलेले फोटो backend/batch_photos मध्ये टाका. फोटोच्या नावात दर आणि वजन लिहा (उदा. toor-daal-190-per-kg.jpg).' : 'मोबाइल से खींचे फोटो backend/batch_photos में रखें। नाम में दाम और वजन लिखें (जैसे toor-daal-190-per-kg.jpg)।' }}
            </p>
          </div>
        </div>

        <!-- Action Controls -->
        <div style="display: flex; gap: 10px; margin: 16px 0; flex-wrap: wrap;">
          <button
            type="button"
            class="admin-action-chip admin-chip-blue"
            @click="runBatchPhotoIngest(true)"
            :disabled="batchIngestStatus === 'loading'"
          >
            🔍 {{ currentLang === 'mr' ? '१. आधी तपासा (Dry Run Preview)' : '१. पहले जांचें (Dry Run Preview)' }}
          </button>
          <button
            type="button"
            class="admin-action-chip admin-chip-primary"
            @click="runBatchPhotoIngest(false)"
            :disabled="batchIngestStatus === 'loading'"
          >
            ⚡ {{ currentLang === 'mr' ? '२. थेट दुकानात आयात करा (Start Import)' : '२. दुकान में सीधे आयात करें (Start Import)' }}
          </button>
        </div>

        <!-- Status & Results -->
        <div v-if="batchIngestStatus === 'loading'" style="text-align: center; padding: 24px; color: #059669; font-weight: 800;">
          ⏳ {{ currentLang === 'mr' ? 'फोटो स्कॅन व डेटाबेस अपडेट होत आहे...' : 'फोटो स्कैन और डेटाबेस अपडेट हो रहा है...' }}
        </div>

        <div v-else-if="batchIngestStatus === 'error'" style="background: #fef2f2; border: 1.5px solid #fecaca; color: #b91c1c; padding: 12px; border-radius: 8px; font-weight: 700;">
          ❌ {{ batchIngestError }}
        </div>

        <div v-else-if="batchIngestStatus === 'complete' || batchIngestStatus === 'preview'">
          <div class="batch-stats-summary">
            <span class="badge-blue">📋 {{ currentLang === 'mr' ? 'स्कॅन फोटो' : 'स्कैन फोटो' }}: {{ batchIngestStats.processed }}</span>
            <span class="badge-green">✨ {{ currentLang === 'mr' ? 'नवीन जोडले' : 'नए जोड़े' }}: {{ batchIngestStats.created }}</span>
            <span class="badge-amber">🔄 {{ currentLang === 'mr' ? 'अपडेट झाले' : 'अपडेट हुए' }}: {{ batchIngestStats.updated }}</span>
          </div>

          <div class="batch-items-preview-table-wrap" v-if="batchIngestItems.length > 0">
            <table class="batch-preview-table">
              <thead>
                <tr>
                  <th>{{ currentLang === 'mr' ? 'फाइल नाव' : 'फ़ाइल नाम' }}</th>
                  <th>{{ currentLang === 'mr' ? 'सामान' : 'सामान' }}</th>
                  <th>{{ currentLang === 'mr' ? 'श्रेणी' : 'कैटेगरी' }}</th>
                  <th>{{ currentLang === 'mr' ? 'वजन' : 'वजन' }}</th>
                  <th>{{ currentLang === 'mr' ? 'दर (₹)' : 'दर (₹)' }}</th>
                  <th>Status</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="(it, itIdx) in batchIngestItems" :key="'batch-it-' + itIdx">
                  <td style="font-family: monospace; font-size: 0.78rem;">{{ it.file }}</td>
                  <td><strong>{{ it.name }}</strong></td>
                  <td><span class="batch-cat-tag">{{ it.category }}</span></td>
                  <td>{{ it.unit_size }}</td>
                  <td style="color: #059669; font-weight: 800;">₹{{ it.price }}</td>
                  <td>
                    <span :class="it.status === 'Created' ? 'status-pill-green' : (it.status === 'Updated' ? 'status-pill-amber' : 'status-pill-blue')">
                      {{ it.status }}
                    </span>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
          <div v-else style="text-align: center; padding: 20px; color: var(--text-muted); font-size: 0.88rem;">
            ℹ️ {{ currentLang === 'mr' ? 'कोणतेही फोटो सापडले नाहीत. backend/batch_photos फोल्डरमध्ये फोटो टाका.' : 'कोई फोटो नहीं मिले। backend/batch_photos में फोटो रखें।' }}
          </div>
        </div>
      </div>
    </div>

    <!-- ======================================================== -->
    <!-- EDIT PRODUCT PHOTOS MODAL (ADMIN)                        -->
    <!-- ======================================================== -->
    <div class="modal-overlay" v-if="showEditPhotosModal" @click.self="showEditPhotosModal = false">
      <div class="modal-card" style="max-width: 580px;">
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 14px;">
          <h3 style="font-size: 1.2rem; font-weight: 900; color: #064e3b;">
            📸 सामान के फोटो बदलें: {{ editPhotosForm.product_name }}
          </h3>
          <button class="close-btn" @click="showEditPhotosModal = false">✕</button>
        </div>

        <form @submit.prevent="saveProductPhotos">
          <!-- 1-Tap Presets Bar -->
          <div style="margin-bottom: 14px; background: #fdfbf7; border: 1.5px solid var(--border); padding: 10px; border-radius: 8px;">
            <span style="font-size: 0.76rem; font-weight: 700; color: #374151; display: block; margin-bottom: 6px;">⚡ झटपट किराना प्रिसेट निवडा (Quick Presets):</span>
            <div style="display: flex; gap: 6px; flex-wrap: wrap;">
              <button
                v-for="(preset, pIdx) in kiranaImagePresets"
                :key="pIdx"
                type="button"
                class="photo-preset-btn"
                @click="applyImagePresetToEdit(preset)"
              >
                {{ preset.label }}
              </button>
            </div>
          </div>

          <!-- 3 Image Slots with Live Camera, Device Upload & Previews -->
          <div style="display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 10px; margin-bottom: 16px;">
            <!-- Angle 1: Front -->
            <div class="photo-slot-card">
              <div style="display: flex; justify-content: space-between; align-items: center;">
                <label class="photo-slot-label">📸 १. Front (समोरासमोर) *</label>
                <button
                  v-if="editPhotosForm.image_front"
                  type="button"
                  class="photo-remove-btn"
                  @click="clearSlot('edit', 'front')"
                  title="फोटो काढा"
                >✕</button>
              </div>
              <div class="photo-slot-preview">
                <span v-if="uploadingSlot === 'edit_front'" style="font-size: 0.72rem; color: #047857; font-weight: 700;">
                  ⏳ अपलोड होत आहे...
                </span>
                <img
                  v-else-if="editPhotosForm.image_front"
                  :src="editPhotosForm.image_front"
                  @error="handleImageFallback($event)"
                  alt="Front"
                />
                <span v-else class="photo-slot-placeholder">फोटो जोडा</span>
              </div>
              <!-- Device / Camera Upload Buttons -->
              <div class="photo-upload-actions">
                <label class="photo-action-btn camera-btn" title="फोनचा कॅमेरा उघडा">
                  📷 कॅमेरा
                  <input
                    type="file"
                    accept="image/*"
                    capture="environment"
                    style="display: none;"
                    @change="handleFileUpload($event, 'edit', 'front')"
                  />
                </label>
                <label class="photo-action-btn" title="फोन किंवा लॅपटॉपमधून निवडा">
                  📁 फाइल/गॅलरी
                  <input
                    type="file"
                    accept="image/*"
                    style="display: none;"
                    @change="handleFileUpload($event, 'edit', 'front')"
                  />
                </label>
              </div>
              <input
                type="text"
                v-model="editPhotosForm.image_front"
                class="form-input photo-slot-input"
                placeholder="किंवा URL टाका"
                required
              />
            </div>

            <!-- Angle 2: Back / Ingredients -->
            <div class="photo-slot-card">
              <div style="display: flex; justify-content: space-between; align-items: center;">
                <label class="photo-slot-label">🏷️ २. Back (घटक व पोषण)</label>
                <button
                  v-if="editPhotosForm.image_back"
                  type="button"
                  class="photo-remove-btn"
                  @click="clearSlot('edit', 'back')"
                  title="फोटो काढा"
                >✕</button>
              </div>
              <div class="photo-slot-preview">
                <span v-if="uploadingSlot === 'edit_back'" style="font-size: 0.72rem; color: #047857; font-weight: 700;">
                  ⏳ अपलोड होत आहे...
                </span>
                <img
                  v-else-if="editPhotosForm.image_back"
                  :src="editPhotosForm.image_back"
                  @error="handleImageFallback($event)"
                  alt="Back"
                />
                <span v-else class="photo-slot-placeholder">ऐच्छिक (Optional)</span>
              </div>
              <!-- Device / Camera Upload Buttons -->
              <div class="photo-upload-actions">
                <label class="photo-action-btn camera-btn" title="मागील बाजूचा फोटो काढा">
                  📷 कॅमेरा
                  <input
                    type="file"
                    accept="image/*"
                    capture="environment"
                    style="display: none;"
                    @change="handleFileUpload($event, 'edit', 'back')"
                  />
                </label>
                <label class="photo-action-btn" title="फोन किंवा लॅपटॉपमधून निवडा">
                  📁 फाइल/गॅलरी
                  <input
                    type="file"
                    accept="image/*"
                    style="display: none;"
                    @change="handleFileUpload($event, 'edit', 'back')"
                  />
                </label>
              </div>
              <input
                type="text"
                v-model="editPhotosForm.image_back"
                class="form-input photo-slot-input"
                placeholder="किंवा URL टाका"
              />
            </div>

            <!-- Angle 3: Pack / Texture -->
            <div class="photo-slot-card">
              <div style="display: flex; justify-content: space-between; align-items: center;">
                <label class="photo-slot-label">📦 ३. Pack (पोत व पोते)</label>
                <button
                  v-if="editPhotosForm.image_pack"
                  type="button"
                  class="photo-remove-btn"
                  @click="clearSlot('edit', 'pack')"
                  title="फोटो काढा"
                >✕</button>
              </div>
              <div class="photo-slot-preview">
                <span v-if="uploadingSlot === 'edit_pack'" style="font-size: 0.72rem; color: #047857; font-weight: 700;">
                  ⏳ अपलोड होत आहे...
                </span>
                <img
                  v-else-if="editPhotosForm.image_pack"
                  :src="editPhotosForm.image_pack"
                  @error="handleImageFallback($event)"
                  alt="Pack"
                />
                <span v-else class="photo-slot-placeholder">ऐच्छिक (Optional)</span>
              </div>
              <!-- Device / Camera Upload Buttons -->
              <div class="photo-upload-actions">
                <label class="photo-action-btn camera-btn" title="पोत/पोत्याचा फोटो काढा">
                  📷 कॅमेरा
                  <input
                    type="file"
                    accept="image/*"
                    capture="environment"
                    style="display: none;"
                    @change="handleFileUpload($event, 'edit', 'pack')"
                  />
                </label>
                <label class="photo-action-btn" title="फोन किंवा लॅपटॉपमधून निवडा">
                  📁 फाइल/गॅलरी
                  <input
                    type="file"
                    accept="image/*"
                    style="display: none;"
                    @change="handleFileUpload($event, 'edit', 'pack')"
                  />
                </label>
              </div>
              <input
                type="text"
                v-model="editPhotosForm.image_pack"
                class="form-input photo-slot-input"
                placeholder="किंवा URL टाका"
              />
            </div>
          </div>

          <div style="display: flex; gap: 10px; justify-content: flex-end;">
            <button type="button" class="btn-cancel" @click="showEditPhotosModal = false">रद्द करा</button>
            <button type="submit" class="save-chip-btn" style="padding: 10px 20px; font-size: 0.9rem;">
              💾 फोटो सेव्ह करा (Save Photos)
            </button>
          </div>
        </form>
      </div>
    </div>
    <!-- ======================================================== -->
    <!-- CUSTOMER ONLINE UPI SETTLEMENT MODAL                     -->
    <!-- ======================================================== -->
    <div class="modal-overlay" v-if="showUpiPayModal" @click.self="showUpiPayModal = false">
      <div class="modal-card" style="max-width: 440px;">
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 14px;">
          <h3 style="font-size: 1.2rem; font-weight: 900; color: #064e3b;">
            📱 ऑनलाइन UPI द्वारा उधारी चुकता करें
          </h3>
          <button class="close-btn" @click="showUpiPayModal = false">✕</button>
        </div>

        <div v-if="pendingUpiOrder" class="upi-qr-card" style="margin-bottom: 0;">
          <div class="upi-header">
            <span class="upi-badge">ऑर्डर पर्चा नं: {{ pendingUpiOrder.order_number }}</span>
            <h4>दुकान का ऑफिशियल UPI QR कोड</h4>
          </div>

          <!-- Mobile 1-Tap Pay Direct App Link -->
          <a
            :href="`upi://pay?pa=thisisroushan01@okaxis&pn=Raushan%20Raj&am=${(pendingUpiOrder.payment_status === 'Partially Paid' && pendingUpiOrder.balance_due > 0) ? pendingUpiOrder.balance_due : pendingUpiOrder.final_amount}&cu=INR&tn=KomalMart_${pendingUpiOrder.order_number}`"
            class="upi-intent-app-btn"
          >
            {{ t('upi_app_pay_btn') }}
          </a>

          <div class="upi-qr-frame" style="display: flex; flex-direction: column; align-items: center; background: white; padding: 14px; border-radius: 12px; border: 1.5px solid #e2e8f0; margin: 10px 0;">
            <div class="qr-code-img-wrap" style="text-align: center;">
              <img src="/komal-mart-upi-qr.jpeg" alt="Komal Mart UPI QR Code" style="width: 200px; max-width: 100%; height: auto; border-radius: 12px; box-shadow: 0 4px 12px rgba(0,0,0,0.1);" />
            </div>
            <div class="upi-details" style="margin-top: 10px; text-align: center; width: 100%;">
              <div class="upi-shop-name" style="font-weight: 800; color: #0f172a; font-size: 1rem;">Komal Mart (Raushan Raj)</div>
              <div class="upi-id-row" style="margin: 4px 0; font-size: 0.9rem;">
                <span>UPI ID:</span> <code style="font-weight: 800; color: #047857; background: #ecfdf5; padding: 3px 8px; border-radius: 6px;">thisisroushan01@okaxis</code>
              </div>

              <div v-if="pendingUpiOrder.payment_status === 'Partially Paid' && pendingUpiOrder.amount_paid > 0" style="background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 8px; padding: 8px 12px; margin: 8px 0; font-size: 0.85rem; text-align: left;">
                <div style="display: flex; justify-content: space-between; color: #64748b;">
                  <span>एकूण बिल (Total):</span>
                  <span>₹{{ pendingUpiOrder.final_amount }}</span>
                </div>
                <div style="display: flex; justify-content: space-between; color: #047857; font-weight: 700; margin-top: 2px;">
                  <span>आधी जमा (Advance Paid):</span>
                  <span>- ₹{{ pendingUpiOrder.amount_paid }}</span>
                </div>
                <div style="display: flex; justify-content: space-between; color: #b91c1c; font-weight: 900; font-size: 1.1rem; border-top: 1px dashed #cbd5e1; margin-top: 4px; padding-top: 4px;">
                  <span>बाकी देय (To Pay Now):</span>
                  <span>₹{{ pendingUpiOrder.balance_due }}</span>
                </div>
              </div>
              <div v-else class="upi-amount-row" style="margin-top: 4px;">
                <span style="font-size: 0.9rem; color: #475569;">बकाया राशि:</span>
                <strong style="color: #b91c1c; font-size: 1.35rem; margin-left: 6px;">₹{{ pendingUpiOrder.final_amount }}</strong>
              </div>

              <!-- Soundbox micro-paise matching instruction -->
              <div style="background: #fefce8; border: 1px solid #fde047; border-radius: 8px; padding: 8px 10px; margin-top: 10px; font-size: 0.8rem; color: #854d0e; text-align: left; line-height: 1.4;">
                🔊 <strong>{{ currentLang === 'en' ? 'Pay EXACT amount (do not round off):' : (currentLang === 'mr' ? 'अचूक पैशांसहित रक्कम भरा (राऊंड ऑफ करू नका):' : 'सटीक पैसे सहित भुगतान करें (राउंड ऑफ न करें):') }}</strong>
                <span style="display: block; margin-top: 3px; font-size: 0.78rem;">
                  {{ currentLang === 'en' ? `Pay precisely ₹${(pendingUpiOrder.payment_status === 'Partially Paid' && pendingUpiOrder.balance_due > 0) ? pendingUpiOrder.balance_due : pendingUpiOrder.final_amount}. Shop Soundbox announces paise (.${getSoundboxPaise((pendingUpiOrder.payment_status === 'Partially Paid' && pendingUpiOrder.balance_due > 0) ? pendingUpiOrder.balance_due : pendingUpiOrder.final_amount)}) to verify your order instantly!` : (currentLang === 'mr' ? `कृपया अचूक ₹${(pendingUpiOrder.payment_status === 'Partially Paid' && pendingUpiOrder.balance_due > 0) ? pendingUpiOrder.balance_due : pendingUpiOrder.final_amount} भरा. दुकानातील साऊंडबॉक्स .${getSoundboxPaise((pendingUpiOrder.payment_status === 'Partially Paid' && pendingUpiOrder.balance_due > 0) ? pendingUpiOrder.balance_due : pendingUpiOrder.final_amount)} पैसे घोषित करतो, ज्यामुळे तुमचे बिल त्वरित कन्फर्म होते!` : `कृपया सटीक ₹${(pendingUpiOrder.payment_status === 'Partially Paid' && pendingUpiOrder.balance_due > 0) ? pendingUpiOrder.balance_due : pendingUpiOrder.final_amount} भरें। दुकान का साउंडबॉक्स .${getSoundboxPaise((pendingUpiOrder.payment_status === 'Partially Paid' && pendingUpiOrder.balance_due > 0) ? pendingUpiOrder.balance_due : pendingUpiOrder.final_amount)} पैसे बोलकर आपका ऑर्डर तुरंत कन्फर्म करता है!`) }}
                </span>
              </div>
              <div class="upi-apps-icons" style="font-size: 0.78rem; color: #64748b; margin-top: 6px;">Google Pay • PhonePe • Paytm • BHIM UPI</div>
            </div>
          </div>

          <!-- UTR / Reference No. Input -->
          <div class="upi-utr-wrap">
            <label style="font-size: 0.82rem; font-weight: 700; color: #334155; display: block; margin-bottom: 4px;">
              {{ t('upi_utr_label') }}
            </label>
            <input
              type="text"
              v-model="pendingUpiUtr"
              maxlength="16"
              placeholder="उदा. 426812345678"
              class="upi-utr-input"
            />
          </div>

          <p style="font-size: 0.8rem; color: var(--text-muted); margin: 6px 0 14px; text-align: center;">
            {{ currentLang === 'en' ? 'After sending payment via UPI, enter your 12-digit UTR above and submit. Store owner will verify against bank receipt and mark your bill as Paid.' : (currentLang === 'mr' ? 'UPI ने पैसे पाठवल्यावर 12-अंकी UTR टाकून सबमिट करा. दुकानदार बँक मेसेज तपासून बिल चुकता करतील.' : 'UPI द्वारा भुगतान करने के बाद 12 अंकों का UTR डालकर सबमिट करें। दुकानदार बैंक SMS देखकर बिल चुकता करेंगे।') }}
          </p>

          <button
            class="checkout-btn"
            @click="confirmUpiPayForCustomerOrder"
          >
            ✅ {{ currentLang === 'en' ? 'Submit for Verification' : (currentLang === 'mr' ? 'पडताळणीसाठी सबमिट करा' : 'सत्यापन के लिए सबमिट करें') }}
          </button>

          <button
            type="button"
            class="checkout-btn"
            style="background: #25d366; margin-top: 10px; display: flex; align-items: center; justify-content: center; gap: 8px;"
            @click="sendCustomerUpiProofWhatsApp(pendingUpiOrder)"
          >
            📲 {{ currentLang === 'en' ? 'Send Payment Confirmation on WhatsApp (1-Tap)' : (currentLang === 'mr' ? 'WhatsApp वर पेमेंट पावती पाठवा (१-टॅप)' : 'WhatsApp पर पेमेंट पर्ची भेजें (१-टैप)') }}
          </button>
        </div>
      </div>
    </div>

    <!-- ================================================================= -->
    <!-- RESTOCK NOTIFICATION MODAL (NOTIFY ME)                            -->
    <!-- ================================================================= -->
    <div class="modal-overlay" v-if="showNotifyModal" @click.self="showNotifyModal = false">
      <div class="modal-card" style="max-width: 440px; border-radius: 16px;">
        <div class="modal-header">
          <div class="modal-title" style="display: flex; align-items: center; gap: 8px; font-size: 1.15rem; font-weight: 900; color: #064e3b;">
            🔔 {{ t('notify_me_title') }}
          </div>
          <button class="close-btn" @click="showNotifyModal = false">✕</button>
        </div>

        <div style="padding: 20px;">
          <!-- Product Preview Card -->
          <div v-if="notifyProduct" style="display: flex; gap: 14px; background: #f8fafc; border: 1.5px solid #e2e8f0; border-radius: 12px; padding: 12px; margin-bottom: 16px; align-items: center;">
            <img :src="notifyProduct.image_url" style="width: 58px; height: 58px; object-fit: cover; border-radius: 8px;" />
            <div>
              <div style="font-weight: 800; font-size: 0.95rem; color: #1e293b;">
                {{ getLocalizedProductName(notifyProduct, currentLang) }}
              </div>
              <div style="font-size: 0.82rem; color: #64748b; margin-top: 3px;">
                <span v-if="notifyVariant" style="background: #e2e8f0; padding: 2px 8px; border-radius: 6px; font-weight: 700; color: #334155;">
                  {{ notifyVariant.unit_size }}
                </span>
                <span v-else style="color: #ef4444; font-weight: 700;">
                  🚫 {{ t('out_of_stock') }}
                </span>
              </div>
            </div>
          </div>

          <p style="font-size: 0.88rem; color: #475569; line-height: 1.45; margin-bottom: 16px;">
            {{ t('notify_me_desc') }}
          </p>

          <div v-if="notifyMessage" :class="notifySuccess ? 'auth-success-banner' : 'auth-error-banner'" style="margin-bottom: 14px; font-size: 0.88rem; padding: 10px 14px; border-radius: 8px;">
            {{ notifyMessage }}
          </div>

          <form v-if="!notifySuccess" @submit.prevent="submitNotifyMe">
            <div class="form-group" style="margin-bottom: 12px;">
              <label class="form-label" style="text-align: left; font-size: 0.85rem; font-weight: 700; color: #334155; margin-bottom: 4px; display: block;">
                {{ currentLang === 'en' ? 'Customer Name' : (currentLang === 'mr' ? 'ग्राहकाचे नाव' : 'ग्राहक का नाम') }}
              </label>
              <input
                type="text"
                class="form-input"
                v-model="notifyForm.customer_name"
                :placeholder="t('notify_me_name_placeholder')"
                style="width: 100%; box-sizing: border-box;"
              />
            </div>

            <div class="form-group" style="margin-bottom: 18px;">
              <label class="form-label" style="text-align: left; font-size: 0.85rem; font-weight: 700; color: #334155; margin-bottom: 4px; display: block;">
                {{ currentLang === 'en' ? 'Mobile Number (10 digits)' : (currentLang === 'mr' ? 'मोबाईल नंबर (१० अंक)' : 'मोबाइल नंबर (१० अंक)') }} <span style="color: #ef4444;">*</span>
              </label>
              <input
                type="tel"
                class="form-input"
                v-model="notifyForm.customer_phone"
                maxlength="10"
                required
                :placeholder="t('notify_me_phone_placeholder')"
                style="width: 100%; box-sizing: border-box; font-weight: 700; letter-spacing: 1px;"
              />
            </div>

            <button
              type="submit"
              class="checkout-btn"
              :disabled="notifySubmitting"
              style="width: 100%; padding: 12px; font-size: 0.95rem; font-weight: 800; border-radius: 8px; background: #059669; color: white; border: none; cursor: pointer; display: flex; align-items: center; justify-content: center; gap: 8px;"
            >
              <span v-if="notifySubmitting">⏳...</span>
              <span v-else>{{ t('notify_me_submit') }}</span>
            </button>
          </form>

          <div v-else style="text-align: center; margin-top: 10px;">
            <button
              class="btn-secondary"
              @click="showNotifyModal = false"
              style="width: 100%; padding: 10px; border-radius: 8px; font-weight: 700; cursor: pointer;"
            >
              OK 👍
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- ======================================================== -->
    <!-- MONTHLY RATION CHECKLIST MODAL (एकमुश्त राशन पर्चा)      -->
    <!-- ======================================================== -->
    <div class="modal-overlay" v-if="showMonthlyParchaModal" @click.self="showMonthlyParchaModal = false">
      <div class="modal-card" style="max-width: 520px; width: 95%; max-height: 88vh; display: flex; flex-direction: column; overflow: hidden; padding: 18px;">
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px;">
          <div>
            <h3 style="font-size: 1.25rem; font-weight: 900; color: #064e3b; display: flex; align-items: center; gap: 8px;">
              📝 एकमुश्त मासिक राशन पर्चा (Monthly Ration)
            </h3>
            <p style="font-size: 0.8rem; color: var(--text-muted); margin-top: 2px;">
              पूरे महीने का ज़रूरी राशन एक क्लिक में चुनें और थैले में जोड़ें।
            </p>
          </div>
          <button class="close-btn" @click="showMonthlyParchaModal = false">✕</button>
        </div>

        <!-- Custom Search to add ANY grocery from catalog -->
        <div class="parcha-search-box">
          <input
            type="text"
            v-model="parchaSearchQuery"
            :placeholder="currentLang === 'en' ? '🔍 Search & add other grocery (oil, spices, soap)...' : (currentLang === 'mr' ? '🔍 पर्चा मध्ये इतर सामान जोडा (उदा. तेल, मसाले, साबण)...' : '🔍 पर्चा में और सामान जोड़ें (उदा. तेल, मसाले, साबुन)...')"
            class="form-input"
            style="padding: 9px 12px; font-size: 0.85rem; border-radius: 10px; border: 1.5px solid #a7f3d0;"
          />
          <div v-if="parchaSearchQuery.trim() && parchaSearchResults.length > 0" class="parcha-search-dropdown">
            <div
              v-for="p in parchaSearchResults"
              :key="p.id"
              class="parcha-search-item"
              @click="addProductToParcha(p)"
            >
              <img :src="p.image_url ? p.image_url.split('||')[0] : '/placeholder.png'" class="parcha-search-thumb" @error="handleImageFallback($event)" />
              <div style="flex: 1; min-width: 0;">
                <div style="font-weight: 700; font-size: 0.86rem; color: #1e293b; white-space: nowrap; overflow: hidden; text-overflow: ellipsis;">
                  {{ getLocalizedProductName(p, currentLang) }}
                </div>
                <div style="font-size: 0.74rem; color: #64748b;">
                  {{ p.variants && p.variants[0] ? p.variants[0].unit_size + ' • ₹' + p.variants[0].selling_price : '' }}
                </div>
              </div>
              <button type="button" class="btn-add-parcha">
                + {{ currentLang === 'en' ? 'Add' : (currentLang === 'mr' ? 'जोडा' : 'जोड़ें') }}
              </button>
            </div>
          </div>
        </div>

        <!-- Checklist of monthly staples & custom items -->
        <div class="parcha-items-grid">
          <div
            v-for="(item, idx) in monthlyParchaItems"
            :key="item.id"
            class="parcha-item-card"
            :class="{ selected: item.selected }"
            @click="item.selected = !item.selected"
          >
            <img :src="item.image" :alt="item.name" class="parcha-item-thumb" @error="handleImageFallback($event)" />
            <div class="parcha-item-info">
              <div class="parcha-item-title">{{ item.name }}</div>
              <div class="parcha-item-sub">{{ item.variantUnit }} • {{ item.isLoose ? 'खुला मंडी तोल' : 'ब्रांडेड पैक' }}</div>
              <div class="parcha-item-prices">
                <span class="parcha-item-selling">₹{{ (item.fallbackPrice * (item.quantity || 1)) }}</span>
              </div>
            </div>

            <!-- Quantity Stepper -->
            <div class="parcha-stepper" @click.stop v-if="item.selected">
              <button type="button" @click.stop="updateParchaQty(item, -1)">-</button>
              <span>{{ item.quantity || 1 }}</span>
              <button type="button" @click.stop="updateParchaQty(item, 1)">+</button>
            </div>

            <div class="parcha-checkbox-wrap">
              <div class="parcha-custom-check">
                <span v-if="item.selected">✓</span>
              </div>
            </div>

            <!-- Remove Button -->
            <button
              type="button"
              class="parcha-remove-btn"
              title="Remove item"
              @click.stop="removeParchaItem(idx)"
            >
              ✕
            </button>
          </div>
        </div>

        <!-- Modal Footer Actions -->
        <div style="background: #ecfdf5; border: 1.5px solid #a7f3d0; border-radius: 12px; padding: 14px; margin-bottom: 6px; display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 10px;">
          <div>
            <div style="font-size: 0.82rem; color: #047857; font-weight: 700;">
              चुने हुए सामान: <strong>{{ monthlyParchaSelectedCount }} आइटम</strong>
            </div>
            <div style="font-size: 1.15rem; font-weight: 900; color: #064e3b;">
              कुल राशि: ₹{{ monthlyParchaTotal }}
            </div>
          </div>
          <button
            class="checkout-btn"
            style="width: auto; padding: 10px 20px;"
            :disabled="monthlyParchaSelectedCount === 0"
            @click="addMonthlyParchaToCart"
          >
            🛒 सब थैले में जोड़ें (Add to Cart)
          </button>
        </div>
      </div>
    </div>

    <!-- ======================================================== -->
    <!-- QUICK VIEW / PRODUCT DETAIL MODAL                        -->
    <!-- ======================================================== -->
    <div class="modal-overlay" v-if="selectedProductQuickView" @click.self="closeQuickView">
      <div class="modal-card quick-view-card">
        <div class="quick-view-header">
          <div class="quick-view-badge-title">
            <span>🌾 {{ t('quick_view_title') }}</span>
          </div>
          <button class="close-btn" @click="closeQuickView">✕</button>
        </div>

        <div class="quick-view-grid">
          <!-- Left: Flipkart-Style Multi-Angle Image Slider & Mandi Badges -->
          <div class="quick-view-image-pane">
            <div
              class="quick-view-main-image-wrap"
              @touchstart="handleTouchStart"
              @touchend="handleTouchEnd"
            >
              <!-- Counter badge (e.g. 📸 1 / 3) -->
              <span class="slider-counter-badge">
                📸 {{ activeQuickViewAngle + 1 }} / {{ quickViewImagesList.length }}
              </span>

              <!-- Previous Arrow (Flipkart style) -->
              <button
                v-if="quickViewImagesList.length > 1"
                type="button"
                class="slider-nav-btn prev-btn"
                @click.stop="prevQuickViewAngle"
                title="मागील फोटो (Previous)"
              >
                ‹
              </button>

              <!-- Main Product Image -->
              <img
                :src="currentQuickViewImage"
                :alt="selectedProductQuickView.name"
                class="quick-view-img"
                @error="handleImageFallback($event)"
              />

              <!-- Next Arrow (Flipkart style) -->
              <button
                v-if="quickViewImagesList.length > 1"
                type="button"
                class="slider-nav-btn next-btn"
                @click.stop="nextQuickViewAngle"
                title="पुढील फोटो (Next)"
              >
                ›
              </button>

              <!-- Active Angle Floating Badge -->
              <span class="active-angle-badge">
                {{ getAngleLabel(activeQuickViewAngle) }}
              </span>
            </div>

            <!-- Flipkart-Style Dot Carousel Indicators -->
            <div class="slider-dots-row" v-if="quickViewImagesList.length > 1">
              <button
                v-for="(_, dIdx) in quickViewImagesList"
                :key="'dot-' + dIdx"
                type="button"
                class="slider-dot"
                :class="{ active: activeQuickViewAngle === dIdx }"
                @click="activeQuickViewAngle = dIdx"
                :title="getAngleShortLabel(dIdx)"
              ></button>
            </div>

            <!-- Multi-Angle Thumbnails Selector -->
            <div class="quick-view-angles-row" v-if="quickViewImagesList.length > 1">
              <button
                v-for="(img, idx) in quickViewImagesList"
                :key="idx"
                type="button"
                class="angle-thumb-btn"
                :class="{ active: activeQuickViewAngle === idx }"
                @click="activeQuickViewAngle = idx"
              >
                <img :src="img" :alt="getAngleLabel(idx)" class="angle-thumb-img" @error="handleImageFallback($event)" />
                <span class="angle-thumb-label">{{ getAngleShortLabel(idx) }}</span>
              </button>
            </div>

            <div style="display: flex; gap: 8px; flex-wrap: wrap; justify-content: center; margin-top: 10px;">
              <span v-if="selectedProductQuickView.is_loose" class="loose-badge" style="position: static;">
                🌾 {{ t('badge_loose') }}
              </span>
              <span v-else class="packed-badge" style="position: static;">
                📦 {{ t('badge_packed') }}
              </span>
              <div class="quick-view-trust-tag" style="margin-top: 0;">
                ✓ {{ t('quick_view_guarantee') }}
              </div>
            </div>
          </div>

          <!-- Right: Details & Purchase Options -->
          <div class="quick-view-info-pane">
            <span class="quick-view-brand-tag" v-if="selectedProductQuickView.brand">{{ selectedProductQuickView.brand }}</span>
            <h2 class="quick-view-title">{{ getLocalizedProductName(selectedProductQuickView, currentLang) }}</h2>
            <div class="quick-view-sub">{{ currentLang === 'en' ? (selectedProductQuickView.name_hi || '') : selectedProductQuickView.name }}</div>

            <p class="quick-view-desc">{{ selectedProductQuickView.description }}</p>

            <div class="quick-view-mandi-promise">
              <span>🌾</span>
              <span>{{ t('quick_view_mandi_badge') }} • {{ t('hero_perk_weight') }}</span>
            </div>

            <!-- Variants Selector & Custom kg Mode -->
            <div class="variants-wrap" style="margin-top: 18px;" v-if="selectedProductQuickView.variants && selectedProductQuickView.variants.length > 0">
              <div class="variant-label-title">{{ t('weight_select_label') }}</div>
              <div class="variant-options">
                <button
                  v-for="v in selectedProductQuickView.variants"
                  :key="v.id"
                  class="variant-chip"
                  :class="{ selected: selectedVariants[selectedProductQuickView.id] === v.id && !customWeightMode[selectedProductQuickView.id] }"
                  @click="selectVariant(selectedProductQuickView.id, v.id)"
                >
                  {{ v.unit_size }}
                </button>
                <!-- Custom Weight Option for Loose Items -->
                <button
                  v-if="isLooseProduct(selectedProductQuickView)"
                  class="variant-chip custom-chip"
                  :class="{ selected: customWeightMode[selectedProductQuickView.id] }"
                  @click="enableCustomWeight(selectedProductQuickView)"
                >
                  ⚖️ {{ t('custom_weight_btn') }}
                </button>
              </div>
            </div>

            <!-- Custom Weight Input Mode -->
            <div v-if="customWeightMode[selectedProductQuickView.id]" class="custom-weight-box" style="margin-top: 14px;">
              <div class="custom-weight-header">
                <span>⚖️ {{ t('enter_custom_weight') }}</span>
                <span class="custom-rate-badge">{{ t('per_kg_rate') }}: ₹{{ getBasePerKgRate(selectedProductQuickView) }}/kg</span>
              </div>
              <div class="custom-input-group">
                <button type="button" class="weight-stepper-btn" @click="adjustCustomWeight(selectedProductQuickView.id, -0.5)">-0.5</button>
                <input
                  type="number"
                  step="0.25"
                  min="0.25"
                  max="100"
                  v-model.number="customWeightInputs[selectedProductQuickView.id]"
                  class="custom-weight-input"
                />
                <span class="custom-unit-label">kg</span>
                <button type="button" class="weight-stepper-btn" @click="adjustCustomWeight(selectedProductQuickView.id, 0.5)">+0.5</button>
                <button type="button" class="weight-stepper-btn" @click="adjustCustomWeight(selectedProductQuickView.id, 1.0)">+1.0</button>
              </div>
              <div class="quick-weights">
                <span class="quick-chip" @click="setQuickCustomWeight(selectedProductQuickView.id, 1.5)">1.5kg</span>
                <span class="quick-chip" @click="setQuickCustomWeight(selectedProductQuickView.id, 2.5)">2.5kg</span>
                <span class="quick-chip" @click="setQuickCustomWeight(selectedProductQuickView.id, 5.0)">5kg</span>
                <span class="quick-chip" @click="setQuickCustomWeight(selectedProductQuickView.id, 10.0)">10kg</span>
              </div>
              <div class="custom-price-calc">
                <span>{{ t('custom_total_label') }}:</span>
                <strong class="custom-total-val">₹{{ getCustomWeightPrice(selectedProductQuickView) }}</strong>
              </div>
              <button
                class="add-to-cart-btn custom-add-btn"
                @click="addCustomWeightItemToCart(selectedProductQuickView); closeQuickView();"
                :disabled="!customWeightInputs[selectedProductQuickView.id] || customWeightInputs[selectedProductQuickView.id] <= 0"
              >
                🛒 {{ customWeightInputs[selectedProductQuickView.id] || 0 }} kg {{ t('add_custom_btn') }}
              </button>
            </div>

            <!-- Standard Variant Mode -->
            <template v-else>
              <div class="price-row" style="margin-top: 16px;" v-if="getActiveVariant(selectedProductQuickView)">
                <span class="selling-price" style="font-size: 1.5rem;">₹{{ getActiveVariant(selectedProductQuickView).selling_price }}</span>
              </div>

              <div style="margin-top: 16px;" v-if="getActiveVariant(selectedProductQuickView)">
                <div v-if="!getActiveVariant(selectedProductQuickView).is_available" class="out-of-stock-action-wrap">
                  <button class="add-to-cart-btn btn-out-of-stock" style="padding: 12px 24px; font-size: 1rem;" disabled>
                    🚫 {{ t('out_of_stock') }}
                  </button>
                  <button
                    type="button"
                    class="btn-notify-me"
                    @click="openNotifyModal(selectedProductQuickView, getActiveVariant(selectedProductQuickView))"
                    style="margin-top: 10px; width: 100%; background: #ecfdf5; border: 1.5px solid #059669; color: #065f46; font-weight: 700; font-size: 0.92rem; padding: 10px 16px; border-radius: 10px; cursor: pointer; display: flex; align-items: center; justify-content: center; gap: 8px; transition: all 0.2s ease;"
                  >
                    {{ t('notify_me_btn') }}
                  </button>
                </div>
                <div v-else-if="getCartItemQuantity(selectedProductQuickView.id, getActiveVariant(selectedProductQuickView).id) === 0">
                  <button
                    class="add-to-cart-btn"
                    style="padding: 12px 24px; font-size: 1rem;"
                    @click="addToCart(selectedProductQuickView, getActiveVariant(selectedProductQuickView))"
                  >
                    + {{ t('add_to_cart') }}
                  </button>
                </div>
                <div v-else class="qty-control-row" style="max-width: 180px;">
                  <button class="qty-btn" @click="decreaseQuantity(getActiveVariant(selectedProductQuickView).id)">-</button>
                  <span class="qty-display" style="font-size: 1.1rem;">
                    {{ getCartItemQuantity(selectedProductQuickView.id, getActiveVariant(selectedProductQuickView).id) }}
                  </span>
                  <button class="qty-btn" @click="increaseQuantity(getActiveVariant(selectedProductQuickView).id)">+</button>
                </div>
              </div>
            </template>
          </div>
        </div>
      </div>
    </div>

    <!-- iOS PWA Install Instruction Modal -->
    <div class="modal-overlay" v-if="showIOSModal" @click.self="showIOSModal = false">
      <div class="modal-card" style="max-width: 420px; text-align: center; padding: 28px;">
        <div style="font-size: 3rem; margin-bottom: 12px;">📲</div>
        <h3 style="font-size: 1.3rem; font-weight: 800; color: #064e3b; margin-bottom: 8px;">Install Komal Mart on iPhone</h3>
        <p style="font-size: 0.92rem; color: #4b5563; line-height: 1.5; margin-bottom: 20px;">
          To install this app on your iPhone or iPad:
          <br /><br />
          1. Tap the <strong>Share</strong> button (📤) at the bottom of Safari.
          <br />
          2. Scroll down and tap <strong>"Add to Home Screen"</strong> (➕).
        </p>
        <button class="submit-btn" @click="showIOSModal = false" style="width: 100%;">
          Got it! 👍
        </button>
      </div>
    </div>

    <!-- Floating Bottom Cart Strip (Blinkit / Zepto Style) -->
    <transition name="floating-cart-slide">
      <div
        v-if="cartTotalQuantity > 0 && !isCartOpen && !isAdminLoggedIn"
        class="floating-cart-strip"
        @click="isCartOpen = true"
      >
        <div class="floating-cart-content">
          <div class="floating-cart-left">
            <div class="floating-cart-badge">
              <svg viewBox="0 0 24 24" width="20" height="20" fill="none" stroke="currentColor" stroke-width="2.3" stroke-linecap="round" stroke-linejoin="round">
                <path d="M6 2L3 6v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2V6l-3-4z"></path>
                <line x1="3" y1="6" x2="21" y2="6"></line>
                <path d="M16 10a4 4 0 0 1-8 0"></path>
              </svg>
              <span class="floating-cart-qty">{{ cartTotalQuantity }}</span>
            </div>
            <div class="floating-cart-info">
              <span class="floating-cart-price">₹{{ cartTotalAmount }}</span>
              <span class="floating-cart-items-label">{{ cartTotalQuantity }} {{ t('floating_cart_items') }}</span>
            </div>
          </div>
          <div class="floating-cart-right">
            <span class="floating-cart-action">{{ t('floating_cart_view') }}</span>
            <span class="floating-cart-arrow">➔</span>
          </div>
        </div>
      </div>
    </transition>

    <!-- Mobile Bottom Navigation Bar (Customer View) -->
    <nav v-if="!isAdminLoggedIn" class="mobile-bottom-nav">
      <button
        class="bottom-nav-item"
        :class="{ active: currentBottomTab === 'home' && !showMobileCategorySheet }"
        @click="handleBottomNav('home')"
      >
        <span class="bottom-nav-icon">🏠</span>
        <span class="bottom-nav-label">{{ t('bottom_nav_home') }}</span>
      </button>

      <button
        class="bottom-nav-item"
        :class="{ active: showMobileCategorySheet || selectedCategorySlug !== '' }"
        @click="handleBottomNav('categories')"
      >
        <span class="bottom-nav-icon">📂</span>
        <span class="bottom-nav-label">{{ t('bottom_nav_categories') }}</span>
      </button>

      <button
        class="bottom-nav-item"
        :class="{ active: currentBottomTab === 'khata' }"
        @click="handleBottomNav('khata')"
      >
        <span class="bottom-nav-icon">📖</span>
        <span class="bottom-nav-label">{{ t('bottom_nav_khata') }}</span>
      </button>

      <button
        class="bottom-nav-item cart-item"
        :class="{ active: isCartOpen }"
        @click="handleBottomNav('cart')"
      >
        <div class="bottom-nav-cart-icon-wrapper">
          <span class="bottom-nav-icon">🛒</span>
          <span v-if="cartTotalQuantity > 0" class="bottom-nav-cart-badge">{{ cartTotalQuantity }}</span>
        </div>
        <span class="bottom-nav-label">{{ t('bottom_nav_cart') }}</span>
      </button>
    </nav>

    <!-- Mobile Bottom Navigation Bar (Store Owner / Admin ERP View - Sleek Handheld POS Dock) -->
    <nav v-else class="mobile-bottom-nav admin-bottom-nav">
      <button
        class="bottom-nav-item"
        :class="{ active: adminActiveTab === 'storefront' && !showAdminMoreSheet }"
        @click="switchAdminTab('storefront'); showAdminMoreSheet = false;"
      >
        <span class="bottom-nav-icon">🏪</span>
        <span class="bottom-nav-label">{{ currentLang === 'mr' ? 'दुकान' : (currentLang === 'hi' ? 'दुकान' : 'Store') }}</span>
      </button>

      <button
        class="bottom-nav-item"
        :class="{ active: adminActiveTab === 'pos' && !showAdminMoreSheet }"
        @click="switchAdminTab('pos'); showAdminMoreSheet = false;"
      >
        <span class="bottom-nav-icon">⚡</span>
        <span class="bottom-nav-label">POS</span>
      </button>

      <button
        class="bottom-nav-item"
        :class="{ active: adminActiveTab === 'orders' && !showAdminMoreSheet }"
        @click="switchAdminTab('orders'); showAdminMoreSheet = false;"
      >
        <div class="bottom-nav-cart-icon-wrapper">
          <span class="bottom-nav-icon">🧾</span>
          <span v-if="pendingVerificationAdminOrders.length > 0" class="bottom-nav-cart-badge" style="background: #d97706;">
            {{ pendingVerificationAdminOrders.length }}
          </span>
          <span v-else-if="unpaidAdminOrders.length > 0" class="bottom-nav-cart-badge">
            {{ unpaidAdminOrders.length }}
          </span>
        </div>
        <span class="bottom-nav-label">{{ currentLang === 'mr' ? 'ऑर्डर्स' : (currentLang === 'hi' ? 'ऑर्डर्स' : 'Orders') }}</span>
      </button>

      <button
        class="bottom-nav-item"
        :class="{ active: adminActiveTab === 'khata' && !showAdminMoreSheet }"
        @click="switchAdminTab('khata'); showAdminMoreSheet = false;"
      >
        <div class="bottom-nav-cart-icon-wrapper">
          <span class="bottom-nav-icon">📒</span>
          <span v-if="adminKhataSummary.total_market_udhaar > 0" class="bottom-nav-cart-badge" style="background: #dc2626; font-size: 0.65rem;">
            ₹
          </span>
        </div>
        <span class="bottom-nav-label">{{ currentLang === 'mr' ? 'खाता' : (currentLang === 'hi' ? 'खाता' : 'Khata') }}</span>
      </button>

      <button
        class="bottom-nav-item"
        :class="{ active: ['customers', 'zreport', 'restock', 'support', 'zones'].includes(adminActiveTab) || showAdminMoreSheet }"
        @click="showAdminMoreSheet = !showAdminMoreSheet"
      >
        <div class="bottom-nav-cart-icon-wrapper">
          <span class="bottom-nav-icon">☰</span>
          <span v-if="pendingRestockCount > 0 || adminOpenComplaintsCount > 0" class="bottom-nav-cart-badge" style="background: #ef4444;">
            {{ pendingRestockCount + adminOpenComplaintsCount }}
          </span>
        </div>
        <span class="bottom-nav-label">{{ currentLang === 'mr' ? 'अधिक' : (currentLang === 'hi' ? 'अन्य' : 'More') }}</span>
      </button>
    </nav>

    <!-- Store Admin "More" Hub Bottom Sheet Drawer -->
    <div class="modal-overlay" v-if="showAdminMoreSheet" @click.self="showAdminMoreSheet = false">
      <div class="admin-more-sheet">
        <div class="admin-more-sheet-handle"></div>
        <div class="admin-more-sheet-head">
          <div class="admin-more-sheet-title">
            <span style="font-size: 1.35rem;">🏪</span>
            <div>
              <h3 style="margin: 0; font-size: 1.05rem; font-weight: 800; color: #0f172a;">Store ERP Management</h3>
              <p style="margin: 2px 0 0; font-size: 0.74rem; color: #64748b;">All secondary tools & daily audit functions</p>
            </div>
          </div>
          <button class="admin-more-sheet-close" @click="showAdminMoreSheet = false">✕</button>
        </div>

        <div class="admin-more-sheet-grid">
          <button
            type="button"
            class="admin-more-sheet-card"
            :class="{ active: adminActiveTab === 'inventory' }"
            @click="switchAdminTab('inventory'); showAdminMoreSheet = false;"
          >
            <div class="admin-more-icon-box" style="background: #f1f5f9; color: #475569;">📋</div>
            <div class="admin-more-info">
              <span class="admin-more-name">{{ t('admin_tab_inventory') }}</span>
              <span class="admin-more-desc">Full Inventory Spreadsheet Table</span>
            </div>
            <span class="admin-more-badge badge-blue">{{ products.length }}</span>
          </button>

          <button
            type="button"
            class="admin-more-sheet-card"
            :class="{ active: adminActiveTab === 'customers' }"
            @click="switchAdminTab('customers'); showAdminMoreSheet = false;"
          >
            <div class="admin-more-icon-box" style="background: #eff6ff; color: #2563eb;">👥</div>
            <div class="admin-more-info">
              <span class="admin-more-name">{{ t('admin_tab_customers') }}</span>
              <span class="admin-more-desc">Ledgers, Past Bills & Udhaar</span>
            </div>
            <span v-if="khataCustomersCount > 0" class="admin-more-badge badge-blue">{{ khataCustomersCount }}</span>
          </button>

          <button
            type="button"
            class="admin-more-sheet-card"
            :class="{ active: adminActiveTab === 'zreport' }"
            @click="switchAdminTab('zreport'); showAdminMoreSheet = false;"
          >
            <div class="admin-more-icon-box" style="background: #f0fdf4; color: #16a34a;">📊</div>
            <div class="admin-more-info">
              <span class="admin-more-name">{{ t('admin_tab_zreport') }}</span>
              <span class="admin-more-desc">Cash & UPI Audit & Print</span>
            </div>
          </button>

          <button
            type="button"
            class="admin-more-sheet-card"
            :class="{ active: adminActiveTab === 'restock' }"
            @click="switchAdminTab('restock'); showAdminMoreSheet = false;"
          >
            <div class="admin-more-icon-box" style="background: #fffbeb; color: #d97706;">⚠️</div>
            <div class="admin-more-info">
              <span class="admin-more-name">{{ t('admin_tab_restock') }}</span>
              <span class="admin-more-desc">Low inventory alerts</span>
            </div>
            <span v-if="pendingRestockCount > 0" class="admin-more-badge badge-amber">{{ pendingRestockCount }}</span>
          </button>

          <button
            type="button"
            class="admin-more-sheet-card"
            :class="{ active: adminActiveTab === 'support' }"
            @click="switchAdminTab('support'); showAdminMoreSheet = false;"
          >
            <div class="admin-more-icon-box" style="background: #fef2f2; color: #dc2626;">💬</div>
            <div class="admin-more-info">
              <span class="admin-more-name">{{ t('admin_tab_support') }}</span>
              <span class="admin-more-desc">Customer Grievances & Tickets</span>
            </div>
            <span v-if="adminOpenComplaintsCount > 0" class="admin-more-badge badge-red">{{ adminOpenComplaintsCount }}</span>
          </button>

          <button
            type="button"
            class="admin-more-sheet-card"
            :class="{ active: adminActiveTab === 'zones' }"
            @click="switchAdminTab('zones'); showAdminMoreSheet = false;"
          >
            <div class="admin-more-icon-box" style="background: #ecfdf5; color: #059669;">🛵</div>
            <div class="admin-more-info">
              <span class="admin-more-name">{{ currentLang === 'en' ? 'Delivery Zones' : (currentLang === 'mr' ? 'डिलिव्हरी परिसर' : 'डिलीवरी क्षेत्र') }}</span>
              <span class="admin-more-desc">Area delivery holds & delays</span>
            </div>
            <span v-if="Object.values(areaDeliveryHolds).filter(h => h.is_held).length > 0" class="admin-more-badge badge-amber">
              {{ Object.values(areaDeliveryHolds).filter(h => h.is_held).length }} Hold
            </span>
          </button>

          <button
            type="button"
            class="admin-more-sheet-card"
            @click="showBatchIngestModal = true; showAdminMoreSheet = false;"
          >
            <div class="admin-more-icon-box" style="background: #fdf4ff; color: #9333ea;">⚡</div>
            <div class="admin-more-info">
              <span class="admin-more-name">Batch Photos Ingest</span>
              <span class="admin-more-desc">Zero-Token Offline Photo OCR</span>
            </div>
          </button>

          <button
            type="button"
            class="admin-more-sheet-card"
            @click="downloadDatabaseBackup(); showAdminMoreSheet = false;"
          >
            <div class="admin-more-icon-box" style="background: #f0f9ff; color: #0284c7;">💾</div>
            <div class="admin-more-info">
              <span class="admin-more-name">Download SQLite DB</span>
              <span class="admin-more-desc">Full store snapshot backup</span>
            </div>
          </button>

          <button
            type="button"
            class="admin-more-sheet-card reset-card"
            @click="confirmResetSeed(); showAdminMoreSheet = false;"
          >
            <div class="admin-more-icon-box" style="background: #fee2e2; color: #b91c1c;">🔄</div>
            <div class="admin-more-info">
              <span class="admin-more-name" style="color: #b91c1c;">Reset Default Catalog</span>
              <span class="admin-more-desc">Reload seed items</span>
            </div>
          </button>
        </div>
      </div>
    </div>

    <!-- Mobile Category Bottom Sheet Modal -->
    <div class="modal-overlay" v-if="showMobileCategorySheet" @click.self="showMobileCategorySheet = false">
      <div class="mobile-category-sheet">
        <div class="category-sheet-header">
          <div class="category-sheet-title">
            <span style="font-size: 1.35rem;">📂</span>
            <h3 style="margin: 0; font-size: 1.15rem; font-weight: 800; color: #064e3b;">{{ t('bottom_nav_categories') }}</h3>
          </div>
          <button class="category-sheet-close" @click="showMobileCategorySheet = false">✕</button>
        </div>
        <div class="category-sheet-grid">
          <button
            class="category-sheet-card"
            :class="{ active: selectedCategorySlug === '' }"
            @click="selectCategoryFromSheet('')"
          >
            <span class="cat-sheet-emoji">🌟</span>
            <span class="cat-sheet-name">{{ t('cat_all') }}</span>
          </button>
          <button
            v-for="cat in categories"
            :key="cat.id"
            class="category-sheet-card"
            :class="{ active: selectedCategorySlug === cat.slug }"
            @click="selectCategoryFromSheet(cat.slug)"
          >
            <span class="cat-sheet-emoji">{{ getCategoryEmoji(cat.slug) }}</span>
            <span class="cat-sheet-name">{{ getLocalizedCategoryName(cat, currentLang) }}</span>
            <span class="cat-sheet-count">{{ cat.product_count }}</span>
          </button>
        </div>
      </div>
    </div>

    <!-- Phone QR Code Modal -->
    <div class="modal-overlay" v-if="showQRModal" @click.self="showQRModal = false">
      <div class="modal-card" style="max-width: 440px; text-align: center; padding: 24px;">
        <div style="font-size: 2.2rem; margin-bottom: 6px;">📱</div>
        <h3 style="font-size: 1.3rem; font-weight: 800; color: #064e3b; margin-bottom: 4px;">
          Open & Install on Phone
        </h3>
        <p style="font-size: 0.84rem; color: #64748b; line-height: 1.4; margin-bottom: 12px;">
          Scan this QR code with your phone camera or Google Lens to open <strong>Komal Mart</strong> instantly on mobile!
        </p>

        <div style="background: #ffffff; border: 2.5px dashed #059669; border-radius: 16px; padding: 14px; display: inline-block; margin-bottom: 12px; box-shadow: 0 4px 12px rgba(0,0,0,0.06);">
          <img :src="`https://api.qrserver.com/v1/create-qr-code/?size=220x220&data=${encodeURIComponent(currentOrigin)}`" alt="Scan to open on phone" width="200" height="200" style="display: block; border-radius: 8px; margin: 0 auto;" />
        </div>

        <div style="background: #f1f5f9; border-radius: 10px; padding: 8px 12px; margin-bottom: 12px; word-break: break-all; font-weight: 700; color: #064e3b; font-size: 0.86rem;">
          🔗 {{ currentOrigin }}
        </div>

        <div style="display: flex; gap: 8px; justify-content: center; margin-bottom: 14px; flex-wrap: wrap;">
          <button type="button" @click="copyLiveLink" class="user-btn" style="padding: 7px 14px; font-size: 0.82rem; background: #059669; color: white; border: none; border-radius: 8px; font-weight: 700; cursor: pointer;">
            📋 Copy Link
          </button>
          <a :href="`https://api.whatsapp.com/send?text=${encodeURIComponent('Komal Mart - Order Daily Kirana Online: ' + currentOrigin)}`" target="_blank" rel="noopener noreferrer" style="text-decoration: none; padding: 7px 14px; font-size: 0.82rem; border-radius: 8px; background: #25D366; color: white; font-weight: 700; display: inline-flex; align-items: center; gap: 6px;">
            💬 WhatsApp
          </a>
        </div>

        <div style="background: #ecfdf5; border: 1px solid #a7f3d0; border-radius: 12px; padding: 10px 14px; margin-bottom: 14px; font-size: 0.82rem; color: #065f46; text-align: left;">
          <strong>💡 2 Quick Steps:</strong>
          <ol style="margin: 4px 0 0 16px; padding: 0; line-height: 1.45;">
            <li>Scan QR with phone camera or click link.</li>
            <li>Tap <strong>"Install App"</strong> on phone for 1-tap ordering!</li>
          </ol>
        </div>

        <button class="submit-btn" @click="showQRModal = false" style="width: 100%;">
          Close
        </button>
      </div>
    </div>

    <!-- PWA Install Guide Modal (For Desktop Browser) -->
    <div class="modal-overlay" v-if="showInstallGuideModal" @click.self="showInstallGuideModal = false">
      <div class="modal-card" style="max-width: 440px; text-align: center; padding: 24px;">
        <div style="margin-bottom: 10px;">
          <img src="/favicon.svg" alt="Komal Mart" style="width: 64px; height: 64px; border-radius: 16px; box-shadow: 0 4px 14px rgba(6,78,59,0.25);" />
        </div>
        <h3 style="font-size: 1.25rem; font-weight: 800; color: #064e3b; margin-bottom: 8px;">
          Install Komal Mart
        </h3>
        <p style="font-size: 0.86rem; color: #475569; margin-bottom: 16px; line-height: 1.45;">
          Install Komal Mart on your phone or laptop for fastest checkout and 1-click home screen access!
        </p>

        <div style="background: #f8fafc; border: 1.5px solid #e2e8f0; border-radius: 12px; padding: 14px; text-align: left; font-size: 0.84rem; color: #1e293b; margin-bottom: 16px;">
          <div style="margin-bottom: 14px;">
            <strong style="color: #065f46;">📱 Standalone Android App (APK):</strong>
            <div style="color: #64748b; margin-top: 4px; display: flex; flex-direction: column; gap: 6px;">
              <span>Fastest native app experience without browser URL bar:</span>
              <a href="/downloads/KomalMart.apk" download="KomalMart.apk" style="display: inline-flex; align-items: center; justify-content: center; gap: 6px; padding: 9px 16px; background: #064e3b; color: #ffffff; border-radius: 8px; font-weight: 700; text-decoration: none; font-size: 0.86rem; box-shadow: 0 3px 8px rgba(6,78,59,0.2);">
                📥 Download Android App (.APK ~1MB)
              </a>
            </div>
          </div>
          <div style="margin-bottom: 12px;">
            <strong style="color: #065f46;">💻 On Laptop (Chrome / Brave / Edge):</strong>
            <div style="color: #64748b; margin-top: 3px;">
              • If installed, click the <strong>[ ↗ ]</strong> icon in your URL bar ↗️ to launch the desktop app.<br>
              • If not installed, click <strong>⊕ (Install)</strong> in the address bar or browser menu (⋮).
            </div>
          </div>
          <div>
            <strong style="color: #065f46;">🍎 On iPhone (iOS Safari):</strong>
            <div style="color: #64748b; margin-top: 3px;">
              Tap the <strong>Share</strong> button (⎋) at the bottom ➔ tap <strong>"Add to Home Screen"</strong>.
            </div>
          </div>
        </div>

        <button class="submit-btn" @click="showInstallGuideModal = false" style="width: 100%;">
          Close Instructions
        </button>
      </div>
    </div>

    <!-- Floating Komal AI Voice & Draft Bill Trigger (Customer View & Storefront Admin) -->
    <button
      v-if="!isAdminLoggedIn || adminActiveTab === 'storefront'"
      class="floating-komal-ai-btn"
      :class="{ 'has-floating-cart': cartTotalQuantity > 0, 'is-dukandar-ai': isAdminLoggedIn && !adminPreviewAsCustomer }"
      @click="openAiModalByRole"
      :aria-label="isAdminLoggedIn && !adminPreviewAsCustomer ? 'Dukandar AI Store Assistant' : 'Komal AI Smart Voice Order'"
      :title="isAdminLoggedIn && !adminPreviewAsCustomer ? '👑 कोमल AI दुकानदार सहाय्यक (Store Control)' : 'Komal AI Voice Assistant'"
    >
      <span class="ai-sparkle-icon">{{ isAdminLoggedIn && !adminPreviewAsCustomer ? '👑' : '🎙️' }}</span>
      <span class="ai-floating-label">{{ isAdminLoggedIn && !adminPreviewAsCustomer ? (currentLang === 'mr' ? 'दुकानदार AI' : 'Dukandar AI') : t('ai_btn_floating') }}</span>
      <span class="ai-live-badge">{{ isAdminLoggedIn && !adminPreviewAsCustomer ? 'ADMIN' : 'AI' }}</span>
    </button>

    <!-- Komal AI Smart Draft Bill Modal -->
    <div class="modal-overlay" v-if="showKomalAiModal" @click.self="closeKomalAiModal">
      <div class="modal-card komal-ai-modal-card">
        <!-- Header -->
        <div class="komal-ai-header">
          <div class="komal-ai-title-wrap">
            <h3 class="komal-ai-title">
              <span class="ai-sparkle-anim">✨</span> {{ tAi('ai_modal_title') }}
            </h3>
            <p class="komal-ai-subtitle">{{ tAi('ai_modal_subtitle') }}</p>
          </div>
          <button class="close-btn" @click="closeKomalAiModal">✕</button>
        </div>

        <!-- Language Selector Chips -->
        <div class="komal-ai-lang-bar">
          <span class="ai-lang-label">🗣️ {{ (aiLanguage || currentLang) === 'mr' ? 'भाषा निवडा:' : ((aiLanguage || currentLang) === 'hi' ? 'भाषा चुनें:' : 'Language:') }}</span>
          <button
            type="button"
            class="ai-lang-chip"
            :class="{ active: aiLanguage === 'mr' }"
            @click="setAiLanguage('mr')"
          >
            मराठी
          </button>
          <button
            type="button"
            class="ai-lang-chip"
            :class="{ active: aiLanguage === 'hi' }"
            @click="setAiLanguage('hi')"
          >
            हिंदी
          </button>
          <button
            type="button"
            class="ai-lang-chip"
            :class="{ active: aiLanguage === 'en' }"
            @click="setAiLanguage('en')"
          >
            English
          </button>
        </div>

        <!-- Mode Switcher: Voice / Typed vs Scan Handwritten Slip -->
        <div class="komal-ai-mode-tabs">
          <button
            type="button"
            class="ai-mode-tab-btn"
            :class="{ active: aiScanMode === 'voice' }"
            @click="aiScanMode = 'voice'"
          >
            🎙️ {{ (aiLanguage || currentLang) === 'mr' ? 'बोलून / टाईप करून' : ((aiLanguage || currentLang) === 'hi' ? 'बोलकर / टाइप करके' : 'Voice / Text') }}
          </button>
          <button
            type="button"
            class="ai-mode-tab-btn"
            :class="{ active: aiScanMode === 'photo' }"
            @click="aiScanMode = 'photo'"
          >
            📷 {{ (aiLanguage || currentLang) === 'mr' ? 'हाताने लिहिलेली यादी स्कॅन करा' : ((aiLanguage || currentLang) === 'hi' ? 'हाथ से लिखी पर्ची स्कैन करें' : 'Scan Handwritten List') }}
          </button>
        </div>

        <!-- Microphone / Input Section -->
        <div class="komal-ai-input-section">
          <!-- Voice Mode Controls -->
          <template v-if="aiScanMode === 'voice'">
            <!-- Voice Button -->
            <div class="komal-ai-mic-wrapper">
              <button
                type="button"
                class="komal-ai-mic-btn"
                :class="{ 'is-recording': isRecording }"
                @click="toggleSpeechRecognition"
                :title="isRecording ? tAi('ai_mic_stop') : tAi('ai_mic_start')"
              >
                <div v-if="isRecording" class="mic-wave-pulse"></div>
                <span class="mic-icon">{{ isRecording ? '⏹️' : '🎙️' }}</span>
              </button>
              <span class="mic-status-hint">
                {{ isRecording ? tAi('ai_mic_listening') : tAi('ai_mic_start') }}
              </span>
            </div>

            <!-- Textarea for spoken / typed list -->
            <div class="ai-input-group">
              <textarea
                v-model="aiInputText"
                rows="3"
                class="komal-ai-textarea"
                :placeholder="(aiLanguage || currentLang) === 'mr' ? 'उदा. कोमल २ किलो साखर, ५ किलो चक्की आटा, आणि तूर डाळ स्वस्त वाली १ किलो...' : ((aiLanguage || currentLang) === 'hi' ? 'उदा. कोमल २ किलो चीनी, ५ किलो आटा, और १ किलो तूर दाल सस्ती वाली...' : 'e.g. 2kg sugar, 5kg chakki atta, and 1kg cheapest toor dal...')"
              ></textarea>
              <div class="ai-textarea-footer">
                <span class="ai-hint-caption">
                  {{ (aiLanguage || currentLang) === 'mr' ? '💡 तुम्ही मराठी, हिंदी किंवा इंग्लिशमध्ये बोलू किंवा टाईप करू शकता.' : ((aiLanguage || currentLang) === 'hi' ? '💡 आप हिंदी, मराठी या इंग्लिश में बोल या टाइप कर सकते हैं।' : '💡 You can speak or type freely in Marathi, Hindi, or English.') }}
                </span>
                <button
                  v-if="aiInputText"
                  type="button"
                  class="ai-clear-btn"
                  @click="aiInputText = ''; aiResult = null"
                >
                  {{ tAi('ai_clear') }}
                </button>
              </div>
            </div>

            <!-- Quick Prompts / Examples -->
            <div class="ai-quick-examples" v-if="!aiResult">
              <span class="quick-examples-title">⚡ {{ (aiLanguage || currentLang) === 'mr' ? 'उदाहरणे (टॅप करा):' : ((aiLanguage || currentLang) === 'hi' ? 'उदाहरण (टैप करें):' : 'Try examples:') }}</span>
              <div class="quick-chips">
                <button
                  type="button"
                  class="quick-chip"
                  @click="applyAiExample('२ किलो साखर, ५ किलो चक्की आटा, १ किलो तूर डाळ स्वस्त वाली')"
                >
                  🌾 २kg साखर, ५kg आटा, १kg डाळ
                </button>
                <button
                  type="button"
                  class="quick-chip"
                  @click="applyAiExample('1 packet Tata Tea Gold, 1 Colgate MaxFresh, 2 kg Poha')"
                >
                  ☕ Tata Tea, Colgate, पोहा
                </button>
                <button
                  type="button"
                  class="quick-chip"
                  @click="applyAiExample('१ लिटर मोहरीचे तेल, आधा किलो सुजी, १ किलो मीठ')"
                >
                  🍳 तेल, रवा, मीठ
                </button>
              </div>
            </div>
          </template>

          <!-- Photo Slip Mode Controls -->
          <template v-else>
            <div class="ai-photo-upload-box">
              <div class="ai-photo-prompt">
                <span class="ai-photo-main-icon">📝</span>
                <div class="ai-photo-prompt-text">
                  <strong>{{ (aiLanguage || currentLang) === 'mr' ? 'हाताने लिहिलेल्या किराणा यादीचा फोटो काढा' : ((aiLanguage || currentLang) === 'hi' ? 'हाथ से लिखी राशन पर्ची की फोटो खींचें' : 'Take a photo of your handwritten grocery list') }}</strong>
                  <p>{{ (aiLanguage || currentLang) === 'mr' ? 'कॅमेऱ्याने थेट फोटो काढा किंवा गॅलरीतून निवडा (जास्तीत जास्त ५ फोटो). आमचा AI आपोआप ड्राफ्ट बिल तयार करेल.' : ((aiLanguage || currentLang) === 'hi' ? 'सीधे कैमरे से फोटो लें या गैलरी से चुनें (अधिकतम 5 फोटो)। AI अपने आप ड्राफ्ट बिल तैयार कर देगा।' : 'Snap directly with camera or upload from gallery (max 5 photos). AI will generate your draft bill.') }}</p>
                </div>
              </div>

              <!-- Upload Buttons: Camera & Gallery -->
              <div class="ai-photo-actions-row">
                <!-- Camera Snap Button -->
                <label class="ai-photo-btn ai-photo-camera-btn">
                  📷 {{ (aiLanguage || currentLang) === 'mr' ? 'कॅमेऱ्याने फोटो काढा' : ((aiLanguage || currentLang) === 'hi' ? 'कैमरे से फोटो लें' : 'Take Photo (Camera)') }}
                  <input
                    type="file"
                    accept="image/*"
                    capture="environment"
                    style="display: none;"
                    @change="handleSlipImageUpload"
                    :disabled="aiImageCompressing || aiUploadedImages.length >= 5"
                  />
                </label>

                <!-- Gallery Upload Button -->
                <label class="ai-photo-btn ai-photo-gallery-btn">
                  🖼️ {{ (aiLanguage || currentLang) === 'mr' ? 'गॅलरीतून निवडा' : ((aiLanguage || currentLang) === 'hi' ? 'गैलरी से चुनें' : 'Upload from Gallery') }}
                  <input
                    type="file"
                    accept="image/*"
                    multiple
                    style="display: none;"
                    @change="handleSlipImageUpload"
                    :disabled="aiImageCompressing || aiUploadedImages.length >= 5"
                  />
                </label>
              </div>

              <!-- Compression Loading Spinner -->
              <div v-if="aiImageCompressing" class="ai-photo-compressing-msg">
                <span>⏳</span> {{ (aiLanguage || currentLang) === 'mr' ? 'फोटो ऑप्टिमाइझ करत आहे...' : ((aiLanguage || currentLang) === 'hi' ? 'फोटो ऑप्टिमाइज़ हो रही है...' : 'Optimizing photo...') }}
              </div>

              <!-- Image Previews Grid -->
              <div v-if="aiUploadedImages.length > 0" class="ai-uploaded-previews-grid">
                <div
                  v-for="(img, imgIdx) in aiUploadedImages"
                  :key="img.id"
                  class="ai-uploaded-thumb-card"
                >
                  <img :src="img.preview" :alt="'Slip ' + (imgIdx + 1)" class="ai-uploaded-thumb-img" />
                  <div class="ai-uploaded-thumb-meta">
                    <span class="ai-thumb-num">#{{ imgIdx + 1 }}</span>
                    <span class="ai-thumb-size">{{ img.sizeKb }} KB</span>
                  </div>
                  <button
                    type="button"
                    class="ai-uploaded-remove-btn"
                    @click="removeSlipImage(imgIdx)"
                    title="Remove this photo"
                  >
                    ✕
                  </button>
                </div>
              </div>

              <div v-if="aiUploadedImages.length > 0" class="ai-photo-count-info">
                <span>✓ {{ aiUploadedImages.length }}/5 {{ (aiLanguage || currentLang) === 'mr' ? 'फोटो जोडले' : ((aiLanguage || currentLang) === 'hi' ? 'फोटो जोड़े गए' : 'photos added') }}</span>
                <button
                  type="button"
                  class="ai-photo-clear-all"
                  @click="aiUploadedImages = []"
                >
                  {{ (aiLanguage || currentLang) === 'mr' ? 'सर्व काढून टाका' : ((aiLanguage || currentLang) === 'hi' ? 'सभी हटाएं' : 'Clear All') }}
                </button>
              </div>
            </div>
          </template>

          <!-- Generate Bill Button -->
          <button
            type="button"
            class="komal-ai-generate-btn"
            :disabled="isAiLoading || (aiScanMode === 'voice' && !aiInputText.trim()) || (aiScanMode === 'photo' && aiUploadedImages.length === 0)"
            @click="handleProcessAiOrder"
          >
            <span v-if="isAiLoading" class="ai-spinner">⏳</span>
            <span v-else>⚡</span>
            {{ isAiLoading ? tAi('ai_analyzing') : (aiScanMode === 'photo' ? ((aiLanguage || currentLang) === 'mr' ? 'यादीतून ड्राफ्ट बिल तयार करा' : ((aiLanguage || currentLang) === 'hi' ? 'पर्ची से ड्राफ्ट बिल बनाएं' : 'Generate Bill from Slip')) : tAi('ai_submit_btn')) }}
          </button>
        </div>

        <!-- Smart Draft Bill Output (Compiled Slip) -->
        <div v-if="aiResult" class="komal-ai-bill-section">
          <!-- AI Vocal Response Banner -->
          <div class="ai-summary-banner">
            <div class="ai-summary-text">
              <strong>🤖 Komal AI:</strong> {{ aiResult.summary_text }}
            </div>
            <button
              type="button"
              class="ai-speak-btn"
              @click="speakAiSummary(aiResult.summary_text)"
              title="Play AI voice"
            >
              🔊
            </button>
          </div>

          <!-- Bill Header -->
            <div class="ai-bill-title-bar">
            <h4>🧾 {{ tAi('ai_draft_bill_title') }}</h4>
            <span class="ai-bill-count">
              {{ aiResult.items ? aiResult.items.length : 0 }} {{ (aiLanguage || currentLang) === 'mr' ? 'वस्तू' : ((aiLanguage || currentLang) === 'hi' ? 'आइटम' : 'items') }}
            </span>
          </div>

          <!-- Bill Items List -->
          <div class="ai-bill-items-list">
            <div
              v-for="(item, idx) in aiResult.items"
              :key="idx"
              class="ai-bill-item-row"
              :class="{
                'is-matched': item.match_status === 'matched',
                'is-ambiguous': item.match_status === 'ambiguous',
                'is-unavailable': item.match_status === 'unavailable'
              }"
            >
              <!-- Thumbnail & Info -->
              <div class="ai-item-left">
                <img
                  :src="item.image_url || '/products/chakki-atta.jpg'"
                  :alt="item.product_name"
                  class="ai-item-thumb"
                  @error="handleImageFallback($event)"
                />
                <div class="ai-item-details">
                  <div class="ai-item-name">
                    {{ (aiLanguage || currentLang) === 'mr' ? item.product_name_hi || item.product_name : ((aiLanguage || currentLang) === 'hi' ? item.product_name_hi || item.product_name : item.product_name) }}
                  </div>
                  <div class="ai-item-sub">
                    <span v-if="item.match_status === 'matched'" class="ai-matched-badge">
                      ✓ {{ item.unit_size }} • ₹{{ item.unit_price }}
                      <span v-if="item.quantity > 1" style="font-weight: 800; color: #047857; margin-left: 4px;">
                        ({{ item.quantity }} {{ (aiLanguage || currentLang) === 'mr' ? 'पॅक' : ((aiLanguage || currentLang) === 'hi' ? 'पैक' : 'packs') }})
                      </span>
                    </span>
                    <span v-else-if="item.match_status === 'ambiguous'" class="ai-ambiguous-badge">
                      ⚠️ {{ tAi('ai_ambiguous_prompt') }}
                    </span>
                    <span v-else class="ai-unavailable-badge">
                      ❌ {{ tAi('ai_unavailable_tag') }}
                    </span>
                  </div>
                </div>
              </div>

              <!-- Matched Item Controls: Qty + Line Total -->
              <div v-if="item.match_status === 'matched'" class="ai-item-right">
                <div class="ai-qty-controls">
                  <button type="button" class="ai-qty-btn" @click="updateAiItemQty(item, -1)">-</button>
                  <span class="ai-qty-val">{{ item.quantity }}</span>
                  <button type="button" class="ai-qty-btn" @click="updateAiItemQty(item, 1)">+</button>
                </div>
                <div class="ai-line-total">
                  ₹{{ item.line_total || Math.round(item.unit_price * item.quantity * 100) / 100 }}
                </div>
                <button type="button" class="ai-remove-btn" @click="removeAiItem(idx)" title="Remove item">
                  🗑️
                </button>
              </div>

              <!-- Ambiguous Item Controls: Selection Chips -->
              <div v-if="item.match_status === 'ambiguous'" class="ai-ambiguous-options">
                <div class="ai-options-label">{{ tAi('ai_ambiguous_prompt') }}:</div>
                <div class="ai-chips-group">
                  <button
                    v-for="opt in item.options"
                    :key="opt.variant_id"
                    type="button"
                    class="ai-variant-chip"
                    @click="selectAmbiguousVariant(item, opt)"
                  >
                    {{ opt.label }}
                  </button>
                </div>
              </div>

              <!-- Unavailable Item Controls: Alternative Suggestion -->
              <div v-if="item.match_status === 'unavailable' && item.suggested_alternative" class="ai-alternative-box">
                <span class="ai-alt-text">
                  💡 {{ tAi('ai_add_alternative') }}: <strong>{{ item.suggested_alternative.product_name }}</strong> ({{ item.suggested_alternative.unit_size }} - ₹{{ item.suggested_alternative.price }})
                </span>
                <button
                  type="button"
                  class="ai-add-alt-btn"
                  @click="addAlternativeItem(item)"
                >
                  ➕ {{ tAi('ai_add_alternative') }}
                </button>
              </div>
            </div>
          </div>

          <!-- Quick Manual Search / Add Item to Draft Bill -->
          <div class="ai-add-item-bar">
            <div class="ai-add-input-wrap">
              <span class="ai-add-search-icon">🔍</span>
              <input
                type="text"
                v-model="draftSearchQuery"
                :placeholder="(aiLanguage || currentLang) === 'mr' ? 'यादीत आणखी सामान जोडा (उदा. मीठ, चहा, बिस्किट)...' : ((aiLanguage || currentLang) === 'hi' ? 'बिल में और सामान जोड़ें (उदा. नमक, चाय, बिस्कुट)...' : 'Search and add any item to draft bill...')"
                class="ai-add-input"
              />
              <button v-if="draftSearchQuery" type="button" class="ai-add-clear" @click="draftSearchQuery = ''">✕</button>
            </div>
            <!-- Live Suggestions Dropdown -->
            <div v-if="draftSearchResults.length > 0" class="ai-add-dropdown">
              <div
                v-for="p in draftSearchResults"
                :key="p.id"
                class="ai-add-result-row"
                @click="addManualProductToDraft(p)"
              >
                <img :src="p.image_url" :alt="p.name" class="ai-add-thumb" @error="handleImageFallback($event)" />
                <div class="ai-add-info">
                  <div class="ai-add-name">{{ getLocalizedProductName(p, aiLanguage || currentLang) }}</div>
                  <div class="ai-add-sub">
                    {{ p.variants && p.variants[0] ? p.variants[0].unit_size + ' • ₹' + (p.variants[0].clearance_price || p.variants[0].selling_price) : '' }}
                  </div>
                </div>
                <button type="button" class="ai-add-plus-btn">➕ {{ (aiLanguage || currentLang) === 'mr' ? 'जोडा' : ((aiLanguage || currentLang) === 'hi' ? 'जोड़ें' : 'Add') }}</button>
              </div>
            </div>
          </div>

          <!-- Total Footer -->
          <div class="ai-bill-footer">
            <div class="ai-total-row">
              <span class="ai-total-label">{{ tAi('ai_est_total') }}:</span>
              <span class="ai-total-amount">₹{{ aiEstimatedTotal }}</span>
            </div>

            <!-- Action Buttons: Add to Cart, Save to Monthly Ration, Quick COD, Fast Checkout -->
            <div class="ai-action-buttons">
              <button
                type="button"
                class="ai-cart-btn"
                @click="addAllAiItemsToCart(false)"
              >
                🛒 {{ tAi('ai_add_to_cart') }}
              </button>
              <button
                type="button"
                class="ai-parcha-btn"
                @click="saveAllAiItemsToMonthlyParcha"
                :title="tAi('ai_save_to_parcha')"
              >
                {{ tAi('ai_save_to_parcha') }}
              </button>
              <button
                type="button"
                class="ai-cod-btn"
                @click="quickCodOrderFromDraft"
                :title="tAi('ai_cod_checkout')"
              >
                {{ tAi('ai_cod_checkout') }}
              </button>
              <button
                type="button"
                class="ai-checkout-btn"
                @click="addAllAiItemsToCart(true)"
              >
                {{ tAi('ai_fast_checkout') }}
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- DUKANDAR QUICK PRICE & STOCK EDIT MODAL -->
    <div
      class="modal-overlay"
      v-if="showQuickPriceEditModal"
      @click.self="showQuickPriceEditModal = false"
      role="dialog"
      aria-modal="true"
      aria-labelledby="quick-edit-modal-title"
    >
      <div class="modal-card dukandar-quick-edit-card">
        <div class="quick-edit-header">
          <div class="quick-edit-header-info">
            <h3 id="quick-edit-modal-title" class="quick-edit-title">
              ✏️ {{ currentLang === 'mr' ? 'किंमत व स्टॉक तात्काळ बदला' : (currentLang === 'hi' ? 'दाम व स्टॉक तुरंत बदलें' : 'Rapid Price & Stock Editor') }}
            </h3>
            <div style="display: flex; align-items: center; justify-content: space-between; flex-wrap: wrap; gap: 8px; margin-top: 4px;">
              <p class="quick-edit-subtitle" v-if="quickEditProduct" style="margin: 0;">
                <strong>{{ getLocalizedProductName(quickEditProduct, currentLang) }}</strong>
                <span v-if="quickEditProduct.name_hi && currentLang !== 'hi'" style="color: #64748b; margin-left: 6px;">({{ quickEditProduct.name_hi }})</span>
              </p>
              <!-- 📸 Direct Photo Edit Button -->
              <button
                type="button"
                class="quick-photos-launch-btn"
                @click="openEditPhotosModal(quickEditProduct)"
                :title="currentLang === 'mr' ? '३-कोनी फोटो बदला' : 'Edit 3-Angle Photos'"
                style="background: #e0f2fe; color: #0284c7; border: 1.5px solid #7dd3fc; border-radius: 8px; padding: 5px 12px; font-size: 0.82rem; font-weight: 800; cursor: pointer; display: inline-flex; align-items: center; gap: 5px; transition: all 0.15s ease;"
              >
                📸 {{ currentLang === 'mr' ? 'फोटो बदला (Edit Photos)' : (currentLang === 'hi' ? 'फोटो बदलें (Edit Photos)' : 'Edit Photos (3-Angle)') }}
              </button>
            </div>
          </div>
          <button class="close-btn" @click="showQuickPriceEditModal = false" aria-label="Close modal">✕</button>
        </div>

        <!-- Variant Selector Tabs (If product has multiple sizes like 500g, 1kg, 5kg) -->
        <div class="quick-edit-variant-tabs" v-if="quickEditProduct && quickEditProduct.variants && quickEditProduct.variants.length > 1">
          <span class="quick-variant-label">⚖️ {{ currentLang === 'mr' ? 'आकार / पॅकेट निवडा:' : (currentLang === 'hi' ? 'साइज / पैकेट चुनें:' : 'Select Size:') }}</span>
          <div class="quick-variant-chips">
            <button
              v-for="v in quickEditProduct.variants"
              :key="v.id"
              type="button"
              class="quick-variant-chip"
              :class="{ active: quickEditSelectedVariantId === v.id }"
              @click="selectQuickEditVariant(v)"
            >
              {{ v.unit_size }} (₹{{ v.selling_price }})
            </button>
          </div>
        </div>

        <!-- Quick Edit Form Fields -->
        <form @submit.prevent="saveQuickPriceEdit" class="quick-edit-form">
          <div class="quick-edit-grid">
            <!-- Selling Price Field -->
            <div class="quick-form-group">
              <label class="quick-label">
                💰 {{ currentLang === 'mr' ? 'विक्री दर (Selling Price)' : (currentLang === 'hi' ? 'बिक्री दर (Selling Price)' : 'Selling Price') }} *
              </label>
              <div class="quick-input-prefix-wrap">
                <span class="input-prefix">₹</span>
                <input
                  type="number"
                  step="0.5"
                  min="0"
                  v-model.number="quickEditForm.selling_price"
                  class="quick-input price-input"
                  required
                  autofocus
                />
              </div>
              <span class="quick-field-hint">{{ currentLang === 'mr' ? 'ग्राहकांना दिसणारा अंतिम दर' : (currentLang === 'hi' ? 'ग्राहकों को दिखने वाला अंतिम दाम' : 'Price visible to customers') }}</span>
            </div>

            <!-- MRP Field -->
            <div class="quick-form-group">
              <label class="quick-label">
                🏷️ {{ currentLang === 'mr' ? 'छापील किंमत (MRP)' : (currentLang === 'hi' ? 'प्रिंटेड दाम (MRP)' : 'Printed MRP') }} *
              </label>
              <div class="quick-input-prefix-wrap">
                <span class="input-prefix">₹</span>
                <input
                  type="number"
                  step="0.5"
                  min="0"
                  v-model.number="quickEditForm.mrp"
                  class="quick-input"
                  required
                />
              </div>
              <span class="quick-field-hint">{{ currentLang === 'mr' ? 'पॅकेटवरील छापील दर' : (currentLang === 'hi' ? 'पैकेट पर छपा दाम' : 'Standard packet MRP') }}</span>
            </div>

            <!-- Stock Quantity Field with Stepper -->
            <div class="quick-form-group">
              <label class="quick-label">
                📦 {{ currentLang === 'mr' ? 'शिल्लक नग (Stock Qty)' : (currentLang === 'hi' ? 'उपलब्ध स्टॉक (Stock Qty)' : 'Stock Quantity') }} *
              </label>
              <div class="quick-stepper-wrap">
                <button type="button" class="quick-stepper-btn" @click="quickEditForm.stock_quantity = Math.max(0, (quickEditForm.stock_quantity || 0) - 5)">-5</button>
                <button type="button" class="quick-stepper-btn" @click="quickEditForm.stock_quantity = Math.max(0, (quickEditForm.stock_quantity || 0) - 1)">-1</button>
                <input
                  type="number"
                  min="0"
                  v-model.number="quickEditForm.stock_quantity"
                  class="quick-input stock-input"
                  required
                />
                <button type="button" class="quick-stepper-btn" @click="quickEditForm.stock_quantity = (quickEditForm.stock_quantity || 0) + 1">+1</button>
                <button type="button" class="quick-stepper-btn" @click="quickEditForm.stock_quantity = (quickEditForm.stock_quantity || 0) + 5">+5</button>
                <button type="button" class="quick-stepper-btn" @click="quickEditForm.stock_quantity = (quickEditForm.stock_quantity || 0) + 10">+10</button>
              </div>
              <span class="quick-field-hint">{{ currentLang === 'mr' ? 'दुकानातील प्रत्यक्ष शिल्लक नग' : (currentLang === 'hi' ? 'दुकान में वास्तविक उपलब्ध नग' : 'Physical units in store') }}</span>
            </div>

            <!-- Availability Toggle -->
            <div class="quick-form-group">
              <label class="quick-label">
                🔘 {{ currentLang === 'mr' ? 'स्टॉक उपलब्धता (Status)' : (currentLang === 'hi' ? 'स्टॉक उपलब्धता (Status)' : 'Availability') }}
              </label>
              <div class="quick-availability-toggle">
                <button
                  type="button"
                  class="quick-toggle-pill in-stock"
                  :class="{ selected: quickEditForm.is_available }"
                  @click="quickEditForm.is_available = true"
                >
                  🟢 {{ currentLang === 'mr' ? 'उपलब्ध (In Stock)' : (currentLang === 'hi' ? 'उपलब्ध (In Stock)' : 'In Stock') }}
                </button>
                <button
                  type="button"
                  class="quick-toggle-pill out-of-stock"
                  :class="{ selected: !quickEditForm.is_available }"
                  @click="quickEditForm.is_available = false"
                >
                  🔴 {{ currentLang === 'mr' ? 'संपला (Out of Stock)' : (currentLang === 'hi' ? 'खत्म (Out of Stock)' : 'Out of Stock') }}
                </button>
              </div>
              <span class="quick-field-hint">{{ quickEditForm.is_available ? (currentLang === 'mr' ? 'ग्राहक ऑर्डर करू शकतात' : 'Customers can order') : (currentLang === 'mr' ? 'ऑर्डरसाठी बंद केले आहे' : 'Marked unavailable') }}</span>
            </div>
          </div>

          <!-- Clearance / Special Offer Toggle -->
          <div class="quick-clearance-section">
            <label class="quick-checkbox-label">
              <input type="checkbox" v-model="quickEditForm.is_clearance" />
              <span>🔥 {{ currentLang === 'mr' ? 'विशेष सवलत (Clearance Sale) दर लागू करा' : (currentLang === 'hi' ? 'विशेष छूट (Clearance Sale) लागू करें' : 'Apply Clearance Markdown') }}</span>
            </label>
            <div v-if="quickEditForm.is_clearance" class="quick-clearance-input-wrap" style="margin-top: 8px;">
              <label style="font-size: 0.8rem; font-weight: 700; color: #b91c1c;">{{ currentLang === 'mr' ? 'सवलत दर (Clearance Price ₹):' : 'Clearance Price (₹):' }}</label>
              <input
                type="number"
                step="0.5"
                min="0"
                v-model.number="quickEditForm.clearance_price"
                class="quick-input"
                placeholder="उदा. 40"
                style="border-color: #fca5a5; margin-top: 4px;"
              />
            </div>
          </div>

          <!-- Proportional Weight Auto-Sync Toggle -->
          <div v-if="quickEditProduct?.is_loose || hasWeightVariants(quickEditProduct)" class="quick-proportional-section" style="margin-top: 14px; background: #f0fdf4; border: 1.5px solid #86efac; border-radius: 8px; padding: 10px 14px;">
            <label class="quick-checkbox-label" style="display: flex; align-items: center; gap: 8px; cursor: pointer; font-size: 0.88rem; font-weight: 700; color: #15803d; margin: 0;">
              <input type="checkbox" v-model="quickEditForm.sync_proportional" style="width: 18px; height: 18px; accent-color: #16a34a; cursor: pointer;" />
              <span>⚖️ {{ currentLang === 'mr' ? 'सर्व वजनांचे दर आपोआप बदला (500g, 2kg, 5kg)' : (currentLang === 'hi' ? 'सभी वजन के दाम अपने आप बदलें (500g, 2kg, 5kg)' : 'Auto-scale all weight variants (500g, 2kg, 5kg)') }}</span>
            </label>
            <div style="font-size: 0.78rem; color: #166534; margin-top: 4px; padding-left: 26px; line-height: 1.35;">
              {{ currentLang === 'mr' ? 'प्रति किलो (1kg) दरावरून इतर पॅकेटचे दर आपोआप हिशोब करून बदलले जातील.' : (currentLang === 'hi' ? 'प्रति किलो (1kg) दाम के हिसाब से अन्य पैकेट के दाम अपने आप अपडेट होंगे।' : 'Sibling package prices will automatically recalculate proportionally.') }}
            </div>
          </div>

          <!-- Optional Collapsible Product Details (Name, Brand, Description) -->
          <div class="quick-details-accordion" style="margin-top: 14px; border: 1.5px solid #e2e8f0; border-radius: 8px; overflow: hidden;">
            <button
              type="button"
              class="quick-details-toggle-btn"
              @click="quickEditForm.showDetailsSection = !quickEditForm.showDetailsSection"
              style="width: 100%; display: flex; justify-content: space-between; align-items: center; background: #f8fafc; border: none; padding: 10px 14px; font-size: 0.88rem; font-weight: 700; color: #334155; cursor: pointer;"
            >
              <span style="display: flex; align-items: center; gap: 6px;">
                📝 {{ currentLang === 'mr' ? 'उत्पादनाचे नाव व ब्रँड बदला (Edit Details)' : (currentLang === 'hi' ? 'उत्पाद का नाम व ब्रांड बदलें (Edit Details)' : 'Edit Product Name & Details') }}
              </span>
              <span style="font-size: 0.75rem; color: #64748b;">{{ quickEditForm.showDetailsSection ? '▲ मिटवा' : '▼ उघडा' }}</span>
            </button>

            <div v-if="quickEditForm.showDetailsSection" style="padding: 14px; background: white; border-top: 1px solid #e2e8f0;">
              <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 12px; margin-bottom: 12px;">
                <div>
                  <label style="font-size: 0.78rem; font-weight: 700; color: #475569; display: block; margin-bottom: 4px;">
                    {{ currentLang === 'mr' ? 'इंग्रजी नाव (English Name)' : 'Name (English)' }} *
                  </label>
                  <input type="text" v-model="quickEditForm.name" class="quick-input" placeholder="e.g. Toor Dal" required />
                </div>
                <div>
                  <label style="font-size: 0.78rem; font-weight: 700; color: #475569; display: block; margin-bottom: 4px;">
                    {{ currentLang === 'mr' ? 'मराठी / हिंदी नाव' : 'Vernacular Name' }}
                  </label>
                  <input type="text" v-model="quickEditForm.name_hi" class="quick-input" placeholder="उदा. तूर डाळ" />
                </div>
              </div>

              <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 12px; margin-bottom: 12px;">
                <div>
                  <label style="font-size: 0.78rem; font-weight: 700; color: #475569; display: block; margin-bottom: 4px;">
                    {{ currentLang === 'mr' ? 'ब्रँड (Brand)' : 'Brand' }}
                  </label>
                  <input type="text" v-model="quickEditForm.brand" class="quick-input" placeholder="e.g. Mandi Staples" />
                </div>
                <div>
                  <label style="font-size: 0.78rem; font-weight: 700; color: #475569; display: block; margin-bottom: 4px;">
                    {{ currentLang === 'mr' ? 'प्रकार (Type)' : 'Type' }}
                  </label>
                  <select v-model="quickEditForm.is_loose" class="quick-input" style="height: 38px;">
                    <option :value="true">🌾 {{ currentLang === 'mr' ? 'मोकळे / धान्य (Loose Mandi)' : 'Loose Mandi' }}</option>
                    <option :value="false">📦 {{ currentLang === 'mr' ? 'पॅकबंद ब्रँडेड (Packaged FMCG)' : 'Packaged FMCG' }}</option>
                  </select>
                </div>
              </div>

              <div>
                <label style="font-size: 0.78rem; font-weight: 700; color: #475569; display: block; margin-bottom: 4px;">
                  {{ currentLang === 'mr' ? 'तपशील / माहिती (Description)' : 'Description' }}
                </label>
                <textarea v-model="quickEditForm.description" rows="2" class="quick-input" placeholder="उदा. अस्सल गावरान चवदार डाळ..."></textarea>
              </div>
            </div>
          </div>

          <!-- Action Buttons -->
          <div class="quick-edit-actions">
            <button
              type="button"
              class="quick-cancel-btn"
              @click="showQuickPriceEditModal = false"
            >
              {{ currentLang === 'mr' ? 'रद्द करा' : (currentLang === 'hi' ? 'रद्द करें' : 'Cancel') }}
            </button>

            <button
              type="submit"
              class="quick-save-btn"
              :disabled="quickEditForm.isSaving"
            >
              <span v-if="quickEditForm.isSaving">⏳ {{ currentLang === 'mr' ? 'सेव्ह होत आहे...' : (currentLang === 'hi' ? 'सेव हो रहा है...' : 'Saving...') }}</span>
              <span v-else>💾 {{ currentLang === 'mr' ? 'बदल सेव्ह करा' : (currentLang === 'hi' ? 'बदलाव सेव करें' : 'Save Changes') }}</span>
            </button>
          </div>
        </form>
      </div>
    </div>

    <!-- DUKANDAR AI STORE ASSISTANT MODAL (STORE CONTROL & POS BILLING) -->
    <div
      class="modal-overlay"
      v-if="showDukandarAiModal"
      @click.self="closeDukandarAiModal"
      role="dialog"
      aria-modal="true"
      aria-labelledby="dukandar-ai-modal-title"
    >
      <div class="modal-card komal-ai-modal-card dukandar-ai-modal-card">
        <!-- Header -->
        <div class="komal-ai-header dukandar-ai-header">
          <div class="komal-ai-title-wrap">
            <div class="dukandar-ai-badge">👑 DUKANDAR AI • दुकानदार सहाय्यक</div>
            <h3 id="dukandar-ai-modal-title" class="komal-ai-title" style="color: #064e3b;">
              Komal AI — Store Control
            </h3>
            <p class="komal-ai-subtitle">
              {{ currentLang === 'mr' ? 'बोलून किंवा टाईप करून भाव, स्टॉक किंवा उपलब्धता बदला' : (currentLang === 'hi' ? 'बोलकर या लिखकर दाम, स्टॉक या उपलब्धता बदलें' : 'Voice & text store management: Update prices, stock & availability') }}
            </p>
          </div>
          <button class="close-btn" @click="closeDukandarAiModal">✕</button>
        </div>

        <!-- Mode Switcher: Store Control vs Walk-in POS Bill -->
        <div class="dukandar-ai-mode-tabs">
          <button
            type="button"
            class="dukandar-mode-tab"
            :class="{ active: dukandarAiTab === 'control' }"
            @click="dukandarAiTab = 'control'"
          >
            👑 {{ currentLang === 'mr' ? 'दुकान नियंत्रण (Store Control)' : 'Store Control' }}
          </button>
          <button
            type="button"
            class="dukandar-mode-tab"
            :class="{ active: dukandarAiTab === 'pos' }"
            @click="dukandarAiTab = 'pos'"
          >
            🧾 {{ currentLang === 'mr' ? 'काऊंटर POS बिल (Walk-in Bill)' : 'Walk-in POS Bill' }}
          </button>
        </div>

        <!-- Language Selector Chips -->
        <div class="komal-ai-lang-bar">
          <span class="ai-lang-label">🗣️ {{ currentLang === 'mr' ? 'भाषा:' : (currentLang === 'hi' ? 'भाषा:' : 'Language:') }}</span>
          <button
            type="button"
            class="ai-lang-chip"
            :class="{ active: dukandarAiLang === 'en' }"
            @click="dukandarAiLang = 'en'"
          >
            🇬🇧 English
          </button>
          <button
            type="button"
            class="ai-lang-chip"
            :class="{ active: dukandarAiLang === 'mr' }"
            @click="dukandarAiLang = 'mr'"
          >
            🇮🇳 मराठी
          </button>
          <button
            type="button"
            class="ai-lang-chip"
            :class="{ active: dukandarAiLang === 'hi' }"
            @click="dukandarAiLang = 'hi'"
          >
            🇮🇳 हिंदी
          </button>
        </div>

        <!-- Microphone / Input Section -->
        <div class="komal-ai-input-section">
          <!-- Voice Button -->
          <div class="komal-ai-mic-wrapper">
            <button
              type="button"
              class="komal-ai-mic-btn dukandar-mic-btn"
              :class="{ 'is-recording': isRecording }"
              @click="toggleSpeechRecognition"
              :title="isRecording ? tAi('ai_mic_stop') : tAi('ai_mic_start')"
            >
              <div v-if="isRecording" class="mic-wave-pulse"></div>
              <span class="mic-icon">{{ isRecording ? '⏹️' : '🎙️' }}</span>
            </button>
            <span class="mic-status-hint">
              {{ isRecording ? (currentLang === 'mr' ? 'ऐकत आहे... बोला' : 'Listening... speak') : (currentLang === 'mr' ? 'माइक सुरू करा' : 'Tap mic to speak') }}
            </span>
          </div>

          <!-- Textarea for spoken / typed command -->
          <div class="ai-input-group">
            <textarea
              v-model="dukandarAiText"
              rows="3"
              class="komal-ai-textarea dukandar-ai-textarea"
              :placeholder="dukandarAiTab === 'control'
                ? (dukandarAiLang === 'mr'
                  ? 'उदा. तूर डाळ 195 रुपये करा, साखर स्टॉक 50 करा, चक्की आटा आउट ऑफ स्टॉक करा...'
                  : (dukandarAiLang === 'hi'
                    ? 'उदा. तूर दाल का भाव 195 करो, चीनी स्टॉक 50 करो, आटा आउट ऑफ स्टॉक करो...'
                    : 'e.g. change toor daal price to Rs195/kg, set sugar stock to 50, mark chakki atta out of stock...'))
                : (dukandarAiLang === 'mr'
                  ? 'उदा. २ किलो तूर डाळ, ५ किलो चक्की आटा, १ किलो साखर...'
                  : (dukandarAiLang === 'hi'
                    ? 'उदा. २ किलो तूर दाल, ५ किलो आटा, १ किलो चीनी...'
                    : 'e.g. 2kg toor dal, 5kg chakki atta, 1kg sugar...'))"
              @keydown.enter.prevent="executeDukandarAiCommand()"
            ></textarea>
            <div class="ai-textarea-footer">
              <span class="ai-hint-caption">
                {{ dukandarAiTab === 'control'
                  ? (dukandarAiLang === 'mr' ? '💡 भाव, स्टॉक, किंवा इन/आउट ऑफ स्टॉक आज्ञा सांगा.' : (dukandarAiLang === 'hi' ? '💡 भाव, स्टॉक, या इन/आउट ऑफ स्टॉक कमांड बोलें।' : '💡 Speak or type price, stock, or availability commands.'))
                  : (dukandarAiLang === 'mr' ? '💡 ग्राहकाची किराणा यादी थेट काऊंटर POS मध्ये जोडली जाईल.' : '💡 Customer grocery list will compile directly into In-Store POS.') }}
              </span>
              <button
                v-if="dukandarAiText"
                type="button"
                class="ai-clear-btn"
                @click="dukandarAiText = ''; dukandarAiResult = null"
              >
                {{ tAi('ai_clear') }}
              </button>
            </div>
          </div>

          <!-- Quick Prompts / Examples for Store Control -->
          <div class="ai-quick-examples" v-if="dukandarAiTab === 'control' && !dukandarAiResult">
            <span class="quick-examples-title">👑 {{ dukandarAiLang === 'mr' ? 'नमुना आज्ञा (टॅप करा):' : (dukandarAiLang === 'hi' ? 'कमांड के उदाहरण (टैप करें):' : 'Sample Commands (Tap to try):') }}</span>
            <div class="quick-chips">
              <button
                type="button"
                class="quick-chip"
                @click="applyDukandarExample('change toor daal price to Rs195/kg')"
              >
                💰 toor daal price Rs195/kg
              </button>
              <button
                type="button"
                class="quick-chip"
                @click="applyDukandarExample('तूर डाळ 190 रुपये करा')"
              >
                🏷️ तूर डाळ 190 रु करा
              </button>
              <button
                type="button"
                class="quick-chip"
                @click="applyDukandarExample('set sugar stock to 50')"
              >
                📦 sugar stock 50
              </button>
              <button
                type="button"
                class="quick-chip"
                @click="applyDukandarExample('साखर आउट ऑफ स्टॉक करा')"
              >
                🚫 साखर आउट ऑफ स्टॉक
              </button>
              <button
                type="button"
                class="quick-chip"
                @click="applyDukandarExample('chana dal in stock')"
              >
                🟢 chana dal in stock
              </button>
              <button
                type="button"
                class="quick-chip"
                @click="applyDukandarExample('what is the price of toor dal')"
              >
                🔍 toor dal price & stock?
              </button>
            </div>
          </div>

          <!-- Quick Prompts for Walk-in POS Bill -->
          <div class="ai-quick-examples" v-if="dukandarAiTab === 'pos' && !dukandarAiResult">
            <span class="quick-examples-title">⚡ {{ dukandarAiLang === 'mr' ? 'काऊंटर ग्राहक सामान (टॅप करा):' : 'Walk-in Items:' }}</span>
            <div class="quick-chips">
              <button
                type="button"
                class="quick-chip"
                @click="applyDukandarExample('2 kg toor dal, 5 kg chakki atta, 1 kg sugar')"
              >
                🌾 2kg Toor Dal, 5kg Atta, 1kg Sugar
              </button>
              <button
                type="button"
                class="quick-chip"
                @click="applyDukandarExample('१ किलो शेंगदाणे, अर्धा किलो बेसन, १ लिटर तेल')"
              >
                🍳 शेंगदाणे, बेसन, तेल
              </button>
            </div>
          </div>

          <!-- Submit Button -->
          <button
            type="button"
            class="komal-ai-generate-btn dukandar-submit-btn"
            :disabled="dukandarAiLoading || !dukandarAiText.trim()"
            @click="executeDukandarAiCommand()"
          >
            <span v-if="dukandarAiLoading" class="ai-spinner">⏳</span>
            <span v-else>⚡</span>
            {{ dukandarAiLoading ? 'प्रक्रिया सुरू आहे...' : (dukandarAiTab === 'control' ? '⚡ आज्ञा लागू करा (Run Store Command)' : '⚡ काऊंटर बिल बनवा (Generate POS Bill)') }}
          </button>
        </div>

        <!-- DUKANDAR OUTPUT SECTION -->
        <div v-if="dukandarAiResult" class="dukandar-ai-result-section">
          <!-- UPDATE SUCCESS RESULT -->
          <div v-if="dukandarAiResult.success && dukandarAiResult.type === 'UPDATE'" class="dukandar-success-box">
            <div class="dukandar-success-header">
              <span class="dukandar-success-badge">✅ आज्ञा यशस्वी (Action Executed)</span>
              <button
                type="button"
                class="ai-speak-btn"
                @click="speakAiSummary(dukandarAiResult.summary_text)"
                title="Play voice"
              >
                🔊
              </button>
            </div>
            
            <p class="dukandar-success-msg">{{ dukandarAiResult.summary_text }}</p>

            <!-- Product Visual Details -->
            <div class="dukandar-result-product-card" v-if="dukandarAiResult.product && dukandarAiResult.variant">
              <img
                :src="dukandarAiResult.product.image_url || '/products/chakki-atta.jpg'"
                :alt="dukandarAiResult.product.name"
                class="dukandar-result-thumb"
                @error="handleImageFallback($event)"
              />
              <div class="dukandar-result-info">
                <div class="dukandar-result-name">
                  {{ getLocalizedProductName(dukandarAiResult.product, dukandarAiLang) }}
                </div>
                <div class="dukandar-result-variant-tag">
                  📦 {{ dukandarAiResult.variant.unit_size }}
                </div>
              </div>
            </div>

            <!-- Diff Changes Grid -->
            <div class="dukandar-diff-grid">
              <div class="dukandar-diff-item" v-for="(chg, ci) in dukandarAiResult.changesSummary" :key="ci">
                <span class="diff-chip">{{ chg }}</span>
              </div>
            </div>

            <!-- Action buttons: Undo & Done -->
            <div class="dukandar-result-actions">
              <button
                type="button"
                class="dukandar-undo-btn"
                v-if="dukandarPreviousState"
                @click="undoDukandarAiAction"
              >
                ↩️ बदल पूर्ववत करा (Undo Revert)
              </button>
              <button
                type="button"
                class="dukandar-done-btn"
                @click="closeDukandarAiModal"
              >
                👍 पूर्ण झाले (Done)
              </button>
              <button
                type="button"
                class="dukandar-another-btn"
                @click="dukandarAiResult = null; dukandarAiText = ''"
              >
                🎙️ आणखी बदल करा (Next Command)
              </button>
            </div>
          </div>

          <!-- QUERY RESULT -->
          <div v-else-if="dukandarAiResult.success && dukandarAiResult.type === 'QUERY'" class="dukandar-query-box">
            <div class="dukandar-success-header">
              <span class="dukandar-query-badge">🔍 थेट माहिती (Live Product Info)</span>
              <button
                type="button"
                class="ai-speak-btn"
                @click="speakAiSummary(dukandarAiResult.summary_text)"
                title="Play voice"
              >
                🔊
              </button>
            </div>
            
            <p class="dukandar-success-msg">{{ dukandarAiResult.summary_text }}</p>

            <div class="dukandar-result-product-card" v-if="dukandarAiResult.product && dukandarAiResult.variant">
              <img
                :src="dukandarAiResult.product.image_url || '/products/chakki-atta.jpg'"
                :alt="dukandarAiResult.product.name"
                class="dukandar-result-thumb"
                @error="handleImageFallback($event)"
              />
              <div class="dukandar-result-info">
                <div class="dukandar-result-name">
                  {{ getLocalizedProductName(dukandarAiResult.product, dukandarAiLang) }}
                </div>
                <div class="dukandar-result-variant-tag">
                  📦 {{ dukandarAiResult.variant.unit_size }} • दर: ₹{{ dukandarAiResult.variant.selling_price }} • शिल्लक: {{ dukandarAiResult.variant.stock_quantity }}
                </div>
              </div>
              <button
                type="button"
                class="quick-chip"
                style="margin-left: auto;"
                @click="openQuickPriceEdit(dukandarAiResult.product, dukandarAiResult.variant); closeDukandarAiModal()"
              >
                ✏️ Edit
              </button>
            </div>
          </div>

          <!-- NOT FOUND OR UNCLEAR RESULT -->
          <div v-else class="dukandar-error-box">
            <div class="dukandar-error-title">⚠️ {{ dukandarAiResult.message }}</div>
            <div v-if="dukandarAiResult.candidates && dukandarAiResult.candidates.length > 0" class="dukandar-candidates-wrap">
              <span class="candidates-hint">तुम्हाला यापैकी काही बदलायचे आहे का? (Did you mean):</span>
              <div class="candidates-chips">
                <button
                  type="button"
                  class="candidate-chip"
                  v-for="cand in dukandarAiResult.candidates"
                  :key="cand.id"
                  @click="openQuickPriceEdit(cand); closeDukandarAiModal()"
                >
                  ✏️ {{ getLocalizedProductName(cand, dukandarAiLang) }}
                </button>
              </div>
            </div>
            <div class="dukandar-result-actions" style="margin-top: 12px;">
              <button
                type="button"
                class="dukandar-another-btn"
                @click="dukandarAiResult = null; dukandarAiText = ''"
              >
                🔄 पुन्हा प्रयत्न करा (Try Again)
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted, nextTick } from 'vue';
import { translations, marathiProductNames, getLocalizedProductName, getLocalizedCategoryName } from './i18n.js';

const API_BASE = '/api';

// PWA Installation State
const deferredInstallPrompt = ref(null);
const showInstallBanner = ref(false);
const isAppInstalled = ref(false);
const showIOSModal = ref(false);
const showQRModal = ref(false);
const showInstallGuideModal = ref(false);
const currentOrigin = ref(typeof window !== 'undefined' ? window.location.origin : 'https://komalmart.onrender.com');

function copyLiveLink() {
  if (navigator.clipboard) {
    navigator.clipboard.writeText(currentOrigin.value);
    showToast(currentLang.value === 'en' ? '📋 Site link copied to clipboard!' : (currentLang.value === 'mr' ? '📋 साइटची लिंक कॉपी केली!' : '📋 साइट लिंक कॉपी हो गई!'));
  }
}

const isIOS = () => {
  return /iPad|iPhone|iPod/.test(navigator.userAgent) && !window.MSStream;
};

const canInstallPWA = computed(() => {
  return !!deferredInstallPrompt.value || (!isAppInstalled.value && isIOS());
});

const triggerInstall = async () => {
  // 1. If browser has native trusted PWA prompt ready, use it! (100% clean, ZERO Play Protect warnings)
  if (deferredInstallPrompt.value) {
    deferredInstallPrompt.value.prompt();
    const { outcome } = await deferredInstallPrompt.value.userChoice;
    if (outcome === 'accepted') {
      showInstallBanner.value = false;
      isAppInstalled.value = true;
      showToast(currentLang.value === 'en' ? '🎉 Komal Mart added to your Home Screen!' : '🎉 कोमल मार्ट ॲप होम स्क्रीनवर सेव्ह झाले!');
    }
    deferredInstallPrompt.value = null;
    return;
  }

  // 2. If iOS Safari, show the iOS Add to Home Screen instructions
  if (isIOS()) {
    showIOSModal.value = true;
    return;
  }

  // 3. Otherwise, open the clear Install Guide modal (offers 1-tap browser guide & optional APK download)
  showInstallGuideModal.value = true;
};

const dismissInstallBanner = () => {
  showInstallBanner.value = false;
  sessionStorage.setItem('pwa_banner_dismissed', 'true');
};

// Mobile Navigation & Floating Cart State
const currentBottomTab = ref('home');
const showMobileCategorySheet = ref(false);

// --- RESTOCK ALERTS & HOT BACKUPS STATE ---
const showNotifyModal = ref(false);
const notifyProduct = ref(null);
const notifyVariant = ref(null);
const notifyForm = ref({ customer_name: '', customer_phone: '' });
const notifySubmitting = ref(false);
const notifyMessage = ref('');
const notifySuccess = ref(false);

const restockAlertsList = ref([]);
const pendingRestockCount = ref(0);

function handleBottomNav(tab) {
  currentBottomTab.value = tab;
  if (tab === 'home') {
    selectedCategorySlug.value = '';
    searchQuery.value = '';
    showMobileCategorySheet.value = false;
    window.scrollTo({ top: 0, behavior: 'smooth' });
  } else if (tab === 'categories') {
    showMobileCategorySheet.value = !showMobileCategorySheet.value;
  } else if (tab === 'khata') {
    showMobileCategorySheet.value = false;
    if (currentUser.value) {
      openAccountModal();
    } else {
      openAuthModal('login');
    }
  } else if (tab === 'cart') {
    showMobileCategorySheet.value = false;
    isCartOpen.value = true;
  }
}

function selectCategoryFromSheet(slug) {
  selectCategory(slug);
  showMobileCategorySheet.value = false;
  currentBottomTab.value = slug === '' ? 'home' : 'categories';
  window.scrollTo({ top: 0, behavior: 'smooth' });
}

// Language State (Marathi default for Maharashtra / Mumbai, user-customizable)
const currentLang = ref(localStorage.getItem('kirana_preferred_lang') || 'mr');
const showLangModal = ref(!localStorage.getItem('kirana_lang_selected'));
const showLangDropdown = ref(false);

function selectLanguage(lang) {
  currentLang.value = lang;
  localStorage.setItem('kirana_preferred_lang', lang);
  localStorage.setItem('kirana_lang_selected', 'true');
  showLangModal.value = false;
  showToast(`🌐 भाषा: ${translations[lang]['lang_' + lang]}`);
}

function toggleLangDropdown() {
  showLangDropdown.value = !showLangDropdown.value;
}

function t(key) {
  return translations[currentLang.value]?.[key] || translations['en']?.[key] || key;
}

function tAi(key) {
  const l = aiLanguage.value || currentLang.value || 'mr';
  return translations[l]?.[key] || translations['en']?.[key] || key;
}

// Auth State
const savedUserStr = localStorage.getItem('kirana_user');
let initialUser = null;
try {
  initialUser = savedUserStr ? JSON.parse(savedUserStr) : null;
} catch (e) {
  initialUser = null;
}
const currentUser = ref(initialUser);
const authToken = ref(localStorage.getItem('kirana_token') || '');
const showAuthModal = ref(false);
const authMode = ref('login'); // 'login' | 'register' | 'admin'
const authError = ref('');
const authSubmitting = ref(false);

const authForm = ref({ identifier: '', password: '' });
const registerForm = ref({ name: '', username: '', email: '', phone: '', password: '', address: '', otp: '' });
const regOtpSent = ref(false);
const regOtpSubmitting = ref(false);
const regOtpCountdown = ref(0);
let regOtpTimer = null;

const resetStep = ref(1); // 1 = enter phone/email, 2 = enter OTP & new password
const resetIdentifier = ref('');
const resetOtp = ref('');
const resetNewPassword = ref('');
const resetConfirmPassword = ref('');
const resetToken = ref('');
const resetMaskedTarget = ref('');
const resetMaskedEmail = ref('');
const resetNoEmailPhone = ref('');
const resetChannel = ref('sms'); // 'whatsapp' | 'email'
const resetWaLink = ref('');
const resetWaCode = ref('');
const resetHasEmail = ref(false);
const resetHasPhone = ref(false);
const smsBalanceInfo = ref({ configured: true, wallet: '145.00', sms_count: 580 });
const admin2faState = ref({
  active: false,
  temp_token: '',
  masked_email: '',
  admin_email: '',
  email_dispatched: true,
  otp_preview: '',
  otp: ''
});

// Customer Account Modal State
const showAccountModal = ref(false);
const customerActiveTab = ref('orders'); // 'orders' | 'profile'
const customerOrders = ref([]);
const customerOrdersLoading = ref(false);
const profileForm = ref({ name: '', email: '', phone: '', address: '' });

const lastDeliveredCustomerOrder = computed(() => {
  if (!currentUser.value || !customerOrders.value || customerOrders.value.length === 0) return null;
  if (isAdminLoggedIn.value && !adminPreviewAsCustomer.value) return null;
  return customerOrders.value.find(o => o.status === 'Delivered') || customerOrders.value[0];
});

// Customer Support & Feedback State
const supportTicketType = ref('complaint'); // 'complaint' | 'feedback'
const supportCategory = ref('');
const supportOrderNumber = ref('');
const supportMessage = ref('');
const isSupportRecording = ref(false);
const supportSubmitting = ref(false);
const supportSuccessTicket = ref(null);
const supportTicketsList = ref([]);
const supportTicketsLoading = ref(false);

const openSupportTicketsCount = computed(() => {
  return (supportTicketsList.value || []).filter(t => t.status === 'Open').length;
});

// Admin Support Tickets State
const adminSupportTickets = ref([]);
const adminSupportLoading = ref(false);
const adminSupportFilter = ref('all'); // 'all' | 'complaint' | 'feedback' | 'open'
const adminOpenComplaintsCount = ref(0);

const filteredAdminSupportTickets = computed(() => {
  if (adminSupportFilter.value === 'complaint') {
    return adminSupportTickets.value.filter(t => t.ticket_type === 'complaint');
  } else if (adminSupportFilter.value === 'feedback') {
    return adminSupportTickets.value.filter(t => t.ticket_type === 'feedback');
  } else if (adminSupportFilter.value === 'open') {
    return adminSupportTickets.value.filter(t => t.status === 'Open');
  }
  return adminSupportTickets.value;
});

// Admin State & Batch Printing
const adminActiveTab = ref('storefront');
const adminPreviewAsCustomer = ref(false);
const showQuickPriceEditModal = ref(false);
const quickEditProduct = ref(null);
const quickEditSelectedVariantId = ref(null);
const quickEditForm = reactive({
  selling_price: 0,
  mrp: 0,
  stock_quantity: 0,
  is_available: true,
  is_clearance: false,
  clearance_price: null,
  sync_proportional: true,
  name: '',
  name_hi: '',
  brand: '',
  is_loose: false,
  description: '',
  showDetailsSection: false,
  isSaving: false
});
const adminSearch = ref('');
const adminCategoryFilter = ref('');
// LocalStorage Order Vault & Instant SWR Cache
const cachedAdminOrdersStr = localStorage.getItem('komal_cached_admin_orders');
let initialAdminOrders = [];
try {
  initialAdminOrders = cachedAdminOrdersStr ? JSON.parse(cachedAdminOrdersStr) : [];
} catch (e) {
  initialAdminOrders = [];
}
const adminOrders = ref(initialAdminOrders);
const isAdminOrdersLoading = ref(initialAdminOrders.length === 0);
const isAdminOrdersSyncing = ref(false);
const showAddProductModal = ref(false);
const selectedAdminOrderIds = ref([]);
const selectedAdminProductIds = ref([]);
const showBatchPrintModal = ref(false);
const batchPrintLayout = ref('auto'); // 'auto' | 'two' | 'four'

// Admin Batch Ingestion & Quick-Add State
const showBatchIngestModal = ref(false);
const batchIngestStatus = ref('idle'); // 'idle' | 'loading' | 'preview' | 'complete' | 'error'
const batchIngestItems = ref([]);
const batchIngestStats = ref({ processed: 0, created: 0, updated: 0 });
const batchIngestError = ref('');

const addProductMode = ref('quick'); // 'quick' | 'full'
const showMobileExpandedStats = ref(false);
const showAdminMoreSheet = ref(false);

const quickCommodities = [
  { name: 'Toor Dal / Arhar Dal (Gavran Loose)', name_hi: 'तूर डाळ (गावरान मोकळी)', catSlug: 'dals-pulses', is_loose: true, unit: '1kg', rate: 190, front: '/products/toor-dal.jpg' },
  { name: 'Chana Dal (Bengal Gram Loose)', name_hi: 'चना डाळ (हरभरा मोकळी)', catSlug: 'dals-pulses', is_loose: true, unit: '1kg', rate: 95, front: '/products/chana-dal.jpg' },
  { name: 'Moong Dal Dhuli (Yellow Split Loose)', name_hi: 'पिवळी मूग डाळ (मोकळी)', catSlug: 'dals-pulses', is_loose: true, unit: '1kg', rate: 120, front: '/products/chana-dal.jpg' },
  { name: 'Chakki Fresh Whole Wheat Atta', name_hi: 'चक्की ताजे गव्हाचे पीठ', catSlug: 'atta-flours', is_loose: true, unit: '1kg', rate: 38, front: '/products/chakki-atta.jpg' },
  { name: 'Sharbati Whole Wheat Grain', name_hi: 'शरबती अख्खा गहू दाना', catSlug: 'atta-flours', is_loose: true, unit: '1kg', rate: 35, front: '/products/chakki-atta.jpg' },
  { name: 'Wada Kolam Rice (Mandi Fresh)', name_hi: 'वाडा कोलम तांदूळ (मोकळा)', catSlug: 'rice-grains', is_loose: true, unit: '1kg', rate: 65, front: '/products/basmati-rice.jpg' },
  { name: 'Madhur Pure Sugar', name_hi: 'मधुर शुद्ध पांढरी साखर', catSlug: 'rice-grains', is_loose: true, unit: '1kg', rate: 42, front: '/products/basmati-rice.jpg' },
  { name: 'Singdana / Peanuts (Raw Groundnuts)', name_hi: 'कच्चे शेंगदाणे (गावरान)', catSlug: 'dals-pulses', is_loose: true, unit: '1kg', rate: 140, front: '/products/chana-dal.jpg' },
  { name: 'Suji / Rava (Fine Semolina)', name_hi: 'बारीक सुजी रवा', catSlug: 'atta-flours', is_loose: true, unit: '1kg', rate: 45, front: '/products/chakki-atta.jpg' },
  { name: 'Tata Salt Vacuum Evaporated', name_hi: 'टाटा मीठ (आयोडीनयुक्त)', catSlug: 'spices-salt', is_loose: false, unit: '1kg', rate: 28, front: '/products/tata-salt.jpg' },
  { name: 'Fortune Refined Sunflower Oil', name_hi: 'फॉर्च्युन सूर्यफूल तेल', catSlug: 'oils-ghee', is_loose: false, unit: '1L', rate: 145, front: '/products/fortune-mustard-oil.jpg' },
  { name: 'Surf Excel Quick Wash Powder', name_hi: 'सर्फ एक्सेल डिटर्जंट पावडर', catSlug: 'cleaning-household', is_loose: false, unit: '1kg', rate: 140, front: '/products/surf-excel.jpg' }
];

function selectQuickCommodity(item) {
  newProductForm.value.name = item.name;
  newProductForm.value.name_hi = item.name_hi;
  newProductForm.value.is_loose = item.is_loose;
  newProductForm.value.unit_size = item.unit;
  newProductForm.value.selling_price = item.rate;
  newProductForm.value.mrp = item.rate;
  if (item.front) newProductForm.value.image_front = item.front;

  const foundCat = categories.value.find(c => c.slug === item.catSlug || (c.name && c.name.toLowerCase().includes(item.catSlug)));
  if (foundCat) {
    newProductForm.value.category_id = foundCat.id;
    newProductForm.value.is_new_category = false;
  }
}

function syncQuickName() {
  if (!newProductForm.value.name) {
    newProductForm.value.name = newProductForm.value.name_hi;
  }
}

function syncQuickPrice() {
  newProductForm.value.mrp = newProductForm.value.selling_price;
}

async function runBatchPhotoIngest(dryRun = false) {
  batchIngestStatus.value = 'loading';
  batchIngestError.value = '';
  try {
    const res = await fetch(`${API_BASE}/admin/batch-ingest-photos`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${authToken.value}`
      },
      body: JSON.stringify({ dry_run: dryRun })
    });
    const data = await res.json();
    if (res.ok && data.success) {
      batchIngestItems.value = data.items || [];
      batchIngestStats.value = {
        processed: data.processed || 0,
        created: data.created || 0,
        updated: data.updated || 0
      };
      batchIngestStatus.value = dryRun ? 'preview' : 'complete';
      if (!dryRun) {
        showToast(currentLang.value === 'mr' ? `✅ ${data.created} सामान नवीन जोडले, ${data.updated} अपडेट झाले!` : `✅ ${data.created} new items created, ${data.updated} updated!`);
        await fetchProducts();
      }
    } else {
      batchIngestStatus.value = 'error';
      batchIngestError.value = data.error || 'Failed to ingest batch photos';
    }
  } catch (err) {
    batchIngestStatus.value = 'error';
    batchIngestError.value = err.message;
  }
}

// Admin Clearance Master Visibility Switch (Default false: preserves kirana store trust)
const adminAllowClearancePublic = ref(localStorage.getItem('komal_allow_clearance_public') === 'true');

function togglePublicClearance(val) {
  adminAllowClearancePublic.value = Boolean(val);
  localStorage.setItem('komal_allow_clearance_public', val ? 'true' : 'false');
  showToast(val ? (currentLang.value === 'en' ? 'Public clearance deals enabled' : 'क्लिअरन्स सेल ग्राहकांसाठी सुरू केले') : (currentLang.value === 'en' ? 'Clearance deals hidden from customers' : 'क्लिअरन्स सेल ग्राहकांपासून लपवले'));
}

// Admin Khata Book State
const adminKhataList = ref([]);
const adminKhataSummary = ref({ total_market_udhaar: 0, total_khata_customers: 0, total_recovered_month: 0 });
const khataSearch = ref('');
const khataLoading = ref(false);

const showKhataPayModal = ref(false);
const activeKhataCustomer = ref(null);
const khataPayForm = ref({ amount: '', payment_method: 'Cash', note: '' });
const isSubmittingKhataPay = ref(false);

const showKhataStatementModal = ref(false);
const activeKhataStatement = ref(null);
const khataStatementLoading = ref(false);

// Customer Khata State
const customerKhataData = ref(null);
const customerKhataLoading = ref(false);

// Admin Daily Z-Report State
const zReportDate = ref(new Date().toISOString().split('T')[0]);
const zReport = ref({
  date: '',
  formatted_date: '',
  total_orders_count: 0,
  gross_sales_mrp: 0,
  net_sales: 0,
  total_savings_given: 0,
  avg_basket_value: 0,
  cash_paid_amount: 0,
  cash_unpaid_amount: 0,
  upi_paid_amount: 0,
  upi_unpaid_amount: 0,
  store_credit_redeemed: 0,
  store_credit_earned_paid: 0,
  khata_new_amount: 0,
  khata_new_count: 0,
  khata_cash_recovered: 0,
  khata_upi_recovered: 0,
  total_khata_recovered: 0,
  total_cash_in_drawer: 0,
  total_upi_received: 0,
  total_liquid_collected: 0,
  total_market_udhaar: 0,
  orders: [],
  repayments: []
});


// Admin POS & Customer Directory State
const adminCustomers = ref([]);
const customerSearch = ref('');
const activeAuditedCustomer = ref(null);
const isPosSubmitting = ref(false);
const selectedPosCustomer = ref(null);
const posUseStoreCredit = ref(false);
const posCustomerDetailsOpen = ref(false);

const counterOrder = ref({
  customer_name: '',
  customer_phone: '',
  customer_address: 'दुकान काउंटर (In-Store Pickup)',
  order_type: 'counter',
  payment_method: 'Cash on Counter',
  payment_status: 'Paid',
  status: 'Delivered',
  user_id: null,
  items: []
});

const posSelectedProduct = ref(null);
const posSelectedVariant = ref(null);
const posCustomWeight = ref(1.0);
const posQuantity = ref(1);
const posCustomRate = ref(null);

const newProductForm = ref({
  category_id: 1,
  is_new_category: false,
  new_category_name: '',
  new_category_name_hi: '',
  name: '',
  name_hi: '',
  brand: 'Local / Mandi',
  is_loose: true,
  description: '',
  unit_size: '1kg',
  mrp: 100,
  selling_price: 90,
  image_front: '/products/chakki-atta.jpg',
  image_back: '',
  image_pack: ''
});

// Multi-Angle Image Presets
const kiranaImagePresets = [
  { label: '🌾 चक्की आटा', front: '/products/chakki-atta.jpg', back: '', pack: '/products/chakki-atta.jpg' },
  { label: '🟡 तुवर डाळ', front: '/products/tata-toor-dal.jpg', back: '', pack: '/products/toor-dal.jpg' },
  { label: '🟤 चना डाळ', front: '/products/chana-dal.jpg', back: '', pack: '/products/chana-dal.jpg' },
  { label: '🍚 बासमती तांदूळ', front: '/products/basmati-rice.jpg', back: '', pack: '/products/basmati-rice.jpg' },
  { label: '🛢️ मोहरी तेल', front: '/products/fortune-mustard-oil.jpg', back: '', pack: '/products/mustard-oil.jpg' },
  { label: '🧈 अमूल तूप', front: '/products/amul-ghee.jpg', back: '', pack: '/products/desi-ghee.jpg' },
  { label: '🧂 टाटा मीठ', front: '/products/tata-salt.jpg', back: '', pack: '/products/tata-salt.jpg' },
  { label: '☕ टाटा चहा', front: '/products/tata-tea-gold.jpg', back: '', pack: '/products/ctc-tea.jpg' },
  { label: '🟡 हळद पावडर', front: '/products/haldi-powder.jpg', back: '', pack: '/products/haldi-powder.jpg' },
  { label: '🌶️ लाल मिरची', front: '/products/mirch-powder.jpg', back: '', pack: '/products/mirch-powder.jpg' },
  { label: '🧼 सर्फ एक्सेल', front: '/products/surf-excel.jpg', back: '', pack: '/products/rin-bar.jpg' },
  { label: '🪥 कोलगेट', front: '/products/colgate-strong.jpg', back: '', pack: '/products/colgate-maxfresh.jpg' }
];

function applyImagePresetToNew(preset) {
  newProductForm.value.image_front = preset.front;
  newProductForm.value.image_back = preset.back;
  newProductForm.value.image_pack = preset.pack;
}

// Edit Product Photos Modal (Admin)
const showEditPhotosModal = ref(false);
const editingProductPhotos = ref(null);
const editPhotosForm = ref({
  product_id: null,
  product_name: '',
  image_front: '',
  image_back: '',
  image_pack: ''
});

function openEditPhotosModal(prod) {
  editingProductPhotos.value = prod;
  const imgs = prod.images || (prod.image_url ? [prod.image_url] : []);
  editPhotosForm.value = {
    product_id: prod.id,
    product_name: prod.name,
    image_front: imgs[0] || prod.image_url || '',
    image_back: imgs[1] || '',
    image_pack: imgs[2] || ''
  };
  showEditPhotosModal.value = true;
}

function applyImagePresetToEdit(preset) {
  editPhotosForm.value.image_front = preset.front;
  editPhotosForm.value.image_back = preset.back;
  editPhotosForm.value.image_pack = preset.pack;
}

async function saveProductPhotos() {
  try {
    const images = [];
    if (editPhotosForm.value.image_front && editPhotosForm.value.image_front.trim()) {
      images.push(editPhotosForm.value.image_front.trim());
    }
    if (editPhotosForm.value.image_back && editPhotosForm.value.image_back.trim()) {
      images.push(editPhotosForm.value.image_back.trim());
    }
    if (editPhotosForm.value.image_pack && editPhotosForm.value.image_pack.trim()) {
      images.push(editPhotosForm.value.image_pack.trim());
    }
    if (images.length === 0) {
      images.push('/products/chakki-atta.jpg');
    }

    const res = await fetch(`${API_BASE}/products/${editPhotosForm.value.product_id}`, {
      method: 'PUT',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${authToken.value}`
      },
      body: JSON.stringify({ images })
    });

    if (res.ok) {
      showToast(`✅ '${editPhotosForm.value.product_name}' चे 3-अँगल फोटो सेव्ह झाले!`);
      showEditPhotosModal.value = false;
      fetchProducts();
    } else {
      showToast('❌ फोटो सेव्ह करता आले नाहीत.');
    }
  } catch (err) {
    console.error('Error saving photos:', err);
    showToast('❌ नेटवर्क त्रुटी.');
  }
}

// Products & Filters State
const categories = ref([]);
const products = ref([]);
const loading = ref(true);
const toastMessage = ref('');
const selectedCategorySlug = ref('');
const searchQuery = ref('');
const looseFilter = ref('all');
const sortBy = ref('');
const selectedVariants = ref({});

const uploadingSlot = ref(null);

async function handleFileUpload(event, targetType, slot) {
  const file = event.target.files && event.target.files[0];
  if (!file) return;

  const key = `${targetType}_${slot}`;
  uploadingSlot.value = key;

  // Immediate local preview
  const blobUrl = URL.createObjectURL(file);
  if (targetType === 'new') {
    if (slot === 'front') newProductForm.value.image_front = blobUrl;
    if (slot === 'back') newProductForm.value.image_back = blobUrl;
    if (slot === 'pack') newProductForm.value.image_pack = blobUrl;
  } else if (targetType === 'edit') {
    if (slot === 'front') editPhotosForm.value.image_front = blobUrl;
    if (slot === 'back') editPhotosForm.value.image_back = blobUrl;
    if (slot === 'pack') editPhotosForm.value.image_pack = blobUrl;
  }

  try {
    const formData = new FormData();
    formData.append('file', file);

    const res = await fetch(`${API_BASE}/upload`, {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${authToken.value}`
      },
      body: formData
    });

    const data = await res.json();
    if (res.ok && data.url) {
      if (targetType === 'new') {
        if (slot === 'front') newProductForm.value.image_front = data.url;
        if (slot === 'back') newProductForm.value.image_back = data.url;
        if (slot === 'pack') newProductForm.value.image_pack = data.url;
      } else if (targetType === 'edit') {
        if (slot === 'front') editPhotosForm.value.image_front = data.url;
        if (slot === 'back') editPhotosForm.value.image_back = data.url;
        if (slot === 'pack') editPhotosForm.value.image_pack = data.url;
      }
      showToast('✅ फोटो यशस्वीरीत्या अपलोड झाला!');
    } else {
      showToast(`❌ ${data.error || 'फोटो अपलोड अयशस्वी.'}`);
    }
  } catch (err) {
    console.error('Upload error:', err);
    showToast('❌ फोटो अपलोड करताना एरर आली.');
  } finally {
    uploadingSlot.value = null;
    event.target.value = '';
  }
}

function clearSlot(targetType, slot) {
  if (targetType === 'new') {
    if (slot === 'front') newProductForm.value.image_front = '';
    if (slot === 'back') newProductForm.value.image_back = '';
    if (slot === 'pack') newProductForm.value.image_pack = '';
  } else if (targetType === 'edit') {
    if (slot === 'front') editPhotosForm.value.image_front = '';
    if (slot === 'back') editPhotosForm.value.image_back = '';
    if (slot === 'pack') editPhotosForm.value.image_pack = '';
  }
}

// Quick View Modal State
const selectedProductQuickView = ref(null);
const activeQuickViewAngle = ref(0);

const quickViewImagesList = computed(() => {
  if (!selectedProductQuickView.value) return [];
  const imgs = selectedProductQuickView.value.images || [];
  if (imgs.length > 0) return imgs;
  if (selectedProductQuickView.value.image_url) return [selectedProductQuickView.value.image_url];
  return ['/products/chakki-atta.jpg'];
});

const currentQuickViewImage = computed(() => {
  const list = quickViewImagesList.value;
  if (!list.length) return '';
  if (activeQuickViewAngle.value >= 0 && activeQuickViewAngle.value < list.length) {
    return list[activeQuickViewAngle.value];
  }
  return list[0];
});

function openQuickView(prod) {
  selectedProductQuickView.value = prod;
  activeQuickViewAngle.value = 0;
}

function closeQuickView() {
  selectedProductQuickView.value = null;
  activeQuickViewAngle.value = 0;
}

function nextQuickViewAngle() {
  const list = quickViewImagesList.value;
  if (list.length <= 1) return;
  activeQuickViewAngle.value = (activeQuickViewAngle.value + 1) % list.length;
}

function prevQuickViewAngle() {
  const list = quickViewImagesList.value;
  if (list.length <= 1) return;
  activeQuickViewAngle.value = (activeQuickViewAngle.value - 1 + list.length) % list.length;
}

// Touch swipe gestures for mobile devices
let touchStartX = 0;
let touchEndX = 0;

function handleTouchStart(e) {
  touchStartX = e.changedTouches[0].screenX;
}

function handleTouchEnd(e) {
  touchEndX = e.changedTouches[0].screenX;
  const diff = touchEndX - touchStartX;
  if (Math.abs(diff) > 40) {
    if (diff < 0) {
      nextQuickViewAngle();
    } else {
      prevQuickViewAngle();
    }
  }
}

function getAngleLabel(idx) {
  if (currentLang.value === 'mr') {
    if (idx === 0) return '📸 समोरासमोरील मुख्य पॅक (Front View)';
    if (idx === 1) return '🏷️ घटक व पोषण माहिती (Back / Ingredients)';
    return '📦 राशन पोत व पॅकिंग (Packaging / Texture)';
  } else if (currentLang.value === 'hi') {
    if (idx === 0) return '📸 सामने का मुख्य पैकेट (Front View)';
    if (idx === 1) return '🏷️ सामग्री व पोषण जानकारी (Back / Ingredients)';
    return '📦 बनावट व पैकिंग (Packaging / Texture)';
  } else {
    if (idx === 0) return '📸 Front Pack View';
    if (idx === 1) return '🏷️ Ingredients & Nutrition (Back)';
    return '📦 Packaging & Texture View';
  }
}

function getAngleShortLabel(idx) {
  if (currentLang.value === 'mr') {
    if (idx === 0) return 'समोरासमोर';
    if (idx === 1) return 'घटक व माहिती';
    return 'पोत व पॅक';
  } else if (currentLang.value === 'hi') {
    if (idx === 0) return 'सामने';
    if (idx === 1) return 'सामग्री';
    return 'पैकिंग';
  } else {
    if (idx === 0) return 'Front';
    if (idx === 1) return 'Back';
    return 'Pack';
  }
}

// Komal AI Voice & Smart Draft Bill State
const showKomalAiModal = ref(false);
const isRecording = ref(false);
const isAiLoading = ref(false);
const aiInputText = ref('');
const aiLanguage = ref('mr');
const aiResult = ref(null);
const speechSupported = ref(false);
let activeSpeechRecognition = null;
const baseSpeechInput = ref('');
let sessionFinalTranscript = '';
let sessionInterimTranscript = '';
let speechSilenceTimer = null;
let isUserExplicitStop = false;
let mediaRecorder = null;
let recordedAudioChunks = [];
let recordedAudioBase64 = null;
let recordedAudioMime = 'audio/webm';
let currentAiAudioPlayer = null;
const cachedAiAudio = ref(null);
let speechSessionId = 0;
const aiScanMode = ref('voice'); // 'voice' | 'photo'
const aiUploadedImages = ref([]); // Array of { id, data, mimeType, preview, sizeKb }
const aiImageCompressing = ref(false);

// Dukandar AI Voice & Store Control State (100% Isolated for Store Management)
const showDukandarAiModal = ref(false);
const dukandarAiTab = ref('control'); // 'control' | 'pos'
const dukandarAiText = ref('');
const dukandarAiLang = ref('en'); // default 'en', 'mr', 'hi'
const dukandarAiLoading = ref(false);
const dukandarAiResult = ref(null);
const dukandarPreviousState = ref(null); // for 1-click Undo

// Cart State
const cart = ref([]);
const isCartOpen = ref(false);
const showCheckoutModal = ref(false);
const orderSubmitting = ref(false);
const lastOrderReceipt = ref(null);
const useStoreCredit = ref(false);

// Delivery Availability 1-Tap State
const showDeliveryCheckModal = ref(false);
const deliveryCheckOrder = ref(null);
const deliveryCheckSubmitting = ref(false);

// Add to Active Delivery State (Plugs "Bhaiya, ek tel bhejwa dena" Margin Leak)
const showAddActiveItemModal = ref(false);
const activeOrderForAddon = ref(null);
const addonSearchQuery = ref('');
const addonSelectedVariant = ref({});
const addonQuantities = ref({});
const addonSubmitting = ref(false);
const addonSuccessItem = ref(null);

const quickAddonChips = [
  { tag: '', icon: '🌟', label: { mr: 'सर्व लोकप्रिय', hi: 'सभी आवश्यक', en: 'All Essentials' } },
  { tag: 'तेल', icon: '🌻', label: { mr: 'तेल', hi: 'तेल', en: 'Cooking Oil' } },
  { tag: 'मीठ', icon: '🧂', label: { mr: 'मीठ व साखर', hi: 'नमक व चीनी', en: 'Salt & Sugar' } },
  { tag: 'साबण', icon: '🧼', label: { mr: 'साबण व सर्फ', hi: 'साबुन व सर्फ', en: 'Soaps' } },
  { tag: 'चहा', icon: '☕', label: { mr: 'चहा व कॉफी', hi: 'चाय व कॉफी', en: 'Tea & Coffee' } },
  { tag: 'बिस्किट', icon: '🍪', label: { mr: 'बिस्किटे', hi: 'बिस्कुट', en: 'Biscuits' } },
  { tag: 'डाळ', icon: '🌾', label: { mr: 'डाळी', hi: 'दालें', en: 'Dals' } },
];

function canAddToActiveOrder(ord) {
  if (!ord) return false;
  const status = (ord.status || '').trim().toLowerCase();
  return ['placed', 'processing', 'packing', 'accepted'].includes(status);
}

function openAddActiveItemModal(order) {
  if (!order) return;
  activeOrderForAddon.value = order;
  addonSearchQuery.value = '';
  addonSuccessItem.value = null;
  showAddActiveItemModal.value = true;
}

function setAddonQuickChip(tag) {
  addonSearchQuery.value = tag;
}

function getAddonSelectedVariant(prod) {
  if (!prod) return null;
  if (addonSelectedVariant.value[prod.id]) return addonSelectedVariant.value[prod.id];
  if (prod.variants && prod.variants.length > 0) return prod.variants[0];
  return null;
}

function onAddonVariantChange(prod, variantId) {
  const v = (prod.variants || []).find(item => item.id == variantId);
  if (v) {
    addonSelectedVariant.value[prod.id] = v;
  }
}

function getAddonQuantity(prod) {
  return addonQuantities.value[prod.id] || 1;
}

function changeAddonQuantity(prod, delta) {
  const cur = getAddonQuantity(prod);
  const next = Math.max(1, Math.min(10, cur + delta));
  addonQuantities.value[prod.id] = next;
}

const addonFilteredProducts = computed(() => {
  if (!products.value || !products.value.length) return [];
  const q = (addonSearchQuery.value || '').trim().toLowerCase();
  if (!q) {
    return products.value.filter(p => {
      const cat = (p.category_name || '').toLowerCase();
      const n = (p.name || '').toLowerCase();
      return n.includes('oil') || n.includes('तेल') || n.includes('salt') || n.includes('मीठ') ||
             n.includes('sugar') || n.includes('साखर') || n.includes('tea') || n.includes('चहा') ||
             n.includes('soap') || n.includes('साबण') || n.includes('atta') || n.includes('पीठ') ||
             cat.includes('oil') || cat.includes('spice') || cat.includes('cleaning');
    }).slice(0, 15);
  }
  return products.value.filter(p => {
    const n = (p.name || '').toLowerCase();
    const cat = (p.category_name || '').toLowerCase();
    const mr = (p.name_mr || '').toLowerCase();
    const hi = (p.name_hi || '').toLowerCase();
    return n.includes(q) || cat.includes(q) || mr.includes(q) || hi.includes(q);
  }).slice(0, 20);
});

async function submitAddItemToActiveOrder(prod) {
  if (!activeOrderForAddon.value || addonSubmitting.value) return;
  const variant = getAddonSelectedVariant(prod);
  if (!variant) return;
  const qty = getAddonQuantity(prod);

  addonSubmitting.value = true;
  try {
    const orderNum = activeOrderForAddon.value.order_number;
    const token = activeOrderForAddon.value.tracking_token || '';

    const headers = { 'Content-Type': 'application/json' };
    if (authToken.value) {
      headers['Authorization'] = `Bearer ${authToken.value}`;
    }
    if (token) {
      headers['X-Tracking-Token'] = token;
    }

    const res = await fetch(`${API_BASE}/orders/${encodeURIComponent(orderNum)}/add-item`, {
      method: 'POST',
      headers,
      body: JSON.stringify({
        variant_id: variant.id,
        quantity: qty,
        token: token
      })
    });

    const data = await res.json();
    if (!res.ok) {
      if (data.code === 'DISPATCH_WINDOW_CLOSED') {
        alert(t('active_addon_dispatched'));
        showAddActiveItemModal.value = false;
        if (activeOrderForAddon.value) {
          activeOrderForAddon.value.status = 'Out for Delivery';
        }
      } else {
        alert(data.error || 'सामान जोडता आले नाही');
      }
      return;
    }

    // Success! Update active order and all synced references
    activeOrderForAddon.value = data.order;
    addonSuccessItem.value = data.added_item;

    // Update in customerOrders array and persistence vault
    if (customerOrders.value && customerOrders.value.length) {
      const idx = customerOrders.value.findIndex(o => o.order_number === data.order.order_number);
      if (idx !== -1) {
        customerOrders.value[idx] = data.order;
        try {
          localStorage.setItem('komal_cached_customer_orders', JSON.stringify(customerOrders.value));
          saveToCustomerOrderVault(customerOrders.value);
        } catch (e) {}
      }
    }

    // Update in lastOrderReceipt if open
    if (lastOrderReceipt.value && lastOrderReceipt.value.order_number === data.order.order_number) {
      lastOrderReceipt.value = data.order;
    }

    // Update in deliveryCheckOrder if open
    if (deliveryCheckOrder.value && deliveryCheckOrder.value.order_number === data.order.order_number) {
      deliveryCheckOrder.value = data.order;
    }

    // Update pendingUpiOrder if open
    if (pendingUpiOrder.value && pendingUpiOrder.value.order_number === data.order.order_number) {
      pendingUpiOrder.value = data.order;
    }

    showToast(
      currentLang.value === 'en'
        ? `✅ Added ${data.added_item.name} (${data.added_item.unit_size}) to Order #${data.order.order_number}! Total: ₹${data.order.final_amount}`
        : (currentLang.value === 'mr'
          ? `✅ ${data.added_item.name} (${data.added_item.unit_size}) चालू डिलिव्हरीमध्ये जोडले गेले! एकूण बिल: ₹${data.order.final_amount}`
          : `✅ ${data.added_item.name} (${data.added_item.unit_size}) चालू डिलीवरी में जुड़ गया! कुल बिल: ₹${data.order.final_amount}`)
    );
  } catch (err) {
    console.error('Error adding item to active order:', err);
    alert('सर्व्हरशी संपर्क होऊ शकला नाही');
  } finally {
    addonSubmitting.value = false;
  }
}

const customerForm = ref({
  name: '',
  phone: '',
  address: '',
  deliveryType: 'home_delivery', // 'home_delivery' | 'store_pickup'
  pincode: '400031',
  deliverySlot: 'standard',
  paymentMethod: 'Cash on Delivery (COD)',
  upiConfirmed: false,
  utrNumber: ''
});

const WADALA_SERVICEABLE_AREAS = [
  { pincode: '400031', name_mr: '४०००३१ — वडाळा (प) / कात्रक रोड / सहकार नगर', name_hi: '400031 — वडाला (प) / कात्रक रोड', name_en: '400031 — Wadala West / Katrak Road' },
  { pincode: '400037', name_mr: '४०००३७ — वडाळा (पू) / अंटॉप हिल / CGS कॉलनी', name_hi: '400037 — वडाला (पू) / अंटॉप हिल', name_en: '400037 — Wadala East / Antop Hill' },
  { pincode: '400015', name_mr: '४०००१५ — शिवडी (Sewri - वडाळा लगत)', name_hi: '400015 — शिवड़ी (Sewri)', name_en: '400015 — Sewri (Wadala Border)' },
  { pincode: '400014', name_mr: '४०००१४ — दादर (पूर्व) / हिंदू कॉलनी', name_hi: '400014 — दादर (पूर्व) / हिंदू कॉलोनी', name_en: '400014 — Dadar East / Hindu Colony' },
  { pincode: '400019', name_mr: '४०००१९ — माटुंगा (पूर्व) / बी.आर. आंबेडकर रोड', name_hi: '400019 — माटुंगा (पूर्व)', name_en: '400019 — Matunga East' },
  { pincode: '400022', name_mr: '४०००२२ — जी.टी.बी. नगर / सायन कोळीवाडा', name_hi: '400022 — जी.टी.बी. नगर / सायन', name_en: '400022 — GTB Nagar / Sion Koliwada' }
];

const ALLOWED_PINCODES = new Set(['400031', '400037', '400015', '400014', '400019', '400022']);

// Dynamic Area Delivery Hold Management State (Synced with Backend)
const areaDeliveryHolds = ref({
  '400031': { is_held: false, reason: '', resume: 'उद्या सकाळपर्यंत' },
  '400037': { is_held: false, reason: '', resume: 'उद्या सकाळपर्यंत' },
  '400015': { is_held: false, reason: '', resume: 'उद्या सकाळपर्यंत' },
  '400014': { is_held: false, reason: '', resume: 'उद्या सकाळपर्यंत' },
  '400019': { is_held: false, reason: '', resume: 'उद्या सकाळपर्यंत' },
  '400022': { is_held: false, reason: '', resume: 'उद्या सकाळपर्यंत' }
});

const isAreaHoldToggling = ref(false);

const isPincodeServiceable = computed(() => {
  if (customerForm.value.deliveryType === 'store_pickup') return true;
  const pin = (customerForm.value.pincode || '').trim();
  return ALLOWED_PINCODES.has(pin);
});

const activeSelectedAreaHold = computed(() => {
  if (customerForm.value.deliveryType === 'store_pickup') return null;
  const pin = (customerForm.value.pincode || '').trim();
  if (areaDeliveryHolds.value && areaDeliveryHolds.value[pin] && areaDeliveryHolds.value[pin].is_held) {
    return areaDeliveryHolds.value[pin];
  }
  return null;
});

async function fetchAreaDeliveryHolds() {
  try {
    const res = await fetch(`${API_BASE}/delivery-areas`);
    if (res.ok) {
      const data = await res.json();
      if (data.holds) {
        areaDeliveryHolds.value = { ...areaDeliveryHolds.value, ...data.holds };
      }
    }
  } catch (err) {
    console.warn('[DELIVERY HOLDS FETCH ERROR]', err);
  }
}

async function toggleAdminAreaHold(pincode, shouldHold, customReason = '') {
  isAreaHoldToggling.value = true;
  try {
    const res = await fetch(`${API_BASE}/admin/delivery-areas/toggle-hold`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${authToken.value}`
      },
      body: JSON.stringify({
        pincode: pincode,
        is_held: shouldHold,
        reason: customReason || (shouldHold ? 'डिलिव्हरी बॉय गैरहजर असल्याने तात्पुरती डिलिव्हरी थांबवली आहे.' : ''),
        resume: 'उद्या सकाळपर्यंत / पुढील २४ तासांत'
      })
    });
    const data = await res.json();
    if (res.ok && data.success) {
      areaDeliveryHolds.value = { ...areaDeliveryHolds.value, ...data.holds };
      showToast(data.message || '✅ डिलिव्हरी स्थिती अपडेट झाली!');
    } else {
      showToast(data.error || 'Failed to update area status');
    }
  } catch (err) {
    showToast('Network error while updating area status');
  } finally {
    isAreaHoldToggling.value = false;
  }
}

const isUrgentDelivery = computed(() => {
  return customerForm.value.deliverySlot === 'urgent' || customerForm.value.deliverySlot === 'instant';
});

const deliverySlotOptions = computed(() => [
  {
    id: 'standard',
    icon: '📦',
    title: t('slot_standard_title'),
    desc: t('slot_standard_desc'),
    label: currentLang.value === 'en' ? '📦 Standard Delivery (Same Day)' : (currentLang.value === 'mr' ? '📦 प्रमाणित डिलिव्हरी (आजच)' : '📦 स्टैंडर्ड डिलीवरी (आज ही)')
  },
  {
    id: 'urgent',
    icon: '⚡',
    title: t('slot_express_title'),
    desc: t('slot_express_desc'),
    label: currentLang.value === 'en' ? '⚡ Urgent Express (Under 30 Mins)' : (currentLang.value === 'mr' ? '⚡ तातडीची एक्सप्रेस (३० मिनिटांत)' : '⚡ ज़रूरी एक्सप्रेस (30 मिनट में)')
  }
]);

// Monthly Ration Checklist State
const showMonthlyParchaModal = ref(false);
const parchaSearchQuery = ref('');
const monthlyParchaItems = ref([
  {
    id: 'm1',
    name: 'चक्की का ताज़ा आटा (Chakki Atta)',
    productQuery: 'Chakki Fresh Shuddh Atta',
    variantUnit: '10kg Bori',
    fallbackPrice: 320,
    mrp: 380,
    isLoose: true,
    customWeight: 10,
    selected: true,
    quantity: 1,
    image: '/products/chakki-atta.jpg'
  },
  {
    id: 'm2',
    name: 'बासमती चावल (Basmati Rice)',
    productQuery: 'Basmati Rice',
    variantUnit: '5kg',
    fallbackPrice: 420,
    mrp: 480,
    isLoose: true,
    customWeight: 5,
    selected: true,
    quantity: 1,
    image: '/products/basmati-rice.jpg'
  },
  {
    id: 'm3',
    name: 'अरहर / तुअर दाल (Toor Dal)',
    productQuery: 'Toor Dal',
    variantUnit: '2kg',
    fallbackPrice: 290,
    mrp: 330,
    isLoose: true,
    customWeight: 2,
    selected: true,
    quantity: 1,
    image: '/products/toor-dal.jpg'
  },
  {
    id: 'm4',
    name: 'धुली मूँग दाल (Moong Dal)',
    productQuery: 'Moong Dal Dhuli',
    variantUnit: '1kg',
    fallbackPrice: 125,
    mrp: 140,
    isLoose: true,
    customWeight: 1,
    selected: true,
    quantity: 1,
    image: '/products/moong-dal-dhuli.jpg'
  },
  {
    id: 'm5',
    name: 'कच्ची घानी सरसों तेल (Mustard Oil)',
    productQuery: 'Mustard Oil',
    variantUnit: '2L',
    fallbackPrice: 270,
    mrp: 310,
    isLoose: true,
    customWeight: 2,
    selected: true,
    quantity: 1,
    image: '/products/fortune-oil.jpg'
  },
  {
    id: 'm6',
    name: 'टाटा नमक (Tata Salt)',
    productQuery: 'Tata Salt',
    variantUnit: '1kg',
    fallbackPrice: 25,
    mrp: 28,
    isLoose: false,
    selected: true,
    quantity: 1,
    image: '/products/tata-salt.jpg'
  },
  {
    id: 'm7',
    name: 'टाटा टी गोल्ड (Tata Tea Gold)',
    productQuery: 'Tata Tea Gold',
    variantUnit: '500g',
    fallbackPrice: 295,
    mrp: 330,
    isLoose: false,
    selected: true,
    quantity: 1,
    image: '/products/tata-tea.jpg'
  },
  {
    id: 'm8',
    name: 'कोलगेट टूथपेस्ट (Colgate Paste)',
    productQuery: 'Colgate Strong Teeth',
    variantUnit: '200g',
    fallbackPrice: 110,
    mrp: 130,
    isLoose: false,
    selected: true,
    quantity: 1,
    image: '/products/colgate-paste.jpg'
  }
]);

const parchaSearchResults = computed(() => {
  const q = parchaSearchQuery.value.trim().toLowerCase();
  if (!q) return [];
  const existingNames = new Set(monthlyParchaItems.value.map(it => (it.name || '').toLowerCase()));
  return products.value.filter(p => {
    const nameMatch = p.name.toLowerCase().includes(q) || (p.name_hi && p.name_hi.includes(q)) || (p.name_mr && p.name_mr.includes(q));
    const catMatch = p.category && p.category.toLowerCase().includes(q);
    return (nameMatch || catMatch) && !existingNames.has(p.name.toLowerCase());
  }).slice(0, 8);
});

function persistParchaToLocalStorage() {
  try {
    localStorage.setItem('komal_monthly_parcha', JSON.stringify(monthlyParchaItems.value));
  } catch (e) {
    console.warn('Failed to save parcha to localStorage:', e);
  }
}

function addProductToParcha(prod) {
  const v = prod.variants && prod.variants.length > 0 ? prod.variants[0] : null;
  const price = v ? v.selling_price : (prod.selling_price || 50);
  const mrp = v ? v.mrp : (prod.mrp || price + 10);
  const unitSize = v ? v.unit_size : '1 Unit';

  monthlyParchaItems.value.unshift({
    id: `custom_${prod.id}_${Date.now()}`,
    productId: prod.id,
    name: getLocalizedProductName(prod, currentLang.value),
    productQuery: prod.name,
    variantUnit: unitSize,
    fallbackPrice: price,
    mrp: mrp,
    isLoose: !!prod.is_loose,
    customWeight: prod.is_loose ? (parseFloat(unitSize) || 1) : null,
    selected: true,
    quantity: 1,
    image: prod.image_url ? prod.image_url.split('||')[0] : '/placeholder.png'
  });
  parchaSearchQuery.value = '';
  persistParchaToLocalStorage();
  showToast(currentLang.value === 'en' ? `Added ${prod.name} to Monthly Parcha!` : `पर्चा मध्ये जोडले!`);
}

function updateParchaQty(item, delta) {
  const current = item.quantity || 1;
  const next = current + delta;
  if (next >= 1) {
    item.quantity = next;
    persistParchaToLocalStorage();
  }
}

function removeParchaItem(index) {
  monthlyParchaItems.value.splice(index, 1);
  persistParchaToLocalStorage();
}

const monthlyParchaTotal = computed(() => {
  return monthlyParchaItems.value
    .filter(it => it.selected)
    .reduce((sum, it) => sum + (it.fallbackPrice * (it.quantity || 1)), 0);
});

const monthlyParchaSelectedCount = computed(() => {
  return monthlyParchaItems.value.filter(it => it.selected).length;
});

// Custom Weight for Loose Items (Khula Ration)
const customWeightMode = ref({});
const customWeightInputs = ref({});

// Customer Khata UPI Settlement Modal
const showUpiPayModal = ref(false);
const pendingUpiOrder = ref(null);
const pendingUpiUtr = ref('');

// Admin Orders Ledger Filter
const adminOrderFilter = ref('all');

// AI Vision & Speech Telemetry State (2-3 Day Live Test Telemetry)
const aiTelemetry = ref({
  summary_24h: {
    total_requests: 0,
    photo_scans: 0,
    voice_scans: 0,
    quota_errors: 0,
    avg_latency_ms: 0,
    engine_breakdown: {}
  },
  recent_logs: []
});

async function fetchAiMetrics() {
  if (!authToken.value) return;
  try {
    const res = await fetch(`${API_BASE}/admin/ai/metrics`, {
      headers: { 'Authorization': `Bearer ${authToken.value}` }
    });
    if (res.ok) {
      const data = await res.json();
      if (data.success && data.summary_24h) {
        aiTelemetry.value = data;
      }
    }
  } catch (e) {
    console.warn('fetchAiMetrics error:', e);
  }
}

const isAdminLoggedIn = computed(() => {
  return currentUser.value && currentUser.value.role === 'admin';
});

function showToast(msg) {
  toastMessage.value = msg;
  setTimeout(() => { toastMessage.value = ''; }, 3500);
}

// Check logged in user profile on load
async function checkAuth() {
  if (!authToken.value) {
    currentUser.value = null;
    localStorage.removeItem('kirana_user');
    return;
  }
  try {
    const res = await fetch(`${API_BASE}/auth/me`, {
      headers: { 'Authorization': `Bearer ${authToken.value}` }
    });
    if (res.ok) {
      const data = await res.json();
      currentUser.value = data.user;
      if (data.user) {
        localStorage.setItem('kirana_user', JSON.stringify(data.user));
        profileForm.value = { ...data.user };
        customerForm.value.name = data.user.name;
        customerForm.value.phone = data.user.phone;
        customerForm.value.address = data.user.address;
        if (data.user.role === 'admin' && adminOrders.value.length === 0) {
          loadAdminOrders();
          loadAdminCustomers();
          loadAdminKhata();
          loadAdminSupportTickets();
          fetchAiMetrics();
        } else if (data.user.role !== 'admin') {
          loadCustomerOrders();
        }
      }
    } else {
      logout();
    }
  } catch (err) {
    console.error('Auth error:', err);
  }
}

function getAuthModalTitle() {
  if (admin2faState.value.active) return t('auth_modal_title_2fa');
  if (authMode.value === 'reset_password') return t('auth_modal_title_reset');
  if (authMode.value === 'admin') return t('auth_modal_title_admin');
  if (authMode.value === 'register') return t('auth_modal_title_register');
  return t('auth_modal_title_login');
}

function formatAuthError(data, defaultMsg) {
  const code = data?.code;
  if (code) {
    const key = 'auth_err_' + code.toLowerCase();
    const translated = t(key);
    if (translated && translated !== key) {
      return translated;
    }
  }
  return data?.error || defaultMsg;
}

function openAuthModal(mode = 'login') {
  authMode.value = mode;
  authError.value = '';
  admin2faState.value = { active: false, temp_token: '', masked_email: '', admin_email: '', otp: '' };
  regOtpSent.value = false;
  regOtpCountdown.value = 0;
  if (regOtpTimer) clearInterval(regOtpTimer);
  registerForm.value = { name: '', username: '', email: '', phone: '', password: '', address: '', otp: '' };
  resetStep.value = 1;
  resetIdentifier.value = '';
  resetOtp.value = '';
  resetNewPassword.value = '';
  resetConfirmPassword.value = '';
  resetToken.value = '';
  resetMaskedTarget.value = '';
  resetMaskedEmail.value = '';
  resetNoEmailPhone.value = '';
  resetChannel.value = 'sms';
  resetHasEmail.value = false;
  resetHasPhone.value = false;
  if (mode === 'admin') {
    authForm.value = { identifier: 'thisisroushan01@gmail.com', password: '' };
  } else {
    authForm.value = { identifier: '', password: '' };
  }
  showAuthModal.value = true;
}

async function handleLogin() {
  authSubmitting.value = true;
  authError.value = '';
  try {
    const res = await fetch(`${API_BASE}/auth/login`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(authForm.value)
    });
    let data;
    try {
      data = await res.json();
    } catch (parseErr) {
      authError.value = res.status >= 500
        ? (currentLang.value === 'mr' ? 'सर्व्हरवर तांत्रिक अडचण आली आहे (500). कृपया थोड्या वेळाने प्रयत्न करा.' : (currentLang.value === 'hi' ? 'सर्वर पर तकनीकी समस्या आई है (500)। कृपया थोड़ी देर बाद प्रयास करें।' : 'Server encountered an internal error (500). Please try again shortly.'))
        : t('auth_err_network');
      return;
    }
    if (res.ok) {
      if (data.require_2fa) {
        admin2faState.value = {
          active: true,
          temp_token: data.temp_token,
          masked_email: data.masked_email,
          admin_email: data.admin_email,
          email_dispatched: data.email_dispatched,
          otp: ''
        };
        showToast(data.message || (currentLang.value === 'mr' ? 'सुरक्षा पडताळणी कोड पाठवला आहे' : (currentLang.value === 'hi' ? 'सुरक्षा सत्यापन कोड भेजा गया है' : 'Security verification code sent')));
        return;
      }

      authToken.value = data.token;
      localStorage.setItem('kirana_token', data.token);
      localStorage.setItem('kirana_user', JSON.stringify(data.user));
      currentUser.value = data.user;
      profileForm.value = { ...data.user };
      customerForm.value.name = data.user.name;
      customerForm.value.phone = data.user.phone;
      customerForm.value.address = data.user.address;
      showAuthModal.value = false;
      authForm.value = { identifier: '', password: '' };
      showToast(`${t('greeting')} ${data.user.name}!`);
      if (data.user.role === 'admin') {
        adminActiveTab.value = 'storefront';
        loadAdminOrders();
        loadAdminCustomers();
        loadAdminKhata();
      } else {
        loadCustomerOrders();
      }
    } else {
      authError.value = formatAuthError(data, currentLang.value === 'mr' ? 'लॉगिन अयशस्वी. कृपया पुन्हा प्रयत्न करा.' : (currentLang.value === 'hi' ? 'लॉगिन असफल। कृपया पुन: प्रयास करें।' : 'Login failed. Please try again.'));
    }
  } catch (err) {
    authError.value = t('auth_err_network');
  } finally {
    authSubmitting.value = false;
  }
}

async function handleVerifyAdmin2Fa() {
  if (!admin2faState.value.otp || admin2faState.value.otp.trim().length !== 6) {
    authError.value = t('auth_err_invalid_otp');
    return;
  }
  authSubmitting.value = true;
  authError.value = '';
  try {
    const res = await fetch(`${API_BASE}/auth/verify-admin-2fa`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        temp_token: admin2faState.value.temp_token,
        otp: admin2faState.value.otp.trim()
      })
    });
    let data;
    try {
      data = await res.json();
    } catch (parseErr) {
      authError.value = res.status >= 500
        ? (currentLang.value === 'mr' ? 'सर्व्हरवर तांत्रिक अडचण आली आहे (500). कृपया थोड्या वेळाने प्रयत्न करा.' : (currentLang.value === 'hi' ? 'सर्वर पर तकनीकी समस्या आई है (500)। कृपया थोड़ी देर बाद प्रयास करें।' : 'Server encountered an internal error (500). Please try again shortly.'))
        : t('auth_err_network');
      return;
    }
    if (res.ok) {
      authToken.value = data.token;
      localStorage.setItem('kirana_token', data.token);
      localStorage.setItem('kirana_user', JSON.stringify(data.user));
      currentUser.value = data.user;
      profileForm.value = { ...data.user };
      showAuthModal.value = false;
      admin2faState.value = { active: false, temp_token: '', masked_email: '', admin_email: '', otp: '' };
      authForm.value = { identifier: '', password: '' };
      showToast(`${t('greeting')} ${data.user.name}! 🔐`);
      if (data.user.role === 'admin') {
        adminActiveTab.value = 'storefront';
        loadAdminOrders();
        loadAdminCustomers();
        loadAdminKhata();
      }
    } else {
      authError.value = formatAuthError(data, t('auth_err_invalid_otp'));
    }
  } catch (err) {
    authError.value = t('auth_err_network');
  } finally {
    authSubmitting.value = false;
  }
}

async function handleRequestResetOtp(preferredChannel = null) {
  if (!resetIdentifier.value.trim()) {
    authError.value = currentLang.value === 'mr' ? 'कृपया मोबाईल नंबर किंवा ईमेल पत्ता टाका.' : (currentLang.value === 'hi' ? 'कृपया मोबाइल नंबर या ईमेल पता दर्ज करें।' : 'Please enter mobile number or email address.');
    return;
  }
  authSubmitting.value = true;
  authError.value = '';
  resetNoEmailPhone.value = '';
  try {
    const payload = {
      identifier: resetIdentifier.value.trim(),
      lang: currentLang.value || 'mr'
    };
    if (preferredChannel) payload.channel = preferredChannel;
    const res = await fetch(`${API_BASE}/auth/forgot-password`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload)
    });
    const data = await res.json();
    if (res.ok) {
      resetToken.value = data.reset_token;
      resetChannel.value = data.channel || 'email';
      resetMaskedTarget.value = data.masked_target || data.masked_email || '';
      resetWaLink.value = data.wa_link || '';
      resetWaCode.value = data.wa_code || '';
      resetHasEmail.value = Boolean(data.has_email);
      resetHasPhone.value = Boolean(data.has_phone);
      resetStep.value = 2;
      showToast(data.message || (resetChannel.value === 'whatsapp' ? '📲 WhatsApp पडताळणी तयार!' : `📩 OTP कोड ${resetMaskedTarget.value} वर पाठवला आहे.`));
    } else {
      authError.value = formatAuthError(data, currentLang.value === 'mr' ? 'रीसेट विनंती अयशस्वी.' : 'Failed to process reset request.');
    }
  } catch (err) {
    authError.value = t('auth_err_network');
  } finally {
    authSubmitting.value = false;
  }
}

async function handleResendResetOtp(switchChannel = null) {
  if (!resetToken.value) {
    resetStep.value = 1;
    return;
  }
  authSubmitting.value = true;
  authError.value = '';
  try {
    const payload = { reset_token: resetToken.value };
    if (switchChannel) payload.channel = switchChannel;
    const res = await fetch(`${API_BASE}/auth/resend-forgot-password`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload)
    });
    const data = await res.json();
    if (res.ok) {
      if (data.channel) resetChannel.value = data.channel;
      if (data.masked_target) resetMaskedTarget.value = data.masked_target;
      showToast(data.message || (resetChannel.value === 'sms' ? '🔄 नवीन OTP SMS द्वारे पुन्हा पाठवला आहे!' : '🔄 New OTP resent to email!'));
    } else {
      authError.value = formatAuthError(data, 'Resend failed');
    }
  } catch (err) {
    authError.value = t('auth_err_network');
  } finally {
    authSubmitting.value = false;
  }
}

async function handleVerifyAndResetPassword() {
  if (!resetOtp.value.trim() || resetOtp.value.trim().length !== 6) {
    authError.value = t('auth_err_invalid_otp');
    return;
  }
  if (!resetNewPassword.value || resetNewPassword.value.length < 4) {
    authError.value = t('auth_err_password_too_short');
    return;
  }
  if (resetNewPassword.value !== resetConfirmPassword.value) {
    authError.value = currentLang.value === 'mr' ? 'दोन्ही पासवर्ड जुळत नाहीत. कृपया पुन्हा तपासा.' : (currentLang.value === 'hi' ? 'दोनों पासवर्ड मेल नहीं खाते। कृपया पुनः जांचें।' : 'Passwords do not match. Please verify.');
    return;
  }

  authSubmitting.value = true;
  authError.value = '';
  try {
    const res = await fetch(`${API_BASE}/auth/reset-password`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        reset_token: resetToken.value,
        otp: resetOtp.value.trim(),
        new_password: resetNewPassword.value.trim()
      })
    });
    const data = await res.json();
    if (res.ok) {
      showToast(currentLang.value === 'mr' ? '✅ पासवर्ड यशस्वीरीत्या बदलला! आता नवीन पासवर्डने लॉगिन करा.' : (currentLang.value === 'hi' ? '✅ पासवर्ड सफलतापूर्वक बदला गया! अब नए पासवर्ड से लॉगिन करें।' : '✅ Password reset successfully! Please login with your new password.'));
      authMode.value = 'login';
      authForm.value.identifier = resetIdentifier.value;
      resetStep.value = 1;
      resetIdentifier.value = '';
      resetOtp.value = '';
      resetNewPassword.value = '';
      resetConfirmPassword.value = '';
      resetToken.value = '';
      resetMaskedTarget.value = '';
    } else {
      authError.value = formatAuthError(data, currentLang.value === 'mr' ? 'पासवर्ड बदल अयशस्वी.' : (currentLang.value === 'hi' ? 'पासवर्ड बदलना असफल।' : 'Password reset failed.'));
    }
  } catch (err) {
    authError.value = t('auth_err_network');
  } finally {
    authSubmitting.value = false;
  }
}

function isDummyPhone(phone) {
  if (!phone || phone.length !== 10) return true;
  if (new Set(phone).size <= 2) return true;
  const seqs = [
    '9876543210', '9876543211', '9876543212', '9876543213', '9876543214', '9876543215',
    '9876543216', '9876543217', '9876543218', '9876543219', '0123456789', '1234567890',
    '9123456789', '6789012345', '9876598765', '1234512345', '1122334455'
  ];
  if (seqs.includes(phone)) return true;
  if (phone.slice(0, 3) === phone.slice(3, 6) && phone.slice(3, 6) === phone.slice(6, 9)) return true;
  if (phone.slice(0, 2).repeat(5) === phone) return true;
  if (phone.slice(0, 4) === phone.slice(4, 8)) return true;
  for (const ch of new Set(phone)) {
    if (phone.split(ch).length - 1 >= 7) return true;
  }
  return false;
}

async function sendRegistrationOtp() {
  const phone = (registerForm.value.phone || '').trim();
  const phoneRegex = /^[6-9]\d{9}$/;
  if (!phoneRegex.test(phone)) {
    authError.value = t('auth_err_invalid_phone');
    return;
  }
  if (isDummyPhone(phone)) {
    authError.value = t('auth_err_dummy_phone');
    return;
  }
  regOtpSubmitting.value = true;
  authError.value = '';
  try {
    const res = await fetch(`${API_BASE}/auth/send-registration-otp`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ phone })
    });
    const data = await res.json();
    if (res.ok) {
      regOtpSent.value = true;
      regOtpCountdown.value = data.cooldown || 60;
      if (regOtpTimer) clearInterval(regOtpTimer);
      regOtpTimer = setInterval(() => {
        if (regOtpCountdown.value > 0) {
          regOtpCountdown.value--;
        } else {
          clearInterval(regOtpTimer);
        }
      }, 1000);
      showToast(currentLang.value === 'mr' ? `📲 OTP कोड ${phone} वर पाठवला आहे!` : (currentLang.value === 'hi' ? `📲 OTP कोड ${phone} पर भेजा गया है!` : `📲 OTP code sent to ${phone}!`));
    } else {
      authError.value = data.error || (currentLang.value === 'mr' ? 'OTP पाठवता आला नाही.' : 'Failed to send OTP.');
    }
  } catch (err) {
    authError.value = t('auth_err_network');
  } finally {
    regOtpSubmitting.value = false;
  }
}

async function handleRegister() {
  const phone = (registerForm.value.phone || '').trim();
  const phoneRegex = /^[6-9]\d{9}$/;
  if (!phoneRegex.test(phone)) {
    authError.value = t('auth_err_invalid_phone');
    return;
  }
  if (isDummyPhone(phone)) {
    authError.value = t('auth_err_dummy_phone');
    return;
  }
  authSubmitting.value = true;
  authError.value = '';
  try {
    const payload = {
      name: registerForm.value.name.trim(),
      username: registerForm.value.username ? registerForm.value.username.trim() : null,
      phone: phone,
      email: registerForm.value.email ? registerForm.value.email.trim() : null,
      password: registerForm.value.password,
      address: registerForm.value.address.trim()
    };

    const res = await fetch(`${API_BASE}/auth/register`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload)
    });
    let data;
    try {
      data = await res.json();
    } catch (parseErr) {
      authError.value = res.status >= 500
        ? (currentLang.value === 'mr' ? 'सर्व्हरवर तांत्रिक अडचण आली आहे (500). कृपया थोड्या वेळाने प्रयत्न करा.' : (currentLang.value === 'hi' ? 'सर्वर पर तकनीकी समस्या आई है (500)। कृपया थोड़ी देर बाद प्रयास करें।' : 'Server encountered an internal error (500). Please try again shortly.'))
        : t('auth_err_network');
      return;
    }
    if (res.ok) {
      authToken.value = data.token;
      localStorage.setItem('kirana_token', data.token);
      localStorage.setItem('kirana_user', JSON.stringify(data.user));
      currentUser.value = data.user;
      profileForm.value = { ...data.user };
      customerForm.value.name = data.user.name;
      customerForm.value.phone = data.user.phone;
      customerForm.value.address = data.user.address;
      showAuthModal.value = false;
      regOtpSent.value = false;
      regOtpCountdown.value = 0;
      if (regOtpTimer) clearInterval(regOtpTimer);
      showToast(`${t('greeting')} ${data.user.name}!`);
    } else {
      authError.value = formatAuthError(data, currentLang.value === 'mr' ? 'नोंदणी अयशस्वी.' : (currentLang.value === 'hi' ? 'पंजीकरण असफल।' : 'Registration failed.'));
    }
  } catch (err) {
    authError.value = t('auth_err_network');
  } finally {
    authSubmitting.value = false;
  }
}

function logout() {
  authToken.value = '';
  currentUser.value = null;
  adminPreviewAsCustomer.value = false;
  adminActiveTab.value = 'storefront';
  localStorage.removeItem('kirana_token');
  localStorage.removeItem('kirana_user');
  showToast('लॉगआउट संपन्न हुआ।');
  resetFilters();
}

// Customer Account & Orders
function openAccountModal() {
  if (!currentUser.value) return;
  profileForm.value = { ...currentUser.value };
  showAccountModal.value = true;
  customerActiveTab.value = 'orders';
  loadCustomerOrders();
}

async function loadCustomerOrders() {
  // 1. Instant 0ms cache & vault hydration
  if (customerOrders.value.length === 0) {
    const cachedCustStr = localStorage.getItem('komal_cached_customer_orders');
    if (cachedCustStr) {
      try { customerOrders.value = JSON.parse(cachedCustStr); } catch (e) {}
    }
    if (customerOrders.value.length === 0) {
      const vaulted = getCustomerOrderVault();
      if (vaulted.length > 0) customerOrders.value = vaulted;
    }
  }
  // Only show blocking spinner if nothing in cache/vault
  customerOrdersLoading.value = customerOrders.value.length === 0;

  try {
    const res = await fetch(`${API_BASE}/customer/orders`, {
      headers: { 'Authorization': `Bearer ${authToken.value}` }
    });
    if (res.ok) {
      const freshOrders = await res.json();
      customerOrders.value = freshOrders;
      try {
        localStorage.setItem('komal_cached_customer_orders', JSON.stringify(freshOrders));
        saveToCustomerOrderVault(freshOrders);
      } catch (cacheErr) {
        console.warn('Customer vault cache error:', cacheErr);
      }
    }
  } catch (err) {
    console.error('Customer orders error:', err);
    // Offline resilience: load from customer vault if empty
    if (customerOrders.value.length === 0) {
      const vaulted = getCustomerOrderVault();
      if (vaulted.length > 0) customerOrders.value = vaulted;
    }
  } finally {
    customerOrdersLoading.value = false;
  }
}

// --- Customer Support, Complaints & Voice Input ---
let supportSpeechRecognition = null;
let baseSupportInput = '';

function toggleSupportVoiceInput() {
  const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
  if (!SpeechRecognition) {
    alert(currentLang.value === 'mr' ? 'तुमच्या ब्राउझरमध्ये व्हॉइस इनपुट समर्थित नाही.' : (currentLang.value === 'hi' ? 'आपके ब्राउज़र में वॉइस इनपुट समर्थित नहीं है।' : 'Voice recognition is not supported in this browser.'));
    return;
  }

  if (isSupportRecording.value) {
    stopSupportVoiceInput();
  } else {
    startSupportVoiceInput();
  }
}

function startSupportVoiceInput() {
  const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
  if (!SpeechRecognition) return;

  try {
    if (supportSpeechRecognition) {
      supportSpeechRecognition.abort();
    }
  } catch (e) {}

  baseSupportInput = supportMessage.value ? supportMessage.value.trim() : '';

  const recognition = new SpeechRecognition();
  recognition.continuous = true;
  recognition.interimResults = true;
  recognition.maxAlternatives = 1;

  const lang = currentLang.value || 'mr';
  recognition.lang = lang === 'mr' ? 'mr-IN' : (lang === 'hi' ? 'hi-IN' : 'en-IN');

  recognition.onstart = () => {
    isSupportRecording.value = true;
  };

  recognition.onresult = (event) => {
    let finalTranscript = '';
    let interimTranscript = '';
    for (let i = 0; i < event.results.length; ++i) {
      const res = event.results[i];
      if (res && res[0]) {
        if (res.isFinal) {
          finalTranscript += (finalTranscript ? ' ' : '') + res[0].transcript.trim();
        } else {
          interimTranscript += (interimTranscript ? ' ' : '') + res[0].transcript.trim();
        }
      }
    }
    const sessionText = [finalTranscript, interimTranscript].filter(Boolean).join(' ').trim();
    if (baseSupportInput) {
      supportMessage.value = baseSupportInput + ' ' + sessionText;
    } else {
      supportMessage.value = sessionText;
    }
  };

  recognition.onerror = (event) => {
    console.warn('Support speech error:', event.error);
    if (event.error !== 'no-speech') {
      isSupportRecording.value = false;
    }
  };

  recognition.onend = () => {
    isSupportRecording.value = false;
  };

  supportSpeechRecognition = recognition;
  try {
    recognition.start();
  } catch (err) {
    console.warn('Failed to start support speech:', err);
    isSupportRecording.value = false;
  }
}

function stopSupportVoiceInput() {
  if (supportSpeechRecognition) {
    try {
      supportSpeechRecognition.stop();
    } catch (e) {}
  }
  isSupportRecording.value = false;
}

async function loadCustomerSupportTickets() {
  if (!authToken.value && !currentUser.value) return;
  supportTicketsLoading.value = true;
  try {
    const res = await fetch(`${API_BASE}/support/my-tickets`, {
      headers: { 'Authorization': `Bearer ${authToken.value}` }
    });
    if (res.ok) {
      supportTicketsList.value = await res.json();
    }
  } catch (err) {
    console.error('Failed to load support tickets:', err);
  } finally {
    supportTicketsLoading.value = false;
  }
}

async function submitSupportTicket() {
  if (!supportCategory.value) {
    alert(currentLang.value === 'mr' ? 'कृपया प्रवर्गाची निवड करा.' : (currentLang.value === 'hi' ? 'कृपया श्रेणी का चयन करें।' : 'Please select a category.'));
    return;
  }
  if (!supportMessage.value || supportMessage.value.trim().length < 5) {
    alert(currentLang.value === 'mr' ? 'कृपया तक्रार किंवा अभिप्रायाचे सविस्तर वर्णन लिहा किंवा माईक वापरून बोला.' : (currentLang.value === 'hi' ? 'कृपया शिकायत या सुझाव का विवरण लिखें या माइक से बोलें।' : 'Please describe your complaint or feedback (or speak using mic).'));
    return;
  }

  const name = currentUser.value?.name || '';
  const phone = currentUser.value?.phone || '';
  const email = currentUser.value?.email || '';

  if (!name || !phone) {
    alert(currentLang.value === 'mr' ? 'कृपया आधी लॉगिन करा.' : 'Please log in to continue.');
    return;
  }

  if (isSupportRecording.value) {
    stopSupportVoiceInput();
  }

  supportSubmitting.value = true;
  try {
    const headers = {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${authToken.value}`
    };

    const payload = {
      ticket_type: supportTicketType.value,
      category: supportCategory.value,
      order_number: supportOrderNumber.value || null,
      message: supportMessage.value.trim(),
      customer_name: name,
      customer_phone: phone,
      customer_email: email
    };

    const res = await fetch(`${API_BASE}/support/ticket`, {
      method: 'POST',
      headers,
      body: JSON.stringify(payload)
    });

    const data = await res.json();
    if (!res.ok) {
      alert(data.error || 'Failed to submit ticket');
      return;
    }

    supportSuccessTicket.value = data.ticket;
    showToast(data.message || (supportTicketType.value === 'complaint' ? 'तक्रार नोंदवली गेली आहे!' : 'अभिप्राय पाठवला आहे!'));
    supportCategory.value = '';
    supportOrderNumber.value = '';
    supportMessage.value = '';

    loadCustomerSupportTickets();
  } catch (err) {
    console.error('Error submitting support ticket:', err);
    alert('नेटवर्क त्रुटी. कृपया पुन्हा प्रयत्न करा.');
  } finally {
    supportSubmitting.value = false;
  }
}

function resetSupportForm() {
  supportSuccessTicket.value = null;
  supportCategory.value = '';
  supportOrderNumber.value = '';
  supportMessage.value = '';
}

function openUpiPayForCustomerOrder(order) {
  pendingUpiOrder.value = order;
  pendingUpiUtr.value = '';
  showUpiPayModal.value = true;
}

async function confirmUpiPayForCustomerOrder() {
  if (!pendingUpiOrder.value) return;
  try {
    const res = await fetch(`${API_BASE}/customer/orders/${pendingUpiOrder.value.id}/pay`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${authToken.value}`
      },
      body: JSON.stringify({
        utr_number: pendingUpiUtr.value.trim()
      })
    });
    if (res.ok) {
      showToast(currentLang.value === 'en' ? '✅ UPI payment submitted! Store owner will verify against bank receipt.' : (currentLang.value === 'mr' ? '✅ UPI पेमेंट सबमिट केले! दुकानदार बँक मेसेज तपासून बिल चुकता करतील.' : '✅ UPI भुगतान सबमिट हुआ! दुकानदार बैंक SMS देखकर बिल चुकता करेंगे।'));
      showUpiPayModal.value = false;
      pendingUpiOrder.value = null;
      pendingUpiUtr.value = '';
      loadCustomerOrders();
    } else {
      const err = await res.json();
      alert(err.error || 'भुगतान दर्ज नहीं हो सका');
    }
  } catch (err) {
    console.error('Pay error:', err);
  }
}

async function confirmOrderAvailability(orderNumber, choice) {
  if (!orderNumber) return;
  deliveryCheckSubmitting.value = true;
  try {
    const headers = { 'Content-Type': 'application/json' };
    if (authToken.value) {
      headers['Authorization'] = `Bearer ${authToken.value}`;
    }
    const token = (deliveryCheckOrder.value && deliveryCheckOrder.value.tracking_token) || '';
    const res = await fetch(`${API_BASE}/orders/${encodeURIComponent(orderNumber)}/availability`, {
      method: 'POST',
      headers,
      body: JSON.stringify({ choice, token })
    });
    const data = await res.json();
    if (res.ok) {
      if (deliveryCheckOrder.value && deliveryCheckOrder.value.order_number === orderNumber) {
        deliveryCheckOrder.value.delivery_availability = choice;
      }
      // Update in customer orders list if present
      if (customerOrders.value) {
        const found = customerOrders.value.find(o => o.order_number === orderNumber);
        if (found) found.delivery_availability = choice;
      }
      // Update in admin orders list if admin is logged in
      if (adminOrders.value) {
        const foundAdmin = adminOrders.value.find(o => o.order_number === orderNumber);
        if (foundAdmin) foundAdmin.delivery_availability = choice;
      }
      showToast(
        choice === 'available'
          ? (currentLang.value === 'en' ? '✅ Delivery confirmed! Partner is on the way.' : (currentLang.value === 'mr' ? '✅ डिलिव्हरी निश्चित केली! पार्टनर तात्काळ पोहोचत आहे.' : '✅ डिलीवरी निश्चित! पार्टनर तुरंत पहुँच रहा है।'))
          : (currentLang.value === 'en' ? '⏳ Reschedule noted! Store will call you.' : (currentLang.value === 'mr' ? '⏳ नोंद घेतली! दुकानदार संपर्क करतील.' : '⏳ रीशेड्यूल दर्ज हुआ! स्टोर टीम कॉल करेगी।'))
      );
      setTimeout(() => {
        showDeliveryCheckModal.value = false;
      }, 1800);
    } else {
      showToast(data.error || 'Failed to update availability', 'error');
    }
  } catch (err) {
    console.error('Availability check error:', err);
    showToast('Network error updating availability', 'error');
  } finally {
    deliveryCheckSubmitting.value = false;
  }
}

async function openDeliveryCheckForOrder(orderNumber, token) {
  try {
    const headers = {};
    if (authToken.value) {
      headers['Authorization'] = `Bearer ${authToken.value}`;
    }
    const tokenQuery = token ? `?token=${encodeURIComponent(token)}` : '';
    const res = await fetch(`${API_BASE}/orders/${encodeURIComponent(orderNumber)}${tokenQuery}`, { headers });
    if (res.ok) {
      deliveryCheckOrder.value = await res.json();
      showDeliveryCheckModal.value = true;
    } else {
      console.warn('Could not find order for delivery check:', orderNumber);
    }
  } catch (err) {
    console.error('Failed to load order for check:', err);
  }
}

async function updateCustomerProfile() {
  try {
    const res = await fetch(`${API_BASE}/auth/profile`, {
      method: 'PUT',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${authToken.value}`
      },
      body: JSON.stringify({
        name: profileForm.value.name,
        email: profileForm.value.email ? profileForm.value.email.trim() : '',
        phone: profileForm.value.phone,
        address: profileForm.value.address,
        lang: currentLang.value
      })
    });
    if (res.ok) {
      const data = await res.json();
      currentUser.value = data.user;
      customerForm.value.name = data.user.name;
      customerForm.value.phone = data.user.phone;
      customerForm.value.address = data.user.address;
      showToast(currentLang.value === 'en' ? '✅ Address & profile updated!' : (currentLang.value === 'mr' ? '✅ पत्ता व प्रोफाईल अपडेट झाले!' : '✅ पता व प्रोफाइल अपडेट हो गया!'));
      showAccountModal.value = false;
    } else {
      const err = await res.json().catch(() => ({}));
      const fallbackMsg = currentLang.value === 'en' ? 'Update failed' : (currentLang.value === 'hi' ? 'अपडेट विफल' : 'अपडेट अयशस्वी');
      const msg = formatAuthError(err, fallbackMsg);
      showToast(`⚠️ ${msg}`, 'error');
    }
  } catch (err) {
    console.error('Profile update error:', err);
    showToast(currentLang.value === 'en' ? '⚠️ Network error updating profile' : (currentLang.value === 'hi' ? '⚠️ प्रोफाइल अपडेट करते समय नेटवर्क त्रुटि' : '⚠️ प्रोफाइल अपडेट करताना नेटवर्क त्रुटी आली'), 'error');
  }
}

function viewOrderReceipt(order) {
  lastOrderReceipt.value = order;
}

// Fetch categories & products
async function fetchCategories() {
  try {
    const res = await fetch(`${API_BASE}/categories`);
    if (res.ok) {
      categories.value = await res.json();
    }
  } catch (err) {
    console.error('Categories fetch error:', err);
  }
}

async function fetchProducts(retryCount = 0) {
  loading.value = true;
  try {
    const params = new URLSearchParams();
    if (selectedCategorySlug.value) params.append('category', selectedCategorySlug.value);
    if (searchQuery.value.trim()) params.append('search', searchQuery.value.trim());
    if (looseFilter.value !== 'all') params.append('loose', looseFilter.value);
    if (sortBy.value) params.append('sort', sortBy.value);

    const res = await fetch(`${API_BASE}/products?${params.toString()}`);
    if (res.ok) {
      products.value = await res.json();
      products.value.forEach(p => {
        if (p.variants && p.variants.length > 0 && !selectedVariants.value[p.id]) {
          selectedVariants.value[p.id] = p.variants[0].id;
        }
      });
    } else if (retryCount < 2) {
      setTimeout(() => { fetchProducts(retryCount + 1); }, 1200);
      return;
    }
  } catch (err) {
    console.error('Products fetch error:', err);
    if (retryCount < 2) {
      setTimeout(() => { fetchProducts(retryCount + 1); }, 1200);
      return;
    }
  } finally {
    loading.value = false;
  }
}

let debounceTimer = null;
function debounceFetchProducts() {
  clearTimeout(debounceTimer);
  debounceTimer = setTimeout(() => { fetchProducts(); }, 300);
}

function clearSearch() {
  clearTimeout(debounceTimer);
  searchQuery.value = '';
  fetchProducts();
}

function selectCategory(slug) {
  selectedCategorySlug.value = slug;
  fetchProducts();
}

function setLooseFilter(val) {
  looseFilter.value = val;
  fetchProducts();
}

function resetFilters() {
  selectedCategorySlug.value = '';
  searchQuery.value = '';
  looseFilter.value = 'all';
  sortBy.value = '';
  fetchProducts();
}

function selectVariant(productId, variantId) {
  customWeightMode.value[productId] = false;
  selectedVariants.value[productId] = variantId;
}

function getActiveVariant(product) {
  if (!product.variants || product.variants.length === 0) return null;
  const currentVariantId = selectedVariants.value[product.id];
  return product.variants.find(v => v.id === currentVariantId) || product.variants[0];
}

function getLocalizedTitle(prod) {
  if (!prod) return '';
  return getLocalizedProductName(prod, currentLang.value);
}

function hasClearanceVariant(prod) {
  if (!adminAllowClearancePublic.value) return false;
  if (!prod || !prod.variants) return false;
  return prod.variants.some(v => v.is_clearance && v.clearance_price);
}

// Loose items custom weight helpers
function isLooseProduct(prod) {
  return prod.is_loose === true || 
    (prod.brand && prod.brand.toLowerCase().includes('loose')) || 
    (prod.name && (prod.name.toLowerCase().includes('loose') || prod.name_hi.includes('खुली') || prod.name_hi.includes('खुला')));
}

function enableCustomWeight(prod) {
  customWeightMode.value[prod.id] = true;
  if (!customWeightInputs.value[prod.id]) {
    customWeightInputs.value[prod.id] = 1;
  }
}

function setQuickCustomWeight(prodId, wt) {
  customWeightInputs.value[prodId] = wt;
}

function adjustCustomWeight(prodId, delta) {
  const current = parseFloat(customWeightInputs.value[prodId]) || 1.0;
  const next = Math.max(0.25, Math.round((current + delta) * 100) / 100);
  customWeightInputs.value[prodId] = next;
}

function getBasePerKgRate(prod) {
  if (!prod.variants || prod.variants.length === 0) return 0;
  const oneKg = prod.variants.find(v => {
    const s = v.unit_size.toLowerCase();
    return s.includes('1kg') || s.includes('1 kg') || s.includes('1 litre') || s.includes('1l');
  });
  if (oneKg) return oneKg.selling_price;
  
  const halfKg = prod.variants.find(v => {
    const s = v.unit_size.toLowerCase();
    return s.includes('500g') || s.includes('500ml');
  });
  if (halfKg) return halfKg.selling_price * 2;

  const quarterKg = prod.variants.find(v => {
    const s = v.unit_size.toLowerCase();
    return s.includes('250g') || s.includes('250ml');
  });
  if (quarterKg) return quarterKg.selling_price * 4;

  return prod.variants[0].selling_price;
}

function getBasePerKgMrp(prod) {
  if (!prod.variants || prod.variants.length === 0) return 0;
  const oneKg = prod.variants.find(v => {
    const s = v.unit_size.toLowerCase();
    return s.includes('1kg') || s.includes('1 kg') || s.includes('1 litre') || s.includes('1l');
  });
  if (oneKg) return oneKg.mrp;
  
  const halfKg = prod.variants.find(v => {
    const s = v.unit_size.toLowerCase();
    return s.includes('500g') || s.includes('500ml');
  });
  if (halfKg) return halfKg.mrp * 2;

  const quarterKg = prod.variants.find(v => {
    const s = v.unit_size.toLowerCase();
    return s.includes('250g') || s.includes('250ml');
  });
  if (quarterKg) return quarterKg.mrp * 4;

  return prod.variants[0].mrp;
}

function getEffectivePerKgRate(prod, wt) {
  let rate = getBasePerKgRate(prod);
  const w = parseFloat(wt) || 0;
  if (prod && prod.tiered_prices && prod.tiered_prices.length > 0 && w > 0) {
    const matching = [...prod.tiered_prices]
      .filter(t => w >= t.min_qty && (!t.max_qty || w <= t.max_qty))
      .sort((a, b) => b.min_qty - a.min_qty)[0];
    if (matching) {
      rate = matching.unit_price;
    }
  }
  return rate;
}

function getMatchingTierInfo(prod, qtyOrWt) {
  if (!prod || !prod.tiered_prices || prod.tiered_prices.length === 0) return null;
  const val = parseFloat(qtyOrWt) || 0;
  if (val <= 0) return null;
  return [...prod.tiered_prices]
    .filter(t => val >= t.min_qty && (!t.max_qty || val <= t.max_qty))
    .sort((a, b) => b.min_qty - a.min_qty)[0] || null;
}

function getCustomWeightPrice(prod) {
  const wt = parseFloat(customWeightInputs.value[prod.id]) || 0;
  const rate = getEffectivePerKgRate(prod, wt);
  return (Math.round(rate * wt * 100) / 100).toFixed(2);
}

function addCustomWeightItemToCart(prod) {
  const wt = parseFloat(customWeightInputs.value[prod.id]);
  if (!wt || wt <= 0) {
    showToast('कृपया सही वजन दर्ज करें (उदा: 1.5, 4.5, 10 kg)');
    return;
  }
  const rate = getEffectivePerKgRate(prod, wt);
  const mrpRate = getBasePerKgMrp(prod);
  const subtotal = Math.round(rate * wt * 100) / 100;
  const mrp = Math.round(mrpRate * wt * 100) / 100;
  const tier = getMatchingTierInfo(prod, wt);
  const unitSize = tier ? `${wt} kg (${tier.tier_label})` : `${wt} kg`;

  const existing = cart.value.find(item => item.is_custom_weight && item.product.id === prod.id && item.custom_weight === wt);
  if (existing) {
    existing.quantity += 1;
    existing.subtotal = Math.round(existing.quantity * subtotal * 100) / 100;
    existing.mrp = Math.round(existing.quantity * mrp * 100) / 100;
  } else {
    cart.value.push({
      id: `custom_${prod.id}_${wt}`,
      is_custom_weight: true,
      product: prod,
      custom_weight: wt,
      custom_unit_size: unitSize,
      unit_price: rate,
      single_subtotal: subtotal,
      single_mrp: mrp,
      subtotal: subtotal,
      mrp: mrp,
      quantity: 1,
      tier_label: tier ? tier.tier_label : null
    });
  }
  const tierMsg = tier ? ` 🎉 ${tier.tier_label} लागू!` : '';
  showToast(`🛒 ${prod.name} (${unitSize} - ₹${subtotal})${tierMsg} थैले में जोड़ा गया!`);
}

function getProductCardImage(prod) {
  if (!prod) return '/products/chakki-atta.jpg';
  const imgs = prod.images && prod.images.length > 0
    ? prod.images
    : (prod.image_url ? prod.image_url.split('||').map(s => s.trim()) : []);
  if (imgs.length <= 1) return imgs[0] || '/products/chakki-atta.jpg';

  const activeV = getActiveVariant(prod);
  if (activeV && activeV.unit_size) {
    const u = activeV.unit_size.toLowerCase();
    if ((u.includes('pack') || u.includes('bundle') || u.includes('+') || u.includes('saver')) && imgs[1]) {
      return imgs[1];
    }
  }
  return imgs[0] || '/products/chakki-atta.jpg';
}

function handleImageFallback(event) {
  event.target.src = '/products/chakki-atta.jpg';
}

// Cart Management
function addToCart(product, variant) {
  const existing = cart.value.find(item => !item.is_custom_weight && item.variant.id === variant.id);
  if (existing) {
    existing.quantity += 1;
  } else {
    cart.value.push({
      is_custom_weight: false,
      product,
      variant,
      quantity: 1
    });
  }
  showToast(`🛒 ${product.name} (${variant.unit_size}) थैले में जोड़ा गया!`);
}

function increaseQuantity(itemId) {
  const item = cart.value.find(i => (i.is_custom_weight ? i.id === itemId : i.variant.id === itemId));
  if (item) {
    item.quantity += 1;
    if (item.is_custom_weight) {
      item.subtotal = Math.round(item.quantity * item.single_subtotal * 100) / 100;
      item.mrp = Math.round(item.quantity * item.single_mrp * 100) / 100;
    }
  }
}

function decreaseQuantity(itemId) {
  const index = cart.value.findIndex(i => (i.is_custom_weight ? i.id === itemId : i.variant.id === itemId));
  if (index !== -1) {
    if (cart.value[index].quantity > 1) {
      cart.value[index].quantity -= 1;
      const item = cart.value[index];
      if (item.is_custom_weight) {
        item.subtotal = Math.round(item.quantity * item.single_subtotal * 100) / 100;
        item.mrp = Math.round(item.quantity * item.single_mrp * 100) / 100;
      }
    } else {
      cart.value.splice(index, 1);
      showToast('सामान थैले से हटाया गया');
    }
  }
}

function reorderEntireBill(order) {
  if (!order || !order.items || order.items.length === 0) return;
  let addedCount = 0;
  for (const it of order.items) {
    if (it.product_name && (it.product_name.includes('डिलिव्हरी') || it.product_name.toLowerCase().includes('delivery'))) continue;

    const prod = products.value.find(p => p.id === it.product_id);
    if (!prod) continue;

    if (it.is_custom_weight) {
      const match = (it.variant_label || it.unit_size || '').match(/([\d.]+)\s*kg/i);
      const wt = match ? parseFloat(match[1]) : 1;
      const rate = it.unit_price || (prod.variants[0] ? prod.variants[0].selling_price : 0);
      const mrpRate = it.mrp || (prod.variants[0] ? prod.variants[0].mrp : rate);
      const subtotal = Math.round(rate * wt * 100) / 100;
      const mrp = Math.round(mrpRate * wt * 100) / 100;
      const qty = it.quantity || 1;

      const existing = cart.value.find(item => item.is_custom_weight && item.product.id === prod.id && item.custom_weight === wt);
      if (existing) {
        existing.quantity += qty;
        existing.subtotal = Math.round(existing.quantity * subtotal * 100) / 100;
        existing.mrp = Math.round(existing.quantity * mrp * 100) / 100;
      } else {
        cart.value.push({
          id: `custom_${prod.id}_${wt}`,
          is_custom_weight: true,
          product: prod,
          custom_weight: wt,
          custom_unit_size: `${wt} kg`,
          unit_price: rate,
          single_subtotal: subtotal,
          single_mrp: mrp,
          subtotal: Math.round(qty * subtotal * 100) / 100,
          mrp: Math.round(qty * mrp * 100) / 100,
          quantity: qty
        });
      }
      addedCount++;
    } else {
      const variant = (prod.variants || []).find(v => v.id === it.variant_id) || (prod.variants || [])[0];
      if (variant) {
        const qty = it.quantity || 1;
        const existing = cart.value.find(item => !item.is_custom_weight && item.variant.id === variant.id);
        if (existing) {
          existing.quantity += qty;
        } else {
          cart.value.push({
            is_custom_weight: false,
            product: prod,
            variant: variant,
            quantity: qty
          });
        }
        addedCount++;
      }
    }
  }

  showAccountModal.value = false;
  showCartDrawer.value = true;
  showToast(
    currentLang.value === 'en'
      ? `🛒 Added ${addedCount} items from Bill #${order.order_number} to your cart!`
      : (currentLang.value === 'mr'
        ? `🛒 पावती #${order.order_number} मधील ${addedCount} वस्तू कार्टमध्ये जोडल्या!`
        : `🛒 पर्चा #${order.order_number} के ${addedCount} सामान थैले में जोड़े गए!`)
  );
}

// ==========================================
// Role-Aware Modal Routing & Dedicated Assistant Handlers
// ==========================================
function openCustomerAiModal() {
  if (!aiLanguage.value) {
    aiLanguage.value = (currentLang.value === 'hi' || currentLang.value === 'mr') ? currentLang.value : 'mr';
  }
  showKomalAiModal.value = true;
  initSpeechRecognition();
}

function openDukandarAiModal() {
  if (!isAdminLoggedIn.value || adminPreviewAsCustomer.value) {
    openCustomerAiModal();
    return;
  }
  if (!dukandarAiLang.value) {
    dukandarAiLang.value = currentLang.value || 'en';
  }
  showDukandarAiModal.value = true;
  dukandarAiResult.value = null;
  initSpeechRecognition();
}

function openAiModalByRole() {
  if (isAdminLoggedIn.value && !adminPreviewAsCustomer.value) {
    openDukandarAiModal();
  } else {
    openCustomerAiModal();
  }
}

function openKomalAiModal() {
  openAiModalByRole();
}

function closeCustomerAiModal() {
  isUserExplicitStop = true;
  if (speechSilenceTimer) {
    clearTimeout(speechSilenceTimer);
    speechSilenceTimer = null;
  }
  if (isRecording.value && activeSpeechRecognition) {
    try { activeSpeechRecognition.stop(); } catch (e) {}
  }
  isRecording.value = false;
  showKomalAiModal.value = false;
}

function closeDukandarAiModal() {
  isUserExplicitStop = true;
  if (speechSilenceTimer) {
    clearTimeout(speechSilenceTimer);
    speechSilenceTimer = null;
  }
  if (isRecording.value && activeSpeechRecognition) {
    try { activeSpeechRecognition.stop(); } catch (e) {}
  }
  isRecording.value = false;
  showDukandarAiModal.value = false;
}

function closeKomalAiModal() {
  closeCustomerAiModal();
  closeDukandarAiModal();
}

function buildLocalizedSummary(result, targetLang) {
  if (!result) return '';
  if (targetLang === 'mr' && result.summary_text_mr) return result.summary_text_mr;
  if (targetLang === 'hi' && result.summary_text_hi) return result.summary_text_hi;
  if (targetLang === 'en' && result.summary_text_en) return result.summary_text_en;

  // Synthesize dynamically from items if the backend didn't supply that language key
  const matched = (result.items || []).filter(it => it.match_status === 'matched');
  if (matched.length === 0) {
    if (targetLang === 'mr') return 'सामान ड्राफ्ट बिलमध्ये जोडले आहे.';
    if (targetLang === 'hi') return 'सामान ड्राफ्ट बिल में जोड़ दिया गया है।';
    return 'Your grocery items have been added to your draft bill.';
  }

  const itemsList = matched.map(it => {
    const q = it.quantity || 1;
    const u = it.unit_size || 'kg';
    const n = (targetLang === 'mr' || targetLang === 'hi') ? (it.product_name_hi || it.product_name) : it.product_name;
    return `${q} ${u} ${n}`;
  }).join(', ');

  if (targetLang === 'mr') {
    return `कोमल मार्टने तुमची ${itemsList} ऑर्डर नोंदवली आहे.`;
  } else if (targetLang === 'hi') {
    return `कोमल मार्ट में आपकी ${itemsList} ऑर्डर जोड़ दी गई है।`;
  } else {
    return `Successfully added ${itemsList} to your Komal Mart order.`;
  }
}

function setAiLanguage(lang) {
  aiLanguage.value = lang;
  cachedAiAudio.value = null; // Invalidate cached audio so speech matches the newly chosen language!

  // Instant response translation & speech: If an order summary already exists, switch to selected language
  if (aiResult.value) {
    aiResult.value.summary_text = buildLocalizedSummary(aiResult.value, lang);
    speakAiSummary(aiResult.value.summary_text, true);
  }

  isUserExplicitStop = true;
  if (speechSilenceTimer) {
    clearTimeout(speechSilenceTimer);
    speechSilenceTimer = null;
  }
  if (isRecording.value && activeSpeechRecognition) {
    try { activeSpeechRecognition.stop(); } catch (e) {}
  }
  if (isRecording.value && mediaRecorder && mediaRecorder.state !== 'inactive') {
    try { mediaRecorder.stop(); } catch (e) {}
  }
  isRecording.value = false;
}

function applyAiExample(phrase) {
  aiInputText.value = phrase;
  handleProcessAiOrder();
}

function initSpeechRecognition() {
  const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
  if (!SpeechRecognition) {
    speechSupported.value = false;
    return;
  }
  speechSupported.value = true;
}

function playNaturalAiAudio(audioB64, mime = 'audio/mpeg') {
  try {
    if (currentAiAudioPlayer) {
      currentAiAudioPlayer.pause();
      currentAiAudioPlayer = null;
    }
    currentAiAudioPlayer = new Audio(`data:${mime};base64,${audioB64}`);
    currentAiAudioPlayer.play().catch(e => {
      console.warn('Audio play restricted or waiting user gesture:', e);
    });
  } catch (err) {
    console.warn('playNaturalAiAudio error:', err);
  }
}

let activeUtterance = null;

async function speakAiSummary(text, forceApi = false) {
  if (!text) return;
  const lang = aiLanguage.value || currentLang.value || 'mr';

  // Stop any currently playing HTML5 audio
  if (currentAiAudioPlayer) {
    try { currentAiAudioPlayer.pause(); } catch (e) {}
    currentAiAudioPlayer = null;
  }

  // If we already have cached audio for this exact language, play it immediately!
  if (cachedAiAudio.value && !forceApi && cachedAiAudio.value.lang === lang) {
    playNaturalAiAudio(cachedAiAudio.value.b64, cachedAiAudio.value.mime);
    return;
  }

  // Local helper for guaranteed browser speech synthesis
  const speakBrowserNative = () => {
    if (!('speechSynthesis' in window)) return;
    try {
      window.speechSynthesis.cancel();
      window.speechSynthesis.resume();

      const utterance = new SpeechSynthesisUtterance(text);
      activeUtterance = utterance;

      const targetTag = lang === 'mr' ? 'mr-IN' : (lang === 'hi' ? 'hi-IN' : 'en-IN');
      utterance.lang = targetTag;
      utterance.rate = 1.0;
      utterance.pitch = 1.0;

      const voices = window.speechSynthesis.getVoices() || [];
      let chosenVoice = voices.find(v => v.lang.replace('_', '-').toLowerCase().startsWith(targetTag.toLowerCase()));
      // If Windows/Browser has no native Marathi voice, use Hindi voice to pronounce Devanagari text clearly
      if (!chosenVoice && lang === 'mr') {
        chosenVoice = voices.find(v => v.lang.replace('_', '-').toLowerCase().startsWith('hi-in') || v.lang.toLowerCase().startsWith('hi'));
      }
      if (!chosenVoice && lang === 'en') {
        chosenVoice = voices.find(v => v.lang.replace('_', '-').toLowerCase().startsWith('en-in') || v.lang.toLowerCase().startsWith('en'));
      }
      if (chosenVoice) {
        utterance.voice = chosenVoice;
      }

      utterance.onend = () => { activeUtterance = null; };
      utterance.onerror = (e) => {
        console.warn('Utterance status:', e);
        activeUtterance = null;
      };

      window.speechSynthesis.speak(utterance);
    } catch (err) {
      console.warn('Speech synthesis error:', err);
    }
  };

  // If Gemini API is available, try cloud synthesis with 2-second timeout
  try {
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), 6000);
    const res = await fetch(`${API_BASE}/ai/tts`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        text: text,
        language: lang,
        voice: 'Kore'
      }),
      signal: controller.signal
    });
    clearTimeout(timeoutId);
    const data = await res.json();
    if (res.ok && data.success && data.audio_base64) {
      const audioMime = data.mime_type || 'audio/mpeg';
      cachedAiAudio.value = { b64: data.audio_base64, mime: audioMime, lang: lang };
      playNaturalAiAudio(data.audio_base64, audioMime);
      return;
    }
  } catch (e) {
    // Cloud TTS unavailable / rate-limited / timed out
  }

  // Fallback to browser native speech
  speakBrowserNative();
}

function startAudioMediaRecorder() {
  recordedAudioChunks = [];
  recordedAudioBase64 = null;
  if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
    return;
  }
  navigator.mediaDevices.getUserMedia({ audio: true }).then(stream => {
    try {
      let mimeType = 'audio/webm';
      if (typeof MediaRecorder !== 'undefined') {
        if (MediaRecorder.isTypeSupported('audio/webm;codecs=opus')) {
          mimeType = 'audio/webm;codecs=opus';
        } else if (MediaRecorder.isTypeSupported('audio/mp4')) {
          mimeType = 'audio/mp4';
        }
      }
      recordedAudioMime = mimeType;
      mediaRecorder = new MediaRecorder(stream, { mimeType });
      mediaRecorder.ondataavailable = (e) => {
        if (e.data && e.data.size > 0) {
          recordedAudioChunks.push(e.data);
        }
      };
      mediaRecorder.onstop = () => {
        stream.getTracks().forEach(tr => tr.stop());
        if (recordedAudioChunks.length > 0) {
          const blob = new Blob(recordedAudioChunks, { type: recordedAudioMime });
          const reader = new FileReader();
          reader.onloadend = () => {
            if (reader.result) {
              const resStr = reader.result.toString();
              const commaIdx = resStr.indexOf(',');
              recordedAudioBase64 = commaIdx >= 0 ? resStr.substring(commaIdx + 1) : resStr;
            }
          };
          reader.readAsDataURL(blob);
        }
      };
      mediaRecorder.start(1000);
    } catch (e) {
      console.warn('MediaRecorder error:', e);
    }
  }).catch(e => {
    console.warn('getUserMedia audio permission or device error:', e);
  });
}

/**
 * Invisible Client-Side Canvas Compression:
 * Downscales handwritten receipt images to max 1000px and exports JPEG at 72% quality.
 * Shrinks raw 5-10MB camera photos to ~70-110KB in <200ms with zero customer effort.
 */
function compressImageSlip(file, maxDimension = 1000, quality = 0.72) {
  return new Promise((resolve, reject) => {
    const reader = new FileReader();
    reader.onload = (e) => {
      const img = new Image();
      img.onload = () => {
        let width = img.width;
        let height = img.height;

        if (width > maxDimension || height > maxDimension) {
          if (width > height) {
            height = Math.round((height * maxDimension) / width);
            width = maxDimension;
          } else {
            width = Math.round((width * maxDimension) / height);
            height = maxDimension;
          }
        }

        const canvas = document.createElement('canvas');
        canvas.width = width;
        canvas.height = height;
        const ctx = canvas.getContext('2d');
        ctx.fillStyle = '#FFFFFF';
        ctx.fillRect(0, 0, width, height);
        ctx.drawImage(img, 0, 0, width, height);

        // Export as JPEG at targeted quality
        const dataUrl = canvas.toDataURL('image/jpeg', quality);
        const commaIdx = dataUrl.indexOf(',');
        const b64 = commaIdx >= 0 ? dataUrl.substring(commaIdx + 1) : dataUrl;
        const sizeBytes = Math.round((b64.length * 3) / 4);

        resolve({
          data: b64,
          mimeType: 'image/jpeg',
          preview: dataUrl,
          sizeKb: Math.round(sizeBytes / 1024)
        });
      };
      img.onerror = reject;
      img.src = e.target.result;
    };
    reader.onerror = reject;
    reader.readAsDataURL(file);
  });
}

async function handleSlipImageUpload(event) {
  const files = Array.from(event.target.files || []);
  if (!files || files.length === 0) return;

  const currentCount = aiUploadedImages.value.length;
  if (currentCount + files.length > 5) {
    const l = aiLanguage.value || currentLang.value || 'mr';
    showToast(
      l === 'mr'
        ? 'एका वेळी जास्तीत जास्त ५ फोटो स्कॅन करता येतील.'
        : (l === 'hi' ? 'एक बार में अधिकतम 5 फोटो स्कैन कर सकते हैं।' : 'Maximum 5 photos allowed per bill scan.')
    );
    event.target.value = '';
    return;
  }

  aiImageCompressing.value = true;
  try {
    for (const file of files) {
      if (!file.type.startsWith('image/')) continue;
      const compressed = await compressImageSlip(file);
      aiUploadedImages.value.push({
        id: Date.now() + Math.random().toString(36).substring(2, 7),
        ...compressed
      });
    }
  } catch (err) {
    console.warn('Image slip compression error:', err);
    showToast('फोटो प्रोसेस करताना त्रुटी. कृपया पुन्हा प्रयत्न करा.');
  } finally {
    aiImageCompressing.value = false;
    event.target.value = '';
  }
}

function removeSlipImage(index) {
  aiUploadedImages.value.splice(index, 1);
}

function cleanSpokenTranscript(text) {
  if (!text) return '';
  let str = text;
  // Convert vernacular pauna / paun phonetic misrecognitions (e.g. "पन पन पन किलो" -> "पाऊण किलो")
  str = str.replace(/(?:(?:पन|पान|पोन)\s*(?:किलो|kg)?\s*)+/gi, 'पाऊण किलो ');
  // Deduplicate consecutive identical numbers like "9 9 kilo" or "9 9 9" -> "9 kilo"
  str = str.replace(/\b(\d+(?:\.\d+)?)(?:\s+\1)+\b/gi, '$1');
  // Deduplicate consecutive identical 2-word phrases like "आधा किलो आधा किलो" -> "आधा किलो"
  str = str.replace(/(\b[\w\u0900-\u097F]+\s+[\w\u0900-\u097F]+)(?:\s*,?\s*\1)+/gi, '$1');
  // Deduplicate consecutive identical words/numbers like "1 1 1 किलो" -> "1 किलो"
  str = str.replace(/(\b[\w\u0900-\u097F]+)(?:\s*,?\s*\1){2,}/gi, '$1');
  return str.replace(/\s{2,}/g, ' ').trim();
}

function startNewRecognitionInstance(currentSession) {
  const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
  if (!SpeechRecognition || isUserExplicitStop || !isRecording.value || currentSession !== speechSessionId) return;

  const recognition = new SpeechRecognition();
  recognition.continuous = true;
  recognition.interimResults = true;
  recognition.maxAlternatives = 1;

  const lang = showDukandarAiModal.value
    ? (dukandarAiLang.value || currentLang.value || 'en')
    : (aiLanguage.value || currentLang.value || 'mr');
  recognition.lang = lang === 'mr' ? 'mr-IN' : (lang === 'hi' ? 'hi-IN' : 'en-IN');

  recognition.onstart = () => {
    isRecording.value = true;
  };

  recognition.onresult = (event) => {
    // Maintain separate buffers per Claude's guidance:
    // finalTranscript is ONLY accumulated when res.isFinal is true.
    // interimTranscript is overwritten fresh each event, never appended or compounded.
    let newFinalChunks = '';
    let interimChunk = '';

    for (let i = event.resultIndex; i < event.results.length; ++i) {
      const res = event.results[i];
      if (res && res[0]) {
        const textChunk = (res[0].transcript || '').trim();
        if (res.isFinal) {
          newFinalChunks += (newFinalChunks ? ' ' : '') + textChunk;
        } else {
          interimChunk += (interimChunk ? ' ' : '') + textChunk;
        }
      }
    }

    if (newFinalChunks) {
      sessionFinalTranscript += (sessionFinalTranscript ? ' ' : '') + newFinalChunks;
    }
    sessionInterimTranscript = interimChunk;

    // Combine base text, accumulated final segments, and active transient interim segment
    const combinedSession = [sessionFinalTranscript, sessionInterimTranscript].filter(Boolean).join(' ').trim();
    const activeTextRef = showDukandarAiModal.value ? dukandarAiText : aiInputText;

    if (baseSpeechInput.value) {
      const prefix = baseSpeechInput.value.trim();
      activeTextRef.value = combinedSession ? cleanSpokenTranscript(prefix + ', ' + combinedSession) : prefix;
    } else {
      activeTextRef.value = cleanSpokenTranscript(combinedSession);
    }

    // Generous 30-second silence auto-cutoff timer for elders reciting 20-30 items
    if (speechSilenceTimer) clearTimeout(speechSilenceTimer);
    speechSilenceTimer = setTimeout(() => {
      if (isRecording.value && !isUserExplicitStop) {
        isUserExplicitStop = true;
        if (activeSpeechRecognition) {
          try { activeSpeechRecognition.stop(); } catch (e) {}
        }
        if (mediaRecorder && mediaRecorder.state !== 'inactive') {
          try { mediaRecorder.stop(); } catch (e) {}
        }
        isRecording.value = false;
      }
    }, 30000);
  };

  recognition.onerror = (event) => {
    console.warn('Speech recognition status:', event.error);
    if (event.error === 'no-speech') {
      return; // Do NOT abort on pauses
    }
    if (event.error === 'not-allowed' || event.error === 'service-not-allowed') {
      isUserExplicitStop = true;
      isRecording.value = false;
      if (speechSilenceTimer) clearTimeout(speechSilenceTimer);
      const l = showDukandarAiModal.value ? (dukandarAiLang.value || 'mr') : (aiLanguage.value || currentLang.value || 'mr');
      showToast(
        l === 'mr'
          ? 'मायक्रोफोन परवानगी नाकारली गेली आहे. कृपया ब्राउझर सेटिंगमध्ये परवानगी द्या.'
          : (l === 'hi'
            ? 'माइक की अनुमति अस्वीकृत है। कृपया ब्राउज़र सेटिंग्स में अनुमति दें।'
            : 'Microphone permission denied. Please allow mic access.')
      );
    }
  };

  recognition.onend = () => {
    // If recognition cycled naturally without user stopping, finalize any remaining interim into sessionFinalTranscript
    if (sessionInterimTranscript) {
      sessionFinalTranscript += (sessionFinalTranscript ? ' ' : '') + sessionInterimTranscript;
      sessionInterimTranscript = '';
    }

    // If not user-stopped, seamlessly cycle recognition instance
    if (!isUserExplicitStop && isRecording.value && currentSession === speechSessionId) {
      setTimeout(() => {
        if (!isUserExplicitStop && isRecording.value && currentSession === speechSessionId) {
          startNewRecognitionInstance(currentSession);
        }
      }, 100);
      return;
    }
    if (speechSilenceTimer) {
      clearTimeout(speechSilenceTimer);
      speechSilenceTimer = null;
    }
    isRecording.value = false;
  };

  activeSpeechRecognition = recognition;
  try {
    recognition.start();
  } catch (err) {
    console.warn('Recognition start error:', err);
  }
}

function toggleSpeechRecognition() {
  const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
  if (!SpeechRecognition && (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia)) {
    const l = showDukandarAiModal.value ? (dukandarAiLang.value || 'mr') : (aiLanguage.value || currentLang.value || 'mr');
    showToast(
      l === 'mr'
        ? 'तुमच्या ब्राउझरमध्ये व्हॉइस इनपुट सपोर्ट नाही. कृपया खाली टाईप करा.'
        : (l === 'hi'
          ? 'आपके ब्राउज़र में आवाज़ इनपुट सपोर्ट नहीं है। कृपया नीचे टाइप करें।'
          : 'Voice input is not supported in this browser. Please type below.')
    );
    return;
  }

  if (speechSilenceTimer) {
    clearTimeout(speechSilenceTimer);
    speechSilenceTimer = null;
  }

  if (isRecording.value) {
    isUserExplicitStop = true;
    if (activeSpeechRecognition) {
      try { activeSpeechRecognition.stop(); } catch (e) {}
    }
    if (mediaRecorder && mediaRecorder.state !== 'inactive') {
      try { mediaRecorder.stop(); } catch (e) {}
    }
    isRecording.value = false;
    return;
  }

  isRecording.value = true;
  isUserExplicitStop = false;
  speechSessionId++;
  sessionFinalTranscript = '';
  sessionInterimTranscript = '';
  const thisSession = speechSessionId;
  const currentActiveVal = showDukandarAiModal.value ? dukandarAiText.value : aiInputText.value;
  baseSpeechInput.value = currentActiveVal ? currentActiveVal.trim() : '';

  // Exclusive mic capture:
  // On Chrome / Edge / Safari / Android, SpeechRecognition handles real-time speech-to-text natively.
  // Running MediaRecorder (getUserMedia) concurrently locks the Android microphone hardware channel,
  // triggering the Android OS conflict: "Speech Recognition and Synthesis from Google cannot record now as Chrome is recording."
  // Therefore, use SpeechRecognition when available, and only fallback to MediaRecorder if SpeechRecognition is unsupported.
  if (SpeechRecognition) {
    startNewRecognitionInstance(thisSession);
  } else {
    startAudioMediaRecorder();
  }
}

async function handleProcessAiOrder() {
  const text = (aiInputText.value || '').trim();
  const hasImages = aiUploadedImages.value && aiUploadedImages.value.length > 0;

  if (!text && !recordedAudioBase64 && !hasImages) {
    const l = aiLanguage.value || currentLang.value || 'mr';
    showToast(
      l === 'mr'
        ? 'कृपया काहीतरी बोला, यादीचा फोटो जोडा, किंवा सामानाची नावे टाका.'
        : (l === 'hi'
          ? 'कृपया कुछ बोलें, पर्ची की फोटो जोड़ें, या राशन का नाम दर्ज करें।'
          : 'Please speak, upload a handwritten list photo, or type your grocery list.')
    );
    return;
  }

  isUserExplicitStop = true;
  if (speechSilenceTimer) {
    clearTimeout(speechSilenceTimer);
    speechSilenceTimer = null;
  }
  if (isRecording.value) {
    if (activeSpeechRecognition) {
      try { activeSpeechRecognition.stop(); } catch (e) {}
    }
    if (mediaRecorder && mediaRecorder.state !== 'inactive') {
      try { mediaRecorder.stop(); } catch (e) {}
    }
    isRecording.value = false;
  }

  // Short delay if media recorder just completed
  if (recordedAudioChunks.length > 0 && !recordedAudioBase64) {
    await new Promise(r => setTimeout(r, 250));
  }

  isAiLoading.value = true;
  try {
    const payload = {
      text: text,
      language: aiLanguage.value || currentLang.value || 'mr'
    };
    if (recordedAudioBase64) {
      payload.audio = recordedAudioBase64;
      payload.mime_type = recordedAudioMime || 'audio/webm';
    }
    if (hasImages) {
      payload.images = aiUploadedImages.value.map(img => ({
        data: img.data,
        mimeType: img.mimeType || 'image/jpeg'
      }));
    }

    const res = await fetch(`${API_BASE}/ai/parse-order`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload)
    });
    const data = await res.json();
    if (res.ok && data.success) {
      aiResult.value = data;
      // If backend detected regional Marathi or Hindi from the customer's input, sync aiLanguage
      if (data.language && ['mr', 'hi', 'en'].includes(data.language)) {
        aiLanguage.value = data.language;
      }

      // Ensure displayed summary text strictly matches the active language
      aiResult.value.summary_text = buildLocalizedSummary(data, aiLanguage.value);

      if (data.raw_text && !aiInputText.value.trim()) {
        aiInputText.value = data.raw_text;
      }
      if (data.audio_base64) {
        const audioMime = data.audio_mime_type || 'audio/mpeg';
        cachedAiAudio.value = { b64: data.audio_base64, mime: audioMime, lang: aiLanguage.value };
        playNaturalAiAudio(data.audio_base64, audioMime);
      } else if (aiResult.value.summary_text) {
        speakAiSummary(aiResult.value.summary_text, true);
      }
    } else {
      showToast(data.error || 'ऑर्डर तयार करताना अडचण आली. कृपया पुन्हा प्रयत्न करा.');
    }
  } catch (err) {
    console.error('Komal AI parse error:', err);
    showToast('सर्व्हरशी संपर्क होऊ शकला नाही. कृपया बॅकएंड तपासा.');
  } finally {
    isAiLoading.value = false;
  }
}

const aiEstimatedTotal = computed(() => {
  if (!aiResult.value || !aiResult.value.items) return 0;
  return aiResult.value.items.reduce((sum, it) => {
    if (it.match_status === 'matched') {
      return sum + (Number(it.unit_price || 0) * Number(it.quantity || 1));
    }
    return sum;
  }, 0).toFixed(2);
});

function selectAmbiguousVariant(item, opt) {
  item.variant_id = opt.variant_id;
  item.unit_size = opt.unit_size;
  item.unit_price = opt.price;
  item.line_total = Math.round(opt.price * item.quantity * 100) / 100;
  item.match_status = 'matched';
}

function addAlternativeItem(item) {
  if (!item.suggested_alternative) return;
  const alt = item.suggested_alternative;
  item.product_id = alt.product_id;
  item.variant_id = alt.variant_id;
  item.product_name = alt.product_name;
  item.product_name_hi = alt.product_name;
  item.unit_size = alt.unit_size;
  item.unit_price = alt.price;
  item.line_total = Math.round(alt.price * item.quantity * 100) / 100;
  item.match_status = 'matched';
  item.suggested_alternative = null;
}

function updateAiItemQty(item, delta) {
  item.quantity = Math.max(1, (item.quantity || 1) + delta);
  item.line_total = Math.round((item.unit_price || 0) * item.quantity * 100) / 100;
}

function removeAiItem(index) {
  if (aiResult.value && aiResult.value.items) {
    aiResult.value.items.splice(index, 1);
  }
}

const draftSearchQuery = ref('');
const draftSearchResults = computed(() => {
  const q = (draftSearchQuery.value || '').trim().toLowerCase();
  if (!q || q.length < 2) return [];
  return (products.value || []).filter(p => {
    const name = (p.name || '').toLowerCase();
    const nameHi = (p.name_hi || '').toLowerCase();
    const brand = (p.brand || '').toLowerCase();
    return name.includes(q) || nameHi.includes(q) || brand.includes(q);
  }).slice(0, 6);
});

function addManualProductToDraft(prod) {
  if (!prod || !prod.variants || prod.variants.length === 0) return;
  if (!aiResult.value) {
    aiResult.value = { items: [], summary_text: '' };
  }
  if (!aiResult.value.items) {
    aiResult.value.items = [];
  }
  const existing = aiResult.value.items.find(it => it.product_id === prod.id && it.match_status === 'matched');
  if (existing) {
    existing.quantity = (existing.quantity || 1) + 1;
    existing.line_total = Math.round((existing.unit_price || 0) * existing.quantity * 100) / 100;
  } else {
    const v = prod.variants.find(vr => vr.is_available) || prod.variants[0];
    const price = v.clearance_price && v.is_clearance ? v.clearance_price : v.selling_price;
    aiResult.value.items.push({
      query_term: prod.name,
      product_id: prod.id,
      variant_id: v.id,
      product_name: prod.name,
      product_name_hi: prod.name_hi || prod.name,
      image_url: prod.image_url,
      is_loose: Boolean(prod.is_loose),
      unit_size: v.unit_size,
      quantity: 1,
      unit_price: price,
      line_total: price,
      match_status: 'matched',
      options: [],
      suggested_alternative: null
    });
  }
  draftSearchQuery.value = '';
}

function addAllAiItemsToCart(autoOpenCheckout = false) {
  if (!aiResult.value || !aiResult.value.items) return;
  const matchedItems = aiResult.value.items.filter(it => it.match_status === 'matched');
  const l = aiLanguage.value || currentLang.value || 'mr';
  if (matchedItems.length === 0) {
    showToast(
      l === 'mr'
        ? 'कृपया आधी सामानाची निवड पूर्ण करा.'
        : (l === 'hi'
          ? 'कृपया पहले सामान का चयन पूरा करें।'
          : 'Please select/resolve items first.')
    );
    return;
  }

  let addedCount = 0;
  for (const it of matchedItems) {
    const prod = products.value.find(p => p.id === it.product_id);
    if (!prod) continue;

    if (it.is_custom_weight && it.custom_weight) {
      const wt = it.custom_weight;
      const rate = it.rate_per_kg || (it.unit_price / wt);
      const subtotal = it.line_total || Math.round(rate * wt * 100) / 100;
      const mrp = subtotal;

      const existing = cart.value.find(item => item.is_custom_weight && item.product && item.product.id === prod.id && item.custom_weight === wt);
      if (existing) {
        existing.quantity += it.quantity || 1;
        existing.subtotal = Math.round(existing.quantity * subtotal * 100) / 100;
        existing.mrp = Math.round(existing.quantity * mrp * 100) / 100;
      } else {
        cart.value.push({
          id: `custom_${prod.id}_${wt}`,
          is_custom_weight: true,
          product: prod,
          custom_weight: wt,
          custom_unit_size: it.unit_size || `${wt} kg`,
          unit_price: rate,
          single_subtotal: subtotal,
          single_mrp: mrp,
          subtotal: Math.round((it.quantity || 1) * subtotal * 100) / 100,
          mrp: Math.round((it.quantity || 1) * mrp * 100) / 100,
          quantity: it.quantity || 1
        });
      }
      addedCount++;
    } else {
      const variant = (prod.variants || []).find(v => v.id === it.variant_id) || prod.variants[0];
      if (!variant) continue;

      const existing = cart.value.find(c => !c.is_custom_weight && c.variant && c.variant.id === variant.id);
      if (existing) {
        existing.quantity += it.quantity;
      } else {
        cart.value.push({
          is_custom_weight: false,
          product: prod,
          variant: variant,
          quantity: it.quantity
        });
      }
      addedCount++;
    }
  }

  showToast(
    l === 'mr'
      ? `🎉 कोमल AI: ${addedCount} सामान थैलीमध्ये जोडले!`
      : (l === 'hi'
        ? `🎉 कोमल AI: ${addedCount} सामान थैले में जोड़ा गया!`
        : `🎉 Komal AI: Added ${addedCount} items to your cart!`)
  );

  showKomalAiModal.value = false;

  if (autoOpenCheckout) {
    showCheckoutModal.value = true;
  } else {
    showCartDrawer.value = true;
  }
}

function saveAllAiItemsToMonthlyParcha() {
  if (!aiResult.value || !aiResult.value.items) return;
  const matchedItems = aiResult.value.items.filter(it => it.match_status === 'matched');
  const l = aiLanguage.value || currentLang.value || 'mr';
  if (matchedItems.length === 0) {
    showToast(
      l === 'mr'
        ? 'कृपया आधी सामानाची निवड पूर्ण करा.'
        : (l === 'hi'
          ? 'कृपया पहले सामान का चयन पूरा करें।'
          : 'Please select/resolve items first.')
    );
    return;
  }

  let addedCount = 0;
  for (const it of matchedItems) {
    const prod = products.value.find(p => p.id === it.product_id);
    const existing = monthlyParchaItems.value.find(p => p.productId === it.product_id && p.variantUnit === it.unit_size);
    if (existing) {
      existing.quantity = (existing.quantity || 1) + (it.quantity || 1);
      existing.selected = true;
    } else {
      monthlyParchaItems.value.unshift({
        id: `ai_${it.product_id || Date.now()}_${Date.now()}_${Math.random().toString(36).substr(2, 4)}`,
        productId: it.product_id,
        name: l === 'mr' ? (it.product_name_hi || it.product_name) : (l === 'hi' ? (it.product_name_hi || it.product_name) : it.product_name),
        productQuery: it.product_name,
        variantUnit: it.unit_size || '1 Unit',
        fallbackPrice: it.unit_price || 50,
        mrp: it.unit_price ? Math.round(it.unit_price * 1.1) : 60,
        isLoose: !!it.is_loose,
        customWeight: null,
        selected: true,
        quantity: it.quantity || 1,
        image: it.image_url || (prod && prod.image_url ? prod.image_url.split('||')[0] : '/products/chakki-atta.jpg')
      });
    }
    addedCount++;
  }

  persistParchaToLocalStorage();

  showToast(
    l === 'mr'
      ? `📋 कोमल AI: ${addedCount} सामान तुमच्या मासिक रेशन यादीत सेव्ह झाले!`
      : (l === 'hi'
        ? `📋 कोमल AI: ${addedCount} सामान आपकी मासिक राशन सूची में सेव हो गए!`
        : `📋 Komal AI: Added ${addedCount} items to your Monthly Ration list!`)
  );
}

function quickCodOrderFromDraft() {
  if (!aiResult.value || !aiResult.value.items) return;
  const matchedItems = aiResult.value.items.filter(it => it.match_status === 'matched');
  const l = aiLanguage.value || currentLang.value || 'mr';
  if (matchedItems.length === 0) {
    showToast(
      l === 'mr'
        ? 'कृपया आधी सामानाची निवड पूर्ण करा.'
        : (l === 'hi'
          ? 'कृपया पहले सामान का चयन पूरा करें।'
          : 'Please select/resolve items first.')
    );
    return;
  }

  // 1. Put matched items in cart
  addAllAiItemsToCart(false);

  // 2. Pre-select Cash on Delivery (COD)
  customerForm.value.paymentMethod = 'Cash on Delivery (COD)';

  // 3. Auto-populate customer details if logged in
  if (currentUser.value && currentUser.value.phone) {
    customerForm.value.name = currentUser.value.name || customerForm.value.name;
    customerForm.value.phone = currentUser.value.phone;
    customerForm.value.address = currentUser.value.address || customerForm.value.address;
  }

  // 4. Close AI draft modal and cart drawer, open checkout modal directly
  showKomalAiModal.value = false;
  showCartDrawer.value = false;
  showCheckoutModal.value = true;

  showToast(
    currentLang.value === 'mr'
      ? '⚡ कॅश ऑन डिलिव्हरी निवडले आहे! कृपया १-टॅप मध्ये ऑर्डर कन्फर्म करा.'
      : (currentLang.value === 'hi'
        ? '⚡ कैश ऑन डिलीवरी चुना गया है! कृपया १-टैप में ऑर्डर कन्फर्म करें।'
        : '⚡ Cash on Delivery selected! Please confirm your order with 1 tap.')
  );
}

function getCartItemQuantity(productId, variantId) {
  const item = cart.value.find(i => !i.is_custom_weight && i.variant.id === variantId);
  return item ? item.quantity : 0;
}

const cartTotalQuantity = computed(() => {
  return cart.value.reduce((acc, item) => acc + item.quantity, 0);
});

const cartTotalAmount = computed(() => {
  return cart.value.reduce((acc, item) => {
    if (item.is_custom_weight) {
      return acc + item.subtotal;
    }
    const unitPrice = (adminAllowClearancePublic.value && item.variant.is_clearance && item.variant.clearance_price)
      ? item.variant.clearance_price
      : item.variant.selling_price;
    return acc + (unitPrice * item.quantity);
  }, 0).toFixed(2);
});

const cartTotalMrp = computed(() => {
  return cart.value.reduce((acc, item) => {
    if (item.is_custom_weight) {
      return acc + item.mrp;
    }
    return acc + (item.variant.mrp * item.quantity);
  }, 0).toFixed(2);
});

const cartTotalSavings = computed(() => {
  const savings = cartTotalMrp.value - cartTotalAmount.value;
  return savings > 0 ? savings.toFixed(2) : '0.00';
});

// Delivery Economics & Smart Add-ons
const DELIVERY_FREE_THRESHOLD = 500;
const DELIVERY_STANDARD_FEE = 35;
const DELIVERY_EXPRESS_FEE = 50;

const deliveryFee = computed(() => {
  if (cart.value.length === 0) return 0;
  if (customerForm.value.deliveryType === 'store_pickup') return 0;
  if (isUrgentDelivery.value) {
    return DELIVERY_EXPRESS_FEE;
  }
  return Number(cartTotalAmount.value) < DELIVERY_FREE_THRESHOLD ? DELIVERY_STANDARD_FEE : 0;
});

const cartPayableWithDelivery = computed(() => {
  return (Number(cartTotalAmount.value) + deliveryFee.value).toFixed(2);
});

// Store Credit Earning & Redemption Computations
const estimatedEarnedCredit = computed(() => {
  let earned = 0.0;
  for (const item of cart.value) {
    let isLoose = false;
    let subtotal = 0.0;
    if (item.is_custom_weight) {
      isLoose = item.product ? Boolean(item.product.is_loose) : true;
      subtotal = item.subtotal || 0;
    } else if (item.variant) {
      isLoose = item.product ? Boolean(item.product.is_loose) : false;
      const unitPrice = (adminAllowClearancePublic.value && item.variant.is_clearance && item.variant.clearance_price)
        ? item.variant.clearance_price
        : (item.variant.selling_price || 0);
      subtotal = unitPrice * (item.quantity || 1);
    }
    const rate = isLoose ? 0.025 : 0.005; // 2.5% on loose mandi staples, 0.5% on packaged FMCG
    earned += subtotal * rate;
  }
  return Math.round(earned * 100) / 100;
});

const appliedCreditAmount = computed(() => {
  if (!useStoreCredit.value || !currentUser.value) return 0;
  const avail = currentUser.value.wallet_balance || 0;
  const totalBefore = Number(cartTotalAmount.value) + deliveryFee.value;
  return Math.min(avail, totalBefore);
});

const finalPayableAmount = computed(() => {
  const total = Number(cartTotalAmount.value) + deliveryFee.value - appliedCreditAmount.value;
  return Math.max(0, total).toFixed(2);
});

const smartAddons = computed(() => {
  if (Number(cartTotalAmount.value) >= DELIVERY_FREE_THRESHOLD || cart.value.length === 0) {
    return [];
  }
  const cartProductIds = new Set(
    cart.value.map(item => (item.product ? item.product.id : (item.id || null)))
  );
  const neededGap = DELIVERY_FREE_THRESHOLD - Number(cartTotalAmount.value);

  // Filter available products not in cart, with price <= 160
  const candidates = products.value.filter(p => {
    if (cartProductIds.has(p.id)) return false;
    const v = p.variants && p.variants.length > 0 ? p.variants[0] : null;
    if (!v || v.selling_price <= 0) return false;
    return v.selling_price <= 160;
  });

  return candidates.sort((a, b) => {
    const priceA = a.variants[0].selling_price;
    const priceB = b.variants[0].selling_price;
    const diffA = Math.abs(neededGap - priceA);
    const diffB = Math.abs(neededGap - priceB);
    return diffA - diffB;
  }).slice(0, 6);
});

function openCheckoutModal() {
  if (currentUser.value) {
    customerForm.value.name = currentUser.value.name;
    customerForm.value.phone = currentUser.value.phone;
    customerForm.value.address = currentUser.value.address;
  }
  customerForm.value.upiConfirmed = false;
  isCartOpen.value = false;
  showCheckoutModal.value = true;
}

async function submitOrder() {
  if (cart.value.length === 0) return;

  const phone = customerForm.value.phone.trim();
  const phoneRegex = /^[6-9]\d{9}$/;
  if (!phoneRegex.test(phone)) {
    const invalidPhoneMsg = currentLang.value === 'en'
      ? 'Please enter a valid 10-digit Indian mobile number (e.g. 9876543210)'
      : (currentLang.value === 'mr' ? 'कृपया १० अंकांचा खरा भारतीय मोबाईल नंबर टाका (उदा. 9876543210)' : 'कृपया 10 अंकों का सही भारतीय मोबाइल नंबर दर्ज करें (उदा: 9876543210)');
    alert(invalidPhoneMsg);
    return;
  }

  if (customerForm.value.paymentMethod === 'UPI / QR Code' && !customerForm.value.upiConfirmed) {
    const upiMsg = currentLang.value === 'en'
      ? 'Please scan the QR code to pay, then check the confirmation box.'
      : (currentLang.value === 'mr' ? 'कृपया QR कोड स्कॅन करून पेमेंट केल्यावर चेकबॉक्स टिक करा.' : 'कृपया QR कोड स्कैन करके पेमेंट करने के बाद चेकबॉक्स टिक करें।');
    alert(upiMsg);
    return;
  }

  if (customerForm.value.deliveryType === 'home_delivery' && !isPincodeServiceable.value) {
    alert(t('delivery_pincode_error'));
    return;
  }

  orderSubmitting.value = true;
  try {
    const headers = { 'Content-Type': 'application/json' };
    if (authToken.value) {
      headers['Authorization'] = `Bearer ${authToken.value}`;
    }

    let finalAddress = '';
    if (customerForm.value.deliveryType === 'store_pickup') {
      finalAddress = `🏬 ${t('pickup_store_address')} [STORE PICKUP / काउंटर पिकअप]`;
    } else {
      const activeSlot = deliverySlotOptions.value.find(s => s.id === customerForm.value.deliverySlot)
        || deliverySlotOptions.value.find(s => s.label === customerForm.value.deliverySlot)
        || deliverySlotOptions.value[0];
      const slotLabel = activeSlot ? activeSlot.label : customerForm.value.deliverySlot;
      const slotPrefix = currentLang.value === 'en' ? '⏰ Slot:' : (currentLang.value === 'mr' ? '⏰ वेळ:' : '⏰ समय:');
      const pinCodeSuffix = customerForm.value.pincode ? ` [PIN: ${customerForm.value.pincode}]` : '';
      finalAddress = `${customerForm.value.address}${pinCodeSuffix} [${slotPrefix} ${slotLabel}]`;
    }

    const payload = {
      customer_name: customerForm.value.name,
      customer_phone: phone,
      customer_address: finalAddress,
      delivery_type: customerForm.value.deliveryType,
      pincode: customerForm.value.deliveryType === 'home_delivery' ? customerForm.value.pincode : '400031',
      payment_method: customerForm.value.paymentMethod,
      utr_number: customerForm.value.utrNumber ? customerForm.value.utrNumber.trim() : '',
      use_credit: useStoreCredit.value,
      items: cart.value.map(i => {
        if (i.is_custom_weight) {
          return {
            is_custom_weight: true,
            product_id: i.product.id,
            product_name: i.product.name,
            unit_size: i.custom_unit_size,
            unit_price: i.unit_price,
            subtotal: i.subtotal,
            mrp: i.mrp
          };
        }
        return {
          variant_id: i.variant.id,
          quantity: i.quantity
        };
      })
    };

    // If order has delivery fee, attach delivery fee line item to persist in DB & bills
    if (deliveryFee.value > 0) {
      const isUrgent = isUrgentDelivery.value;
      const feeLabel = isUrgent
        ? (currentLang.value === 'en' ? '⚡ Urgent Express Priority Fee (Under 30 Mins)' : (currentLang.value === 'mr' ? '⚡ तातडीची एक्सप्रेस डिलिव्हरी शुल्क (३० मिनिटे)' : '⚡ ज़रूरी एक्सप्रेस डिलीवरी शुल्क (30 मिनट)'))
        : (currentLang.value === 'en' ? 'Standard Delivery Fee (Under ₹500)' : (currentLang.value === 'mr' ? 'प्रमाणित डिलिव्हरी शुल्क (₹५०० पेक्षा कमी)' : 'स्टैंडर्ड डिलीवरी शुल्क (₹500 से कम)'));
      payload.items.push({
        is_custom_weight: true,
        product_id: null,
        product_name: feeLabel,
        unit_size: isUrgent ? '30-Min Priority' : 'Standard',
        unit_price: deliveryFee.value,
        subtotal: deliveryFee.value,
        mrp: deliveryFee.value
      });
    }

    const res = await fetch(`${API_BASE}/orders`, {
      method: 'POST',
      headers,
      body: JSON.stringify(payload)
    });

    if (res.ok) {
      const data = await res.json();
      if (data.order) {
        saveToCustomerOrderVault([data.order]);
      }
      if (data.user) {
        currentUser.value = data.user;
      } else if (currentUser.value && data.order) {
        const earnedToAdd = data.order.payment_status === 'Paid' ? (data.order.credit_earned || 0) : 0;
        currentUser.value.wallet_balance = (currentUser.value.wallet_balance || 0) - (data.order.credit_used || 0) + earnedToAdd;
      }
      useStoreCredit.value = false;
      cart.value = [];
      customerForm.value.upiConfirmed = false;
      customerForm.value.utrNumber = '';
      showCheckoutModal.value = false;
      const orderConfirmedMsg = currentLang.value === 'en'
        ? `🎉 Order confirmed! Bill #${data.order.order_number}`
        : (currentLang.value === 'mr' ? `🎉 ऑर्डर निश्चित झाली! बिल क्र.: ${data.order.order_number}` : `🎉 ऑर्डर पक्का हुआ! बिल संख्या: ${data.order.order_number}`);
      showToast(orderConfirmedMsg);
      fetchProducts();
      if (currentUser.value) {
        loadCustomerOrders();
      }
      if (data.order.payment_method && data.order.payment_method.toLowerCase().includes('upi')) {
        openUpiPayForCustomerOrder(data.order);
      } else {
        lastOrderReceipt.value = data.order;
      }
    } else {
      let err = null;
      try {
        err = await res.json();
      } catch (jsonErr) {
        err = { error: currentLang.value === 'en' ? `Server technical issue (${res.status}). Please try again.` : (currentLang.value === 'mr' ? `सर्व्हरवर तांत्रिक अडचण आली (${res.status}). कृपया पुन्हा प्रयत्न करा.` : `सर्वर पर तकनीकी समस्या (${res.status})। कृपया पुनः प्रयास करें।`) };
      }
      alert(err.error || (currentLang.value === 'en' ? 'Order could not be placed' : (currentLang.value === 'mr' ? 'ऑर्डर नोंदवता आली नाही' : 'ऑर्डर दर्ज नहीं हो सका')));
    }
  } catch (err) {
    console.error('Order error:', err);
    alert(currentLang.value === 'en' ? 'Unable to connect to server.' : (currentLang.value === 'mr' ? 'सर्व्हरशी संपर्क होऊ शकला नाही.' : 'सर्वर से संपर्क नहीं हो पाया।'));
  } finally {
    orderSubmitting.value = false;
  }
}

function printParcha() {
  window.print();
}

function shareOrderOnWhatsApp(order) {
  if (!order) return;
  const itemsText = order.items.map((it, idx) => {
    return `${idx + 1}. ${it.product_name} (${it.variant_label}) × ${it.quantity} = ₹${it.subtotal}`;
  }).join('\n');

  const creditUsedLine = order.credit_used > 0 ? `\n💳 *स्टोअर क्रेडिट सूट:* -₹${order.credit_used}` : '';
  const creditEarnedLine = order.credit_earned > 0 ? `\n🎉 *मिळवलेले स्टोअर क्रेडिट:* +₹${order.credit_earned}` : '';

  const payStatusDesc = order.payment_status === 'Paid'
    ? '🟢 चुकता (Paid)'
    : (order.payment_status === 'Partially Paid'
        ? `🟡 अर्धवट भरले (बाकी: ₹${order.balance_due || (order.final_amount - (order.amount_paid || 0))})`
        : (order.payment_status === 'Pending Verification' ? '⏳ UPI पडताळणी बाकी' : '🔴 बाकी उधारी'));

  const partialBreakdown = (order.amount_paid > 0 && (order.balance_due || (order.final_amount - order.amount_paid)) > 0)
    ? `\n💵 *आधी जमा (Advance Paid):* -₹${order.amount_paid}\n🔴 *घरी देय बाकी (Balance to Collect):* *₹${order.balance_due || (order.final_amount - order.amount_paid)}*`
    : '';

  const text = 
`🌾 *कोमल मार्ट (Komal Mart) - ऑर्डर पावती / बिल*
━━━━━━━━━━━━━━━━━━━━
📄 *पर्चा संख्या:* ${order.order_number}
📅 *दिनांक:* ${order.created_at}
👤 *ग्राहक:* ${order.customer_name} (📞 ${order.customer_phone})
📍 *पता:* ${order.customer_address}
💳 *भुगतान:* ${order.payment_method} (${payStatusDesc})

📦 *सामान सूची:*
${itemsText}
━━━━━━━━━━━━━━━━━━━━
💵 *कुल एमआरपी:* ₹${order.total_mrp}
🎉 *किराना बचत:* -₹${order.total_savings}${creditUsedLine}
💰 *कुल देय राशि:* *₹${order.final_amount}*${partialBreakdown}${creditEarnedLine}

🙏 धन्यवाद! फिर पधारें!`;

  const url = `https://api.whatsapp.com/send?text=${encodeURIComponent(text)}`;
  window.open(url, '_blank');
}

function openMonthlyParchaModal() {
  showMonthlyParchaModal.value = true;
}

function addMonthlyParchaToCart() {
  let addedCount = 0;
  monthlyParchaItems.value.forEach(mItem => {
    if (!mItem.selected) return;
    const qty = mItem.quantity || 1;

    const matchedProduct = products.value.find(p => 
      (mItem.productId && p.id === mItem.productId) ||
      p.name.toLowerCase().includes(mItem.productQuery.toLowerCase()) || 
      (p.name_hi && p.name_hi.includes(mItem.productQuery))
    );

    if (mItem.isLoose && mItem.customWeight) {
      const prodObj = matchedProduct || {
        id: mItem.id,
        name: mItem.name,
        name_hi: mItem.name,
        is_loose: true,
        image_url: mItem.image
      };
      const wt = mItem.customWeight;
      const rate = mItem.fallbackPrice / wt;
      const subtotal = mItem.fallbackPrice;
      const mrp = mItem.mrp;
      const unitSize = `${wt} kg`;

      const existing = cart.value.find(item => item.is_custom_weight && item.product.id === prodObj.id && item.custom_weight === wt);
      if (existing) {
        existing.quantity += qty;
        existing.subtotal = Math.round(existing.quantity * subtotal * 100) / 100;
        existing.mrp = Math.round(existing.quantity * mrp * 100) / 100;
      } else {
        cart.value.push({
          id: `custom_${prodObj.id}_${wt}`,
          is_custom_weight: true,
          product: prodObj,
          custom_weight: wt,
          custom_unit_size: unitSize,
          unit_price: rate,
          single_subtotal: subtotal,
          single_mrp: mrp,
          subtotal: Math.round(subtotal * qty * 100) / 100,
          mrp: Math.round(mrp * qty * 100) / 100,
          quantity: qty
        });
      }
      addedCount += qty;
    } else {
      if (matchedProduct && matchedProduct.variants && matchedProduct.variants.length > 0) {
        const variant = matchedProduct.variants.find(v => v.unit_size.toLowerCase().includes(mItem.variantUnit.toLowerCase())) || matchedProduct.variants[0];
        for (let i = 0; i < qty; i++) {
          addToCart(matchedProduct, variant);
        }
        addedCount += qty;
      } else {
        const fallbackVariant = {
          id: `var_${mItem.id}`,
          unit_size: mItem.variantUnit,
          selling_price: mItem.fallbackPrice,
          mrp: mItem.mrp
        };
        const prodObj = {
          id: mItem.id,
          name: mItem.name,
          image_url: mItem.image,
          variants: [fallbackVariant]
        };
        for (let i = 0; i < qty; i++) {
          addToCart(prodObj, fallbackVariant);
        }
        addedCount += qty;
      }
    }
  });

  showToast(`🎉 मासिक राशन के ${addedCount} सामान आपके थैले में जोड़े गए!`);
  showMonthlyParchaModal.value = false;
  isCartOpen.value = true;
}

// Admin Operations (Protected)
const filteredAdminProducts = computed(() => {
  let list = products.value;
  if (adminCategoryFilter.value !== '') {
    list = list.filter(p => p.category_id === adminCategoryFilter.value);
  }
  if (!adminSearch.value.trim()) return list;
  const q = adminSearch.value.toLowerCase();
  return list.filter(p =>
    p.name.toLowerCase().includes(q) ||
    (p.name_hi && p.name_hi.includes(q)) ||
    (p.brand && p.brand.toLowerCase().includes(q))
  );
});

async function saveVariantPrice(variant) {
  try {
    const res = await fetch(`${API_BASE}/variants/${variant.id}`, {
      method: 'PATCH',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${authToken.value}`
      },
      body: JSON.stringify({
        selling_price: variant.selling_price,
        mrp: variant.mrp,
        stock_quantity: variant.stock_quantity,
        is_clearance: Boolean(variant.is_clearance),
        clearance_price: variant.clearance_price ? Number(variant.clearance_price) : null
      })
    });

    if (res.ok) {
      const resData = await res.json().catch(() => ({}));
      if (resData.sibling_variants && Array.isArray(resData.sibling_variants)) {
        for (const p of products.value) {
          if (p.id === variant.product_id) {
            for (const sv of resData.sibling_variants) {
              const sib = (p.variants || []).find(vr => vr.id === sv.id);
              if (sib) Object.assign(sib, sv);
            }
            break;
          }
        }
      }
      const clearanceMsg = variant.is_clearance ? ` (🔥 सेल दर: ₹${variant.clearance_price})` : '';
      let msg = `✅ ${variant.unit_size} दर ₹${variant.selling_price}${clearanceMsg} सेव्ह झाली!`;
      if (resData.sibling_variants && resData.sibling_variants.length > 0) {
        const sibSummary = resData.sibling_variants.map(sv => `${sv.unit_size}: ₹${sv.selling_price}`).join(', ');
        msg = `✅ ${variant.unit_size} दर ₹${variant.selling_price}! इतर वजने: ${sibSummary}`;
      }
      showToast(msg);
    } else {
      const err = await res.json();
      alert(err.error || 'त्रुटि हुई');
    }
  } catch (err) {
    console.error('Update error:', err);
  }
}

async function toggleVariantStock(variant) {
  const currentActive = variant.is_in_stock !== undefined ? variant.is_in_stock : variant.is_available;
  const newActive = !currentActive;

  variant.is_in_stock = newActive;
  variant.is_available = newActive && (variant.stock_quantity === undefined || variant.stock_quantity > 0);

  try {
    const res = await fetch(`${API_BASE}/variants/${variant.id}`, {
      method: 'PATCH',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${authToken.value}`
      },
      body: JSON.stringify({
        is_available: newActive
      })
    });

    if (res.ok) {
      const msg = newActive
        ? (currentLang.value === 'mr' ? `✅ ${variant.unit_size} आता स्टॉकमध्ये उपलब्ध आहे!` : (currentLang.value === 'hi' ? `✅ ${variant.unit_size} अब स्टॉक में उपलब्ध है!` : `✅ ${variant.unit_size} is now In Stock!`))
        : (currentLang.value === 'mr' ? `⚠️ ${variant.unit_size} आता आउट-ऑफ-स्टॉक केले गेले.` : (currentLang.value === 'hi' ? `⚠️ ${variant.unit_size} अब आउट-ऑफ-स्टॉक कर दिया गया।` : `⚠️ ${variant.unit_size} marked Out of Stock.`));
      showToast(msg);
    } else {
      variant.is_in_stock = currentActive;
      variant.is_available = currentActive;
      const err = await res.json();
      showToast(`❌ ${err.error || 'स्टॉक अपडेट अयशस्वी'}`);
    }
  } catch (err) {
    console.error('Toggle stock error:', err);
    variant.is_in_stock = currentActive;
    variant.is_available = currentActive;
    showToast('❌ नेटवर्क त्रुटी.');
  }
}

async function quickRestockVariant(variant, amount = 10) {
  const oldQty = variant.stock_quantity || 0;
  variant.stock_quantity = oldQty + amount;
  variant.is_in_stock = true;
  variant.is_available = true;
  await saveVariantPrice(variant);
}

// --- DUKANDAR STOREKEEPER RAPID PRICE & STOCK EDIT METHODS ---
function hasWeightVariants(prod) {
  if (!prod || !prod.variants || prod.variants.length < 2) return false;
  let cnt = 0;
  for (const v of prod.variants) {
    const s = (v.unit_size || '').toLowerCase();
    if (/(?:\d+(?:\.\d+)?)\s*(?:g|gm|gms|kg|kilo|l|litre|liter|ml)/i.test(s) && !s.includes('₹') && !s.includes('rs') && !s.includes('pack of')) {
      cnt++;
    }
  }
  return cnt >= 2;
}

function openQuickPriceEdit(product, variant = null) {
  if (!product) return;
  quickEditProduct.value = product;
  const v = variant || (product.variants && product.variants.length > 0 ? product.variants[0] : null);
  if (v) {
    quickEditSelectedVariantId.value = v.id;
    quickEditForm.selling_price = v.selling_price;
    quickEditForm.mrp = v.mrp;
    quickEditForm.stock_quantity = v.stock_quantity !== undefined && v.stock_quantity !== null ? v.stock_quantity : 0;
    quickEditForm.is_available = v.is_available !== false;
    quickEditForm.is_clearance = Boolean(v.is_clearance);
    quickEditForm.clearance_price = v.clearance_price || null;
    quickEditForm.sync_proportional = true;
    quickEditForm.name = product.name || '';
    quickEditForm.name_hi = product.name_hi || '';
    quickEditForm.brand = product.brand || '';
    quickEditForm.is_loose = Boolean(product.is_loose);
    quickEditForm.description = product.description || '';
    quickEditForm.showDetailsSection = false;
  }
  showQuickPriceEditModal.value = true;
}

function selectQuickEditVariant(v) {
  if (!v) return;
  quickEditSelectedVariantId.value = v.id;
  quickEditForm.selling_price = v.selling_price;
  quickEditForm.mrp = v.mrp;
  quickEditForm.stock_quantity = v.stock_quantity !== undefined && v.stock_quantity !== null ? v.stock_quantity : 0;
  quickEditForm.is_available = v.is_available !== false;
  quickEditForm.is_clearance = Boolean(v.is_clearance);
  quickEditForm.clearance_price = v.clearance_price || null;
  quickEditForm.sync_proportional = true;
}

async function saveQuickPriceEdit() {
  if (!quickEditProduct.value || !quickEditSelectedVariantId.value) return;
  quickEditForm.isSaving = true;
  try {
    const payload = {
      selling_price: parseFloat(quickEditForm.selling_price),
      mrp: parseFloat(quickEditForm.mrp),
      stock_quantity: parseInt(quickEditForm.stock_quantity, 10),
      is_available: Boolean(quickEditForm.is_available),
      is_clearance: Boolean(quickEditForm.is_clearance),
      clearance_price: quickEditForm.clearance_price ? parseFloat(quickEditForm.clearance_price) : null,
      sync_proportional: quickEditForm.sync_proportional !== false
    };

    const res = await fetch(`${API_BASE}/variants/${quickEditSelectedVariantId.value}`, {
      method: 'PATCH',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${authToken.value}`
      },
      body: JSON.stringify(payload)
    });

    if (res.ok) {
      const resData = await res.json().catch(() => ({}));
      // Immediately reflect updates in reactive products state
      const prod = products.value.find(p => p.id === quickEditProduct.value.id);
      if (prod && prod.variants) {
        const v = prod.variants.find(vr => vr.id === quickEditSelectedVariantId.value);
        if (v) {
          Object.assign(v, payload);
          v.is_in_stock = payload.is_available && payload.stock_quantity > 0;
        }
        if (resData.sibling_variants && Array.isArray(resData.sibling_variants)) {
          for (const sv of resData.sibling_variants) {
            const sib = prod.variants.find(vr => vr.id === sv.id);
            if (sib) {
              Object.assign(sib, sv);
            }
          }
        }
      }
      if (quickEditProduct.value && quickEditProduct.value.variants && resData.sibling_variants) {
        for (const sv of resData.sibling_variants) {
          const sib = quickEditProduct.value.variants.find(vr => vr.id === sv.id);
          if (sib) {
            Object.assign(sib, sv);
          }
        }
      }

      // Check if product details (name, brand, description, is_loose) were also modified
      const isNameChanged = quickEditForm.name && quickEditForm.name.trim() !== quickEditProduct.value.name;
      const isNameHiChanged = quickEditForm.name_hi !== (quickEditProduct.value.name_hi || '');
      const isBrandChanged = quickEditForm.brand !== (quickEditProduct.value.brand || '');
      const isLooseChanged = quickEditForm.is_loose !== Boolean(quickEditProduct.value.is_loose);
      const isDescChanged = quickEditForm.description !== (quickEditProduct.value.description || '');

      if (isNameChanged || isNameHiChanged || isBrandChanged || isLooseChanged || isDescChanged) {
        const prodPayload = {
          name: quickEditForm.name.trim(),
          name_hi: quickEditForm.name_hi.trim(),
          brand: quickEditForm.brand.trim(),
          is_loose: Boolean(quickEditForm.is_loose),
          description: quickEditForm.description.trim()
        };
        await fetch(`${API_BASE}/products/${quickEditProduct.value.id}`, {
          method: 'PUT',
          headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${authToken.value}`
          },
          body: JSON.stringify(prodPayload)
        }).catch(e => console.error('Product details update error:', e));

        Object.assign(quickEditProduct.value, prodPayload);
        const storeProd = products.value.find(p => p.id === quickEditProduct.value.id);
        if (storeProd) Object.assign(storeProd, prodPayload);
      }

      const prodName = getLocalizedProductName(quickEditProduct.value, currentLang.value);
      const varSize = prod?.variants?.find(vr => vr.id === quickEditSelectedVariantId.value)?.unit_size || '';
      let toastMsg = currentLang.value === 'mr'
        ? `✅ ${prodName} (${varSize}) अपडेट झाले: ₹${payload.selling_price}, शिल्लक: ${payload.stock_quantity}`
        : `✅ ${prodName} (${varSize}) updated: ₹${payload.selling_price}, Stock: ${payload.stock_quantity}`;

      if (resData.sibling_variants && resData.sibling_variants.length > 0) {
        const sibSummary = resData.sibling_variants.map(sv => `${sv.unit_size}: ₹${sv.selling_price}`).join(', ');
        toastMsg = currentLang.value === 'mr'
          ? `✅ ${prodName} (${varSize}) दर ₹${payload.selling_price}! इतर वजने: ${sibSummary}`
          : `✅ ${prodName} (${varSize}) ₹${payload.selling_price}! Scaled: ${sibSummary}`;
      }

      showToast(toastMsg);
      showQuickPriceEditModal.value = false;
    } else {
      const err = await res.json().catch(() => ({}));
      showToast(`❌ ${err.error || 'अपडेट अयशस्वी'}`);
    }
  } catch (err) {
    console.error('saveQuickPriceEdit error:', err);
    showToast('❌ नेटवर्क त्रुटी आली. कृपया पुन्हा प्रयत्न करा.');
  } finally {
    quickEditForm.isSaving = false;
  }
}

function normalizeDukandarSynonyms(str) {
  return (str || '').toLowerCase()
    .replace(/[०-९]/g, d => '०१२३४५६७८९'.indexOf(d))
    .replace(/\bdaal\b/gi, 'dal')
    .replace(/\baata\b/gi, 'atta')
    .replace(/\bgehu\s*(?:ka)?\s*atta\b/gi, 'atta')
    .replace(/\bchini\b/gi, 'sugar')
    .replace(/\bsakhar\b/gi, 'sugar')
    .replace(/\btur\b/gi, 'toor')
    .replace(/\barhar\b/gi, 'toor')
    .replace(/\btandul\b/gi, 'rice')
    .replace(/\bchawal\b/gi, 'rice')
    .replace(/\bshilak\b/gi, 'stock')
    .replace(/\bkhata\b/gi, 'ledger');
}

function parseDukandarCommand(rawText, loadedProducts) {
  if (!rawText) return { success: false, reason: 'EMPTY' };
  const text = normalizeDukandarSynonyms(rawText);

  // 1. Detect Intent
  const isOutOfStock = /(?:out\s*of\s*stock|out-of-stock|आऊट\s*ऑफ\s*स्टॉक|आउट\s*ऑफ\s*स्टॉक|संपला|खत्म|बंद|not\s*available)/i.test(text);
  const isInStock = /(?:in\s*stock|in-stock|इन\s*स्टॉक|उपलब्ध|सुरू|चालू|available)/i.test(text) && !isOutOfStock;

  // Price extraction
  // Handles: 'price to Rs195/kg', 'price to 195', 'Rs 195', '₹195', '195/kg', '195 rupees', '190 रुपये', 'rate 195'
  const priceRegex = /(?:price|rate|भाव|दर|किंमत|रेट)\s*(?:is|to|set|of|=|करा|कर|ठेवा|करून)?\s*(?:rs\.?|₹|inr|रुपये|रुपया|रु)?\s*(\d+(?:\.\d+)?)|(?:rs\.?|₹|inr|रुपये|रुपया|रु)\s*(\d+(?:\.\d+)?)|(\d+(?:\.\d+)?)\s*(?:rs|₹|inr|रुपये|रुपया|रु|rupees|\/kg|per\s*kg)/i;
  const pm = text.match(priceRegex);
  const newPrice = pm ? parseFloat(pm[1] || pm[2] || pm[3]) : null;

  // Stock extraction
  const stockRegex = /(?:stock|qty|quantity|शिल्लक|स्टॉक)\s*(?:is|to|set|=|करा|कर|ठेवा|करून)?\s*(\d+)|(\d+)\s*(?:stock|packets?|units?|पॅक|नग|बोरी|units|items)/i;
  const sm = text.match(stockRegex);
  const newStock = sm ? parseInt(sm[1] || sm[2], 10) : null;

  // Status Query check
  const isQuery = /(?:what\s*is|check|show|tell|how\s*much|काय\s*आहे|किती\s*आहे|कितना\s*है)/i.test(text) && !newPrice && newStock === null && !isOutOfStock && !isInStock;

  // 2. Product Matching
  let bestProd = null;
  let bestScore = 0;
  const candidates = [];

  const skipWords = new Set([
    'change', 'update', 'price', 'rate', 'stock', 'qty', 'set', 'make', 'into', 'with', 'out',
    'mark', 'what', 'check', 'show', 'tell', 'how', 'much', 'the', 'of', 'to', 'is', 'for',
    'करा', 'कर', 'आहे', 'किती', 'भाव', 'दर', 'किंमत', 'रेट', 'रुपये', 'रुपया', 'स्टॉक',
    'करून', 'ठेवा', 'करो', 'देना', 'का', 'की', 'के'
  ]);

  const tokens = text.replace(/[^a-z0-9\u0900-\u097F\s]/gi, ' ').split(/\s+/).filter(w => w.length >= 2 && !skipWords.has(w));

  for (const p of loadedProducts) {
    const pNorm = normalizeDukandarSynonyms(p.name + ' ' + (p.name_hi || '') + ' ' + (p.brand || ''));
    let score = 0;

    for (const t of tokens) {
      if (pNorm.includes(t)) {
        score += t.length;
      }
    }

    if (score > 0) {
      candidates.push({ product: p, score });
    }
    if (score > bestScore) {
      bestScore = score;
      bestProd = p;
    }
  }

  candidates.sort((a, b) => b.score - a.score);

  if (!bestProd) {
    return {
      success: false,
      reason: 'PRODUCT_NOT_FOUND',
      query: rawText,
      candidates: candidates.slice(0, 4).map(c => c.product)
    };
  }

  // 3. Variant Matching
  let targetVariant = null;
  for (const v of (bestProd.variants || [])) {
    const sizeNorm = (v.unit_size || '').toLowerCase().replace(/\s+/g, '');
    if (text.includes(sizeNorm) ||
        (sizeNorm.includes('5kg') && (text.includes('5kg') || text.includes('5 kg') || text.includes('5 किलो') || text.includes('पाच किलो'))) ||
        (sizeNorm.includes('500g') && (text.includes('500g') || text.includes('500 g') || text.includes('आधा किलो') || text.includes('पावशेर'))) ||
        (sizeNorm.includes('1kg') && (text.includes('1kg') || text.includes('1 kg') || text.includes('1 किलो') || text.includes('/kg') || text.includes('per kg')))) {
      targetVariant = v;
      break;
    }
  }
  if (!targetVariant && bestProd.variants && bestProd.variants.length > 0) {
    targetVariant = getActiveVariant(bestProd) || bestProd.variants.find(v => (v.unit_size || '').toLowerCase().includes('1kg')) || bestProd.variants[0];
  }

  if (!targetVariant) {
    return { success: false, reason: 'NO_VARIANT', product: bestProd };
  }

  return {
    success: true,
    action: isQuery ? 'QUERY' : 'UPDATE',
    product: bestProd,
    variant: targetVariant,
    patch: {
      price: newPrice,
      stock: newStock,
      isAvailable: isOutOfStock ? false : (isInStock ? true : undefined)
    }
  };
}

function applyDukandarExample(text) {
  dukandarAiText.value = text;
  executeDukandarAiCommand(text);
}

async function executeDukandarAiCommand(rawText) {
  const input = (rawText || dukandarAiText.value || '').trim();
  if (!input) {
    showToast(dukandarAiLang.value === 'mr' ? 'कृपया काहीतरी बोला किंवा आज्ञा टाईप करा.' : (dukandarAiLang.value === 'hi' ? 'कृपया कुछ बोलें या कमांड टाइप करें।' : 'Please speak or enter a store command.'));
    return;
  }

  if (!isAdminLoggedIn.value || adminPreviewAsCustomer.value) {
    showToast('Unauthorized: Storekeeper access required.');
    return;
  }

  dukandarAiLoading.value = true;
  dukandarAiResult.value = null;

  try {
    // Mode: Walk-in POS Bill
    if (dukandarAiTab.value === 'pos') {
      await handleDukandarPosVoiceBill(input);
      return;
    }

    // Mode: Store Control (Price, Stock, In/Out of stock, Query)
    const parsed = parseDukandarCommand(input, products.value);

    if (!parsed.success) {
      if (parsed.reason === 'PRODUCT_NOT_FOUND') {
        dukandarAiResult.value = {
          success: false,
          type: 'NOT_FOUND',
          query: input,
          message: dukandarAiLang.value === 'mr'
            ? `"${input}" या आज्ञेशी जुळणारे उत्पादन सापडले नाही.`
            : (dukandarAiLang.value === 'hi'
              ? `"${input}" से मेल खाता उत्पाद नहीं मिला।`
              : `Could not find a product matching "${input}".`),
          candidates: parsed.candidates || []
        };
      } else {
        dukandarAiResult.value = {
          success: false,
          type: 'UNCLEAR',
          query: input,
          message: dukandarAiLang.value === 'mr'
            ? 'आज्ञा समजली नाही. उदा. "तूर डाळ 195 रुपये करा" किंवा "साखर स्टॉक 50 करा" असे बोला.'
            : (dukandarAiLang.value === 'hi'
              ? 'कमांड समझ नहीं आई। उदा. "तूर दाल 195 रु करो" या "चीनी स्टॉक 50 करो" बोलें।'
              : 'Command unclear. e.g. "change toor daal price to Rs195/kg" or "set sugar stock to 50".')
        };
      }
      return;
    }

    const { action, product, variant, patch } = parsed;

    // Handle STATUS QUERY (e.g. 'what is the price of toor dal')
    if (action === 'QUERY') {
      const pName = getLocalizedProductName(product, dukandarAiLang.value);
      const msg = dukandarAiLang.value === 'mr'
        ? `${pName} (${variant.unit_size}): विक्री दर ₹${variant.selling_price} (MRP: ₹${variant.mrp || variant.selling_price}), शिल्लक स्टॉक: ${variant.stock_quantity} (${variant.is_available ? '🟢 इन स्टॉक' : '🔴 आउट ऑफ स्टॉक'}).`
        : (dukandarAiLang.value === 'hi'
          ? `${pName} (${variant.unit_size}): बिक्री दर ₹${variant.selling_price} (MRP: ₹${variant.mrp || variant.selling_price}), कुल स्टॉक: ${variant.stock_quantity} (${variant.is_available ? '🟢 इन स्टॉक' : '🔴 आउट ऑफ स्टॉक'})।`
          : `${product.name} (${variant.unit_size}) is currently ₹${variant.selling_price} (MRP: ₹${variant.mrp || variant.selling_price}) with ${variant.stock_quantity} units in stock (${variant.is_available ? 'In Stock' : 'Out of Stock'}).`);

      dukandarAiResult.value = {
        success: true,
        type: 'QUERY',
        product,
        variant,
        summary_text: msg
      };
      speakAiSummary(msg, true);
      return;
    }

    // Handle UPDATE: Price, Stock, or Availability
    const patchPayload = {};
    const beforeState = {
      variant_id: variant.id,
      selling_price: variant.selling_price,
      mrp: variant.mrp,
      stock_quantity: variant.stock_quantity,
      is_available: variant.is_available
    };

    const siblingBeforeStates = (product.variants || [])
      .filter(v => v.id !== variant.id)
      .map(v => ({
        variant_id: v.id,
        unit_size: v.unit_size,
        selling_price: v.selling_price,
        mrp: v.mrp,
        stock_quantity: v.stock_quantity,
        is_available: v.is_available
      }));

    const changesSummary = [];

    if (patch.price !== null && patch.price !== undefined) {
      patchPayload.selling_price = patch.price;
      if (patch.price > (variant.mrp || 0)) {
        patchPayload.mrp = patch.price;
      }
      patchPayload.sync_proportional = true;
      changesSummary.push(`दर (${variant.unit_size}): ₹${variant.selling_price} ➔ ₹${patch.price}`);
    }

    if (patch.stock !== null && patch.stock !== undefined) {
      patchPayload.stock_quantity = patch.stock;
      if (patch.stock > 0 && patch.isAvailable === undefined && !variant.is_available) {
        patchPayload.is_available = true;
      }
      changesSummary.push(`स्टॉक: ${variant.stock_quantity} ➔ ${patch.stock}`);
    }

    if (patch.isAvailable !== undefined) {
      patchPayload.is_available = patch.isAvailable;
      if (!patch.isAvailable) {
        patchPayload.stock_quantity = 0;
        changesSummary.push(`उपलब्धता: 🔴 Out of Stock`);
      } else {
        if (!variant.stock_quantity || variant.stock_quantity <= 0) {
          patchPayload.stock_quantity = 20;
        }
        changesSummary.push(`उपलब्धता: 🟢 In Stock`);
      }
    }

    if (Object.keys(patchPayload).length === 0) {
      dukandarAiResult.value = {
        success: false,
        type: 'NO_CHANGES',
        message: 'No changes detected in command.'
      };
      return;
    }

    // PATCH variant via backend
    const res = await fetch(`${API_BASE}/variants/${variant.id}`, {
      method: 'PATCH',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${authToken.value}`
      },
      body: JSON.stringify(patchPayload)
    });

    if (res.ok) {
      const resData = await res.json().catch(() => ({}));
      // 0ms Reactive state update
      Object.assign(variant, patchPayload);
      if (patchPayload.is_available !== undefined) {
        variant.is_in_stock = patchPayload.is_available && (variant.stock_quantity > 0);
      }

      // Update sibling variants reactively in product.variants and products.value
      const scaledSiblings = [];
      if (resData.sibling_variants && Array.isArray(resData.sibling_variants)) {
        for (const sv of resData.sibling_variants) {
          const sib = (product.variants || []).find(v => v.id === sv.id);
          if (sib) {
            Object.assign(sib, sv);
            scaledSiblings.push(sib);
          }
          const pInStore = products.value.find(p => p.id === product.id);
          if (pInStore && pInStore !== product) {
            const pSib = (pInStore.variants || []).find(v => v.id === sv.id);
            if (pSib) Object.assign(pSib, sv);
          }
        }
      }

      if (scaledSiblings.length > 0) {
        const sibSummary = scaledSiblings.map(s => `${s.unit_size}: ₹${s.selling_price}`).join(', ');
        changesSummary.push(`⚖️ इतर वजने आपोआप: ${sibSummary}`);
      }

      // Save previous state for 1-click Undo (including all siblings)
      dukandarPreviousState.value = {
        ...beforeState,
        siblings: siblingBeforeStates
      };

      const pName = getLocalizedProductName(product, dukandarAiLang.value);
      let spokenText = '';
      if (scaledSiblings.length > 0) {
        const sibSpeak = scaledSiblings.map(s => `${s.unit_size} चा दर ₹${s.selling_price}`).join(', ');
        spokenText = dukandarAiLang.value === 'mr'
          ? `${pName} (${variant.unit_size}) चा दर ₹${patch.price} केला, आणि इतर वजने (${sibSpeak}) आपोआप अपडेट झाली.`
          : (dukandarAiLang.value === 'hi'
            ? `${pName} (${variant.unit_size}) का दाम ₹${patch.price} किया, और बाकी वजन (${sibSpeak}) अपने आप अपडेट हो गए।`
            : `Updated ${product.name} (${variant.unit_size}) to ₹${patch.price}, and scaled ${scaledSiblings.map(s => `${s.unit_size}: ₹${s.selling_price}`).join(', ')}.`);
      } else {
        spokenText = dukandarAiLang.value === 'mr'
          ? `${pName} (${variant.unit_size}) चे ${changesSummary.join(', ')} यशस्वीपणे अपडेट केले आहे.`
          : (dukandarAiLang.value === 'hi'
            ? `${pName} (${variant.unit_size}) का ${changesSummary.join(', ')} सफलतापूर्वक अपडेट कर दिया गया है।`
            : `Successfully updated ${product.name} (${variant.unit_size}): ${changesSummary.join(', ')}.`);
      }

      dukandarAiResult.value = {
        success: true,
        type: 'UPDATE',
        product,
        variant,
        beforeState,
        patchPayload,
        changesSummary,
        scaledSiblings,
        summary_text: spokenText
      };

      showToast(`✅ ${spokenText}`);
      speakAiSummary(spokenText, true);
    } else {
      const err = await res.json().catch(() => ({}));
      showToast(`❌ ${err.error || 'Update failed'}`);
    }
  } catch (err) {
    console.error('executeDukandarAiCommand error:', err);
    showToast('❌ नेटवर्क त्रुटी आली. कृपया पुन्हा प्रयत्न करा.');
  } finally {
    dukandarAiLoading.value = false;
  }
}

async function undoDukandarAiAction() {
  if (!dukandarPreviousState.value) return;
  const prev = dukandarPreviousState.value;
  try {
    const res = await fetch(`${API_BASE}/variants/${prev.variant_id}`, {
      method: 'PATCH',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${authToken.value}`
      },
      body: JSON.stringify({
        selling_price: prev.selling_price,
        mrp: prev.mrp,
        stock_quantity: prev.stock_quantity,
        is_available: prev.is_available,
        sync_proportional: false
      })
    });
    if (res.ok) {
      for (const p of products.value) {
        const v = (p.variants || []).find(vr => vr.id === prev.variant_id);
        if (v) {
          Object.assign(v, {
            selling_price: prev.selling_price,
            mrp: prev.mrp,
            stock_quantity: prev.stock_quantity,
            is_available: prev.is_available,
            is_in_stock: prev.is_available && prev.stock_quantity > 0
          });
          break;
        }
      }

      if (prev.siblings && prev.siblings.length > 0) {
        for (const sibPrev of prev.siblings) {
          await fetch(`${API_BASE}/variants/${sibPrev.variant_id}`, {
            method: 'PATCH',
            headers: {
              'Content-Type': 'application/json',
              'Authorization': `Bearer ${authToken.value}`
            },
            body: JSON.stringify({
              selling_price: sibPrev.selling_price,
              mrp: sibPrev.mrp,
              sync_proportional: false
            })
          }).catch(() => {});

          for (const p of products.value) {
            const sv = (p.variants || []).find(vr => vr.id === sibPrev.variant_id);
            if (sv) {
              Object.assign(sv, {
                selling_price: sibPrev.selling_price,
                mrp: sibPrev.mrp
              });
              break;
            }
          }
        }
      }

      dukandarPreviousState.value = null;
      dukandarAiResult.value = null;
      showToast('↩️ मागील बदल पूर्ववत केला (Changes reverted successfully)');
    }
  } catch (e) {
    console.error('Undo failed:', e);
  }
}

async function handleDukandarPosVoiceBill(text) {
  const payload = {
    text: text,
    language: dukandarAiLang.value || currentLang.value || 'mr'
  };
  const res = await fetch(`${API_BASE}/ai/parse-order`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload)
  });
  const data = await res.json();
  if (res.ok && data.success && data.items) {
    const matched = data.items.filter(it => it.match_status === 'matched');
    let addedCount = 0;
    for (const it of matched) {
      const prod = products.value.find(p => p.id === it.product_id);
      if (!prod) continue;
      const variant = (prod.variants || []).find(v => v.id === it.variant_id) || prod.variants[0];
      if (!variant) continue;
      
      addToPosCart(prod, variant, it.quantity || 1, it.unit_price || variant.selling_price);
      addedCount++;
    }
    dukandarAiResult.value = {
      success: true,
      type: 'POS_BILL',
      items: matched,
      summary_text: `${addedCount} सामान काऊंटर POS बिलामध्ये जोडले गेले!`
    };
    showToast(`🧾 ${addedCount} सामान थेट काऊंटर POS मध्ये जोडले!`);
    switchAdminTab('pos');
  }
}

async function handleDukandarVoiceCommand(rawText) {
  return executeDukandarAiCommand(rawText);
}

// --- ADMIN POS COUNTER BILLING METHODS ---
function updatePosTierRate() {
  if (!posSelectedProduct.value) return;
  const prod = posSelectedProduct.value;
  const isLoose = prod.is_loose || isLooseProduct(prod);
  const qtyOrWt = isLoose ? (parseFloat(posCustomWeight.value) || 1.0) : (parseInt(posQuantity.value) || 1);
  const tier = getMatchingTierInfo(prod, qtyOrWt);
  if (tier) {
    posCustomRate.value = tier.unit_price;
  } else {
    if (isLoose) {
      posCustomRate.value = getBasePerKgRate(prod);
    } else {
      const v = posSelectedVariant.value || (prod.variants && prod.variants[0]);
      if (v) posCustomRate.value = v.selling_price;
    }
  }
}

function onPosProductSelect(prod) {
  posSelectedProduct.value = prod;
  if (!prod) return;
  if (prod.is_loose || isLooseProduct(prod)) {
    posCustomWeight.value = 1.0;
    updatePosTierRate();
  } else {
    posSelectedVariant.value = prod.variants && prod.variants[0] ? prod.variants[0] : null;
    posQuantity.value = 1;
    updatePosTierRate();
  }
}

function addPosItem() {
  if (!posSelectedProduct.value) return;
  const prod = posSelectedProduct.value;
  const isLoose = prod.is_loose || isLooseProduct(prod);

  if (isLoose) {
    const wt = parseFloat(posCustomWeight.value) || 1.0;
    const rate = parseFloat(posCustomRate.value) || 35.0;
    const tier = getMatchingTierInfo(prod, wt);
    const unitSize = tier ? `${wt} kg (${tier.tier_label})` : `${wt} kg`;
    const subtotal = Math.round(wt * rate);
    const mrp = Math.round(subtotal * 1.15);

    counterOrder.value.items.push({
      is_custom_weight: true,
      custom_weight: wt,
      product_id: prod.id,
      variant_id: null,
      product_name: getLocalizedTitle(prod),
      unit_size: unitSize,
      unit_price: rate,
      quantity: 1,
      mrp: mrp,
      subtotal: subtotal,
      is_loose: true,
      tier_label: tier ? tier.tier_label : null
    });
  } else {
    const variant = posSelectedVariant.value || (prod.variants && prod.variants[0]);
    if (!variant) return;
    const qty = parseInt(posQuantity.value) || 1;
    const unitPrice = parseFloat(posCustomRate.value) || variant.selling_price;
    const tier = getMatchingTierInfo(prod, qty);
    const unitSize = tier ? `${variant.unit_size} (${tier.tier_label})` : variant.unit_size;
    const subtotal = Math.round(unitPrice * qty);
    const mrp = Math.round(variant.mrp * qty);

    counterOrder.value.items.push({
      is_custom_weight: false,
      product_id: prod.id,
      variant_id: variant.id,
      product_name: getLocalizedTitle(prod),
      unit_size: unitSize,
      unit_price: unitPrice,
      quantity: qty,
      mrp: mrp,
      subtotal: subtotal,
      is_loose: false,
      tier_label: tier ? tier.tier_label : null
    });
  }

  // Reset item picker
  posSelectedProduct.value = null;
  posSelectedVariant.value = null;
  posCustomWeight.value = 1.0;
  posQuantity.value = 1;
  posCustomRate.value = null;
  showToast(currentLang.value === 'en' ? 'Item added to bill!' : (currentLang.value === 'mr' ? 'सामान बिलात जोडले!' : 'सामान बिल में जोड़ा!'));
}

function removePosItem(index) {
  counterOrder.value.items.splice(index, 1);
}

const counterOrderTotals = computed(() => {
  let mrp = 0;
  let subtotal = 0;
  counterOrder.value.items.forEach(it => {
    mrp += it.mrp || it.subtotal;
    subtotal += it.subtotal;
  });
  const savings = mrp > subtotal ? mrp - subtotal : 0;
  return { mrp, subtotal, savings };
});

const posEstimatedCredit = computed(() => {
  let earned = 0.0;
  for (const it of counterOrder.value.items) {
    const isLoose = Boolean(it.is_loose);
    const rate = isLoose ? 0.025 : 0.005; // 2.5% on loose, 0.5% on packaged
    earned += (it.subtotal || 0) * rate;
  }
  return Math.round(earned * 100) / 100;
});

const posAppliedCredit = computed(() => {
  if (!posUseStoreCredit.value || !selectedPosCustomer.value) return 0;
  const avail = selectedPosCustomer.value.wallet_balance || 0;
  return Math.min(avail, counterOrderTotals.value.subtotal);
});

const posFinalPayable = computed(() => {
  return Math.max(0, counterOrderTotals.value.subtotal - posAppliedCredit.value).toFixed(2);
});

function selectRegisteredCustomerForPos(cust) {
  selectedPosCustomer.value = cust || null;
  posUseStoreCredit.value = false;
  if (!cust) {
    counterOrder.value.customer_name = '';
    counterOrder.value.customer_phone = '';
    counterOrder.value.customer_address = currentLang.value === 'en' ? 'Store Counter (In-Store Pickup)' : (currentLang.value === 'mr' ? 'दुकान काउंटर (In-Store Pickup)' : 'दुकान काउंटर (In-Store Pickup)');
    counterOrder.value.user_id = null;
    return;
  }
  counterOrder.value.customer_name = cust.name;
  counterOrder.value.customer_phone = cust.phone;
  counterOrder.value.customer_address = cust.address || (currentLang.value === 'en' ? 'Store Counter (In-Store Pickup)' : (currentLang.value === 'mr' ? 'दुकान काउंटर (In-Store Pickup)' : 'दुकान काउंटर (In-Store Pickup)'));
  counterOrder.value.user_id = cust.id;
  showToast(currentLang.value === 'en' ? `${cust.name} selected!` : (currentLang.value === 'mr' ? `${cust.name} निवडले!` : `${cust.name} चुना गया!`));
}

function onPosCustomerManualEdit() {
  if (selectedPosCustomer.value) {
    if (counterOrder.value.customer_name.trim() !== selectedPosCustomer.value.name ||
        counterOrder.value.customer_phone.trim() !== selectedPosCustomer.value.phone) {
      selectedPosCustomer.value = null;
      counterOrder.value.user_id = null;
      posUseStoreCredit.value = false;
    }
  }
}

async function submitCounterOrder(action = 'view') {
  if (counterOrder.value.items.length === 0) {
    showToast(currentLang.value === 'en' ? 'Add at least 1 item to bill!' : (currentLang.value === 'mr' ? 'बिलात किमान १ सामान जोडा!' : 'बिल में कम से कम 1 सामान जोड़ें!'), 'error');
    return;
  }
  if (!counterOrder.value.customer_name.trim()) {
    counterOrder.value.customer_name = currentLang.value === 'en' ? 'Counter Customer (Walk-in)' : (currentLang.value === 'mr' ? 'काउंटर ग्राहक (Walk-in)' : 'काउंटर ग्राहक (Walk-in)');
  }

  isPosSubmitting.value = true;
  try {
    // Only link user_id if selected customer matches the input phone and name
    const validUserId = (selectedPosCustomer.value && 
      selectedPosCustomer.value.id === counterOrder.value.user_id &&
      selectedPosCustomer.value.phone === counterOrder.value.customer_phone.trim()) 
      ? counterOrder.value.user_id 
      : null;

    const payload = {
      customer_name: counterOrder.value.customer_name.trim(),
      customer_phone: counterOrder.value.customer_phone.trim() || '9999999999',
      customer_address: counterOrder.value.customer_address.trim() || (currentLang.value === 'en' ? 'Store Counter (In-Store Pickup)' : (currentLang.value === 'mr' ? 'दुकान काउंटर (In-Store Pickup)' : 'दुकान काउंटर (In-Store Pickup)')),
      order_type: counterOrder.value.order_type,
      payment_method: counterOrder.value.payment_method,
      payment_status: counterOrder.value.payment_status,
      status: counterOrder.value.order_type === 'counter' ? 'Delivered' : 'Placed',
      user_id: validUserId,
      use_credit: posUseStoreCredit.value,
      items: counterOrder.value.items
    };

    const res = await fetch(`${API_BASE}/admin/orders/create`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${authToken.value}`
      },
      body: JSON.stringify(payload)
    });

    const data = await res.json();
    if (res.ok && data.order) {
      showToast(currentLang.value === 'en' ? `Bill #${data.order.order_number} created!` : (currentLang.value === 'mr' ? `बिल #${data.order.order_number} तयार झाले!` : `बिल #${data.order.order_number} बन गया!`));
      saveToAdminOrderVault([data.order]);
      adminOrders.value = [data.order, ...adminOrders.value.filter(o => o.order_number !== data.order.order_number)];
      // Reload admin orders & customers in background
      loadAdminOrders();
      loadAdminCustomers();

      const createdOrder = data.order;

      // Reset form
      counterOrder.value = {
        customer_name: '',
        customer_phone: '',
        customer_address: currentLang.value === 'en' ? 'Store Counter (In-Store Pickup)' : (currentLang.value === 'mr' ? 'दुकान काउंटर (In-Store Pickup)' : 'दुकान काउंटर (In-Store Pickup)'),
        order_type: 'counter',
        payment_method: 'Cash on Counter',
        payment_status: 'Paid',
        status: 'Delivered',
        user_id: null,
        items: []
      };
      selectedPosCustomer.value = null;
      posUseStoreCredit.value = false;

      if (action === 'print') {
        printSingleOrder(createdOrder);
      } else if (action === 'whatsapp') {
        shareOrderOnWhatsApp(createdOrder);
      } else {
        viewOrderReceipt(createdOrder);
      }
    } else {
      showToast(data.error || (currentLang.value === 'en' ? 'Error saving bill' : (currentLang.value === 'mr' ? 'बिल सेव्ह करताना त्रुटी आली' : 'बिल सहेजने में त्रुटि आई')), 'error');
    }
  } catch (err) {
    console.error('POS order error:', err);
    showToast(currentLang.value === 'en' ? 'Network error while saving bill' : (currentLang.value === 'mr' ? 'बिल सेव्ह करताना नेटवर्क त्रुटी आली' : 'बिल सहेजते समय नेटवर्क त्रुटि आई'), 'error');
  } finally {
    isPosSubmitting.value = false;
  }
}

// --- ADMIN CUSTOMERS DIRECTORY & KHATA AUDIT METHODS ---
async function loadAdminCustomers() {
  try {
    const res = await fetch(`${API_BASE}/admin/users`, {
      headers: { 'Authorization': `Bearer ${authToken.value}` }
    });
    if (res.ok) {
      adminCustomers.value = await res.json();
    }
  } catch (err) {
    console.error('Admin customers error:', err);
  }
}

const filteredAdminCustomers = computed(() => {
  if (!customerSearch.value.trim()) return adminCustomers.value;
  const q = customerSearch.value.toLowerCase().trim();
  return adminCustomers.value.filter(c =>
    (c.name && c.name.toLowerCase().includes(q)) ||
    (c.phone && c.phone.includes(q)) ||
    (c.email && c.email.toLowerCase().includes(q))
  );
});

const totalKhataOutstanding = computed(() => {
  return adminCustomers.value.reduce((acc, c) => acc + (c.unpaid_balance || 0), 0);
});

const khataCustomersCount = computed(() => {
  return adminCustomers.value.filter(c => (c.unpaid_balance || 0) > 0).length;
});

function openCustomerAudit(customer) {
  activeAuditedCustomer.value = customer;
}

function sendKhataReminderWhatsApp(customer) {
  if (!customer || !customer.phone) return;
  const rawPhone = customer.phone.replace(/\D/g, '');
  const cleanPhone = rawPhone.length === 10 ? `91${rawPhone}` : rawPhone;

  let text = '';
  if (currentLang.value === 'en') {
    text =
`🌾 *Komal Mart - Customer Khata & Due Statement*
━━━━━━━━━━━━━━━━━━━━
👤 *Customer Name:* ${customer.name}
📞 *Mobile:* ${customer.phone}
🧾 *Total Orders:* ${customer.total_orders}
💰 *Total Purchases:* ₹${customer.total_spent}
━━━━━━━━━━━━━━━━━━━━
⚠️ *Current Due Balance:* *₹${customer.unpaid_balance}*

Kindly clear your balance via UPI or cash at store:
📲 *UPI ID:* komalmart@upi
📍 *Komal Mart*, Main Bazaar, Station Road
Thank you! 🙏`;
  } else if (currentLang.value === 'hi') {
    text =
`🌾 *कोमल मार्ट (Komal Mart) - ग्राहक खाता व उधारी बहीखाता*
━━━━━━━━━━━━━━━━━━━━
👤 *ग्राहक नाम:* ${customer.name}
📞 *मोबाइल:* ${customer.phone}
🧾 *कुल ऑर्डर्स:* ${customer.total_orders}
💰 *कुल खरीदारी:* ₹${customer.total_spent}
━━━━━━━━━━━━━━━━━━━━
⚠️ *वर्तमान बकाया उधारी राशि:* *₹${customer.unpaid_balance}*

कृपया नीचे दिए UPI या दुकान पर आकर नकद भुगतान करें:
📲 *UPI ID:* komalmart@upi
📍 *कोमल मार्ट*, मेन बाज़ार, स्टेशन रोड
धन्यवाद! 🙏`;
  } else {
    text =
`🌾 *कोमल मार्ट (Komal Mart) - मासिक खाते व उधारी बहीखाता*
━━━━━━━━━━━━━━━━━━━━
👤 *ग्राहक नाव:* ${customer.name}
📞 *मोबाईल:* ${customer.phone}
🧾 *एकूण खरेदी ऑर्डर्स:* ${customer.total_orders}
💰 *एकूण खरेदी:* ₹${customer.total_spent}
━━━━━━━━━━━━━━━━━━━━
⚠️ *सध्याची बाकी उधारी रक्कम:* *₹${customer.unpaid_balance}*

कृपया सोयीनुसार खालील UPI ID किंवा दुकानात येऊन रोख भरणा करावा:
📲 *UPI ID:* komalmart@upi
📍 *कोमल मार्ट*, मेन बाजार, स्टेशन रोड
धन्यवाद! 🙏`;
  }

  const encoded = encodeURIComponent(text);
  window.open(`https://api.whatsapp.com/send?phone=${cleanPhone}&text=${encoded}`, '_blank');
}

// --- ADMIN KHATA BOOK (UDHAAR LEDGER) METHODS ---
async function loadAdminKhata() {
  khataLoading.value = true;
  try {
    const res = await fetch(`${API_BASE}/admin/khata`, {
      headers: { 'Authorization': `Bearer ${authToken.value}` }
    });
    if (res.ok) {
      const data = await res.json();
      adminKhataList.value = data.customers || [];
      adminKhataSummary.value = data.summary || { total_market_udhaar: 0, total_khata_customers: 0, total_recovered_month: 0 };
    }
  } catch (err) {
    console.error('Failed to load Khata:', err);
  } finally {
    khataLoading.value = false;
  }
}

const filteredKhataList = computed(() => {
  if (!khataSearch.value.trim()) return adminKhataList.value;
  const q = khataSearch.value.toLowerCase().trim();
  return adminKhataList.value.filter(c => 
    (c.customer_name && c.customer_name.toLowerCase().includes(q)) ||
    (c.customer_phone && c.customer_phone.includes(q))
  );
});

function openKhataPay(cust) {
  activeKhataCustomer.value = cust;
  khataPayForm.value = {
    amount: cust.net_balance_due > 0 ? cust.net_balance_due : '',
    payment_method: 'Cash',
    note: ''
  };
  showKhataPayModal.value = true;
}

async function submitKhataPayment() {
  if (!activeKhataCustomer.value) return;
  const amt = parseFloat(khataPayForm.value.amount);
  if (!amt || amt <= 0) {
    showToast(currentLang.value === 'en' ? 'Please enter a valid amount!' : (currentLang.value === 'mr' ? 'कृपया वैध रक्कम टाका!' : 'कृपया वैध राशि दर्ज करें!'), 'error');
    return;
  }
  isSubmittingKhataPay.value = true;
  try {
    const res = await fetch(`${API_BASE}/admin/khata/pay`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${authToken.value}`
      },
      body: JSON.stringify({
        customer_phone: activeKhataCustomer.value.customer_phone,
        customer_name: activeKhataCustomer.value.customer_name,
        amount: amt,
        payment_method: khataPayForm.value.payment_method,
        note: khataPayForm.value.note
      })
    });
    const data = await res.json();
    if (res.ok) {
      showToast(data.message || (currentLang.value === 'en' ? 'Payment recorded successfully!' : (currentLang.value === 'mr' ? 'पेमेंट यशस्वीरित्या नोंदवले गेले!' : 'भुगतान सफलतापूर्वक दर्ज किया गया!')));
      showKhataPayModal.value = false;
      loadAdminKhata();
      loadAdminOrders();
      loadAdminCustomers();
    } else {
      showToast(data.error || (currentLang.value === 'en' ? 'Could not record payment.' : (currentLang.value === 'mr' ? 'पेमेंट नोंदवता आले नाही' : 'भुगतान दर्ज नहीं किया जा सका।')), 'error');
    }
  } catch (e) {
    console.error(e);
    showToast(currentLang.value === 'en' ? 'Server error.' : (currentLang.value === 'mr' ? 'सर्व्हर त्रुटी.' : 'सर्वर त्रुटि।'), 'error');
  } finally {
    isSubmittingKhataPay.value = false;
  }
}

async function openKhataStatement(phone) {
  khataStatementLoading.value = true;
  showKhataStatementModal.value = true;
  try {
    const res = await fetch(`${API_BASE}/admin/khata/${phone}/statement`, {
      headers: { 'Authorization': `Bearer ${authToken.value}` }
    });
    if (res.ok) {
      activeKhataStatement.value = await res.json();
    }
  } catch (err) {
    console.error(err);
  } finally {
    khataStatementLoading.value = false;
  }
}

function sendKhataWhatsAppReminder(cust) {
  if (!cust || !cust.customer_phone) return;
  const billWord = currentLang.value === 'en' ? 'Bill' : (currentLang.value === 'mr' ? 'बिल' : 'बिल');
  const billsText = (cust.unpaid_orders || []).map((o, idx) => {
    return `${idx + 1}. ${billWord} #${o.order_number} (${o.created_at}) — ₹${o.final_amount}`;
  }).join('\n');

  let text = '';
  if (currentLang.value === 'en') {
    text = 
`🌾 *Komal Mart - Khata / Due Balance Reminder*
━━━━━━━━━━━━━━━━━━━━
Hello *${cust.customer_name}*,
Here is the summary of your outstanding balance at Komal Mart:

📋 *Pending Bills:*
${billsText}

🔴 *Total Balance Due (Net Due):* ₹${cust.net_balance_due}

Kindly pay the balance amount via UPI or at the counter:
💳 *UPI ID:* 9820088888@upi
📞 *Contact:* +91 98200 88888

🙏 Thank you! We appreciate your business.
━━━━━━━━━━━━━━━━━━━━
*Komal Mart*`;
  } else if (currentLang.value === 'hi') {
    text = 
`🌾 *कोमल मार्ट (Komal Mart) - खाता बही / उधारी बकाया स्मरणपत्र*
━━━━━━━━━━━━━━━━━━━━
नमस्ते *${cust.customer_name}* जी,
आपकी दुकान की बकाया उधारी का विवरण निम्नलिखित है:

📋 *बाकी रहे बिल:*
${billsText}

🔴 *कुल बकाया (Net Due):* ₹${cust.net_balance_due}

कृपया यह राशि नीचे दिए गए UPI या दुकान पर आकर जल्द से जल्द जमा करें:
💳 *UPI ID:* 9820088888@upi
📞 *संपर्क:* +91 98200 88888

🙏 धन्यवाद! आपका सहयोग बहुमूल्य है।
━━━━━━━━━━━━━━━━━━━━
*कोमल मार्ट (Komal Mart)*`;
  } else {
    text = 
`🌾 *कोमल मार्ट (Komal Mart) - खाते बही / उधारी बाकी स्मरणपत्र*
━━━━━━━━━━━━━━━━━━━━
नमस्कार *${cust.customer_name}* जी,
तुमच्या दुकानातील उधारीचे विवरण खालीलप्रमाणे आहे:

📋 *बाकी राहिलेली बिले:*
${billsText}

🔴 *एकूण येणे बाकी (Net Due):* ₹${cust.net_balance_due}

कृपया ही रक्कम खालील UPI किंवा दुकानात येऊन लवकरात लवकर जमा करावी:
💳 *UPI ID:* 9820088888@upi
📞 *संपर्क:* +91 98200 88888

🙏 धन्यवाद! आपले सहकार्य मोलाचे आहे.
━━━━━━━━━━━━━━━━━━━━
*कोमल मार्ट (Komal Mart)*`;
  }

  const cleanPhone = cust.customer_phone.replace(/\D/g, '');
  const url = `https://wa.me/91${cleanPhone}?text=${encodeURIComponent(text)}`;
  window.open(url, '_blank');
}

function openKhataPayForCustomer(c) {
  if (!c) return;
  openKhataPay({
    customer_phone: c.phone,
    customer_name: c.name || 'Customer',
    net_balance_due: c.unpaid_balance || 0
  });
}

// WhatsApp Order Status Dispatch & Customer UPI Confirmation State & Actions
const activeWhatsAppOrderMenuId = ref(null);

function toggleWhatsAppOrderMenu(orderId) {
  activeWhatsAppOrderMenuId.value = activeWhatsAppOrderMenuId.value === orderId ? null : orderId;
}

function sendAdminWhatsAppStatus(order, statusType) {
  if (!order || !order.customer_phone) {
    showToast(currentLang.value === 'en' ? 'Customer phone not available' : 'ग्राहक संपर्क क्रमांक उपलब्ध नाही', 'error');
    return;
  }
  let rawPhone = String(order.customer_phone).replace(/\D/g, '');
  if (rawPhone.length === 10) rawPhone = '91' + rawPhone;
  // If customer number is a dummy/test number, offer prompt so Roushan can test with real WhatsApp
  const isDummy = rawPhone.endsWith('9876543210') || rawPhone.endsWith('1234567890') || /^91(\d)\1{7,}/.test(rawPhone);
  if (isDummy) {
    const promptNumber = prompt(
      currentLang.value === 'en'
        ? `Customer phone (${order.customer_phone}) is a dummy/demo number.\nEnter your real 10-digit WhatsApp number to test live status dispatch:`
        : `हा ग्राहक क्रमांक (${order.customer_phone}) डमी नंबर आहे.\nWhatsApp मेसेज टेस्ट करण्यासाठी तुमचा खरा 10-अंकी मोबाईल नंबर टाका:`,
      '91'
    );
    if (!promptNumber) return;
    rawPhone = promptNumber.replace(/\D/g, '');
    if (rawPhone.length === 10) rawPhone = '91' + rawPhone;
  }

  const custName = order.customer_name || 'Customer';
  const orderNum = order.order_number || ('KM-' + order.id);
  const amount = Number(order.final_amount || 0).toFixed(2);
  const lang = currentLang.value || 'mr';

  // Base URL for 1-tap availability confirmation
  const checkLink = `${window.location.origin}/?order=${encodeURIComponent(orderNum)}&check=1`;

  const bal = Number(order.balance_due || (order.amount_paid > 0 ? (order.final_amount - order.amount_paid) : 0)).toFixed(2);
  const paid = Number(order.amount_paid || 0).toFixed(2);
  const isPart = order.payment_status === 'Partially Paid' && Number(bal) > 0;
  const balNoticeMr = isPart ? `\n\n💵 *पेमेंट सूचना:* आधी ₹${paid} जमा आहेत, उर्वरित *₹${bal}* कृपया डिलिव्हरी पार्टनरकडे रोख किंवा UPI ने द्यावे.` : '';
  const balNoticeEn = isPart ? `\n\n💵 *Payment Notice:* ₹${paid} was paid in advance. Please pay the remaining balance *₹${bal}* to our delivery partner via Cash or UPI.` : '';
  const balNoticeHi = isPart ? `\n\n💵 *भुगतान सूचना:* पहले ₹${paid} जमा हैं, बकाया *₹${bal}* कृपया डिलीवरी बॉय को नकद या UPI द्वारा दें।` : '';

  let msg = '';
  if (lang === 'mr') {
    if (statusType === 'confirmed') {
      msg = `नमस्ते ${custName} जी, कोमल मार्टकडून तुमचा ऑर्डर #${orderNum} (₹${amount}) कन्फर्म झाला आहे आणि सामान पॅक केले जात आहे. 📦\nलवकरच आपल्या पत्त्यावर पोहोचेल. धन्यवाद! 🙏\n- कोमल मार्ट (91420-52967)`;
    } else if (statusType === 'out_for_delivery') {
      msg = `नमस्ते ${custName} जी, तुमचा कोमल मार्ट ऑर्डर #${orderNum} (₹${amount}) डिलिव्हरीसाठी निघाला आहे! 🛵💨\n\nआमचा डिलिव्हरी पार्टनर पुढील 10-15 मिनिटांत आपल्या घरी पोहोचत आहे.${balNoticeMr}\n\n👉 *तुम्ही घरी उपलब्ध आहात का?*\nकृपया डिलिव्हरी कन्फर्म करण्यासाठी खालील लिंकवर १-टॅप करा:\n🔗 ${checkLink}\n\nमदत किंवा पत्त्यासाठी कॉल करा: 91420-52967\nधन्यवाद! 🙏\n- कोमल मार्ट, वडाळा`;
    } else if (statusType === 'delivered') {
      msg = `नमस्ते ${custName} जी, तुमचा ऑर्डर #${orderNum} यशस्वीरित्या पोहोचवला गेला आहे. ✅\nकोमल मार्टमधून खरेदी केल्याबद्दल मनःपूर्वक धन्यवाद! 🌾✨`;
    } else if (statusType === 'verified') {
      msg = `नमस्ते ${custName} जी, तुमच्या ऑर्डर #${orderNum} चे UPI पेमेंट (₹${amount}) यशस्वी पडताळले गेले आहे! ✅\nऑर्डर डिलिव्हरीसाठी तयार केली जात आहे. धन्यवाद! 🙏\n- कोमल मार्ट`;
    } else if (statusType === 'payment_failed') {
      msg = `नमस्ते ${custName} जी, तुम्ही ऑर्डर #${orderNum} (₹${amount}) साठी UPI पेमेंट केले होते, परंतु बँक सर्व्हरच्या समस्येमुळे ही रक्कम खात्यात जमा झाली नाही. ⚠️\n(पैसे कट झाले असल्यास २४ तासांत बँकेकडून आपोआप परत मिळतील).\n\nकाळजी करू नका! तुम्ही सामान घेताना रोख (Cash) किंवा डिलिव्हरी बॉयसमोर पुन्हा UPI करू शकता.\nसंपर्क: 91420-52967. धन्यवाद! 🙏\n- कोमल मार्ट`;
    } else {
      msg = `नमस्ते ${custName} जी, कोमल मार्ट ऑर्डर #${orderNum} चे अपडेट.`;
    }
  } else if (lang === 'en') {
    if (statusType === 'confirmed') {
      msg = `Hello ${custName}, your Komal Mart order #${orderNum} (₹${amount}) is confirmed and being packed! 📦\nIt will reach your doorstep shortly. Thank you! 🙏\n- Komal Mart (91420-52967)`;
    } else if (statusType === 'out_for_delivery') {
      msg = `Hello ${custName}, your Komal Mart order #${orderNum} (₹${amount}) is OUT FOR DELIVERY! 🛵💨\n\nOur delivery partner will reach your address in the next 10-15 minutes.${balNoticeEn}\n\n👉 *Are you available right now?*\nPlease tap below to confirm delivery availability:\n🔗 ${checkLink}\n\nFor directions or support, call: 91420-52967.\nThank you! 🙏\n- Komal Mart, Wadala`;
    } else if (statusType === 'delivered') {
      msg = `Hello ${custName}, your order #${orderNum} has been successfully delivered! ✅\nThank you for shopping with Komal Mart! 🌾✨`;
    } else if (statusType === 'verified') {
      msg = `Hello ${custName}, your UPI payment of ₹${amount} for order #${orderNum} has been verified successfully! ✅\nYour order is being prepared for dispatch. Thank you! 🙏\n- Komal Mart`;
    } else if (statusType === 'payment_failed') {
      msg = `Hello ${custName}, we noticed your UPI payment of ₹${amount} for order #${orderNum} was not received due to bank server issues. ⚠️\n(If debited, your bank will refund automatically within 24 hours).\n\nNo worries! You can pay Cash on Delivery or UPI directly to our delivery boy upon arrival.\nAssistance: 91420-52967. Thank you! 🙏\n- Komal Mart`;
    } else {
      msg = `Hello ${custName}, update for your Komal Mart order #${orderNum}.`;
    }
  } else {
    // Default: Hindi
    if (statusType === 'confirmed') {
      msg = `नमस्ते ${custName} जी, कोमल मार्ट से आपका ऑर्डर #${orderNum} (₹${amount}) कन्फर्म हो गया है और सामान पैक किया जा रहा है। 📦\nजल्द ही आपके पते पर पहुंचेगा। धन्यवाद! 🙏\n- कोमल मार्ट (91420-52967)`;
    } else if (statusType === 'out_for_delivery') {
      msg = `नमस्ते ${custName} जी, आपका कोमल मार्ट ऑर्डर #${orderNum} (₹${amount}) डिलीवरी के लिए निकल चुका है! 🛵💨\n\nहमारा डिलीवरी पार्टनर अगले 10-15 मिनट में आपके पते पर पहुँच रहा है।${balNoticeHi}\n\n👉 *क्या आप घर पर उपलब्ध हैं?*\nकृपया डिलीवरी कन्फर्म करने के लिए नीचे दिए गए लिंक पर टैप करें:\n🔗 ${checkLink}\n\nसहायता या निर्देश के लिए कॉल करें: 91420-52967\nधन्यवाद! 🙏\n- कोमल मार्ट, वडाला`;
    } else if (statusType === 'delivered') {
      msg = `नमस्ते ${custName} जी, आपका ऑर्डर #${orderNum} सफलतापूर्वक डिलीवर हो चुका है। ✅\nकोमल मार्ट से खरीदारी करने के लिए आपका बहुत-बहुत धन्यवाद! 🌾✨`;
    } else if (statusType === 'verified') {
      msg = `नमस्ते ${custName} जी, आपके ऑर्डर #${orderNum} का UPI पेमेंट (₹${amount}) सफलतापूर्वक वेरिफाई हो गया है! ✅\nऑर्डर डिलीवरी के लिए तैयार किया जा रहा है। धन्यवाद! 🙏\n- कोमल मार्ट`;
    } else if (statusType === 'payment_failed') {
      msg = `नमस्ते ${custName} जी, आपने ऑर्डर #${orderNum} (₹${amount}) के लिए UPI पेमेंट मार्क किया था, लेकिन बैंक सर्वर में समस्या के कारण यह राशि हमारे खाते में प्राप्त नहीं हुई है (यदि आपके बैंक खाते से पैसे कटे हैं तो 24 घंटे में बैंक द्वारा स्वतः वापस रिफंड हो जाएंगे)। ⚠️\n\nचिंता न करें! आप सामान प्राप्त करते समय नकद (Cash on Delivery) दे सकते हैं या डिलीवरी बॉय के सामने दोबारा UPI कर सकते हैं।\nसहायता या पूछताछ के लिए कॉल करें: 91420-52967\nधन्यवाद! 🙏\n- कोमल मार्ट`;
    } else {
      msg = `नमस्ते ${custName} जी, आपके कोमल मार्ट ऑर्डर #${orderNum} का स्टेटस अपडेट: ठीक है।`;
    }
  }

  const url = `https://wa.me/${rawPhone}?text=${encodeURIComponent(msg)}`;
  window.open(url, '_blank');
}

function sendCustomerUpiProofWhatsApp(order) {
  if (!order) return;
  const storePhone = '919142052967';
  const orderNum = order.order_number || ('KM-' + order.id);
  const amount = Number(order.final_amount || 0).toFixed(2);
  const name = order.customer_name || currentUser.value?.name || 'Customer';
  const phone = order.customer_phone || currentUser.value?.phone || '';

  const msg = `नमस्ते कोमल मार्ट! 🙏\nमैंने ऑर्डर #${orderNum} के लिए ₹${amount} का UPI पेमेंट कर दिया है।\n\n👤 ग्राहक: ${name}\n📱 मोबाइल: ${phone}\n💰 भुगतान राशि: ₹${amount}\n\nकृपया पेमेंट वेरिफाई करके मेरा ऑर्डर कन्फर्म करें। धन्यवाद!`;

  const url = `https://wa.me/${storePhone}?text=${encodeURIComponent(msg)}`;
  window.open(url, '_blank');
}

function switchAdminTab(tabName) {
  adminActiveTab.value = tabName;
  if (tabName === 'pos' || tabName === 'customers') {
    loadAdminCustomers();
  } else if (tabName === 'khata') {
    loadAdminKhata();
  } else if (tabName === 'orders') {
    loadAdminOrders();
  } else if (tabName === 'zreport') {
    loadDailyZReport();
  } else if (tabName === 'restock') {
    loadRestockAlerts();
  } else if (tabName === 'support') {
    loadAdminSupportTickets();
  } else if (tabName === 'storefront') {
    fetchProducts();
  }
  nextTick(() => {
    if (tabName !== 'storefront') {
      const anchor = document.getElementById('admin-tab-content-anchor');
      if (anchor) {
        anchor.scrollIntoView({ behavior: 'smooth', block: 'start' });
      }
    } else {
      window.scrollTo({ top: 0, behavior: 'smooth' });
    }
  });
}

async function loadAdminSupportTickets() {
  if (!authToken.value) return;
  adminSupportLoading.value = true;
  try {
    const res = await fetch(`${API_BASE}/admin/support/tickets`, {
      headers: { 'Authorization': `Bearer ${authToken.value}` }
    });
    if (res.ok) {
      const data = await res.json();
      adminSupportTickets.value = data.tickets || [];
      adminOpenComplaintsCount.value = data.open_complaints_count || 0;
    }
  } catch (err) {
    console.error('Error loading admin support tickets:', err);
  } finally {
    adminSupportLoading.value = false;
  }
}

async function updateTicketByAdmin(tkt) {
  if (!tkt || !tkt.id) return;
  try {
    const res = await fetch(`${API_BASE}/admin/support/tickets/${tkt.id}/status`, {
      method: 'PATCH',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${authToken.value}`
      },
      body: JSON.stringify({
        status: tkt.status,
        admin_notes: tkt.admin_notes || ''
      })
    });
    const data = await res.json();
    if (res.ok) {
      showToast(data.message || 'Status updated successfully!');
      loadAdminSupportTickets();
    } else {
      alert(data.error || 'Failed to update ticket');
    }
  } catch (err) {
    console.error('Error updating ticket:', err);
    alert('Network error while updating status');
  }
}

async function loadCustomerKhata() {
  if (!authToken.value) return;
  customerKhataLoading.value = true;
  try {
    const res = await fetch(`${API_BASE}/customer/khata`, {
      headers: { 'Authorization': `Bearer ${authToken.value}` }
    });
    if (res.ok) {
      customerKhataData.value = await res.json();
    }
  } catch (e) {
    console.error(e);
  } finally {
    customerKhataLoading.value = false;
  }
}

async function fetchSmsBalance() {
  if (!authToken.value || currentUser.value?.role !== 'admin') return;
  try {
    const res = await fetch(`${API_BASE}/admin/sms-balance`, {
      headers: { 'Authorization': `Bearer ${authToken.value}` }
    });
    if (res.ok) {
      smsBalanceInfo.value = await res.json();
    }
  } catch (e) {
    console.error('Failed to fetch SMS balance', e);
  }
}

// --- DUAL-TIER ORDER VAULT & DISASTER RECOVERY (OFFLINE & BROWSER IMMUTABILITY) ---
function saveToAdminOrderVault(ordersList) {
  try {
    let vault = {};
    const existingStr = localStorage.getItem('komal_admin_order_vault');
    if (existingStr) {
      vault = JSON.parse(existingStr);
    }
    for (const ord of ordersList) {
      if (ord.order_number) {
        vault[ord.order_number] = ord;
      }
    }
    localStorage.setItem('komal_admin_order_vault', JSON.stringify(vault));
  } catch (e) {
    console.warn('Admin vault save error:', e);
  }
}

function getAdminOrderVault() {
  try {
    const existingStr = localStorage.getItem('komal_admin_order_vault');
    if (!existingStr) return [];
    const vault = JSON.parse(existingStr);
    return Object.values(vault);
  } catch (e) {
    return [];
  }
}

function saveToCustomerOrderVault(ordersList) {
  try {
    let vault = {};
    const existingStr = localStorage.getItem('komal_customer_order_vault');
    if (existingStr) {
      vault = JSON.parse(existingStr);
    }
    for (const ord of ordersList) {
      if (ord.order_number) {
        vault[ord.order_number] = ord;
      }
    }
    localStorage.setItem('komal_customer_order_vault', JSON.stringify(vault));
  } catch (e) {
    console.warn('Customer vault save error:', e);
  }
}

function getCustomerOrderVault() {
  try {
    const existingStr = localStorage.getItem('komal_customer_order_vault');
    if (!existingStr) return [];
    const vault = JSON.parse(existingStr);
    return Object.values(vault);
  } catch (e) {
    return [];
  }
}

function downloadAdminOrderVault() {
  const vaulted = getAdminOrderVault();
  const listToExport = vaulted.length > 0 ? vaulted : adminOrders.value;
  if (!listToExport || listToExport.length === 0) {
    showToast(currentLang.value === 'en' ? 'No orders in vault to export' : 'ऑर्डर सापडले नाहीत', 'warning');
    return;
  }
  const blob = new Blob([JSON.stringify(listToExport, null, 2)], { type: 'application/json' });
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = `komal_mart_orders_vault_backup_${new Date().toISOString().slice(0, 10)}.json`;
  a.click();
  URL.revokeObjectURL(url);
  showToast(currentLang.value === 'en' ? '🛡️ Complete Order Vault exported safely!' : '🛡️ संपूर्ण ऑर्डर बॅकअप फाईल सेव्ह झाली!');
}

async function restoreAdminOrderVault() {
  const vaulted = getAdminOrderVault();
  const listToSync = vaulted.length > 0 ? vaulted : adminOrders.value;
  if (!listToSync || listToSync.length === 0) {
    showToast(currentLang.value === 'en' ? 'No orders found in browser vault to sync.' : 'ब्राउझर व्हॉल्टमध्ये कोणतेही ऑर्डर्स नाहीत.', 'warning');
    return;
  }
  const confirmMsg = currentLang.value === 'en'
    ? `Sync ${listToSync.length} orders from your offline browser vault to the cloud database? Any missing orders will be safely restored.`
    : (currentLang.value === 'mr'
      ? `तुमच्या ऑफलाइन व्हॉल्टमधील ${listToSync.length} ऑर्डर्स क्लाउड डेटाबेसमध्ये रिस्टोअर करायचे का?`
      : `क्या आप ऑफलाइन वॉल्ट के ${listToSync.length} ऑर्डर्स क्लाउड डेटाबेस में पुनर्स्थापित (Restore) करना चाहते हैं?`);
  if (!confirm(confirmMsg)) return;

  try {
    const res = await fetch(`${API_BASE}/admin/orders/restore-vault`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${authToken.value}`
      },
      body: JSON.stringify({ orders: listToSync })
    });
    const d = await res.json();
    if (res.ok) {
      showToast(`✅ ${d.message}`);
      loadAdminOrders();
    } else {
      showToast(d.error || 'Failed to sync vault', 'error');
    }
  } catch (e) {
    showToast('Network error syncing vault', 'error');
  }
}

async function loadAdminOrders(shouldSwitchTab = false) {
  if (shouldSwitchTab) {
    adminActiveTab.value = 'orders';
  }
  // Only show blocking loading state if no cached orders exist
  if (adminOrders.value.length === 0) {
    isAdminOrdersLoading.value = true;
  } else {
    isAdminOrdersSyncing.value = true;
  }
  fetchSmsBalance();
  try {
    const res = await fetch(`${API_BASE}/admin/orders`, {
      headers: { 'Authorization': `Bearer ${authToken.value}` }
    });
    if (res.ok) {
      const freshOrders = await res.json();
      adminOrders.value = freshOrders;
      try {
        localStorage.setItem('komal_cached_admin_orders', JSON.stringify(freshOrders));
        saveToAdminOrderVault(freshOrders);
      } catch (cacheErr) {
        console.warn('Vault cache update error:', cacheErr);
      }
    }
  } catch (err) {
    console.error('Admin orders fetch error:', err);
    // Offline resilience: load from device vault if empty
    if (adminOrders.value.length === 0) {
      const vaulted = getAdminOrderVault();
      if (vaulted.length > 0) {
        adminOrders.value = vaulted;
        showToast('🛡️ Offline Mode: Orders loaded from Device Vault', 'warning');
      }
    }
  } finally {
    isAdminOrdersLoading.value = false;
    isAdminOrdersSyncing.value = false;
  }
}

const unpaidAdminOrders = computed(() => {
  return adminOrders.value.filter(o => o.payment_status !== 'Paid');
});

const pendingVerificationAdminOrders = computed(() => {
  return adminOrders.value.filter(o => o.payment_status === 'Pending Verification');
});

const paidAdminOrders = computed(() => {
  return adminOrders.value.filter(o => o.payment_status === 'Paid');
});

const codAdminOrders = computed(() => {
  return adminOrders.value.filter(o => o.payment_method && o.payment_method.toLowerCase().includes('cash'));
});

const upiAdminOrders = computed(() => {
  return adminOrders.value.filter(o => o.payment_method && o.payment_method.toLowerCase().includes('upi'));
});

const adminOrderSearch = ref('');

function getSoundboxPaise(amount) {
  if (amount == null) return '00';
  const parts = String(amount).split('.');
  if (parts.length > 1) {
    return parts[1].padEnd(2, '0').slice(0, 2);
  }
  return '00';
}

function isUpiMethod(method) {
  const m = (method || '').toLowerCase();
  return m.includes('upi') || m.includes('qr') || m.includes('paytm') || m.includes('gpay') || m.includes('phonepe') || m.includes('online');
}

const displayedAdminOrders = computed(() => {
  let list = adminOrders.value;
  if (adminOrderFilter.value === 'pending') list = pendingVerificationAdminOrders.value;
  else if (adminOrderFilter.value === 'unpaid') list = unpaidAdminOrders.value;
  else if (adminOrderFilter.value === 'paid') list = paidAdminOrders.value;
  else if (adminOrderFilter.value === 'cod') list = codAdminOrders.value;
  else if (adminOrderFilter.value === 'upi') list = upiAdminOrders.value;

  const q = adminOrderSearch.value.trim().toLowerCase();
  if (!q) return list;

  const cleanPaise = q.startsWith('.') ? q.slice(1) : q;
  return list.filter(o => {
    const paise = getSoundboxPaise(o.final_amount);
    return (
      (o.order_number && o.order_number.toLowerCase().includes(q)) ||
      (o.customer_name && o.customer_name.toLowerCase().includes(q)) ||
      (o.customer_phone && o.customer_phone.includes(q)) ||
      (cleanPaise.length >= 2 && paise === cleanPaise) ||
      String(o.final_amount).includes(q)
    );
  });
});

// Admin Batch Selection & Multi-Slip Print Helpers
const selectedBatchOrders = computed(() => {
  return adminOrders.value.filter(o => selectedAdminOrderIds.value.includes(o.id));
});

const isAllDisplayedOrdersSelected = computed(() => {
  return displayedAdminOrders.value.length > 0 &&
    displayedAdminOrders.value.every(o => selectedAdminOrderIds.value.includes(o.id));
});

function toggleSelectAllOrders() {
  if (isAllDisplayedOrdersSelected.value) {
    selectedAdminOrderIds.value = [];
  } else {
    selectedAdminOrderIds.value = displayedAdminOrders.value.map(o => o.id);
  }
}

const resolvedBatchLayout = computed(() => {
  if (batchPrintLayout.value === 'auto') {
    return selectedBatchOrders.value.length <= 2 ? 'two' : 'four';
  }
  return batchPrintLayout.value;
});

const resolvedBatchLayoutClass = computed(() => {
  return resolvedBatchLayout.value === 'two' ? 'layout-2-slips' : 'layout-4-slips';
});

const chunkedBatchOrders = computed(() => {
  const chunkSize = resolvedBatchLayout.value === 'two' ? 2 : 4;
  const chunks = [];
  for (let i = 0; i < selectedBatchOrders.value.length; i += chunkSize) {
    chunks.push(selectedBatchOrders.value.slice(i, i + chunkSize));
  }
  return chunks;
});

function openBatchPrintModal() {
  if (selectedAdminOrderIds.value.length === 0) {
    showToast(currentLang.value === 'en' ? 'Please select at least 1 order for batch printing.' : (currentLang.value === 'mr' ? 'कृपया प्रिंटसाठी आधी किमान १ ऑर्डर निवडा.' : 'कृपया प्रिंट के लिए पहले कम से कम 1 ऑर्डर चुनें।'));
    return;
  }
  showBatchPrintModal.value = true;
}

function printSingleOrder(order) {
  lastOrderReceipt.value = order;
  nextTick(() => {
    window.print();
  });
}

function triggerBatchPrint() {
  window.print();
}

async function markOrderAsPaid(order) {
  try {
    const res = await fetch(`${API_BASE}/admin/orders/${order.id}/status`, {
      method: 'PATCH',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${authToken.value}`
      },
      body: JSON.stringify({
        payment_status: 'Paid'
      })
    });
    if (res.ok) {
      order.payment_status = 'Paid';
      showToast(currentLang.value === 'en' ? `✅ Order #${order.order_number} marked as Paid!` : (currentLang.value === 'mr' ? `✅ ऑर्डर #${order.order_number} चुकता (Paid) नोंदवले गेले!` : `✅ ऑर्डर #${order.order_number} चुकता (Paid) दर्ज कर दिया गया!`));
    } else {
      const err = await res.json();
      alert(err.error || 'Error updating order status');
    }
  } catch (err) {
    console.error('Status update error:', err);
  }
}

async function deleteAdminProduct(productId, productName) {
  const confirmMsg = currentLang.value === 'en' ? `Are you sure you want to remove '${productName}' from store?` : (currentLang.value === 'mr' ? `तुम्हाला नक्की '${productName}' दुकानातून काढून टाकायचे आहे का?` : `क्या आप सच में '${productName}' को दुकान से हटाना चाहते हैं?`);
  if (confirm(confirmMsg)) {
    try {
      const res = await fetch(`${API_BASE}/products/${productId}`, {
        method: 'DELETE',
        headers: { 'Authorization': `Bearer ${authToken.value}` }
      });
      if (res.ok) {
        showToast(currentLang.value === 'en' ? `🗑️ '${productName}' removed from store!` : (currentLang.value === 'mr' ? `🗑️ '${productName}' दुकानातून काढून टाकले!` : `🗑️ '${productName}' दुकान से हटा दिया गया!`));
        fetchProducts();
      } else {
        const err = await res.json();
        alert(err.error || 'Error removing product');
      }
    } catch (err) {
      console.error('Delete product error:', err);
    }
  }
}

function toggleSelectAllProducts(e) {
  if (e.target.checked) {
    selectedAdminProductIds.value = filteredAdminProducts.value.map(p => p.id);
  } else {
    selectedAdminProductIds.value = [];
  }
}

function toggleProductSelection(productId) {
  const idx = selectedAdminProductIds.value.indexOf(productId);
  if (idx > -1) {
    selectedAdminProductIds.value.splice(idx, 1);
  } else {
    selectedAdminProductIds.value.push(productId);
  }
}

async function bulkDeleteSelectedProducts() {
  const count = selectedAdminProductIds.value.length;
  if (count === 0) return;
  const confirmMsg = currentLang.value === 'en'
    ? `Are you sure you want to permanently delete ${count} selected products?`
    : (currentLang.value === 'mr'
      ? `तुम्हाला नक्की ${count} निवडलेले सामान कायमचे हटवायचे आहे का?`
      : `क्या आप सच में चुने गए ${count} सामान को दुकान से हटाना चाहते हैं?`);

  if (!confirm(confirmMsg)) return;

  try {
    const res = await fetch(`${API_BASE}/products/bulk-delete`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${authToken.value}`
      },
      body: JSON.stringify({ product_ids: selectedAdminProductIds.value })
    });
    if (res.ok) {
      showToast(currentLang.value === 'en' ? `🗑️ Successfully deleted ${count} products!` : `🗑️ ${count} सामान दुकानातून यशस्वीरित्या हटवले!`, 'success');
      selectedAdminProductIds.value = [];
      fetchProducts();
    } else {
      const err = await res.json();
      showToast(err.error || 'Failed to delete products', 'error');
    }
  } catch (err) {
    console.error('Bulk delete error:', err);
    showToast('Network error during bulk delete', 'error');
  }
}

async function updateAdminOrderStatus(order) {
  try {
    const res = await fetch(`${API_BASE}/admin/orders/${order.id}/status`, {
      method: 'PATCH',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${authToken.value}`
      },
      body: JSON.stringify({
        status: order.status,
        payment_status: order.payment_status
      })
    });
    if (res.ok) {
      showToast(currentLang.value === 'en' ? `✅ Order #${order.order_number} status updated!` : (currentLang.value === 'mr' ? `✅ ऑर्डर #${order.order_number} स्टेटस अपडेट झाले!` : `✅ ऑर्डर #${order.order_number} का स्टेटस अपडेट हुआ!`));
    }
  } catch (err) {
    console.error('Status update error:', err);
  }
}

async function submitNewProduct() {
  try {
    const images = [];
    if (newProductForm.value.image_front && newProductForm.value.image_front.trim()) {
      images.push(newProductForm.value.image_front.trim());
    }
    if (newProductForm.value.image_back && newProductForm.value.image_back.trim()) {
      images.push(newProductForm.value.image_back.trim());
    }
    if (newProductForm.value.image_pack && newProductForm.value.image_pack.trim()) {
      images.push(newProductForm.value.image_pack.trim());
    }
    if (images.length === 0) {
      images.push('/products/chakki-atta.jpg');
    }

    const payload = {
      category_id: newProductForm.value.is_new_category ? null : newProductForm.value.category_id,
      new_category_name: newProductForm.value.is_new_category ? newProductForm.value.new_category_name.trim() : null,
      new_category_name_hi: newProductForm.value.is_new_category ? newProductForm.value.new_category_name_hi.trim() : null,
      name: newProductForm.value.name,
      name_hi: newProductForm.value.name_hi,
      brand: newProductForm.value.brand,
      is_loose: newProductForm.value.is_loose,
      description: newProductForm.value.description,
      images: images,
      image_url: images[0],
      variants: [
        {
          unit_size: newProductForm.value.unit_size,
          mrp: newProductForm.value.mrp,
          selling_price: newProductForm.value.selling_price,
          stock_quantity: 50
        }
      ]
    };

    const res = await fetch(`${API_BASE}/products`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${authToken.value}`
      },
      body: JSON.stringify(payload)
    });

    if (res.ok) {
      showToast(currentLang.value === 'en' ? `✅ New item '${newProductForm.value.name}' added successfully!` : (currentLang.value === 'mr' ? `✅ नवीन सामान '${newProductForm.value.name}' यशस्वीरीत्या जोडले!` : `✅ नया सामान '${newProductForm.value.name}' सफलतापूर्वक जोड़ा गया!`));
      showAddProductModal.value = false;
      newProductForm.value.name = '';
      newProductForm.value.name_hi = '';
      newProductForm.value.is_new_category = false;
      newProductForm.value.new_category_name = '';
      newProductForm.value.new_category_name_hi = '';
      newProductForm.value.image_front = '/products/chakki-atta.jpg';
      newProductForm.value.image_back = '';
      newProductForm.value.image_pack = '';
      await fetchCategories();
      await fetchProducts();
    }
  } catch (err) {
    console.error('Add product error:', err);
  }
}

async function confirmResetSeed() {
  const confirmMsg = currentLang.value === 'en' 
    ? 'Are you sure you want to reset the store catalog to default items?' 
    : (currentLang.value === 'mr' ? 'तुम्हाला नक्की सर्व स्टोअर डीफॉल्ट किराणा मालावर रीसेट करायचे आहे का?' : 'क्या आप सच में पूरे स्टोर को डिफ़ॉल्ट देसी किराना सामान पर रीसेट करना चाहते हैं?');
  if (confirm(confirmMsg)) {
    try {
      const res = await fetch(`${API_BASE}/reset-seed`, {
        method: 'POST',
        headers: { 'Authorization': `Bearer ${authToken.value}` }
      });
      if (res.ok) {
        showToast(currentLang.value === 'en' ? '🔄 Store reset successfully!' : (currentLang.value === 'mr' ? '🔄 दुकान यशस्वीरीत्या रीसेट झाले!' : '🔄 स्टोर सफलतापूर्वक रीसेट हो गया!'));
        fetchCategories();
        fetchProducts();
      }
    } catch (err) {
      console.error('Reset error:', err);
    }
  }
}

function getCategoryEmoji(slug) {
  const map = {
    'dals-pulses': '🥣',
    'atta-flours': '🌾',
    'rice-grains': '🍚',
    'beans-legumes': '🫘',
    'tea-beverages': '☕',
    'oral-care': '🪥',
    'oils-ghee': '🫗',
    'spices-masalas': '🌶️',
    'household-cleaning': '🧼',
    'dry-fruits-nuts': '🥜',
    'sugar-jaggery': '🍯',
    'biscuits-bakery': '🍪',
    'cold-drinks': '🥤',
    'pooja-samagri': '🪔'
  };
  return map[slug] || '📦';
}

// --- RESTOCK ALERTS & HOT BACKUPS ACTION METHODS ---

function openNotifyModal(prod, variant) {
  if (!prod) return;
  notifyProduct.value = prod;
  notifyVariant.value = variant || null;
  notifyMessage.value = '';
  notifySuccess.value = false;
  notifyForm.value = {
    customer_name: currentUser.value ? currentUser.value.name : '',
    customer_phone: currentUser.value ? currentUser.value.phone : ''
  };
  showNotifyModal.value = true;
}

async function submitNotifyMe() {
  if (!notifyProduct.value) return;
  const phone = (notifyForm.value.customer_phone || '').trim();
  if (!phone || phone.length !== 10) {
    notifyMessage.value = currentLang.value === 'en' ? 'Please enter a valid 10-digit mobile number' : (currentLang.value === 'mr' ? 'कृपया १० अंकांचा वैध मोबाईल नंबर टाका' : 'कृपया १० अंकों का वैध मोबाइल नंबर लिखें');
    notifySuccess.value = false;
    return;
  }
  notifySubmitting.value = true;
  notifyMessage.value = '';
  try {
    const res = await fetch(`${API_BASE}/products/${notifyProduct.value.id}/notify-me`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        ...(authToken.value ? { 'Authorization': `Bearer ${authToken.value}` } : {})
      },
      body: JSON.stringify({
        customer_name: notifyForm.value.customer_name.trim(),
        customer_phone: phone,
        variant_id: notifyVariant.value ? notifyVariant.value.id : null
      })
    });
    const data = await res.json();
    if (res.ok) {
      notifySuccess.value = true;
      notifyMessage.value = data.message || t('notify_me_success');
      showToast(notifyMessage.value);
    } else {
      notifySuccess.value = false;
      notifyMessage.value = data.error || 'Failed to register notification alert.';
    }
  } catch (err) {
    notifySuccess.value = false;
    notifyMessage.value = 'Network error. Please try again.';
  } finally {
    notifySubmitting.value = false;
  }
}

async function loadRestockAlerts() {
  if (!authToken.value) return;
  try {
    const res = await fetch(`${API_BASE}/admin/restock-alerts`, {
      headers: { 'Authorization': `Bearer ${authToken.value}` }
    });
    if (res.ok) {
      const data = await res.json();
      restockAlertsList.value = data.alerts || [];
      pendingRestockCount.value = data.pending_count || 0;
    }
  } catch (err) {
    console.error('Failed to load restock alerts:', err);
  }
}

async function downloadDatabaseBackup() {
  if (!authToken.value) {
    showToast('Admin login required');
    return;
  }
  try {
    showToast(currentLang.value === 'en' ? '⏳ Generating safe hot database backup...' : (currentLang.value === 'mr' ? '⏳ सुरक्षित हॉट बॅकअप तयार होत आहे...' : '⏳ सुरक्षित हॉट बैकअप तैयार हो रहा है...'));
    const res = await fetch(`${API_BASE}/admin/backup/download?compress=true`, {
      headers: { 'Authorization': `Bearer ${authToken.value}` }
    });
    if (!res.ok) {
      const err = await res.json().catch(() => ({}));
      showToast(err.error || 'Backup download failed');
      return;
    }
    const blob = await res.blob();
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    const disposition = res.headers.get('Content-Disposition');
    let filename = `kirana_backup_${new Date().toISOString().replace(/[-:T]/g, '_').slice(0, 15)}.db.gz`;
    if (disposition && disposition.indexOf('filename=') !== -1) {
      const matches = /filename[^;=\n]*=((['"]).*?\2|[^;\n]*)/.exec(disposition);
      if (matches != null && matches[1]) {
        filename = matches[1].replace(/['"]/g, '');
      }
    }
    a.download = filename;
    document.body.appendChild(a);
    a.click();
    window.URL.revokeObjectURL(url);
    document.body.removeChild(a);
    showToast(currentLang.value === 'en' ? '✅ Database snapshot downloaded!' : (currentLang.value === 'mr' ? '✅ डेटाबेस बॅकअप डाऊनलोड झाला!' : '✅ डेटाबेस बैकअप डाउनलोड हो गया!'));
  } catch (err) {
    console.error('Backup download error:', err);
    showToast('Failed to download database backup');
  }
}

// --- 1-CLICK DOWNLOADABLE PDF BILL & DAILY Z-REPORT METHODS ---

async function downloadOrderPdf(order) {
  if (!order) return;
  lastOrderReceipt.value = order;
  await nextTick();

  setTimeout(async () => {
    const el = document.getElementById('printable-parcha-slip');
    if (!el) {
      showToast(currentLang.value === 'en' ? 'Receipt is loading, please try again...' : (currentLang.value === 'mr' ? 'पावती लोड होत आहे, पुन्हा प्रयत्न करा...' : 'पर्चा लोड हो रहा है, पुन: प्रयास करें...'), 'warning');
      return;
    }
    try {
      showToast(currentLang.value === 'en' ? '⏳ Generating PDF...' : (currentLang.value === 'mr' ? '⏳ PDF तयार होत आहे...' : '⏳ PDF तैयार हो रही है...'));
      const html2pdf = (await import('html2pdf.js')).default;
      const opt = {
        margin: [6, 6, 6, 6],
        filename: `Komal_Mart_Bill_${order.order_number}.pdf`,
        image: { type: 'jpeg', quality: 0.98 },
        html2canvas: { scale: 2, useCORS: true, letterRendering: true, logging: false },
        jsPDF: { unit: 'mm', format: 'a5', orientation: 'portrait' }
      };
      await html2pdf().from(el).set(opt).save();
      showToast(currentLang.value === 'en' ? `📥 PDF downloaded: Komal_Mart_Bill_${order.order_number}.pdf` : (currentLang.value === 'mr' ? `📥 PDF डाऊनलोड झाले: Komal_Mart_Bill_${order.order_number}.pdf` : `📥 PDF डाउनलोड हो गई: Komal_Mart_Bill_${order.order_number}.pdf`));
    } catch (err) {
      console.error('PDF error:', err);
      showToast(currentLang.value === 'en' ? 'Error downloading PDF, please use Print' : (currentLang.value === 'mr' ? 'PDF डाउनलोड करताना अडचण आली, प्रिंट वापरा' : 'PDF डाउनलोड करने में त्रुटि आई, कृपया प्रिंट उपयोग करें'), 'error');
    }
  }, 120);
}

async function loadDailyZReport() {
  try {
    const res = await fetch(`${API_BASE}/admin/reports/daily-z?date=${zReportDate.value}`, {
      headers: { 'Authorization': `Bearer ${authToken.value}` }
    });
    if (res.ok) {
      zReport.value = await res.json();
    }
  } catch (err) {
    console.error('Daily Z-Report error:', err);
  }
}

function setZReportQuickDate(offsetDays) {
  const d = new Date();
  d.setDate(d.getDate() + offsetDays);
  zReportDate.value = d.toISOString().split('T')[0];
  loadDailyZReport();
}

function shareDailyZReportWhatsApp() {
  if (!zReport.value) return;
  const z = zReport.value;
  let text = '';
  if (currentLang.value === 'en') {
    text =
`🏪 *Komal Mart — Daily Financial Settlement (Z-Report)* 🏪
📅 *Date:* ${z.formatted_date || z.date}
━━━━━━━━━━━━━━━━━━
💰 *Realized Cash & Bank Liquidity:*
• 💵 Cash in Hand (Drawer): ₹${z.total_cash_in_drawer}
• 📲 UPI / Bank Deposits: ₹${z.total_upi_received}
• ✨ *Total Liquid Collected:* ₹${z.total_liquid_collected}

🛒 *Sales & Basket Performance:*
• Total Orders: ${z.total_orders_count} (Avg Basket: ₹${z.avg_basket_value})
• Net Realized Sales: ₹${z.net_sales}
• Customer Savings Delivered: ₹${z.total_savings_given}
• Store Credits Redeemed: ₹${z.store_credit_redeemed}

📒 *Market Khata & Credit Flow:*
• Today's New Khata Given: ₹${z.khata_new_amount} (${z.khata_new_count} bills)
• Today's Khata Recovered: ₹${z.total_khata_recovered} (Cash: ₹${z.khata_cash_recovered}, UPI: ₹${z.khata_upi_recovered})
• Total Outstanding Market Udhaar: ₹${z.total_market_udhaar}
━━━━━━━━━━━━━━━━━━
📊 *Komal Mart ERP*`;
  } else if (currentLang.value === 'hi') {
    text =
`🏪 *कोमल मार्ट (Komal Mart) — दैनिक हिसाब (Daily Z-Report)* 🏪
📅 *तारीख:* ${z.formatted_date || z.date}
━━━━━━━━━━━━━━━━━━
💰 *गल्ला व बैंक जमा (Liquid Realized):*
• 💵 नकद गल्ला (Cash in Hand): ₹${z.total_cash_in_drawer}
• 📲 UPI / बैंक जमा: ₹${z.total_upi_received}
• ✨ *कुल नकद+बैंक जमा:* ₹${z.total_liquid_collected}

🛒 *बिक्री प्रदर्शन (Sales Performance):*
• कुल ऑर्डर्स: ${z.total_orders_count} (औसत बिल: ₹${z.avg_basket_value})
• वास्तविक बिक्री रकम: ₹${z.net_sales}
• ग्राहकों की कुल बचत: ₹${z.total_savings_given}
• उपयोग हुआ स्टोर क्रेडिट: ₹${z.store_credit_redeemed}

📒 *उधारी बहीखाता (Khata Movement):*
• आज दी गई नई उधारी: ₹${z.khata_new_amount} (${z.khata_new_count} बिल)
• आज वसूल हुई उधारी: ₹${z.total_khata_recovered} (नकद: ₹${z.khata_cash_recovered}, UPI: ₹${z.khata_upi_recovered})
• कुल बाजार बकाया उधारी: ₹${z.total_market_udhaar}
━━━━━━━━━━━━━━━━━━
📊 *Komal Mart ERP*`;
  } else {
    text =
`🏪 *कोमल मार्ट (Komal Mart) — दैनिक हिशोब (Daily Z-Report)* 🏪
📅 *तारीख:* ${z.formatted_date || z.date}
━━━━━━━━━━━━━━━━━━
💰 *गल्ला व बँक जमा (Liquid Realized):*
• 💵 रोख गल्ला (Cash in Hand): ₹${z.total_cash_in_drawer}
• 📲 UPI / बँक जमा: ₹${z.total_upi_received}
• ✨ *एकूण रोख+बँक जमा:* ₹${z.total_liquid_collected}

🛒 *विक्री कामगिरी (Sales Performance):*
• एकूण ऑर्डर्स: ${z.total_orders_count} (सरासरी: ₹${z.avg_basket_value})
• प्रत्यक्ष विक्री रक्कम: ₹${z.net_sales}
• ग्राहकांची थेट बचत: ₹${z.total_savings_given}
• वापरलेले स्टोअर क्रेडिट: ₹${z.store_credit_redeemed}

📒 *उधारी बही (Khata Movement):*
• आज दिलेली नवीन उधारी: ₹${z.khata_new_amount} (${z.khata_new_count} बिले)
• आज वसूल उधारी: ₹${z.total_khata_recovered} (रोख: ₹${z.khata_cash_recovered}, UPI: ₹${z.khata_upi_recovered})
• एकूण बाजार थकबाकी: ₹${z.total_market_udhaar}
━━━━━━━━━━━━━━━━━━
📊 *Komal Mart ERP*`;
  }

  const url = `https://api.whatsapp.com/send?text=${encodeURIComponent(text)}`;
  window.open(url, '_blank');
}

async function downloadZReportPdf() {
  const el = document.getElementById('printable-z-report');
  if (!el) return;
  try {
    showToast(currentLang.value === 'en' ? '⏳ Generating Z-Report PDF...' : (currentLang.value === 'mr' ? '⏳ Z-Report PDF तयार होत आहे...' : '⏳ Z-Report PDF तैयार हो रही है...'));
    const html2pdf = (await import('html2pdf.js')).default;
    const opt = {
      margin: [8, 8, 8, 8],
      filename: `Komal_Mart_ZReport_${zReportDate.value}.pdf`,
      image: { type: 'jpeg', quality: 0.98 },
      html2canvas: { scale: 2, useCORS: true, logging: false },
      jsPDF: { unit: 'mm', format: 'a4', orientation: 'portrait' }
    };
    await html2pdf().from(el).set(opt).save();
    showToast(currentLang.value === 'en' ? `📥 Z-Report PDF downloaded: Komal_Mart_ZReport_${zReportDate.value}.pdf` : (currentLang.value === 'mr' ? `📥 Z-Report PDF डाऊनलोड झाले: Komal_Mart_ZReport_${zReportDate.value}.pdf` : `📥 Z-Report PDF डाउनलोड हो गई: Komal_Mart_ZReport_${zReportDate.value}.pdf`));
  } catch (err) {
    console.error('Z-Report PDF error:', err);
    showToast(currentLang.value === 'en' ? 'Error downloading PDF' : (currentLang.value === 'mr' ? 'PDF डाउनलोड करताना अडचण आली' : 'PDF डाउनलोड करने में त्रुटि आई'), 'error');
  }
}

const zReportCurrentPrintTime = computed(() => {
  const now = new Date();
  return now.toLocaleDateString('en-IN', { day: '2-digit', month: 'short', year: 'numeric' }) + ' ' + now.toLocaleTimeString('en-IN', { hour: '2-digit', minute: '2-digit' });
});

const sendingWeeklyEmail = ref(false);
async function sendSundayWeeklyReportEmail() {
  sendingWeeklyEmail.value = true;
  try {
    const res = await fetch(`${API_BASE}/admin/reports/send-weekly`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${authToken.value}`
      }
    });
    const d = await res.json();
    if (res.ok && d.dispatched) {
      showToast(currentLang.value === 'en' ? `📧 Weekly Summary dispatched to ${d.recipient}!` : `📧 साप्ताहिक वित्तीय अहवाल ${d.recipient} वर यशस्वीरीत्या पाठवला!`);
    } else {
      showToast(d.message || d.details || 'ईमेल पाठवण्यात त्रुटी आली', 'error');
    }
  } catch (err) {
    console.error('Weekly email error:', err);
    showToast('Weekly email error: ' + err.message, 'error');
  } finally {
    sendingWeeklyEmail.value = false;
  }
}

function printZReport() {
  window.print();
}

async function downloadAdminExport(type) {
  const token = localStorage.getItem('kirana_token') || authToken.value;
  if (!token) {
    showToast(currentLang.value === 'en' ? 'Please log in as Admin' : 'कृपया ॲडमिन म्हणून लॉगिन करा', 'error');
    return;
  }
  showToast(currentLang.value === 'en' ? '⏳ Preparing export download...' : '⏳ फाईल डाऊनलोड तयार होत आहे...');
  try {
    let endpoint = '';
    let defaultFilename = '';
    const dateStamp = new Date().toISOString().slice(0, 10);
    if (type === 'orders.csv') {
      endpoint = `${API_BASE}/admin/export/orders.csv`;
      defaultFilename = `komalmart_orders_${dateStamp}.csv`;
    } else if (type === 'customers.csv') {
      endpoint = `${API_BASE}/admin/export/customers.csv`;
      defaultFilename = `komalmart_khata_customers_${dateStamp}.csv`;
    } else if (type === 'database') {
      endpoint = `${API_BASE}/admin/backup/download?compress=true`;
      defaultFilename = `komalmart_backup_${dateStamp}.db.gz`;
    }

    const res = await fetch(endpoint, {
      headers: { 'Authorization': `Bearer ${token}` }
    });
    if (!res.ok) {
      showToast(currentLang.value === 'en' ? 'Failed to download export file' : 'फाईल डाऊनलोड अयशस्वी झाली', 'error');
      return;
    }
    const blob = await res.blob();
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = defaultFilename;
    document.body.appendChild(a);
    a.click();
    a.remove();
    window.URL.revokeObjectURL(url);
    showToast(currentLang.value === 'en' ? '✅ File downloaded successfully!' : '✅ फाईल यशस्वीरीत्या डाऊनलोड झाली!');
  } catch (e) {
    console.error('Export download error:', e);
    showToast(currentLang.value === 'en' ? 'Download error' : 'डाऊनलोड त्रुटी', 'error');
  }
}

onMounted(() => {
  // If admin is already authenticated in localStorage, immediately kick off admin data fetches
  if (isAdminLoggedIn.value) {
    loadAdminOrders();
    loadAdminCustomers();
    loadAdminKhata();
    loadAdminSupportTickets();
  } else if (currentUser.value && authToken.value && currentUser.value.role !== 'admin') {
    loadCustomerOrders();
  }

  checkAuth();
  fetchCategories();
  fetchProducts();
  fetchAreaDeliveryHolds();

  // Restore saved Monthly Ration Parcha from localStorage
  try {
    const savedParcha = localStorage.getItem('komal_monthly_parcha');
    if (savedParcha) {
      const parsed = JSON.parse(savedParcha);
      if (Array.isArray(parsed) && parsed.length > 0) {
        monthlyParchaItems.value = parsed;
      }
    }
  } catch (e) {
    console.warn('Failed to parse saved parcha:', e);
  }

  // Check URL query parameters for 1-Tap Delivery Availability Check (e.g. ?order=KM-20261002-1098&token=abc... or &check=1)
  const urlParams = new URLSearchParams(window.location.search);
  const checkOrderNum = urlParams.get('order');
  const isDeliveryCheck = urlParams.get('check');
  const trackingToken = urlParams.get('token');
  if (checkOrderNum && (isDeliveryCheck || trackingToken)) {
    // Do not hijack admin ERP screen if storekeeper is already in admin mode
    if (!isAdminLoggedIn.value || window.location.hash !== '#admin') {
      openDeliveryCheckForOrder(checkOrderNum, trackingToken);
    }
    // Clean URL query params immediately so browser reloads never repeat the popup loop
    const cleanUrl = window.location.pathname + (window.location.hash || '');
    window.history.replaceState({}, document.title, cleanUrl);
  }

  // Handle #admin route direct access
  if (window.location.hash === '#admin') {
    if (!isAdminLoggedIn.value) {
      openAuthModal('admin');
    }
  }

  window.addEventListener('hashchange', () => {
    if (window.location.hash === '#admin' && !isAdminLoggedIn.value) {
      openAuthModal('admin');
    }
  });

  // PWA standalone detection
  if (window.matchMedia('(display-mode: standalone)').matches || window.navigator.standalone === true) {
    isAppInstalled.value = true;
  }

  // PWA install prompt handler
  window.addEventListener('beforeinstallprompt', (e) => {
    e.preventDefault();
    deferredInstallPrompt.value = e;
    if (!sessionStorage.getItem('pwa_banner_dismissed') && !isAppInstalled.value) {
      showInstallBanner.value = true;
    }
  });

  // Track app installation completion
  window.addEventListener('appinstalled', () => {
    isAppInstalled.value = true;
    showInstallBanner.value = false;
    deferredInstallPrompt.value = null;
    showToast(currentLang.value === 'en' ? '🎉 Komal Mart app added to Home Screen!' : (currentLang.value === 'mr' ? '🎉 कोमल मार्ट ॲप होम स्क्रीनवर जोडले गेले!' : '🎉 कोमल मार्ट ऐप होम स्क्रीन पर जोड़ा गया!'));
  });
});
</script>
