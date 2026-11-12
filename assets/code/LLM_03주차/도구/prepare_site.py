"""공개할 정적 사이트를 deploy/에 복사한다. 신규 폴더만 생성한다.

명령은 하나다 : python3 도구/prepare_site.py
  mine/index.html 이 있으면 mine 을, 없으면 실습 1의 web 을 고른다.
직접 고를 때만 : python3 도구/prepare_site.py web
"""
from pathlib import Path
import argparse, shutil

p = argparse.ArgumentParser(description='공개할 폴더를 deploy/로 복사한다.')
p.add_argument('source', nargs='?', choices=['web', 'mine'],
               help='(선택) 비우면 mine/index.html 유무로 자동으로 고른다.')
a = p.parse_args()

r = Path(__file__).resolve().parents[1]
dst = r / 'deploy'
if dst.exists():
    raise SystemExit('deploy가 이미 있습니다. 내용을 검토하거나 이전 폴더를 다른 이름으로 보관한 뒤 다시 실행하세요.')

if a.source:
    name = a.source
    how = f'{name} (내가 직접 고름)'
elif (r / 'mine' / 'index.html').is_file():
    name, how = 'mine', 'mine (index.html이 있습니다. 검증한 결과물을 그대로 올립니다)'
elif (r / 'web' / 'index.html').is_file():
    name, how = 'web', 'web (mine에 index.html이 없어 실습 1 결과를 씁니다)'
else:
    raise SystemExit('mine에도 web에도 index.html이 없습니다. 실습 1의 web/index.html을 먼저 확인하세요.')

src = r / name
if not (src / 'index.html').is_file():
    raise SystemExit(f'{src} 에 index.html이 없습니다. "python3 {r}/도구/prepare_site.py web" 으로 실습 1 결과를 고르세요.')

allowed = {'.html', '.css', '.js', '.png', '.jpg', '.jpeg', '.svg', '.webp', '.gif', '.ico', '.woff', '.woff2', '.ttf'}
skip = {'.git', '.venv', 'node_modules', 'tests', '__pycache__'}
files = [x for x in src.rglob('*') if x.is_file() and x.suffix.lower() in allowed
         and not any(y in skip or y.startswith('.') for y in x.relative_to(src).parts) and not x.is_symlink()]
for x in files:
    t = dst / x.relative_to(src); t.parent.mkdir(parents=True, exist_ok=True); shutil.copy2(x, t)

print('공개 폴더:', how)
print('정적 파일 복사 완료:', len(files), '파일')
print('자동 보안 검사가 아닙니다. 아래 목록과 파일 내용을 직접 읽고, 브라우저에서 기능을 확인하세요.')
for x in files:
    print(x.relative_to(src))
print('CSV/JSON 데이터가 필요한 화면은 공개할 데이터만 HTML/JS에 담고 다시 준비하세요. 원본 폴더 전체를 업로드하지 마세요.')
