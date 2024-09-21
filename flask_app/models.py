# flask_app/models.py
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
