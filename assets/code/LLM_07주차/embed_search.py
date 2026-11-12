# -*- coding: utf-8 -*-
"""임베딩 유사도 검색기 (week07 키트 · 완성되어 있음).

앞 주제 「API 연동과 RAG 챗봇」에서 두 함수(cosine_similarity · search)를 채워 만든 검색기와
같은 구조의 완성본입니다. 이 수업에서는 고치지 않고 도구의 부품으로 씁니다.

사용법:
    .venv/bin/python embed_search.py index 학과FAQ.md           # 문서를 청킹 · 임베딩하여 index.json 생성
    .venv/bin/python embed_search.py search "질문 문장"          # 질문과 가까운 상위 3개 청크 출력
    .venv/bin/python embed_search.py sim "문장1" "문장2"        # 두 문장의 유사도 출력

두 번째 문서(사내규정/복무규정.md)는 그 폴더에서 ../ 로 부릅니다.
    cd 사내규정 && ../.venv/bin/python ../embed_search.py index 복무규정.md

임베딩은 서버의 Ollama(공개 임베딩 모델)를 씁니다.
    - 환경변수 EMBED_MODEL: 임베딩 모델 이름 (과목 공지 값, 없으면 기본 nomic-embed-text)
    - 환경변수 CHUNK_MODE: "section"(제목 단위, 기본) 또는 "size"(고정 길이)
    - 환경변수 EMBED_BACKEND: "ollama"(기본) 또는 "fallback"
      임베딩 서버에 연결할 수 없으면 자동으로 예비 임베딩(fallback)으로 넘어갑니다.
      예비 임베딩은 설치가 필요 없는 저품질 대체 경로입니다. 검색은 되지만
      유사도 값은 참고용입니다. 색인과 질문은 같은 경로로 만들어야 합니다.

index.json은 명령을 실행한 폴더에 만들어지고 읽힙니다.
"""
import csv
import json
import math
import os
import sys
import urllib.error
import urllib.request

OLLAMA_URL = os.environ.get("OLLAMA_URL", "http://localhost:11434")
EMBED_MODEL = os.environ.get("EMBED_MODEL", "nomic-embed-text")
CHUNK_MODE = os.environ.get("CHUNK_MODE", "section")
EMBED_BACKEND = os.environ.get("EMBED_BACKEND", "ollama")  # "ollama" 또는 "fallback"
INDEX_FILE = "index.json"
TOP_K = 3
_FALLBACK_DIM = 1024
_notified = {"fallback": False}


def _embed_fallback(text):
    """예비 임베딩: 글자 두 개씩 묶은 조각(bigram)을 해시해 고정 길이 벡터로 만든다.
    의미를 이해하지는 못하지만 표현이 겹치는 정도를 잰다. 서버가 없을 때만 쓴다."""
    text = " ".join(text.lower().split())
    vec = [0.0] * _FALLBACK_DIM
    grams = [text[i:i + 2] for i in range(len(text) - 1)] or [text]
    for g in grams:
        h = 0
        for ch in g:
            h = (h * 131 + ord(ch)) % 1000003
        vec[h % _FALLBACK_DIM] += 1.0
    norm = math.sqrt(sum(v * v for v in vec)) or 1.0
    return [v / norm for v in vec]


def _embed_ollama(text):
    """Ollama 임베딩 호출. 현재 주소(/api/embed)를 먼저 쓰고, 옛 판 서버면 /api/embeddings로 다시 부른다."""
    calls = (
        ("/api/embed", {"model": EMBED_MODEL, "input": text}, lambda data: data["embeddings"][0]),
        ("/api/embeddings", {"model": EMBED_MODEL, "prompt": text}, lambda data: data["embedding"]),
    )
    for path, body, pick in calls:
        request = urllib.request.Request(
            OLLAMA_URL + path,
            data=json.dumps(body).encode("utf-8"),
            headers={"Content-Type": "application/json"},
        )
        try:
            with urllib.request.urlopen(request, timeout=30) as response:
                return pick(json.loads(response.read()))
        except urllib.error.HTTPError as e:
            if e.code == 404 and path == "/api/embed":
                continue  # 옛 판 서버: 다음 주소로
            raise


def embed(text):
    """텍스트 하나를 임베딩 벡터(숫자 목록)로 바꾼다. (완성되어 있음)"""
    global EMBED_BACKEND
    if EMBED_BACKEND == "ollama":
        try:
            return _embed_ollama(text)
        except (urllib.error.URLError, OSError, KeyError, IndexError, ValueError) as e:
            EMBED_BACKEND = "fallback"
            print(f"[예비 경로] 임베딩 서버({OLLAMA_URL}, 모델 {EMBED_MODEL})에 연결할 수 없어 "
                  f"예비 임베딩으로 넘어갑니다. 유사도 값은 참고용입니다. ({type(e).__name__})",
                  file=sys.stderr)
    if not _notified["fallback"]:
        _notified["fallback"] = True
        if os.environ.get("EMBED_BACKEND", "ollama") == "fallback":
            print("[예비 경로] EMBED_BACKEND=fallback: 예비 임베딩을 씁니다. 유사도 값은 참고용입니다.",
                  file=sys.stderr)
    return _embed_fallback(text)


