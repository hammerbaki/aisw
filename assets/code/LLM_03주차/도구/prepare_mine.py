"""실습 2 개인 복사본 만들기. SDD 포트폴리오는 건드리지 않는다.

재료는 포트폴리오 하나다.
명령은 하나다 : python3 도구/prepare_mine.py
  SDD 결과물(week02/포트폴리오/rebuild)이 있으면 그것을 가져온다.
  없으면 키트 예제(week03/예제/포트폴리오)로 대신하고 화면에 이유를 알린다.
  내소재.md가 없으면 양식에서 직접 만든다.
  복사 뒤 index.html이 없으면 이름을 바꾸거나 키트 예제를 넣는다.
  mine에서 pytest를 돌릴 수 있도록 tests/ · pytest.ini · conftest.py를 갖춰 둔다.
화면에 찍는 명령은 모두 절대경로다. 학생이 어느 폴더에서 실행해도 그대로 치면 된다.
"""
from pathlib import Path
import argparse, shutil

root = Path(__file__).resolve().parents[1]          # ~/week03
me = f'python3 {root}/도구/prepare_mine.py'

p = argparse.ArgumentParser(description='실습 2의 mine 폴더를 만든다. 재료는 포트폴리오 하나다.')
p.add_argument('--track', help='(옛 인자) 재료가 포트폴리오로 고정되어 쓰지 않습니다.')
a = p.parse_args()

if a.track and a.track.upper() != 'D':
    raise SystemExit(f'재료는 포트폴리오 하나입니다. 인자 없이 "{me}" 만 치세요.')

dst = root / 'mine'
answer = root / '내소재.md'
tmpl = root / '내소재_양식.md'

if dst.exists():
    raise SystemExit(f'mine이 이미 있습니다: {dst}\n이어서 사용하세요. 새로 만들려면 기존 mine을 다른 이름으로 보관한 뒤 "{me}" 를 다시 실행하세요.')

if not answer.is_file():
    if not tmpl.is_file():
        raise SystemExit(f'{tmpl} 가 없습니다. 키트를 다시 받으세요.')
    shutil.copy2(tmpl, answer)
    print('내소재.md를 만들었습니다:', answer)

src = root.parent / 'week02' / '포트폴리오' / 'rebuild'
how = '지난주 결과물 · week02/포트폴리오/rebuild'
if not (src / '요구사항명세서.md').is_file():
    src = root / '예제' / '포트폴리오'
    how = '키트 예제 · 포트폴리오 (지난주 포트폴리오가 없어 대체)'
if not (src / '요구사항명세서.md').is_file():
    raise SystemExit(f'{src} 에서 요구사항명세서.md를 찾지 못했습니다. 키트를 다시 받으세요.')

shutil.copytree(src, dst, ignore=shutil.ignore_patterns(
    '.venv', 'node_modules', '.git', '__pycache__', '.pytest_cache', 'tests', '.test-baseline.json'))
shutil.copy2(answer, dst / '내소재.md')

# 실습 대상은 index.html 한 장이다. 없으면 여기서 채운다.
fixed = ''
if not (dst / 'index.html').is_file():
    htmls = sorted(x for x in dst.rglob('*.html'))
    if len(htmls) == 1:
        htmls[0].rename(dst / 'index.html')
        fixed = f'index.html이 없어 {htmls[0].name} 을 index.html 로 바꿨습니다.'
    else:
        # 화면을 예제로 바꾸면 명세도 예제 것이라야 짝이 맞는다. 지난주 명세는 옆에 보관한다.
        sample_dir = root / '예제' / '포트폴리오'
        sample, spec = sample_dir / 'index.html', sample_dir / '요구사항명세서.md'
        if not sample.is_file() or not spec.is_file():
            raise SystemExit(f'{sample_dir} 의 index.html 또는 요구사항명세서.md가 없습니다. 키트를 다시 받으세요.')
        shutil.copy2(sample, dst / 'index.html')
        kept = ''
        old_spec = dst / '요구사항명세서.md'
        if old_spec.is_file():
            old_spec.rename(dst / '요구사항명세서_지난주.md')
            kept = ' 지난주 명세는 요구사항명세서_지난주.md 로 옮겨 두었습니다.'
        shutil.copy2(spec, dst / '요구사항명세서.md')
        fixed = ('index.html이 없어 키트 예제의 index.html 과 요구사항명세서.md 를 함께 넣었습니다. '
                 '화면과 명세의 짝을 맞추기 위해서입니다.' + kept)

# 여기서 pytest를 돌린다. 골격과 같은 최소 구성을 갖춰 둔다.
# tests/ 가 없으면 "pytest -q tests" 가 file or directory not found 로 죽는다.
(dst / 'tests').mkdir(exist_ok=True)
(dst / 'tests' / '.gitkeep').write_text('', encoding='utf-8')
(dst / 'pytest.ini').write_text('[pytest]\ntestpaths = tests\n', encoding='utf-8')
(dst / 'conftest.py').write_text(
    '# pytest가 이 폴더를 임포트 경로에 넣게 하는 빈 파일입니다. 지우지 않습니다.\n', encoding='utf-8')

print('준비 완료:', dst)
print('가져온 곳:', how)
if fixed:
    print('손본 곳:', fixed)
print('고칠 파일: index.html')
print()
print('「가져온 곳」 한 줄을 내소재.md 0) 칸에 그대로 옮겨 적습니다.')
print(f'답을 쓰는 파일은 {answer} 하나입니다. mine 안의 내소재.md는 AI가 읽는 사본입니다.')
print('테스트는 mine/tests/ 안에 만들어집니다. 지금은 비어 있어 pytest가 no tests ran 이라고 합니다.')
print('다음: 이 폴더에서 claude를 실행해 내프롬프트.md의 1)을 보냅니다.')
