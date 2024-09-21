# flask_app/models.py
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class UserWallet(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    discord_user_id = db.Column(db.String(50), unique=True, nullable=False)
    wallet_address = db.Column(db.String(100), unique=True, nullable=False)

    def __repr__(self):
        return f'<UserWallet {self.discord_user_id} - {self.wallet_address}>'


class AdminNetwork(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    discord_user_id = db.Column(
        db.String(50), unique=True, nullable=False)  # Admin's Discord ID
    chain_id = db.Column(db.String(20), nullable=False)  # Example: '0x64'
    network_name = db.Column(db.String(100), nullable=False)
    rpc_url = db.Column(db.String(255), nullable=False)
    symbol = db.Column(db.String(20), nullable=False)
    block_explorer_url = db.Column(db.String(255), nullable=False)
    token_contract_address = db.Column(
        db.String(100), nullable=False)  # ERC-20 Token Contract Address

    def __repr__(self):
        return f'<AdminNetwork {self.discord_user_id} - {self.chain_id}>'



class PostUpvote(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    post_id = db.Column(db.String(100), nullable=False)  # Post/Message ID
    reply_id = db.Column(db.String(100), nullable=True)  # Reply ID (Optional)
    # ID of user who made the post or reply
    user_id = db.Column(db.String(50), nullable=False)
    upvotes = db.Column(db.Integer, default=0)
    notification_sent = db.Column(db.Boolean, default=False)
    last_updated = db.Column(db.DateTime, default=datetime.utcnow)
    # Track if notification is sent
    

    def __repr__(self):
        return f'<PostUpvote Post {self.post_id} - User {self.user_id} - Upvotes {self.upvotes}>'
