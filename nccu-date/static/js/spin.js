// spin.js — 轉盤頁邏輯

let isSpinning = false;
let currentDeg = 0;

document.addEventListener("DOMContentLoaded", () => {
  document.getElementById("spinTrigger")?.addEventListener("click", doSpin);
  document.getElementById("reSpinBtn")?.addEventListener("click", doSpin);
});

async function doSpin() {
  if (isSpinning) return;
  isSpinning = true;

  const btn = document.getElementById("spinTrigger");
  const reBtn = document.getElementById("reSpinBtn");
  if (btn) btn.disabled = true;
  if (reBtn) reBtn.disabled = true;

  // 隱藏舊結果
  document.getElementById("spinResult").style.display = "none";

  // 轉動動畫
  const wheel = document.getElementById("wheel");
  const extraDeg = 1440 + Math.floor(Math.random() * 360);
  currentDeg += extraDeg;
  wheel.style.transform = `rotate(${currentDeg}deg)`;

  // 拿偏好
  const prefs = JSON.parse(sessionStorage.getItem("spinPrefs") || "{}");

  try {
    const res = await fetch("/api/spin", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(prefs),
    });

    await new Promise((r) => setTimeout(r, 3200)); // 等動畫

    if (!res.ok) {
      alert("找不到行程，試試放寬條件");
      return;
    }

    const data = await res.json();
    renderSpinResult(data);
    document.getElementById("spinResult").style.display = "block";
    window.scrollTo({ top: document.body.scrollHeight, behavior: "smooth" });
  } catch (_) {
    alert("發生錯誤，請重試");
  } finally {
    isSpinning = false;
    if (btn) btn.disabled = false;
    if (reBtn) reBtn.disabled = false;
  }
}

function renderSpinResult(itin) {
  const card = document.getElementById("spinResultCard");
  const travel = (itin.places[0]?.travel_info) || {};

  card.innerHTML = `
    <div style="font-size:13px;color:#8B8B8B;margin-bottom:12px">${itin.budget_range}</div>
    ${itin.places.map((p, i) => `
      <div style="display:flex;gap:10px;margin-bottom:14px;align-items:flex-start">
        <div style="width:24px;height:24px;border-radius:50%;background:linear-gradient(135deg,#FF6B9D,#A78BFA);color:#fff;font-size:11px;font-weight:700;display:flex;align-items:center;justify-content:center;flex-shrink:0;margin-top:2px">${i+1}</div>
        <div>
          <div style="font-weight:700;font-size:15px;margin-bottom:3px">${p.name}</div>
          <div style="font-size:12px;color:#8B8B8B">📍 ${p.area} ・ ${p.indoor ? "室內" : "室外"} ・ ${p.budget_max === 0 ? "免費" : p.budget_min + "–" + p.budget_max + " 元"}${travel.duration ? " ・ 🚇 " + travel.duration : ""}</div>
          ${p.reason ? `<div style="font-size:12px;color:#D94F83;background:#FFE0ED;padding:3px 8px;border-radius:6px;margin-top:4px;display:inline-block">💬 ${p.reason}</div>` : ""}
        </div>
      </div>
    `).join("")}
    ${itin.tags.length ? `<div style="display:flex;gap:6px;flex-wrap:wrap;margin-top:8px">${itin.tags.map(t=>`<span style="font-size:11px;padding:3px 10px;border-radius:99px;background:#F9F5FF;color:#A78BFA;border:1px solid #DDD6FE">#${t}</span>`).join("")}</div>` : ""}
  `;
}
