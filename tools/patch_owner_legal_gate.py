from pathlib import Path

path=Path('index.html')
html=path.read_text(encoding='utf-8')

needle='''function openBusinessLegalGate(){
  if(hasCurrentBusinessLegalAcceptance())return;
  document.getElementById("businessLegalGate")?.classList.remove("hidden");
  document.body.style.overflow="hidden";
}'''
replacement='''let businessLegalOwnerNoticeShown=false;

async function handleMissingBusinessLegalAcceptance(user){
  if(hasCurrentBusinessLegalAcceptance())return;
  try{
    const currentUser=user||supabaseUser;
    if(!currentUser||!supabaseClient){openBusinessLegalGate();return;}
    const {data,error}=await supabaseClient.from("company_members").select("role").eq("user_id",currentUser.id).maybeSingle();
    if(error)throw error;
    if(data?.role==="owner"){
      openBusinessLegalGate();
      return;
    }
    closeBusinessLegalGate();
    if(!businessLegalOwnerNoticeShown){
      businessLegalOwnerNoticeShown=true;
      alert("Die aktuellen AGB und der AVV müssen zuerst vom Inhaber des Unternehmenskontos bestätigt werden. Bis dahin ist die Bearbeitung vorübergehend gesperrt.");
    }
  }catch(error){
    console.error("Rechtliche Rollenprüfung:",error);
    openBusinessLegalGate();
  }
}

function openBusinessLegalGate(){
  if(hasCurrentBusinessLegalAcceptance())return;
  document.getElementById("businessLegalGate")?.classList.remove("hidden");
  document.body.style.overflow="hidden";
}'''

if 'async function handleMissingBusinessLegalAcceptance(user)' not in html:
    if needle not in html: raise SystemExit('openBusinessLegalGate pattern missing')
    html=html.replace(needle,replacement,1)

old='if(!hasCurrentBusinessLegalAcceptance())setTimeout(openBusinessLegalGate,0);'
new='if(!hasCurrentBusinessLegalAcceptance())setTimeout(()=>handleMissingBusinessLegalAcceptance(user),0);'
count=html.count(old)
if count:
    html=html.replace(old,new)
elif new not in html:
    raise SystemExit('loadBusinessData legal gate patterns missing')

old_req='''function requireBusinessWriteAccess(){
  if(!hasCurrentBusinessLegalAcceptance()){openBusinessLegalGate();return false;}'''
new_req='''function requireBusinessWriteAccess(){
  if(!hasCurrentBusinessLegalAcceptance()){
    const role=window.businessCurrentRole||"";
    if(role==="admin"||role==="member"){
      alert("Die aktuellen AGB und der AVV müssen zuerst vom Inhaber des Unternehmenskontos bestätigt werden.");
    }else{
      openBusinessLegalGate();
    }
    return false;
  }'''
if old_req in html:
    html=html.replace(old_req,new_req,1)
elif new_req not in html:
    raise SystemExit('requireBusinessWriteAccess pattern missing')

path.write_text(html,encoding='utf-8')
print('Patched owner-only legal gate UI')
