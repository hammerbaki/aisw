from pathlib import Path
import shutil
r=Path(__file__).resolve().parents[1];dst=r/'demo'
if dst.exists():raise SystemExit('demo가 이미 있습니다. 이어서 쓰거나 다른 이름으로 보관한 뒤 준비하세요.')
dst.mkdir()
for name in ('사고1','tdd'):
 src=r/'시연'/name
 if not src.is_dir():raise SystemExit(f'시연/{name} 폴더가 없습니다. 키트를 다시 받으세요.')
 shutil.copytree(src,dst/name)
print('만들었습니다:',dst)
print('demo/사고1 · demo/tdd  ← 실행은 여기서. 원본 week03/시연은 그대로 둡니다')
