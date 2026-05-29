import json
from app import db


class Place(db.Model):
    __tablename__ = "places"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    area = db.Column(db.String(20), nullable=False)      # 政大附近 / 信義 / 中山
    category = db.Column(db.String(30), nullable=False)  # 餐廳 / 咖啡廳 / 展覽 ...

    description = db.Column(db.Text)

    # 條件篩選欄位
    indoor = db.Column(db.String(10), nullable=False)    # "室內" / "室外" / "皆可"
    budget_min = db.Column(db.Integer, default=0)
    budget_max = db.Column(db.Integer, default=0)

    # 適合時段（JSON 字串，例如 '["早上","下午"]'）
    suitable_time = db.Column(db.Text, default='["早上","下午","晚上"]')

    # 適合旅伴（JSON 字串）
    companion_types = db.Column(db.Text, default='["情侶","朋友","家人","個人"]')

    # 人數限制
    min_people = db.Column(db.Integer, default=1)
    max_people = db.Column(db.Integer, default=99)

    # 時長適合性（JSON 字串）
    suitable_duration = db.Column(db.Text, default='["3小時以內","半天","一整天"]')

    # 推薦理由
    reason = db.Column(db.Text, default="")

    # 標籤（JSON 字串）
    tags = db.Column(db.Text, default="[]")

    # 地圖資訊
    lat = db.Column(db.Float)
    lng = db.Column(db.Float)
    google_place_id = db.Column(db.String(200))
    address = db.Column(db.String(200))
    google_maps_url = db.Column(db.String(500), default="")

    # 圖片
    image_url = db.Column(db.String(500), default="")

    # 評分（1–5）
    score = db.Column(db.Float, default=3.0)

    def suitable_time_list(self):
        return json.loads(self.suitable_time)

    def companion_types_list(self):
        return json.loads(self.companion_types)

    def suitable_duration_list(self):
        return json.loads(self.suitable_duration)

    def tags_list(self):
        return json.loads(self.tags)

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "area": self.area,
            "category": self.category,
            "description": self.description,
            "indoor": self.indoor,
            "budget_min": self.budget_min,
            "budget_max": self.budget_max,
            "suitable_time": self.suitable_time_list(),
            "companion_types": self.companion_types_list(),
            "suitable_duration": self.suitable_duration_list(),
            "reason": self.reason,
            "tags": self.tags_list(),
            "lat": self.lat,
            "lng": self.lng,
            "address": self.address,
            "google_maps_url": self.google_maps_url,
            "image_url": self.image_url,
            "score": self.score,
        }

    def __repr__(self):
        return f"<Place {self.name}>"
