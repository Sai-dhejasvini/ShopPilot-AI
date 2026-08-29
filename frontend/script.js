// ShopPilot AI - Premium Frontend Controller
let currentSessionId = "session_" + Math.random().toString(36).substring(2, 9);
let comparisonList = [];
let catalogData = [];

document.addEventListener("DOMContentLoaded", () => {
  checkBackendHealth();
  loadCatalog();
  loadAnalytics();
  
  // Set initial page
  navigateTo('assistant');
});

// ---- NAVIGATION & SIDEBAR ----
function navigateTo(pageId) {
  // Update nav UI
  document.querySelectorAll('.nav-item').forEach(el => el.classList.remove('active'));
  const navItem = document.getElementById(`nav-${pageId}`);
  if (navItem) navItem.classList.add('active');

  // Update page visibility
  document.querySelectorAll('.page').forEach(el => el.classList.remove('active'));
  const page = document.getElementById(`page-${pageId}`);
  if (page) page.classList.add('active');

  // Update header title
  const titles = {
    'assistant': 'AI Assistant',
    'discover': 'Discover Products',
    'compare': 'Product Comparison',
    'analytics': 'Commerce Analytics',
    'architecture': 'System Architecture'
  };
  document.getElementById('page-title').textContent = titles[pageId] || 'ShopPilot AI';

  // Specific page logic
  if (pageId === 'compare') renderComparisonView();
  if (pageId === 'analytics') loadAnalytics();
  
  // Close sidebar on mobile after navigation
  if (window.innerWidth <= 1024) {
    closeSidebar();
  }
}

function toggleSidebar() {
  document.getElementById('sidebar').classList.toggle('open');
  document.getElementById('sidebar-overlay').classList.toggle('visible');
}

function closeSidebar() {
  document.getElementById('sidebar').classList.remove('open');
  document.getElementById('sidebar-overlay').classList.remove('visible');
}

// ---- HEALTH CHECK ----
async function checkBackendHealth() {
  const sidebarStatus = document.getElementById("sidebar-status");
  const headerStatus = document.getElementById("header-status");
  
  try {
    const res = await fetch("/health");
    if (res.ok) {
      const data = await res.json();
      sidebarStatus.textContent = `Online (${data.catalog_size} items)`;
      headerStatus.textContent = "AI Online";
      document.querySelectorAll('.status-dot').forEach(el => el.style.background = 'var(--success)');
    } else {
      setOfflineStatus();
    }
  } catch (err) {
    setOfflineStatus();
  }
}

function setOfflineStatus() {
  document.getElementById("sidebar-status").textContent = "System Offline";
  document.getElementById("header-status").textContent = "Disconnected";
  document.querySelectorAll('.status-dot').forEach(el => el.style.background = 'var(--danger)');
  showToast("Cannot connect to backend server.", "error");
}

// ---- GLOBAL SEARCH ----
function handleGlobalSearch() {
  const input = document.getElementById("global-search-input");
  const query = input.value.trim();
  if (!query) return;
  
  input.value = "";
  navigateTo('assistant');
  
  const chatInput = document.getElementById("chat-input");
  if(chatInput) {
    chatInput.value = query;
    sendChat();
  }
}

// ---- AI COPILOT (CHAT) ----
function askPrompt(text) {
  const input = document.getElementById("chat-input");
  input.value = text;
  sendChat();
}

async function sendChat() {
  const input = document.getElementById("chat-input");
  const msg = input.value.trim();
  if (!msg) return;

  input.value = "";
  appendUserMessage(msg);

  const feed = document.getElementById("chat-feed");
  const loadingId = "loading-" + Date.now();
  appendLoadingBubble(loadingId);

  // Hide suggested prompts once conversation starts
  document.getElementById("suggested-prompts").style.display = 'none';

  try {
    const res = await fetch("/api/chat", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ message: msg, session_id: currentSessionId }),
    });

    const loadingEl = document.getElementById(loadingId);
    if (loadingEl) loadingEl.remove();

    if (!res.ok) {
      appendAgentText("I encountered an error processing your request. Please check the backend server.");
      showToast("Error processing request", "error");
      return;
    }

    const data = await res.json();
    appendAgentResponse(data);
    
    // If products were returned, also update the discovery grid
    if (data.products && data.products.length > 0) {
      updateDiscoveryGrid(data.products);
    }
  } catch (err) {
    const loadingEl = document.getElementById(loadingId);
    if (loadingEl) loadingEl.remove();
    appendAgentText("Network connection error. Is the FastAPI backend running?");
    showToast("Network error", "error");
  }
}

