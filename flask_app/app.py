# flask_app/app.py
from flask import Flask, render_template, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from models import db, UserWallet
from web3 import Web3
import os

app = Flask(__name__)
# Replace with a secure secret key
app.config['SECRET_KEY'] = 'your_generated_secret_key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'

db.init_app(app)

# Initialize Web3
# Replace with your Infura Project ID
INFURA_PROJECT_ID = 'YOUR_INFURA_PROJECT_ID'
w3 = Web3(Web3.HTTPProvider(
    f'https://mainnet.infura.io/v3/9595c12e1d784a39879aa3faa5dabd0e'))


@app.route('/')
def index():
    discord_user_id = request.args.get('discord_user_id')
    if not discord_user_id:
        return "Discord user ID is required.", 400
    return render_template('index.html', discord_user_id=discord_user_id)


@app.route('/register_wallet', methods=['POST'])
def register_wallet():
    try:
        data = request.get_json()
        discord_user_id = data.get('discord_user_id')
        wallet_address = data.get('wallet_address')

        print(f"Received discord_user_id: {discord_user_id}")
        print(f"Received wallet_address: {wallet_address}")

        # Validate the wallet address
        if not Web3.is_address(wallet_address):
            return jsonify({'status': 'error', 'message': 'Invalid wallet address.'}), 400

        # Normalize the address
        wallet_address = Web3.to_checksum_address(wallet_address)

        # Check if the user already exists
        existing_user = UserWallet.query.filter_by(
            discord_user_id=discord_user_id).first()
        if existing_user:
            existing_user.wallet_address = wallet_address
        else:
            new_user = UserWallet(
                discord_user_id=discord_user_id, wallet_address=wallet_address)
            db.session.add(new_user)

        db.session.commit()
        return jsonify({'status': 'success'})
    except Exception as e:
        # Log the exception (you can use logging module)
        print(f"An error occurred: {e}")
        return jsonify({'status': 'error', 'message': 'An internal error occurred.'}), 500


@app.route('/add_network')
def add_network():
    # Extract network parameters from query parameters
    chain_id = request.args.get('chainId')
    network_name = request.args.get('networkName')
    rpc_url = request.args.get('rpcUrl')
    symbol = request.args.get('symbol')
    block_explorer_url = request.args.get('blockExplorerUrl')
    print(chain_id, network_name, rpc_url, symbol, block_explorer_url)
    if not all([chain_id, network_name, rpc_url, symbol, block_explorer_url]):
        return "Missing network parameters.", 400

    return render_template('add_network.html', chain_id=chain_id, network_name=network_name,
                           rpc_url=rpc_url, symbol=symbol, block_explorer_url=block_explorer_url)


@app.route('/switch_network')
def switch_network():
    discord_user_id = request.args.get('discord_user_id')
    if not discord_user_id:
        return "Discord user ID is required.", 400

    chain_id = request.args.get('chainId')
    network_name = request.args.get('networkName')
    rpc_url = request.args.get('rpcUrl')
    symbol = request.args.get('symbol')
    block_explorer_url = request.args.get('blockExplorerUrl')
    print(chain_id, network_name, rpc_url, symbol, block_explorer_url)

    if not all([chain_id, network_name, rpc_url, symbol, block_explorer_url]):
        return "Missing network parameters.", 400
    # For this example, we'll hardcode the admin's network parameters.
    # In a real application, you would retrieve these from a database or configuration.
    admin_network = {
        'chain_id': chain_id,   
        'network_name': network_name,
        'rpc_url': rpc_url,
        'symbol': symbol,
        'block_explorer_url': block_explorer_url
    }

    return render_template('switch_network.html', discord_user_id=discord_user_id, **admin_network)


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
