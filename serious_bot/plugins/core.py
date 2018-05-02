from disco.bot import Plugin
from serious_bot.db import init


class CorePlugin(Plugin):
    def load(self, ctx):
        init()

        super(CorePlugin, self).load(ctx)
