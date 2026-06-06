import diskcache
import hashlib
cache = diskcache.Cache("D:/HUNDREDXMIND/data/llm_cache")
def get_cache_key(prompt: str, model: str = "llama3.2:1b") -> str:
    return hashlib.md5(f"{model}:{prompt}".encode()).hexdigest()
def cache_response(prompt: str, response: str, model: str = "llama3.2:1b", ttl: int = 3600):
    key = get_cache_key(prompt, model)
    cache.set(key, response, expire=ttl)
def get_cached_response(prompt: str, model: str = "llama3.2:1b") -> str | None:
    key = get_cache_key(prompt, model)
    return cache.get(key)