function appendUserMessage(text) {
  const feed = document.getElementById("chat-feed");
  const div = document.createElement("div");
  div.className = "msg msg-user";
  div.innerHTML = `<div class="msg-bubble">${escapeHtml(text)}</div>`;
  feed.appendChild(div);
  feed.scrollTop = feed.scrollHeight;
}

function appendLoadingBubble(id) {
  const feed = document.getElementById("chat-feed");
  const div = document.createElement("div");
  div.id = id;
  div.className = "msg msg-agent";
  div.innerHTML = `
    <div class="msg-avatar">⚡</div>
    <div class="msg-bubble">
      <div class="typing-indicator">
        <div class="typing-dot"></div>
        <div class="typing-dot"></div>
        <div class="typing-dot"></div>
      </div>
    </div>`;
  feed.appendChild(div);
  feed.scrollTop = feed.scrollHeight;
}

function appendAgentText(text) {
  const feed = document.getElementById("chat-feed");
  const div = document.createElement("div");
  div.className = "msg msg-agent";
  div.innerHTML = `
    <div class="msg-avatar">⚡</div>
    <div class="msg-bubble">
      <div>${escapeHtml(text)}</div>
      <div class="msg-timestamp">Just now</div>
    </div>`;
  feed.appendChild(div);
  feed.scrollTop = feed.scrollHeight;
}

function appendAgentResponse(data) {
  const feed = document.getElementById("chat-feed");
  const div = document.createElement("div");
  div.className = "msg msg-agent";
  
  // Format Tool Trace
  let toolsHtml = "";
  if (data.tools_used && data.tools_used.length > 0) {
    toolsHtml = `<div class="tool-trace">` + 
      data.tools_used.map(t => `
        <div class="tool-step">
          <svg class="step-icon" viewBox="0 0 20 20" fill="currentColor"><path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clip-rule="evenodd"/></svg>
          Executed: ${escapeHtml(t.tool_name)}
        </div>
      `).join("") + 
      `</div>`;
  }
  
  // Format Requirements
  let reqsHtml = "";
  if (data.requirement) {
    const reqs = [];
    if (data.requirement.category) reqs.push(`Category: ${data.requirement.category}`);
    if (data.requirement.max_price) reqs.push(`Max: ₹${data.requirement.max_price.toLocaleString()}`);
    if (data.requirement.min_rating) reqs.push(`Min Rating: ${data.requirement.min_rating}★`);
    if (data.requirement.required_features && data.requirement.required_features.length > 0) {
      data.requirement.required_features.forEach(f => reqs.push(`Feature: ${f}`));
    }
    
    if (reqs.length > 0) {
      reqsHtml = `<div class="req-badges">` + 
        reqs.map(r => `<span class="req-badge">${escapeHtml(r)}</span>`).join("") + 
        `</div>`;
    }
  }

  // Format main reply (bold markdown parsing)
  let formattedReply = escapeHtml(data.reply)
    .replace(/\*\*(.*?)\*\*/g, "<strong>$1</strong>")
    .replace(/\n/g, "<br>");
    
  let productsFound = "";
  if (data.products && data.products.length > 0) {
    productsFound = `<div style="margin-top:0.75rem; font-size:0.75rem; color:var(--text-muted); font-weight:600;">Found ${data.products.length} products (check Discovery panel) →</div>`;
  }

  div.innerHTML = `
    <div class="msg-avatar">⚡</div>
    <div class="msg-bubble">
      ${toolsHtml}
      ${reqsHtml}
      <div style="line-height:1.6;">${formattedReply}</div>
      ${productsFound}
      <div class="msg-timestamp">Just now</div>
    </div>`;
    
  feed.appendChild(div);
  feed.scrollTop = feed.scrollHeight;
}

