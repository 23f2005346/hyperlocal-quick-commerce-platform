<template>
  <div class="kirana-app">
    <!-- Top Announcement Bar -->
    <div class="top-announcement">
      <span>🌾 <strong>अपना देसी किराना स्टोर</strong> — ताज़ा माल • सही तोल • कम दाम</span>
      <span>🛵 30 मिनट में घर पहुँचाएं • फ्री डिलीवरी</span>
      <span>📞 ऑर्डर हेल्पलाइन: <strong>98765-43210</strong></span>
    </div>

    <!-- Main Navigation Header -->
    <header class="kirana-header">
      <div class="header-container">
        <!-- Logo & Store Branding -->
        <div class="store-brand" @click="resetFilters">
          <div class="store-logo">
            <svg viewBox="0 0 24 24" width="24" height="24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round">
              <path d="M6 2L3 6v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2V6l-3-4z"></path>
              <line x1="3" y1="6" x2="21" y2="6"></line>
              <path d="M16 10a4 4 0 0 1-8 0"></path>
            </svg>
          </div>
          <div class="brand-text">
            <h1>अपना किराना स्टोर</h1>
            <p>Apna Desi Kirana & General Store</p>
          </div>
        </div>

        <!-- Search Bar -->
        <div class="search-bar-wrap" v-if="!isAdminLoggedIn">
          <span class="search-icon">🔍</span>
          <input
            type="text"
            v-model="searchQuery"
            @input="debounceFetchProducts"
            placeholder="चावल, दाल, आटा, तेल, चाय, टूथपेस्ट खोजें (Search)..."
            class="search-input"
          />
        </div>

        <!-- Header Actions: User Profile / Login & Cart -->
        <div class="header-actions">
          <!-- ADMIN CONTROLS (IF LOGGED IN AS ADMIN) -->
          <template v-if="isAdminLoggedIn">
            <span style="font-size: 0.88rem; font-weight: 800; color: #064e3b; background: #ecfdf5; padding: 6px 14px; border-radius: 20px; border: 1px solid #a7f3d0;">
              👑 दुकानदार एडमिन
            </span>
            <button class="user-btn" @click="logout">
              🚪 लॉगआउट (Logout)
            </button>
          </template>

          <!-- CUSTOMER OR GUEST CONTROLS -->
          <template v-else>
            <!-- Logged in Customer -->
            <div v-if="currentUser" style="display: flex; align-items: center; gap: 8px;">
              <button class="user-btn" @click="openAccountModal">
                👤 नमस्ते, {{ currentUser.name.split(' ')[0] }}! (खाता)
              </button>
              <button class="user-btn" @click="logout" title="Logout" style="padding: 8px 12px;">
                🚪
              </button>
            </div>

            <!-- Guest / Not Logged In -->
            <button v-else class="user-btn" @click="openAuthModal('login')">
              👤 लॉगिन / रजिस्टर (Login)
            </button>

            <!-- Shopping Cart (Only for Customers / Guests) -->
            <button class="cart-btn" @click="isCartOpen = true">
              🛒 <span>थैला (Cart)</span>
              <span class="cart-badge">{{ cartTotalQuantity }}</span>
              <span v-if="cartTotalAmount > 0">₹{{ cartTotalAmount }}</span>
            </button>
          </template>
        </div>
      </div>
    </header>

    <!-- Category Bar (Only visible for customer store view) -->
    <nav class="category-nav" v-if="!isAdminLoggedIn">
      <div class="category-scroll">
        <button
          class="category-pill"
          :class="{ active: selectedCategorySlug === '' }"
          @click="selectCategory('')"
        >
          🌟 सब सामान (All Items)
        </button>
        <button
          v-for="cat in categories"
          :key="cat.id"
          class="category-pill"
          :class="{ active: selectedCategorySlug === cat.slug }"
          @click="selectCategory(cat.slug)"
        >
          {{ getCategoryEmoji(cat.slug) }} {{ cat.name_hi || cat.name }} ({{ cat.product_count }})
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
    <!-- VIEW 1: CUSTOMER STORE VIEW (PRODUCTS, FILTERS, CART)    -->
    <!-- ======================================================== -->
    <main class="main-layout" v-if="!isAdminLoggedIn">
      <!-- Desi Kirana Hero Promotional Banner -->
      <section class="hero-promo-banner">
        <div class="hero-text">
          <h2>🌾 शुद्ध अनाज, असली स्वाद • Mandi Direct Wholesale & Retail</h2>
          <p>Fresh Chakki Atta, unpolished pulses & 100% genuine desi spices at market-direct prices.</p>
          <div class="hero-perks">
            <div class="hero-perk-item">
              <svg viewBox="0 0 24 24" width="15" height="15" fill="none" stroke="#064e3b" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><path d="m16 16 3-8 3 8c-.87.65-1.92 1-3 1s-2.13-.35-3-1Z"/><path d="m2 16 3-8 3 8c-.87.65-1.92 1-3 1s-2.13-.35-3-1Z"/><path d="M7 21h10"/><path d="M12 3v18"/><path d="M3 7h2c2 0 5-1 7-2 2 1 5 2 7 2h2"/></svg>
              <span>सही तोल • 100% Accurate Weight</span>
            </div>
            <div class="hero-perk-item">
              <svg viewBox="0 0 24 24" width="15" height="15" fill="none" stroke="#064e3b" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><polygon points="13 2 3 14 12 14 11 22 21 10 12 10 13 2"/></svg>
              <span>30 मिनट में डिलीवरी • Fast Delivery</span>
            </div>
            <div class="hero-perk-item">
              <svg viewBox="0 0 24 24" width="15" height="15" fill="none" stroke="#064e3b" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><path d="M4 19.5v-15A2.5 2.5 0 0 1 6.5 2H20v20H6.5a2.5 2.5 0 0 1-2.5-2.5Z"/><path d="M6 6h10"/><path d="M6 10h10"/></svg>
              <span>मासिक खाता • Khata Credit</span>
            </div>
            <div class="hero-perk-item">
              <svg viewBox="0 0 24 24" width="15" height="15" fill="none" stroke="#064e3b" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/><polyline points="9 12 11 14 15 10"/></svg>
              <span>100% असली ब्रांड्स • Authentic Goods</span>
            </div>
          </div>
          <div class="hero-action-row">
            <button class="hero-cta-btn" @click="openMonthlyParchaModal">
              📝 एकमुश्त मासिक राशन पर्चा बनाएं (Monthly Ration Checklist) ➔
            </button>
          </div>
        </div>
      </section>

      <!-- Secondary Filter Row -->
      <div class="filter-row">
        <div class="sub-filter-group">
          <button
            class="filter-btn"
            :class="{ active: looseFilter === 'all' }"
            @click="setLooseFilter('all')"
          >
            सभी (All)
          </button>
          <button
            class="filter-btn"
            :class="{ active: looseFilter === 'true' }"
            @click="setLooseFilter('true')"
          >
            🌾 खुला राशन (Loose Mandi)
          </button>
          <button
            class="filter-btn"
            :class="{ active: looseFilter === 'false' }"
            @click="setLooseFilter('false')"
          >
            📦 ब्रांडेड पैकेट (Packaged)
          </button>
        </div>

        <div style="display: flex; align-items: center; gap: 8px;">
          <span style="font-size: 0.84rem; color: #57534e; font-weight: 700;">सॉर्ट करें:</span>
          <select v-model="sortBy" @change="fetchProducts" class="sort-select">
            <option value="">लोकप्रिय (Featured)</option>
            <option value="price_asc">कीमत: कम से ज्यादा (Price: Low to High)</option>
            <option value="price_desc">कीमत: ज्यादा से कम (Price: High to Low)</option>
            <option value="name">नाम के अनुसार (A to Z)</option>
          </select>
        </div>
      </div>

      <!-- Loading State -->
      <div v-if="loading" style="text-align: center; padding: 70px 20px;">
        <div style="font-size: 2.5rem; margin-bottom: 12px; animation: bounce 1s infinite;">🌾</div>
        <p style="font-weight: 800; color: #047857; font-size: 1.1rem;">
          किराना भंडार से ताज़ा सामान लोड हो रहा है...
        </p>
      </div>

      <!-- Empty State -->
      <div v-else-if="products.length === 0" style="text-align: center; padding: 70px 20px; background: white; border-radius: 14px; border: 1.5px dashed #d6cfc7;">
        <div style="font-size: 3.5rem; margin-bottom: 14px;">🔍</div>
        <h3 style="font-size: 1.3rem; font-weight: 800; color: #1c1917;">कोई सामान नहीं मिला</h3>
        <p style="color: #78716c; font-size: 0.95rem; margin-top: 4px;">
          कृपया कोई दूसरा नाम खोजें या फ़िल्टर रीसेट करें।
        </p>
        <button
          @click="resetFilters"
          style="margin-top: 18px; padding: 10px 22px; background: #047857; color: white; border: none; border-radius: 10px; font-weight: 800; cursor: pointer;"
        >
          सब सामान देखें
        </button>
      </div>

      <!-- Products Grid -->
      <div v-else class="products-grid">
        <div v-for="prod in products" :key="prod.id" class="product-card">
          <!-- Product Photo (Verified Local Images) -->
          <div class="product-thumb-wrap">
            <img
              :src="prod.image_url"
              :alt="prod.name"
              class="product-thumb"
              loading="lazy"
              @error="handleImageFallback($event)"
            />
            <span v-if="prod.is_loose" class="loose-badge">🌾 खुला (Loose)</span>
            <span v-else class="packed-badge">📦 पैकेट (Packed)</span>
            <span class="brand-badge">{{ prod.brand }}</span>
          </div>

          <!-- Product Details -->
          <div class="product-info">
            <h3 class="product-title">{{ prod.name }}</h3>
            <div class="product-hindi-name">{{ prod.name_hi }}</div>
            <p class="product-desc">{{ prod.description }}</p>

            <!-- Unit Variant Selector & Loose Custom Weight Option -->
            <div class="variants-wrap" v-if="prod.variants && prod.variants.length > 0">
              <div class="variant-label-title">वजन / पैक चुनें:</div>
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
                  title="अपनी मर्जी का वजन लिखें जैसे 4.5kg, 1.75kg, 15kg"
                >
                  ✏️ मनचाहा तोल (Custom kg)
                </button>
              </div>
            </div>

            <!-- MODE A: CUSTOM WEIGHT ENTRY FOR LOOSE COMMODITIES -->
            <div v-if="customWeightMode[prod.id]" class="custom-weight-box">
              <div class="custom-weight-header">
                <span>⚖️ मनचाहा वजन लिखें:</span>
                <span class="custom-rate-badge">दर: ₹{{ getBasePerKgRate(prod) }}/kg</span>
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
                <span class="quick-chip" @click="setQuickCustomWeight(prod.id, 4.5)">4.5kg</span>
                <span class="quick-chip" @click="setQuickCustomWeight(prod.id, 10)">10kg</span>
                <span class="quick-chip" @click="setQuickCustomWeight(prod.id, 15)">15kg</span>
              </div>
              <div class="custom-price-calc">
                <span>कुल कीमत (₹{{ getBasePerKgRate(prod) }} × {{ customWeightInputs[prod.id] || 0 }}):</span>
                <strong class="custom-total-val">₹{{ getCustomWeightPrice(prod) }}</strong>
              </div>
              <button
                class="add-to-cart-btn custom-add-btn"
                @click="addCustomWeightItemToCart(prod)"
                :disabled="!customWeightInputs[prod.id] || customWeightInputs[prod.id] <= 0"
              >
                🛒 {{ customWeightInputs[prod.id] || 0 }} kg थैले में जोड़ें
              </button>
            </div>

            <!-- MODE B: STANDARD PACKET / FIXED VARIANT DISPLAY -->
            <template v-else>
              <!-- Price & Discount Row -->
              <div class="price-row" v-if="getActiveVariant(prod)">
                <span class="selling-price">₹{{ getActiveVariant(prod).selling_price }}</span>
                <span class="mrp-price" v-if="getActiveVariant(prod).mrp > getActiveVariant(prod).selling_price">
                  ₹{{ getActiveVariant(prod).mrp }}
                </span>
                <span class="discount-tag" v-if="getActiveVariant(prod).discount_pct > 0">
                  {{ getActiveVariant(prod).discount_pct }}% बचत
                </span>
              </div>

              <!-- Add to Cart or Quantity Controls -->
              <div v-if="getActiveVariant(prod)">
                <div v-if="getCartItemQuantity(prod.id, getActiveVariant(prod).id) === 0">
                  <button
                    class="add-to-cart-btn"
                    @click="addToCart(prod, getActiveVariant(prod))"
                  >
                    🛒 थैले में जोड़ें (Add to Cart)
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

      <!-- Footer with Admin Login Link -->
      <footer style="margin-top: 60px; padding: 24px; border-top: 1.5px solid var(--border); text-align: center; color: var(--text-subtle); font-size: 0.88rem;">
        <p>अपना देसी किराना स्टोर • शुद्ध राशन, दालें, आटा एवं घरेलू सामान</p>
        <p style="margin-top: 6px;">
          <a href="javascript:void(0)" @click="openAuthModal('admin')" style="color: #d97706; font-weight: 700; text-decoration: none;">
            🔐 दुकानदार पोर्टल लॉगिन (Store Owner Access)
          </a>
        </p>
      </footer>
    </main>

    <!-- ======================================================== -->
    <!-- VIEW 2: DUKANDAR / STORE OWNER ADMIN DASHBOARD           -->
    <!-- ======================================================== -->
    <section class="main-layout" v-if="isAdminLoggedIn">
      <div style="background: white; border: 1.5px solid var(--border); border-radius: 16px; padding: 26px; box-shadow: var(--shadow-sm); margin-bottom: 24px;">
        <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 16px; border-bottom: 1.5px solid var(--border); padding-bottom: 18px;">
          <div>
            <h2 style="font-size: 1.45rem; font-weight: 900; color: #064e3b; display: flex; align-items: center; gap: 10px;">
              🏪 दुकानदार कंट्रोल पैनल (Storekeeper Management)
            </h2>
            <p style="color: var(--text-muted); font-size: 0.9rem; margin-top: 4px;">
              यहाँ से आप तुरंत किसी भी दाल, आटा, तेल की दर (Price) और स्टॉक सुरक्षित तरीके से SQLite में बदल सकते हैं।
            </p>
          </div>
          <div style="display: flex; gap: 10px;">
            <button
              @click="showAddProductModal = true"
              style="background: #047857; color: white; border: none; padding: 10px 18px; border-radius: 10px; font-weight: 800; cursor: pointer; display: flex; align-items: center; gap: 6px;"
            >
              ➕ नया सामान जोड़ें (Add Product)
            </button>
            <button
              @click="confirmResetSeed"
              style="background: #fee2e2; color: #991b1b; border: 1px solid #fecaca; padding: 10px 18px; border-radius: 10px; font-weight: 800; cursor: pointer;"
              title="Reset to default authentic Indian Kirana catalog"
            >
              🔄 रीसेट डिफ़ॉल्ट सामान
            </button>
          </div>
        </div>

        <!-- Dashboard Sub-Tabs -->
        <div class="account-tabs" style="margin-top: 20px;">
          <button
            class="account-tab-btn"
            :class="{ active: adminActiveTab === 'inventory' }"
            @click="adminActiveTab = 'inventory'"
          >
            📋 पूरा सामान व लाइव कीमत (Live Price Editor)
          </button>
          <button
            class="account-tab-btn"
            :class="{ active: adminActiveTab === 'orders' }"
            @click="loadAdminOrders"
          >
            🧾 बहीखाता व ग्राहक ऑर्डर (Customer Orders Book)
          </button>
        </div>

        <!-- TAB 1: INVENTORY & QUICK PRICE CHANGER -->
        <div v-if="adminActiveTab === 'inventory'">
          <div style="margin-top: 14px; display: flex; justify-content: space-between; align-items: center; gap: 12px; flex-wrap: wrap;">
            <input
              type="text"
              v-model="adminSearch"
              placeholder="सामान खोजें (Filter items)..."
              style="padding: 9px 16px; border: 1.5px solid var(--border); border-radius: 10px; font-size: 0.9rem; min-width: 300px;"
            />
            <span style="font-size: 0.88rem; color: var(--text-muted);">
              कुल सामान: <strong>{{ filteredAdminProducts.length }}</strong>
            </span>
          </div>

          <div class="admin-table-wrap">
            <table class="admin-table">
              <thead>
                <tr>
                  <th>सामान (Product & Hindi Name)</th>
                  <th>प्रकार (Type)</th>
                  <th>ब्रांड (Brand)</th>
                  <th>वजन/यूनिट</th>
                  <th>MRP (₹)</th>
                  <th>दुकान दर (Selling ₹)</th>
                  <th>स्टॉक संख्या</th>
                  <th>एक्शन</th>
                </tr>
              </thead>
              <tbody>
                <template v-for="prod in filteredAdminProducts" :key="prod.id">
                  <tr v-for="v in prod.variants" :key="v.id">
                    <td>
                      <strong>{{ prod.name }}</strong>
                      <div style="font-size: 0.8rem; color: #c2410c; font-family: var(--font-hindi);">
                        {{ prod.name_hi }}
                      </div>
                    </td>
                    <td>
                      <span v-if="prod.is_loose" style="background: #fffbeb; color: #b45309; padding: 2px 7px; border-radius: 4px; font-size: 0.76rem; font-weight: 800;">
                        खुला
                      </span>
                      <span v-else style="background: #eff6ff; color: #1d4ed8; padding: 2px 7px; border-radius: 4px; font-size: 0.76rem; font-weight: 800;">
                        पैकेट
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
                      <input
                        type="number"
                        v-model.number="v.stock_quantity"
                        class="admin-inline-input"
                      />
                    </td>
                    <td>
                      <div style="display: flex; gap: 6px; align-items: center;">
                        <button
                          class="save-chip-btn"
                          @click="saveVariantPrice(v)"
                          title="Save changed price to SQLite"
                        >
                          💾 सेव करें
                        </button>
                        <button
                          class="delete-product-btn"
                          @click="deleteAdminProduct(prod.id, prod.name)"
                          title="इस सामान को दुकान से हटाएं"
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
        </div>

        <!-- TAB 2: ORDERS & KHATA LEDGER -->
        <div v-if="adminActiveTab === 'orders'" style="margin-top: 14px;">
          <!-- Filter Row for Admin Orders -->
          <div class="admin-orders-filter-row">
            <button
              :class="{ active: adminOrderFilter === 'all' }"
              @click="adminOrderFilter = 'all'"
            >
              सभी ऑर्डर ({{ adminOrders.length }})
            </button>
            <button
              :class="{ active: adminOrderFilter === 'unpaid' }"
              @click="adminOrderFilter = 'unpaid'"
              style="color: #b91c1c; font-weight: 800;"
            >
              🔴 बाकी / उधारी ({{ unpaidAdminOrders.length }})
            </button>
            <button
              :class="{ active: adminOrderFilter === 'paid' }"
              @click="adminOrderFilter = 'paid'"
              style="color: #15803d; font-weight: 800;"
            >
              🟢 चुकता ({{ paidAdminOrders.length }})
            </button>
            <button
              :class="{ active: adminOrderFilter === 'cod' }"
              @click="adminOrderFilter = 'cod'"
            >
              💵 नकद COD ({{ codAdminOrders.length }})
            </button>
            <button
              :class="{ active: adminOrderFilter === 'upi' }"
              @click="adminOrderFilter = 'upi'"
            >
              📱 UPI QR ({{ upiAdminOrders.length }})
            </button>
          </div>

          <div v-if="displayedAdminOrders.length === 0" style="text-align: center; padding: 40px 20px; color: var(--text-muted); background: white; border-radius: 12px; border: 1px dashed var(--border);">
            इस फ़िल्टर में कोई ऑर्डर नहीं मिला।
          </div>
          <div v-else style="display: flex; flex-direction: column; gap: 16px;">
            <div
              v-for="ord in displayedAdminOrders"
              :key="ord.id"
              style="border: 1.5px solid var(--border); border-radius: 12px; padding: 18px; background: #fdfbf7;"
            >
              <div style="display: flex; justify-content: space-between; align-items: center; border-bottom: 1px solid var(--border); padding-bottom: 12px; flex-wrap: wrap; gap: 10px;">
                <div>
                  <span style="font-weight: 900; color: #064e3b; font-size: 1.05rem;">
                    {{ ord.order_number }}
                  </span>
                  <span style="margin-left: 12px; font-size: 0.82rem; color: var(--text-subtle);">
                    {{ ord.created_at }}
                  </span>
                </div>
                <div style="display: flex; align-items: center; gap: 10px; flex-wrap: wrap;">
                  <!-- Delivery Status Dropdown -->
                  <select
                    v-model="ord.status"
                    @change="updateAdminOrderStatus(ord)"
                    style="padding: 5px 10px; border-radius: 8px; border: 1px solid var(--border); font-weight: 700; font-size: 0.82rem;"
                  >
                    <option value="Placed">Placed (ऑर्डर दर्ज)</option>
                    <option value="Packed">Packed (पैक तैयार)</option>
                    <option value="Out for Delivery">Out for Delivery (रास्ते में)</option>
                    <option value="Delivered">Delivered (सफलतापूर्वक दिया)</option>
                  </select>

                  <!-- Payment Status Dropdown -->
                  <select
                    v-model="ord.payment_status"
                    @change="updateAdminOrderStatus(ord)"
                    style="padding: 5px 10px; border-radius: 8px; border: 1px solid var(--border); font-weight: 800; font-size: 0.82rem;"
                    :style="ord.payment_status === 'Paid' ? 'color: #14532d; background: #dcfce7;' : 'color: #991b1b; background: #fee2e2;'"
                  >
                    <option value="Paid">🟢 चुकता (Paid)</option>
                    <option value="Unpaid">🔴 बाकी उधारी (Unpaid)</option>
                  </select>

                  <!-- 1-Click Mark as Paid Button for COD/Unpaid Orders -->
                  <button
                    v-if="ord.payment_status !== 'Paid'"
                    @click="markOrderAsPaid(ord)"
                    class="admin-mark-paid-btn"
                    title="ग्राहक से नकद/UPI मिलते ही चुकता मार्क करें"
                  >
                    ✅ नकद मिला (Mark Paid)
                  </button>

                  <span style="font-weight: 900; font-size: 1.2rem; color: #1c1917;">
                    ₹{{ ord.final_amount }}
                  </span>
                </div>
              </div>

              <div style="display: flex; justify-content: space-between; margin-top: 12px; font-size: 0.88rem; color: var(--text-main); flex-wrap: wrap; gap: 10px;">
                <div>
                  <strong>ग्राहक:</strong> {{ ord.customer_name }} (📞 {{ ord.customer_phone }})<br />
                  <strong>पता:</strong> {{ ord.customer_address }}
                </div>
                <div style="text-align: right;">
                  <strong>भुगतान तरीका:</strong> {{ ord.payment_method }}<br />
                  <span style="color: #047857; font-weight: 800;">किराना बचत: ₹{{ ord.total_savings }}</span>
                </div>
              </div>

              <!-- Order Items Preview -->
              <div style="margin-top: 12px; background: white; padding: 10px 14px; border-radius: 8px; border: 1px solid var(--border); font-size: 0.84rem;">
                <strong>सामान सूची:</strong>
                <span v-for="(it, idx) in ord.items" :key="idx" style="margin-left: 8px; color: var(--text-muted);">
                  {{ it.product_name }} ({{ it.variant_label }}) × {{ it.quantity }} = ₹{{ it.subtotal }}{{ idx < ord.items.length - 1 ? ' | ' : '' }}
                </span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>

    <!-- ======================================================== -->
    <!-- VIEW 3: CUSTOMER ACCOUNT & ORDERS MODAL                  -->
    <!-- ======================================================== -->
    <div class="modal-overlay" v-if="showAccountModal" @click.self="showAccountModal = false">
      <div class="modal-card" style="max-width: 620px;">
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 16px;">
          <h3 style="font-size: 1.3rem; font-weight: 900; color: #064e3b; display: flex; align-items: center; gap: 8px;">
            👤 मेरा किराना खाता (My Account)
          </h3>
          <button class="close-btn" @click="showAccountModal = false">✕</button>
        </div>

        <div class="account-tabs">
          <button
            class="account-tab-btn"
            :class="{ active: customerActiveTab === 'orders' }"
            @click="customerActiveTab = 'orders'"
          >
            📦 मेरे ऑर्डर व उधारी (My Orders)
          </button>
          <button
            class="account-tab-btn"
            :class="{ active: customerActiveTab === 'profile' }"
            @click="customerActiveTab = 'profile'"
          >
            ⚙️ प्रोफाइल व डिलीवरी पता (Profile & Address)
          </button>
        </div>

        <!-- CUSTOMER TAB 1: MY ORDERS -->
        <div v-if="customerActiveTab === 'orders'">
          <div v-if="customerOrdersLoading" style="text-align: center; padding: 30px;">
            ऑर्डर लोड हो रहे हैं...
          </div>
          <div v-else-if="customerOrders.length === 0" style="text-align: center; padding: 40px 20px; color: var(--text-muted);">
            <div style="font-size: 2.5rem; margin-bottom: 8px;">🧺</div>
            <p style="font-weight: 700;">आपने अभी तक कोई ऑर्डर नहीं दिया है।</p>
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
                </div>
              </div>

              <!-- Statuses Row -->
              <div style="display: flex; justify-content: space-between; align-items: center; margin-top: 10px; font-size: 0.85rem;">
                <div style="display: flex; gap: 8px; align-items: center;">
                  <span class="status-badge" :class="ord.status.toLowerCase().replace(/\s+/g, '')">
                    📦 {{ ord.status }}
                  </span>
                  <span class="pay-badge" :class="ord.payment_status.toLowerCase().includes('paid') && !ord.payment_status.toLowerCase().includes('unpaid') ? 'paid' : 'unpaid'">
                    {{ ord.payment_status === 'Paid' ? '🟢 चुकता (Paid)' : '🔴 बाकी उधारी (Unpaid)' }}
                  </span>
                </div>

                <div style="display: flex; gap: 8px;">
                  <button
                    v-if="ord.payment_status !== 'Paid'"
                    @click="openUpiPayForCustomerOrder(ord)"
                    style="background: #047857; color: white; border: none; padding: 5px 12px; border-radius: 6px; font-size: 0.8rem; font-weight: 800; cursor: pointer;"
                  >
                    💳 UPI से भुगतान करें
                  </button>
                  <button
                    @click="viewOrderReceipt(ord)"
                    style="background: white; border: 1px solid var(--border); padding: 5px 12px; border-radius: 6px; font-size: 0.8rem; font-weight: 700; cursor: pointer;"
                  >
                    🧾 पर्चा देखें
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
              <label class="form-label">पूरा नाम (Full Name) *</label>
              <input type="text" v-model="profileForm.name" required class="form-input" />
            </div>
            <div class="form-group">
              <label class="form-label">ईमेल (Email ID - Read Only)</label>
              <input type="email" :value="profileForm.email" disabled class="form-input" style="background: #f5f0e8; cursor: not-allowed;" />
            </div>
            <div class="form-group">
              <label class="form-label">मोबाइल नंबर (Phone Number) *</label>
              <input type="tel" v-model="profileForm.phone" required class="form-input" />
            </div>
            <div class="form-group">
              <label class="form-label">डिफ़ॉल्ट डिलीवरी का पता (Delivery Address) *</label>
              <textarea v-model="profileForm.address" rows="3" required class="form-input" placeholder="मकान नं, बिल्डिंग, गली, मोहल्ला / लैंडमार्क"></textarea>
            </div>
            <button type="submit" class="checkout-btn">
              💾 पता व सेटिंग्स सेव करें
            </button>
          </form>
        </div>
      </div>
    </div>

    <!-- ======================================================== -->
    <!-- AUTH MODAL: LOGIN / REGISTER / ADMIN LOGIN               -->
    <!-- ======================================================== -->
    <div class="modal-overlay" v-if="showAuthModal" @click.self="showAuthModal = false">
      <div class="modal-card" style="max-width: 440px;">
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 16px;">
          <h3 style="font-size: 1.25rem; font-weight: 900; color: #064e3b;">
            {{ authMode === 'admin' ? '🔐 दुकानदार लॉगिन (Admin Portal)' : (authMode === 'register' ? '📝 नया ग्राहक खाता बनाएं' : '👤 ग्राहक लॉगिन') }}
          </h3>
          <button class="close-btn" @click="showAuthModal = false">✕</button>
        </div>

        <!-- Auth Tabs (Only for Customer) -->
        <div class="account-tabs" v-if="authMode !== 'admin'">
          <button
            class="account-tab-btn"
            :class="{ active: authMode === 'login' }"
            @click="authMode = 'login'"
          >
            लॉगिन करें
          </button>
          <button
            class="account-tab-btn"
            :class="{ active: authMode === 'register' }"
            @click="authMode = 'register'"
          >
            नया खाता बनाएं
          </button>
        </div>

        <!-- Error Alert -->
        <div v-if="authError" style="background: #fee2e2; color: #991b1b; padding: 10px 14px; border-radius: 8px; font-size: 0.85rem; font-weight: 700; margin-bottom: 14px; border: 1px solid #fecaca;">
          {{ authError }}
        </div>

        <!-- LOGIN FORM -->
        <form v-if="authMode === 'login' || authMode === 'admin'" @submit.prevent="handleLogin">
          <div class="form-group">
            <label class="form-label">ईमेल आईडी (Email) *</label>
            <input
              type="email"
              v-model="authForm.email"
              required
              class="form-input"
              :placeholder="authMode === 'admin' ? 'admin@kirana.com' : 'apna-email@gmail.com'"
            />
          </div>
          <div class="form-group">
            <label class="form-label">पासवर्ड (Password) *</label>
            <input
              type="password"
              v-model="authForm.password"
              required
              class="form-input"
              :placeholder="authMode === 'admin' ? 'admin123' : 'पासवर्ड दर्ज करें'"
            />
          </div>

          <button type="submit" class="checkout-btn" :disabled="authSubmitting">
            {{ authSubmitting ? 'जाँच हो रही है...' : (authMode === 'admin' ? '🔐 एडमिन डैशबोर्ड खोलें' : 'लॉगिन करें') }}
          </button>

          <p v-if="authMode === 'admin'" style="font-size: 0.78rem; color: #78716c; margin-top: 12px; text-align: center;">
            डिफ़ॉल्ट क्रेडेंशियल्स: <code>admin@kirana.com</code> / <code>admin123</code>
          </p>
        </form>

        <!-- REGISTER FORM -->
        <form v-else @submit.prevent="handleRegister">
          <div class="form-group">
            <label class="form-label">पूरा नाम (Full Name) *</label>
            <input type="text" v-model="registerForm.name" required class="form-input" placeholder="जैसे: Roushan Kumar" />
          </div>
          <div class="form-group">
            <label class="form-label">ईमेल (Email) *</label>
            <input type="email" v-model="registerForm.email" required class="form-input" placeholder="naam@example.com" />
          </div>
          <div class="form-group">
            <label class="form-label">मोबाइल नंबर (Phone) *</label>
            <input type="tel" v-model="registerForm.phone" required pattern="[0-9]{10}" class="form-input" placeholder="10 अंकों का फोन नंबर" />
          </div>
          <div class="form-group">
            <label class="form-label">पासवर्ड (Password) *</label>
            <input type="password" v-model="registerForm.password" required minlength="4" class="form-input" placeholder="कम से कम 4 अक्षर" />
          </div>
          <div class="form-group">
            <label class="form-label">डिलीवरी का पता (Delivery Address) *</label>
            <textarea v-model="registerForm.address" required rows="2" class="form-input" placeholder="मकान नं, मोहल्ला / लैंडमार्क"></textarea>
          </div>

          <button type="submit" class="checkout-btn" :disabled="authSubmitting">
            {{ authSubmitting ? 'खाता बन रहा है...' : '✅ रजिस्टर करें व खरीदारी शुरू करें' }}
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
            🛒 आपका थैला (Cart)
          </h2>
          <button class="close-btn" @click="isCartOpen = false">✕</button>
        </div>

        <!-- Free Delivery Progress Meter -->
        <div class="free-delivery-meter" v-if="cart.length > 0">
          <div class="meter-text-row">
            <span v-if="Number(cartTotalAmount) < 300">
              🛵 बस <strong>₹{{ (300 - Number(cartTotalAmount)).toFixed(2) }}</strong> और जोड़ें <strong>मुफ़्त डिलीवरी</strong> हेतु!
            </span>
            <span v-else style="color: #064e3b; font-weight: 800;">
              🎉 बधाई! आपके ऑर्डर पर <strong>मुफ़्त डिलीवरी</strong> लागू है!
            </span>
            <span class="meter-pct-badge">{{ Math.min(100, Math.round((Number(cartTotalAmount) / 300) * 100)) }}%</span>
          </div>
          <div class="meter-track">
            <div
              class="meter-bar"
              :class="{ completed: Number(cartTotalAmount) >= 300 }"
              :style="{ width: Math.min(100, Math.round((Number(cartTotalAmount) / 300) * 100)) + '%' }"
            ></div>
          </div>
        </div>

        <!-- Empty Cart -->
        <div v-if="cart.length === 0" style="flex: 1; display: flex; flex-direction: column; align-items: center; justify-content: center; padding: 30px; text-align: center;">
          <div style="font-size: 3.5rem; margin-bottom: 12px;">🧺</div>
          <h4 style="font-size: 1.15rem; font-weight: 800;">आपका थैला खाली है</h4>
          <p style="color: var(--text-subtle); font-size: 0.9rem; margin-top: 4px;">
            दालें, चावल, आटा और रोज़मर्रा का सामान जोड़ें।
          </p>
          <button
            @click="isCartOpen = false"
            style="margin-top: 18px; padding: 10px 22px; background: #047857; color: white; border: none; border-radius: 10px; font-weight: 800; cursor: pointer;"
          >
            खरीदारी शुरू करें
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
                  कुल: <strong>₹{{ item.subtotal.toFixed(2) }}</strong>
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
                  ₹{{ item.variant.selling_price }} × {{ item.quantity }} =
                  <strong>₹{{ (item.variant.selling_price * item.quantity).toFixed(2) }}</strong>
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
              <span>सामान का कुल मूल्य (MRP Total)</span>
              <span>₹{{ cartTotalMrp }}</span>
            </div>
            <div class="bill-row savings">
              <span>किराना बचत (Savings / Discount)</span>
              <span>- ₹{{ cartTotalSavings }}</span>
            </div>
            <div class="bill-row total">
              <span>कुल देय राशि (Payable Amount)</span>
              <span>₹{{ cartTotalAmount }}</span>
            </div>
          </div>

          <button class="checkout-btn" @click="openCheckoutModal">
            📝 बिल / पर्चा बनाएं (Proceed to Bill)
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
            📝 डिलीवरी व बिल विवरण (Order Details)
          </h3>
          <button class="close-btn" @click="showCheckoutModal = false">✕</button>
        </div>

        <form @submit.prevent="submitOrder">
          <div class="form-group">
            <label class="form-label">ग्राहक का नाम (Customer Name) *</label>
            <input type="text" v-model="customerForm.name" required class="form-input" />
          </div>

          <div class="form-group">
            <label class="form-label">मोबाइल नंबर (Phone Number) *</label>
            <input type="tel" v-model="customerForm.phone" required pattern="[0-9]{10}" class="form-input" />
          </div>

          <div class="form-group">
            <label class="form-label">डिलीवरी का पता / लैंडमार्क (Address) *</label>
            <textarea v-model="customerForm.address" required rows="2" class="form-input" placeholder="मकान नं, गली, मोहल्ला / लैंडमार्क"></textarea>
          </div>

          <!-- Delivery Slot Selector -->
          <div class="form-group">
            <label class="form-label">⏰ डिलीवरी का समय चुनें (Delivery Slot) *</label>
            <div class="delivery-slots-grid">
              <div
                v-for="slot in deliverySlotOptions"
                :key="slot.id"
                class="delivery-slot-card"
                :class="{ active: customerForm.deliverySlot === slot.label }"
                @click="customerForm.deliverySlot = slot.label"
              >
                <div class="slot-icon">{{ slot.icon }}</div>
                <div class="slot-details">
                  <div class="slot-label">{{ slot.title }}</div>
                  <div class="slot-desc">{{ slot.desc }}</div>
                </div>
                <div class="slot-check-icon" v-if="customerForm.deliverySlot === slot.label">✓</div>
              </div>
            </div>
          </div>

          <div class="form-group">
            <label class="form-label">भुगतान का तरीका (Payment Option)</label>
            <select v-model="customerForm.paymentMethod" class="form-input">
              <option value="Cash on Delivery (COD)">💵 नकद डिलीवरी पर (Cash on Delivery)</option>
              <option value="UPI / QR Code">📱 तुरंत UPI / QR कोड (PhonePe / GPay / Paytm)</option>
              <option value="Kirana Khata (Pay Later)">📖 किराना खाता (उधारी / बाद में भुगतान)</option>
            </select>
          </div>

          <!-- COD Notice -->
          <div v-if="customerForm.paymentMethod === 'Cash on Delivery (COD)'" class="payment-notice-banner cod-banner">
            <div style="font-weight: 800; color: #92400e; font-size: 0.88rem; margin-bottom: 2px;">
              💵 नकद भुगतान (Cash on Delivery)
            </div>
            <div style="font-size: 0.8rem; color: #78350f;">
              सामान घर पहुँचने पर डिलीवरी वाले को नकद भुगतान करें। ऑर्डर बिल पर स्थिति <strong>🔴 बाकी / उधारी (Unpaid)</strong> दिखेगी।
            </div>
          </div>

          <!-- Khata Notice -->
          <div v-if="customerForm.paymentMethod === 'Kirana Khata (Pay Later)'" class="payment-notice-banner khata-banner">
            <div style="font-weight: 800; color: #1e3a8a; font-size: 0.88rem; margin-bottom: 2px;">
              📖 मासिक किराना खाता (Pay Later)
            </div>
            <div style="font-size: 0.8rem; color: #1e40af;">
              यह ऑर्डर आपके मासिक खाते में लिख लिया जाएगा। स्थिति <strong>🔴 बाकी उधारी (Unpaid)</strong> रहेगी जिसे आप कभी भी चुका सकते हैं।
            </div>
          </div>

          <!-- Shop Owner UPI QR Code Display -->
          <div v-if="customerForm.paymentMethod === 'UPI / QR Code'" class="upi-qr-card">
            <div class="upi-header">
              <span class="upi-badge">BHIM UPI • PhonePe • Google Pay • Paytm</span>
              <h4>दुकान का ऑफिशियल UPI QR कोड</h4>
            </div>

            <div class="upi-qr-frame">
              <div class="qr-code-svg-wrap">
                <svg viewBox="0 0 200 200" width="145" height="145">
                  <rect width="200" height="200" fill="#ffffff" rx="8" />
                  <rect x="15" y="15" width="45" height="45" fill="#1c1917" rx="4" />
                  <rect x="22" y="22" width="31" height="31" fill="#ffffff" rx="2" />
                  <rect x="28" y="28" width="19" height="19" fill="#047857" rx="2" />
                  <rect x="140" y="15" width="45" height="45" fill="#1c1917" rx="4" />
                  <rect x="147" y="22" width="31" height="31" fill="#ffffff" rx="2" />
                  <rect x="153" y="28" width="19" height="19" fill="#047857" rx="2" />
                  <rect x="15" y="140" width="45" height="45" fill="#1c1917" rx="4" />
                  <rect x="22" y="147" width="31" height="31" fill="#ffffff" rx="2" />
                  <rect x="28" y="153" width="19" height="19" fill="#047857" rx="2" />
                  <circle cx="75" cy="25" r="4" fill="#1c1917" /><circle cx="95" cy="25" r="4" fill="#1c1917" /><circle cx="115" cy="25" r="4" fill="#1c1917" />
                  <circle cx="85" cy="40" r="4" fill="#1c1917" /><circle cx="105" cy="40" r="4" fill="#047857" /><circle cx="125" cy="40" r="4" fill="#1c1917" />
                  <circle cx="25" cy="75" r="4" fill="#1c1917" /><circle cx="45" cy="75" r="4" fill="#1c1917" /><circle cx="25" cy="95" r="4" fill="#1c1917" />
                  <circle cx="75" cy="75" r="4" fill="#047857" /><circle cx="90" cy="75" r="4" fill="#1c1917" /><circle cx="110" cy="75" r="4" fill="#1c1917" />
                  <circle cx="75" cy="115" r="4" fill="#1c1917" /><circle cx="95" cy="115" r="4" fill="#047857" /><circle cx="115" cy="115" r="4" fill="#1c1917" />
                  <circle cx="145" cy="75" r="4" fill="#1c1917" /><circle cx="165" cy="75" r="4" fill="#1c1917" /><circle cx="175" cy="95" r="4" fill="#047857" />
                  <circle cx="145" cy="115" r="4" fill="#047857" /><circle cx="165" cy="115" r="4" fill="#1c1917" />
                  <circle cx="75" cy="145" r="4" fill="#1c1917" /><circle cx="95" cy="145" r="4" fill="#1c1917" /><circle cx="115" cy="145" r="4" fill="#047857" />
                  <circle cx="85" cy="165" r="4" fill="#047857" /><circle cx="105" cy="165" r="4" fill="#1c1917" /><circle cx="135" cy="175" r="4" fill="#1c1917" />
                  <rect x="80" y="80" width="40" height="40" rx="8" fill="#d97706" />
                  <text x="100" y="106" font-size="22" font-weight="bold" fill="#ffffff" text-anchor="middle" font-family="sans-serif">₹</text>
                </svg>
              </div>
              <div class="upi-details">
                <div class="upi-shop-name">अपना देसी किराना स्टोर</div>
                <div class="upi-id-row"><span>UPI ID:</span> <code>apnakirana@upi</code></div>
                <div class="upi-amount-row">
                  <span>भुगतान राशि:</span>
                  <strong style="color: #064e3b; font-size: 1.25rem;">₹{{ cartTotalAmount }}</strong>
                </div>
                <div class="upi-apps-icons">PhonePe • GPay • Paytm</div>
              </div>
            </div>

            <div class="upi-confirm-check">
              <label>
                <input type="checkbox" v-model="customerForm.upiConfirmed" />
                <span>हाँ, मैंने QR कोड स्कैन करके ₹{{ cartTotalAmount }} का ऑनलाइन भुगतान पूरा कर लिया है (Mark as Paid)</span>
              </label>
            </div>
          </div>

          <div style="background: #ecfdf5; border: 1.5px solid #a7f3d0; border-radius: 10px; padding: 14px; margin-bottom: 18px;">
            <div style="display: flex; justify-content: space-between; font-weight: 900; color: #064e3b; font-size: 1.15rem;">
              <span>कुल भुगतान राशि:</span>
              <span>₹{{ cartTotalAmount }}</span>
            </div>
            <div style="font-size: 0.84rem; color: #047857; font-weight: 700; margin-top: 4px;">
              🎉 इस ऑर्डर पर आपकी कुल बचत: ₹{{ cartTotalSavings }}!
            </div>
          </div>

          <button
            type="submit"
            :disabled="orderSubmitting || (customerForm.paymentMethod === 'UPI / QR Code' && !customerForm.upiConfirmed)"
            class="checkout-btn"
          >
            {{ orderSubmitting ? 'ऑर्डर दर्ज हो रहा है...' : '✅ ऑर्डर कन्फ़र्म करें व पर्चा प्राप्त करें' }}
          </button>
        </form>
      </div>
    </div>

    <!-- ======================================================== -->
    <!-- DESI KIRANA PRINTABLE PARCHA (BILL) MODAL                -->
    <!-- ======================================================== -->
    <div class="modal-overlay" v-if="lastOrderReceipt" @click.self="lastOrderReceipt = null">
      <div class="modal-card printable-area" style="max-width: 480px;">
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px;">
          <span style="font-size: 0.88rem; font-weight: 800; color: #047857;">✅ बिल जनरेट हुआ</span>
          <button class="close-btn" @click="lastOrderReceipt = null">✕</button>
        </div>

        <div class="parcha-receipt">
          <div class="parcha-header">
            <h3>अपना देसी किराना स्टोर</h3>
            <p style="font-size: 0.8rem;">मेन बाजार, स्टेशन रोड • फोन: 98765-43210</p>
            <p style="font-size: 0.85rem; font-weight: bold; margin-top: 4px;">
              दुकान का पक्का बिल (INVOICE)
            </p>
            <div style="display: flex; justify-content: space-between; font-size: 0.76rem; margin-top: 8px;">
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
              ({{ lastOrderReceipt.payment_status === 'Paid' ? '🟢 चुकता' : '🔴 बाकी उधारी' }})
            </div>
          </div>

          <table class="parcha-table">
            <thead>
              <tr>
                <th>सामान विवरण</th>
                <th>मात्रा</th>
                <th>दर (₹)</th>
                <th style="text-align: right;">रकम (₹)</th>
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
              <span>कुल एमआरपी (MRP):</span>
              <span>₹{{ lastOrderReceipt.total_mrp }}</span>
            </div>
            <div style="display: flex; justify-content: space-between; color: #047857; font-weight: bold;">
              <span>किराना छूट (बचत):</span>
              <span>- ₹{{ lastOrderReceipt.total_savings }}</span>
            </div>
            <div style="display: flex; justify-content: space-between; font-size: 1.2rem; font-weight: 900; margin-top: 6px; border-top: 2px solid #000; padding-top: 4px;">
              <span>कुल देय राशि:</span>
              <span>₹{{ lastOrderReceipt.final_amount }}</span>
            </div>
          </div>

          <div style="text-align: center; font-size: 0.78rem; margin-top: 16px; border-top: 1.5px dashed #78716c; padding-top: 8px;">
            🙏 फिर पधारें! धन्यवाद! 🙏
          </div>
        </div>

        <div style="display: flex; gap: 10px; margin-top: 16px; flex-wrap: wrap;">
          <button
            @click="shareOrderOnWhatsApp(lastOrderReceipt)"
            class="whatsapp-share-btn"
          >
            📲 व्हाट्सएप पर पर्चा भेजें
          </button>
          <button
            @click="printParcha"
            style="flex: 1; min-width: 130px; padding: 11px; background: #1c1917; color: white; border: none; border-radius: 10px; font-weight: 800; cursor: pointer; display: flex; align-items: center; justify-content: center; gap: 6px;"
          >
            🖨️ प्रिंट (Print)
          </button>
          <button
            @click="lastOrderReceipt = null"
            style="padding: 11px 18px; background: #e7e2d9; color: #1c1917; border: none; border-radius: 10px; font-weight: 800; cursor: pointer;"
          >
            बंद करें
          </button>
        </div>
      </div>
    </div>

    <!-- ======================================================== -->
    <!-- ADD PRODUCT MODAL (ADMIN FEATURE)                        -->
    <!-- ======================================================== -->
    <div class="modal-overlay" v-if="showAddProductModal" @click.self="showAddProductModal = false">
      <div class="modal-card">
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 16px;">
          <h3 style="font-size: 1.25rem; font-weight: 900; color: #064e3b;">
            ➕ नया किराना सामान जोड़ें (Add Product)
          </h3>
          <button class="close-btn" @click="showAddProductModal = false">✕</button>
        </div>

        <form @submit.prevent="submitNewProduct">
          <div class="form-group">
            <label class="form-label">कैटेगरी (Category) *</label>
            <select v-model.number="newProductForm.category_id" required class="form-input">
              <option v-for="cat in categories" :key="cat.id" :value="cat.id">
                {{ cat.name }} ({{ cat.name_hi }})
              </option>
            </select>
          </div>

          <div class="form-group">
            <label class="form-label">अंग्रेजी नाम (English Name) *</label>
            <input type="text" v-model="newProductForm.name" required class="form-input" placeholder="e.g. Masoor Dal Malka" />
          </div>

          <div class="form-group">
            <label class="form-label">हिंदी नाम (Hindi Name) *</label>
            <input type="text" v-model="newProductForm.name_hi" required class="form-input" placeholder="जैसे: मलका मसूर दाल" />
          </div>

          <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 12px;">
            <div class="form-group">
              <label class="form-label">ब्रांड (Brand)</label>
              <input type="text" v-model="newProductForm.brand" class="form-input" placeholder="e.g. Tata, Local, Loose" />
            </div>
            <div class="form-group">
              <label class="form-label">प्रकार (Type)</label>
              <select v-model="newProductForm.is_loose" class="form-input">
                <option :value="true">🌾 खुला राशन (Loose)</option>
                <option :value="false">📦 पैकेट (Packaged)</option>
              </select>
            </div>
          </div>

          <div class="form-group">
            <label class="form-label">विवरण (Description)</label>
            <textarea v-model="newProductForm.description" rows="2" class="form-input"></textarea>
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

          <div class="upi-qr-frame">
            <div class="qr-code-svg-wrap">
              <svg viewBox="0 0 200 200" width="140" height="140">
                <rect width="200" height="200" fill="#ffffff" rx="8" />
                <rect x="15" y="15" width="45" height="45" fill="#1c1917" rx="4" />
                <rect x="22" y="22" width="31" height="31" fill="#ffffff" rx="2" />
                <rect x="28" y="28" width="19" height="19" fill="#047857" rx="2" />
                <rect x="140" y="15" width="45" height="45" fill="#1c1917" rx="4" />
                <rect x="147" y="22" width="31" height="31" fill="#ffffff" rx="2" />
                <rect x="153" y="28" width="19" height="19" fill="#047857" rx="2" />
                <rect x="15" y="140" width="45" height="45" fill="#1c1917" rx="4" />
                <rect x="22" y="147" width="31" height="31" fill="#ffffff" rx="2" />
                <rect x="28" y="153" width="19" height="19" fill="#047857" rx="2" />
                <circle cx="75" cy="25" r="4" fill="#1c1917" /><circle cx="95" cy="25" r="4" fill="#1c1917" /><circle cx="115" cy="25" r="4" fill="#1c1917" />
                <circle cx="85" cy="40" r="4" fill="#1c1917" /><circle cx="105" cy="40" r="4" fill="#047857" /><circle cx="125" cy="40" r="4" fill="#1c1917" />
                <circle cx="25" cy="75" r="4" fill="#1c1917" /><circle cx="45" cy="75" r="4" fill="#1c1917" /><circle cx="25" cy="95" r="4" fill="#1c1917" />
                <circle cx="75" cy="75" r="4" fill="#047857" /><circle cx="90" cy="75" r="4" fill="#1c1917" /><circle cx="110" cy="75" r="4" fill="#1c1917" />
                <circle cx="75" cy="115" r="4" fill="#1c1917" /><circle cx="95" cy="115" r="4" fill="#047857" /><circle cx="115" cy="115" r="4" fill="#1c1917" />
                <circle cx="145" cy="75" r="4" fill="#1c1917" /><circle cx="165" cy="75" r="4" fill="#1c1917" /><circle cx="175" cy="95" r="4" fill="#047857" />
                <circle cx="145" cy="115" r="4" fill="#047857" /><circle cx="165" cy="115" r="4" fill="#1c1917" />
                <circle cx="75" cy="145" r="4" fill="#1c1917" /><circle cx="95" cy="145" r="4" fill="#1c1917" /><circle cx="115" cy="145" r="4" fill="#047857" />
                <circle cx="85" cy="165" r="4" fill="#047857" /><circle cx="105" cy="165" r="4" fill="#1c1917" /><circle cx="135" cy="175" r="4" fill="#1c1917" />
                <rect x="80" y="80" width="40" height="40" rx="8" fill="#d97706" />
                <text x="100" y="106" font-size="22" font-weight="bold" fill="#ffffff" text-anchor="middle" font-family="sans-serif">₹</text>
              </svg>
            </div>
            <div class="upi-details">
              <div class="upi-shop-name">अपना देसी किराना स्टोर</div>
              <div class="upi-id-row"><span>UPI ID:</span> <code>apnakirana@upi</code></div>
              <div class="upi-amount-row">
                <span>बकाया राशि:</span>
                <strong style="color: #b91c1c; font-size: 1.25rem;">₹{{ pendingUpiOrder.final_amount }}</strong>
              </div>
              <div class="upi-apps-icons">PhonePe • GPay • Paytm</div>
            </div>
          </div>

          <p style="font-size: 0.82rem; color: var(--text-muted); margin: 14px 0 16px; text-align: center;">
            UPI ऐप से स्कैन कर ₹{{ pendingUpiOrder.final_amount }} का भुगतान करें, फिर नीचे कन्फ़र्म बटन दबाएं।
          </p>

          <button
            class="checkout-btn"
            @click="confirmUpiPayForCustomerOrder"
          >
            ✅ मैंने भुगतान कर दिया है (Confirm & Mark Paid)
          </button>
        </div>
      </div>
    </div>

    <!-- Floating Sticky Cart Pill (Blinkit / Zepto Style) -->
    <div
      v-if="!isAdminLoggedIn && cart.length > 0 && !isCartOpen"
      class="floating-cart-pill"
      @click="isCartOpen = true"
    >
      <div class="pill-left">
        <div class="pill-badge">🛒 {{ cartTotalQuantity }} आइटम</div>
        <div class="pill-info">
          <span class="pill-amount">₹{{ cartTotalAmount }}</span>
          <span class="pill-savings" v-if="Number(cartTotalSavings) > 0">
            बचत: ₹{{ cartTotalSavings }}
          </span>
        </div>
      </div>
      <div class="pill-right">
        <span>थैला देखें</span>
        <span class="pill-arrow">➔</span>
      </div>
    </div>

    <!-- ======================================================== -->
    <!-- MONTHLY RATION CHECKLIST MODAL (एकमुश्त राशन पर्चा)      -->
    <!-- ======================================================== -->
    <div class="modal-overlay" v-if="showMonthlyParchaModal" @click.self="showMonthlyParchaModal = false">
      <div class="modal-card" style="max-width: 580px;">
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

        <!-- Checklist of monthly staples -->
        <div class="parcha-items-grid">
          <div
            v-for="item in monthlyParchaItems"
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
                <span class="parcha-item-selling">₹{{ item.fallbackPrice }}</span>
                <span class="parcha-item-mrp" v-if="item.mrp > item.fallbackPrice">₹{{ item.mrp }}</span>
              </div>
            </div>
            <div class="parcha-checkbox-wrap">
              <div class="parcha-custom-check">
                <span v-if="item.selected">✓</span>
              </div>
            </div>
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
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue';

