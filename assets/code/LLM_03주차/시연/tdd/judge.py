# -*- coding: utf-8 -*-
"""숫자 맞히기 판정 규칙 (골격 tests/test_judge.py를 통과하는 구현 · 교수 시연용 완성본)."""


def judge(guess, answer):
    """추측이 정답보다 작으면 "더 큰 수", 크면 "더 작은 수", 같으면 "정답"."""
    if guess < answer:
        return "더 큰 수"
    if guess > answer:
        return "더 작은 수"
    return "정답"
