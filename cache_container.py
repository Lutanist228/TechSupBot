from aiocache import caches, SimpleMemoryCache

cache = SimpleMemoryCache()

caches.set_config({
    'default': {
        'cache': 'aiocache.SimpleMemoryCache',
        'serializer': {
            'class': 'aiocache.serializers.PickleSerializer'
        }
    }   
})

