# flask_app/models.py
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class UserWallet(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    discord_user_id = db.Column(db.String(50), unique=True, nullable=False)
    wallet_address = db.Column(db.String(100), unique=True, nullable=False)

    def __repr__(self):
        return f'<UserWallet {self.discord_user_id} - {self.wallet_address}>'
