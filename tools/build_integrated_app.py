from pathlib import Path

source = Path('index.html')
output = Path('app.html')
html = source.read_text(encoding='utf-8')

marker_start = '<!-- UEBERGABECHECK_ROLE_GUARDS_START -->'
marker_end = '<!-- UEBERGABECHECK_ROLE_GUARDS_END -->'

role_script = r'''
<!-- UEBERGABECHECK_ROLE_GUARDS_START -->
<script>
(function(){
  "use strict";

  let roleCache=null;
  let rolePromise=null;

  function isManager(role){return role==="owner" || role==="admin";}

  window.refreshBusinessRole=()=>loadCurrentBusinessRole(true);

  function resetRoleState(){
    roleCache=null;
    rolePromise=null;
    syncRoleUI(null);
  }

  async function loadCurrentBusinessRole(force=false,userOverride=null){
    if(force){
      roleCache=null;
      rolePromise=null;
    }else{
      if(roleCache)return roleCache;
      if(rolePromise)return rolePromise;
    }

    rolePromise=(async()=>{
      try{
        if(typeof initSupabase==="function")initSupabase();
        if(typeof supabaseClient==="undefined" || !supabaseClient)return null;

        let user=userOverride||null;
        if(!user){
          const {data}=await supabaseClient.auth.getSession();
          user=data?.session?.user||null;
        }

        if(!user){
          roleCache=null;
          syncRoleUI(null);
          return null;
        }

        const requestedUserId=user.id;
        const {data,error}=await supabaseClient
          .from("company_members")
          .select("role")
          .eq("user_id",requestedUserId)
          .maybeSingle();

        if(error){
          console.error("Rollenprüfung:",error);
          syncRoleUI(null);
          return null;
        }

        const {data:sessionData}=await supabaseClient.auth.getSession();
        const activeUser=sessionData?.session?.user||null;
        if(!activeUser || activeUser.id!==requestedUserId){
          roleCache=null;
          syncRoleUI(null);
          return null;
        }

        roleCache=data?.role||null;
        window.businessCurrentRole=roleCache;
        syncRoleUI(roleCache);
        return roleCache;
      }catch(error){
        console.error("Rollenprüfung:",error);
        syncRoleUI(null);
        return null;
      }finally{
        rolePromise=null;
      }
    })();

    return rolePromise;
  }

  function syncRoleUI(role){
    window.businessCurrentRole=role||null;
    document.body.dataset.businessRole=role||"";

    const dashboardActions=document.querySelector("#businessDashboard .dashboard-top .dashboard-actions");
    let teamButton=document.getElementById("businessTeamButton");
    if(dashboardActions && !teamButton){
      teamButton=document.createElement("button");
      teamButton.id="businessTeamButton";
      teamButton.type="button";
      teamButton.className="secondary hidden";
      teamButton.textContent="👥 Team";
      teamButton.onclick=()=>{location.href="team.html";};
      const logoutButton=[...dashboardActions.querySelectorAll("button")].find(b=>String(b.getAttribute("onclick")||"").includes("businessLogout"));
      if(logoutButton)dashboardActions.insertBefore(teamButton,logoutButton);
      else dashboardActions.appendChild(teamButton);
    }
    teamButton?.classList.toggle("hidden",!isManager(role));

    const companyButton=[...document.querySelectorAll("#businessDashboard .dashboard-top .dashboard-actions button")].find(b=>String(b.getAttribute("onclick")||"").includes("openCompanyProfile"));
    companyButton?.classList.toggle("hidden",role!=="owner");

    const subscriptionAction=document.getElementById("businessSubscriptionAction");
    if(subscriptionAction){
      if(role!=="owner") subscriptionAction.classList.add("hidden");
      else if(typeof refreshBusinessSubscriptionUI==="function" && businessSubscription) {
        // The normal subscription renderer decides whether the owner action is visible.
      }
    }
  }

  async function requireManager(message){
    const role=await loadCurrentBusinessRole();
    if(isManager(role))return true;
    if(role==="member"){
      alert(message||"Keine Berechtigung – nur Inhaber und Admins können Objekte und Wohnungen verwalten.");
      return false;
    }
    alert("Deine Benutzerrolle konnte gerade nicht geprüft werden. Bitte lade die Seite neu und versuche es erneut.");
    return false;
  }

  async function requireOwner(message){
    const role=await loadCurrentBusinessRole();
    if(role==="owner")return true;
    if(role==="admin" || role==="member"){
      alert(message||"Keine Berechtigung – nur der Inhaber kann diese Einstellung verwalten.");
      return false;
    }
    alert("Deine Benutzerrolle konnte gerade nicht geprüft werden. Bitte lade die Seite neu und versuche es erneut.");
    return false;
  }

  function wrap(name,permission){
    const original=window[name];
    if(typeof original!=="function" || original.__roleGuarded)return;
    const wrapped=async function(...args){
      if(!(await permission()))return;
      return original.apply(this,args);
    };
    wrapped.__roleGuarded=true;
    wrapped.__original=original;
    window[name]=wrapped;
  }

  function installGuards(){
    const structureMessage="Keine Berechtigung – nur Inhaber und Admins können Objekte und Wohnungen verwalten.";
    const manager=()=>requireManager(structureMessage);
    [
      "showObjectForm","editObject","saveObject","deleteObject","safeDeleteObject",
      "quickAddApartment","showApartmentForm","editApartment","editSelectedApartment",
      "saveApartment","deleteApartment","safeDeleteApartment"
    ].forEach(name=>wrap(name,manager));

    wrap("deleteBusinessTransfer",()=>requireManager("Keine Berechtigung – nur Inhaber und Admins können Übergaben löschen. Du kannst Übergaben weiterhin öffnen und bearbeiten."));
    wrap("openCompanyProfile",()=>requireOwner("Keine Berechtigung – nur der Inhaber kann die Unternehmensdaten verwalten."));
    wrap("saveCompanyProfile",()=>requireOwner("Keine Berechtigung – nur der Inhaber kann die Unternehmensdaten ändern."));
    wrap("startStripeCheckout",()=>requireOwner("Keine Berechtigung – nur der Inhaber kann das Abonnement verwalten."));
    wrap("openStripeCustomerPortal",()=>requireOwner("Keine Berechtigung – nur der Inhaber kann das Abonnement verwalten."));

    const originalRefresh=window.refreshBusinessSubscriptionUI;
    if(typeof originalRefresh==="function" && !originalRefresh.__roleGuarded){
      const wrappedRefresh=function(...args){
        const result=originalRefresh.apply(this,args);
        loadCurrentBusinessRole().then(syncRoleUI).catch(()=>{});
        return result;
      };
      wrappedRefresh.__roleGuarded=true;
      window.refreshBusinessSubscriptionUI=wrappedRefresh;
    }

    const originalShowDashboard=window.showBusinessDashboard;
    if(typeof originalShowDashboard==="function" && !originalShowDashboard.__roleSessionGuarded){
      const wrappedShowDashboard=function(...args){
        resetRoleState();
        const result=originalShowDashboard.apply(this,args);
        const user=args[0]||null;
        setTimeout(()=>loadCurrentBusinessRole(true,user).catch(()=>{}),0);
        return result;
      };
      wrappedShowDashboard.__roleSessionGuarded=true;
      window.showBusinessDashboard=wrappedShowDashboard;
    }

    const originalLogout=window.businessLogout;
    if(typeof originalLogout==="function" && !originalLogout.__roleSessionGuarded){
      const wrappedLogout=async function(...args){
        resetRoleState();
        return originalLogout.apply(this,args);
      };
      wrappedLogout.__roleSessionGuarded=true;
      window.businessLogout=wrappedLogout;
    }
  }

  function initRoleGuards(){
    installGuards();
    resetRoleState();
    loadCurrentBusinessRole(true).catch(()=>{});

    try{
      if(typeof initSupabase==="function")initSupabase();
      if(typeof supabaseClient!=="undefined" && supabaseClient?.auth){
        supabaseClient.auth.onAuthStateChange((_event,session)=>{
          resetRoleState();
          if(!session?.user)return;
          if(typeof supabaseUser!=="undefined")supabaseUser=session.user;
          setTimeout(()=>loadCurrentBusinessRole(true,session.user).catch(()=>{}),0);
        });
      }
    }catch(error){
      console.error("Rollen-UI:",error);
      resetRoleState();
    }
  }

  if(document.readyState==="loading")document.addEventListener("DOMContentLoaded",initRoleGuards,{once:true});
  else initRoleGuards();
})();
</script>
<!-- UEBERGABECHECK_ROLE_GUARDS_END -->
'''

