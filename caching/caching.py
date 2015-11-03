from django.core.cache import cache



def cache_update(sender, **kwargs):
	item = kwargs.get('instance')
	cache.set(item.cache_key, item, 60*15)

def cache_evict(sender, **kwargs):
	item = kwargs.get('instance')
	cache.delete(item.cache_key)