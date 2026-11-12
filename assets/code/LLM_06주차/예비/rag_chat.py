# -*- coding: utf-8 -*-
"""RAG 챗봇 완성본 (week06 실습 4의 예비 · build_prompt가 채워진 판. 끝내 안 되면 cp 예비/rag_chat.py . 로 가져온다).

사용법:
    .venv/bin/python rag_chat.py ask "질문"     # 단건 질의응답 (검색 → 증강 → 생성)
    .venv/bin/python rag_chat.py chat           # 대화형 모드 (이력 유지, 종료는 빈 입력)

전제:
    - 실습 3에서 완성한 embed_search.py가 이 파일과 같은 폴더에 있고,
      index.json이 명령을 실행하는 폴더에 있어야 합니다.
      (embed_search.py가 미완성이면 예비_검색기/의 완성본을 복사합니다)
    - 두 번째 문서 챗봇: 사내규정/ 폴더에서 ../.venv/bin/python ../rag_chat.py ask "질문" 처럼 실행하면
      사내규정/index.json을 읽습니다. embed_search.py는 이 파일 옆의 것을 자동으로 찾습니다.
    - 환경변수 ANTHROPIC_API_KEY, COURSE_MODEL (실습 1과 동일)
    - 검색기 쪽 환경변수 EMBED_MODEL. 자세한 것은 embed_search.py 첫머리를 봅니다.
    - THRESHOLD는 아래 상수를 고치거나 환경변수 THRESHOLD로 바꿉니다(예비 임베딩이면 값의 눈금이 다릅니다).

build_prompt는 실습 4에서 완성합니다. 이 판은 build_prompt가 채워져 있습니다.
build_prompt 완성 전에는 ask, chat이 NotImplementedError로 멈춥니다.
trim_history는 비어 있어 전체 이력을 그대로 반환합니다(이번 실습에서 채우지 않아 테스트 1개는 실패로 남습니다).
"""
import json
import os
import sys

import anthropic

import embed_search
from embed_search import load_index, search

MODEL = os.environ.get("COURSE_MODEL", "claude-haiku-4-5-20251001")
THRESHOLD = float(os.environ.get("THRESHOLD", "0.5"))  # 유사도 필터의 기준값: 1위 유사도가 이보다 낮으면 답하지 않는다 (실습에서 조정)
MAX_TURNS = 4  # 이력에 원문으로 유지할 최근 왕복 수 (실습에서 사용)
FALLBACK_THRESHOLD = 0.2  # 예비 임베딩일 때의 기준값 (눈금이 달라 THRESHOLD보다 낮게 둔다)
SESSION_FILE = "세션.json"

_client = None


def get_client():
    """API 클라이언트를 처음 쓸 때 만든다(키는 환경변수 ANTHROPIC_API_KEY에서 읽는다)."""
    global _client
    if _client is None:
        _client = anthropic.Anthropic()
    return _client


def build_prompt(question, chunks):
    """검색된 청크를 근거로 붙인 증강 프롬프트 문자열을 만든다. [완성본 · 예비]

    구성: ① 각 청크를 <근거1>...</근거1> 태그로 감싸 나열
          ② <질문> 태그로 질문 추가
          ③ 지시: 위 근거만 사용해 답하고, 근거에 없으면
             "주어진 자료에서 찾을 수 없습니다"라고 답하며,
             답 끝에 사용한 근거 번호를 표기하라.
    """
    parts = []
    for i, text in enumerate(chunks, start=1):
        parts.append(f"<근거{i}>\n{text}\n</근거{i}>")
    parts.append(f"<질문>\n{question}\n</질문>")
    parts.append(
        "위 근거만 사용해 답하라. 근거에 없으면 "
        '"주어진 자료에서 찾을 수 없습니다"라고 답하라. '
        "답 끝에 사용한 근거 번호를 표기하라.")
    return "\n\n".join(parts)


def trim_history(history):
    """대화 이력에서 최근 MAX_TURNS 왕복만 남긴다. [발전 · 이번 실습에서는 채우지 않음]

    history는 {"role": "user"|"assistant", "content": ...} 목록이다.
    한 왕복은 user와 assistant 각 1건이므로, 최근 MAX_TURNS * 2개만 남기면 된다.
    완성 전까지는 임시로 전체 이력을 그대로 반환한다(자르지 않음).
    """
    return history  # 발전: 최근 MAX_TURNS 왕복만 남기도록 수정하십시오


def retrieve(question):
    """검색을 수행하고 (1위 유사도, 청크 텍스트 목록)을 반환한다. (완성되어 있음)"""
    results = search(question, load_index())
    top_score = results[0][0] if results else 0.0
    chunks = [text for _, text in results]
    return top_score, chunks


def generate(messages):
    """Claude API로 응답을 생성한다. (완성되어 있음)"""
    response = get_client().messages.create(
        model=MODEL,
        max_tokens=500,
        system="너는 주어진 자료를 근거로 답하는 안내 챗봇이다. 존댓말로 간결하게 답한다.",
        messages=messages,
    )
    return response.content[0].text


def ask(question, history=None):
    """질문 1건을 처리한다: 검색 → 유사도 필터 판정 → 증강 → 생성. (완성되어 있음)"""
    top_score, chunks = retrieve(question)
    threshold = THRESHOLD
    if embed_search.EMBED_BACKEND == "fallback" and "THRESHOLD" not in os.environ:
        threshold = min(THRESHOLD, FALLBACK_THRESHOLD)  # 예비 경로: 눈금이 달라 기준값을 낮춘다
    if top_score < threshold:
        return f"주어진 자료에서 찾을 수 없습니다. (1위 유사도 {top_score:.4f} < 필터 기준값 {threshold})"
    augmented = build_prompt(question, chunks)
    messages = list(history or []) + [{"role": "user", "content": augmented}]
    return generate(messages)


def chat():
    """대화형 모드: 이력을 유지하며 질의응답을 반복한다. (완성되어 있음)"""
    history = load_session()
    if history:
        print(f"(이전 세션 이어하기: {len(history) // 2}왕복 로드됨)")
    print("질문을 입력하십시오. 빈 입력이면 저장하고 종료합니다.\n")
    while True:
        try:
            question = input("질문> ").strip()
        except EOFError:  # Ctrl+D
            question = ""
        if not question:
            save_session(history)
            print(f"세션을 {SESSION_FILE}에 저장했습니다.")
            break
        reply = ask(question, history=trim_history(history))
        print(f"\n{reply}\n")
        # 이력에는 증강 전의 원래 질문만 저장한다 (근거 반복 저장은 컨텍스트 낭비)
        history.append({"role": "user", "content": question})
        history.append({"role": "assistant", "content": reply})


def save_session(history):
    with open(SESSION_FILE, "w", encoding="utf-8") as f:
        json.dump(history, f, ensure_ascii=False, indent=2)


def load_session():
    if not os.path.exists(SESSION_FILE):
        return []
    with open(SESSION_FILE, encoding="utf-8") as f:
        return json.load(f)


def main():
    if len(sys.argv) >= 3 and sys.argv[1] == "ask":
        print(ask(sys.argv[2]))
    elif len(sys.argv) == 2 and sys.argv[1] == "chat":
        chat()
    else:
        print(__doc__)
        sys.exit(1)


if __name__ == "__main__":
    main()
