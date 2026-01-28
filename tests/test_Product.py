from src.core.product import Product
import unittest

class TestProduct(unittest.TestCase):
    def test_initialization(self):
        product = Product(id=1, name="Laptop", price=1000.0, stock=10, iva=0.19)
        self.assertEqual(product.id, 1)
        self.assertEqual(product.name, "Laptop")
        self.assertEqual(product.price, 1000.0)
        self.assertEqual(product.stock, 10)
        self.assertEqual(product.iva, 0.19)

    def test_negative_price_initialization(self):
        with self.assertRaises(ValueError):
            Product(id=2, name="Phone", price=-500.0)

    def test_negative_stock_initialization(self):
        with self.assertRaises(ValueError):
            Product(id=3, name="Tablet", price=300.0, stock=-5)

    def test_calculate_total_price(self):
        product = Product(id=4, name="Monitor", price=200.0, iva=0.15)
        total_price = product.calculate_total_price()
        self.assertAlmostEqual(total_price, 230.0)

    def test_update_stock_increase(self):
        product = Product(id=5, name="Keyboard", price=50.0, stock=5)
        product.update_stock(10)
        self.assertEqual(product.stock, 15)

    def test_update_stock_decrease(self):
        product = Product(id=6, name="Mouse", price=25.0, stock=10)
        product.update_stock(-4)
        self.assertEqual(product.stock, 6)

    def test_update_stock_insufficient(self):
        product = Product(id=7, name="Headphones", price=80.0, stock=3)
        with self.assertRaises(ValueError):
            product.update_stock(-5)