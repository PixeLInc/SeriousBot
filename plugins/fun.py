from disco.bot import Plugin
from disco.types.message import MessageEmbed
from disco.bot.command import CommandLevels

from datetime import datetime
import random

from .dyk import didyouknow
from .utils.roast import Roast
from .utils.reddit_scraper import Reddit
import urbandictionary as ud

class FunPlugin(Plugin):

    def load(self, ctx):
        self.roaster = Roast()
        self.reddit = Reddit('dankmemes')

        # Just scrape them right off the bat and get it over with
        # TODO: Sync them every now and then?
        self.memes = self.reddit.scrape_posts()

        print(f"Loaded {len(self.memes)} memes into the cache.")

    @Plugin.pre_command()
    def on_pre_command(self, command, event, _par, _brack):
        user_level = self.bot.get_level(event.author)
        # Staff can use whatever, anywhere.
        if user_level and user_level >= CommandLevels.MOD:
            return event

        if event.msg.guild.id == 370720048773333002:
            if event.msg.channel_id != 407414352073719809:
                return None

        return event

    @Plugin.command('dyk')
    def on_dyk(self, event):
        self.client.api.channels_typing(event.msg.channel_id)

        (fact, name) = didyouknow.grab_fact()

        embed = MessageEmbed()
        embed.description = f"**{fact}**"
        embed.set_footer(text=name)
        embed.timestamp = datetime.utcnow().isoformat()
        embed.color = '10038562'

        event.msg.reply(embed=embed)

    @Plugin.command('urban', '[phrase:str...]')
    def on_urban(self, event, phrase = None):
        self.client.api.channels_typing(event.msg.channel_id)

        urban_entry = None

        if phrase is None:
            urban_entry = random.choice(ud.random()) # grab some random words | list of urbandef
        else:
            defs = ud.define(phrase)

            if len(defs) > 0:
                urban_entry = defs[0]

        if urban_entry is None:
            event.msg.reply('Failed to find a definition for that!')
        else:
            definition = urban_entry.definition
            # Let's do a little... checking!
            if len(definition) >= 2000:
                definition = definition[:1950] + '...'

            # Let's construct an embed :)
            embed = MessageEmbed()
            embed.title = f"**Defintion of {urban_entry.word}**"
            embed.description = definition

            embed.add_field(name='Example', value=urban_entry.example)
            embed.add_field(name='Rating', value=f"{urban_entry.upvotes} 👍 | {urban_entry.downvotes} 👎")

            embed.color = '5824574'

            event.msg.reply(embed=embed)

    @Plugin.command('roast')
    def on_roast(self, event):
        roast = self.roaster.get_random()

        event.msg.reply(f"{event.author.mention}, {roast}")

    @Plugin.command('meme')
    def on_reddit(self, event):
        event.msg.reply(self.reddit.random_url(self.memes))