function clearChat() {
  currentSessionId = "session_" + Math.random().toString(36).substring(2, 9);
  const feed = document.getElementById("chat-feed");
  feed.innerHTML = `
    <div class="msg msg-agent">
      <div class="msg-avatar">⚡</div>
      <div class="msg-bubble">
        <div>Session cleared! What would you like to explore next?</div>
        <div class="msg-timestamp">Just now</div>
      </div>
    </div>`;
  
  document.getElementById("suggested-prompts").style.display = 'flex';
  document.getElementById("discovery-grid").innerHTML = `
    <div class="empty-state">
      <div class="empty-state-icon">🔍</div>
      <h3>No products yet</h3>
      <p>Ask the AI Assistant to find products for you.</p>
    </div>`;
  document.getElementById("discovery-count").textContent = "Ask AI to discover products";
  
  showToast("Session memory cleared", "info");
}

// ---- PRODUCT CARDS & DISCOVERY ----
function updateDiscoveryGrid(rankedProducts) {
  const grid = document.getElementById("discovery-grid");
  const countEl = document.getElementById("discovery-count");
  
  if (!rankedProducts || rankedProducts.length === 0) {
    grid.innerHTML = `<div class="empty-state"><h3>No products match</h3><p>Try relaxing your constraints.</p></div>`;
    countEl.textContent = "0 products found";
    return;
  }
  
  countEl.textContent = `${rankedProducts.length} top matches found`;
  grid.innerHTML = rankedProducts.map(rp => renderPremiumCard(rp.product, rp.rank, rp.scores)).join("");
}

function renderPremiumCard(p, rank = null, scores = null) {
  const isCompared = comparisonList.includes(p.product_id);
  const rankHtml = rank ? `<div class="card-rank">Rank #${rank}</div>` : '';
  
  const inStock = p.availability;
  const stockHtml = `<span class="card-stock ${inStock ? 'in-stock' : 'out-of-stock'}">${inStock ? 'In Stock' : 'Out of Stock'}</span>`;
  
  const featuresHtml = (p.features || []).slice(0, 3)
    .map(f => `<span class="spec-pill">${escapeHtml(f)}</span>`).join("");
    
  let scoreHtml = "";
  if (scores) {
    const finalPct = Math.round(scores.final_score * 100);
    
    // Generate mini-reasons
    let reasonsHtml = "";
    if (scores.budget_fit_score > 0.8) reasonsHtml += `<span class="match-reason budget">Great Price</span>`;
    if (scores.feature_match_score > 0) reasonsHtml += `<span class="match-reason feature">Matches Spec</span>`;
    if (scores.rating_score > 0.8) reasonsHtml += `<span class="match-reason rating">Highly Rated</span>`;
    if (scores.popularity_score > 0.8) reasonsHtml += `<span class="match-reason popularity">Popular</span>`;
    
    scoreHtml = `
      <div class="match-score-box">
        <div class="match-header">
          <span class="match-label">AI Match Score</span>
          <span class="match-pct">${finalPct}%</span>
        </div>
        <div class="match-bar-track">
          <div class="match-bar-fill" style="width: ${finalPct}%"></div>
        </div>
        <div class="match-reasons">
          ${reasonsHtml}
        </div>
      </div>
    `;
  }
  
  // Create safe JSON string for modal
  const pJson = escapeHtml(JSON.stringify({p, scores}));

  return `
    <div class="product-card" id="card-${escapeHtml(p.product_id)}">
      <div class="card-top">
        <div class="card-brand">${escapeHtml(p.brand)}</div>
        ${rankHtml}
      </div>
      <h3 class="card-name">${escapeHtml(p.product_name)}</h3>
      <div class="card-price-row">
        <div class="card-price">₹${p.price.toLocaleString("en-IN")}</div>
        <div class="card-rating">★ ${p.rating} <span class="card-reviews">(${p.review_count.toLocaleString("en-IN")})</span></div>
      </div>
      <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:0.5rem;">
        ${stockHtml}
      </div>
      <div class="card-specs">
        ${featuresHtml}
      </div>
      ${scoreHtml}
      
      <div class="card-actions">
        <button class="btn-primary" style="flex:1;" onclick="openProductModal('${escapeHtml(p.product_id)}', '${encodeURIComponent(JSON.stringify(p))}', '${encodeURIComponent(JSON.stringify(scores || {}))}')">View Details</button>
        <button class="btn-outline ${isCompared ? 'active' : ''}" style="width:auto; min-width:44px;" onclick="toggleCompare('${escapeHtml(p.product_id)}', '${escapeHtml(p.product_name)}')" title="Compare">
          ${isCompared ? '✓' : '⚖️'}
        </button>
      </div>
    </div>
  `;
}

