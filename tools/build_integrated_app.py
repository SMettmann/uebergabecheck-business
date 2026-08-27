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

output.write_text(html,encoding='utf-8')
print(f'Built {output} ({len(html)} chars)')