# -*- coding: utf-8 -*-
"""스킬 형식 고정 테스트. 고치지 않는다(TDD에서 동결한 테스트와 같은 역할).

.claude/skills/portfolio-check/SKILL.md의 형식만 본다. 내용(무엇을 점검하는가)은 사람이 판정한다.
가장 단순한 형태는 앞의 둘, 발전형은 셋 다 통과한다.
"""
import re
from pathlib import Path

SKILL = Path(__file__).resolve().parents[1] / ".claude" / "skills" / "portfolio-check" / "SKILL.md"


def read_skill():
    assert SKILL.exists(), ".claude/skills/portfolio-check/SKILL.md가 없습니다"
    return SKILL.read_text(encoding="utf-8")


def test_머리말에_폴더와_같은_name과_description이_있다():
    lines = read_skill().splitlines()
    assert lines and lines[0].strip() == "---", "첫 줄이 --- 여야 합니다"
    ends = [i for i in range(1, len(lines)) if lines[i].strip() == "---"]
    assert ends, "머리말을 닫는 --- 줄이 없습니다"
    head = "\n".join(lines[1:ends[0]])
    assert re.search(r"^name:\s*portfolio-check\s*$", head, re.M), "name이 없거나 폴더 이름(portfolio-check)과 다릅니다"
    m = re.search(r"^description:[ \t]*(.*)$", head, re.M)
    assert m, "description이 없습니다"
    desc = m.group(1).strip()
    if desc in ("", ">", "|", ">-", "|-"):  # 여러 줄로 쓴 경우: 들여 쓴 다음 줄들을 이어 읽는다
        rest = head[m.end():].splitlines()
        desc = " ".join(l.strip() for l in rest if l.startswith((" ", "\t")))
    assert len(desc) >= 10, "description이 너무 짧습니다"


def test_전체가_60줄을_넘지_않는다():
    n = len(read_skill().splitlines())
    assert n <= 60, f"{n}줄입니다. 60줄 이하로 줄입니다(안티패턴 ① 거대 본문)"


def test_규칙_두_개에_이유가_붙어_있다():
    n = read_skill().count("왜냐하면")
    assert n >= 2, f"「왜냐하면」이 {n}개입니다. 규칙 두 개에 이유를 붙입니다(안티패턴 ③ 이유 없는 규칙)"
