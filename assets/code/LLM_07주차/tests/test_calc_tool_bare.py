# -*- coding: utf-8 -*-
"""검증 · 폴백 고정 테스트. 고치지 않는다(TDD에서 동결한 테스트와 같은 역할).

calc_tool_bare.py의 run_tool을 모델 없이 직접 호출해 확인한다. API를 부르지 않는다.
시작은 첫 테스트만 통과하고, 실습 2에서 검증을 붙이면 셋 다 통과한다.
"""
from calc_tool_bare import run_tool


def test_정상_금액은_부가세와_합계를_계산한다():
    assert run_tool("vat_calc", {"amount": 1000000}) == "공급가액 1,000,000원, 부가세 100,000원, 합계 1,100,000원"


def test_숫자가_아닌_인자는_죽지_않고_오류_문자열로_돌려준다():
    assert run_tool("vat_calc", {"amount": "미정"}) == "오류: amount는 숫자여야 합니다"
    assert run_tool("vat_calc", {}) == "오류: amount는 숫자여야 합니다"


def test_음수_금액은_오류_문자열로_돌려준다():
    assert run_tool("vat_calc", {"amount": -50000}) == "오류: 금액은 0 이상이어야 합니다"
