"""
This file demonstrates writing tests using the unittest module. These will pass
when you run "manage.py test".

Replace this with more appropriate tests for your application.
"""
from inventory_sync.api_connectors import BigCommerceConnector, VendHQConnector, standard_vhq_connector, standard_bc_connector

from django.utils import unittest
from django.test import TestCase


class TestBCConnector(TestCase):
    def setUp(self):
        self.bc = standard_bc_connector()
        self.products = self.bc.products()
        
    def test_get_products(self):
        print self.products
        self.assertTrue(len(self.products) > 10)

    def test_has_specific_sku(self):
        small_classic_tee_sku = 1020120117
        found_flag = False
        for p in self.products:
            if p.sku == small_classic_tee_sku:
                found_flag = True
        self.assertTrue(found_flag)
    
    def test_options(self):
        self.bc.load_options()
        print self.bc.cached_options
    
    def test_get_current_product(self):
        product_id = "212"
        sku_id = "1170"
        product = self.bc.get_current_product(product_id=product_id, sku_id=sku_id)
        self.assertIsNotNone(product)
        print product
        
    def test_update_product(self):
        product_id = "212"
        sku_id = "1170"
        product = self.bc.get_current_product(product_id=product_id, sku_id=sku_id)
        self.assertIsNotNone(product)
        
        old_inventory_count = product.inventory_count
        self.bc.update_product_inventory(old_inventory_count + 1, product_id=product_id, sku_id=sku_id)
        new_product = self.bc.get_current_product(product_id=product_id, sku_id=sku_id)
        self.assertEquals(new_product.inventory_count, old_inventory_count + 1)
        
        self.bc.update_product_inventory(old_inventory_count, product_id=product_id, sku_id=sku_id)
        new_product = self.bc.get_current_product(product_id=product_id, sku_id=sku_id)
        self.assertEquals(new_product.inventory_count, old_inventory_count)
        
class TestVHQConnector(TestCase):
    def setUp(self):
        self.vhq = standard_vhq_connector()
        self.products = self.vhq.products()
        
    def test_get_products(self):
        print self.products
        self.assertTrue(len(self.products) > 10)
    
    def test_get_current_product(self):
        vhq_product_id = "a4dbcd10-12f6-11e2-b195-4040782fde00"
        product = self.vhq.get_current_product(product_id=vhq_product_id)
        self.assertIsNotNone(product)
        print product

    def test_update_product_inventory(self):
        product_id = "a4dbcd10-12f6-11e2-b195-4040782fde00"
        product = self.vhq.get_current_product(product_id=product_id)
        self.assertIsNotNone(product)
        
        old_inventory_count = product.inventory_count
        
        self.vhq.update_product_inventory(old_inventory_count + 1, product_id=product_id)
        new_product = self.vhq.get_current_product(product_id=product_id)
        self.assertEquals(new_product.inventory_count, old_inventory_count + 1)
        
        self.vhq.update_product_inventory(old_inventory_count, product_id=product_id)
        new_product = self.vhq.get_current_product(product_id=product_id)
        self.assertEquals(new_product.inventory_count, old_inventory_count)
       