// ---- PRODUCT MODAL ----
function openProductModal(productId, pDataEnc, sDataEnc) {
  try {
    const p = JSON.parse(decodeURIComponent(pDataEnc));
    const scores = JSON.parse(decodeURIComponent(sDataEnc));
    
    const content = document.getElementById("modal-content");
    
    let scoresHtml = "";
    if (scores && Object.keys(scores).length > 0 && scores.final_score !== undefined) {
      const bPct = Math.round((scores.budget_fit_score || 0) * 100);
      const fPct = Math.round((scores.feature_match_score || 0) * 100);
      const rPct = Math.round((scores.rating_score || 0) * 100);
      const pPct = Math.round((scores.popularity_score || 0) * 100);
      const aPct = Math.round((scores.availability_score || 0) * 100);
      
      scoresHtml = `
        <div class="modal-score-section">
          <h4>Match Breakdown</h4>
          
          <div class="modal-score-bar">
            <span class="modal-score-label">Budget Fit</span>
            <div class="modal-score-track"><div class="modal-score-fill budget" style="width: ${bPct}%"></div></div>
            <span class="modal-score-pct">${bPct}%</span>
          </div>
          
          <div class="modal-score-bar">
            <span class="modal-score-label">Feature Match</span>
            <div class="modal-score-track"><div class="modal-score-fill feature" style="width: ${fPct}%"></div></div>
            <span class="modal-score-pct">${fPct}%</span>
          </div>
          
          <div class="modal-score-bar">
            <span class="modal-score-label">Rating</span>
            <div class="modal-score-track"><div class="modal-score-fill rating" style="width: ${rPct}%"></div></div>
            <span class="modal-score-pct">${rPct}%</span>
          </div>
          
          <div class="modal-score-bar">
            <span class="modal-score-label">Popularity</span>
            <div class="modal-score-track"><div class="modal-score-fill popularity" style="width: ${pPct}%"></div></div>
            <span class="modal-score-pct">${pPct}%</span>
          </div>
          
          <div class="modal-explanation">
            <strong>AI Explanation:</strong> ${escapeHtml(scores.explanation || "No explanation provided.")}
          </div>
        </div>
      `;
    }

    const inStock = p.availability;
    
    content.innerHTML = `
      <button class="modal-close" onclick="closeProductModal()">✕</button>
      <div class="modal-brand">${escapeHtml(p.brand)}</div>
      <h2 class="modal-product-name">${escapeHtml(p.product_name)}</h2>
      
      <div style="display:flex; align-items:baseline; gap:1rem; margin-bottom:1.5rem;">
        <span style="font-size:1.75rem; font-weight:800; color:var(--accent);">₹${p.price.toLocaleString("en-IN")}</span>
        <span style="font-size:1rem; font-weight:700; color:var(--amber);">★ ${p.rating} (${p.review_count.toLocaleString()} reviews)</span>
        <span class="card-stock ${inStock ? 'in-stock' : 'out-of-stock'}">${inStock ? 'In Stock' : 'Out of Stock'}</span>
      </div>
      
      <div style="margin-bottom:1.5rem;">
        <h4 style="font-size:0.85rem; color:var(--text-muted); margin-bottom:0.5rem; text-transform:uppercase; letter-spacing:0.05em;">Key Features</h4>
        <div style="display:flex; flex-wrap:wrap; gap:0.4rem;">
          ${(p.features || []).map(f => `<span class="spec-pill" style="font-size:0.8rem; padding:0.3rem 0.6rem;">${escapeHtml(f)}</span>`).join("")}
        </div>
      </div>
      
      <div class="modal-specs-grid">
        <div class="modal-spec">
          <span class="modal-spec-label">Category</span>
          <span class="modal-spec-val">${escapeHtml(p.category)}</span>
        </div>
        <div class="modal-spec">
          <span class="modal-spec-label">Product ID</span>
          <span class="modal-spec-val" style="font-family:monospace; font-size:0.8rem;">${escapeHtml(p.product_id)}</span>
        </div>
      </div>
      
      ${scoresHtml}
      
      <div style="margin-top:1.5rem; padding-top:1.5rem; border-top:1px solid var(--border); display:flex; justify-content:flex-end; gap:0.75rem;">
        <button class="btn-outline" onclick="closeProductModal()">Close</button>
        <button class="btn-primary" onclick="toggleCompare('${escapeHtml(p.product_id)}', '${escapeHtml(p.product_name).replace(/'/g, "\\'")}'); closeProductModal();">
          ${comparisonList.includes(p.product_id) ? 'Remove from Compare' : 'Add to Compare'}
        </button>
      </div>
    `;
    
    document.getElementById("product-modal").classList.add("visible");
  } catch(e) {
    console.error("Error opening modal", e);
    showToast("Error loading product details", "error");
  }
}

