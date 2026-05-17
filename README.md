# 🌸 政大約會提案

> 以政大學生生活圈為核心的互動式約會推薦平台

## 專案簡介

解決政大學生在安排約會時常遇到的「選擇困難」問題。  
只要回答 7 個問題，系統就能根據旅伴類型、時長、預算、時段等條件，快速推薦 1–3 組量身打造的約會行程。

涵蓋範圍：**政大周邊（貓空、木柵）、信義商圈、北車中山一帶**

---

## 功能特色

- 📋 **互動式問卷** — 7 步驟逐一引導，自動偵測當前時段
- 🗺 **智慧推薦** — 依旅伴、預算、室內外、動靜態、人數交叉篩選
- 🚇 **Google Maps 串接** — 顯示從政大出發的交通時間
- 🎡 **命運轉盤** — 選擇困難特別版，隨機幫你決定
- 📱 **RWD 設計** — 手機、電腦都好用

---

## 技術架構

```
前端：HTML / CSS / JavaScript（由 Flask 直接 serve）
後端：Python 3.12 + Flask 3
資料庫：SQLite + SQLAlchemy
外部 API：Google Maps Distance Matrix API
部署：Railway / Render（推薦）
```

---

## 快速開始（本地開發）

### 1. 複製專案

```bash
git clone <your-repo-url>
cd nccu-date
```

### 2. 建立虛擬環境並安裝套件

```bash
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 3. 設定環境變數

```bash
cp .env.example .env
# 用文字編輯器打開 .env，填入你的 Google Maps API Key
```

### 4. 匯入初始地點資料

```bash
python seed.py
```

### 5. 啟動伺服器

```bash
python run.py
```

開啟瀏覽器前往 → **http://localhost:5000**

---

## 地點資料維護

所有地點資料在 `seed.py` 的 `PLACES` 列表中手動維護。

每筆地點的主要欄位：

| 欄位 | 說明 | 範例 |
|------|------|------|
| `name` | 地點名稱 | `"象山步道"` |
| `area` | 區域 | `"信義"` / `"政大周邊"` / `"中山"` |
| `indoor` | 室內/室外 | `True` / `False` |
| `activity_type` | 動靜態 | `"靜態"` / `"動態"` / `"兩者"` |
| `budget_min/max` | 每人消費範圍（元） | `0` / `300` |
| `suitable_time` | 適合時段（JSON） | `'["早上","下午"]'` |
| `companion_types` | 適合旅伴（JSON） | `'["情侶","朋友"]'` |
| `suitable_duration` | 適合時長（JSON） | `'["半天","一整天"]'` |
| `reason` | 推薦理由 | `"夜景絕美，情侶首選"` |
| `lat` / `lng` | 地理座標 | `25.0268` / `121.5766` |

修改後重新執行 `python seed.py` 即可更新資料庫。

---

## 部署到 Railway（免費方案）

1. 前往 [railway.app](https://railway.app) 建立帳號
2. New Project → Deploy from GitHub repo
3. 在 Variables 頁面加入：
   - `GOOGLE_MAPS_API_KEY` = 你的 API Key
   - `SECRET_KEY` = 任意一串隨機字串
4. 部署完成後，在 Settings 取得公開網址

---

## 執行測試

```bash
pytest tests/ -v
```

---

## 專案結構

```
nccu-date/
├── run.py                  # 啟動入口
├── seed.py                 # 資料匯入腳本
├── requirements.txt
├── .env.example
├── app/
│   ├── __init__.py         # Flask app 工廠
│   ├── models/
│   │   ├── place.py        # 地點資料模型
│   │   └── session.py      # 使用者 session 記錄
│   ├── routes/
│   │   ├── main.py         # 頁面路由
│   │   └── api.py          # API 路由
│   ├── services/
│   │   └── recommender.py  # 推薦引擎核心邏輯
│   └── utils/
│       └── maps.py         # Google Maps 工具
├── templates/
│   ├── index.html          # 問卷入口頁
│   ├── result.html         # 推薦結果頁
│   └── spin.html           # 命運轉盤頁
├── static/
│   ├── css/main.css
│   └── js/
│       ├── quiz.js
│       ├── result.js
│       └── spin.js
└── tests/
    └── test_recommender.py
```

---

## 開發團隊

政治大學 × 約會提案小組
