from pathlib import Path

p=Path('index.html')
s=p.read_text(encoding='utf-8')

def rep(old,new,count=-1):
    global s
    if old not in s:
        raise SystemExit('Anchor not found: '+old[:220])
    s=s.replace(old,new) if count==-1 else s.replace(old,new,count)

# Versioning / evidence
rep('Stand: 26. August 2026 · Version 2026-08-26','Stand: 27. August 2026 · Version 2026-08-27')
rep('nach Art. 28 DSGVO · Stand: 26. August 2026 · Version 2026-08-26','nach Art. 28 DSGVO · Stand: 27. August 2026 · Version 2026-08-27')
rep('<p><strong>Stand: 26. August 2026</strong></p>','<p><strong>Stand: 27. August 2026</strong></p>')
rep('const BUSINESS_TERMS_VERSION="2026-08-26";','const BUSINESS_TERMS_VERSION="2026-08-27";')
rep('const BUSINESS_AVV_VERSION="2026-08-26";','const BUSINESS_AVV_VERSION="2026-08-27";')

# Clear authority to bind the company
rep(
'Ich bestätige, dass ich als <strong>Unternehmer im Sinne des § 14 BGB</strong> handle und ÜbergabeCheck Business ausschließlich für meine gewerbliche oder selbständige berufliche Tätigkeit nutze.',
'Ich bestätige, dass ich als <strong>Unternehmer im Sinne des § 14 BGB</strong> handle, ÜbergabeCheck Business ausschließlich für meine gewerbliche oder selbständige berufliche Tätigkeit nutze und <strong>berechtigt bin, diese Vereinbarungen für das Unternehmen abzuschließen</strong>.'
)
rep(
'Ich bestätige, dass ich als <strong>Unternehmer im Sinne des § 14 BGB</strong> handle.</span>',
'Ich bestätige, dass ich als <strong>Unternehmer im Sinne des § 14 BGB</strong> handle und <strong>berechtigt bin, diese Vereinbarungen für das Unternehmen abzuschließen</strong>.</span>'
)
rep('Bitte bestätige Unternehmerstatus, AGB und AVV.','Bitte bestätige Unternehmerstatus, Vertretungsbefugnis, AGB und AVV.')

# Current small-business invoice wording under the post-2025 rules
rep(
'<p>Der Business-Tarif kostet derzeit 29,99 € pro Monat. Maßgeblich ist der im Buchungsprozess ausgewiesene Preis. Soweit aufgrund der Kleinunternehmerregelung nach § 19 UStG keine Umsatzsteuer erhoben wird, wird dies auf der Rechnung entsprechend ausgewiesen.</p>',
'<p>Der Business-Tarif kostet derzeit 29,99 € pro Monat. Maßgeblich ist der im Buchungsprozess ausgewiesene Preis. Solange die Umsätze des Anbieters unter die Steuerbefreiung für Kleinunternehmer nach § 19 UStG fallen, wird keine Umsatzsteuer berechnet; die Rechnung enthält einen entsprechenden Hinweis auf die Steuerbefreiung.</p>'
)

# Customer data minimisation / Art. 9 guardrail
rep(
'<li>Der Kunde ist für die Information betroffener Personen und die Erfüllung eigener datenschutzrechtlicher Pflichten verantwortlich.</li><li>Rechtswidrige Inhalte, Schadsoftware sowie eine missbräuchliche oder sicherheitsgefährdende Nutzung sind untersagt.</li>',
'<li>Der Kunde ist für die Information betroffener Personen und die Erfüllung eigener datenschutzrechtlicher Pflichten verantwortlich.</li><li>Besondere Kategorien personenbezogener Daten im Sinne des Art. 9 DSGVO sind nicht für die reguläre Nutzung vorgesehen. Soweit der Kunde solche Daten dennoch verarbeitet, ist er für eine tragfähige Rechtsgrundlage, Datenminimierung und erforderliche Schutzmaßnahmen verantwortlich.</li><li>Rechtswidrige Inhalte, Schadsoftware sowie eine missbräuchliche oder sicherheitsgefährdende Nutzung sind untersagt.</li>'
)

