# -*- coding: utf-8 -*-
"""검색기를 도구로 등록한 챗봇 완성본 (week07 실습 1의 예비. 끝내 안 되면 cp 예비/faq_tool_chat.py . 로 가져온다).

사용법:
    .venv/bin/python faq_tool_chat.py "API 키를 잃어버렸어요"   # 검색이 필요한 질문
    .venv/bin/python faq_tool_chat.py "안녕하세요"               # 검색이 필요 없는 질문

RAG 챗봇(rag_chat.py)은 코드가 매 질문마다 무조건 검색을 실행했습니다.
이 챗봇은 검색기를 도구로 등록만 해 두고, 부를지 말지를 모델이 판단합니다.

전제:
    - 같은 폴더의 embed_search.py(완성본)를 쓰고, index.json은 명령을 실행하는 폴더에서 읽습니다.
      색인은 실습 1의 1단계에서 만듭니다: .venv/bin/python embed_search.py index 학과FAQ.md
    - 사내규정 도구: 사내규정/ 폴더에서 ../.venv/bin/python ../faq_tool_chat.py "질문" 처럼 실행하면
      사내규정/index.json을 읽습니다. embed_search.py는 이 파일 옆의 것을 자동으로 찾습니다.
    - 환경변수 ANTHROPIC_API_KEY. COURSE_MODEL · EMBED_MODEL은 없으면 기본값을 씁니다.

description과 handle_tool_use가 채워진 판입니다. tests/test_faq_tool_chat.py 3개가 통과합니다.
실습 1의 4단계(빈약한 description)를 하려면 description을 지우고 시작합니다.
"""
import os
import sys

import anthropic

from embed_search import load_index, search

MODEL = os.environ.get("COURSE_MODEL", "claude-haiku-4-5-20251001")
MAX_ROUNDS = 5  # 도구 호출 반복의 상한 (무한 반복을 막는다)
SYSTEM = ("너는 주어진 자료를 검색해 답하는 안내 챗봇이다. 존댓말로 간결하게 답한다. "
          "검색 결과에 없는 내용은 지어내지 않는다.")

_client = None


def get_client():
    """API 클라이언트를 처음 쓸 때 만든다(키는 환경변수 ANTHROPIC_API_KEY에서 읽는다)."""
    global _client
    if _client is None:
        _client = anthropic.Anthropic()
    return _client


# 도구 정의. description은 실습에서 완성한다.
# 무엇을 하는 도구인지, 어떤 질문에 사용해야 하는지를 모델이 이 문장만 보고 판단한다.
FAQ_TOOL = {
    "name": "faq_search",
    "description": (
        "학과 FAQ와 사내 복무 규정 문서를 의미 검색한다. "
        "학과 생활과 근무 · 휴가 · 출장 질문에 사용한다. "
        "인사말이나 일반 상식 질문에는 사용하지 않는다."
    ),
    "input_schema": {
        "type": "object",
        "properties": {
            "query": {"type": "string", "description": "검색할 질문 문장"}
        },
        "required": ["query"],
    },
}


def handle_tool_use(name, args):
    """도구 호출 요청을 받아 검색을 실행하고 결과 문자열을 돌려준다. (완성본)"""
    if name != "faq_search":
        return f"오류: 알 수 없는 도구 {name}"
    query = args.get("query", "").strip()
    if not query:
        return "오류: query가 비어 있습니다"
    lines = [f"유사도 {score:.2f}: {text}"
             for score, text in search(query, load_index())]
    return "\n".join(lines)


def ask(question):
    """도구 사이클로 질문 1건을 처리한다. (완성되어 있음)

    한 응답에 tool_use 블록이 여럿이면(다중 호출) 모두 실행해 tool_result를 같은 개수만큼 돌려보내고,
    모델이 결과를 보고 다시 부르면(연쇄 호출) while이 받는다. 반복은 MAX_ROUNDS까지만 한다.
    """
    messages = [{"role": "user", "content": question}]
    response = get_client().messages.create(
        model=MODEL, max_tokens=500, system=SYSTEM, tools=[FAQ_TOOL], messages=messages
    )
    rounds = 0
    while response.stop_reason == "tool_use" and rounds < MAX_ROUNDS:
        rounds += 1
        results = []
        for block in response.content:
            if block.type != "tool_use":
                continue
            print(f"(도구 호출: {block.name}, 인자: {block.input})")
            results.append({"type": "tool_result", "tool_use_id": block.id,
                            "content": handle_tool_use(block.name, block.input)})
        messages.append({"role": "assistant", "content": response.content})
        messages.append({"role": "user", "content": results})
        response = get_client().messages.create(
            model=MODEL, max_tokens=500, system=SYSTEM, tools=[FAQ_TOOL], messages=messages
        )
    if rounds == 0:
        print("(도구 호출 없음)")
    if response.stop_reason == "tool_use":
        print(f"(도구 호출이 상한 {MAX_ROUNDS}회에 걸려 멈췄습니다)")
    return "".join(b.text for b in response.content if b.type == "text")


def main():
    if len(sys.argv) != 2:
        print(__doc__)
        sys.exit(1)
    print(ask(sys.argv[1]))


if __name__ == "__main__":
    main()
