"""唯一复现入口：校验冻结、运行既有Pipeline、评价本次输出；保留首次报告。"""
import argparse
import subprocess
import sys
from pathlib import Path
from evaluate import verify, evaluate
ROOT=Path(__file__).resolve().parents[2]
def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--verify-only',action='store_true',help='只检查冻结数据，不执行模型')
    args=p.parse_args()
    verify()
    if args.verify_only:
        print('冻结校验通过；未运行模型。'); return 0
    folder=ROOT/'week07/runs'
    previous=set(folder.glob('baseline-*'))
    result=subprocess.run([sys.executable,str(ROOT/'week06/scripts/run_pipeline.py'),'--config',str(ROOT/'week07/configs/baseline.json')],cwd=ROOT)
    created=set(folder.glob('baseline-*'))-previous
    if len(created)!=1:
        print('没有唯一新运行目录；保留日志，停止自动评测。',file=sys.stderr); return 2
    run=created.pop()
    # A completed batch can contain failed conversions; evaluator retains all 24 pages.
    try:
        evaluate(run)
    except (OSError,ValueError,KeyError) as error:
        print(f'评测拒绝：{error}',file=sys.stderr); return 2
    print(f'本次指标：{run / "evaluation.json"}；首次人工报告与收尾清单未覆盖。')
    return result.returncode
if __name__=='__main__': raise SystemExit(main())
