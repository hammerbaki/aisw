# 9주차 검증 키트

검증과 평가(Evals), 검토자 서브에이전트 실습용 키트입니다. 개인 폴더의 `week09/` 아래에 복사하여 사용합니다. `reviewer/`와 `deploy-check/`의 구도는 참고 서적 《하네스 엔지니어링 with 클로드 코드》 공식 예제 저장소(https://github.com/revfactory/harness-engineering-with-cc, Apache 2.0)의 ex-04-01(읽기 전용 검토자), ex-11-06(의도 버그 검증)을 수업용으로 각색한 것입니다.

## 구성

| 폴더·파일 | 내용 |
|---|---|
| `evals/eval_runner.py` | 규칙 채점과 Judge 채점을 비교하는 평가 러너 (완성되어 있음) |
| `evals/정답셋.json`, `evals/응답로그.json` | 채점 재료: 질문·키워드·참고 답안 6건과 챗봇 응답 로그 |
| `reviewer/검토자_골격.md` | 배포 전 점검 검토자(서브에이전트) 정의 파일 골격 |
| `deploy-check/site/` | 배포 직전 폴더 샘플. 위반 3건이 심어져 있음 (검토자 성능 검증용) |
| `deploy-check/정답_위반목록.md` | 심어 둔 위반의 정답. **판정 기록을 마친 뒤에 엽니다** |

## 사용 순서

```bash
python evals/eval_runner.py --rule-only   # 규칙 채점만 (API 불필요)
python evals/eval_runner.py               # 규칙 + Judge 비교
```

검토자 정의 파일은 골격을 참고해 `week09/.claude/agents/deploy-checker.md`에 직접 작성합니다. 절차는 강의안을 따릅니다.

## 주의

- `deploy-check/site/`의 키 문자열은 실습용 가짜 값이며, 이 폴더는 절대 실제로 배포하지 않습니다.
- `정답_위반목록.md`는 자기 판정 기록을 마치기 전에 열지 않습니다.

## 전제

`eval_runner.py`의 Judge 채점만 API 환경(`ANTHROPIC_API_KEY`, `COURSE_MODEL`)이 필요합니다. 나머지는 API 키가 필요 없습니다.
