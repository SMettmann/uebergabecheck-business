from pathlib import Path

p = Path('index.html')
s = p.read_text(encoding='utf-8')

old_actions = '''      <div style="display:flex;gap:10px;flex-wrap:wrap;justify-content:flex-end;">
        <button class="secondary" id="transferEmailSendButton" type="button" onclick="sendTransferEmail()">Direkt versenden</button>
        <button class="primary" id="transferEmailClientButton" type="button" onclick="openTransferMailClient()">E-Mail-Programm öffnen</button>
      </div>'''
new_actions = '''      <button class="primary" id="transferEmailClientButton" type="button" onclick="openTransferMailClient()">E-Mail-Programm öffnen</button>'''
assert old_actions in s
s = s.replace(old_actions, new_actions, 1)

start = s.find('function blobToBase64(blob){')
end = s.find('function showSummary(){', start)
assert start != -1 and end != -1
block = s[start:end]
a = block.find('async function openTransferMailClient(){')
b = block.find('async function sendTransferEmail(){')
assert a != -1 and b != -1
s = s[:start] + block[a:b] + '\n' + s[end:]

marker = 'let meterPhotos={electric:[],water:[],gas:[]};'
assert marker in s
s = s.replace(marker, marker + '\nlet storedSignatures={tenant:"",landlord:""};\nlet storedSignatureDetails={tenantPlace:"",landlordPlace:"",date:""};', 1)

old = '''  const ids=["address","date","tenant","landlord","electricNo","electric","waterNo","water","gasNo","gas","keys","notes","tenantSignaturePlace","landlordSignaturePlace","signatureDate"];
  const fields={};
  ids.forEach(id=>{
    const el=document.getElementById(id);
    fields[id]=el ? (el.value ?? "") : "";
  });'''
new = '''  const ids=["address","date","tenant","landlord","electricNo","electric","waterNo","water","gasNo","gas","keys","notes"];
  const fields={};
  ids.forEach(id=>{
    const el=document.getElementById(id);
    fields[id]=el ? (el.value ?? "") : "";
  });
  fields.tenantSignaturePlace=document.getElementById("tenantSignaturePlace")?.value ?? storedSignatureDetails.tenantPlace ?? "";
  fields.landlordSignaturePlace=document.getElementById("landlordSignaturePlace")?.value ?? storedSignatureDetails.landlordPlace ?? "";
  fields.signatureDate=document.getElementById("signatureDate")?.value ?? storedSignatureDetails.date ?? "";
  storedSignatureDetails={tenantPlace:fields.tenantSignaturePlace||"",landlordPlace:fields.landlordSignaturePlace||"",date:fields.signatureDate||""};'''
assert old in s
s = s.replace(old, new, 1)

old = '''    signatures:{
      tenant:document.getElementById("sigTenant")?.toDataURL("image/png")||"",
      landlord:document.getElementById("sigLandlord")?.toDataURL("image/png")||""
    },'''
new = '''    signatures:(()=>{
      const tenantCanvas=document.getElementById("sigTenant");
      const landlordCanvas=document.getElementById("sigLandlord");
      storedSignatures={tenant:tenantCanvas?tenantCanvas.toDataURL("image/png"):(storedSignatures.tenant||""),landlord:landlordCanvas?landlordCanvas.toDataURL("image/png"):(storedSignatures.landlord||"")};
      return {...storedSignatures};
    })(),'''
assert old in s
s = s.replace(old, new, 1)

old = '''    meterPhotos=snapshot.meterPhotos&&typeof snapshot.meterPhotos==="object"?JSON.parse(JSON.stringify(snapshot.meterPhotos)):{electric:[],water:[],gas:[]};
    currentRoom=snapshot.currentRoom||selectedRooms[0]||"Flur";'''
new = '''    meterPhotos=snapshot.meterPhotos&&typeof snapshot.meterPhotos==="object"?JSON.parse(JSON.stringify(snapshot.meterPhotos)):{electric:[],water:[],gas:[]};
    storedSignatures={tenant:snapshot.signatures?.tenant||"",landlord:snapshot.signatures?.landlord||""};
    storedSignatureDetails={tenantPlace:snapshot.fields?.tenantSignaturePlace||"",landlordPlace:snapshot.fields?.landlordSignaturePlace||"",date:snapshot.fields?.signatureDate||""};
    currentRoom=snapshot.currentRoom||selectedRooms[0]||"Flur";'''
