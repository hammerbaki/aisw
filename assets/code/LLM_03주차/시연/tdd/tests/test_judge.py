"""숫자 맞히기 게임의 판정 규칙.

추측이 정답보다 작으면 "더 큰 수", 크면 "더 작은 수", 같으면 "정답".
"""
import pytest
from judge import judge


def test_correct():
    assert judge(50, 50) == "정답"


def test_guess_too_low():
    assert judge(30, 50) == "더 큰 수"


def test_guess_too_high():
    assert judge(80, 50) == "더 작은 수"


def test_boundary_low():
    assert judge(1, 1) == "정답"


def test_boundary_high():
    assert judge(100, 100) == "정답"
