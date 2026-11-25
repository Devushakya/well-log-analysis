"""Apply portable paths to the upstream notebooks in a local fork."""
import json
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
PREFIX = 'C:/Users/user/Desktop/SK/Data Science/Personal Projects/Well-Log-Analysis/'
BOOTSTRAP = '''from pathlib import Path
PROJECT_ROOT = next((p for p in (Path.cwd(), *Path.cwd().parents)
                     if (p / "notebooks").is_dir()), None)
if PROJECT_ROOT is None:
    raise RuntimeError("Start Jupyter from the repository root or notebooks folder.")
for folder in ("data/raw", "data/processed", "outputs/figures", "outputs/models"):
    (PROJECT_ROOT / folder).mkdir(parents=True, exist_ok=True)
'''

def main():
    files = sorted((ROOT / 'notebooks').glob('*.ipynb'))
    if not files:
        raise SystemExit('Copy this kit .')
    for file in files:
        nb = json.loads(file.read_text(encoding='utf-8'))
        changed = False
        for cell in nb['cells']:
            if cell['cell_type'] != 'code':
                continue
            source = ''.join(cell['source'])
            updated = re.sub(r'"' + re.escape(PREFIX) + r'([^"]+)"',
                             lambda m: 'str(PROJECT_ROOT / ' + repr(m[1]) + ')', source)
            if updated != source:
                cell['source'] = updated.splitlines(keepends=True)
                changed = True
        if changed:
            nb['cells'].insert(0, {'cell_type':'code','execution_count':None,'metadata':{},'outputs':[], 'source':BOOTSTRAP.splitlines(keepends=True)})
            file.write_text(json.dumps(nb, ensure_ascii=False, indent=1)+'\n', encoding='utf-8')
        print(file.name, 'updated' if changed else 'unchanged')
    for name in ('data/raw','data/processed','outputs/models'):
        (ROOT/name).mkdir(parents=True, exist_ok=True)

if __name__ == '__main__':
    main()
