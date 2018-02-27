from disco.bot import Plugin
from disco.bot import Bot
from disco.api.http import APIException

import sys
import textwrap
import traceback
import subprocess

from .utils import time_convert as tc

class UtilityPlugin(Plugin):

    def load(self, ctx):
        self._eval = {}

    @Plugin.command('help')
    def on_help(self, event):
        commands = []

        for st, plugin in self.bot.plugins.items():
            for command in plugin.commands:
                if command.name == event.command.name:
                    continue

                commands.append(command.name)

        event.msg.reply(', '.join(commands))

    @Plugin.command('timeleft')
    def on_time_left(self, event):
        pfriday = tc.get_next_friday()

        event.msg.reply('Time left until game night: \n\n{}'.format(pfriday))

    @Plugin.command('kick', '<user:user> <reason:str...>')
    def on_kick(self, event, user, reason):
        if event.author.id != 117789813427535878:
            return

        if user is None:
            return event.msg.reply('Invalid User!')

        try:
            user_dm = user.open_dm()
            guild_member = event.guild.get_member(user)

            user_dm.send_message(f"You have been kicked from {event.guild.name} for **{reason}**")

            guild_member.kick(reason=reason)
        except APIException as e:
            print(e)
            return event.msg.reply('Sorry, cant do that!')

        event.msg.reply(':green_tick:')

    # Plugin reloading (and stuff)
    @Plugin.command('update')
    def on_update(self, event):
        if event.author.id != 117789813427535878: # (IS_ME DECORATOR WHEN!? or ranks..?!)
            return

        proc = subprocess.Popen('git pull origin master', stdout=subprocess.PIPE, stderr=subprocess.STDOUT, shell=True)
        out, _ = proc.communicate()

        event.msg.reply(f"```\n{out.decode().strip()}\n```")

    @Plugin.command('list', group='plugin')
    def on_list(self, event):
        if event.author.id != 117789813427535878:
            return

        event.msg.reply(', '.join(self.bot.plugins.keys()))

    @Plugin.command('reload', '<plugin_name:str>', group='plugin')
    def on_reload(self, event, plugin_name):
        if event.author.id != 117789813427535878:
            return

        if plugin_name == 'all':
            to_reload = self.bot.plugins
            del to_reload['UtilityPlugin'] # Find a way to reload the current plugin

            [plugin.reload() for plugin in to_reload.values()]
            return event.msg.reply(':ok_hand:')

        plugin = self.bot.plugins.get(plugin_name)

        if plugin is None or plugin_name == 'DefaultPlugin':
            return event.msg.reply(f"{plugin_name} does not exist.")

        plugin.reload()
        event.msg.reply(":ok_hand:")

    @Plugin.command('unload', '<plugin_name:str>', group='plugin')
    def on_unload(self, event, plugin_name):
        if event.author.id != 117789813427535878:
            return

        plugin = self.bot.plugins.get(plugin_name)

        if plugin is None:
            return event.msg.reply(f"{plugin_name} does not exist.")

        self.bot.rmv_plugin(plugin.__class__)
        event.msg.reply(":ok_hand:")

    @Plugin.command('load', '<plugin_name:str>', group='plugin', disabled=True)
    def on_load(self, event, plugin_name):
        if event.author.id != 117789813427535878:
            return

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
            # tback = ''.join(traceback.format_exception(type(e), e, e.__traceback__)).replace('/mnt/backup/Coding/Langs/Python/gobot-py/plugins/', '')
            output = str(e)


        message = '```\n{}```'.format(output)

        if len(message) > 2000:
            message = message[:1980] + '... (truncated)'

        event.msg.reply(message)


