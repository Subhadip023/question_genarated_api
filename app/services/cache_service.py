import json
import redis

from app.config import settings


redis_client = redis.Redis.from_url(
    settings.redis_url,
    decode_responses=True,
    protocol=2,
)

USER_CACHE_TTL = 3600


def get_user_by_email(email: str) -> dict | None:
    key = f"user:email:{email.lower()}"

    try:
        data = redis_client.get(key)
    except redis.RedisError:
        # Redis is unavailable → caller will use MySQL
        return None

    if not data:
        return None

    return json.loads(data)


def get_user_by_id(user_id: int) -> dict | None:
    key = f"user:id:{user_id}"

    try:
        data = redis_client.get(key)
    except redis.RedisError:
        # Redis is unavailable → caller will use MySQL
        return None

    if not data:
        return None

    return json.loads(data)


def cache_user(user) -> None:
    data = {
        "id": user.id,
        "role": user.role,
        "name": user.name,
        "email": user.email,
        "password": user.password,
        "created_at": user.created_at.isoformat(),
        "updated_at": user.updated_at.isoformat(),
    }

    try:
        redis_client.setex(
            f"user:email:{user.email.lower()}",
            USER_CACHE_TTL,
            json.dumps(data),
        )

        redis_client.setex(
            f"user:id:{user.id}",
            USER_CACHE_TTL,
            json.dumps(data),
        )

    except redis.RedisError:
        # Redis unavailable → don't break login/registration
        pass


def delete_user_cache(
    user_id: int,
    email: str | None = None,
) -> None:
    try:
        redis_client.delete(f"user:id:{user_id}")

        if email:
            redis_client.delete(
                f"user:email:{email.lower()}"
            )

    except redis.RedisError:
        # Redis unavailable → nothing to invalidate
        pass