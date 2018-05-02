from disco.bot import Plugin
from disco.types.user import Game, GameType, Status


class EventsPlugin(Plugin):

    def load(self, ctx):
        super(EventsPlugin, self).load(ctx)
        self._servers = ctx.get('servers', {})

    def unload(self, ctx):
        ctx['servers'] = self._servers
        super(EventsPlugin, self).unload(ctx)

    @Plugin.listen('MessageCreate')
    def on_message_create(self, event):
        self.log.info(u'{}: {}'.format(event.author, event.content))

        for key, attachment in event.attachments.items():
            self.log.info(u'{}, {}, {}'.format(attachment.filename, attachment.url, attachment.proxy_url))

    @Plugin.listen('PresenceUpdate')
    def on_presence_update(self, event):
        self.log.info(u'Update in {} -> {}'.format(event.guild_id, event.presence.user))

    @Plugin.listen('Ready')
    def on_ready(self, event):
        self.client.update_presence(Status.online, Game(type=GameType.watching, name='you fail at life.'))