const API_BASE = window.location.port === '5173' ? 'http://127.0.0.1:5000/api' : '/api';

// Auth State
const currentUser = ref(null);
const authToken = ref(localStorage.getItem('kirana_token') || '');
const showAuthModal = ref(false);
const authMode = ref('login'); // 'login' | 'register' | 'admin'
const authError = ref('');
const authSubmitting = ref(false);

const authForm = ref({ email: '', password: '' });
const registerForm = ref({ name: '', email: '', phone: '', password: '', address: '' });

// Customer Account Modal State
const showAccountModal = ref(false);
const customerActiveTab = ref('orders'); // 'orders' | 'profile'
const customerOrders = ref([]);
const customerOrdersLoading = ref(false);
const profileForm = ref({ name: '', email: '', phone: '', address: '' });

// Admin State
const adminActiveTab = ref('inventory');
const adminSearch = ref('');
const adminOrders = ref([]);
const showAddProductModal = ref(false);
const newProductForm = ref({
  category_id: 1,
  name: '',
  name_hi: '',
  brand: 'Local / Mandi',
  is_loose: true,
  description: '',
  unit_size: '1kg',
  mrp: 100,
  selling_price: 90
});

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

// Cart State
const cart = ref([]);
const isCartOpen = ref(false);
const showCheckoutModal = ref(false);
const orderSubmitting = ref(false);
const lastOrderReceipt = ref(null);

