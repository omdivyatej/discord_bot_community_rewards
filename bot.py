import discord
from discord.ext import commands
import json
import os

intents = discord.Intents.default()
intents.message_content = True  # Needed to read message content
intents.messages = True         # Needed to receive message events
intents.reactions = True        # Needed to read reactions

bot = commands.Bot(command_prefix='!', intents=intents)

# Load previous message data from JSON file
if os.path.exists('message_data.json'):
    with open('message_data.json', 'r') as f:
        message_data = json.load(f)
else:
    message_data = {}


@bot.command()
async def analyze_messages(ctx):
    bot_statistics_channel = discord.utils.get(
        ctx.guild.channels, name="bot-statistics")
    if not bot_statistics_channel:
        await ctx.send("The 'bot-statistics' channel does not exist.")
        return

    source_channel = ctx.channel  # The channel where the command was invoked

    updated_message_data = {}

    async for message in source_channel.history(limit=None, oldest_first=True):
        if message.author.bot:
            continue

        message_id_str = str(message.id)

        # Collect replies to the message
        replies = []
        async for potential_reply in source_channel.history(limit=None, oldest_first=True):
            if (potential_reply.reference and
                potential_reply.reference.message_id == message.id and
                    potential_reply.id != message.id):
                replies.append(potential_reply)

        num_replies = len(replies)

        # Only process messages with at least one reply
        if num_replies == 0:
            continue

        # Count green upvote reactions on each reply
        upvote_counts = {}
        for reply in replies:
            green_upvote_count = 0
            for reaction in reply.reactions:
                # Replace with your green upvote emoji
                if (str(reaction.emoji) == '🟢' or
                        (hasattr(reaction.emoji, 'name') and reaction.emoji.name == 'green_upvote')):
                    green_upvote_count = reaction.count
            upvote_counts[str(reply.id)] = green_upvote_count

        # Determine the winner
        if upvote_counts:
            winner_reply_id = max(upvote_counts, key=upvote_counts.get)
            winner_reply = None
            for reply in replies:
                if str(reply.id) == winner_reply_id:
                    winner_reply = reply
                    break
            winner_username = winner_reply.author.display_name
            highest_upvotes = upvote_counts[winner_reply_id]
        else:
            winner_username = "No replies with green upvotes"
            highest_upvotes = 0

        # Prepare current data for this message
        current_data = {
            'num_replies': num_replies,
            'highest_upvotes': highest_upvotes
        }

        # Get previous data for this message
        prev_data = message_data.get(message_id_str)

        # Compare current data with previous data
        if not prev_data or prev_data != current_data:
            # There is a change, so we report it
            embed = discord.Embed(title="Message Analysis",
                                  color=discord.Color.green())
            embed.add_field(name="Original Message",
                            value=message.content, inline=False)
            embed.add_field(name="Number of Replies",
                            value=num_replies, inline=True)
            embed.add_field(name="Winner", value=winner_username, inline=True)
            embed.add_field(name="Highest Upvotes",
                            value=highest_upvotes, inline=True)
            await bot_statistics_channel.send(embed=embed)

        # Update the message data
        updated_message_data[message_id_str] = current_data

    # Save the updated message data to the JSON file
    with open('message_data.json', 'w') as f:
        json.dump(updated_message_data, f)

    await ctx.send("Analysis complete.")


bot.run('MTI4NjQxNTk2MTAwMzY1NTI2Mg.G81Yyb.2i7rSnwXrOcKKtY0QSZVNPcTk103XIqhRXknsk')
