"""
Unit Test Suite - Pipeline Pre-deployment Gate
Candidate: Sai Nayan Mamilla (sainayanmamilla)
"""

import pytest
from app.main import calculate_order_financials

def test_financial_calculation_standard():
    res = calculate_order_financials(quantity=10, unit_price=100.0, tax_rate=0.18)
    assert res["subtotal"] == 1000.0
    assert res["tax"] == 180.0
    assert res["final_amount"] == 1180.0

def test_financial_calculation_fractional():
    res = calculate_order_financials(quantity=3, unit_price=49.99, tax_rate=0.05)
    assert res["subtotal"] == 149.97
    assert res["tax"] == 7.50
    assert res["final_amount"] == 157.47

def test_financial_calculation_zero_tax():
    res = calculate_order_financials(quantity=5, unit_price=20.0, tax_rate=0.0)
    assert res["subtotal"] == 100.0
    assert res["tax"] == 0.0
    assert res["final_amount"] == 100.0

def test_financial_calculation_negative_quantity_raises_value_error():
    with pytest.raises(ValueError, match="Quantity must be positive integer"):
        calculate_order_financials(quantity=-1, unit_price=50.0)

def test_financial_calculation_zero_quantity_raises_value_error():
    with pytest.raises(ValueError, match="Quantity must be positive integer"):
        calculate_order_financials(quantity=0, unit_price=50.0)

def test_financial_calculation_negative_price_raises_value_error():
    with pytest.raises(ValueError, match="Unit price must be positive"):
        calculate_order_financials(quantity=5, unit_price=-10.0)

def test_financial_calculation_rounding_boundary():
    res = calculate_order_financials(quantity=7, unit_price=14.2857, tax_rate=0.18)
    assert isinstance(res["final_amount"], float)
    assert round(res["final_amount"], 2) == res["final_amount"]