const customerForm = ref({
  name: '',
  phone: '',
  address: '',
  deliverySlot: '⚡ 30 मिनट में (Instant - 30 Mins)',
  paymentMethod: 'Cash on Delivery (COD)',
  upiConfirmed: false
});

const deliverySlotOptions = [
  {
    id: 'instant',
    icon: '⚡',
    title: '30 मिनट में (Instant Delivery)',
    desc: 'ताज़ा व तुरंत आपके दरवाज़े पर',
    label: '⚡ 30 मिनट में (Instant - 30 Mins)'
  },
  {
    id: 'morning',
    icon: '🌅',
    title: 'सुबह का स्लॉट (7:00 - 10:00 AM)',
    desc: 'ताज़ी चाय, दूध व सुबह का नाश्ता',
    label: '🌅 सुबह (7:00 AM - 10:00 AM)'
  },
  {
    id: 'evening',
    icon: '🌆',
    title: 'शाम का स्लॉट (6:00 - 9:00 PM)',
    desc: 'रात के खाने व अगले दिन का राशन',
    label: '🌆 शाम (6:00 PM - 9:00 PM)'
  }
];

// Monthly Ration Checklist State
const showMonthlyParchaModal = ref(false);
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
    image: '/products/colgate-paste.jpg'
  }
]);

