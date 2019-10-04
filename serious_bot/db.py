from peewee import Proxy, Model
from playhouse.postgres_ext import PostgresqlExtDatabase

database = Proxy()
MODELS = []


class BaseModel(Model):
    class Meta:
        database = database

    @staticmethod
    def register(cls):
        print(f"Registering {cls}")
        MODELS.append(cls)
        return cls


def init():
    print("INITIALIZING DATABASE AND LOADING MODELS...")
    database.initialize(
        PostgresqlExtDatabase(
            "seriousbot_dev", user="postgres", port=5432, autorollback=True
        )
    )

    for model in MODELS:
        print(f"Looping {model}")
        model.create_table(True)

        if hasattr(model, "SQL"):
            database.execute_sql(model.SQL)


def reset():
    init()

    for model in MODELS:
        model.drop_table(True)
        model.create_table(True)
