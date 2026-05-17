import json
from datetime import datetime
from flask import Blueprint, request, jsonify
from app import db
from app.models.session import UserSession
from app.services.recommender import get_recommendation, get_spin_result
from app.utils.maps import get_travel_times_batch

api_bp = Blueprint("api", __name__, url_prefix="/api")


def _current_time_of_day() -> str:
    hour = datetime.now().hour
    if 5 <= hour < 12:
        return "早上"
    elif 12 <= hour < 18:
        return "下午"
    else:
        return "晚上"


@api_bp.route("/time", methods=["GET"])
def get_current_time():
    """前端用來自動偵測當前時段。"""
    return jsonify({"time_of_day": _current_time_of_day()})


@api_bp.route("/recommend", methods=["POST"])
def recommend():
    """
    接收使用者問卷，回傳推薦行程。
    Request JSON:
    {
        "companion_type": "情侶",
        "people_count": 2,
        "duration": "半天",
        "time_of_day": "下午",
        "budget": "300~500",
        "indoor_pref": "都可以",
        "activity_pref": "靜態"
    }
    """
    data = request.get_json()
    if not data:
        return jsonify({"error": "請提供問卷資料"}), 400

    # 若前端沒傳時段，自動偵測
    if not data.get("time_of_day"):
        data["time_of_day"] = _current_time_of_day()

    itineraries = get_recommendation(data)

    # 每個地點加入推薦店家資料
    from app.data.shops import get_shops_for_place
    for itin in itineraries:
        for place in itin["places"]:
            place["nearby_shops"] = get_shops_for_place(
                category=place.get("category", ""),
                area=place.get("area", ""),
                count=3
            )

    # 批次查詢交通時間
    for itin in itineraries:
        itin["places"] = get_travel_times_batch(itin["places"])

    # 儲存這次 session（匿名統計）
    place_ids = []
    for itin in itineraries:
        place_ids.extend([p["id"] for p in itin["places"]])

    session = UserSession(
        companion_type=data.get("companion_type"),
        people_count=data.get("people_count", 2),
        duration=data.get("duration"),
        time_of_day=data.get("time_of_day"),
        budget=data.get("budget"),
        indoor_pref=data.get("indoor_pref"),
        activity_pref=data.get("activity_pref"),
        result_place_ids=json.dumps(list(set(place_ids))),
    )
    db.session.add(session)
    db.session.commit()

    if not itineraries:
        return jsonify({
            "itineraries": [],
            "message": "找不到符合條件的行程，試試調整預算或時段？"
        })

    return jsonify({
        "itineraries": itineraries,
        "message": f"為你找到 {len(itineraries)} 組行程！"
    })


@api_bp.route("/spin", methods=["POST"])
def spin():
    """轉盤模式：隨機回傳一組行程。"""
    data = request.get_json() or {}
    if not data.get("time_of_day"):
        data["time_of_day"] = _current_time_of_day()

    result = get_spin_result(data)

    if not result:
        return jsonify({"error": "找不到行程，試試放寬條件"}), 404

    result["places"] = get_travel_times_batch(result["places"])
    return jsonify(result)


@api_bp.route("/places", methods=["GET"])
def list_places():
    """列出所有地點（給管理者確認用）。"""
    from app.models.place import Place
    places = Place.query.all()
    return jsonify([p.to_dict() for p in places])
