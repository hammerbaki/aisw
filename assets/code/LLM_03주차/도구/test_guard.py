"""수용한 tests/를 동결하고 변경/삭제/추가 여부를 확인한다."""
from pathlib import Path
import argparse,hashlib,json
p=argparse.ArgumentParser();p.add_argument('action',choices=['freeze','check']);a=p.parse_args()
r=Path.cwd(); tests=r/'tests';dest=r/'.test-baseline.json'
files={str(x.relative_to(r)):hashlib.sha256(x.read_bytes()).hexdigest() for x in sorted(tests.rglob('*.py'))} if tests.exists() else {}
if not files:raise SystemExit('tests/에 Python 테스트 파일이 없습니다.')
if a.action=='freeze':
 if dest.exists():raise SystemExit('이미 동결했습니다. 기준을 다시 덮어쓰지 않습니다.')
 dest.write_text(json.dumps(files,ensure_ascii=False,indent=2),encoding='utf-8');print('동결 완료:',len(files),'파일')
else:
 if not dest.exists():raise SystemExit('동결 기록이 없습니다.')
 before=json.loads(dest.read_text(encoding='utf-8'))
 changed=sorted(k for k in before.keys()|files.keys() if before.get(k)!=files.get(k))
 if changed:print('TEST_CHANGED:',*changed,sep='\n');raise SystemExit(1)
 print(f'TEST_UNCHANGED (.test-baseline.json 기준 · {len(files)}개 파일)')
