# bot.py
import asyncio
import discord
from discord.ext import commands

import requests
from gradient_client.tools import create_knowledge_base
from openai_chat.chat import get_answers_from_knowledge_base
intents = discord.Intents.default()
intents.message_content = True  # Required to read message content

bot = commands.Bot(command_prefix='!', intents=intents)


# Replace with your Flask app's URL
#FLASK_APP_URL = 'http://localhost:5000'
FLASK_APP_URL = 'https://acf4-223-255-254-102.ngrok-free.app'

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user}')

@bot.command(name='register_wallet')
async def register_wallet(ctx):
    discord_user_id = str(ctx.author.id)
    link = f"{FLASK_APP_URL}/?discord_user_id={discord_user_id}"
    await ctx.author.send(f"Please connect your wallet using this link: {link}")
    await ctx.send("I've sent you a direct message with instructions to connect your wallet.")

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

    # Build the query parameters
    query_params = f"?chainId={chain_id_str}&networkName={network_name}&rpcUrl={rpc_url}&symbol={symbol}&blockExplorerUrl={block_explorer_url}"

    # Send link to the admin
    link = f"{FLASK_APP_URL}/add_network{query_params}"
    await ctx.author.send(f"Click this link to add the network to MetaMask: {link}")
    await ctx.send("I've sent you a direct message with instructions to add the network.")

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

@bot.command(name='create_knowledge_base')
async def upload_text(ctx):
    await ctx.send("Please upload your `.txt` file or type your text within the next 60 seconds.")

    def check(m):
        return m.author == ctx.author and (m.content or m.attachments)

    try:
        message = await bot.wait_for('message', timeout=60.0, check=check)
    except asyncio.TimeoutError:
        await ctx.send('⏰ You took too long to respond. Please try again.')
        return

    if message.attachments:
        attachment = message.attachments[0]
        if attachment.filename.endswith('.txt'):
            file_content = await attachment.read()
            text = file_content.decode('utf-8')

            print(f"Received text from file: {text}")
            await create_knowledge_base(text)
            await ctx.send(f"📄 **Knowledge Base Created!**")
        else:
            await ctx.send('❌ Please upload a file with a `.txt` extension.')
    elif message.content:
        text = message.content
        create_knowledge_base(text)
        await ctx.send(f"📝 **Received text:**\n{text}")
    else:
        await ctx.send('⚠️ No text or file received. Please try again.')

@bot.command(name='ask')
async def ask_question(ctx, *, question):

    await ctx.send("🔍 Processing your question...")

    try:
        answer = get_answers_from_knowledge_base(question)
        print(answer)
        await ctx.send(f"💡 **Answer:**\n{answer}")
    except Exception as e:
        print(f"Error: {e}")
        await ctx.send("❌ Sorry, I couldn't process your question.")

@bot.command(name='predict_reply')
async def predict_reply(ctx):
    # Fetch last 10 messages from the current channel
    messages = [message async for message in ctx.channel.history(limit=10)]

    # Reverse the order to make it chronological
    messages.reverse()

    # Format messages
    formatted_messages = "\n".join([f"{message.author.name}: {message.content}" for message in messages])

    await ctx.author.send("🔍 Processing the last 10 messages to predict the next best reply...")

    try:
        # Send messages to the LLM to predict the next reply
        predicted_reply = get_answers_from_knowledge_base(formatted_messages)
        await ctx.author.send(f"🤖 **Predicted Reply:**\n{predicted_reply}")
    except Exception as e:
        print(f"Error: {e}")
        await ctx.author.send("❌ Sorry, I couldn't predict the next reply.")


bot.run('MTI4NjgwOTkyMzIwODA4NTU0OA.GN7EAL.wGXZ2P_ZuCTST5Y13fAnbWItBgAdrBQG_rVV3g')