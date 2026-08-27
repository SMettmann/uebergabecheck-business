from pathlib import Path

path = Path('index.html')
html = path.read_text(encoding='utf-8')

old = '''<div class="site-footer">
    ÜbergabeCheck · <a onclick="openImpressum()">Impressum</a> · <a onclick="openDatenschutz()">Datenschutz</a>
</div>'''

if old not in html:
    raise SystemExit('Duplicate dashboard footer not found')

html = html.replace(old, '', 1)
path.write_text(html, encoding='utf-8')
print('Removed duplicate dashboard legal footer')
