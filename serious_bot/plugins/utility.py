from disco.bot import Plugin
from disco.api.http import APIException
from disco.bot.command import CommandLevels

import textwrap
import subprocess

from .utils import time_convert as tc


class UtilityPlugin(Plugin):

    def load(self, ctx):
        self._eval = {}
        self._hidden_commands = ['eval', 'update']

    @Plugin.command('help')
    def on_help(self, event):
        command_list = [command for command in self.bot.commands if command.name not in self._hidden_commands]  # LIST K o m p r e h e n s i o n # noqa
        grouped = {'GENERAL': []}

        for command in command_list:
            if command.group is None:
                grouped['GENERAL'].append(command.name)
            else:
                if grouped.get(command.group) is None:
                    grouped[command.group] = []
                grouped[command.group].append(command.name)

        builder = ''
        for key, item in grouped.items():
            builder += f"**{key.upper()}:**\n{', '.join(item)}\n\n"

        event.msg.reply(builder)

    @Plugin.command('timeleft')
    def on_time_left(self, event):
        pfriday = tc.get_next_friday()

        event.msg.reply('Time left until game night: \n\n{}'.format(pfriday))

    @Plugin.command('kick', '<user:user> <reason:str...>', level=CommandLevels.ADMIN)
    def on_kick(self, event, user, reason):
        if user is None:
            return event.msg.reply('Invalid User!')

        try:
            user_dm = user.open_dm()
            guild_member = event.guild.members.get(user.id)

            user_dm.send_message(f"You have been kicked from {event.guild.name} for **{reason}**")

            guild_member.kick(reason=reason)
        except APIException as e:
            print(e)
            return event.msg.reply('Sorry, cant do that!')

        event.msg.reply(':green_tick:')

    @Plugin.command('ban', '<user:user> <reason:str...>', level=CommandLevels.ADMIN)
    def on_ban(self, event, user, reason):
        if user is None:
            return event.msg.reply('Invalid user!')

        try:
            user_dm = user.open_dm()
            guild_member = event.guild.members.get(user.id)

            user_dm.send_message(f"You have been **banned** from {event.guild.name} for **{reason}**")

            guild_member.ban(0)
        except APIException as e:
            print(e)
            return event.msg.reply('Sorry, cant do that!')

        event.msg.reply(':green_tick:')

    # Level Management - THIS IS TEMPORARY!
    @Plugin.command('set', '<user:user> <rank:str>', group='rank', level=CommandLevels.OWNER)
    def on_rank_set(self, event, user, rank):
        # for some reason you need all lower-case to get the enum
        _rank = CommandLevels.get(rank.lower())

        if not _rank:
            return event.msg.reply('Invalid rank')

        if not user:
            return

        current_rank = self.bot.get_level(user)
        author_rank = self.bot.get_level(event.author)

        if current_rank and author_rank:
            if current_rank > author_rank:
                return event.msg.reply('Woah there! You can\'t target this person.')

        self.bot.config.levels[user.id] = _rank
        event.msg.reply(f"{user.username} has been assigned '{rank}'")

    @Plugin.command('list', group='rank', level=CommandLevels.OWNER)
    def on_rank_list(self, event):
        event.msg.reply(', '.join([level for level in CommandLevels._attrs.keys()]))

    # Plugin reloading (and stuff)
    @Plugin.command('update', level=CommandLevels.OWNER)
    def on_update(self, event):
        proc = subprocess.Popen('git pull origin master', stdout=subprocess.PIPE, stderr=subprocess.STDOUT, shell=True)
        out, _ = proc.communicate()

        event.msg.reply(f"```\n{out.decode().strip()}\n```")

    @Plugin.command('list', group='plugin', level=CommandLevels.OWNER)
    def on_plugin_list(self, event):
        event.msg.reply(', '.join(self.bot.plugins.keys()))

    @Plugin.command('reload', '<plugin_name:str>', group='plugin', level=CommandLevels.OWNER)
    def on_plugin_reload(self, event, plugin_name):
        if plugin_name == 'all':
            to_reload = self.bot.plugins
            del to_reload['UtilityPlugin']

            [plugin.reload() for plugin in to_reload.values()]
            return event.msg.reply(':ok_hand:')

        plugin = self.bot.plugins.get(plugin_name)

        if plugin is None or plugin_name == 'DefaultPlugin':
            return event.msg.reply(f"{plugin_name} does not exist.")

        plugin.reload()
        event.msg.reply(":ok_hand:")

    @Plugin.command('unload', '<plugin_name:str>', group='plugin', level=CommandLevels.OWNER)
    def on_plugin_unload(self, event, plugin_name):
        plugin = self.bot.plugins.get(plugin_name)

        if plugin is None:
            return event.msg.reply(f"{plugin_name} does not exist.")

        self.bot.rmv_plugin(plugin.__class__)
        event.msg.reply(":ok_hand:")

    @Plugin.command('load', '<plugin_name:str>', group='plugin', level=CommandLevels.OWNER, disabled=True)
    def on_plugin_load(self, event, plugin_name):
        if self.bot.plugins.get(plugin_name) is not None:
            return event.msg.reply(f"{plugin_name} already exists.")

        module = __import__(self)

        print(module)

        plugin = getattr(module, plugin_name)()

        if plugin is None:
            return event.msg.reply(f"{plugin_name} doesn't exist.")

        self.bot.add_plugin(plugin)
        event.msg.reply(":ok_hand:")

    # E V A L
    @Plugin.command('eval', '<code:str...>')
    def on_eval(self, event, code):
        if event.author.id != 117789813427535878:
            return

        if self._eval.get('env') is None:
            self._eval['env'] = {}

        self._eval['env'].update({
            'bot': self.bot,
            'event': event,
            'client': self.bot.client,
            'message': event.msg,
            'channel': event.msg.channel,
            'guild': event.msg.guild,
            'author': event.author,
        })

        code = code.replace('```py\n', '').replace('```', '').replace('`', '')
        _code = 'def func(self):\n  try:\n{}\n  finally:\n    self._eval[\'env\'].update(locals())'\
                .format(textwrap.indent(code, '    '))

        try:
            exec(_code, self._eval['env'])

            func = self._eval['env']['func']
            output = func(self)

            if output is not None:
                output = repr(output)
            else:
                output = 'No output'

        except Exception as e:
            output = str(e)

        message = '```\n{}```'.format(output)

        if len(message) > 2000:
            message = message[:1980] + '... (truncated)'

        event.msg.reply(message)
