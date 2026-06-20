import hashlib
import redis
from app.config import settings

_client = redis.Redis.from_url(settings.redis_url, decode_responses=True)


def _key(site_id: int, error_signature: str) -> str:
    h = hashlib.sha256(error_signature.encode()).hexdigest()[:16]
    return f"incident:{site_id}:{h}"


def should_create_incident(site_id: int, error_signature: str) -> bool:
    """Return True if no incident exists for this signature in the dedup window."""
    key = _key(site_id, error_signature)
    # SET NX with TTL — atomic
    created = _client.set(key, "1", nx=True, ex=settings.dedup_ttl_seconds)
    return bool(created)