# Align paid subscription end with account/AVV lifecycle
rep(
'<p>Nach Ende eines kostenpflichtigen Abonnements können gespeicherte Daten zunächst im lesenden Zugriff verbleiben. Der Kunde ist dafür verantwortlich, benötigte Protokolle und Unterlagen rechtzeitig zu exportieren. ÜbergabeCheck kann dauerhaft inaktive Unternehmenskonten und deren Inhaltsdaten frühestens sechs Monate nach Ende des kostenpflichtigen Abonnements löschen, wenn die im Konto hinterlegte geschäftliche E-Mail-Adresse mindestens 30 Tage vorher informiert wurde. Gesetzliche Aufbewahrungspflichten, insbesondere für Abrechnungsdaten, bleiben unberührt.</p>',
'<p>Die Beendigung des kostenpflichtigen Abonnements beendet nicht automatisch das Unternehmenskonto. Gespeicherte Daten können zunächst im lesenden Zugriff verbleiben; solange ÜbergabeCheck diese Inhaltsdaten für den Kunden bereitstellt, gilt der AVV fort. Der Kunde kann die Löschung seines Unternehmenskontos und der Inhaltsdaten verlangen und ist dafür verantwortlich, benötigte Protokolle zuvor zu exportieren. ÜbergabeCheck kann dauerhaft inaktive Unternehmenskonten und deren Inhaltsdaten frühestens sechs Monate nach Ende des kostenpflichtigen Abonnements löschen, wenn die im Konto hinterlegte geschäftliche E-Mail-Adresse mindestens 30 Tage vorher informiert wurde. Gesetzliche Aufbewahrungspflichten, insbesondere für Abrechnungsdaten, bleiben unberührt.</p>'
)

# AVV: special categories and clearer subprocessor chain
rep(
'<li>sonstige vom Kunden freiwillig in Freitextfeldern hinterlegte personenbezogene Angaben</li></ul>\n<h3>4. Kategorien betroffener Personen</h3>',
'<li>sonstige vom Kunden freiwillig in Freitextfeldern hinterlegte personenbezogene Angaben</li></ul>\n<p>Besondere Kategorien personenbezogener Daten nach Art. 9 DSGVO sind nicht Gegenstand der vorgesehenen Standardverarbeitung. Werden solche Daten durch den Kunden dennoch eingegeben, erfolgt dies ausschließlich auf dessen Weisung und Verantwortung für die hierfür erforderliche Rechtsgrundlage und Schutzmaßnahmen.</p>\n<h3>4. Kategorien betroffener Personen</h3>'
)
old_sub='''<h3>8. Unterauftragsverarbeiter</h3>\n<p>Der Kunde erteilt eine allgemeine Genehmigung zum Einsatz der nachfolgend aufgeführten Unterauftragsverarbeiter, soweit diese personenbezogene Daten im Rahmen der Auftragsverarbeitung verarbeiten:</p>\n<ul><li><strong>Supabase</strong> – Backend, Authentifizierung und Datenbank; für das ÜbergabeCheck-Business-Projekt ist eine EU-Projektregion (Frankfurt) eingerichtet.</li><li><strong>STRATO AG</strong> – Hosting und Auslieferung der Webanwendung sowie technisch erforderliche Server-/Verbindungsprotokolle.</li></ul>\n<p>Beabsichtigte wesentliche Änderungen bei Unterauftragsverarbeitern werden dem Kunden in geeigneter Form, insbesondere per E-Mail oder innerhalb der Anwendung, angekündigt. Der Kunde kann aus berechtigten datenschutzrechtlichen Gründen widersprechen. Ist keine zumutbare Alternative möglich, kann das Vertragsverhältnis hinsichtlich der betroffenen Leistung beendet werden.</p>'''
new_sub='''<h3>8. Unterauftragsverarbeiter</h3>\n<p>Der Kunde erteilt eine allgemeine Genehmigung zum Einsatz der nachfolgend aufgeführten Unterauftragsverarbeiter, soweit diese personenbezogene Daten im Rahmen der Auftragsverarbeitung verarbeiten:</p>\n<ul><li><strong>Supabase, Inc. (USA)</strong> – Backend, Authentifizierung, Datenbank und Edge Functions. Die primären Projektdaten von ÜbergabeCheck Business werden in der ausgewählten Region <strong>eu-central-1 (Frankfurt)</strong> gespeichert. Supabase setzt im Rahmen seines Data Processing Addendum weitere Unterauftragsverarbeiter ein, insbesondere Infrastruktur- und Sicherheitsdienstleister. Soweit Drittlandtransfers stattfinden, gelten die im Supabase-DPA vorgesehenen Übermittlungsmechanismen und Garantien.</li><li><strong>STRATO GmbH, Pascalstraße 10, 10587 Berlin</strong> – Hosting und Auslieferung der Webanwendung sowie technisch erforderliche Server-/Verbindungsprotokolle; die von STRATO hierfür eingesetzte Datenverarbeitung erfolgt nach den für das Hosting geltenden Vereinbarungen zur Auftragsverarbeitung.</li></ul>\n<p>Eine aktuelle Information über die eingesetzte Verarbeitungskette und die einschlägigen Anbieterunterlagen kann unter info@uebergabe-check.de angefordert werden. Beabsichtigte wesentliche Änderungen bei Unterauftragsverarbeitern werden dem Kunden in geeigneter Form, insbesondere per E-Mail oder innerhalb der Anwendung, vor ihrem Einsatz angekündigt. Der Kunde erhält Gelegenheit, aus berechtigten datenschutzrechtlichen Gründen zu widersprechen. Ist keine zumutbare Alternative möglich, kann das Vertragsverhältnis hinsichtlich der betroffenen Leistung beendet werden.</p>'''
rep(old_sub,new_sub)

