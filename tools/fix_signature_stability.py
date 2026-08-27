from pathlib import Path

path = Path('index.html')
html = path.read_text(encoding='utf-8')

old_setup = '''  const ctx=c.getContext("2d");
  const ratio=window.devicePixelRatio||1;
  const rect=c.getBoundingClientRect();
  c.width=Math.max(560, Math.round(rect.width*ratio));
  c.height=Math.max(180, Math.round(rect.height*ratio));
  ctx.scale(c.width/560,c.height/180);'''
new_setup = '''  const ctx=c.getContext("2d");
  // Feste interne Auflösung: verhindert kumulatives Skalieren/Verschieben
  // beim Speichern, erneuten Öffnen und auf Geräten mit anderer Pixeldichte.
  c.width=1120;
  c.height=360;
  ctx.setTransform(2,0,0,2,0,0);'''

old_restore = '''  const ctx=canvas.getContext("2d");
  const img=new Image();
  img.onload=()=>{
    ctx.clearRect(0,0,canvas.width,canvas.height);
    ctx.drawImage(img,0,0,canvas.width,canvas.height);
  };
  img.src=dataUrl;'''
new_restore = '''  const ctx=canvas.getContext("2d");
  const img=new Image();
  img.onload=()=>{
    // Das Bild muss in echten Canvas-Pixeln wiederhergestellt werden.
    // Der Zeichen-Kontext ist für die Eingabe 2x skaliert; ohne Reset
    // würde die gespeicherte Unterschrift bei jedem Öffnen erneut skaliert.
    ctx.save();
    ctx.setTransform(1,0,0,1,0,0);
    ctx.clearRect(0,0,canvas.width,canvas.height);
    ctx.drawImage(img,0,0,canvas.width,canvas.height);
    ctx.restore();
  };
  img.src=dataUrl;'''

changed = False
if old_setup in html:
    html = html.replace(old_setup, new_setup, 1)
    changed = True
elif 'c.width=1120;' not in html or 'ctx.setTransform(2,0,0,2,0,0);' not in html:
    raise SystemExit('Signature setup block not found and stable setup not present')

if old_restore in html:
    html = html.replace(old_restore, new_restore, 1)
    changed = True
elif 'ctx.setTransform(1,0,0,1,0,0);' not in html:
    raise SystemExit('Signature restore block not found and stable restore not present')

if 'c.width=1120;' not in html:
    raise SystemExit('Stable signature width missing')
if 'c.height=360;' not in html:
    raise SystemExit('Stable signature height missing')
if 'ctx.setTransform(2,0,0,2,0,0);' not in html:
    raise SystemExit('Stable drawing transform missing')
if 'ctx.setTransform(1,0,0,1,0,0);' not in html:
    raise SystemExit('Identity restore transform missing')

if changed:
    path.write_text(html, encoding='utf-8')
    print('Signature stability fix applied to index.html')
else:
    print('Signature stability fix already present')
