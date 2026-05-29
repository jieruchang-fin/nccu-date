// result.js — 結果頁邏輯

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
        <h3>${labels[i] || `行程 ${i + 1}`}</h3>
        <span class="itin-budget">${itin.budget_range}</span>
      </div>
      <div class="itin-places">
        ${itin.places.map((p, idx) => renderPlace(p, idx + 1)).join("")}
      </div>
      ${itin.tags.length ? `
      <div class="itin-tags">
        ${itin.tags.map((t) => '<span class="tag">#' + t + '</span>').join("")}
      </div>` : ""}
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

function renderPlace(place, num) {
  const indoor = place.indoor ? "🏢 室內" : "🌳 室外";
  const budget = place.budget_max === 0
    ? "免費"
    : place.budget_min + "–" + place.budget_max + " 元";
  const mapsUrl = getMapsUrl(place);

  return '<div class="place-item">' +
    '<div class="place-num">' + num + '</div>' +
    '<div class="place-info">' +
      '<div class="place-name">' + place.name + '</div>' +
      '<div class="place-meta">' +
        '<span>📍 ' + place.area + '</span>' +
        '<span>' + indoor + '</span>' +
        '<span>💰 ' + budget + '</span>' +
      '</div>' +
      (place.reason ? '<div class="place-reason">💬 ' + place.reason + '</div>' : '') +
      '<a class="maps-btn" href="' + mapsUrl + '" target="_blank" rel="noopener">🗺 在 Google Maps 開啟</a>' +
    '</div>' +
  '</div>';
}