# AVV deletion: backups where applicable
rep(
'<p>Nach Ende der Auftragsverarbeitung werden personenbezogene Inhaltsdaten nach Wahl des Kunden gelöscht oder – soweit technisch vorgesehen – zur Verfügung gestellt, sofern keine gesetzliche Pflicht zur weiteren Speicherung besteht. Der Kunde kann die Löschung seines Unternehmenskontos und seiner Inhaltsdaten verlangen. Die Regelungen zu inaktiven Konten in den AGB bleiben ergänzend anwendbar.</p>',
'<p>Nach Ende der Auftragsverarbeitung werden personenbezogene Inhaltsdaten nach Wahl des Kunden gelöscht oder – soweit technisch vorgesehen – zur Verfügung gestellt, sofern keine gesetzliche Pflicht zur weiteren Speicherung besteht. Der Kunde kann die Löschung seines Unternehmenskontos und seiner Inhaltsdaten verlangen. Sicherungskopien, soweit vorhanden, werden bis zu ihrer regulären Überschreibung für die produktive Nutzung gesperrt und anschließend gelöscht. Die Regelungen zu inaktiven Konten in den AGB bleiben ergänzend anwendbar.</p>'
)

# Privacy: evidence, necessary local storage, provider details and external CDNs
rep(
'Bei Registrierung und Nutzung verarbeiten wir insbesondere Unternehmensname, Ansprechpartner, geschäftliche E-Mail-Adresse, Authentifizierungsdaten, Kontozuordnung, Tarifstatus und rechtliche Zustimmungen. Die Verarbeitung ist für die Bereitstellung des Dienstes und die Durchführung des Vertrags erforderlich. Rechtsgrundlagen sind je nach Einzelfall Art. 6 Abs. 1 lit. b DSGVO sowie Art. 6 Abs. 1 lit. f DSGVO, insbesondere für sicheren Betrieb, Missbrauchsschutz und die Verwaltung von Unternehmenskonten.',
'Bei Registrierung und Nutzung verarbeiten wir insbesondere Unternehmensname, Ansprechpartner, geschäftliche E-Mail-Adresse, Authentifizierungsdaten, Kontozuordnung, Tarifstatus und rechtliche Zustimmungen. Die Verarbeitung ist für die Bereitstellung des Dienstes und die Durchführung des Vertrags erforderlich. Rechtsgrundlagen sind je nach Einzelfall Art. 6 Abs. 1 lit. b DSGVO sowie Art. 6 Abs. 1 lit. f DSGVO, insbesondere für sicheren Betrieb, Missbrauchsschutz und die Verwaltung von Unternehmenskonten. Die versionierte Protokollierung von B2B-, AGB- und AVV-Bestätigungen dient dem Nachweis des Vertragsschlusses und der Rechenschaftspflichten und erfolgt auf Grundlage unserer gesetzlichen Pflichten sowie unseres berechtigten Interesses an einer belastbaren Vertragsdokumentation.'
)
rep(
'<p>Die Anwendung kann technisch notwendige Browser-Speichermechanismen einsetzen, insbesondere um Anmeldesitzungen und vorübergehende Entwürfe zu verwalten. Diese Funktionen dienen dem Betrieb der Anwendung und werden nicht für werbliche Profilbildung eingesetzt.</p>',
'<p>Die Anwendung setzt technisch notwendige Browser-Speichermechanismen ein, insbesondere um Anmeldesitzungen und vorübergehende Entwürfe zu verwalten. Diese Speicherung bzw. der Zugriff ist für die vom Nutzer ausdrücklich gewünschte Business-Anwendung erforderlich und dient nicht der werblichen Profilbildung. Soweit § 25 TDDDG anwendbar ist, stützen wir diese technisch notwendigen Vorgänge auf § 25 Abs. 2 Nr. 2 TDDDG.</p>'
)
rep(
'<p>Für Authentifizierung, Kontozuordnung, Datenbank und zentrale Speicherung verwenden wir Supabase. Dabei werden je nach Nutzung Konto- und Anmeldedaten sowie die vom Unternehmenskunden gespeicherten Business-Inhalte verarbeitet. Das ÜbergabeCheck-Business-Projekt ist in einer EU-Projektregion (Frankfurt) eingerichtet.</p>',
'<p>Für Authentifizierung, Kontozuordnung, Datenbank, Edge Functions und zentrale Speicherung verwenden wir <strong>Supabase, Inc.</strong>. Dabei werden je nach Nutzung Konto- und Anmeldedaten sowie die vom Unternehmenskunden gespeicherten Business-Inhalte verarbeitet. Die primären Projektdaten von ÜbergabeCheck Business werden in <strong>eu-central-1 (Frankfurt)</strong> gespeichert. Supabase kann für einzelne Leistungen weitere Unterauftragsverarbeiter einsetzen; Drittlandtransfers werden nach Maßgabe des mit Supabase geltenden Data Processing Addendum und der dort vorgesehenen Garantien abgesichert.</p>'
)
rep(
'<p>Zur Auswertung und Verbesserung der Anwendung verwenden wir Umami Cloud. Erfasst werden technische Nutzungsinformationen wie Seitenaufrufe, Referrer, Browser, Betriebssystem, Gerätetyp und Herkunftsland sowie ausgewählte Nutzungsereignisse. Inhalte von Übergabeprotokollen, Namen, Adressen, Fotos und Unterschriften werden nicht als Analyseereignisse an Umami übermittelt. Die Analyse dient unserem berechtigten Interesse an der technischen und wirtschaftlichen Verbesserung des Dienstes gemäß Art. 6 Abs. 1 lit. f DSGVO.</p>',
'<p>Zur Auswertung und Verbesserung der Anwendung verwenden wir <strong>Umami Cloud</strong>. Erfasst werden technische, nach Anbieterangaben anonymisierte Nutzungsinformationen wie Seitenaufrufe, Referrer, Browser, Betriebssystem, Gerätetyp und Herkunftsland sowie ausgewählte Nutzungsereignisse. Umami verwendet im Tracking-Code nach Anbieterangaben keine Cookies und kein websiteübergreifendes Tracking. Inhalte von Übergabeprotokollen, Namen, Adressen, Fotos und Unterschriften werden nicht als Analyseereignisse an Umami übermittelt. Die Analyse dient unserem berechtigten Interesse an der technischen und wirtschaftlichen Verbesserung des Dienstes gemäß Art. 6 Abs. 1 lit. f DSGVO.</p>'
)
# Renumber existing sections first, then insert CDN section
for old,new in [
('<h3>9. Hosting durch STRATO</h3>','<h3>10. Hosting durch STRATO</h3>'),
('<h3>10. E-Mails und Benachrichtigungen</h3>','<h3>11. E-Mails und Benachrichtigungen</h3>'),
('<h3>11. Empfänger und Drittstaaten</h3>','<h3>12. Empfänger und Drittstaaten</h3>'),
('<h3>12. Speicherdauer</h3>','<h3>13. Speicherdauer</h3>'),
('<h3>13. Pflicht zur Bereitstellung</h3>','<h3>14. Pflicht zur Bereitstellung</h3>'),
('<h3>14. Rechte betroffener Personen</h3>','<h3>15. Rechte betroffener Personen</h3>'),
('<h3>15. Beschwerderecht</h3>','<h3>16. Beschwerderecht</h3>'),
('<h3>16. Änderungen</h3>','<h3>17. Änderungen</h3>')]: rep(old,new)
rep(
'<h3>10. Hosting durch STRATO</h3>',
'<h3>9. Externe Bibliotheken und Content-Delivery-Netzwerke</h3>\n<p>Für die Bereitstellung einzelner technischer JavaScript-Bibliotheken nutzt die Business-Anwendung derzeit <strong>jsDelivr</strong> (Supabase-Client) und beim PDF-Export <strong>cdnjs/Cloudflare</strong> (jsPDF). Beim Abruf dieser Dateien wird technisch bedingt insbesondere die IP-Adresse des verwendeten Anschlusses an den jeweiligen CDN-Anbieter übertragen. Die Einbindung dient unserem berechtigten Interesse an einer sicheren und effizienten Bereitstellung der benötigten Programmkomponenten gemäß Art. 6 Abs. 1 lit. f DSGVO. Soweit dabei Drittlandtransfers stattfinden, gelten die jeweiligen gesetzlichen Übermittlungsmechanismen und Garantien.</p>\n<h3>10. Hosting durch STRATO</h3>'
)
rep(
'<p>Die Webanwendung wird über STRATO bereitgestellt. Beim Aufruf können technisch notwendige Verbindungsdaten wie IP-Adresse, Zeitpunkt, aufgerufene Ressource sowie Browser- und Geräteinformationen in Serverprotokollen verarbeitet werden. Dies dient der sicheren und zuverlässigen Bereitstellung des Dienstes auf Grundlage von Art. 6 Abs. 1 lit. f DSGVO.</p>',
'<p>Die Webanwendung wird über die <strong>STRATO GmbH</strong> bereitgestellt. Beim Aufruf können technisch notwendige Verbindungsdaten wie IP-Adresse, Zeitpunkt, aufgerufene Ressource sowie Browser- und Geräteinformationen in Serverprotokollen verarbeitet werden. Dies dient der sicheren und zuverlässigen Bereitstellung des Dienstes auf Grundlage von Art. 6 Abs. 1 lit. f DSGVO.</p>'
)
rep(
'<p>Daten werden nur an Dienstleister und Empfänger übermittelt, soweit dies für Betrieb, Sicherheit, Vertrag, Zahlung oder gesetzliche Pflichten erforderlich ist. Soweit ein eingesetzter Dienstleister Daten außerhalb des Europäischen Wirtschaftsraums verarbeitet oder Zugriffsmöglichkeiten aus Drittstaaten bestehen, werden – soweit erforderlich – geeignete Garantien nach Kapitel V DSGVO zugrunde gelegt.</p>',
'<p>Daten werden nur an Dienstleister und Empfänger übermittelt, soweit dies für Betrieb, Sicherheit, Vertrag, Zahlung oder gesetzliche Pflichten erforderlich ist. Hierzu zählen insbesondere Supabase, STRATO, Stripe, Umami Cloud sowie die genannten CDN-Anbieter. Soweit personenbezogene Daten in ein Drittland übermittelt werden, wird – abhängig vom jeweiligen Anbieter – insbesondere auf einen Angemessenheitsbeschluss wie das EU-U.S. Data Privacy Framework oder auf Standardvertragsklauseln nach Art. 46 DSGVO und ergänzende Schutzmaßnahmen zurückgegriffen. Informationen zu den konkret einschlägigen Garantien oder eine Bezugsquelle können unter info@uebergabe-check.de angefragt werden.</p>'
)