function closeProductModal() {
  document.getElementById("product-modal").classList.remove("visible");
}

// Close modal on outside click
document.getElementById("product-modal").addEventListener("click", function(e) {
  if (e.target === this) {
    closeProductModal();
  }
});

// ---- FULL CATALOG (DISCOVER PAGE) ----
async function loadCatalog() {
  const grid = document.getElementById("catalog-grid");
  const countEl = document.getElementById("catalog-count");
  
  // Show skeletons
  grid.innerHTML = Array(8).fill('<div class="skeleton-card skeleton"></div>').join("");
  
  try {
    const res = await fetch("/api/products?limit=60");
    if (res.ok) {
      const data = await res.json();
      catalogData = data.products || [];
      renderCatalogGrid(catalogData);
    }
  } catch (err) {
    console.error("Failed to load catalog:", err);
    grid.innerHTML = `<div class="empty-state"><h3>Error loading catalog</h3></div>`;
  }
}

function renderCatalogGrid(products) {
  const grid = document.getElementById("catalog-grid");
  const countEl = document.getElementById("catalog-count");
  
  countEl.textContent = `Showing ${products.length} verified products`;

  if (products.length === 0) {
    grid.innerHTML = `
      <div class="empty-state" style="grid-column: 1 / -1;">
        <div class="empty-state-icon">🔍</div>
        <h3>No products match filters</h3>
        <button class="btn-outline" style="margin-top:1rem;" onclick="resetFilters()">Clear Filters</button>
      </div>`;
    return;
  }

  grid.innerHTML = products.map(p => renderPremiumCard(p)).join("");
}

async function applyFilters() {
  const category = document.getElementById("filter-category").value;
  const maxPriceVal = document.getElementById("filter-max-price").value;
  const maxPrice = maxPriceVal ? parseFloat(maxPriceVal) : null;
  const minRatingVal = document.getElementById("filter-rating").value;
  const minRating = minRatingVal ? parseFloat(minRatingVal) : null;
  const sortBy = document.getElementById("filter-sort").value;

  const grid = document.getElementById("catalog-grid");
  grid.innerHTML = Array(4).fill('<div class="skeleton-card skeleton"></div>').join("");

  try {
    const res = await fetch("/api/search", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        category: category || null,
        max_price: maxPrice,
        min_rating: minRating,
        sort_by: sortBy,
        top_n: 60,
      }),
    });
    if (res.ok) {
      const data = await res.json();
      renderCatalogGrid(data.products || []);
    }
  } catch (err) {
    console.error("Filter search failed:", err);
    showToast("Search failed", "error");
  }
}

