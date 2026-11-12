#!/usr/bin/env python3
"""학교 기준 맛집 목록 · 명령줄 프로그램.

근거: 같은 폴더의 요구사항명세서.md (REQ-01 ~ REQ-09)
데이터: 같은 폴더의 맛집.csv (이름,종류,기준점,도보분,가격대,한줄메모)
"""
import csv
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, "맛집.csv")


def load():
    """REQ-06: 파일이 없거나 비어 있으면 안내하고 빈 목록을 돌려준다."""
    if not os.path.exists(DATA):
        print("데이터 파일이 없습니다: 맛집.csv")
        return []
    with open(DATA, encoding="utf-8", newline="") as f:
        rows = [r for r in csv.DictReader(f) if r.get("이름")]
    if not rows:
        print("데이터 파일이 없습니다: 맛집.csv (비어 있음)")
    return rows


def walk_min(row):
    try:
        return int(row.get("도보분", "") or 0)
    except ValueError:
        return 0


def show_list(rows, title="가게 목록"):
    """REQ-02 · REQ-04 · REQ-07 · REQ-08: 가게를 한 줄씩, 개수는 아래에."""
    print(f"\n[{title}]")
    for i, r in enumerate(rows, 1):
        memo = f" · {r['한줄메모']}" if r.get("한줄메모") else ""  # REQ-07
        print(f"{i:2d}) {r['이름']} | {r['종류']} | {r['기준점']}에서 도보 {r['도보분']}분 | {r['가격대']}{memo}")
    print(f"모두 {len(rows)}곳")  # REQ-08 ← 고침


def show_by_walk(rows):
    """REQ-09 ← 추가: 도보분이 짧은 가게부터."""
    show_list(sorted(rows, key=walk_min), "도보 시간 순")


def find_by_kind(rows):
    """REQ-03 · REQ-05: 종류로 거른다. 없는 종류면 안내."""
    kind = input("종류 (예: 분식, 한식, 카페): ").strip()
    hit = [r for r in rows if r["종류"] == kind]
    if not hit:
        print(f"'{kind}' 종류의 가게가 없습니다. 있는 종류: {', '.join(sorted({r['종류'] for r in rows}))}")
        return
    show_list(hit, f"{kind} 가게")


def main():
    rows = load()
    while True:
        print("\n1) 가게 목록  2) 도보 시간 순  3) 종류로 찾기  0) 종료")  # REQ-01
        choice = input("선택: ").strip()
        if choice == "0":
            print("종료합니다.")
            return
        if not rows:
            rows = load()
            if not rows:
                continue
        if choice == "1":
            show_list(rows)
        elif choice == "2":
            show_by_walk(rows)
        elif choice == "3":
            find_by_kind(rows)
        else:
            print("없는 번호입니다. 1 · 2 · 3 · 0 중에서 고르세요.")  # REQ-05


if __name__ == "__main__":
    try:
        main()
    except (KeyboardInterrupt, EOFError):
        print("\n종료합니다.")
        sys.exit(0)
