from pathlib import Path

PATH = Path("app.html")
START = "/* UEBERGABECHECK_DESKTOP_DASHBOARD_V1_START */"
END = "/* UEBERGABECHECK_DESKTOP_DASHBOARD_V1_END */"

CSS = r'''
/* UEBERGABECHECK_DESKTOP_DASHBOARD_V1_START */
@media (min-width:901px){
  body:has(#businessDashboard:not(.hidden)){background:#f3f4f6}
  body:has(#businessDashboard:not(.hidden)) .app{max-width:1280px;padding:22px 28px 72px}

  #businessDashboard{display:grid;grid-template-columns:minmax(0,2fr) minmax(300px,.82fr);column-gap:16px;row-gap:14px;padding:8px 0 54px}
  #businessDashboard>*{grid-column:1/-1;min-width:0}

  #businessDashboard .dashboard-top{align-items:center;gap:24px;margin:0;padding:2px 2px 0}
  #businessDashboard .dashboard-top>div:first-child{min-width:260px}
  #businessDashboard .dashboard-kicker{font-size:10.5px;letter-spacing:1.7px;margin-bottom:5px;color:#7a7c82}
  #businessDashboard .dashboard-top h1{font-size:29px;line-height:1.05;letter-spacing:-1.1px;margin:0 0 5px}
  #businessDashboard .dashboard-top p{font-size:12.5px;color:#74767d}
  #businessDashboard .dashboard-actions{justify-content:flex-end;align-items:center;gap:8px}
  #businessDashboard .dashboard-actions button{padding:9px 12px;border:1px solid #e0e1e4;background:#fff;color:#25262a;border-radius:11px;box-shadow:0 1px 3px rgba(0,0,0,.025)}
  #businessDashboard .dashboard-actions button:hover{background:#fafafa;border-color:#ced0d4;transform:translateY(-1px)}
  #businessDashboard .dashboard-actions .primary{order:-1;background:#111;color:#fff;border-color:#111;box-shadow:0 6px 16px rgba(0,0,0,.10)}
  #businessDashboard .dashboard-actions .primary:hover{background:#242424;border-color:#242424}
  #businessDashboard .dashboard-top .dashboard-actions button[onclick*="goBusinessHome"]{display:none!important}

  #businessDashboard .subscription-notice{padding:10px 13px;margin:0;border-radius:13px;box-shadow:0 1px 3px rgba(0,0,0,.02)}
  #businessDashboard .subscription-notice strong{font-size:12.5px;margin-bottom:2px}
  #businessDashboard .subscription-notice span{font-size:11px}
  #businessDashboard .subscription-status-pill{padding:5px 9px;font-size:10px}
  #businessDashboard .subscription-action{padding:7px 10px;font-size:10.5px}
  #businessDashboard .dashboard-legal-links{font-size:10px;margin:-6px 3px -2px;color:#999}
  #businessDashboard .dashboard-legal-links a{color:#696b71;margin-left:8px}

  #businessDashboard .dashboard-nav{display:flex;align-items:center;gap:4px;background:#fff;border:1px solid #e0e1e4;border-radius:14px;padding:5px;margin:0;box-shadow:0 2px 8px rgba(0,0,0,.025)}
  #businessDashboard .dashboard-nav button{background:transparent;color:#505258;padding:8px 14px;border-radius:9px;font-size:12px}
  #businessDashboard .dashboard-nav button:hover{background:#f1f2f4;color:#111}
  #businessDashboard .dashboard-nav button.active{background:#111;color:#fff;box-shadow:0 3px 9px rgba(0,0,0,.11)}

  #businessDashboard .dashboard-grid{gap:10px;margin:0}
  #businessDashboard .dashboard-stat{min-height:82px;padding:13px 16px;border-radius:15px;box-shadow:0 2px 9px rgba(0,0,0,.022);transition:transform .15s ease,border-color .15s ease}
  #businessDashboard .dashboard-stat:hover{transform:translateY(-1px);border-color:#d3d5d9}
  #businessDashboard .dashboard-stat span{font-size:10.5px;margin-bottom:6px;color:#7c7e84}
  #businessDashboard .dashboard-stat strong{font-size:25px;letter-spacing:-.8px}
  #businessDashboard .dashboard-stat:nth-child(4){background:#fffafa;border-color:#f0dede}
  #businessDashboard .dashboard-stat:nth-child(4) strong{color:#a03434}

  #businessSearchCard{display:grid;grid-template-columns:180px minmax(0,1fr);column-gap:15px;row-gap:0;align-items:center;padding:14px 17px;margin:0!important;border-radius:17px;box-shadow:0 2px 9px rgba(0,0,0,.023)}
  #businessSearchCard .dashboard-card-head{margin:0}
  #businessSearchCard .dashboard-card-head h2{font-size:16px;margin-bottom:2px}
  #businessSearchCard .dashboard-card-head small{font-size:10.5px!important}
  #businessSearchCard>div:nth-of-type(2){flex-wrap:nowrap!important;align-items:center}
  #businessSearchCard input,#businessSearchCard select{padding:10px 11px;border-radius:10px;background:#fff}
  #businessSearchCard select{flex:0 0 165px;width:165px;min-width:165px!important}
  #businessSearchResults{grid-column:1/-1;margin-top:9px!important}
  #businessSearchResults .empty-state{padding:10px 14px;border-radius:11px;background:#fafafa}

  #businessDashboard>#objectsCard{grid-column:1;margin:0!important;padding:20px;border-radius:18px;box-shadow:0 2px 10px rgba(0,0,0,.025)}
  #businessDashboard>.dashboard-main{grid-column:2;display:block;margin:0;min-width:0}
  #businessDashboard>.dashboard-main .dashboard-card{padding:18px;border-radius:18px;box-shadow:0 2px 10px rgba(0,0,0,.025)}
  #businessDashboard>.dashboard-main .dashboard-card-head{margin-bottom:12px}
  #businessDashboard>.dashboard-main .dashboard-card-head h2{font-size:17px}

  #objectsCard .dashboard-card-head{margin-bottom:12px}
  #objectsCard .dashboard-card-head h2{font-size:18px}
  #objectsCard .dashboard-card-head .secondary{padding:9px 12px;background:#111;color:#fff}
  #objectsCard .dashboard-list{gap:8px}
  #objectsCard .dashboard-list-item{padding:13px 15px;border-radius:12px;background:#fff;transition:background .15s ease,border-color .15s ease,transform .15s ease}
  #objectsCard .dashboard-list-item:hover{background:#fafafa;border-color:#d7d9dd;transform:translateY(-1px)}

  #businessDashboard>.dashboard-main .dashboard-list{gap:8px}
  #businessDashboard>.dashboard-main .dashboard-list-item{padding:12px 13px;border-radius:11px;background:#fafafa;transition:background .15s ease,border-color .15s ease,transform .15s ease}
  #businessDashboard>.dashboard-main .dashboard-list-item:hover{background:#f1f2f4;border-color:#d7d9dc;transform:translateY(-1px)}
  #businessDashboard>.dashboard-main .dashboard-list-item strong{font-size:13px}
  #businessDashboard>.dashboard-main .dashboard-list-item small{font-size:11px}
  #businessDashboard>.dashboard-main .dashboard-list-item>span:last-child{font-size:17px;color:#666}

  #businessDashboard:has(>.dashboard-main.hidden)>#objectsCard:not(.hidden){grid-column:1/-1}
  #businessDashboard:has(>#objectsCard.hidden)>.dashboard-main:not(.hidden){grid-column:1/-1}

  #businessDashboard .dashboard-card,#businessDashboard .object-detail{border-color:#e0e1e4}
  #businessDashboard button{transition:background .15s ease,border-color .15s ease,transform .15s ease}
}
/* UEBERGABECHECK_DESKTOP_DASHBOARD_V1_END */
'''

text = PATH.read_text(encoding="utf-8")
if START in text:
    raise SystemExit(0)

pos = text.find("</style>")
if pos < 0:
    raise RuntimeError("No closing style tag found in app.html")

text = text[:pos] + CSS + "\n" + text[pos:]
PATH.write_text(text, encoding="utf-8")