assert old in s
s = s.replace(old, new, 1)

old = '''    if(snapshot.signatures){
      restoreSignatureImage("sigTenant",snapshot.signatures.tenant||"");
      restoreSignatureImage("sigLandlord",snapshot.signatures.landlord||"");
    }

'''
assert old in s
s = s.replace(old, '', 1)

old = '''  setupSignature("sigTenant");
  setupSignature("sigLandlord");

  const sigDate = document.getElementById("signatureDate");
  const today = new Date();
  const localToday = new Date(today.getTime() - today.getTimezoneOffset() * 60000).toISOString().slice(0,10);
  if(sigDate && !sigDate.value) sigDate.value = localToday;'''
new = '''  setupSignature("sigTenant");
  setupSignature("sigLandlord");

  const tenantPlaceInput=document.getElementById("tenantSignaturePlace");
  const landlordPlaceInput=document.getElementById("landlordSignaturePlace");
  const sigDate = document.getElementById("signatureDate");
  if(tenantPlaceInput) tenantPlaceInput.value=storedSignatureDetails.tenantPlace||"";
  if(landlordPlaceInput) landlordPlaceInput.value=storedSignatureDetails.landlordPlace||"";
  if(sigDate) sigDate.value=storedSignatureDetails.date||"";
  const today = new Date();
  const localToday = new Date(today.getTime() - today.getTimezoneOffset() * 60000).toISOString().slice(0,10);
  if(sigDate && !sigDate.value) sigDate.value = localToday;
  restoreSignatureImage("sigTenant",storedSignatures.tenant||"");
  restoreSignatureImage("sigLandlord",storedSignatures.landlord||"");'''
assert old in s
s = s.replace(old, new, 1)

old = '''    if(tdd) tdd.textContent = formatted;
    if(ldd) ldd.textContent = formatted;
    saveDraft();'''
new = '''    if(tdd) tdd.textContent = formatted;
    if(ldd) ldd.textContent = formatted;
    storedSignatureDetails={tenantPlace:document.getElementById("tenantSignaturePlace")?.value.trim()||"",landlordPlace:document.getElementById("landlordSignaturePlace")?.value.trim()||"",date:sigDate?.value||""};
    saveDraft();'''
assert old in s
s = s.replace(old, new, 1)

old = '  const stop=()=>{drawing=false;};'
new = '''  const stop=()=>{
    if(!drawing) return;
    drawing=false;
    storedSignatures={tenant:document.getElementById("sigTenant")?.toDataURL("image/png")||storedSignatures.tenant||"",landlord:document.getElementById("sigLandlord")?.toDataURL("image/png")||storedSignatures.landlord||""};
    saveDraft();
    queueTransferAutosave();
  };'''
assert old in s
s = s.replace(old, new, 1)

old = '''function clearSignature(id){
  const c=document.getElementById(id); if(!c)return;
  c.getContext("2d").clearRect(0,0,c.width,c.height);
  saveDraft();
}'''
new = '''function clearSignature(id){
  const c=document.getElementById(id); if(!c)return;
  c.getContext("2d").clearRect(0,0,c.width,c.height);
  if(id==="sigTenant") storedSignatures.tenant="";
  if(id==="sigLandlord") storedSignatures.landlord="";
  saveDraft();
  queueTransferAutosave();
}'''
assert old in s
s = s.replace(old, new, 1)

old = '''  if(updateError){
    console.error("Passwort ändern:",updateError);
    if(error){error.textContent="Das Passwort konnte nicht geändert werden. Bitte den Reset-Link erneut öffnen.";error.classList.remove("hidden");}
    return;
  }'''
new = '''  if(updateError){
    console.error("Passwort ändern:",updateError);
    const msg=String(updateError.message||"").toLowerCase();
    let text="Das Passwort konnte nicht geändert werden.";
    if(msg.includes("same")||msg.includes("different")||msg.includes("previous")||msg.includes("old password")) text="Das neue Passwort muss sich vom bisherigen Passwort unterscheiden.";
    else if(msg.includes("expired")||msg.includes("invalid")||msg.includes("token")) text="Der Reset-Link ist ungültig oder abgelaufen. Bitte fordere einen neuen Link an.";
    if(error){error.textContent=text;error.classList.remove("hidden");}
    return;
  }'''
assert old in s
s = s.replace(old, new, 1)

p.write_text(s, encoding='utf-8')
