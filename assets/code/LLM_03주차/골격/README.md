# 실습 2 · 1/6~2/6 · 숫자 판정 골격

덱 「실습 공통 · 준비」 장에서 `~/week03`에 가상환경을 만든 뒤 실행합니다.

```bash
cd ~/week03
test -d tdd || cp -r 골격 tdd
cd ~/week03/tdd
~/week03/.venv/bin/python -m pytest -q tests
```

처음에는 `judge.py`가 `NotImplementedError: 테스트를 먼저 읽고 구현하세요`를 내므로 **`5 failed`가 정상**입니다(전원 같은 화면). `No module named pytest`는 준비 장의 설치가 안 된 것이고, `No module named judge`는 `tdd` 폴더가 아닌 곳에서 실행한 것입니다. 둘 다 이 실습의 정상 Red가 아니므로 먼저 해결합니다.

테스트는 그대로 두고 `judge.py`만 구현하면 `5 passed`가 됩니다. 시작 전에 동결하고 구현 뒤 비교하는 절차는 덱 실습 2 · 1/6~2/6과 같습니다.

```bash
cd ~/week03/tdd
python3 ~/week03/도구/test_guard.py freeze   # 동결 완료: 1 파일
# 구현 뒤
python3 ~/week03/도구/test_guard.py check    # TEST_UNCHANGED (.test-baseline.json 기준 · 1개 파일)
```

동결 기록 `.test-baseline.json`은 **명령을 실행한 폴더**에 생깁니다. 그래서 `tdd`와 `mine`은 각각 따로 동결합니다.

모순 테스트는 교수 시연에서만 쓰며 재료는 `week03/시연/tdd_교수/`에 있습니다. 이 골격에는 두지 않습니다.
