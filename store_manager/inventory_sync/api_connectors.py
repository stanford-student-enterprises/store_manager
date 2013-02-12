from base64 import b64encode
import httplib2
import json
from urllib import urlencode

from models import ProductInventorySnapshot
                
class StoreAPIConnector(object):
    def __init__(self, username, api_token, base_api_url):
        self.username = username
        self.api_token = api_token
        self.base_api_url = base_api_url
        self.token = b64encode("%s:%s" % (self.username, self.api_token))
        self.auth_header_string = 'Basic %s' % self.token
        self.cached_products = None
        self.cached_sku_to_inventory = {}
     
    def make_request(self, method, url, headers={}, body=""):
        full_headers = {"Authorization":self.auth_header_string}
        if headers:
            full_headers.update(headers)

        h = httplib2.Http()
        if method == 'GET':
            resp, content = h.request(self.base_api_url + url, method, "", full_headers)
        elif method == 'PUT':
            resp, content = h.request(self.base_api_url + url, method, body=body, headers=full_headers)
        elif method == 'POST':
            print body
            resp, content = h.request(self.base_api_url + url, method, body=body, headers=full_headers)
            print resp
            print content
        if resp['status'] == 401:
            raise Error("Unauthorized request")
        try:
            result = json.loads(content)
        except:
            result = []
        return result
    
    def product_skus_with_inventory(self):
        if not self.cached_sku_to_inventory:
            d = {}
            for product in self.products():
                d[product.sku] = product.inventory_level
            self.cached_sku_to_inventory = d
        return self.cached_sku_to_inventory
        
    def update_product_inventory(self, sku, new_count):
        pass
    
    def product_inventory_count(self, sku):
         if sku in self.product_skus_with_inventory():
            return self.product_skus_with_inventory()[sku]
         else:
            return None
            
    def products(self):
        raise NotImplementedError
    
    def get_matching_product(self, other_product):
        for product in self.products():
            if product.approx_equals(other_product):
                return product
                       
class BigCommerceConnector(StoreAPIConnector):
    def __init__(self, *args, **kwargs):
        super(BigCommerceConnector, self).__init__(*args, **kwargs)
        self.cached_options = {}
        
    def load_options(self):
        page = 1
        while True:
            data = self.make_request('GET', '/options/values.json?page=%d' % page)
            if not len(data) or data[0]['id'] in self.cached_options.keys():
                break
            for option in data:
                self.cached_options[option['id']] = option['label']
            page += 1
        
        
        
    def num_products(self):
        return self.make_request('GET', '/products/count')
    
    def product_from_json(self, json):
        return ProductInventorySnapshot(store_id = json['id'],
                                        name = json['name'], 
                                        sku = json['sku'], 
                                        inventory_count = json['inventory_level'],
                                        store = 'O')
    
    def product_from_sku_json(self, product, json):
        options = json['options']
        option_value_ids = [o['option_value_id'] for o in options]
                
        name = product.name
        name += " - %s" % (",".join([self.cached_options[option_id] if option_id in self.cached_options.keys() else "" for option_id in option_value_ids]))
        
        return ProductInventorySnapshot(store_id = product.store_id,
                                        name = name,
                                        sku = json['sku'],
                                        product_id = json['product_id'],
                                        sku_id=json['id'],
                                        inventory_count = json['inventory_level'],
                                        store = 'O')
    
    def products(self):
        if not self.cached_options:
            self.load_options()    
        if not self.cached_products:
            page = 1
            self.cached_products = []
            while len(self.cached_products) < self.num_products():
                product_response = self.make_request('GET', '/products.json?page=%d' % (page))
                if len(product_response) == 0:
                    break
                for product_json in product_response:
                    product = self.product_from_json(product_json)
                    skus_json = self.make_request('GET', '/products/%s/skus.json' % (product.store_id))
                    for sku_json in skus_json:
                        sku_product = self.product_from_sku_json(product, sku_json)
                        self.cached_products.append(sku_product)
                page += 1
        
        return self.cached_products
    
    def get_current_product(self, sku=None, product_id=None, sku_id=None):
        if product_id is not None and sku_id is not None:
            product_response = self.make_request('GET', '/products/%s.json' % product_id)
            product = self.product_from_json(product_response)
            product_sku_response = self.make_request('GET', '/products/%s/skus/%s.json' % (product_id, sku_id))
            
            return self.product_from_sku_json(product, product_sku_response)
    
    def update_product_inventory(self, inventory, product_id=None, sku_id=None):
        if product_id is not None and sku_id is not None:
            body = "<sku><inventory_level>%d</inventory_level></sku>" % inventory
            self.make_request('PUT', '/products/%s/skus/%s' % (product_id, sku_id), body=body, headers={"Content-Type":"application/xml"})

class VendHQConnector(StoreAPIConnector):
    def __init__(self, *args, **kwargs):
        super(VendHQConnector, self).__init__(*args, **kwargs)
        
    def num_products(self):
        return len(self.products())
        
    def get_product_list_from_json(self, json):
        products = []
        for product_json in json:
            products.append(self.product_from_json(product_json))
        
        return products
    
    def get_current_product(self, sku=None, product_id=None):
        if product_id is not None:
            product_response = self.make_request('GET', '/1.0/product/%s' % product_id)
            product = self.product_from_json(product_response)
            return product
    
    def products(self):
        if not self.cached_products:
            page = 1
            self.cached_products = []
            product_response = self.make_request('GET', '/products')
            if 'pagination' in product_response:
                total_pages = int(product_response['pagination']['pages'])
                for page_num in range(1, total_pages+1):
                    product_response = self.make_request('GET', '/products/page/%d' % page_num)
                    product_list_json = product_response['products']
                    self.cached_products.extend(self.get_product_list_from_json(product_list_json))
            else:
                self.cached_products = self.get_product_list_from_json(product_response['products'])
            
        return self.cached_products
        
    def product_from_json(self, json, outlet_id="b3680bc4-b23a-11e0-a22b-4040dde94e2e"):
        inventory_count = -1
        for outlet in json['inventory']:
            if outlet['outlet_id'] == outlet_id:
                inventory_count = float(outlet['count'])
        return ProductInventorySnapshot(store_id=json['id'],
                                        name=json['name'], 
                                        sku=json['sku'], 
                                        inventory_count=inventory_count,
                                        vhq_product_id=json['id'],
                                        store="R")
    
    def update_product_inventory(self, inventory, product_id=None, outlet_id="b3680bc4-b23a-11e0-a22b-4040dde94e2e"):
        if product_id:
            product_data = self.make_request('GET', '/1.0/product/%s' % product_id)
            print inventory
            product_data['inventory'][0]['count'] = float(inventory)
            product_data['inventory'][0]['outlet_name'] = "Main Outlet"

            self.make_request('POST', '/products', body=json.dumps(product_data), headers={"Content-Type":"application/json"})
             
def standard_vhq_connector():
    return VendHQConnector("tjsavage@sse.stanford.edu", "6YK254YYWH", "https://stanfordstore.vendhq.com/api")
    
def standard_bc_connector():
    return BigCommerceConnector("tjsavage", "38775c05bcc4041ea4544cb1b6ba60c7","https://store-0ef21.mybigcommerce.com/api/v2")
