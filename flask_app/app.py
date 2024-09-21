# flask_app/app.py

import requests
from models import db, PostUpvote, UserWallet
from flask import jsonify
from datetime import datetime
from models import PostUpvote, db, UserWallet, AdminNetwork
from flask import Flask, render_template, request, jsonify
from web3 import Web3

# Replace with your Flask app's URL
FLASK_APP_URL = 'https://acf4-223-255-254-102.ngrok-free.app'
app = Flask(__name__)
# Replace with a secure secret key
app.config['SECRET_KEY'] = 'your_generated_secret_key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'

db.init_app(app)

# Initialize Web3
# Replace with your Infura Project ID
INFURA_PROJECT_ID = '9595c12e1d784a39879aa3faa5dabd0e'
TOKEN_CONTRACT_ADDRESS = '0x07865c6e87b9f70255377e024ace6630c1eaa37f'
w3 = Web3(Web3.HTTPProvider(
    f'https://mainnet.infura.io/v3/{INFURA_PROJECT_ID}'))

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

    # Retrieve the admin's network configuration from the database
    # Assuming there's only one admin network config
    admin_network = AdminNetwork.query.first()

    if not admin_network:
        return "Admin network configuration not found.", 404

    return render_template('switch_network.html',
                           discord_user_id=discord_user_id,
                           chain_id=admin_network.chain_id,
                           network_name=admin_network.network_name,
                           rpc_url=admin_network.rpc_url,
                           symbol=admin_network.symbol,
                           block_explorer_url=admin_network.block_explorer_url)


@app.route('/save_network')
def save_network():
    discord_user_id = request.args.get('discord_user_id')
    chain_id = request.args.get('chainId')
    network_name = request.args.get('networkName')
    rpc_url = request.args.get('rpcUrl')
    symbol = request.args.get('symbol')
    block_explorer_url = request.args.get('blockExplorerUrl')
    token_contract_address = request.args.get('tokenContractAddress')

    # Validate required parameters
    if not all([discord_user_id, chain_id, network_name, rpc_url, symbol, block_explorer_url, token_contract_address]):
        return "Missing network parameters.", 400

    # Check if network configuration for this admin already exists
    existing_network = AdminNetwork.query.filter_by(
        discord_user_id=discord_user_id).first()
    if existing_network:
        # Update the existing network configuration
        existing_network.chain_id = chain_id
        existing_network.network_name = network_name
        existing_network.rpc_url = rpc_url
        existing_network.symbol = symbol
        existing_network.block_explorer_url = block_explorer_url
        existing_network.token_contract_address = token_contract_address
    else:
        # Create a new network configuration
        new_network = AdminNetwork(
            discord_user_id=discord_user_id,
            chain_id=chain_id,
            network_name=network_name,
            rpc_url=rpc_url,
            symbol=symbol,
            block_explorer_url=block_explorer_url,
            token_contract_address=token_contract_address
        )
        db.session.add(new_network)

    db.session.commit()

    return "Network configuration saved successfully."

@app.route('/send_tokens_testnet')
def send_tokens_testnet():
    recipient_id = request.args.get('recipient_id')
    amount = request.args.get('amount')
    admin_id = request.args.get('admin_id')

    # Fetch the recipient's wallet address from the database
    recipient = UserWallet.query.filter_by(
        discord_user_id=recipient_id).first()
    if not recipient:
        return "Recipient not found.", 404

    wallet_address = recipient.wallet_address

    # Simulate sending testnet tokens (use Goerli Testnet for this example)
    # Use Goerli Testnet RPC URL
    testnet_rpc_url = f'https://sepolia.infura.io/v3/{INFURA_PROJECT_ID}'
    # Replace with your testnet ERC-20 token contract
    token_contract_address = TOKEN_CONTRACT_ADDRESS

    return render_template('send_tokens_testnet.html', wallet_address=wallet_address, amount=amount, token_contract_address=token_contract_address, rpc_url=testnet_rpc_url)

@app.route('/add_and_save_network')
def add_and_save_network():
    discord_user_id = request.args.get('discord_user_id')
    chain_id = request.args.get('chainId')
    network_name = request.args.get('networkName')
    rpc_url = request.args.get('rpcUrl')
    symbol = request.args.get('symbol')
    block_explorer_url = request.args.get('blockExplorerUrl')
    token_contract_address = request.args.get('tokenContractAddress')

    if not all([discord_user_id, chain_id, network_name, rpc_url, symbol, block_explorer_url, token_contract_address]):
        return "Missing network parameters.", 400

    # Render a page where the admin will add the network first and then confirm to save it
    return render_template('add_and_save_network.html',
                           discord_user_id=discord_user_id,
                           chain_id=chain_id,
                           network_name=network_name,
                           rpc_url=rpc_url,
                           symbol=symbol,
                           block_explorer_url=block_explorer_url,
                           token_contract_address=token_contract_address)

