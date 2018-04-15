from disco.bot import Plugin, Bot
from serious_bot.db import init

import serious_bot.models

class CorePlugin(Plugin):
    def load(self, ctx):
        init()

        super(CorePlugin, self).load(ctx)

