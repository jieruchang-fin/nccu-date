// quiz.js — 問卷邏輯（v5 修正版）

const TOTAL_STEPS = 8;
let currentStep = 1;
let prefs = {
  companion_type: "",
  people_count: 2,
  duration: "",
  time_of_day: "",
  budget: "",
  indoor_pref: "",
  activity_pref: "",
};

// ── 初始化 ───────────────────────────────────────────────────
document.addEventListener("DOMContentLoaded", () => {
  showStep(1);
  detectLocalTime();   // 用瀏覽器本地時間，不用 API
  setupNumberPicker();
  setupBackBtn();
  setupSubmitBtn();
  setupSpinBtn();
});

// ── 用瀏覽器本地時間偵測時段 ─────────────────────────────────
function detectLocalTime() {
  const hour = new Date().getHours(); // 用戶當地時間
  let tod;
  if (hour >= 5 && hour < 12)       tod = "早上";
  else if (hour >= 12 && hour < 18) tod = "下午";
  else                               tod = "晚上";

  const hint = document.getElementById("autoHint");
  if (hint) hint.textContent = "系統偵測到現在是" + tod + "，已幫你預選 ✓";

  document.querySelectorAll('[data-key="time_of_day"]').forEach((btn) => {
    btn.classList.remove("selected");
    if (btn.dataset.value === tod) {
      btn.classList.add("selected");
      prefs.time_of_day = tod;
    }
  });
}

// ── 顯示步驟 ─────────────────────────────────────────────────
function showStep(n) {
  document.querySelectorAll(".step").forEach((s) => s.classList.remove("active"));
  const target = document.querySelector('[data-step="' + n + '"]');
  if (target) target.classList.add("active");

  const pct = ((n - 1) / (TOTAL_STEPS - 1)) * 100;
  document.getElementById("progressBar").style.width = pct + "%";
  document.getElementById("progressLabel").textContent = n + " / " + TOTAL_STEPS;
  document.getElementById("backBtn").style.display = n > 1 ? "block" : "none";

  if (n === 8) updateSummary();
}

function goToStep(n) {
  currentStep = n;
  showStep(n);
}

// ── 點選選項按鈕 → 自動前進 ──────────────────────────────────
document.addEventListener("click", (e) => {
  const btn = e.target.closest(".choice-btn");
  if (!btn) return;

  const key = btn.dataset.key;
  const value = btn.dataset.value;
  if (!key || !value) return;

  document.querySelectorAll('[data-key="' + key + '"]').forEach((b) =>
    b.classList.remove("selected")
  );
  btn.classList.add("selected");
  prefs[key] = value;

  if (key === "companion_type" && value === "個人") {
    prefs.people_count = 1;
    setTimeout(() => goToStep(3), 200);
    return;
  }

  setTimeout(() => advanceFrom(key), 200);
});

function advanceFrom(key) {
  const map = {
    companion_type: 2,
    duration:       4,
    time_of_day:    5,
    budget:         6,
    indoor_pref:    7,
    activity_pref:  8,
  };
  const next = map[key];
  if (next) goToStep(next);
}

// ── 人數選擇器 ───────────────────────────────────────────────
function setupNumberPicker() {
  let count = 2;
  const display = document.getElementById("numDisplay");
  const minus   = document.getElementById("numMinus");
  const plus    = document.getElementById("numPlus");
  const confirm = document.getElementById("numConfirm");
  if (!display) return;

  minus.addEventListener("click", () => {
    if (count > 2) { count--; display.textContent = count; }
  });
  plus.addEventListener("click", () => {
    if (count < 20) { count++; display.textContent = count; }
  });
  confirm.addEventListener("click", () => {
    prefs.people_count = count;
    goToStep(3);
  });
}

// ── 返回按鈕 ─────────────────────────────────────────────────
function setupBackBtn() {
  document.getElementById("backBtn").addEventListener("click", () => {
    if (currentStep > 1) goToStep(currentStep - 1);
  });
}

// ── 確認摘要 ─────────────────────────────────────────────────
function updateSummary() {
  const el = document.getElementById("finalSummary");
  if (!el) return;

  const missing = [];
  if (!prefs.companion_type) missing.push("旅伴類型");
  if (!prefs.duration)       missing.push("時長");
  if (!prefs.time_of_day)    missing.push("時段");
  if (!prefs.budget)         missing.push("預算");
  if (!prefs.indoor_pref)    missing.push("室內外");
  if (!prefs.activity_pref)  missing.push("動靜偏好");

  if (missing.length > 0) {
    el.innerHTML = "⚠️ 還有項目未填寫：" + missing.join("、");
    el.style.color = "#D94F83";
  } else {
    el.innerHTML =
      "👥 " + prefs.companion_type + "（" + prefs.people_count + " 人）&nbsp;&nbsp;" +
      "⏱ " + prefs.duration + "&nbsp;&nbsp;" +
      "🕐 " + prefs.time_of_day + "<br>" +
      "💰 " + prefs.budget + "&nbsp;&nbsp;" +
      "🏠 " + prefs.indoor_pref + "&nbsp;&nbsp;" +
      "⚡ " + prefs.activity_pref;
    el.style.color = "";
  }
}

// ── 送出推薦 ─────────────────────────────────────────────────
function setupSubmitBtn() {
  const btn = document.getElementById("submitBtn");
  if (!btn) return;
  btn.addEventListener("click", async () => {
    if (!prefs.companion_type || !prefs.duration || !prefs.time_of_day ||
        !prefs.budget || !prefs.indoor_pref || !prefs.activity_pref) {
      alert("還有選項未完成，請往回補填！");
      return;
    }
    showLoading("幫你找最棒的約會行程中…");
    try {
      const res = await fetch("/api/recommend", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(prefs),
      });
      const data = await res.json();
      sessionStorage.setItem("recommendation", JSON.stringify(data));
      sessionStorage.setItem("userPrefs", JSON.stringify(prefs));
      location.href = "/result";
    } catch (err) {
      hideLoading();
      alert("發生錯誤，請重試");
    }
  });
}

// ── 轉盤模式 ─────────────────────────────────────────────────
function setupSpinBtn() {
  const btn = document.getElementById("spinBtn");
  if (!btn) return;
  btn.addEventListener("click", () => {
    sessionStorage.setItem("spinPrefs", JSON.stringify(prefs));
    location.href = "/spin";
  });
}

// ── 載入遮罩 ─────────────────────────────────────────────────
function showLoading(msg) {
  const overlay = document.getElementById("loadingOverlay");
  const text    = document.getElementById("loadingText");
  if (overlay) overlay.style.display = "flex";
  if (text)    text.textContent = msg;
}
function hideLoading() {
  const overlay = document.getElementById("loadingOverlay");
  if (overlay) overlay.style.display = "none";
}