def chunk(text):
    """문서를 청크 목록으로 자른다. (완성되어 있음, 기준은 CHUNK_MODE로 선택)"""
    if CHUNK_MODE == "section":
        parts = []
        current = []
        for line in text.split("\n"):
            if line.startswith("## ") and current:
                parts.append("\n".join(current).strip())
                current = []
            current.append(line)
        if current:
            parts.append("\n".join(current).strip())
        return [p for p in parts if p]
    if CHUNK_MODE == "size":
        size = 150
        return [text[i:i + size] for i in range(0, len(text), size)]
    raise ValueError("CHUNK_MODE는 section 또는 size")


def cosine_similarity(a, b):
    """두 벡터의 코사인 유사도를 반환한다. [실습에서 완성]

    공식: (a와 b의 내적) / (a의 크기 * b의 크기)
    내적은 같은 위치 성분끼리 곱해 모두 더한 값,
    크기는 각 성분 제곱합의 제곱근(math.sqrt)이다.
    """
    dot = sum(x * y for x, y in zip(a, b))  # zip: 두 목록을 같은 위치끼리 짝지음
    norm_a = math.sqrt(sum(x * x for x in a))
    norm_b = math.sqrt(sum(x * x for x in b))
    return dot / (norm_a * norm_b)


def search(query, index):
    """질문과 가까운 순으로 (유사도, 청크) 상위 TOP_K개를 반환한다. (완성되어 있음)

    순서: ① 질문을 embed로 벡터화 ② index의 모든 청크 벡터와
    cosine_similarity 계산 ③ 유사도 내림차순 정렬 후 앞 TOP_K개 반환.
    index는 [{"text": 청크, "vector": 벡터}, ...] 형태다.
    """
    query_vector = embed(query)
    scored = [(cosine_similarity(query_vector, item["vector"]), item["text"])
              for item in index]
    scored.sort(key=lambda pair: -pair[0])  # lambda는 이름 없이 한 줄로 쓰는 임시 함수. 점수가 큰 순서가 되도록 음수로 뒤집어 정렬
    return scored[:TOP_K]


def build_index(path):
    with open(path, encoding="utf-8") as f:
        text = f.read()
    chunks = chunk(text)
    index = []
    for i, c in enumerate(chunks, 1):
        index.append({"text": c, "vector": embed(c)})
        print(f"임베딩 {i}/{len(chunks)}")
    with open(INDEX_FILE, "w", encoding="utf-8") as f:
        json.dump(index, f, ensure_ascii=False)
    print(f"청크 {len(chunks)}개를 {INDEX_FILE}에 저장 (CHUNK_MODE={CHUNK_MODE}, 임베딩={EMBED_BACKEND})")


def load_index():
    if not os.path.exists(INDEX_FILE):
        sys.exit(f"{INDEX_FILE}이 이 폴더에 없습니다. 먼저 index 명령으로 색인을 만듭니다.")
    with open(INDEX_FILE, encoding="utf-8") as f:
        return json.load(f)


def evaluate(csv_path):
    """평가 문항 CSV(질문,정답키워드)로 top-3 재현율을 측정한다."""
    with open(csv_path, encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    index = load_index()
    hit = 0
    for i, row in enumerate(rows, 1):
        results = search(row["질문"], index)
        found = any(row["정답키워드"] in text for _, text in results)
        hit += int(found)
        print(f"{i:2d}. [{'O' if found else 'X'}] {row['질문']}")
    print(f"\n재현율(top-{TOP_K}): {hit}/{len(rows)} ({hit / len(rows) * 100:.0f}%)")


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)
    command = sys.argv[1]
    if command == "sim" and len(sys.argv) == 4:
        a, b = embed(sys.argv[2]), embed(sys.argv[3])
        print(f"유사도: {cosine_similarity(a, b):.4f}")
    elif command == "index" and len(sys.argv) == 3:
        build_index(sys.argv[2])
    elif command == "search" and len(sys.argv) == 3:
        for score, text in search(sys.argv[2], load_index()):
            print(f"\n[유사도 {score:.4f}] {text[:200]}")
    elif command == "eval" and len(sys.argv) == 3:
        evaluate(sys.argv[2])
    else:
        print(__doc__)
        sys.exit(1)


if __name__ == "__main__":
    main()
