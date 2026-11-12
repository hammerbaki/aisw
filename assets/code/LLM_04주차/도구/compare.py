from pathlib import Path
import json
r=Path(__file__).resolve().parents[1]
print('실행 | 종류 | 완료 | 정확도 | JSON 정상 | 입력 | 출력')
for p in sorted((r/'results').glob('*/summary.json')):
 d=json.loads(p.read_text(encoding='utf-8'));print(p.parent.name,d['kind'],str(d['completed'])+'/'+str(d['count']),d['accuracy'],d['json_valid'],d['input_tokens'],d['output_tokens'],sep=' | ')
print('같은 문항 해시·모델·채점기·완료 상태·실측 종류인지 summary.json을 확인한 뒤 비교합니다.')
