from disco.bot import Plugin
from disco.types.message import MessageEmbed

from datetime import datetime
import random

from .dyk import didyouknow
import urbandictionary as ud

class FunPlugin(Plugin):

    @Plugin.pre_command()
    def on_pre_command(self, command, event, _par, _brack):
        if event.msg.guild.id == 370720048773333002:
            if event.msg.channel_id != 407414352073719809:
                return None

        return event

    @Plugin.command('dyk')
    def on_dyk(self, event):
        # self.client.api.channels_typing(event.msg.channel_id)

        (fact, name) = didyouknow.grab_fact()

        embed = MessageEmbed()
        embed.description = f"**{fact}**"
        embed.set_footer(text=name)
        embed.timestamp = datetime.utcnow().isoformat()
        embed.color = '10038562'

        with self.client.api.capture() as requests:
            event.msg.reply('', embed=embed)
            for request in requests:
                print('Request Made: {}'.format(request.response))
                print('Exception Thrown: {}'.format(request.exception))

    @Plugin.command('urban', '[phrase:str...]', disabled=True)
    def on_urban(self, event, phrase = None):
        # self.client.api.channels_typing(event.msg.channel_id)

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

