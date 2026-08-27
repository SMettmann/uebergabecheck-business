from pathlib import Path

app_source = Path('index.html')
team_source = Path('team.html')

html = app_source.read_text(encoding='utf-8')

old = '''  if(membership?.company_id){ businessCompanyId=membership.company_id; return businessCompanyId; }

  const companyId=crypto.randomUUID();'''
new = '''  if(membership?.company_id){ businessCompanyId=membership.company_id; return businessCompanyId; }

  // Eingeladene Mitarbeiter dürfen nach Entfernung aus einem Team nicht
  // automatisch zu Inhabern eines neuen Firmenkontos werden.
  if(String(user.user_metadata?.account_type||"")==="business_member"){
    throw new Error("TEAM_ACCESS_REMOVED");
  }

  const companyId=crypto.randomUUID();'''
if old not in html:
    raise SystemExit('ensureBusinessCompany anchor not found')
html = html.replace(old, new, 1)

anchor = '''async function loadBusinessData(user){
'''
helper = '''async function handleRemovedBusinessMember(){
  businessDataLoadedForUser=null;
  businessCompanyId=null;
  businessSubscription=null;
  businessLegalAcceptance=null;
  window.businessSubscription=null;
  window.businessLegalAcceptance=null;
  window.businessCurrentRole=null;
  window.currentBusinessApartmentId=null;
  window.currentBusinessTransferId=null;
  window.currentBusinessTransferCreatedByName="";
  businessObjects=[];
  businessApartments={};
  apartmentTransfers={};
  selectedBusinessObjectId=null;
  selectedApartmentId=null;

  document.getElementById("businessDashboard")?.classList.add("hidden");
  document.getElementById("appContent")?.classList.add("hidden");
  closeBusinessLegalGate?.();

  try{ if(supabaseClient) await supabaseClient.auth.signOut(); }catch(_error){}
  supabaseUser=null;

  const landing=document.getElementById("landing");
  if(landing){landing.classList.remove("hidden");landing.style.display="flex";}
  if(typeof showLogin==="function")showLogin();
  const error=document.getElementById("loginError");
  if(error){
    error.textContent="Dein Mitarbeiterzugang ist aktuell keinem Unternehmen mehr zugeordnet. Bitte wende dich an den Inhaber deines Unternehmenskontos.";
    error.classList.remove("hidden");
  }
}

let businessMembershipCheckRunning=false;
async function revalidateBusinessMembership(){
  if(businessMembershipCheckRunning || !supabaseClient || !supabaseUser)return;
  businessMembershipCheckRunning=true;
  try{
    const user=supabaseUser;
    const {data,error}=await supabaseClient.from("company_members").select("company_id,role").eq("user_id",user.id).maybeSingle();
    if(error)return;
    if(!data && String(user.user_metadata?.account_type||"")==="business_member"){
      await handleRemovedBusinessMember();
      return;
    }
    if(data?.company_id){
      businessCompanyId=data.company_id;
      if(typeof window.refreshBusinessRole==="function")window.refreshBusinessRole();
    }
  }finally{businessMembershipCheckRunning=false;}
}

window.addEventListener("focus",()=>revalidateBusinessMembership().catch(()=>{}));
document.addEventListener("visibilitychange",()=>{if(!document.hidden)revalidateBusinessMembership().catch(()=>{});});
setInterval(()=>revalidateBusinessMembership().catch(()=>{}),30000);

async function loadBusinessData(user){
'''
if anchor not in html:
    raise SystemExit('loadBusinessData anchor not found')
html = html.replace(anchor, helper, 1)

oldcatch = '''  }catch(error){
    businessDataLoadedForUser=null;
    console.error("Business-Daten:",error);
    alert("Die Business-Daten konnten nicht geladen werden. Bitte prüfe die Supabase-Datenbank.");
  }finally{businessDataLoading=false;}
}'''
newcatch = '''  }catch(error){
    businessDataLoadedForUser=null;
    if(String(error?.message||"").includes("TEAM_ACCESS_REMOVED")){
      await handleRemovedBusinessMember();
      return;
    }
    console.error("Business-Daten:",error);
    alert("Die Business-Daten konnten nicht geladen werden. Bitte prüfe die Supabase-Datenbank.");
  }finally{businessDataLoading=false;}
}'''
if oldcatch not in html:
    raise SystemExit('loadBusinessData catch anchor not found')
html = html.replace(oldcatch, newcatch, 1)

app_source.write_text(html, encoding='utf-8')

team = team_source.read_text(encoding='utf-8')
oldteam = '''    if(message.toLowerCase().includes("berechtigung")){
      location.replace(APP_URL);
      return;
    }
    only("loginView");
    status("loginStatus",message||"Teamverwaltung konnte nicht geladen werden.","error");'''
newteam = '''    if(message.toLowerCase().includes("berechtigung")){
      location.replace(APP_URL);
      return;
    }
    if(message.toLowerCase().includes("kein unternehmen")){
      await client.auth.signOut();
      only("loginView");
      status("loginStatus","Dein Mitarbeiterzugang ist aktuell keinem Unternehmen mehr zugeordnet. Bitte wende dich an den Inhaber.","error");
      return;
    }
    only("loginView");
    status("loginStatus",message||"Teamverwaltung konnte nicht geladen werden.","error");'''
if oldteam not in team:
    raise SystemExit('team catch anchor not found')
team = team.replace(oldteam, newteam, 1)
team_source.write_text(team, encoding='utf-8')

print('Removed-member access hardening applied')