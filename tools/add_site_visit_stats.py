from pathlib import Path

PATH = Path("admin.html")
MARKER = "UEBERGABECHECK_SITE_VISIT_STATS_V1"
text = PATH.read_text(encoding="utf-8")

if MARKER not in text:
    block = '''  <!-- UEBERGABECHECK_SITE_VISIT_STATS_V1 -->
  <div class="section-label"><h2>Website-Besucher</h2><span>Anonym gezählte Besuche pro Browser-Sitzung</span></div>
  <div class="kpis">
    <div class="kpi business"><span>Besucher gesamt</span><strong id="kpiVisitsTotal">–</strong></div>
    <div class="kpi business active"><span>Heute</span><strong id="kpiVisitsToday">–</strong></div>
    <div class="kpi business"><span>Letzte 7 Tage</span><strong id="kpiVisits7">–</strong></div>
    <div class="kpi business"><span>Letzte 30 Tage</span><strong id="kpiVisits30">–</strong></div>
  </div>

'''
    needle = '  <div class="section-label"><h2>Support & Verbesserungen</h2><span>Anfragen deiner Kunden</span></div>'
    if needle not in text:
        raise SystemExit("Admin stats insertion point not found")
    text = text.replace(needle, block + needle, 1)

    function = '''async function loadSiteVisitStats(){
  const now=new Date(),today=new Date(now.getFullYear(),now.getMonth(),now.getDate()),d7=new Date(now),d30=new Date(now);
  d7.setDate(d7.getDate()-7);d30.setDate(d30.getDate()-30);
  const [total,todayQ,weekQ,monthQ]=await Promise.all([
    client.from("site_visit_events").select("id",{count:"exact",head:true}).eq("source","website"),
    client.from("site_visit_events").select("id",{count:"exact",head:true}).eq("source","website").gte("visited_at",today.toISOString()),
    client.from("site_visit_events").select("id",{count:"exact",head:true}).eq("source","website").gte("visited_at",d7.toISOString()),
    client.from("site_visit_events").select("id",{count:"exact",head:true}).eq("source","website").gte("visited_at",d30.toISOString())
  ]);
  const queries=[total,todayQ,weekQ,monthQ];
  if(queries.some(q=>q.error)){console.error(...queries.map(q=>q.error).filter(Boolean));return;}
  document.getElementById("kpiVisitsTotal").textContent=total.count??0;
  document.getElementById("kpiVisitsToday").textContent=todayQ.count??0;
  document.getElementById("kpiVisits7").textContent=weekQ.count??0;
  document.getElementById("kpiVisits30").textContent=monthQ.count??0;
}

'''
    fn_needle = 'async function load(){'
    if fn_needle not in text:
        raise SystemExit("Admin function insertion point not found")
    text = text.replace(fn_needle, function + fn_needle, 1)

old_refresh = 'async function refreshAll(){await Promise.all([loadBusinessStats(),loadCompanies(),loadPrivateStats(),load()]);}'
new_refresh = 'async function refreshAll(){await Promise.all([loadBusinessStats(),loadCompanies(),loadPrivateStats(),loadSiteVisitStats(),load()]);}'
if old_refresh in text:
    text = text.replace(old_refresh, new_refresh, 1)
elif new_refresh not in text:
    raise SystemExit("refreshAll insertion point not found")

PATH.write_text(text, encoding="utf-8")
