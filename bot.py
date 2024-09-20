# bot.py
import discord
from discord.ext import commands
import os

# Define the intents
intents = discord.Intents.default()
intents.messages = True
intents.dm_messages = True
intents.message_content = True  # Required to read message content

bot = commands.Bot(command_prefix='!', intents=intents)

# Replace with your Flask app's URL
FLASK_APP_URL = 'http://localhost:5000'


@bot.event
async def on_ready():
    print(f'Logged in as {bot.user}')


@bot.command()
async def register_wallet(ctx):
    discord_user_id = str(ctx.author.id)
    link = f"{FLASK_APP_URL}/?discord_user_id={discord_user_id}"
    print(link)
    await ctx.author.send(f"Please connect your wallet using this link: {link}")
    await ctx.send("I've sent you a direct message with instructions to connect your wallet.")


bot.run('MTI4NjQxNTk2MTAwMzY1NTI2Mg.G81Yyb.2i7rSnwXrOcKKtY0QSZVNPcTk103XIqhRXknsk')