from pathlib import Path

TAG = '<script>document.write(\'<script src="business-tools.js?v=\'+Date.now()+\'"><\\/script>\');</script>'
LEGACY_TAG = '<script src="business-tools.js?v=1"></script>'

for filename in ('index.html', 'app.html'):
    path = Path(filename)
    if not path.exists():
        continue
    html = path.read_text(encoding='utf-8')
    # Remove the old fixed-version loader so phones and PCs cannot run different cached JS.
    html = html.replace(LEGACY_TAG, '')
    if TAG in html:
        path.write_text(html, encoding='utf-8')
        continue
    if '</body>' not in html:
        raise SystemExit(f'No </body> found in {filename}')
    html = html.replace('</body>', f'{TAG}\n</body>', 1)
    path.write_text(html, encoding='utf-8')
    print(f'Injected cache-safe Support/Admin launcher into {filename}')
