# -*- coding: utf-8 -*-
"""도구 챗봇 고정 테스트. 고치지 않는다(TDD에서 동결한 테스트와 같은 역할).

faq_tool_chat.py의 handle_tool_use를 확인한다. API와 임베딩 서버 없이 돈다.
검색은 정해 둔 결과를 돌려주는 가짜(Mock)로 바꿔 끼운다. 셋 다 실습 1에서 통과한다.
"""
import faq_tool_chat as bot

FOUND = [(0.82, "## 제24조 (재택근무)\n부서장 승인 후 신청"),
         (0.51, "## 제7조 (유연근무)"),
         (0.40, "## 제3조 (근무시간)")]


def fake_search(monkeypatch, results):
    monkeypatch.setattr(bot, "load_index", lambda: [])
    monkeypatch.setattr(bot, "search", lambda query, index: results)


def test_모르는_도구_이름은_오류_문자열로_돌려준다(monkeypatch):
    fake_search(monkeypatch, FOUND)
    assert bot.handle_tool_use("calc", {"query": "재택근무"}) == "오류: 알 수 없는 도구 calc"


def test_빈_query는_오류_문자열로_돌려준다(monkeypatch):
    fake_search(monkeypatch, FOUND)
    assert bot.handle_tool_use("faq_search", {"query": "   "}) == "오류: query가 비어 있습니다"
    assert bot.handle_tool_use("faq_search", {}) == "오류: query가 비어 있습니다"


def test_검색_결과를_유사도_줄로_이어_돌려준다(monkeypatch):
    fake_search(monkeypatch, FOUND)
    out = bot.handle_tool_use("faq_search", {"query": "재택근무 신청"})
    assert out.startswith("유사도 0.82: ## 제24조 (재택근무)"), "첫 줄은 1위 결과여야 합니다"
    assert "\n유사도 0.51: ## 제7조 (유연근무)" in out and "\n유사도 0.40: ## 제3조 (근무시간)" in out
    assert out.index("0.82") < out.index("0.51") < out.index("0.40")
