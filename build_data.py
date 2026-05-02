import json, os, shutil
from pathlib import Path
from datetime import datetime, timezone

ROOT = Path.cwd()
CONTENT_ROOT = Path(os.environ.get('IMAGINARIUM_CONTENT_ROOT', ROOT)).resolve()
RULES_DIR = CONTENT_ROOT / 'rules'
DATA_DIR = ROOT / 'data'
PUBLIC_CONTENT = ROOT / 'public' / 'content'
IMAGE_EXT = {'.png','.jpg','.jpeg','.webp','.gif','.svg'}

DATA_DIR.mkdir(parents=True, exist_ok=True)
PUBLIC_CONTENT.mkdir(parents=True, exist_ok=True)

def label_from_file(name:str)->str:
    stem = Path(name).stem.replace('_',' ').replace('-',' ')
    return ' '.join(w.capitalize() for w in stem.split())

rules_lines = []
if RULES_DIR.exists():
    for f in sorted([p for p in RULES_DIR.iterdir() if p.is_file()]):
        txt=' '.join([ln.strip() for ln in f.read_text(encoding='utf-8', errors='ignore').splitlines() if ln.strip()])
        rules_lines.append(f'- **{f.name}**: {txt}')
else:
    rules_lines.append('- No se encontró carpeta `rules/` en la ruta de contenido.')
rules_summary='\n'.join(rules_lines) if rules_lines else '- Sin reglas detectadas.'

categories=[]
for d in sorted([p for p in CONTENT_ROOT.iterdir() if p.is_dir() and p.name!='rules' and not p.name.startswith('.')], key=lambda x:x.name.lower()):
    rec=d/'recortadas'
    if not rec.exists() or not rec.is_dir():
        continue
    files=sorted([p for p in rec.iterdir() if p.is_file() and p.suffix.lower() in IMAGE_EXT], key=lambda x:x.name.lower())
    if not files:
        continue
    slug='-'.join(''.join(c.lower() if c.isalnum() else ' ' for c in d.name).split())
    out=PUBLIC_CONTENT/slug
    out.mkdir(parents=True, exist_ok=True)
    images=[]
    for f in files:
        shutil.copy2(f, out/f.name)
        images.append({'file':f.name,'label':label_from_file(f.name),'url':f'/content/{slug}/{f.name}'})
    categories.append({'category':d.name,'slug':slug,'images':images})

manifest={
    'generatedAt': datetime.now(timezone.utc).isoformat(),
    'contentRoot': str(CONTENT_ROOT),
    'title': "Mr TeacherDan's Imaginarium machine",
    'footer': 'Contenido registrado por "Dan M. Mecikovsky"',
    'rulesSummary': rules_summary,
    'categories': categories,
}
(ROOT/'data'/'manifest.json').write_text(json.dumps(manifest,indent=2,ensure_ascii=False),encoding='utf-8')

readme=f"""# Mr TeacherDan's Imaginarium machine

## Resumen de reglas
{rules_summary}

## Categorías detectadas automáticamente
"""
if categories:
    readme+='\n'.join([f"- {c['category']}: {len(c['images'])} imágenes" for c in categories])
else:
    readme+='- No se encontraron categorías con subcarpeta `recortadas`.'
readme+="""

## Ejecución local
1. (Opcional) exportar `IMAGINARIUM_CONTENT_ROOT` con la carpeta del contenido.
2. `python3 build_data.py`
3. `python3 server.py`
4. Abrir `http://localhost:3000`
"""
(ROOT/'README.md').write_text(readme,encoding='utf-8')
print(f'Manifest generado con {len(categories)} categorías')
