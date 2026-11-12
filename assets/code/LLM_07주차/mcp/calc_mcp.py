# -*- coding: utf-8 -*-
"""부가세 계산 도구의 MCP 서버판 (week07 실습 4용, 완성되어 있음).

실습 2의 vat_calc를 FastMCP로 포장한 것입니다.
같은 함수가 우리 코드 전용 도구에서, 어떤 AI에든 꽂을 수 있는 표준 부품이 됩니다.

전제: fastmcp 패키지 (실습 1에서 requirements.txt로 .venv에 설치됨, 파이썬 3.10 이상)

Claude Code에 연결 (week07 폴더에서):
    claude mcp add vat-calc -- ~/week07/.venv/bin/python ~/week07/mcp/calc_mcp.py

연결 확인은 Claude Code 대화창에서 /mcp, 해제는 claude mcp remove vat-calc

함수 동작만 먼저 확인하려면 (mcp 폴더에서):
    ../.venv/bin/python -c "from calc_mcp import vat_calc; print(vat_calc(1000000))"
"""
try:
    from fastmcp import FastMCP
except ImportError:          # 직접 호출 확인은 fastmcp 없이도 되게 둔다
    FastMCP = None

mcp = FastMCP("vat-calc") if FastMCP else None


def vat_calc(amount: float) -> str:
    """공급가액(원)을 받아 부가세 10%와 합계 금액을 계산한다. 금액 계산이 필요한 질문에 사용한다."""
    # 인자 검증은 도구 사용 실습과 같은 원칙: 모델이 만든 인자를 신뢰하지 않는다.
    try:
        amount = float(amount)
    except (TypeError, ValueError):
        return "오류: amount는 숫자여야 합니다"
    if amount < 0:
        return "오류: 금액은 0 이상이어야 합니다"
    vat = round(amount * 0.1)
    return f"공급가액 {amount:,.0f}원, 부가세 {vat:,}원, 합계 {amount + vat:,.0f}원"


# 명시 등록: 어떤 함수를 도구로 내놓는지 한 줄로 드러난다(@mcp.tool 데코레이터와 등록 결과는 같다).
if mcp is not None:
    mcp.add_tool(vat_calc)


if __name__ == "__main__":
    if mcp is None:
        raise SystemExit("fastmcp가 설치되어 있지 않습니다. .venv/bin/python -m pip install -r requirements.txt 뒤 .venv/bin/python으로 실행합니다")
    mcp.run()
