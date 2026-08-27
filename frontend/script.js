// ShopPilot AI - Frontend Controller & API Integration
let currentSessionId = "session_" + Math.random().toString(36).substring(2, 9);
let comparisonList = [];
let catalogData = [];

document.addEventListener("DOMContentLoaded", () => {
  checkBackendHealth();
  loadCatalog();
  loadAnalytics();
});

// TAB SWITCHING
function switchTab(tabId) {
  document.querySelectorAll(".tab-pane").forEach(pane => pane.classList.remove("active"));
  document.querySelectorAll(".nav-link").forEach(link => link.classList.remove("active"));

  const targetPane = document.getElementById(`tab-${tabId}`);
  if (targetPane) targetPane.classList.add("active");

  const matchingBtn = Array.from(document.querySelectorAll(".nav-link")).find(btn =>
    btn.getAttribute("onclick")?.includes(`'${tabId}'`)
  );
  if (matchingBtn) matchingBtn.classList.add("active");

  if (tabId === "compare") renderComparisonView();
  if (tabId === "analytics") loadAnalytics();
}

// HEALTH CHECK
async function checkBackendHealth() {
  const statusEl = document.getElementById("backend-status");
  try {
    const res = await fetch("/health");
    if (res.ok) {
      const data = await res.json();
      statusEl.textContent = `Online (${data.catalog_size} items)`;
    } else {
      statusEl.textContent = "Offline";
    }
  } catch (err) {
    statusEl.textContent = "Offline";
  }
}

// 1. HERO PRESETS
function handleHeroEnter(e) {
  if (e.key === "Enter") submitHeroQuery();
}

function submitHeroQuery() {
  const input = document.getElementById("hero-input");
  const query = input.value.trim();
  if (!query) return;
  input.value = "";
  switchTab("chat");
  document.getElementById("chat-input").value = query;
  sendChatMessage();
}

function askPreset(text) {
  switchTab("chat");
  document.getElementById("chat-input").value = text;
  sendChatMessage();
}

// 2. CHAT & AGENT COMMUNICATION
function handleChatEnter(e) {
  if (e.key === "Enter") sendChatMessage();
}

async function sendChatMessage() {
  const input = document.getElementById("chat-input");
  const msg = input.value.trim();
  if (!msg) return;

  input.value = "";
  appendUserMessage(msg);

  const feed = document.getElementById("chat-feed");
  const loadingId = "loading-" + Date.now();
  appendLoadingBubble(loadingId);

  try {
    const res = await fetch("/api/chat", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ message: msg, session_id: currentSessionId }),
    });

    const loadingEl = document.getElementById(loadingId);
    if (loadingEl) loadingEl.remove();

    if (!res.ok) {
      appendAgentText("I encountered an error processing your request. Please try again.");
      return;
    }

    const data = await res.json();
    appendAgentResponse(data);
  } catch (err) {
    const loadingEl = document.getElementById(loadingId);
    if (loadingEl) loadingEl.remove();
    appendAgentText("Network connection error. Is the backend server running?");
  }
}

function appendUserMessage(text) {
  const feed = document.getElementById("chat-feed");
  const div = document.createElement("div");
  div.className = "message message-user";
  div.innerHTML = `<div class="msg-body"><div class="msg-text">${escapeHtml(text)}</div></div>`;
  feed.appendChild(div);
  feed.scrollTop = feed.scrollHeight;
}

function appendLoadingBubble(id) {
  const feed = document.getElementById("chat-feed");
  const div = document.createElement("div");
  div.id = id;
  div.className = "message message-agent";
  div.innerHTML = `
    <div class="msg-avatar">⚡</div>
    <div class="msg-body">
      <div class="msg-text"><em>ShopPilot AI is planning and querying the catalog...</em></div>
    </div>`;
  feed.appendChild(div);
  feed.scrollTop = feed.scrollHeight;
}

function appendAgentText(text) {
  const feed = document.getElementById("chat-feed");
  const div = document.createElement("div");
  div.className = "message message-agent";
  div.innerHTML = `
    <div class="msg-avatar">⚡</div>
    <div class="msg-body">
      <div class="msg-text">${escapeHtml(text)}</div>
    </div>`;
  feed.appendChild(div);
  feed.scrollTop = feed.scrollHeight;
}

function appendAgentResponse(data) {
  const feed = document.getElementById("chat-feed");
  const div = document.createElement("div");
  div.className = "message message-agent";

  // Build Tool Execution Badges
  let toolsHtml = "";
  if (data.tools_used && data.tools_used.length > 0) {
    toolsHtml = `<div class="tool-badge-row">` +
      data.tools_used.map(t => `<span class="tool-badge">⚡ Tool: ${escapeHtml(t.tool_name)}</span>`).join("") +
      `</div>`;
  }

  // Format Text Reply with Markdown bold support
  let formattedReply = escapeHtml(data.reply).replace(/\*\*(.*?)\*\*/g, "<strong>$1</strong>");

  // Product Cards HTML
  let cardsHtml = "";
  if (data.products && data.products.length > 0) {
    cardsHtml = `<div class="chat-cards-grid">` +
      data.products.map(rp => renderProductCard(rp.product, rp.rank, rp.scores)).join("") +
      `</div>`;
  }

  div.innerHTML = `
    <div class="msg-avatar">⚡</div>
    <div class="msg-body">
      ${toolsHtml}
      <div class="msg-text">${formattedReply}</div>
      ${cardsHtml}
    </div>`;

  feed.appendChild(div);
  feed.scrollTop = feed.scrollHeight;
}

