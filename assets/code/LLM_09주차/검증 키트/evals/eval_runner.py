# -*- coding: utf-8 -*-
"""평가 러너 (week09 실습용, 완성되어 있음. 실행하며 출력을 읽는 용도).

같은 챗봇 응답 묶음을 두 방식으로 채점하여 비교합니다.
    ① 규칙 채점: 정답셋의 키워드가 응답에 들어 있는가 (빠르고 싸지만 융통성 없음)
    ② Judge 채점: Claude가 기준을 들고 응답을 판정 (융통성 있지만 비용·비결정성)

사용법:
    python eval_runner.py --rule-only     # 규칙 채점만 (API 불필요)
    python eval_runner.py                 # 규칙 + Judge 채점 비교

전제(Judge 사용 시): 환경변수 ANTHROPIC_API_KEY, COURSE_MODEL
"""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))

JUDGE_SYSTEM = """너는 학과 FAQ 챗봇의 응답을 채점하는 심판이다. 기준은 세 가지다.
① 정확성: 참고 답안의 사실과 어긋나지 않는가.
② 거절 적절성: 문서에 없는 주제라면 지어내지 않고 거절했는가.
③ 근거 없는 단정 금지: 참고 답안에 없는 절차나 조건을 만들어 붙이지 않았는가.
반드시 첫 줄에 "판정: 통과" 또는 "판정: 탈락"을 쓰고, 둘째 줄에 "이유: "로 한 문장을 쓴다."""


def rule_grade(answer, keywords):
    """키워드가 하나라도 없으면 탈락하는 단순 규칙."""
    return all(k in answer for k in keywords)


def judge_grade(client, model, item, answer):
    prompt = (f"질문: {item['question']}\n참고 답안: {item['reference']}\n"
              f"챗봇 응답: {answer}\n채점하라.")
    r = client.messages.create(model=model, max_tokens=200,
                               system=JUDGE_SYSTEM,
                               messages=[{"role": "user", "content": prompt}])
    text = "".join(b.text for b in r.content if b.type == "text")
    verdict = "통과" in text.split("\n")[0]
    reason = next((ln[3:].strip() for ln in text.split("\n") if ln.startswith("이유:")), text[:80])
    return verdict, reason


def main():
    rule_only = "--rule-only" in sys.argv
    items = json.load(open(os.path.join(HERE, "정답셋.json"), encoding="utf-8"))
    answers = json.load(open(os.path.join(HERE, "응답로그.json"), encoding="utf-8"))

    client = model = None
    if not rule_only:
        import anthropic
        client = anthropic.Anthropic()
        model = os.environ.get("COURSE_MODEL", "claude-haiku-4-5")

    print(f"{'번호':<4}{'규칙':<6}{'Judge':<7}비고")
    mismatch = []
    for item in items:
        answer = answers[str(item["id"])]
        rule = rule_grade(answer, item["keywords"])
        if rule_only:
            print(f"{item['id']:<4}{'통과' if rule else '탈락':<6}{'-':<7}")
            continue
        judge, reason = judge_grade(client, model, item, answer)
        note = ""
        if rule != judge:
            note = f"불일치! {reason}"
            mismatch.append(item["id"])
        print(f"{item['id']:<4}{'통과' if rule else '탈락':<6}{'통과' if judge else '탈락':<7}{note}")

    if not rule_only:
        print(f"\n불일치 문항: {mismatch if mismatch else '없음'}")
        print("불일치 문항의 응답과 정답셋을 직접 읽고, 어느 채점이 옳았는지 판단해 기록하세요.")


if __name__ == "__main__":
    main()