function resetFilters() {
  document.getElementById("filter-category").value = "";
  document.getElementById("filter-max-price").value = "";
  document.getElementById("filter-rating").value = "";
  document.getElementById("filter-sort").value = "rating_desc";
  loadCatalog();
}

// ---- COMPARISON SYSTEM ----
let comparisonNames = {}; // store names for the dock

function toggleCompare(productId, productName) {
  const idx = comparisonList.indexOf(productId);
  if (idx > -1) {
    comparisonList.splice(idx, 1);
    delete comparisonNames[productId];
    showToast("Removed from comparison", "info");
  } else {
    if (comparisonList.length >= 4) {
      showToast("You can compare up to 4 products at once", "error");
      return;
    }
    comparisonList.push(productId);
    if(productName) comparisonNames[productId] = productName;
    showToast("Added to comparison", "success");
  }
  
  updateCompareDock();
  
  // Re-render buttons in catalog and discovery if they are active
  const cards = document.querySelectorAll('.product-card');
  // Simple re-render would be better, but for now we just let the toggle happen
  // If we are on compare page, refresh it
  if (document.getElementById("page-compare").classList.contains("active")) {
    renderComparisonView();
  }
}

function updateCompareDock() {
  const dock = document.getElementById("compare-dock");
  const countEl = document.getElementById("dock-count");
  const badgeEl = document.getElementById("nav-compare-badge");
  const productsList = document.getElementById("dock-products");
  
  countEl.textContent = comparisonList.length;
  badgeEl.textContent = comparisonList.length;
  
  if (comparisonList.length > 0) {
    dock.classList.add("visible");
    badgeEl.style.display = "inline-block";
    
    productsList.innerHTML = comparisonList.map(id => `
      <div class="dock-product-pill">
        ${escapeHtml((comparisonNames[id] || id).substring(0, 15))}...
        <span class="remove-x" onclick="toggleCompare('${escapeHtml(id)}')">✕</span>
      </div>
    `).join("");
  } else {
    dock.classList.remove("visible");
    badgeEl.style.display = "none";
  }
}

function clearComparison() {
  comparisonList = [];
  comparisonNames = {};
  updateCompareDock();
  if (document.getElementById("page-compare").classList.contains("active")) {
    renderComparisonView();
  }
  showToast("Comparison cleared", "info");
}

