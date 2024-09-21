# bot.py
  # Make sure this path points to where your Flask app is initialized
import discord
from discord.ext import commands
import requests

intents = discord.Intents.default()
intents.message_content = True  # Required to read message content

bot = commands.Bot(command_prefix='!', intents=intents)

# Replace with your Flask app's URL
#FLASK_APP_URL = 'http://localhost:5000'
FLASK_APP_URL = 'https://acf4-223-255-254-102.ngrok-free.app'

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user}')

# bot.py
@bot.command(name='admin_connect')
async def admin_connect(ctx, *, params):
    # Check if the user is an admin
    if not ctx.author.guild_permissions.administrator:
        await ctx.send("You do not have permission to use this command.")
        return

    # Parse parameters
    try:
        chain_id_str, network_name, rpc_url, symbol, block_explorer_url, token_contract_address = [
            param.strip() for param in params.split(',')]
        chain_id = chain_id_str  # Chain ID stays in string form (e.g., '0x64')
    except ValueError:
        await ctx.send("Invalid parameters. Please provide: chainId, networkName, rpcUrl, symbol, blockExplorerUrl, tokenContractAddress")
        return

    # Generate the link to the Flask app for adding the network and saving it
    discord_user_id = str(ctx.author.id)
    link = f"{FLASK_APP_URL}/add_and_save_network?discord_user_id={discord_user_id}&chainId={chain_id}&networkName={network_name}&rpcUrl={rpc_url}&symbol={symbol}&blockExplorerUrl={block_explorer_url}&tokenContractAddress={token_contract_address}"

    await ctx.author.send(f"Click this link to add the network to MetaMask and then save it: {link}")
    await ctx.send("I've sent you a direct message with the link to add and save the network.")


@bot.command(name='register_user_wallet')
async def register_user_wallet(ctx):
    discord_user_id = str(ctx.author.id)
    link = f"{FLASK_APP_URL}/switch_network?discord_user_id={discord_user_id}"
    await ctx.author.send(f"Please connect your wallet and switch to the admin's network using this link: {link}")
    await ctx.send("I've sent you a direct message with instructions to switch networks and register your wallet.")

# Import your Flask app instance


@bot.command(name='send_test_tokens')
async def send_test_tokens(ctx, user: str, amount: float):
    print("User received is: ", user)

    # Check if the user is an admin
    if not ctx.author.guild_permissions.administrator:
        await ctx.send("You do not have permission to use this command.")
        return

    # Attempt to resolve user mention (discord.Member)
    try:
        user_obj = await commands.MemberConverter().convert(ctx, user)
    except discord.ext.commands.errors.MemberNotFound:
        await ctx.send(f"User '{user}' not found. Please ensure the user is in this server.")
        return

    # Make a request to the Flask API to get the user's wallet address
    discord_user_id = str(user_obj.id)
    response = requests.get(
        f'{FLASK_APP_URL}/api/get_wallet/{discord_user_id}')

    if response.status_code == 200:
        data = response.json()
        if data['status'] == 'success':
            wallet_address = data['wallet_address']
            # Send the link to the Flask app for the actual token transfer
            admin_discord_id = str(ctx.author.id)
            link = f"{FLASK_APP_URL}/send_tokens_testnet?recipient_id={discord_user_id}&amount={amount}&admin_id={admin_discord_id}"
            await ctx.author.send(f"Click this link to send {amount} test tokens to {user_obj.name}: {link}")
            await ctx.send(f"I've sent you a DM with the link to send {amount} test tokens.")
        else:
            await ctx.send(f"Error: {data['message']}")
    else:
        await ctx.send(f"Error: Could not reach Flask API (status code: {response.status_code})")


bot.run('MTI4NjQxNTk2MTAwMzY1NTI2Mg.G81Yyb.2i7rSnwXrOcKKtY0QSZVNPcTk103XIqhRXknsk')