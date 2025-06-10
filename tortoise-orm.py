from tortoise import Tortoise

TORTOISE_ORM = {
    "connections": {"default": "sqlite://db.sqlite3"},
    "apps": {
        "models": {
            "models": ["botapp.db.models", "aerich.models"],
            "default_connection": "default",
        }
    },
}