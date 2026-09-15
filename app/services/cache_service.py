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

    data = redis_client.get(key)

    if not data:
        return None

    return json.loads(data)


def get_user_by_id(user_id: int) -> dict | None:
    key = f"user:id:{user_id}"

    data = redis_client.get(key)

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


def delete_user_cache(
    user_id: int,
    email: str | None = None,
) -> None:
    redis_client.delete(
        f"user:id:{user_id}"
    )

    if email:
        redis_client.delete(
            f"user:email:{email.lower()}"
        )