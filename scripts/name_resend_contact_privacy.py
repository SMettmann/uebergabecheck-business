from pathlib import Path
p=Path('index.html')
s=p.read_text(encoding='utf-8')
old='Die technische E-Mail-Übermittlung erfolgt über den hierfür eingesetzten E-Mail-Dienst.'
new='Für die technische Übermittlung der Kontaktanfrage nutzen wir <strong>Resend (Plus Five Five, Inc., USA)</strong>. Für Übermittlungen in die USA stützt Resend seine Datenschutzunterlagen unter anderem auf das EU-U.S. Data Privacy Framework und Standardvertragsklauseln.'
if old not in s: raise SystemExit('privacy anchor not found')
s=s.replace(old,new,1)
s=s.replace('Supabase, STRATO, Stripe, Umami Cloud sowie die genannten CDN-Anbieter','Supabase, STRATO, Stripe, Resend, Umami Cloud sowie die genannten CDN-Anbieter',1)
p.write_text(s,encoding='utf-8')
