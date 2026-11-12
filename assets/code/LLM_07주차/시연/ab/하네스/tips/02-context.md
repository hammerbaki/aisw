# 작업이 바뀌면 컨텍스트를 정리한다 (/clear, /compact)

근거: https://code.claude.com/docs/en/how-claude-code-works

- 상황: 앞 작업의 대화 이력이 새 작업에 소음이 되고, 컨텍스트가 차면 오래된 내용이 유실된다.
- 방법: 이력을 버릴 때는 /clear, 요약해 이어갈 때는 /compact를 쓴다. 남길 내용은 /compact 뒤에 지시로 적는다.
- 예시: `/compact 테스트 실패 원인과 수정 방침은 반드시 남겨라`
- 주의점: /clear는 복구되지 않는다. 기록이 필요하면 /export로 먼저 내보낸다.
