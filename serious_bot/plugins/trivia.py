from disco.bot import Plugin, Config
from disco.types.message import MessageEmbed
from disco.bot.command import CommandLevels

from serious_bot.models.user import Trivia
from peewee import SQL
import traceback

import random
import requests
import html
import json


class OpenTDB:

    class Question:

        def __init__(self, category, type, difficulty, question, correct_answer, incorrect_answers):
            self.category = category
            self.kind = type
            self.difficulty = difficulty
            self.question = html.unescape(question)
            self.answer = html.unescape(correct_answer)
            self.answers = [html.unescape(answer) for answer in incorrect_answers]
            self.caller = None

    def get_questions(self):
        response = requests.get('https://opentdb.com/api.php?amount=10').text

        data = json.loads(response)

        if len(data) == 0:
            return None

        # Parse each into a `Question` class and store it in a list.
        return [OpenTDB.Question(**k) for k in data['results']]

    def get_random(self):
        question_list = self.get_questions()

        if question_list is None:
            return None

        question = random.choice(question_list)

        all_answers = question.answers
        all_answers.append(question.answer)

        random.shuffle(all_answers)

        question.answers = all_answers

        return question


class TriviaPluginConfig(Config):
    mode = 'command'
    lock = False


@Plugin.with_config(TriviaPluginConfig)
class TriviaPlugin(Plugin):
    """
        2 modes: Command, Wait

        Command: Use `answer` to answer the trivia question
        Wait: Wait for the callers response (wait for number in chat without a command)

        TODO: Database load the mode and stuff into a map with the corresponding server or something.
        This is temporary.
    """

    def load(self, ctx):
        super(TriviaPlugin, self).load(ctx)
        self.otd = OpenTDB()
        self.active_servers = ctx.get('active_servers', {})

    def unload(self, ctx):
        ctx['active_servers'] = self.active_servers
        super(TriviaPlugin, self).unload(ctx)

    @Plugin.pre_command()
    def on_pre_command(self, command, event, _par, _brack):
        user_level = self.bot.get_level(event.author)
        if user_level and user_level >= CommandLevels.MOD:
            return event

        if event.msg.guild.id == 370720048773333002:
            if event.msg.channel_id != 394291136975601665:
                return None

        return event

    def generate_embed(self, question):
        desc = ''
        count = 1

        for answer in question.answers:
            desc += f"{count}. **{answer}**\n"
            count += 1

        embed = MessageEmbed()
        embed.description = desc
        embed.set_footer(text=f"Difficulty: {question.difficulty} | {question.category}")
        embed.color = 0x9300ff

        return embed

    @Plugin.command('trivia', parser=True)
    @Plugin.parser.add_argument('-h', action='store_true', help='Shows help')
    @Plugin.parser.add_argument('-m', action='store_true', help='Gets current trivia mode')
    @Plugin.parser.add_argument('-l', action='store_true', help='Gets current lock status')
    @Plugin.parser.add_argument('--mode', help='Sets the current trivia mode', required=False)
    @Plugin.parser.add_argument('--lock', help='User-lock trivia questions', required=False)
    def on_trivia(self, event, args):
        if event.author.id == 117789813427535878:
            if args.h:
                return event.msg.reply(event.parser.format_help())
            if args.m:
                return event.msg.reply(f"The current trivia mode is: **{self.config.mode}**")
            if args.l:
                return event.msg.reply(f"The current lock status is: **{self.config.lock}**")

            if args.mode is not None:
                self.config.mode = args.mode
                return event.msg.reply(f"Set mode to **{args.mode}**")

            if args.lock is not None:
                isLocked = False
                if args.lock == 'True':
                    isLocked = True

                self.config.lock = isLocked
                return event.msg.reply(f"Questions locked? **{isLocked}**")

        guild_id = event.msg.guild

        if guild_id is None:
            event.msg.reply('Something went wrong')
            return

        guild_id = guild_id.id
        question = self.active_servers[guild_id] if guild_id in self.active_servers else self.otd.get_random()

        if guild_id not in self.active_servers:
            question.caller = event.author.id

            self.active_servers[guild_id] = question
        else:
            event.msg.reply('There is already an active question!')

        self.log.info('Question: %s\nAnswer: %s\n', question.question, question.answer)

        if question is None:
            event.msg.reply('Something went wrong!')
            return

        embed = self.generate_embed(question)

        event.msg.reply(f"**{question.question}**", embed=embed)

    # Trivia subcommands
    @Plugin.command('leaderboard', group='trivia', parser=True)
    @Plugin.parser.add_argument('-g', action='store_true', help='Show global stats', required=False)
    def on_trivia_leaderboard(self, event, args):
        try:
            if args.g:
                users = list(Trivia.select(
                    Trivia.user_id,
                    Trivia.correct_answers,
                    Trivia.incorrect_answers,
                    Trivia.points
                ).order_by(SQL('points').desc()).limit(5).tuples())
            else:
                users = list(Trivia.select(
                    Trivia.user_id,
                    Trivia.correct_answers,
                    Trivia.incorrect_answers,
                    Trivia.points
                ).where(
                    event.guild.id == Trivia.guild_id
                ).order_by(SQL('points').desc()).limit(5).tuples())

        except Exception as e:
            print(traceback.format_exc())
            return event.msg.reply('Failed to grab leaderboard stats: ```{}```'.format(e))

        event.msg.reply('**TOP TRIVIA EXPERTS**\n' + (len(users) > 0 and '\n'.join(
            '{}. **{}** {}\n <:green_tick:435164337167138826> {} <:red_tick:435164344125489155> {}\n**{}** points'.format( # noqa
                i + 1,
                (self.state.users.get(row[0]) and self.state.users.get(row[0]).username or 'Invalid User'),
                ':crown:' if i == 0 else '',
                row[1],
                row[2],
                row[3]
            ) for i, row in enumerate(users)) or '***No trivia stats found for this server***'
        ))

    # End

    @Plugin.command('answer', '<number:int>')
    def on_answer(self, event, number):
        if self.config.mode != 'command':
            event.msg.reply('Sorry, command mode is disabled. Please just respond with the number you wish to use.')
            return

        guild_id = event.msg.guild.id

        # Make sure there is an active question
        if guild_id not in self.active_servers:
            event.msg.reply('There is not currently an active question!')
            return

        question = self.active_servers[guild_id]

        # Check if person calling it is the one answering as well for lock
        if self.config.lock == 'True' or self.config.lock:
            # Do checks
            if question.caller != event.author.id:
                return

        # print(f"Number is: {number} or {number - 1}")

        if number > len(question.answers):
            event.msg.reply(f"Please input a number 1-{len(question.answers)}")
            return

        # Used to just create a record if it doesn't already exist for the user.
        trivia_stats = Trivia.get_or_create(
           guild_id=guild_id,
           user_id=event.author.id,
           defaults={
               'correct_answers': 0,
               'incorrect_answers': 0,
               'points': 0
           }
        )

        # Now let's check if it's right or not
        if question.answers[number - 1] == question.answer:
            if question.difficulty == 'hard':
                points_gained = 3
            elif question.difficulty == 'medium':
                points_gained = 2
            else:
                points_gained = 1

            event.msg.reply('You got it right! Awesome job!\nYou got **{}** point(s)! You now have **{}**'.format(
                points_gained,
                trivia_stats.points + points_gained
            ))

            Trivia.update({
                Trivia.points: Trivia.points + points_gained,
                Trivia.correct_answers: Trivia.correct_answers + 1
            }).where(Trivia.user_id == event.author.id).execute()
        else:
            event.msg.reply(f"Nope, sorry.. The correct answer was **{question.answer}**")

            Trivia.update({
                Trivia.incorrect_answers: Trivia.incorrect_answers + 1
            }).where(Trivia.user_id == event.author.id).execute()

        del self.active_servers[guild_id]
