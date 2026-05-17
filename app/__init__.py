import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from dotenv import load_dotenv

load_dotenv()

db = SQLAlchemy()


def create_app():
    app = Flask(__name__, template_folder="../templates", static_folder="../static")

    app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", "dev-secret")
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///nccu_date.db"
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    db.init_app(app)

    from app.routes.main import main_bp
    from app.routes.api import api_bp
    app.register_blueprint(main_bp)
    app.register_blueprint(api_bp)

    with app.app_context():
        db.create_all()
        _auto_seed()

    return app


def _auto_seed():
    """每次啟動都確認資料庫有資料，沒有就自動匯入。"""
    from app.models.place import Place
    if Place.query.count() == 0:
        print("🌱 資料庫是空的，自動匯入地點資料...")
        try:
            import sys, os
            sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
            from seed import PLACES, PLACES_EXTRA
            import json
            all_places = PLACES + PLACES_EXTRA
            for data in all_places:
                place = Place(**data)
                db.session.add(place)
            db.session.commit()
            print(f"✅ 成功匯入 {len(all_places)} 筆地點資料！")
        except Exception as e:
            print(f"❌ 匯入失敗：{e}")
            db.session.rollback()