function renderProductCard(p, rank = null, scores = null) {
  const isCompared = comparisonList.includes(p.product_id);
  const rankHtml = rank ? `<span class="card-rank-badge">Rank #${rank}</span>` : "";
  const featuresHtml = (p.features || []).slice(0, 3).map(f => `<span class="card-feature-pill">${escapeHtml(f)}</span>`).join("");
  
  let scoreBox = "";
  if (scores) {
    const scorePct = Math.round(scores.final_score * 100);
    scoreBox = `
      <div class="score-breakdown-box">
        <strong>Match Score: ${scorePct}%</strong> — ${escapeHtml(scores.explanation)}
      </div>`;
  }

  return `
    <div class="product-card" id="card-${p.product_id}">
      <div>
        <div class="card-header-row">
          <span class="card-brand">${escapeHtml(p.brand)}</span>
          ${rankHtml}
        </div>
        <h4 class="card-title">${escapeHtml(p.product_name)}</h4>
        <div class="card-price-row">
          <span class="card-price">₹${p.price.toLocaleString("en-IN")}</span>
          <span class="card-rating">★ ${p.rating} (${p.review_count.toLocaleString("en-IN")})</span>
        </div>
        <div class="card-features-list">
          ${featuresHtml}
        </div>
        ${scoreBox}
      </div>
      <div class="card-actions">
        <button class="btn-secondary btn-sm" onclick="toggleCompare('${p.product_id}')">
          ${isCompared ? "✓ Compared" : "+ Add to Compare"}
        </button>
      </div>
    </div>`;
}

function clearChat() {
  currentSessionId = "session_" + Math.random().toString(36).substring(2, 9);
  document.getElementById("chat-feed").innerHTML = `
    <div class="message message-agent">
      <div class="msg-avatar">⚡</div>
      <div class="msg-body">
        <div class="msg-text">
          Session cleared! What would you like to explore next?
        </div>
      </div>
    </div>`;
}

// 3. CATALOG & FILTERS
async function loadCatalog() {
  try {
    const res = await fetch("/api/products?limit=60");
    if (res.ok) {
      const data = await res.json();
      catalogData = data.products || [];
      renderCatalogGrid(catalogData);
    }
  } catch (err) {
    console.error("Failed to load catalog:", err);
  }
}

function renderCatalogGrid(products) {
  const grid = document.getElementById("product-grid");
  const countEl = document.getElementById("catalog-count-text");
  countEl.textContent = `Showing ${products.length} verified products`;

  if (products.length === 0) {
    grid.innerHTML = `<div class="empty-state"><h3>No products match your filters.</h3></div>`;
    return;
  }

  grid.innerHTML = products.map(p => renderProductCard(p)).join("");
}

async function applyFilters() {
  const category = document.getElementById("filter-category").value;
  const maxPriceVal = document.getElementById("filter-max-price").value;
  const maxPrice = maxPriceVal ? parseFloat(maxPriceVal) : null;
  const minRatingVal = document.getElementById("filter-rating").value;
  const minRating = minRatingVal ? parseFloat(minRatingVal) : null;
  const sortBy = document.getElementById("filter-sort").value;

  try {
    const res = await fetch("/api/search", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        category: category || null,
        max_price: maxPrice,
        min_rating: minRating,
        sort_by: sortBy,
        top_n: 50,
      }),
    });
    if (res.ok) {
      const data = await res.json();
      renderCatalogGrid(data.products || []);
    }
  } catch (err) {
    console.error("Filter search failed:", err);
  }
}

function resetFilters() {
  document.getElementById("filter-category").value = "";
  document.getElementById("filter-max-price").value = "";
  document.getElementById("filter-rating").value = "";
  document.getElementById("filter-sort").value = "rating_desc";
  loadCatalog();
}

// 4. COMPARISON
function toggleCompare(productId) {
  const idx = comparisonList.indexOf(productId);
  if (idx > -1) {
    comparisonList.splice(idx, 1);
  } else {
    if (comparisonList.length >= 4) {
      alert("You can compare up to 4 products at once.");
      return;
    }
    comparisonList.push(productId);
  }
  updateCompareBadge();
  // Re-render open catalog cards
  if (document.getElementById("tab-search").classList.contains("active")) {
    applyFilters();
  }
}

function updateCompareBadge() {
  document.getElementById("compare-badge").textContent = comparisonList.length;
}