const monthlyParchaTotal = computed(() => {
  return monthlyParchaItems.value
    .filter(it => it.selected)
    .reduce((sum, it) => sum + it.fallbackPrice, 0);
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

// Admin Orders Ledger Filter
const adminOrderFilter = ref('all');

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
        profileForm.value = { ...data.user };
        customerForm.value.name = data.user.name;
        customerForm.value.phone = data.user.phone;
        customerForm.value.address = data.user.address;
      }
    } else {
      logout();
    }
  } catch (err) {
    console.error('Auth error:', err);
  }
}

function openAuthModal(mode = 'login') {
  authMode.value = mode;
  authError.value = '';
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
    const data = await res.json();
    if (res.ok) {
      authToken.value = data.token;
      localStorage.setItem('kirana_token', data.token);
      currentUser.value = data.user;
      profileForm.value = { ...data.user };
      customerForm.value.name = data.user.name;
      customerForm.value.phone = data.user.phone;
      customerForm.value.address = data.user.address;
      showAuthModal.value = false;
      authForm.value = { email: '', password: '' };
      showToast(`नमस्ते ${data.user.name}! लॉगिन सफल रहा।`);
      if (data.user.role === 'admin') {
        loadAdminOrders();
      }
    } else {
      authError.value = data.error || 'लॉगिन असफल रहा। कृपया पुनः प्रयास करें।';
    }
  } catch (err) {
    authError.value = 'सर्वर से संपर्क नहीं हो पाया।';
  } finally {
    authSubmitting.value = false;
  }
}

