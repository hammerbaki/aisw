# -*- coding: utf-8 -*-
"""재시도 상한(MAX_RETRIES) 안전장치 (week09 실습용, 완성되어 있음).

자동 반복 작업의 기본 안전장치입니다. 생성과 검증을 반복하되,
상한을 넘으면 무한 반복 대신 실패를 보고하고 사람에게 넘깁니다.

사용법:
    python retry_loop.py success   # 2번째 시도에서 검증 통과
    python retry_loop.py fail      # 상한 도달 후 수동 개입 요청

API 키가 필요 없습니다 (생성기와 검증기는 시나리오용 대역).
"""
import sys

MAX_RETRIES = 3


def generate(scenario, attempt):
    """생성 단계의 대역. 실제로는 AI 생성 호출이 들어갈 자리다."""
    if scenario == "success" and attempt >= 2:
        return f"산출물_v{attempt}_정상"
    return f"산출물_v{attempt}_불량"


def verify(artifact):
    """검증 단계의 대역. 실제로는 pytest나 배포 전 점검이 들어갈 자리다."""
    ok = "정상" in artifact
    reason = "" if ok else "검증 실패: 기준 미달"
    return ok, reason


def generate_with_retries(scenario):
    for attempt in range(1, MAX_RETRIES + 1):
        artifact = generate(scenario, attempt)
        ok, reason = verify(artifact)
        print(f"[시도 {attempt}/{MAX_RETRIES}] 산출물={artifact} 통과={ok} {reason}")
        if ok:
            return artifact
    return None


def main():
    scenario = sys.argv[1] if len(sys.argv) > 1 else "success"
    if scenario not in ("success", "fail"):
        print("사용법: python retry_loop.py success|fail")
        return 1
    result = generate_with_retries(scenario)
    if result is None:
        print(f"중단: {MAX_RETRIES}회 실패. 수동 개입이 필요합니다.")
        return 1
    print(f"완료: {result}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