# API endpoint to fetch a user's wallet by their Discord ID


@app.route('/api/get_wallet/<discord_user_id>', methods=['GET'])
def get_wallet(discord_user_id):
    try:
        user_wallet = UserWallet.query.filter_by(
            discord_user_id=discord_user_id).first()
        if user_wallet:
            return jsonify({
                'status': 'success',
                'wallet_address': user_wallet.wallet_address
            })
        else:
            return jsonify({
                'status': 'error',
                'message': 'Wallet not found'
            }), 404
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500


@app.route('/api/capture_upvote', methods=['POST'])
def capture_upvote():
    try:
        data = request.get_json()
        post_id = data.get('post_id')
        reply_id = data.get('reply_id', None)
        user_id = data.get('user_id')
        upvotes = data.get('upvotes', 0)

        # Find the upvote in DB
        post_upvote = PostUpvote.query.filter_by(
            post_id=post_id, reply_id=reply_id, user_id=user_id).first()

        if post_upvote:
            # Check if upvote count has changed
            if post_upvote.upvotes != upvotes:
                previous_upvotes = post_upvote.upvotes
                post_upvote.upvotes = upvotes
                post_upvote.last_updated = datetime.utcnow()
                # Reset notification flag when upvote changes
                post_upvote.notification_sent = False
                db.session.commit()

                return jsonify({
                    'status': 'success',
                    'change_detected': True,  # Change detected
                    'previous_upvotes': previous_upvotes,
                    'new_upvotes': upvotes
                }), 200
            else:
                return jsonify({
                    'status': 'success',
                    'change_detected': False,  # No change in upvotes
                }), 200
        else:
            # New upvote entry
            post_upvote = PostUpvote(
                post_id=post_id,
                reply_id=reply_id,
                user_id=user_id,
                upvotes=upvotes,
                notification_sent=False  # New entry, so no notification sent
            )
            db.session.add(post_upvote)
            db.session.commit()

            return jsonify({
                'status': 'success',
                'change_detected': True,  # New upvote entry
                'previous_upvotes': 0,
                'new_upvotes': upvotes
            }), 200

    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500



@app.route('/api/generate_token_link', methods=['POST'])
def generate_token_link():
    try:
        data = request.get_json()
        recipient_id = data.get('recipient_id')
        upvotes = data.get('upvotes')

        # Fetch wallet address of the recipient
        recipient = UserWallet.query.filter_by(
            discord_user_id=recipient_id).first()

        if not recipient:
            return jsonify({'status': 'error', 'message': 'Wallet not found'}), 404

        wallet_address = recipient.wallet_address
        # Calculate the token amount based on upvotes        
        token_amount = upvotes * 0.01
        
        # Return the link to send tokens
        link = f"{FLASK_APP_URL}/send_tokens_testnet?recipient_id={recipient_id}&amount={token_amount}&admin_id=admin"

        return jsonify({'status': 'success', 'link': link}), 200

    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500


# app.py

@app.route('/api/update_notification', methods=['POST'])
def update_notification():
    try:
        data = request.get_json()
        post_id = data.get('post_id')
        reply_id = data.get('reply_id', None)
        notification_sent = data.get('notification_sent', False)

        # Find the upvote record in the DB
        post_upvote = PostUpvote.query.filter_by(
            post_id=post_id, reply_id=reply_id).first()

        if post_upvote:
            post_upvote.notification_sent = notification_sent
            db.session.commit()

            return jsonify({'status': 'success', 'message': 'Notification status updated'}), 200
        else:
            return jsonify({'status': 'error', 'message': 'Upvote record not found'}), 404

    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500


@app.route('/api/get_upvotes/<discord_user_id>', methods=['GET'])
def get_upvotes(discord_user_id):
    try:
        # Fetch all posts and replies by the user
        posts = PostUpvote.query.filter_by(user_id=discord_user_id).all()

        total_upvotes = 0

        for post in posts:
            total_upvotes += post.upvotes

        # Generate the token link
        token_link_response = requests.post(f'{FLASK_APP_URL}/api/generate_token_link', json={
            'recipient_id': discord_user_id,
            'upvotes': total_upvotes
        })

        if token_link_response.status_code == 200:
            token_link_data = token_link_response.json()
            token_link = token_link_data.get('link')

            return jsonify({
                'status': 'success',
                'total_upvotes': total_upvotes,
                'token_link': token_link
            })
        else:
            return jsonify({'status': 'error', 'message': 'Failed to generate token link.'}), 500

    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
