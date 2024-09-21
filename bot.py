# bot.py
import logging
  # Make sure this path points to where your Flask app is initialized
import asyncio
import discord
from discord.ext import commands
import requests
import discord
from discord.ext import commands, tasks
import asyncio
import requests

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


admin_channel_id = 1287119882529542144


# bot.py

# Add logging configuration at the top
logging.basicConfig(level=logging.INFO)


# @tasks.loop(seconds=10000)  # Run every 10 seconds
# async def track_upvotes():
#     logging.info("Checking for upvote changes...")

#     for guild in bot.guilds:
#         for channel in guild.text_channels:
#             async for message in channel.history(limit=100):
#                 if message.reactions:
#                     for reaction in message.reactions:
#                         if str(reaction.emoji) == "🟢":  # Green circle emoji for upvotes
#                             upvote_count = reaction.count

#                             # Determine if it's a reply to a post
#                             if message.reference:
#                                 parent_message = await channel.fetch_message(message.reference.message_id)
#                                 logging.info(
#                                     f"Tracking upvote for reply: {message.content} to post: {parent_message.content}")
#                                 data = {
#                                     'post_id': parent_message.id,
#                                     'reply_id': message.id,
#                                     'user_id': message.author.id,
#                                     'upvotes': upvote_count
#                                 }
#                             else:
#                                 logging.info(
#                                     f"Tracking upvote for post: {message.content}")
#                                 data = {
#                                     'post_id': message.id,
#                                     'reply_id': None,
#                                     'user_id': message.author.id,
#                                     'upvotes': upvote_count
#                                 }

#                             # Capture and check upvote in Flask API
#                             capture_response = requests.post(
#                                 f'{FLASK_APP_URL}/api/capture_upvote', json=data)

#                             if capture_response.status_code == 200:
#                                 capture_data = capture_response.json()
#                                 if capture_data.get('change_detected'):
#                                     logging.info(
#                                         f"Upvote change detected for user {message.author.name}")

#                                     # Generate token transfer link if a change is detected
#                                     generate_link_response = requests.post(f'{FLASK_APP_URL}/api/generate_token_link', json={
#                                         'recipient_id': message.author.id,
#                                         'upvotes': capture_data.get('new_upvotes')
#                                     })

#                                     if generate_link_response.status_code == 200:
#                                         link_data = generate_link_response.json()
#                                         token_link = link_data.get('link')

#                                         # Send message to admin channel
#                                         admin_channel = bot.get_channel(
#                                             admin_channel_id)
#                                         if message.reference:
#                                             await admin_channel.send(
#                                                 f"User {message.author.name} received {upvote_count} upvotes for reply: {message.content} to post: {parent_message.content}.\n[Send tokens]({token_link})"
#                                             )
#                                         else:
#                                             await admin_channel.send(
#                                                 f"User {message.author.name} received {upvote_count} upvotes for post: {message.content}.\n[Send tokens]({token_link})"
#                                             )

#                                         # Mark notification as sent in the DB
#                                         update_notification_response = requests.post(f'{FLASK_APP_URL}/api/update_notification', json={
#                                             'post_id': data['post_id'],
#                                             'reply_id': data['reply_id'],
#                                             'notification_sent': True
#                                         })

#                                         if update_notification_response.status_code != 200:
#                                             logging.error(
#                                                 f"Failed to update notification status in DB")

#                                     else:
#                                         logging.error(
#                                             f"Error generating token link: {generate_link_response.json().get('message')}")
#                             else:
#                                 logging.error(
#                                     f"Error capturing upvote: {capture_response.json().get('message')}")

#     await asyncio.sleep(10)  # Wait for 10 seconds before checking again

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user}')
    #track_upvotes.start()

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


bot.run('MTI4NjQxNTk2MTAwMzY1NTI2Mg.G81Yyb.2i7rSnwXrOcKKtY0QSZVNPcTk103XIqhRXknsk')