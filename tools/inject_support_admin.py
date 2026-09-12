from pathlib import Path

TAG = '<script src="business-tools.js?v=1"></script>'

for filename in ('index.html', 'app.html'):
    path = Path(filename)
    if not path.exists():
        continue
    html = path.read_text(encoding='utf-8')
    if TAG in html:
        continue
    if '</body>' not in html:
        raise SystemExit(f'No </body> found in {filename}')
    html = html.replace('</body>', f'{TAG}\n</body>', 1)
    path.write_text(html, encoding='utf-8')
    print(f'Injected Support/Admin launcher into {filename}')
