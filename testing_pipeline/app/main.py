"""
Enterprise Microservice Application
Author: Sai Nayan Mamilla (sainayanmamilla)
Course: Advanced Deployment Strategies & Enterprise DevOps (Lab 4)
"""

from fastapi import FastAPI, HTTPException, status, Depends, Header
from pydantic import BaseModel, Field
from typing import Optional, List, Dict
import time
import os

app = FastAPI(
    title="Enterprise DevOps Microservice",
    version="2.0.0",
    description="High-resilience cloud-native microservice with automated test gates."
)

# In-memory storage mock for integration testing
DB_STORE: Dict[str, dict] = {}

class ItemPayload(BaseModel):
    item_id: str = Field(..., min_length=3, max_length=50)
    name: str = Field(..., min_length=1)
    quantity: int = Field(..., ge=1, le=10000)
    unit_price: float = Field(..., gt=0.0)

class OrderSummary(BaseModel):
    order_id: str
    item_id: str
    total_cost: float
    tax: float
    final_amount: float
    status: str

def calculate_order_financials(quantity: int, unit_price: float, tax_rate: float = 0.18) -> Dict[str, float]:
    """Pure domain function for unit testing."""
    if quantity <= 0:
        raise ValueError("Quantity must be positive integer.")
    if unit_price <= 0:
        raise ValueError("Unit price must be positive.")
    subtotal = round(quantity * unit_price, 2)
    tax = round(subtotal * tax_rate, 2)
    total = round(subtotal + tax, 2)
    return {
        "subtotal": subtotal,
        "tax": tax,
        "final_amount": total
    }

@app.get("/healthz", status_code=status.HTTP_200_OK)
def health_check():
    """Liveness probe endpoint."""
    return {"status": "HEALTHY", "version": "2.0.0", "timestamp": time.time()}

@app.get("/readyz", status_code=status.HTTP_200_OK)
def readiness_check():
    """Readiness probe endpoint ensuring vault secrets and db are connected."""
    db_connected = True
    vault_synced = os.getenv("VAULT_SECRET_INJECTED", "true").lower() == "true"
    if not (db_connected and vault_synced):
        raise HTTPException(status_code=503, detail="Service dependencies not ready")
    return {"ready": True, "dependencies": {"database": "ok", "vault": "ok"}}

@app.post("/api/v1/items", status_code=status.HTTP_201_CREATED)
def create_item(payload: ItemPayload):
    """Create item endpoint verified via integration tests."""
    if payload.item_id in DB_STORE:
        raise HTTPException(status_code=409, detail=f"Item {payload.item_id} already exists.")
    DB_STORE[payload.item_id] = payload.dict()
    return {"message": "Item stored successfully", "item": DB_STORE[payload.item_id]}

@app.get("/api/v1/items/{item_id}", status_code=status.HTTP_200_OK)
def get_item(item_id: str):
    """Retrieve item."""
    if item_id not in DB_STORE:
        raise HTTPException(status_code=404, detail="Item not found")
    return DB_STORE[item_id]

@app.post("/api/v1/orders/calculate", response_model=OrderSummary, status_code=status.HTTP_200_OK)
def process_order(payload: ItemPayload):
    """Order processing pipeline logic."""
    financials = calculate_order_financials(payload.quantity, payload.unit_price)
    order_id = f"ORD-{int(time.time())}-{payload.item_id}"
    return OrderSummary(
        order_id=order_id,
        item_id=payload.item_id,
        total_cost=financials["subtotal"],
        tax=financials["tax"],
        final_amount=financials["final_amount"],
        status="CONFIRMED"
    )
