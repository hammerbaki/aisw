"""수업 채점기 1.1: 고정 기준, 원문 보존, 재개, 앞뒤 문장부호 제거 후 정확 일치. Python 표준 라이브러리만 사용.
260924: --overwrite 추가(기존 결과 폴더를 results/_이전/ 아래로 옮기고 새로 실행). 채점 규칙은 그대로."""
import argparse,csv,hashlib,json,os,re,sys,time,urllib.request,urllib.error
from pathlib import Path
from datetime import datetime,timezone
VERSION='1.1'
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def extract(answer,labels):
    text=answer.strip();candidate=text.splitlines()[-1] if text else ''
    def obj(s):
        try:
            v=json.loads(s)
            return v['분류'] if isinstance(v,dict) and set(v)=={'분류'} and v['분류'] in labels else None
        except (ValueError,TypeError,KeyError):return None
    full=obj(text);last=obj(candidate)
    # JSON object as the final line is accepted for classification. Whole response JSON is a separate measure.
    if full:return full,True
    if last:return last,False
    # Plain responses must equal a single label after trimming surrounding punctuation/quotes. No substring or guessing.
    plain=text.strip().strip('.。!?,;:"\'`*「」『』“”‘’()（）').strip()
    return (plain if plain in labels else None),False

def dataset(path):
    path=Path(path);lp=path.with_suffix('.labels.txt')
    labels=[s.strip() for s in lp.read_text(encoding='utf-8-sig').splitlines() if s.strip()]
    if len(labels)!=5 or len(set(labels))!=5 or '기타' not in labels:raise ValueError('라벨 파일에는 기타를 포함한 서로 다른 라벨 5개가 필요합니다.')
    with path.open(encoding='utf-8-sig',newline='') as f:
        reader=csv.DictReader(f)
        if reader.fieldnames!=['질문','정답']:raise ValueError('CSV 첫 줄은 질문,정답이어야 합니다.')
        rows=list(reader)
    if not rows:raise ValueError('문항이 없습니다.')
    if len({r.get('질문') for r in rows})!=len(rows):raise ValueError('중복 문항이 있습니다.')
    for i,r in enumerate(rows,1):
        if set(r)!={'질문','정답'} or not r['질문'] or r['정답'] not in labels:raise ValueError(f'{i}번 문항: 쉼표·빈칸·라벨을 확인하세요.')
    if set(r['정답'] for r in rows)!=set(labels):raise ValueError('각 라벨 문항이 최소 1개씩 필요합니다.')
    return rows,labels,lp

def call_api(model,prompt,question):
    payload=json.dumps({'model':model,'max_tokens':300,'system':prompt,'messages':[{'role':'user','content':question}]}).encode()
    req=urllib.request.Request('https://api.anthropic.com/v1/messages',data=payload,headers={'x-api-key':os.environ['ANTHROPIC_API_KEY'],'anthropic-version':'2023-06-01','content-type':'application/json'})
    for attempt in range(6):
        try:
            with urllib.request.urlopen(req,timeout=45) as response: data=json.load(response)
            return ''.join(b.get('text','') for b in data.get('content',[]) if b.get('type')=='text'),data.get('usage',{}),data.get('model',model),data.get('stop_reason')
        except urllib.error.HTTPError as e:
            if e.code in [429,500,502,503,529] and attempt<5:
                ra=e.headers.get('retry-after') if e.headers else None
                wait=float(ra) if ra and ra.replace('.','',1).isdigit() else 2**(attempt+1)
                print(f'  HTTP {e.code}: {min(wait,60):.0f}초 뒤 다시 시도 ({attempt+1}/5)',flush=True);time.sleep(min(wait,60));continue
            raise RuntimeError(f'HTTP {e.code}: 인증·모델 권한·요청 제한을 확인하세요. 원문 오류에 키가 포함될 수 있어 출력하지 않습니다.') from None
        except (urllib.error.URLError,TimeoutError):
            if attempt<5:time.sleep(2**(attempt+1));continue
            raise RuntimeError('네트워크 또는 시간 초과. 저장 결과를 보존하고 --resume으로 이어서 실행하세요.') from None