# Frontend legal evidence schema
rep(
'return !!(businessLegalAcceptance && businessLegalAcceptance.b2b_confirmed===true && businessLegalAcceptance.terms_version===BUSINESS_TERMS_VERSION && businessLegalAcceptance.avv_version===BUSINESS_AVV_VERSION);',
'return !!(businessLegalAcceptance && businessLegalAcceptance.b2b_confirmed===true && businessLegalAcceptance.authorized_to_bind===true && businessLegalAcceptance.terms_version===BUSINESS_TERMS_VERSION && businessLegalAcceptance.avv_version===BUSINESS_AVV_VERSION);'
)
rep(
'.select("company_id,user_id,terms_version,avv_version,b2b_confirmed,source,accepted_at")',
'.select("company_id,user_id,terms_version,avv_version,b2b_confirmed,authorized_to_bind,source,accepted_at")'
)
rep(
'{body:{b2bConfirmed:true,termsAccepted:true,avvAccepted:true,source}}',
'{body:{b2bConfirmed:true,termsAccepted:true,avvAccepted:true,authorizedToBind:true,source}}'
)
rep(
'if(m.b2b_confirmed===true && m.legal_terms_version===BUSINESS_TERMS_VERSION && m.avv_version===BUSINESS_AVV_VERSION){',
'if(m.b2b_confirmed===true && m.authorized_to_bind===true && m.legal_terms_version===BUSINESS_TERMS_VERSION && m.avv_version===BUSINESS_AVV_VERSION){'
)
rep(
'        b2b_confirmed: true,\n        legal_terms_version: BUSINESS_TERMS_VERSION,',
'        b2b_confirmed: true,\n        authorized_to_bind: true,\n        legal_terms_version: BUSINESS_TERMS_VERSION,'
)

p.write_text(s,encoding='utf-8')