async function handleRegister() {
  const phone = registerForm.value.phone.trim();
  const phoneRegex = /^[6-9]\d{9}$/;
  if (!phoneRegex.test(phone)) {
    authError.value = 'कृपया 10 अंकों का सही भारतीय मोबाइल नंबर दर्ज करें (6, 7, 8 या 9 से शुरू)';
    return;
  }
  authSubmitting.value = true;
  authError.value = '';
  try {
    const res = await fetch(`${API_BASE}/auth/register`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(registerForm.value)
    });
    const data = await res.json();
    if (res.ok) {
      authToken.value = data.token;
      localStorage.setItem('kirana_token', data.token);
      currentUser.value = data.user;
      profileForm.value = { ...data.user };
      customerForm.value.name = data.user.name;
      customerForm.value.phone = data.user.phone;
      customerForm.value.address = data.user.address;
      showAuthModal.value = false;
      showToast(`स्वागत है ${data.user.name}! खाता बन गया है।`);
    } else {
      authError.value = data.error || 'रजिस्ट्रेशन असफल रहा।';
    }
  } catch (err) {
    authError.value = 'सर्वर से संपर्क नहीं हो पाया।';
  } finally {
    authSubmitting.value = false;
  }
}

function logout() {
  authToken.value = '';
  currentUser.value = null;
  localStorage.removeItem('kirana_token');
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
  customerOrdersLoading.value = true;
  try {
    const res = await fetch(`${API_BASE}/customer/orders`, {
      headers: { 'Authorization': `Bearer ${authToken.value}` }
    });
    if (res.ok) {
      customerOrders.value = await res.json();
    }
  } catch (err) {
    console.error('Customer orders error:', err);
  } finally {
    customerOrdersLoading.value = false;
  }
}

