# bot.py
import asyncio
import discord
from discord.ext import commands
import os

intents = discord.Intents.default()
intents.message_content = True  # Required to read message content

bot = commands.Bot(command_prefix='!', intents=intents)

# Replace with your Flask app's URL
FLASK_APP_URL = 'http://localhost:5000'

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
        chain_id_str, network_name, rpc_url, symbol, block_explorer_url = [
            param.strip() for param in params.split(',')]
        # Automatically handles hex (e.g., '0x64')
        print(chain_id_str)
        chain_id = chain_id_str
        print(chain_id)
    except ValueError:
        await ctx.send("Invalid parameters. Please provide: chainId, networkName, rpcUrl, symbol, blockExplorerUrl")
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

@bot.command(name='upload_text')
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
            await ctx.send(f"📄 **Text from file:**\n{text}")
        else:
            await ctx.send('❌ Please upload a file with a `.txt` extension.')
    elif message.content:
        text = message.content
        await ctx.send(f"📝 **Received text:**\n{text}")
    else:
        await ctx.send('⚠️ No text or file received. Please try again.')
        
bot.run('MTI4NjQxNTk2MTAwMzY1NTI2Mg.G81Yyb.2i7rSnwXrOcKKtY0QSZVNPcTk103XIqhRXknsk')