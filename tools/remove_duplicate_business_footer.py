from pathlib import Path

path = Path('index.html')
html = path.read_text(encoding='utf-8')

old = '''<div class="site-footer">
    ÜbergabeCheck · <a onclick="openImpressum()">Impressum</a> · <a onclick="openDatenschutz()">Datenschutz</a>
</div>
</section><div class="hidden" id="appContent">'''
new = '''</section><div class="hidden" id="appContent">'''

if old not in html:
    raise SystemExit('Duplicate business footer block not found')

html = html.replace(old, new, 1)
path.write_text(html, encoding='utf-8')
print('Removed duplicate Business footer')
