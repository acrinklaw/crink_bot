import base64
import io
import json
import random
import tempfile

import asyncpraw
import discord
import requests
from dotenv import dotenv_values

from plot import plot_probability

config = dotenv_values(".env")


class DiscordClient(discord.Client):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.item_dict = self.load_runescape_icons()

    def load_runescape_icons(self) -> dict:
        """
        Load base64 encoded strings for OSRS item icons from a JSON file
        """
        with open("data/item-icons.json", "r") as infile:
            item_dict = json.load(infile)

        return item_dict

    async def on_message(self, message):
        """
        Processes and parses various commands given a message event
        """
        if message.author.id == self.user.id:
            return

        if message.content.lower().startswith("findme"):
            self.stats[message.author] += 1
            try:
                subreddit = message.content.split(" ")[1]
                threshold = int(message.content.split(" ")[2])
                await self.scrape_reddit(message, subreddit, threshold)
            except:
                await message.channel.send(
                    f"Example command usage: ```findme dankmemes 100```"
                )

        if message.content.lower() == "test_image":
            await self.send_base64_image(message)

        if message.content.lower().startswith("fetch_last_item"):
            user = (" ").join(message.content.lower().split(" ")[1:])
            await self.get_most_recent_item(message, user)

        if message.content.lower().startswith("dropchance"):
            content = message.content.lower().split(" ")[1:]
            trials = int(content[0])
            probability = int(content[1])
            await self.plot_probability(message, trials, probability)

        if message.content.lower() == "^help":
            await self.help(message)

    async def help(self, message):
        """ """
        embed = discord.Embed(
            title="Crink Bot", description="Crink's discord bot", color=0x4B0082
        )
        embed.add_field(
            name="findme", value="Search for image posts from a subreddit", inline=False
        )
        await message.channel.send(embed=embed)

    async def search_subreddit(self, message, subreddit, threshold=100):
        """ """
        reddit = asyncpraw.Reddit(
            client_id=config["reddit_client_id"],
            client_secret=config["reddit_client_secret"],
            user_agent="crink-bot",
        )

        subreddit = await reddit.subreddit(subreddit, fetch=True)
        await message.channel.send(
            f"...parsing the top {threshold} posts from the {subreddit.display_name} subreddit for the past month..."
        )

        results = [
            submission async for submission in subreddit.top("month", limit=threshold)
        ]
        selected = random.randint(1, len(results))
        choice = results[selected - 1].url
        embed = discord.Embed(title="Crink Bot", description="", color=0x4B0082)

        if "jpg" in choice or "png" in choice:
            embed.image(url=choice)
            await message.channel.send(embed=embed)
        else:
            await message.channel.send(choice)

    """
    async def collection_log_roulette(self):
        pass
    """

    async def plot_probability(self, message, trials, probability):
        """
        Plot the success distribution given a probability of receiving an item
        Annotates the plot with where you are at on the curve given # of trials
        """
        with tempfile.NamedTemporaryFile(suffix=".png") as outfile:
            plot_probability(trials, probability, outfile.name)
            await message.channel.send(file=discord.File(outfile.name))

    async def get_most_recent_item(self, message, username):
        """
        Queries the collection log API to return the last received item
        Posts a base64 encoded image representing the item
        """
        url = f"https://api.collectionlog.net/items/recent/{username}"

        response = requests.get(url).json()
        for index, item in enumerate(response["items"]):
            if index >= 1:
                break
            item_id = str(item["id"])
            item_name = item["name"]
            item_date = item["obtainedAt"].split("T")[0]
            await self.send_base64_image(message, item_id)
            await message.channel.send(
                f"{username}'s last collection log slot obtained was {item_name} on {item_date}"
            )

    async def send_base64_image(self, message, item_id):
        """
        Decode a base64 encoded string that represents a picture
        """
        file = discord.File(
            io.BytesIO(base64.b64decode(self.item_dict[item_id])), filename="temp.jpg"
        )
        await message.channel.send(file=file)


intents = discord.Intents.all()
intents.members = True
game = discord.Game("^help")
client = DiscordClient(intents=intents, activity=game)
client.run(config["discord_client_token"])
