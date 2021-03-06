from django.conf.urls import patterns, include, url


urlpatterns = patterns('inventory_sync.views',
    url(r'store/', 'store_inventory'),
    url(r'online/',  'online_inventory'),
    url(r'update/', 'update_snapshots'),
    url(r'sync/', 'sync'),
    url(r'product/(?P<sku>\w+)/', 'product'),
    url(r'compare/', 'compare'),
)