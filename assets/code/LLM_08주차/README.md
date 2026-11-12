# 8주차 에이전트 키트

에이전트 구현 실습용 키트입니다. 개인 폴더의 `week08/` 아래에 복사하여 사용합니다.

## 구성

| 폴더·파일 | 내용 |
|---|---|
| `react/react_agent.py` | ReAct 루프 골격. TODO 2곳(parse_action, 관찰 재주입)을 실습에서 완성 |
| `sdk/sdk_agent.py` | 같은 에이전트의 Claude Agent SDK 재구현판 (완성되어 있음, 실행·대조 용도) |
| `charter/Charter_양식.md` | 프로젝트 Charter 양식 |
| `charter/Spec_양식.md` | Requirement Spec 양식 (EARS 문형 참조표 포함) |

## 사용 순서

```bash
python react/react_agent.py mock            # 완성 전에는 NotImplementedError로 멈춤 (정상)
python react/react_agent.py mock            # TODO 2곳 완성 후: API 없이 루프 검증
python react/react_agent.py ask "100만원 노트북, 부가세 포함가에서 20% 할인하면?"
python sdk/sdk_agent.py "100만원 노트북, 부가세 포함가에서 20% 할인하면?"
```

## 전제

1. `react_agent.py`의 mock 모드는 API가 필요 없습니다. ask 모드는 API 연동 실습과 같은 환경(`ANTHROPIC_API_KEY`, `COURSE_MODEL`)이 필요합니다.
2. `sdk_agent.py`는 claude-agent-sdk 패키지와 Claude Code 설치 환경이 필요합니다(실습 서버에는 준비되어 있음).
