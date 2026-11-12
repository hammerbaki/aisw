# -*- coding: utf-8 -*-
"""검증 없는 도구에 검증과 폴백을 붙인 판 (week07 실습 2의 예비. cp 예비/calc_tool_bare.py . 로 가져온다).

사용법:
    .venv/bin/python calc_tool_bare.py "가격이 -50000원인 상품의 부가세 포함 가격은?"

calc_tool.py에서 입력 검증과 오류 처리를 뺀 판입니다.
방어가 없는 도구가 어떻게 되는지 관찰한 뒤, 실습에서 검증과 폴백을 직접 붙입니다.
검증을 붙이면 tests/test_calc_tool_bare.py의 테스트 3개가 통과합니다(시작은 1개만 통과).

전제: 환경변수 ANTHROPIC_API_KEY. COURSE_MODEL은 없으면 기본값을 씁니다.
"""
import os
import sys

import anthropic

MODEL = os.environ.get("COURSE_MODEL", "claude-haiku-4-5-20251001")
MAX_ROUNDS = 5  # 도구 호출 반복의 상한 (무한 반복을 막는다)

_client = None


def get_client():
    """API 클라이언트를 처음 쓸 때 만든다(키는 환경변수 ANTHROPIC_API_KEY에서 읽는다)."""
    global _client
    if _client is None:
        _client = anthropic.Anthropic()
    return _client


# 도구 정의: 이름(영문), 설명, 입력 스키마. 모델은 이 정의만 보고 호출 여부를 판단한다.
VAT_TOOL = {
    "name": "vat_calc",
    "description": "공급가액(원)을 받아 부가세 10%와 합계 금액을 계산한다. "
                   "금액 계산이 필요한 질문에 사용한다. "
                   "부가세 제도나 세법을 설명하는 질문에는 사용하지 않는다.",
    "input_schema": {
        "type": "object",
        "properties": {
            "amount": {"type": "number", "description": "공급가액(원, 부가세 제외 금액)"}
        },
        "required": ["amount"],
    },
}


def run_tool(name, args):
    """도구 실행부. 실습 2에서 검증과 폴백을 붙인 판이다.

    모델이 만든 인자는 신뢰하지 않는 입력으로 취급하여 검증한다.
    실행 오류는 프로그램 중단 대신 문자열로 돌려주어 모델이 대처하게 한다.
    """
    if name == "vat_calc":
        try:
            amount = float(args.get("amount", None))
        except (TypeError, ValueError):
            return "오류: amount는 숫자여야 합니다"
        if amount < 0:
            return "오류: 금액은 0 이상이어야 합니다"
        vat = round(amount * 0.1)
        return f"공급가액 {amount:,.0f}원, 부가세 {vat:,}원, 합계 {amount + vat:,.0f}원"
    return f"오류: 알 수 없는 도구 {name}"


def ask(question):
    """도구 호출 사이클을 단계별로 출력하며 질문 1건을 처리한다.

    한 응답의 tool_use 블록을 모두 실행해 tool_result를 같은 개수만큼 돌려보낸다. 반복은 MAX_ROUNDS까지.
    """
    messages = [{"role": "user", "content": question}]
    response = get_client().messages.create(
        model=MODEL, max_tokens=500, tools=[VAT_TOOL], messages=messages
    )
    print(f"[1차 응답] stop_reason = {response.stop_reason}")

    rounds = 0
    while response.stop_reason == "tool_use" and rounds < MAX_ROUNDS:
        rounds += 1
        results = []
        for block in response.content:
            if block.type != "tool_use":
                continue
            print(f"[호출 결정] 모델이 요청한 도구 = {block.name}, 인자 = {block.input}")
            result = run_tool(block.name, block.input)
            print(f"[코드가 실행] 결과 = {result}")
            results.append({"type": "tool_result", "tool_use_id": block.id, "content": result})
        messages.append({"role": "assistant", "content": response.content})
        messages.append({"role": "user", "content": results})
        response = get_client().messages.create(
            model=MODEL, max_tokens=500, tools=[VAT_TOOL], messages=messages
        )
        print(f"[결과 재주입 후 응답] stop_reason = {response.stop_reason}")

    final = "".join(b.text for b in response.content if b.type == "text")
    print(f"\n[최종 답변] {final}")


def main():
    if len(sys.argv) != 2:
        print(__doc__)
        sys.exit(1)
    ask(sys.argv[1])


if __name__ == "__main__":
    main()
