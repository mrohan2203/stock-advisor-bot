# tests/test_tools.py
import unittest
from tools.stock_data import get_stock_stats

class TestStockTools(unittest.TestCase):
    def test_valid_ticker(self):
        result = get_stock_stats("AAPL")
        self.assertEqual(result["symbol"], "AAPL")
        self.assertIn("current_price", result)

    def test_invalid_ticker(self):
        result = get_stock_stats("INVALID_TICKER_123")
        self.assertIn("error", result)

if __name__ == "__main__":
    unittest.main()