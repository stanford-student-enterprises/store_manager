from store_manager.inventory_sync.api_connectors import BigCommerceConnector, VendHQConnector, standard_vhq_connector, standard_bc_connector

from store_manager.inventory_sync.models import InventorySnapshot, ProductInventorySnapshot

from django.core.exceptions import ObjectDoesNotExist

class InventorySyncer:
    def __init__(self, bc_connector, vhq_connector):
        self.bc_connector = bc_connector
        self.vhq_connector = vhq_connector
        self.bc_products = self.bc_connector.products()
        self.vhq_products = self.vhq_connector.products()
        
    def product_intersection(self):
        common_products = {}
        for bc_product in self.bc_products:
            for vhq_product in self.vhq_products:
                if bc_product.sku == vhq_product.sku:
                    common_products[bc_product.sku] = {"O":bc_product,"R":vhq_product}
        return common_products
    
    def sync_products(self):
        for sku, product_dict in self.product_intersection().items():
            print "Syncing %s" % (product_dict)
            try:
                last_global_snapshot = ProductInventorySnapshot.objects.filter(sku=sku).filter(store="G").latest("date_added")
            except ObjectDoesNotExist:
                print "\t No global snapshot found"
                continue
            vhq_product = product_dict['R']
            bc_product = product_dict['O']
            previous_inventory = last_global_snapshot.inventory_count
            vhq_sold = previous_inventory - vhq_product.inventory_count
            bc_sold = previous_inventory - bc_product.inventory_count
            new_inventory = previous_inventory - vhq_sold - bc_sold
            
            if vhq_sold < 0 or bc_sold < 0 or new_inventory > previous_inventory:
                print "\t Looks like there was a problem: Previous: %d, VHQ Sold: %d, BC Sold: %d, New: %d" % (previous_inventory, vhq_sold, bc_sold, new_inventory)
                continue
            
            self.bc_connector.update_product_inventory(new_inventory, product_id=bc_product.product_id, sku_id=bc_product.sku_id)
            self.vhq_connector.update_product_inventory(new_inventory, product_id=vhq_product.vhq_product_id)
            print "\t Synced: Previous: %d, VHQ Sold: %d, BC Sold: %d, New: %d" % (previous_inventory, vhq_sold, bc_sold, new_inventory)
        
        save_snapshots()
     
def save_snapshots():
    bc_connector = standard_bc_connector()
    vhq_connector = standard_vhq_connector()
    
    bc_snapshot = InventorySnapshot(store="O")
    vhq_snapshot = InventorySnapshot(store="R")
    
    bc_snapshot.save()
    vhq_snapshot.save()
    
    for product in bc_connector.products():
        product.snapshot = bc_snapshot
        product.save()
        
    for product in vhq_connector.products():
        product.snapshot = vhq_snapshot
        product.save()   

def default_syncer():
    return InventorySyncer(standard_bc_connector(), standard_vhq_connector())
    
    
if __name__ == '__main__':
    print InventorySyncer()