# -*- coding: utf-8 -*-
import pytest

from app.orders import create_order, get_order, reset


@pytest.fixture(autouse=True)
def _reset():
    reset()


def test_주문_생성():
    order = create_order("A-1", "노트북", 1)
    assert order["status"] == "접수"


def test_재고_부족이면_실패():
    with pytest.raises(ValueError):
        create_order("A-2", "키보드", 1)


def test_없는_주문_조회는_실패():
    with pytest.raises(KeyError):
        get_order("없는번호")
