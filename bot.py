# bot.py
import logging
  # Make sure this path points to where your Flask app is initialized
import asyncio
import discord
from discord.ext import commands
from gaianet.main import update_knowledge_base
import requests
import discord
from discord.ext import commands, tasks
import asyncio
import requests
from gradient_client.tools import create_knowledge_base
from openai_chat.chat import get_answers_from_knowledge_base
from flask_app.models import PostUpvote


DISCORD_BOT_TOKEN = 'MTI4NjQxNTk2MTAwMzY1NTI2Mg.G81Yyb.2i7rSnwXrOcKKtY0QSZVNPcTk103XIqhRXknsk'

intents = discord.Intents.default()
intents.message_content = True  # Required to read message content
intents.reactions = True  # Enable reaction tracking
intents.messages = True

bot = commands.Bot(command_prefix='!', intents=intents)


# Replace with your Flask app's URL
FLASK_APP_URL = 'https://acf4-223-255-254-102.ngrok-free.app'

# Tracking upvotes every 10 seconds


admin_channel_id = 1287184435380490272


# bot.py

# Add logging configuration at the top
logging.basicConfig(level=logging.INFO)


@tasks.loop(seconds=10)  # Run every 10 seconds
async def track_upvotes():
    #logging.info("Checking for upvote changes...")

    for guild in bot.guilds:
        for channel in guild.text_channels:
            async for message in channel.history(limit=100):
                if message.reactions:
                    for reaction in message.reactions:
                        if str(reaction.emoji) == "🟢":  # Green circle emoji for upvotes
                            upvote_count = reaction.count

                            # Determine if it's a reply to a post
                            if message.reference:
                                parent_message = await channel.fetch_message(message.reference.message_id)
                                #logging.info(
                                #    f"Tracking upvote for reply: {message.content} to post: {parent_message.content}")
                                data = {
                                    'post_id': parent_message.id,
                                    'reply_id': message.id,
                                    'user_id': message.author.id,
                                    'upvotes': upvote_count
                                }
                            else:
                                #logging.info(
                                 #   f"Tracking upvote for post: {message.content}")
                                data = {
                                    'post_id': message.id,
                                    'reply_id': None,
                                    'user_id': message.author.id,
                                    'upvotes': upvote_count
                                }

                            # Capture and check upvote in Flask API
                            capture_response = requests.post(
                                f'{FLASK_APP_URL}/api/capture_upvote', json=data)

                            if capture_response.status_code == 200:
                                capture_data = capture_response.json()
                                if capture_data.get('change_detected'):
                                    logging.info(
                                        f"Upvote change detected for user {message.author.name}")

                                    # Generate token transfer link if a change is detected
                                    generate_link_response = requests.post(f'{FLASK_APP_URL}/api/generate_token_link', json={
                                        'recipient_id': message.author.id,
                                        'upvotes': capture_data.get('new_upvotes')
                                    })

                                    if generate_link_response.status_code == 200:
                                        link_data = generate_link_response.json()
                                        token_link = link_data.get('link')

                                        # Send message to admin channel
                                        admin_channel = bot.get_channel(
                                            admin_channel_id)
                                        # if message.reference:
                                        #     await admin_channel.send(
                                        #         f"User {message.author.name} received {upvote_count} upvotes for reply: {message.content} to post: {parent_message.content}.\n[Send tokens]({token_link})"
                                        #     )
                                        # else:
                                        #     await admin_channel.send(
                                        #         f"User {message.author.name} received {upvote_count} upvotes for post: {message.content}.\n[Send tokens]({token_link})"
                                        #     )

                                        # Mark notification as sent in the DB
                                        update_notification_response = requests.post(f'{FLASK_APP_URL}/api/update_notification', json={
                                            'post_id': data['post_id'],
                                            'reply_id': data['reply_id'],
                                            'notification_sent': True
                                        })

                                        if update_notification_response.status_code != 200:
                                            logging.error(
                                                f"Failed to update notification status in DB")

                                    else:
                                        logging.error(
                                            f"Error generating token link: {generate_link_response.json().get('message')}")
                            else:
                                logging.error(
                                    f"Error capturing upvote: {capture_response.json().get('message')}")

    await asyncio.sleep(10)  # Wait for 10 seconds before checking again

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user}')
    track_upvotes.start()

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
    discord_user_id = str(ctx.author.id)
    link = f"{FLASK_APP_URL}/add_and_save_network?discord_user_id={discord_user_id}&chainId={chain_id}&networkName={network_name}&rpcUrl={rpc_url}&symbol={symbol}&blockExplorerUrl={block_explorer_url}&tokenContractAddress={token_contract_address}"
    # Send link to the admin
    await ctx.author.send(f"Click this link to add the network to MetaMask and then save it: {link}")
    await ctx.send("I've sent you a direct message with the link to add and save the network.")

@bot.command(name='register_user_wallet')
async def register_user_wallet(ctx):
    discord_user_id = str(ctx.author.id)
    link = f"{FLASK_APP_URL}/switch_network?discord_user_id={discord_user_id}"
    await ctx.author.send(f"Please connect your wallet and switch to the admin's network using this link: {link}")
    await ctx.send("I've sent you a direct message with instructions to switch networks and register your wallet.")


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


@bot.command(name='redeem_my_tokens')
async def redeem_my_tokens(ctx):
    discord_user_id = str(ctx.author.id)
    user_name = ctx.author.name

    # Fetch total upvotes from Flask API
    response = requests.get(
        f'{FLASK_APP_URL}/api/get_upvotes/{discord_user_id}')

    if response.status_code == 200:
        data = response.json()

        if data['status'] == 'success':
            total_upvotes = data.get('total_upvotes', 0)
            token_link = data.get('token_link')

            # Format the message
            message_content = f"User {user_name} is requesting their rewards. They have received {total_upvotes} upvotes in total.\n"
            message_content += f"[Send tokens]({token_link})"

            # Send the message to the admin channel
            admin_channel = bot.get_channel(admin_channel_id)
            await admin_channel.send(message_content)

            await ctx.send("Your reward request has been sent to the admin.")
        else:
            await ctx.send(f"Error: {data.get('message', 'Unable to fetch upvotes.')}")
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
            output = await create_knowledge_base(text)
            await ctx.send(f"📄 **Knowledge Base Created!**")
            await ctx.send(f"📄 **Updating Knowledge Base!**")
            update_knowledge_base(output)
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