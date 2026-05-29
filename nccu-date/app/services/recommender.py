import random
from app.models.place import Place

BUDGET_MAP = {
    "免費":      (0, 0),
    "300以下":   (0, 300),
    "300-500":  (300, 500),
    "500-1000": (500, 1000),
    "1000以上": (1000, 99999),
}

DURATION_SLOTS = {
    "3小時以內": 1,
    "半天":      2,
    "一整天":    3,
}


def filter_places(user_prefs: dict) -> list[Place]:
    """
    依照使用者條件篩選地點。
    user_prefs 格式：
    {
        "companion_type": "情侶",
        "people_count": 2,
        "duration": "半天",
        "time_of_day": "下午",
        "budget": "300-500",
        "indoor_pref": "室內",   # 室內 / 室外 / 都可以
    }
    """
    query = Place.query

    # 1. 預算篩選
    budget_str = user_prefs.get("budget", "300以下")
    bmin, bmax = BUDGET_MAP.get(budget_str, (0, 9999))
    query = query.filter(Place.budget_min <= bmax)
    if bmin > 0:
        query = query.filter(Place.budget_max >= bmin)

    # 2. 室內外篩選（在 DB 層過濾，皆可永遠不排除）
    indoor_pref = user_prefs.get("indoor_pref", "都可以")
    if indoor_pref == "室內":
        query = query.filter(Place.indoor.in_(["室內", "皆可"]))
    elif indoor_pref == "室外":
        query = query.filter(Place.indoor.in_(["室外", "皆可"]))
    # 都可以 → 不加條件，全部顯示

    places = query.all()

    # 3. 其餘條件用 Python 過濾
    result = []
    for p in places:
        # 時段
        if user_prefs.get("time_of_day") not in p.suitable_time_list():
            continue

        # 旅伴類型
        companion = user_prefs.get("companion_type", "情侶")
        if companion not in p.companion_types_list():
            continue

        # 時長
        duration = user_prefs.get("duration", "半天")
        if duration not in p.suitable_duration_list():
            continue

        # 人數
        people = int(user_prefs.get("people_count", 2))
        if people < p.min_people or people > p.max_people:
            continue

        result.append(p)

    return result


def score_place(place: Place, user_prefs: dict) -> float:
    score = place.score

    companion = user_prefs.get("companion_type", "")
    if companion in place.companion_types_list():
        score += 0.5

    return score


def build_itineraries(places: list[Place], user_prefs: dict) -> list[dict]:
    if not places:
        return []

    duration = user_prefs.get("duration", "半天")
    slot_count = DURATION_SLOTS.get(duration, 2)

    sorted_places = sorted(places, key=lambda p: score_place(p, user_prefs), reverse=True)

    if len(sorted_places) < slot_count:
        return [build_single_itinerary(sorted_places, user_prefs, index=1)]

    max_possible = len(sorted_places) // slot_count
    max_itineraries = min(3, max_possible)

    itineraries = []
    used_ids = set()

    for i in range(max_itineraries):
        available = [p for p in sorted_places if p.id not in used_ids]
        if len(available) < slot_count:
            break

        if i == 0:
            chosen = available[:slot_count]
        else:
            top = available[:max(slot_count * 2, 4)]
            chosen = random.sample(top, min(slot_count, len(top)))

        itinerary = build_single_itinerary(chosen, user_prefs, index=i + 1)
        itineraries.append(itinerary)

        for p in chosen:
            used_ids.add(p.id)

    return itineraries


def build_single_itinerary(places: list[Place], user_prefs: dict, index: int) -> dict:
    total_min = sum(p.budget_min for p in places)
    total_max = sum(p.budget_max for p in places)

    reasons = [p.reason for p in places if p.reason]

    tags = []
    for p in places:
        tags.extend(p.tags_list())
    tags = list(set(tags))[:5]

    return {
        "index": index,
        "places": [p.to_dict() for p in places],
        "budget_range": f"約 {total_min}–{total_max} 元／人" if total_max > 0 else "免費",
        "reasons": reasons,
        "tags": tags,
        "area_summary": "、".join(set(p.area for p in places)),
    }


def get_recommendation(user_prefs: dict) -> list[dict]:
    places = filter_places(user_prefs)
    return build_itineraries(places, user_prefs)


def get_spin_result(user_prefs: dict) -> dict | None:
    places = filter_places(user_prefs)
    if not places:
        return None

    duration = user_prefs.get("duration", "半天")
    slot_count = DURATION_SLOTS.get(duration, 2)
    chosen = random.sample(places, min(slot_count, len(places)))
    return build_single_itinerary(chosen, user_prefs, index=1)
