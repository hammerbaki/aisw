# -*- coding: utf-8 -*-
"""MCP 포장 고정 테스트. 고치지 않는다(TDD에서 동결한 테스트와 같은 역할).

mcp/calc_mcp.py를 확인한다. API를 부르지 않는다.
둘째 테스트는 fastmcp의 메모리 안 연결(Client에 서버를 바로 넘기는 방식)로 MCP 규약대로 도구를 부른다.
"""
import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "mcp"))

import calc_mcp
from calc_tool import run_tool


def test_직접_호출은_실습_2의_검증판과_같은_답을_낸다():
    for amount in (1000000, -50000, "미정"):
        assert calc_mcp.vat_calc(amount) == run_tool("vat_calc", {"amount": amount})


def test_MCP_규약으로_불러도_같은_답을_낸다():
    assert calc_mcp.mcp is not None, "fastmcp가 설치되어 있지 않습니다(pip install -r requirements.txt)"
    from fastmcp import Client

    async def call():
        async with Client(calc_mcp.mcp) as client:
            tools = await client.list_tools()
            result = await client.call_tool("vat_calc", {"amount": 1000000})
            data = getattr(result, "data", None)
            return [t.name for t in tools], data if isinstance(data, str) else result.content[0].text

    names, text = asyncio.run(call())
    assert names == ["vat_calc"], f"등록된 도구가 {names}입니다"
    assert text == "공급가액 1,000,000원, 부가세 100,000원, 합계 1,100,000원"
