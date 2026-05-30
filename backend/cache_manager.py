from gptcache import Cache
from gptcache.manager import manager_base
from gptcache.processor.pre import get_content_input
def init_cache():
    cache = Cache()
    cache.init(
        pre_embedding_func=get_content_input,
        data_manager=manager_base("sqlite", "sqlite", cache_base_dir="./cache_data")
    )
    return cache
question_cache = init_cache()
def get_cached_answer(question: str) -> str | None:
    return question_cache.get(question)
def set_cached_answer(question: str, answer: str):
    question_cache.put(question, answer)
