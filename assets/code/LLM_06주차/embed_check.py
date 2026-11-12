# -*- coding: utf-8 -*-
"""임베딩 서버 점검 (실습 3의 준비 단계).

실행: .venv/bin/python embed_check.py
출력: 서버 연결 여부 · 모델 목록에 EMBED_MODEL이 있는지 · 없을 때의 예비 경로 안내
"""
import json
import os
import sys
import urllib.error
import urllib.request

OLLAMA_URL = os.environ.get("OLLAMA_URL", "http://localhost:11434")
EMBED_MODEL = os.environ.get("EMBED_MODEL", "")

print(f"EMBED_MODEL = {EMBED_MODEL or '(비어 있음. ~/.bashrc에 등록했는지 확인)'}")
try:
    with urllib.request.urlopen(OLLAMA_URL + "/api/tags", timeout=5) as r:
        names = [m.get("name", "") for m in json.loads(r.read()).get("models", [])]
    print(f"임베딩 서버 연결: OK ({OLLAMA_URL})")
    print("서버의 모델:", ", ".join(names) or "(없음)")
    if EMBED_MODEL and any(n.split(":")[0] == EMBED_MODEL.split(":")[0] for n in names):
        print(f"{EMBED_MODEL}: 있음. 실습 3을 그대로 진행합니다.")
    else:
        print(f"{EMBED_MODEL or '(모델 이름 없음)'}: 목록에 없습니다. 교수에게 알리고, 기다리는 동안은 예비 경로로 진행합니다.")
        print("예비 경로: EMBED_BACKEND=fallback .venv/bin/python embed_search.py index 학과FAQ.md")
except (urllib.error.URLError, OSError, ValueError) as e:
    print(f"임베딩 서버 연결: 실패 ({type(e).__name__})")
    print("예비 경로로 진행합니다. embed_search.py가 자동으로 예비 임베딩을 씁니다(유사도 값은 참고용).")
    sys.exit(1)