function openUpiPayForCustomerOrder(order) {
  pendingUpiOrder.value = order;
  showUpiPayModal.value = true;
}

async function confirmUpiPayForCustomerOrder() {
  if (!pendingUpiOrder.value) return;
  try {
    const res = await fetch(`${API_BASE}/customer/orders/${pendingUpiOrder.value.id}/pay`, {
      method: 'POST',
      headers: { 'Authorization': `Bearer ${authToken.value}` }
    });
    if (res.ok) {
      showToast(`🎉 ₹${pendingUpiOrder.value.final_amount} का भुगतान सफल! बिल चुकता कर दिया गया।`);
      showUpiPayModal.value = false;
      pendingUpiOrder.value = null;
      loadCustomerOrders();
    } else {
      const err = await res.json();
      alert(err.error || 'भुगतान दर्ज नहीं हो सका');
    }
  } catch (err) {
    console.error('Pay error:', err);
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
        phone: profileForm.value.phone,
        address: profileForm.value.address
      })
    });
    if (res.ok) {
      const data = await res.json();
      currentUser.value = data.user;
      customerForm.value.name = data.user.name;
      customerForm.value.phone = data.user.phone;
      customerForm.value.address = data.user.address;
      showToast('✅ पता व प्रोफाइल अपडेट हो गया!');
      showAccountModal.value = false;
    }
  } catch (err) {
    console.error('Profile update error:', err);
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

async function fetchProducts() {
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
    }
  } catch (err) {
    console.error('Products fetch error:', err);
  } finally {
    loading.value = false;
  }
}

