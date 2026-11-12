"""5주차 실습 3의 1단계: 문장의 토큰 수를 잰다.

사용법:
    python3 스크립트/token_count.py "측정할 문장"
    python3 스크립트/token_count.py --check        # 키·모델 설정만 확인

동작:
    4주차 채점기(ab_runner.py)와 같은 방식으로 파이썬 표준 라이브러리(urllib)만 써서
    Claude API의 토큰 계산 기능(count_tokens)에 문장을 보내고 토큰 수를 받는다.
    설치할 패키지가 없다. 인증은 환경변수 ANTHROPIC_API_KEY, 모델은 환경변수
    COURSE_MODEL(없으면 수업 기본 모델)을 쓴다. 키는 화면에 출력하지 않는다.

참고:
    결과에는 요청 형식에 붙는 고정 토큰이 더해져 있다(교수 화면 7토큰. "a" 한 글자가 8).
    측정값 = 고정분 + 문장 토큰. 비교할 때는 고정분을 빼고 본다.
"""
import json
import os
import sys
import urllib.error
import urllib.request

MODEL = os.environ.get("COURSE_MODEL", "claude-haiku-4-5-20251001")
URL = "https://api.anthropic.com/v1/messages/count_tokens"


def count_tokens(text):
    key = os.environ.get("ANTHROPIC_API_KEY", "")
    if not key:
        raise SystemExit("KEY_NOT_SET: ANTHROPIC_API_KEY가 없습니다. 강의안 0장의 키 등록을 먼저 합니다.")
    payload = json.dumps({"model": MODEL, "messages": [{"role": "user", "content": text}]}).encode()
    headers = {"x-api-key": key, "anthropic-version": "2023-06-01", "content-type": "application/json"}
    for attempt in range(2):
        req = urllib.request.Request(URL, data=payload, headers=headers)
        try:
            with urllib.request.urlopen(req, timeout=30) as resp:
                return json.load(resp)["input_tokens"]
        except urllib.error.HTTPError as e:
            if e.code == 400 and attempt == 0 and "anthropic-beta" not in headers:
                headers["anthropic-beta"] = "token-counting-2024-11-01"  # 구 버전 API용. 보통은 필요 없음
                continue
            raise SystemExit(f"HTTP {e.code}: 인증·모델 권한·요청 제한을 확인합니다. 원문 오류에 키가 들어 있을 수 있어 출력하지 않습니다.")
        except (urllib.error.URLError, TimeoutError):
            raise SystemExit("네트워크 오류 또는 시간 초과. 잠시 뒤 다시 실행합니다.")


if __name__ == "__main__":
    args = sys.argv[1:]
    if args == ["--check"]:
        print("MODEL", MODEL, "API_KEY_SET=" + str(bool(os.environ.get("ANTHROPIC_API_KEY"))))
        sys.exit(0)
    if not args:
        print('사용법: python3 스크립트/token_count.py "측정할 문장"')
        sys.exit(1)
    text = " ".join(args)
    print(f"문장: {text}")
    print(f"토큰 수: {count_tokens(text)}")