async function renderComparisonView() {
  const emptyEl = document.getElementById("compare-empty");
  const resEl = document.getElementById("compare-content");

  if (comparisonList.length === 0) {
    emptyEl.style.display = "block";
    resEl.style.display = "none";
    return;
  }

  emptyEl.style.display = "none";
  resEl.style.display = "block";
  
  const table = document.getElementById("compare-table");
  table.innerHTML = `<tr><td colspan="${comparisonList.length + 1}" style="text-align:center; padding:3rem;"><div class="typing-dot" style="display:inline-block;"></div> <div class="typing-dot" style="display:inline-block;"></div></td></tr>`;

  try {
    const res = await fetch("/api/compare", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ product_ids: comparisonList }),
    });
    if (res.ok) {
      const data = await res.json();
      
      // Trade-off text
      document.getElementById("trade-off-text").innerHTML =
        escapeHtml(data.trade_off_summary || "")
        .replace(/\*\*(.*?)\*\*/g, "<strong style='color:var(--text-heading)'>$1</strong>")
        .replace(/\n/g, "<br>");

      const matrix = data.comparison_matrix || [];
      
      // Helper to find best numeric values for highlighting
      const prices = matrix.map(m => parseFloat(m.price.replace(/[^0-9.]/g, '')));
      const ratings = matrix.map(m => parseFloat(m.rating));
      
      const minPrice = Math.min(...prices.filter(p => !isNaN(p)));
      const maxRating = Math.max(...ratings.filter(r => !isNaN(r)));

      let headerRow = `<tr><th>Attribute</th>` + 
        matrix.map(m => `
          <th style="font-size:1rem; color:var(--text-heading);">
            <div style="display:flex; justify-content:space-between; align-items:flex-start;">
              ${escapeHtml(m.name)} 
              <button class="btn-ghost" style="padding:0; min-width:24px; height:24px;" onclick="toggleCompare('${m.product_id}')">✕</button>
            </div>
          </th>
        `).join("") + `</tr>`;
        
      let brandRow = `<tr><th>Brand</th>` + matrix.map(m => `<td><span class="spec-pill">${escapeHtml(m.brand)}</span></td>`).join("") + `</tr>`;
      
      let priceRow = `<tr><th>Price</th>` + matrix.map(m => {
        const val = parseFloat(m.price.replace(/[^0-9.]/g, ''));
        const isBest = val === minPrice && !isNaN(val);
        return `<td class="${isBest ? 'best-val' : ''}" style="font-size:1.1rem;">${m.price} ${isBest ? '<span style="font-size:0.7rem; background:var(--accent-dim); padding:0.1rem 0.3rem; border-radius:3px; margin-left:0.3rem;">BEST</span>' : ''}</td>`;
      }).join("") + `</tr>`;
      
      let ratingRow = `<tr><th>Rating</th>` + matrix.map(m => {
        const val = parseFloat(m.rating);
        const isBest = val === maxRating && !isNaN(val);
        return `<td class="${isBest ? 'best-val' : ''}"><span style="color:var(--amber);">★ ${m.rating}</span> <span style="font-size:0.75rem; color:var(--text-muted);">(${m.reviews} revs)</span> ${isBest ? '<span style="font-size:0.7rem; background:var(--amber-dim); color:var(--amber); padding:0.1rem 0.3rem; border-radius:3px; margin-left:0.3rem;">TOP</span>' : ''}</td>`;
      }).join("") + `</tr>`;
      
      let availRow = `<tr><th>Availability</th>` + matrix.map(m => `<td><span class="card-stock ${m.availability === 'In Stock' ? 'in-stock' : 'out-of-stock'}">${m.availability}</span></td>`).join("") + `</tr>`;
      
      let featRow = `<tr><th>Key Features</th>` + matrix.map(m => `
        <td>
          <ul style="padding-left:1.2rem; margin:0; list-style-type:square; color:var(--text-body);">
            ${(m.features || []).map(f => `<li style="margin-bottom:0.25rem;">${escapeHtml(f)}</li>`).join("")}
          </ul>
        </td>
      `).join("") + `</tr>`;
      
      let descRow = `<tr><th>Description</th>` + matrix.map(m => `<td style="font-size:0.82rem; color:var(--text-muted); line-height:1.6;">${escapeHtml(m.description)}</td>`).join("") + `</tr>`;

      table.innerHTML = headerRow + brandRow + priceRow + ratingRow + availRow + featRow + descRow;
    }
  } catch (err) {
    console.error("Comparison load error:", err);
    table.innerHTML = `<tr><td colspan="5" style="text-align:center; color:var(--danger); padding:2rem;">Error loading comparison data.</td></tr>`;
  }
}

