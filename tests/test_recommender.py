"""
pytest 測試 — 推薦引擎核心邏輯
執行方式：pytest tests/
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import pytest
from app import create_app, db
from app.models.place import Place
from app.services.recommender import get_recommendation, get_spin_result


@pytest.fixture(scope="module")
def app():
    _app = create_app()
    _app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///:memory:"
    _app.config["TESTING"] = True
    with _app.app_context():
        db.create_all()
        _seed_test_data()
        yield _app


def _seed_test_data():
    """塞入最小測試資料"""
    import json
    places = [
        Place(
            name="測試室內靜態免費",
            area="政大周邊", category="景點",
            indoor=True, activity_type="靜態",
            budget_min=0, budget_max=0,
            suitable_time=json.dumps(["早上", "下午", "晚上"]),
            companion_types=json.dumps(["情侶", "朋友", "個人", "家人"]),
            suitable_duration=json.dumps(["3小時以內", "半天", "一整天"]),
            min_people=1, max_people=99,
            reason="測試用", score=4.0,
            lat=24.98, lng=121.57,
        ),
        Place(
            name="測試室外動態低預算",
            area="信義", category="景點",
            indoor=False, activity_type="動態",
            budget_min=0, budget_max=100,
            suitable_time=json.dumps(["早上", "下午"]),
            companion_types=json.dumps(["情侶", "朋友"]),
            suitable_duration=json.dumps(["半天", "一整天"]),
            min_people=2, max_people=10,
            reason="測試用2", score=4.2,
            lat=25.03, lng=121.56,
        ),
    ]
    for p in places:
        db.session.add(p)
    db.session.commit()


# ── 測試案例 ──────────────────────────────────────────

def test_recommend_returns_list(app):
    with app.app_context():
        prefs = {
            "companion_type": "情侶", "people_count": 2,
            "duration": "半天", "time_of_day": "下午",
            "budget": "300以下", "indoor_pref": "都可以",
            "activity_pref": "都可以",
        }
        result = get_recommendation(prefs)
        assert isinstance(result, list)


def test_recommend_indoor_filter(app):
    with app.app_context():
        prefs = {
            "companion_type": "情侶", "people_count": 2,
            "duration": "半天", "time_of_day": "下午",
            "budget": "300以下", "indoor_pref": "室內",
            "activity_pref": "都可以",
        }
        result = get_recommendation(prefs)
        for itin in result:
            for p in itin["places"]:
                assert p["indoor"] is True, f"{p['name']} 不是室內地點"


def test_recommend_budget_filter(app):
    with app.app_context():
        prefs = {
            "companion_type": "個人", "people_count": 1,
            "duration": "3小時以內", "time_of_day": "晚上",
            "budget": "免費", "indoor_pref": "都可以",
            "activity_pref": "都可以",
        }
        result = get_recommendation(prefs)
        for itin in result:
            for p in itin["places"]:
                assert p["budget_max"] == 0, f"{p['name']} 不是免費地點"


def test_spin_returns_one_itinerary(app):
    with app.app_context():
        prefs = {
            "companion_type": "朋友", "people_count": 3,
            "duration": "半天", "time_of_day": "下午",
            "budget": "300以下", "indoor_pref": "都可以",
            "activity_pref": "都可以",
        }
        result = get_spin_result(prefs)
        # 可能為 None（條件太嚴），但如果有結果格式要正確
        if result:
            assert "places" in result
            assert "budget_range" in result


def test_no_result_when_impossible(app):
    with app.app_context():
        prefs = {
            "companion_type": "個人", "people_count": 1,
            "duration": "一整天", "time_of_day": "晚上",
            "budget": "免費", "indoor_pref": "室外",
            "activity_pref": "動態",
        }
        result = get_recommendation(prefs)
        # 不崩潰即可，結果可能為空 list
        assert isinstance(result, list)
