# -*- coding: utf-8 -*-
"""ReAct 루프 골격 (week08 실습용).

생각(Thought) → 행동(Action) → 관찰(Observation)을 반복하는 에이전트 루프를
클린 아키텍처 골격(LLMServiceInterface + 어댑터 주입) 위에 직접 구현합니다.

완성할 곳은 TODO 2곳입니다.
    ① parse_action: 모델 출력에서 행동과 입력을 골라내는 분기
    ② run_loop 안의 관찰 재주입: 관찰 결과를 다음 프롬프트에 추가

검증 순서:
    1) Mock으로 루프 검증 (API 불필요):  python react_agent.py mock
    2) 실제 모델로 실행:                python react_agent.py ask "질문"

전제(실제 모델 실행 시): 환경변수 ANTHROPIC_API_KEY, COURSE_MODEL
"""
import os
import sys

MAX_STEPS = 5  # 무한 반복을 막는 상한. 루프 안전장치의 최소형이다.

SYSTEM = """너는 도구를 쓰는 상담원이다. 반드시 아래 서식으로만 답한다.

생각: (다음에 무엇을 할지 한 문장)
행동: (vat_calc 또는 discount_calc 또는 finish 중 하나)
입력: (행동에 넘길 값. vat_calc는 공급가액 숫자, discount_calc는 "원가,할인율" 형식, finish는 사용자에게 줄 최종 답)

규칙: 한 번에 행동 하나만 쓴다. 계산은 직접 하지 말고 반드시 도구로 한다.
관찰 결과가 주어지면 그것을 근거로 다음 생각을 잇는다."""


# ---------- 도구 (도구 사용 실습의 원칙 그대로: 인자 검증, 오류는 문자열로) ----------

def vat_calc(raw):
    try:
        amount = float(str(raw).replace(",", "").replace("원", "").strip())
    except (TypeError, ValueError):
        return "오류: 숫자가 필요합니다"
    if amount < 0:
        return "오류: 금액은 0 이상이어야 합니다"
    vat = round(amount * 0.1)
    return f"공급가액 {amount:,.0f}원, 부가세 {vat:,}원, 합계 {amount + vat:,.0f}원"


def discount_calc(raw):
    try:
        price_s, rate_s = str(raw).split(",")
        price, rate = float(price_s), float(rate_s)
    except (TypeError, ValueError):
        return "오류: '원가,할인율' 형식이 필요합니다 (예: 50000,20)"
    if not (0 <= rate <= 100):
        return "오류: 할인율은 0~100 사이여야 합니다"
    sale = round(price * (1 - rate / 100))
    return f"원가 {price:,.0f}원, {rate:g}% 할인 적용가 {sale:,}원"


TOOLS = {"vat_calc": vat_calc, "discount_calc": discount_calc}


# ---------- ① 행동 선택: 모델 출력 파싱 ----------

def parse_action(text):
    """모델 출력에서 (행동, 입력) 쌍을 골라낸다.

    TODO(실습): 아래 독스트링의 구성대로 완성하라.
    ① 출력의 각 줄에서 "행동:"으로 시작하는 줄과 "입력:"으로 시작하는 줄을 찾는다.
    ② 각각 앞머리("행동:", "입력:")를 떼고 양끝 공백을 지운 값을 만든다.
    ③ (행동, 입력) 튜플을 돌려준다. 행동 줄을 찾지 못했으면 ("finish", text)를
       돌려준다(서식을 벗어난 출력은 최종 답으로 취급하는 폴백).
    """
    raise NotImplementedError("parse_action을 완성하세요")


# ---------- 에이전트 루프 ----------

def run_loop(llm, question, verbose=True):
    """생각→행동→관찰 반복. llm은 generate(system, prompt) 메서드를 가진 어댑터."""
    prompt = f"사용자 질문: {question}\n"
    for step in range(1, MAX_STEPS + 1):
        text = llm.generate(SYSTEM, prompt)
        if verbose:
            print(f"\n[{step}단계 모델 출력]\n{text}")
        action, arg = parse_action(text)
        if action == "finish":
            return arg
        if action not in TOOLS:
            observation = f"오류: 알 수 없는 행동 {action}"
        else:
            observation = TOOLS[action](arg)
        if verbose:
            print(f"[관찰] {observation}")
        # TODO(실습): 관찰 재주입.
        # 지금까지의 대화가 이어지도록, 모델 출력(text)과 관찰 결과를
        # prompt 끝에 붙인다. 다음 형식을 사용한다.
        #   prompt += text + f"\n관찰: {observation}\n"
        raise NotImplementedError("관찰 재주입을 완성하세요")
    return "중단: 최대 단계 수를 넘었습니다"


# ---------- 어댑터 ----------

class MockLLMAdapter:
    """정해진 각본을 차례로 돌려주는 Mock. 루프 자체를 API 없이 검증한다."""

    def __init__(self, script):
        self.script = list(script)

    def generate(self, system, prompt):
        return self.script.pop(0)


class ClaudeAdapter:
    def __init__(self):
        import anthropic
        self.client = anthropic.Anthropic()
        self.model = os.environ.get("COURSE_MODEL", "claude-haiku-4-5")

    def generate(self, system, prompt):
        r = self.client.messages.create(
            model=self.model, max_tokens=400, system=system,
            messages=[{"role": "user", "content": prompt}],
        )
        return "".join(b.text for b in r.content if b.type == "text")


MOCK_SCRIPT = [
    "생각: 부가세부터 계산한다\n행동: vat_calc\n입력: 1000000",
    "생각: 합계에 20% 할인을 적용한다\n행동: discount_calc\n입력: 1100000,20",
    "생각: 답을 정리한다\n행동: finish\n입력: 부가세 포함 110만원에서 20% 할인하면 880,000원입니다",
]


def main():
    if len(sys.argv) >= 2 and sys.argv[1] == "mock":
        answer = run_loop(MockLLMAdapter(MOCK_SCRIPT),
                          "100만원 노트북, 부가세 포함가에서 20% 할인하면?")
        print(f"\n[최종 답] {answer}")
    elif len(sys.argv) >= 3 and sys.argv[1] == "ask":
        answer = run_loop(ClaudeAdapter(), sys.argv[2])
        print(f"\n[최종 답] {answer}")
    else:
        print(__doc__)
        sys.exit(1)


if __name__ == "__main__":
    main()
