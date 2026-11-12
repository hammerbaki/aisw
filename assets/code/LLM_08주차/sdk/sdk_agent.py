# -*- coding: utf-8 -*-
"""같은 에이전트의 Claude Agent SDK 재구현판 (week10 실습용, 완성되어 있음).

react_agent.py에서 직접 만들던 것(서식 프롬프트, 파싱, 루프, 재주입, 단계 상한)을
SDK가 대신합니다. 우리가 쓰는 코드는 도구 정의와 질문뿐입니다.
Claude Code를 움직이는 것과 같은 인프라입니다.

사용법:
    python sdk_agent.py "100만원 노트북, 부가세 포함가에서 20% 할인하면?"

전제: pip install claude-agent-sdk (ASO Lab에는 설치되어 있음),
      Claude Code 설치 환경, 환경변수 ANTHROPIC_API_KEY, COURSE_MODEL
"""
import asyncio
import os
import sys

from claude_agent_sdk import (
    ClaudeAgentOptions,
    create_sdk_mcp_server,
    query,
    tool,
)


# ---------- 도구: react_agent.py와 같은 계산, 같은 검증 원칙 ----------

@tool("vat_calc", "공급가액(원)을 받아 부가세 10%와 합계 금액을 계산한다.", {"amount": float})
async def vat_calc(args):
    try:
        amount = float(args.get("amount"))
    except (TypeError, ValueError):
        return {"content": [{"type": "text", "text": "오류: amount는 숫자여야 합니다"}]}
    if amount < 0:
        return {"content": [{"type": "text", "text": "오류: 금액은 0 이상이어야 합니다"}]}
    vat = round(amount * 0.1)
    text = f"공급가액 {amount:,.0f}원, 부가세 {vat:,}원, 합계 {amount + vat:,.0f}원"
    return {"content": [{"type": "text", "text": text}]}


@tool("discount_calc", "원가(원)와 할인율(%)을 받아 할인 적용가를 계산한다.", {"price": float, "rate": float})
async def discount_calc(args):
    try:
        price, rate = float(args.get("price")), float(args.get("rate"))
    except (TypeError, ValueError):
        return {"content": [{"type": "text", "text": "오류: price와 rate는 숫자여야 합니다"}]}
    if not (0 <= rate <= 100):
        return {"content": [{"type": "text", "text": "오류: 할인율은 0~100 사이여야 합니다"}]}
    sale = round(price * (1 - rate / 100))
    text = f"원가 {price:,.0f}원, {rate:g}% 할인 적용가 {sale:,}원"
    return {"content": [{"type": "text", "text": text}]}


async def main(question):
    calc = create_sdk_mcp_server(name="calc", tools=[vat_calc, discount_calc])
    options = ClaudeAgentOptions(
        model=os.environ.get("COURSE_MODEL", "claude-haiku-4-5"),
        mcp_servers={"calc": calc},
        allowed_tools=["mcp__calc__vat_calc", "mcp__calc__discount_calc"],
        system_prompt="너는 계산 상담원이다. 계산은 직접 하지 말고 반드시 도구로 한다. 한국어로 답한다.",
        max_turns=6,  # react_agent.py의 MAX_STEPS에 해당하는 안전장치
    )
    async for message in query(prompt=question, options=options):
        # 메시지 종류를 그대로 출력해 SDK 루프의 진행(도구 호출·결과·최종 답)을 관찰한다
        print(f"[{type(message).__name__}] {message}")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print(__doc__)
        sys.exit(1)
    asyncio.run(main(sys.argv[1]))
