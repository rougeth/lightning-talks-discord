import motor.motor_asyncio
from decouple import config


def mongo_client():
    database_url = config("DATABASE_URL")
    return motor.motor_asyncio.AsyncIOMotorClient(database_url).lightning


db = mongo_client()


def mongo_query(f):
    async def decorator(*args, **kwargs):
        result = await f(*args, **kwargs)
        return result or {}

    return decorator


@mongo_query
async def check_in_progress_lightning_talk(guild_id):
    return await db.lightning_talks.find_one(
        {
            "guild_id": guild_id,
            "in_progress": True,
        }
    )


@mongo_query
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


@mongo_query
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


@mongo_query
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


@mongo_query
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


@mongo_query
async def add_speaker_to_queue(lt, user):
    return await db.lightning_talks.update_one(
        {
            "guild_id": lt["guild_id"],
            "message_id": lt["message_id"],
        },
        {
            "$push": {"speakers_queue": user},
        },
    )


@mongo_query
async def remove_speaker_from_queue(lt, user):
    return await db.lightning_talks.update_one(
        {
            "guild_id": lt["guild_id"],
            "message_id": lt["message_id"],
        },
        {
            "$pull": {"speakers_queue": user},
        },
    )


@mongo_query
async def invite_speaker(lt, user_id, invite_message_id):
    lt["speakers"][str(user_id)]["invited"] = True
    lt["speakers"][str(user_id)]["invite_message_id"] = invite_message_id
    return await db.lightning_talks.update_one(
        {
            "guild_id": lt["guild_id"],
            "message_id": lt["message_id"],
        },
        {
            "$set": {"speakers": lt["speakers"]},
        },
    )