let debounceTimer = null;
function debounceFetchProducts() {
  clearTimeout(debounceTimer);
  debounceTimer = setTimeout(() => { fetchProducts(); }, 300);
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

function getCustomWeightPrice(prod) {
  const rate = getBasePerKgRate(prod);
  const wt = parseFloat(customWeightInputs.value[prod.id]) || 0;
  return (Math.round(rate * wt * 100) / 100).toFixed(2);
}

function addCustomWeightItemToCart(prod) {
  const wt = parseFloat(customWeightInputs.value[prod.id]);
  if (!wt || wt <= 0) {
    showToast('कृपया सही वजन दर्ज करें (उदा: 1.5, 4.5, 10 kg)');
    return;
  }
  const rate = getBasePerKgRate(prod);
  const mrpRate = getBasePerKgMrp(prod);
  const subtotal = Math.round(rate * wt * 100) / 100;
  const mrp = Math.round(mrpRate * wt * 100) / 100;
  const unitSize = `${wt} kg`;

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
      quantity: 1
    });
  }
  showToast(`🛒 ${prod.name} (${unitSize} - ₹${subtotal}) थैले में जोड़ा गया!`);
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
    return acc + (item.variant.selling_price * item.quantity);
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
    alert('कृपया 10 अंकों का सही भारतीय मोबाइल नंबर दर्ज करें (उदा: 9876543210)');
    return;
  }

  if (customerForm.value.paymentMethod === 'UPI / QR Code' && !customerForm.value.upiConfirmed) {
    alert('कृपया QR कोड स्कैन करके पेमेंट करने के बाद चेकबॉक्स टिक करें।');
    return;
  }

  orderSubmitting.value = true;
  try {
    const headers = { 'Content-Type': 'application/json' };
    if (authToken.value) {
      headers['Authorization'] = `Bearer ${authToken.value}`;
    }

    const deliveryAddressWithSlot = customerForm.value.deliverySlot
      ? `${customerForm.value.address} [⏰ समय: ${customerForm.value.deliverySlot}]`
      : customerForm.value.address;

    const payload = {
      customer_name: customerForm.value.name,
      customer_phone: phone,
      customer_address: deliveryAddressWithSlot,
      payment_method: customerForm.value.paymentMethod,
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

    const res = await fetch(`${API_BASE}/orders`, {
      method: 'POST',
      headers,
      body: JSON.stringify(payload)
    });

    if (res.ok) {
      const data = await res.json();
      lastOrderReceipt.value = data.order;
      cart.value = [];
      customerForm.value.upiConfirmed = false;
      showCheckoutModal.value = false;
      showToast(`🎉 ऑर्डर पक्का हुआ! बिल संख्या: ${data.order.order_number}`);
      fetchProducts();
      if (currentUser.value) {
        loadCustomerOrders();
      }
    } else {
      const err = await res.json();
      alert(err.error || 'ऑर्डर दर्ज नहीं हो सका');
    }
  } catch (err) {
    console.error('Order error:', err);
    alert('सर्वर से संपर्क नहीं हो पाया।');
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

  const text = 
`🌾 *अपना देसी किराना स्टोर - ऑर्डर पर्चा*
━━━━━━━━━━━━━━━━━━━━
📄 *पर्चा संख्या:* ${order.order_number}
📅 *दिनांक:* ${order.created_at}
👤 *ग्राहक:* ${order.customer_name} (📞 ${order.customer_phone})
📍 *पता:* ${order.customer_address}
💳 *भुगतान:* ${order.payment_method} (${order.payment_status === 'Paid' ? '🟢 चुकता' : '🔴 बाकी उधारी'})

📦 *सामान सूची:*
${itemsText}
━━━━━━━━━━━━━━━━━━━━
💵 *कुल एमआरपी:* ₹${order.total_mrp}
🎉 *किराना बचत:* -₹${order.total_savings}
💰 *कुल देय राशि:* *₹${order.final_amount}*

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

    const matchedProduct = products.value.find(p => 
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
        existing.quantity += 1;
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
          subtotal: subtotal,
          mrp: mrp,
          quantity: 1
        });
      }
      addedCount++;
    } else {
      if (matchedProduct && matchedProduct.variants && matchedProduct.variants.length > 0) {
        const variant = matchedProduct.variants.find(v => v.unit_size.toLowerCase().includes(mItem.variantUnit.toLowerCase())) || matchedProduct.variants[0];
        addToCart(matchedProduct, variant);
        addedCount++;
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
        addToCart(prodObj, fallbackVariant);
        addedCount++;
      }
    }
  });

  showToast(`🎉 मासिक राशन के ${addedCount} सामान आपके थैले में जोड़े गए!`);
  showMonthlyParchaModal.value = false;
  isCartOpen.value = true;
}

// Admin Operations (Protected)
const filteredAdminProducts = computed(() => {
  if (!adminSearch.value.trim()) return products.value;
  const q = adminSearch.value.toLowerCase();
  return products.value.filter(p =>
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
        stock_quantity: variant.stock_quantity
      })
    });

    if (res.ok) {
      showToast(`✅ ${variant.unit_size} की नई दर ₹${variant.selling_price} SQLite में सुरक्षित रूप से सेव हुई!`);
    } else {
      const err = await res.json();
      alert(err.error || 'त्रुटि हुई');
    }
  } catch (err) {
    console.error('Update error:', err);
  }
}

async function loadAdminOrders() {
  adminActiveTab.value = 'orders';
  try {
    const res = await fetch(`${API_BASE}/admin/orders`, {
      headers: { 'Authorization': `Bearer ${authToken.value}` }
    });
    if (res.ok) {
      adminOrders.value = await res.json();
    }
  } catch (err) {
    console.error('Admin orders fetch error:', err);
  }
}

const unpaidAdminOrders = computed(() => {
  return adminOrders.value.filter(o => o.payment_status !== 'Paid');
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

const displayedAdminOrders = computed(() => {
  if (adminOrderFilter.value === 'unpaid') return unpaidAdminOrders.value;
  if (adminOrderFilter.value === 'paid') return paidAdminOrders.value;
  if (adminOrderFilter.value === 'cod') return codAdminOrders.value;
  if (adminOrderFilter.value === 'upi') return upiAdminOrders.value;
  return adminOrders.value;
});

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
      showToast(`✅ ऑर्डर ${order.order_number} चुकता (Paid) दर्ज कर दिया गया!`);
    } else {
      const err = await res.json();
      alert(err.error || 'त्रुटि हुई');
    }
  } catch (err) {
    console.error('Status update error:', err);
  }
}

async function deleteAdminProduct(productId, productName) {
  if (confirm(`क्या आप सच में '${productName}' को दुकान से हटाना चाहते हैं?`)) {
    try {
      const res = await fetch(`${API_BASE}/products/${productId}`, {
        method: 'DELETE',
        headers: { 'Authorization': `Bearer ${authToken.value}` }
      });
      if (res.ok) {
        showToast(`🗑️ '${productName}' दुकान से हटा दिया गया!`);
        fetchProducts();
      } else {
        const err = await res.json();
        alert(err.error || 'त्रुटि हुई');
      }
    } catch (err) {
      console.error('Delete product error:', err);
    }
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
      showToast(`✅ ऑर्डर ${order.order_number} का स्टेटस अपडेट हुआ!`);
    }
  } catch (err) {
    console.error('Status update error:', err);
  }
}

async function submitNewProduct() {
  try {
    const payload = {
      category_id: newProductForm.value.category_id,
      name: newProductForm.value.name,
      name_hi: newProductForm.value.name_hi,
      brand: newProductForm.value.brand,
      is_loose: newProductForm.value.is_loose,
      description: newProductForm.value.description,
      image_url: '/products/chakki-atta.jpg',
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
      showToast(`✅ नया सामान '${newProductForm.value.name}' स्टोर में जोड़ा गया!`);
      showAddProductModal.value = false;
      newProductForm.value.name = '';
      newProductForm.value.name_hi = '';
      fetchProducts();
      fetchCategories();
    }
  } catch (err) {
    console.error('Add product error:', err);
  }
}

async function confirmResetSeed() {
  if (confirm('क्या आप सच में पूरे स्टोर को डिफ़ॉल्ट देसी किराना सामान पर रीसेट करना चाहते हैं?')) {
    try {
      const res = await fetch(`${API_BASE}/reset-seed`, {
        method: 'POST',
        headers: { 'Authorization': `Bearer ${authToken.value}` }
      });
      if (res.ok) {
        showToast('🔄 स्टोर सफलतापूर्वक रीसेट हो गया!');
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
    'household-cleaning': '🧼'
  };
  return map[slug] || '📦';
}

onMounted(() => {
  checkAuth();
  fetchCategories();
  fetchProducts();

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
});
</script>
