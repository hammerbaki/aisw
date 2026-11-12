# -*- coding: utf-8 -*-
"""포트폴리오 고정 테스트. 고치지 않는다(TDD에서 동결한 테스트와 같은 역할).

REQ-01 섹션 id 네 개 · REQ-03 이메일은 프로필.md에 있는 것만 · REQ-04 전화번호 없음.
pytest와 표준 라이브러리만 쓴다.
"""
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PAGE = (ROOT / "index.html").read_text(encoding="utf-8")
PROFILE = (ROOT / "프로필.md").read_text(encoding="utf-8")


def test_섹션_id_네_개가_있다():
    for sid in ("about", "skills", "projects", "contact"):
        assert f'id="{sid}"' in PAGE, f"섹션 id {sid}가 없습니다"


def test_이메일은_프로필에_있는_것만_쓴다():
    emails = set(re.findall(r"[\w.+-]+@[\w-]+(?:\.[\w-]+)+", PAGE))
    assert emails, "이메일이 없습니다"
    for e in emails:
        assert e in PROFILE, f"프로필.md에 없는 이메일입니다: {e}"


def test_전화번호를_표시하지_않는다():
    found = re.search(r"01[016789][-. ]?\d{3,4}[-. ]?\d{4}", PAGE)
    assert found is None, f"전화번호가 있습니다: {found.group() if found else ''}"
