from urllib.parse import urlencode

from discord import Message, Embed
from discord.ext.commands import (BadArgument, Bot, Context, EmojiConverter,
                                  command)

from bot.constants import EVERYONE_REACTIONS

from requests import get

import ipdb


class Fun:
    """
    Commands for fun!
    """

    def __init__(self, bot: Bot):
        self.bot = bot

    async def on_message(self, message: Message):
        # React if a message contains an @here or @everyone mention.
        if any(
                mention in message.content
                for mention in ("@here", "@everyone")):
            for emoji in EVERYONE_REACTIONS:
                await message.add_reaction(emoji)

        # React if message contains dabato.
        if "dabato" in message.content:
            await message.add_reaction("🤔")

    @command()
    async def lmgtfy(search_text: str, *args):
        """
        Lets the bot google tself, ctx: Context,hat for you.
        """

        # Flag checking.
        delete = False
        ie = False
        if "-d" in args:
            delete = True
        if "-ie" in args:
            ie = True

        # Creates a lmgtfy.com url for the given query.
        request_data = {"q": search_text, "ie": int(ie)}
        url = "https://lmgtfy.com/?" + urlencode(request_data)

        await ctx.send(url)

        if delete:
            await ctx.message.delete()

    @command()
    async def react(self, ctx: Context, *reactions: str):
        """
        Reacts to the previous message with the given space-separated emojis.
        """
        # Added mutability
        reactions = list(reactions)

        # Detect if message number is present in the invocation arguments.
        msg_num = 1
        if reactions[0].isdigit():
            msg_num += int(reactions.pop(0))
        else:
            msg_num += 1

        # Getting the message to react to.
        message = await ctx.channel.history(limit=msg_num, reverse=True).next()
        await ctx.message.delete()

        unknown_emojis = []

        # Reacts to the message.
        for reaction in reactions:
            if len(reaction) > 1:
                try:
                    reaction = await EmojiConverter().convert(ctx, reaction)
                except BadArgument:
                    unknown_emojis.append(reaction)
                    continue
            await message.add_reaction(reaction)

        # Informs the user of unknown emojis.
        if unknown_emojis:
            emoji_string = ", ".join(unknown_emojis)
            await ctx.send(f"Unknown emojis: {emoji_string}")

    @command()
    async def xkcd(self, ctx: Context, number=None):
        """
        Fetches the latest XKCD comic, or one requested by the user.
        """

        # Creates endpoint URI
        if number is None:
            endpoint = "https://xkcd.com/info.0.json"
        else:
            endpoint = f"https://xkcd.com/{number}/info.0.json"

        # Fetches JSON data from endpoint
        data = get(endpoint).json()
        ipdb.set_trace()
        # Updates comic number
        number = data["num"]

        # Creates Rich Embed and populates it with JSON data

        comic = Embed()
        comic.title = data["safe_title"]
        comic.description = data["alt"]
        comic.image.url = data["img"]
        comic.url = f"https://xkcd.com/{number}"
        comic.author.name = "xkcd"
        comic.author.url = "https://xkcd.com/"
        comic.author.icon_url = "https://xkcd.com/favicon.ico"

        # Sends Embed
        await ctx.send(embed=comic)


def setup(bot):
    bot.add_cog(Fun(bot))
