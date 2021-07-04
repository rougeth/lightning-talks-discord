import motor.motor_asyncio
from decouple import config


def mongo_client():
    database_url = config("DATABASE_URL")
    return motor.motor_asyncio.AsyncIOMotorClient(database_url).lightning


db = mongo_client()


async def check_in_progress_lightning_talk(guild_id):
    return await db.lightning_talks.find_one(
        {
            "guild_id": guild_id,
            "in_progress": True,
        }
    )


async def create_lightning_talk(guild_id, message_id):
    return await db.lightning_talks.insert_one(
        {
            "guild_id": guild_id,
            "message_id": message_id,
            "speakers_queue": [],
            "speakers": {},
            "in_progress": True,
            "open_registration": True,
            # TODO: created_at, updated_at
        }
    )


async def close_lightning_talk(guild_id, message_id):
    return await db.lightning_talks.update_one(
        {
            "guild_id": guild_id,
            "message_id": message_id,
        },
        {
            "$set": {"open_registration": False},
        },
    )


async def close_lightning_talk(guild_id, message_id):
    return await db.lightning_talks.update_one(
        {
            "guild_id": guild_id,
            "message_id": message_id,
        },
        {
            "$set": {"open_registration": False},
        },
    )


async def set_speakers_order(lt, speakers):
    return await db.lightning_talks.update_one(
        {
            "guild_id": lt["guild_id"],
            "message_id": lt["message_id"],
        },
        {
            "$set": {"speakers": speakers},
        },
    )