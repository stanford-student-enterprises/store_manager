from django.shortcuts import render_to_response
from django.http import HttpResponseRedirect
from django.template import RequestContext
from django.contrib.auth.decorators import login_required

from store_manager.inventory_sync.api_connectors import BigCommerceConnector, VendHQConnector, standard_vhq_connector, standard_bc_connector
from store_manager.inventory_sync.sync import save_snapshots

from store_manager.inventory_sync.models import ProductInventorySnapshot, InventorySnapshot

@login_required
def store_inventory(request):
    snapshots = InventorySnapshot.objects.filter(store="R").order_by("-date")
    if not snapshots.count():
        save_snapshots()
        snapshots = InventorySnapshot.objects.filter(store="R").order_by("-date")
    
    snapshot = snapshots[0]
    
    products = ProductInventorySnapshot.objects.filter(snapshot=snapshot)
    
    return render_to_response("inventory.html", {"type":"Store", "products":products})

@login_required 
def update_snapshots(request):
    save_snapshots()
    
    if 'next' in request.GET.keys():
        return HttpResponseRedirect(request.GET['next'])
    return HttpResponseRedirect("/")

@login_required   
def online_inventory(request):   
    snapshots = InventorySnapshot.objects.filter(store="O").order_by("-date")
    
    snapshot = snapshots[0]
    
    products = ProductInventorySnapshot.objects.filter(snapshot=snapshot)
    
    return render_to_response("inventory.html", {"type":"Online", "products":products})

@login_required  
def compare(request):
    latest_bc = InventorySnapshot.objects.filter(store="O").order_by("-date")
    latest_vhq = InventorySnapshot.objects.filter(store="R").order_by("-date")
    
    latest_bc_products = ProductInventorySnapshot.objects.filter(snapshot=latest_bc)
    latest_vhq_products = ProductInventorySnapshot.objects.filter(snapshot=latest_vhq)
    
    common_products = {}
    for product in latest_bc_products:
        common_products[product.sku] = {}
        common_products[product.sku]["O"] = product
    
    for product in latest_vhq_products:
        if product.sku in common_products.keys():
            common_products[product.sku]["R"] = product
    
    for sku in common_products.keys():
        try:
            global_product = ProductInventorySnapshot.objects.filter(store="G").filter(sku=sku).order_by("-date_added")[0]
        except:
            global_product = None
            print "Couldn't find %s" % sku
        common_products[sku]["G"] = global_product
        if "R" not in common_products[sku].keys():
            del common_products[sku]
    
    return render_to_response("compare.html", {"common_products":common_products}, context_instance=RequestContext(request))

@login_required
def product(request, sku):
    snapshots = ProductInventorySnapshot.objects.filter(sku=sku).order_by("-date_added")
    bc_snapshot = None
    vhq_snapshot = None
    if snapshots.filter(store="O").count() > 0:
        bc_snapshot = snapshots.filter(store="O")[0] 
    if snapshots.filter(store="R").count() > 0:
        vhq_snapshot = snapshots.filter(store="R")[0]
    bc = standard_bc_connector()
    vhq = standard_vhq_connector()
    
    if not snapshots.count():
        return HttpResponseRedirect("/inventory/update?next=/inventory/products/%s/" % sku)
    
    if request.method == 'POST':
        inventory = int(request.POST['inventory'])
        
        global_snapshot = ProductInventorySnapshot(sku=sku, inventory_count=inventory, store="G")
        global_snapshot.save()
        
        if bc_snapshot:
            bc.update_product_inventory(inventory, product_id=bc_snapshot.product_id, sku_id=bc_snapshot.sku_id)
        
        if vhq_snapshot:
            vhq.update_product_inventory(inventory, product_id=vhq_snapshot.vhq_product_id)
        
        snapshots = ProductInventorySnapshot.objects.filter(sku=sku).order_by("-date_added")

    if vhq_snapshot:
        product_name = vhq_snapshot.name
    else:
        product_name = bc_snapshot.name
    
    current_bc_product = None
    current_vhq_product = None
    
    if bc_snapshot:
        current_bc_product = bc.get_current_product(product_id=bc_snapshot.product_id, sku_id=bc_snapshot.sku_id)
    if vhq_snapshot:
        current_vhq_product = vhq.get_current_product(product_id=vhq_snapshot.vhq_product_id)
    
    global_snapshot = None
    if snapshots.filter(store='G').count() > 0:
        global_snapshot = snapshots.filter(store='G')[0]
    
    actual_inventory = None
    if global_snapshot: 
        actual_inventory = global_snapshot.inventory_count
        if current_bc_product:
            actual_inventory -= global_snapshot.inventory_count - current_bc_product.inventory_count
        if current_vhq_product:
            actual_inventory -= global_snapshot.inventory_count - current_vhq_product.inventory_count
    
    return render_to_response("product.html", {"snapshots":snapshots, "product_name":product_name, "sku":sku, "current_bc_product":current_bc_product, "current_vhq_product":current_vhq_product, "global_snapshot":global_snapshot, "actual_inventory":actual_inventory},
                            context_instance=RequestContext(request))