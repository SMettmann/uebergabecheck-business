from pathlib import Path
import re

path = Path('index.html')
html = path.read_text(encoding='utf-8')

pattern = re.compile(
    r'<div class="site-footer">\s*'
    r'ÜbergabeCheck\s*·\s*'
    r'<a onclick="openImpressum\(\)">Impressum</a>\s*·\s*'
    r'<a onclick="openDatenschutz\(\)">Datenschutz</a>\s*'
    r'</div>',
    re.S,
)

html, count = pattern.subn('', html, count=1)
if count != 1:
    raise SystemExit(f'Duplicate dashboard footer matches: {count}')

path.write_text(html, encoding='utf-8')
print('Removed duplicate dashboard legal footer')