if marker_start in html and marker_end in html:
    before = html.split(marker_start,1)[0]
    after = html.split(marker_end,1)[1]
    html = before + role_script + after
else:
    if '</body>' not in html:
        raise SystemExit('No </body> found in index.html')
    html = html.replace('</body>', role_script + '\n</body>', 1)

# Defensive delete checks: local UI state is changed only when the backend actually deleted a row.
html = html.replace(
    'const {error}=await supabaseClient.from("objects").delete().eq("id",id);\n  if(error){console.error(error);alert("Das Objekt konnte nicht gelöscht werden.");return;}',
    'const {data:deletedRows,error}=await supabaseClient.from("objects").delete().eq("id",id).select("id");\n  if(error){console.error(error);alert("Das Objekt konnte nicht gelöscht werden.");return;}\n  if(!deletedRows?.length){alert("Keine Berechtigung – das Objekt wurde nicht gelöscht.");return;}'
)
html = html.replace(
    'const {error}=await supabaseClient.from("apartments").delete().eq("id",id);\n  if(error){console.error(error);alert("Die Wohnung konnte nicht gelöscht werden.");return;}',
    'const {data:deletedRows,error}=await supabaseClient.from("apartments").delete().eq("id",id).select("id");\n  if(error){console.error(error);alert("Die Wohnung konnte nicht gelöscht werden.");return;}\n  if(!deletedRows?.length){alert("Keine Berechtigung – die Wohnung wurde nicht gelöscht.");return;}'
)
old_transfer='''const {error}=await supabaseClient\n    .from("transfers")\n    .delete()\n    .eq("id",transferId);'''
new_transfer='''const {data:deletedRows,error}=await supabaseClient\n    .from("transfers")\n    .delete()\n    .eq("id",transferId)\n    .select("id");'''
html=html.replace(old_transfer,new_transfer)
html=html.replace(
    'if(error){\n    console.error("Übergabe löschen:",error);\n    alert("Die Übergabe konnte nicht gelöscht werden.\\n\\n"+(error.message || "Unbekannter Fehler"));\n    return;\n  }\n\n  if(apartmentTransfers[apartmentId]){',
    'if(error){\n    console.error("Übergabe löschen:",error);\n    alert("Die Übergabe konnte nicht gelöscht werden.\\n\\n"+(error.message || "Unbekannter Fehler"));\n    return;\n  }\n  if(!deletedRows?.length){alert("Keine Berechtigung – die Übergabe wurde nicht gelöscht.");return;}\n\n  if(apartmentTransfers[apartmentId]){'
)

# Persistent desktop-only dashboard refinement. It is generated into app.html on every build,
# so future Business builds keep the desktop workspace without touching the mobile layout.
desktop_marker = '/* UEBERGABECHECK_DESKTOP_DASHBOARD_V1_START */'
desktop_css = r'''
/* UEBERGABECHECK_DESKTOP_DASHBOARD_V1_START */
@media (min-width:901px){
  body:has(#businessDashboard:not(.hidden)){background:#f3f4f6}
  body:has(#businessDashboard:not(.hidden)) .app{max-width:1280px;padding:22px 28px 72px}

  #businessDashboard:not(.hidden){display:grid!important;grid-template-columns:minmax(0,2fr) minmax(300px,.82fr);column-gap:16px;row-gap:14px;padding:8px 0 54px}
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

if desktop_marker not in html:
    if '</style>' not in html:
        raise SystemExit('No </style> found in index.html')
    html = html.replace('</style>', desktop_css + '\n</style>', 1)

output.write_text(html,encoding='utf-8')
print(f'Built {output} ({len(html)} chars)')