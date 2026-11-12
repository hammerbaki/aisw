"""검토한 deploy 폴더를 루트 index.html 구조의 ZIP으로 묶는다."""
from pathlib import Path
import zipfile
r=Path(__file__).resolve().parents[1];src=r/'deploy';out=r/'deploy.zip'
if out.exists():raise SystemExit('deploy.zip이 이미 있습니다. 이전 ZIP을 다른 이름으로 보관한 뒤 다시 실행하세요.')
if not (src/'index.html').is_file():raise SystemExit(f'deploy/index.html이 없습니다. "python3 {r}/도구/prepare_site.py" 를 먼저 실행하세요.')
files=sorted(x for x in src.rglob('*') if x.is_file())
allowed={'.html','.css','.js','.png','.jpg','.jpeg','.svg','.webp','.gif','.ico','.woff','.woff2','.ttf'}
if any(x.is_symlink() or x.suffix.lower() not in allowed or any(y.startswith('.') for y in x.relative_to(src).parts) for x in files):raise SystemExit('정적 파일 이외의 항목 또는 링크가 있습니다. deploy의 공개 파일 목록을 다시 확인하세요.')
with zipfile.ZipFile(out,'x',zipfile.ZIP_DEFLATED) as z:
 for x in files:z.write(x,x.relative_to(src).as_posix())
with zipfile.ZipFile(out) as z:
 assert 'index.html' in z.namelist()
 print('ZIP_READY:',out)
 print(*z.namelist(),sep='\n')
print('내용 검토 후 VS Code에서 deploy.zip을 Download하여 내 PC의 Cloudflare에 업로드하세요.')
