# -*- coding: utf-8 -*-
"""주문 관리 샘플 모듈 (CLAUDE.md 실습용)."""

_ORDERS = {}
_STOCK = {"노트북": 5, "마우스": 20, "키보드": 0}


def create_order(order_id, product, quantity):
    """주문을 생성한다. 재고가 부족하면 ValueError를 던진다."""
    if quantity <= 0:
        raise ValueError("수량은 1 이상이어야 한다")
    stock = _STOCK.get(product, 0)
    if quantity > stock:
        raise ValueError("재고 부족")
    _STOCK[product] = stock - quantity
    _ORDERS[order_id] = {"product": product, "quantity": quantity, "status": "접수"}
    return _ORDERS[order_id]


def get_order(order_id):
    """주문을 조회한다."""
    if order_id not in _ORDERS:
        raise KeyError("존재하지 않는 주문")
    return _ORDERS[order_id]


def reset():
    """테스트용 초기화."""
    _ORDERS.clear()
    _STOCK.clear()
    _STOCK.update({"노트북": 5, "마우스": 20, "키보드": 0})
