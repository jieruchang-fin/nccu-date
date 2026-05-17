// result.js — 結果頁邏輯（v7 展開式店家版）

document.addEventListener("DOMContentLoaded", () => {
  const raw = sessionStorage.getItem("recommendation");
  if (!raw) { location.href = "/"; return; }

  const data = JSON.parse(raw);
  const { itineraries = [], message = "" } = data;

  document.getElementById("resultCount").textContent = itineraries.length;
  document.getElementById("resultSubtitle").textContent = message;

  if (itineraries.length === 0) {
    document.getElementById("emptyState").style.display = "block";
    return;
  }

  renderItineraries(itineraries);
  document.getElementById("resultActions").style.display = "flex";
});

function renderItineraries(itineraries) {
  const list = document.getElementById("itineraryList");
  const labels = ["💘 首選行程", "🌟 備選行程", "✨ 驚喜行程"];

  itineraries.forEach((itin, i) => {
    const card = document.createElement("div");
    card.className = "itin-card";
    card.innerHTML = `
      <div class="itin-card-header">
        <h3>${labels[i] || "行程 " + (i + 1)}</h3>
        <span class="itin-budget">${itin.budget_range}</span>
      </div>
      <div class="itin-places">
        ${itin.places.map((p, idx) => renderPlace(p, idx + 1, i + "_" + idx)).join("")}
      </div>
      ${itin.tags.length ? '<div class="itin-tags">' + itin.tags.map(t => '<span class="tag">#' + t + '</span>').join("") + '</div>' : ""}
    `;
    list.appendChild(card);
  });
}

function getMapsUrl(place) {
  if (place.lat && place.lng) {
    return "https://www.google.com/maps/search/?api=1&query=" + place.lat + "," + place.lng;
  }
  return "https://www.google.com/maps/search/?api=1&query=" + encodeURIComponent(place.name + " " + (place.address || "台北"));
}

function getShopMapsUrl(shop) {
  if (shop.lat && shop.lng) {
    return "https://www.google.com/maps/search/?api=1&query=" + shop.lat + "," + shop.lng;
  }
  return "https://www.google.com/maps/search/?api=1&query=" + encodeURIComponent(shop.name + " 台北");
}

function renderPlace(place, num, uid) {
  const indoor = place.indoor ? "🏢 室內" : "🌳 室外";
  const budget = place.budget_max === 0 ? "免費" : place.budget_min + "–" + place.budget_max + " 元";
  const mapsUrl = getMapsUrl(place);
  const shops = place.nearby_shops || [];

  const shopsHtml = shops.length ? `
    <div class="expand-btn" id="btn-${uid}" onclick="toggleShops('shops-${uid}', 'btn-${uid}')">
      <span class="expand-icon">▾</span>
      <span>查看附近 ${shops.length} 家推薦店家</span>
    </div>
    <div class="shops-panel" id="shops-${uid}">
      <div class="shops-header">📍 附近同類型好評店家</div>
      ${shops.map(s => renderShop(s)).join("")}
    </div>
  ` : "";

  return `
    <div class="place-item">
      <div class="place-num">${num}</div>
      <div class="place-info">
        <div class="place-name">${place.name}</div>
        <div class="place-meta">
          <span>📍 ${place.area}</span>
          <span>${indoor}</span>
          <span>💰 ${budget}</span>
        </div>
        ${place.reason ? '<div class="place-reason">💬 ' + place.reason + '</div>' : ""}
        <a class="maps-btn" href="${mapsUrl}" target="_blank" rel="noopener">🗺 在 Google Maps 開啟</a>
      </div>
    </div>
    ${shopsHtml}
  `;
}

function renderShop(shop) {
  const mapsUrl = getShopMapsUrl(shop);
  const tags = (shop.tags || []).map(t => '<span class="shop-tag">#' + t + '</span>').join("");
  return `
    <div class="shop-item">
      <div class="shop-info">
        <div class="shop-name">${shop.name}</div>
        <div class="shop-desc">${shop.desc}</div>
        <div class="shop-row">
          ${tags}
          <span class="shop-price">💰 ${shop.price} 元</span>
        </div>
      </div>
      <a class="shop-map-btn" href="${mapsUrl}" target="_blank" rel="noopener">地圖</a>
    </div>
  `;
}

function toggleShops(panelId, btnId) {
  const panel = document.getElementById(panelId);
  const btn = document.getElementById(btnId);
  const isOpen = panel.classList.contains("open");
  panel.classList.toggle("open", !isOpen);
  btn.classList.toggle("open", !isOpen);
  const span = btn.querySelector("span:last-child");
  if (span) span.textContent = isOpen
    ? "查看附近 " + panel.querySelectorAll(".shop-item").length + " 家推薦店家"
    : "收起店家";
}
