"""3주차 실습 2: 이 테스트를 통과하는 judge.py를 구현한다.

숫자 맞히기 게임의 판정 규칙: 추측이 정답보다 작으면 "더 큰 수",
크면 "더 작은 수", 같으면 "정답".
이 파일은 수정하지 않는다.
사람이 테스트를 정의하고 AI가 구현한다.
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
