import os
import requests

# 政大正門座標
NCCU_LAT = 24.9871
NCCU_LNG = 121.5770

NCCU_ORIGIN = f"{NCCU_LAT},{NCCU_LNG}"


def get_travel_time(dest_lat: float, dest_lng: float, mode: str = "transit") -> dict:
    """
    查詢從政大到目的地的交通時間。
    mode: transit（大眾運輸）| driving | walking
    回傳 {"duration": "約 25 分鐘", "distance": "8.2 公里"}
    """
    api_key = os.getenv("GOOGLE_MAPS_API_KEY", "")
    if not api_key or api_key == "your-google-maps-api-key-here":
        return {"duration": "查詢中", "distance": "—"}

    url = "https://maps.googleapis.com/maps/api/distancematrix/json"
    params = {
        "origins": NCCU_ORIGIN,
        "destinations": f"{dest_lat},{dest_lng}",
        "mode": mode,
        "language": "zh-TW",
        "key": api_key,
    }

    try:
        resp = requests.get(url, params=params, timeout=5)
        data = resp.json()
        element = data["rows"][0]["elements"][0]

        if element["status"] == "OK":
            return {
                "duration": element["duration"]["text"],
                "distance": element["distance"]["text"],
            }
    except Exception:
        pass

    return {"duration": "查詢失敗", "distance": "—"}


def get_travel_times_batch(places: list[dict]) -> list[dict]:
    """
    批次查詢多個地點的交通時間（節省 API 次數）。
    places: [{"id": 1, "lat": 24.99, "lng": 121.58, ...}, ...]
    回傳每個 place 加上 travel_info 欄位。
    """
    api_key = os.getenv("GOOGLE_MAPS_API_KEY", "")
    if not api_key or api_key == "your-google-maps-api-key-here":
        for p in places:
            p["travel_info"] = {"duration": "查詢中", "distance": "—"}
        return places

    destinations = "|".join(
        f"{p['lat']},{p['lng']}" for p in places if p.get("lat") and p.get("lng")
    )

    if not destinations:
        for p in places:
            p["travel_info"] = {"duration": "—", "distance": "—"}
        return places

    url = "https://maps.googleapis.com/maps/api/distancematrix/json"
    params = {
        "origins": NCCU_ORIGIN,
        "destinations": destinations,
        "mode": "transit",
        "language": "zh-TW",
        "key": api_key,
    }

    try:
        resp = requests.get(url, params=params, timeout=8)
        data = resp.json()
        elements = data["rows"][0]["elements"]

        idx = 0
        for p in places:
            if p.get("lat") and p.get("lng"):
                el = elements[idx] if idx < len(elements) else {}
                if el.get("status") == "OK":
                    p["travel_info"] = {
                        "duration": el["duration"]["text"],
                        "distance": el["distance"]["text"],
                    }
                else:
                    p["travel_info"] = {"duration": "—", "distance": "—"}
                idx += 1
            else:
                p["travel_info"] = {"duration": "—", "distance": "—"}
    except Exception:
        for p in places:
            p["travel_info"] = {"duration": "—", "distance": "—"}

    return places
