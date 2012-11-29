from django.contrib import admin
from inventory_sync.models import ProductInventorySnapshot, InventorySnapshot

admin.site.register(ProductInventorySnapshot)
admin.site.register(InventorySnapshot)