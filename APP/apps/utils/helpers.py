from django.core.cache import cache


def get_cached_data(key):
    try:
        data = cache.get(key)
        return data
    except Exception as e:
        print('There is some issue with the cache, was called for the key', key)
        return None