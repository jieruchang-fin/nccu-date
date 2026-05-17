import json
from datetime import datetime
from app import db


class UserSession(db.Model):
    __tablename__ = "user_sessions"

    id = db.Column(db.Integer, primary_key=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # 使用者填寫的條件
    companion_type = db.Column(db.String(20))   # 個人 / 情侶 / 家人 / 朋友
    people_count = db.Column(db.Integer, default=2)
    duration = db.Column(db.String(20))          # 3小時以內 / 半天 / 一整天
    time_of_day = db.Column(db.String(10))       # 早上 / 下午 / 晚上
    budget = db.Column(db.String(20))            # 免費 / 300以下 / 300~500 / 500~1000 / 1000以上
    indoor_pref = db.Column(db.String(10))       # 室內 / 室外 / 都可以
    activity_pref = db.Column(db.String(10))     # 靜態 / 動態 / 都可以
    spin_mode = db.Column(db.Boolean, default=False)

    # 推薦結果（存 place id 列表的 JSON）
    result_place_ids = db.Column(db.Text, default="[]")

    def result_ids_list(self):
        return json.loads(self.result_place_ids)

    def __repr__(self):
        return f"<UserSession {self.id} {self.companion_type}>"
