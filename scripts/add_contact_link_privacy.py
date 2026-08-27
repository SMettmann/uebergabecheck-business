from pathlib import Path

p=Path('index.html')
s=p.read_text(encoding='utf-8')

def rep(old,new,count=1):
    global s
    if old not in s:
        raise SystemExit('Anchor not found: '+old[:180])
    s=s.replace(old,new,count)

# Impressum gets a second direct communication channel via the public contact form.
rep('''<h3>Kontakt</h3>
<p>
      E-Mail: info@uebergabe-check.de
    </p>''','''<h3>Kontakt</h3>
<p>
      E-Mail: <a href="mailto:info@uebergabe-check.de">info@uebergabe-check.de</a><br/>
      Kontaktformular: <a href="/business/#kontakt">direkt online schreiben</a>
    </p>''')

# Add contact form processing to the Business privacy notice and renumber following headings.
anchor='''<h3>11. E-Mails und Benachrichtigungen</h3>
<p>Im Zusammenhang mit Registrierung, Passwort-Wiederherstellung, Zahlung, Rechnung und Abonnement können technisch oder vertraglich erforderliche E-Mails durch die jeweils eingesetzten Dienste, insbesondere Supabase und Stripe, versendet werden.</p>'''
new='''<h3>11. Kontaktformular</h3>
<p>Auf der öffentlichen Business-Seite steht ein Kontaktformular zur Verfügung. Wenn es genutzt wird, verarbeiten wir Name, E-Mail-Adresse, optional das Unternehmen und den Inhalt der Nachricht, um die Anfrage zu bearbeiten und zu beantworten. Die Verarbeitung erfolgt je nach Inhalt zur Durchführung vorvertraglicher oder vertraglicher Maßnahmen gemäß Art. 6 Abs. 1 lit. b DSGVO oder auf Grundlage unseres berechtigten Interesses an der Bearbeitung geschäftlicher Anfragen gemäß Art. 6 Abs. 1 lit. f DSGVO. Die technische E-Mail-Übermittlung erfolgt über den hierfür eingesetzten E-Mail-Dienst. Anfragen werden nur so lange gespeichert, wie dies für Bearbeitung, Nachweis und gegebenenfalls gesetzliche Aufbewahrungspflichten erforderlich ist.</p>
<h3>12. E-Mails und Benachrichtigungen</h3>
<p>Im Zusammenhang mit Registrierung, Passwort-Wiederherstellung, Zahlung, Rechnung und Abonnement können technisch oder vertraglich erforderliche E-Mails durch die jeweils eingesetzten Dienste, insbesondere Supabase und Stripe, versendet werden.</p>'''
rep(anchor,new)
for old,newh in [
('<h3>12. Empfänger und Drittstaaten</h3>','<h3>13. Empfänger und Drittstaaten</h3>'),
('<h3>13. Speicherdauer</h3>','<h3>14. Speicherdauer</h3>'),
('<h3>14. Pflicht zur Bereitstellung</h3>','<h3>15. Pflicht zur Bereitstellung</h3>'),
('<h3>15. Rechte betroffener Personen</h3>','<h3>16. Rechte betroffener Personen</h3>'),
('<h3>16. Beschwerderecht</h3>','<h3>17. Beschwerderecht</h3>'),
('<h3>17. Änderungen</h3>','<h3>18. Änderungen</h3>')
]:
    if old in s:
        s=s.replace(old,newh,1)

# If the old final headings were still 15/16 (depending on prior version), normalize them safely.
s=s.replace('<h3>15. Beschwerderecht</h3>','<h3>17. Beschwerderecht</h3>',1)
s=s.replace('<h3>16. Änderungen</h3>','<h3>18. Änderungen</h3>',1)

p.write_text(s,encoding='utf-8')
