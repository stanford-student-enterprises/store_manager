from django.db import models

STORE_CHOICES = (('O', 'Online'), ('R',  'Retail Store'), ('G', 'Global'))

class ProductInventorySnapshot(models.Model):
    store_id = models.CharField(max_length=100, blank=True, null=True)
    date_added = models.DateTimeField(auto_now_add=True)
    sku = models.CharField(max_length=100)
    name = models.CharField(max_length=100, blank=True, null=True)
    inventory_count = models.FloatField()
    store = models.CharField(max_length=2, choices=STORE_CHOICES)
    product_id = models.CharField(max_length=100, null=True, blank=True) #for BC
    sku_id = models.CharField(max_length=100, null=True, blank=True) #for BC
    vhq_product_id = models.CharField(max_length=100, null=True, blank=True) #for vhq
    snapshot = models.ForeignKey("InventorySnapshot", null=True, blank=True)

    def __unicode__(self):
        return "%s (%s): %s on %s" % (self.name, self.sku, self.inventory_count, self.date_added)

class InventorySnapshot(models.Model):
    date = models.DateTimeField(auto_now_add=True)
    store = models.CharField(max_length=2, choices=STORE_CHOICES)
    
    def __unicode__(self):
        return "%s (%s)" % (self.date, self.get_store_display())