def main():
    a=argparse.ArgumentParser();a.add_argument('prompt');a.add_argument('csv');a.add_argument('output');a.add_argument('--json',action='store_true');a.add_argument('--resume',action='store_true');a.add_argument('--check',action='store_true');a.add_argument('--overwrite',action='store_true',help='기존 결과 폴더를 results/_이전/ 아래로 옮기고 새로 실행');a.add_argument('--replay',help='교수 참고 응답 JSON 배열. 실제 API 결과가 아님');args=a.parse_args()
    rows,labels,lp=dataset(args.csv);p=Path(args.prompt);prompt=p.read_text(encoding='utf-8-sig').strip()
    if not prompt:raise ValueError('프롬프트가 비었습니다.')
    model=os.environ.get('COURSE_MODEL','claude-haiku-4-5-20251001')
    replay=json.loads(Path(args.replay).read_text(encoding='utf-8-sig')) if args.replay else None
    if replay is not None and (len(replay)!=len(rows) or not all(isinstance(v,str) for v in replay)):raise ValueError('참고 응답은 문항 수와 같은 문자열 배열이어야 합니다.')
    meta={'grader':VERSION,'grader_sha256':sha(__file__),'model':model,'prompt_sha256':sha(p),'csv_sha256':sha(args.csv),'labels_sha256':sha(lp),'json_required':args.json,'count':len(rows),'kind':'참고 응답 재생' if replay is not None else '실제 API','replay_sha256':sha(args.replay) if replay is not None else None}
    if args.check:
        print('CHECK_OK',len(rows),'문항',model,'API_KEY_SET='+str(bool(os.environ.get('ANTHROPIC_API_KEY'))));return
    if replay is None and not os.environ.get('ANTHROPIC_API_KEY'):raise ValueError('API 키 미설정. 키 값을 화면에 출력하지 말고 교수에게 설정 방법을 확인하세요.')
    if args.resume and args.overwrite:raise ValueError('--resume과 --overwrite는 함께 쓸 수 없습니다.')
    out=Path(args.output)
    if out.exists() and args.overwrite:
        backup=out.parent/'_이전'/f"{out.name}_{datetime.now().strftime('%m%d_%H%M%S')}"
        backup.parent.mkdir(parents=True,exist_ok=True);out.rename(backup)
        print(f'기존 결과를 {backup}로 옮겼습니다.')
    records=[]
    if out.exists():
        if not args.resume:raise ValueError('결과 폴더가 있습니다. 다시 실행하려면 --overwrite, 멈춘 실행은 --resume을 붙이세요.')
        if json.loads((out/'metadata.json').read_text(encoding='utf-8'))!=meta:raise ValueError('재개 불가: 모델·프롬프트·문항·채점 기준이 달라졌습니다. 처음부터 다시 하려면 --resume 대신 --overwrite를 붙이세요.')
        records=[json.loads(s) for s in (out/'responses.jsonl').read_text(encoding='utf-8').splitlines()] if (out/'responses.jsonl').exists() else []
        if [r['index'] for r in records]!=list(range(1,len(records)+1)) or len(records)>len(rows):raise ValueError('결과 기록 순서가 잘못되었습니다.')
    else:
        out.mkdir(parents=True);(out/'metadata.json').write_text(json.dumps(meta,ensure_ascii=False,indent=2),encoding='utf-8')
    error=None
    try:
        for i in range(len(records),len(rows)):
            row=rows[i]
            answer,usage,resolved,stop=(replay[i],{},'참고 응답','reference') if replay is not None else call_api(model,prompt,row['질문'])
            label,json_ok=extract(answer,labels)
            record={'index':i+1,'question':row['질문'],'expected':row['정답'],'response':answer,'label':label,'correct':label==row['정답'],'json_valid':json_ok,'usage':usage,'resolved_model':resolved,'stop_reason':stop,'utc':datetime.now(timezone.utc).isoformat()}
            with (out/'responses.jsonl').open('a',encoding='utf-8') as f:f.write(json.dumps(record,ensure_ascii=False)+'\n')
            records.append(record);print(f'{i+1}: {"O" if record["correct"] else "X"} 정답={row["정답"]} 판정={label} JSON={json_ok}')
    except (RuntimeError,KeyboardInterrupt) as e:error=str(e) or '사용자 중단'
    summary={**meta,'completed':len(records),'complete':len(records)==len(rows),'correct':sum(r['correct'] for r in records),'accuracy':round(100*sum(r['correct'] for r in records)/len(rows),2) if len(records)==len(rows) else None,'json_valid':sum(r['json_valid'] for r in records),'input_tokens':sum(r['usage'].get('input_tokens',0) for r in records) if replay is None else None,'output_tokens':sum(r['usage'].get('output_tokens',0) for r in records) if replay is None else None,'error':error}
    (out/'summary.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps(summary,ensure_ascii=False,indent=2))
    if error:raise SystemExit(2)
if __name__=='__main__':
    try:main()
    except (ValueError,OSError,KeyError) as e:print('실행 중단:',e);raise SystemExit(2)
