# -*- coding: utf-8 -*-
"""RAG 챗봇 고정 테스트. 고치지 않는다(TDD에서 동결한 테스트와 같은 역할).

rag_chat.py의 build_prompt와 trim_history를 확인한다. API를 부르지 않는다.
지시 문장은 내 말로 고쳐도 되지만, 거절 문구 「주어진 자료에서 찾을 수 없습니다」와
「근거」 · 「번호」라는 말은 지시 안에 남아 있어야 한다.
"""
import rag_chat

QUESTION = "재택근무는 어떻게 신청하나요"
CHUNKS = ["## 제24조 (재택근무)\n부서장 승인 후 신청", "## 제3조 (근무시간)\n오전 9시부터"]


def test_근거는_번호_태그로_질문은_질문_태그로_감싼다():
    prompt = rag_chat.build_prompt(QUESTION, CHUNKS)
    for tag in ("<근거1>", "</근거1>", "<근거2>", "</근거2>", "<질문>", "</질문>"):
        assert tag in prompt, f"{tag} 태그가 없습니다"
    assert CHUNKS[0] in prompt and QUESTION in prompt
    assert prompt.index("</근거2>") < prompt.index("<질문>"), "근거 다음에 질문이 와야 합니다"


def test_trim_history는_최근_MAX_TURNS_왕복만_남긴다():
    history = []
    for i in range(10):
        history.append({"role": "user", "content": f"질문{i}"})
        history.append({"role": "assistant", "content": f"답{i}"})
    trimmed = rag_chat.trim_history(history)
    assert len(trimmed) == rag_chat.MAX_TURNS * 2
    assert trimmed[0] == {"role": "user", "content": f"질문{10 - rag_chat.MAX_TURNS}"}
    assert trimmed[-1] == {"role": "assistant", "content": "답9"}
    assert rag_chat.trim_history(history[:2]) == history[:2], "짧은 이력은 그대로 둡니다"


def test_지시에는_근거만_없으면_없다_번호_표기가_들어간다():
    prompt = rag_chat.build_prompt(QUESTION, CHUNKS)
    instruction = prompt.split("</질문>", 1)[1]
    assert "근거" in instruction, "근거만 사용하라는 지시가 없습니다"
    assert "주어진 자료에서 찾을 수 없습니다" in instruction, "없을 때의 거절 문구가 없습니다"
    assert "번호" in instruction, "근거 번호를 표기하라는 지시가 없습니다"
