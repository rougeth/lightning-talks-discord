import motor.motor_asyncio
from decouple import config


def mongo_client():
    database_url = config("DATABASE_URL")
    return motor.motor_asyncio.AsyncIOMotorClient(database_url).lightning


db = mongo_client()


async def check_active_lightning_talk(guild_id):
    return await db.lightning_talks.find_one({
        "guild_id": guild_id,
        "is_active": True,
    })



async def create_lightning_talk(guild_id, message_id):
    return await db.lightning_talks.insert_one({
        "guild_id": guild_id,
        "message_id": message_id,
        "speakers_queue": [],
        "is_active": True,
        "is_finished": False,
        # TODO: created_at, updated_at
    })
