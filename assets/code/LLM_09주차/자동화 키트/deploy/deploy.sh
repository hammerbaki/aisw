#!/bin/bash
# 배포 파이프라인 (week11 실습용): 점검 통과일 때만 배포한다.
#
# 사용법: bash deploy.sh 배포폴더
# 예:     bash deploy.sh site

SITE="${1:-site}"

echo "[1/3] API 키 노출 검사"
if grep -rn "sk-ant" "$SITE"; then
    echo "중단: 키 문자열이 발견되었습니다. 위 위치를 정리한 뒤 다시 실행하세요."
    exit 1
fi
echo "통과"

echo "[2/3] 금지 파일 검사"
if [ -f "$SITE/.env" ]; then
    echo "중단: .env 파일이 배포 폴더에 있습니다. 제거한 뒤 다시 실행하세요."
    exit 1
fi
echo "통과"

echo "[3/3] 배포"
# TODO(실습): 아래 주석을 풀어 실제 배포로 연결하라. 프로젝트 이름은 자기 것으로 바꾼다.
# npx wrangler pages deploy "$SITE" --project-name=자기프로젝트이름
echo "점검 통과. 배포 명령을 활성화하면 여기서 URL이 발급됩니다."