// ---- COMMERCE ANALYTICS ----
async function loadAnalytics() {
  try {
    const res = await fetch("/api/analytics");
    if (!res.ok) return;
    const data = await res.json();

    // 1. Update KPIs (Both main page and sidebar)
    if (data.kpis) {
      const p = data.kpis.total_products;
      const b = data.kpis.total_brands;
      const r = `${data.kpis.average_rating}★`;
      const s = `${data.kpis.in_stock_rate_pct}%`;
      
      // Main page
      const kp = document.getElementById("kpi-products"); if(kp) kp.textContent = p;
      const kb = document.getElementById("kpi-brands"); if(kb) kb.textContent = b;
      const kr = document.getElementById("kpi-rating"); if(kr) kr.textContent = r;
      const ks = document.getElementById("kpi-stock"); if(ks) ks.textContent = s;
      
      // Sidebar
      const mkp = document.getElementById("mini-kpi-products"); if(mkp) mkp.textContent = p;
      const mkb = document.getElementById("mini-kpi-brands"); if(mkb) mkb.textContent = b;
      const mkr = document.getElementById("mini-kpi-rating"); if(mkr) mkr.textContent = data.kpis.average_rating;
      const mks = document.getElementById("mini-kpi-stock"); if(mks) mks.textContent = s;
    }

    // 2. Category Charts
    if (data.category_distribution) {
      const entries = Object.entries(data.category_distribution);
      const maxVal = Math.max(...entries.map(e => e[1])) || 1;
      
      const renderBars = (containerClass) => entries.map(([cat, val]) => `
        <div class="${containerClass}">
          <span class="${containerClass.replace('-row', '-label')}" title="${escapeHtml(cat)}">${escapeHtml(cat)}</span>
          <div class="${containerClass.replace('-row', '-track')}">
            <div class="${containerClass.replace('-row', '-fill')}" style="width: ${(val / maxVal) * 100}%"></div>
          </div>
          <span class="${containerClass.replace('-row', '-val')}">${val}</span>
        </div>
      `).join("");
      
      const mainCat = document.getElementById("full-category-chart");
      if(mainCat) mainCat.innerHTML = renderBars("chart-bar-row");
      
      const miniCat = document.getElementById("mini-category-chart");
      if(miniCat) miniCat.innerHTML = renderBars("mini-bar-row");
    }

    // 3. Budget Charts
    if (data.budget_distribution) {
      const entries = Object.entries(data.budget_distribution);
      const maxVal = Math.max(...entries.map(e => e[1])) || 1;
      
      const renderBars = (containerClass) => entries.map(([bracket, val]) => `
        <div class="${containerClass}">
          <span class="${containerClass.replace('-row', '-label')}" title="${escapeHtml(bracket)}">${escapeHtml(bracket)}</span>
          <div class="${containerClass.replace('-row', '-track')}">
            <div class="${containerClass.replace('-row', '-fill')}" style="width: ${(val / maxVal) * 100}%"></div>
          </div>
          <span class="${containerClass.replace('-row', '-val')}">${val}</span>
        </div>
      `).join("");
      
      const mainBud = document.getElementById("full-budget-chart");
      if(mainBud) mainBud.innerHTML = renderBars("chart-bar-row");
      
      const miniBud = document.getElementById("mini-budget-chart");
      if(miniBud) miniBud.innerHTML = renderBars("mini-bar-row");
    }

    // 4. Catalog Gaps
    const gapsList = document.getElementById("gaps-list");
    if (data.catalog_gaps && gapsList) {
      gapsList.innerHTML = data.catalog_gaps.map(g => {
        const urgencyClass = g.urgency.toLowerCase() === 'high' ? 'high' : 'medium';
        return `
          <div class="gap-item">
            <div class="gap-title">
              ${escapeHtml(g.gap_title)} 
              <span class="gap-urgency ${urgencyClass}">${escapeHtml(g.urgency)}</span>
            </div>
            <div class="gap-desc">${escapeHtml(g.opportunity)}</div>
            <div class="gap-action">🎯 Recommended Action: ${escapeHtml(g.recommended_action)}</div>
          </div>
        `;
      }).join("");
    }
  } catch (err) {
    console.error("Failed to load analytics:", err);
  }
}

// ---- TOAST NOTIFICATIONS ----
function showToast(message, type = "info") {
  const container = document.getElementById("toast-container");
  const toast = document.createElement("div");
  toast.className = `toast ${type}`;
  
  let icon = "ℹ️";
  if (type === "success") icon = "✅";
  if (type === "error") icon = "❌";
  
  toast.innerHTML = `<span>${icon}</span> <span>${escapeHtml(message)}</span>`;
  container.appendChild(toast);
  
  setTimeout(() => {
    toast.style.opacity = "0";
    toast.style.transform = "translateX(30px)";
    toast.style.transition = "all 0.3s ease";
    setTimeout(() => toast.remove(), 300);
  }, 3500);
}

// ---- UTILITY ----
function escapeHtml(str) {
  if (str === null || str === undefined) return "";
  return String(str)
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;")
    .replace(/'/g, "&#039;");
}
