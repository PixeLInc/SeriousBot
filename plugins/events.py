from disco.bot import Plugin
from disco.bot import Bot
from disco.types.user import Game, GameType, Status

class EventsPlugin(Plugin):

    @Plugin.listen('MessageCreate')
    def on_message_create(self, event):
        self.log.info(u'{}: {}'.format(event.author, event.content))


    @Plugin.listen('PresenceUpdate')
    def on_presence_update(self, event):
        self.log.info(u'Update in {} -> {}'.format(event.guild_id, event.presence.user))


    @Plugin.listen('Ready')
    def on_ready(self, event):
        self.client.update_presence(Status.online, Game(type=GameType.watching, name='you fail at life.'))

