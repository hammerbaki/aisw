# 9주차 자동화 키트

업무 자동화와 배포 파이프라인 실습용 키트입니다. 개인 폴더의 `week09/` 아래에 복사하여 사용합니다. `retry/retry_loop.py`는 참고 서적 《하네스 엔지니어링 with 클로드 코드》 공식 예제 저장소(https://github.com/revfactory/harness-engineering-with-cc, Apache 2.0)의 ex-08-15를 수업용으로 각색한 것입니다.

## 구성

| 폴더·파일 | 내용 |
|---|---|
| `pipeline/서버로그.txt`, `pipeline/pipeline.sh` | 수집·요약·통지 파이프라인 골격. 종료 코드 분기를 실습에서 완성 |
| `hooks/훅_설정예시.md` | PostToolUse 훅 설정 예시와 주의점 |
| `deploy/deploy.sh` | 배포 파이프라인: 점검 2종 통과 시에만 wrangler 배포. 배포 명령 연결을 실습에서 완성 |
| `retry/retry_loop.py` | 재시도 상한(MAX_RETRIES) 안전장치. 성공·실패 2 시나리오 (완성되어 있음, API 불필요) |
| `sync/sync_체크리스트.md` | 코드-문서 동기화 게이트 점검표 |
| `크로스테스트_기록표.md` | 동료 산출물 시험 기록표 |

## 전제

1. `pipeline.sh`는 Claude Code 로그인 환경(학과 키, Haiku)이 필요합니다.
2. `deploy.sh`의 배포 단계는 Cloudflare 계정과 wrangler 실행 환경(Node.js)이 필요합니다. 환경이 없으면 점검 단계까지 실행하고 배포는 대시보드 업로드(배포 카드)로 대체합니다.
3. `retry_loop.py`는 API 키가 필요 없습니다.
