from pathlib import Path

path = Path('team.html')
html = path.read_text(encoding='utf-8')

if 'async function revalidateTeamSession()' in html and 'client.auth.onAuthStateChange' in html:
    print('team.html session revalidation already present')
    raise SystemExit(0)

old_load = '''async function loadTeam(){const {data}=await client.auth.getSession();if(!data?.session){only("loginView");return;}try{teamData=await invoke("manage-team",{action:"list"});only("teamView");renderTeam();}catch(e){only("loginView");status("loginStatus",e.message,"error");}}'''
new_load = '''async function loadTeam(){
  const {data}=await client.auth.getSession();
  if(!data?.session){teamData=null;only("loginView");return;}
  try{
    teamData=await invoke("manage-team",{action:"list"});
    only("teamView");
    renderTeam();
  }catch(e){
    teamData=null;
    const message=String(e?.message||"");
    if(message.toLowerCase().includes("berechtigung")){
      location.replace(APP_URL);
      return;
    }
    only("loginView");
    status("loginStatus",message||"Teamverwaltung konnte nicht geladen werden.","error");
  }
}'''

if old_load not in html:
    raise SystemExit('loadTeam pattern not found')
html = html.replace(old_load, new_load, 1)

old_tail = '''async function inviteLogout(){await client.auth.signOut();await refreshInviteAuth()}\n(async()=>{if(inviteToken)await loadInvite();else await loadTeam()})();'''
new_tail = '''async function inviteLogout(){await client.auth.signOut();await refreshInviteAuth()}

async function revalidateTeamSession(){
  if(inviteToken){await refreshInviteAuth();return;}
  teamData=null;
  only("loading");
  const {data}=await client.auth.getSession();
  if(!data?.session){only("loginView");return;}
  await loadTeam();
}

client.auth.onAuthStateChange((_event,session)=>{
  teamData=null;
  if(inviteToken){
    setTimeout(()=>refreshInviteAuth().catch(()=>{}),0);
    return;
  }
  only("loading");
  if(!session?.user){
    only("loginView");
    return;
  }
  setTimeout(()=>loadTeam().catch(()=>{}),0);
});

window.addEventListener("focus",()=>{
  if(!inviteToken)revalidateTeamSession().catch(()=>{});
});

document.addEventListener("visibilitychange",()=>{
  if(document.visibilityState==="visible" && !inviteToken)revalidateTeamSession().catch(()=>{});
});

(async()=>{if(inviteToken)await loadInvite();else await loadTeam()})();'''

if old_tail not in html:
    raise SystemExit('team auth tail pattern not found')
html = html.replace(old_tail, new_tail, 1)

path.write_text(html, encoding='utf-8')
print('Patched team.html session revalidation')
