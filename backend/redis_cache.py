import redis
import hashlib
redis_client = redis.Redis(host='localhost', port=6379, decode_responses=True)
def get_cache_key(prompt: str, model: str = "llama3.2:1b") -> str:
    return hashlib.md5(f"{model}:{prompt}".encode()).hexdigest()
def cache_response(prompt: str, response: str, model: str = "llama3.2:1b", ttl: int = 3600):
    redis_client.setex(get_cache_key(prompt, model), ttl, response)
def get_cached_response(prompt: str, model: str = "llama3.2:1b") -> str | None:
    return redis_client.get(get_cache_key(prompt, model))