async function renderComparisonView() {
  const emptyEl = document.getElementById("compare-empty");
  const resEl = document.getElementById("compare-results");

  if (comparisonList.length === 0) {
    emptyEl.style.display = "block";
    resEl.style.display = "none";
    return;
  }

  emptyEl.style.display = "none";
  resEl.style.display = "block";

  try {
    const res = await fetch("/api/compare", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ product_ids: comparisonList }),
    });
    if (res.ok) {
      const data = await res.json();
      document.getElementById("trade-off-text").innerHTML =
        escapeHtml(data.trade_off_summary || "").replace(/\*\*(.*?)\*\*/g, "<strong>$1</strong>").replace(/\n/g, "<br>");

      const matrix = data.comparison_matrix || [];
      const table = document.getElementById("compare-table");

      let headerRow = `<tr><th>Attribute</th>` + matrix.map(m => `<th>${escapeHtml(m.name)} <button class="btn-text" onclick="toggleCompare('${m.product_id}'); renderComparisonView();">✕</button></th>`).join("") + `</tr>`;
      let brandRow = `<tr><th>Brand</th>` + matrix.map(m => `<td>${escapeHtml(m.brand)}</td>`).join("") + `</tr>`;
      let priceRow = `<tr><th>Price</th>` + matrix.map(m => `<td><strong>${m.price}</strong></td>`).join("") + `</tr>`;
      let ratingRow = `<tr><th>Rating</th>` + matrix.map(m => `<td>${m.rating} (${m.reviews} reviews)</td>`).join("") + `</tr>`;
      let availRow = `<tr><th>Stock</th>` + matrix.map(m => `<td>${m.availability}</td>`).join("") + `</tr>`;
      let featRow = `<tr><th>Key Features</th>` + matrix.map(m => `<td>${(m.features || []).join(", ")}</td>`).join("") + `</tr>`;
      let descRow = `<tr><th>Description</th>` + matrix.map(m => `<td>${escapeHtml(m.description)}</td>`).join("") + `</tr>`;

      table.innerHTML = headerRow + brandRow + priceRow + ratingRow + availRow + featRow + descRow;
    }
  } catch (err) {
    console.error("Comparison load error:", err);
  }
}

// 5. GROWTH ANALYTICS
async function loadAnalytics() {
  try {
    const res = await fetch("/api/analytics");
    if (!res.ok) return;
    const data = await res.json();

    // KPIs
    if (data.kpis) {
      document.getElementById("kpi-products").textContent = data.kpis.total_products;
      document.getElementById("kpi-brands").textContent = data.kpis.total_brands;
      document.getElementById("kpi-rating").textContent = `${data.kpis.average_rating}★`;
      document.getElementById("kpi-stock").textContent = `${data.kpis.in_stock_rate_pct}%`;
    }

    // Category Chart
    const catChart = document.getElementById("category-chart");
    if (data.category_distribution && catChart) {
      const entries = Object.entries(data.category_distribution);
      const maxVal = Math.max(...entries.map(e => e[1])) || 1;
      catChart.innerHTML = entries.map(([cat, val]) => `
        <div class="chart-bar-row">
          <span class="chart-bar-label">${escapeHtml(cat)}</span>
          <div class="chart-bar-track">
            <div class="chart-bar-fill" style="width: ${(val / maxVal) * 100}%"></div>
          </div>
          <span class="chart-bar-val">${val}</span>
        </div>
      `).join("");
    }

    // Budget Distribution Chart
    const budgetChart = document.getElementById("budget-chart");
    if (data.budget_distribution && budgetChart) {
      const entries = Object.entries(data.budget_distribution);
      const maxVal = Math.max(...entries.map(e => e[1])) || 1;
      budgetChart.innerHTML = entries.map(([bracket, val]) => `
        <div class="chart-bar-row">
          <span class="chart-bar-label">${escapeHtml(bracket)}</span>
          <div class="chart-bar-track">
            <div class="chart-bar-fill" style="width: ${(val / maxVal) * 100}%"></div>
          </div>
          <span class="chart-bar-val">${val}</span>
        </div>
      `).join("");
    }

    // Catalog Gaps
    const gapsList = document.getElementById("gaps-list");
    if (data.catalog_gaps && gapsList) {
      gapsList.innerHTML = data.catalog_gaps.map(g => `
        <div class="gap-item">
          <div class="gap-title">${escapeHtml(g.gap_title)} <span class="card-rank-badge">${escapeHtml(g.urgency)} Urgency</span></div>
          <div class="gap-desc">${escapeHtml(g.opportunity)}</div>
          <div class="gap-action">🎯 Recommended Action: ${escapeHtml(g.recommended_action)}</div>
        </div>
      `).join("");
    }
  } catch (err) {
    console.error("Failed to load analytics:", err);
  }
}

// UTILITY: Escape HTML to prevent XSS
function escapeHtml(str) {
  if (!str) return "";
  return String(str)
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;")
    .replace(/'/g, "&#039;");
}
