from serious_bot.db import BaseModel

from peewee import BigIntegerField, TextField, SmallIntegerField

@BaseModel.register
class User(BaseModel):
    id = BigIntegerField(primary_key = True)
    username = TextField()
    discriminator = SmallIntegerField()

    user_rank = SmallIntegerField(default = 0)

    class Meta:
        db_table = 'users'

        indexes = (
            (('id', 'username', 'discriminator'), True),
        )


@BaseModel.register
class Trivia(BaseModel):
    guild_id = BigIntegerField()
    user_id = BigIntegerField()

    correct_answers = SmallIntegerField()
    incorrect_answers = SmallIntegerField()
    points = SmallIntegerField() # Small should be good.. right? :thonk:

    class Meta:
        db_table = 'trivia'

        indexes = (
            (('guild_id', 'user_id'), False),
        )
