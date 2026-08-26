from pathlib import Path
import re

p = Path('index.html')
s = p.read_text(encoding='utf-8')

# Email: only use the customer's own mail client.
direct_button = '        <button class="secondary" id="transferEmailSendButton" type="button" onclick="sendTransferEmail()">Direkt versenden</button>\n'
assert direct_button in s, 'direct send button not found'
s = s.replace(direct_button, '', 1)

old_notice = '<div class="notice" style="margin-top:14px;">Das PDF wird gespeichert und dein Standard-E-Mail-Programm mit Empfänger, Betreff und Nachricht geöffnet. Den heruntergeladenen PDF-Anhang fügst du anschließend der E-Mail hinzu.</div>'
new_notice = '<div class="notice" style="margin-top:14px;">Das Übergabeprotokoll wird als PDF gespeichert und dein Standard-E-Mail-Programm mit Empfänger, Betreff und Nachricht geöffnet. Füge anschließend das gespeicherte PDF als Anhang hinzu.</div>'
assert old_notice in s, 'email notice not found'
s = s.replace(old_notice, new_notice, 1)

s = re.sub(
    r'\nfunction blobToBase64\(blob\)\{.*?\n\}\n\n(?=async function openTransferMailClient\(\)\{)',
    '\n', s, count=1, flags=re.S
)
before = s
s = re.sub(
    r'\nasync function sendTransferEmail\(\)\{.*?\n\}\n\n(?=function showSummary\(\)\{)',
    '\n', s, count=1, flags=re.S
)
assert s != before, 'direct send function not removed'

# Persistent signature state exists independently of the dynamically rendered summary DOM.
meter = 'let meterPhotos={electric:[],water:[],gas:[]};'
insert = '''let meterPhotos={electric:[],water:[],gas:[]};
let savedSignatureState={tenant:"",landlord:"",tenantPlace:"",landlordPlace:"",date:""};

function resetSavedSignatureState(){
  savedSignatureState={tenant:"",landlord:"",tenantPlace:"",landlordPlace:"",date:""};
}

function storeSignatureCanvas(id,canvas){
  if(!canvas) return;
  try{
    const data=canvas.toDataURL("image/png");
    if(id==="sigTenant") savedSignatureState.tenant=data;
    if(id==="sigLandlord") savedSignatureState.landlord=data;
  }catch(e){}
}
'''
assert meter in s, 'meterPhotos marker not found'
s = s.replace(meter, insert, 1)

old_fields = '''  ids.forEach(id=>{
    const el=document.getElementById(id);
    fields[id]=el ? (el.value ?? "") : "";
  });
  return {'''
new_fields = '''  ids.forEach(id=>{
    const el=document.getElementById(id);
    fields[id]=el ? (el.value ?? "") : "";
  });
  fields.tenantSignaturePlace=savedSignatureState.tenantPlace||fields.tenantSignaturePlace||"";
  fields.landlordSignaturePlace=savedSignatureState.landlordPlace||fields.landlordSignaturePlace||"";
  fields.signatureDate=savedSignatureState.date||fields.signatureDate||"";
  return {'''
assert old_fields in s, 'formSnapshot fields block not found'
s = s.replace(old_fields, new_fields, 1)

old_sigs = '''    signatures:{
      tenant:document.getElementById("sigTenant")?.toDataURL("image/png")||"",
      landlord:document.getElementById("sigLandlord")?.toDataURL("image/png")||""
    },'''
new_sigs = '''    signatures:{
      tenant:savedSignatureState.tenant||"",
      landlord:savedSignatureState.landlord||""
    },'''
assert old_sigs in s, 'formSnapshot signatures block not found'
s = s.replace(old_sigs, new_sigs, 1)

restore_marker = '''    meterPhotos=snapshot.meterPhotos&&typeof snapshot.meterPhotos==="object"?JSON.parse(JSON.stringify(snapshot.meterPhotos)):{electric:[],water:[],gas:[]};
    currentRoom=snapshot.currentRoom||selectedRooms[0]||"Flur";'''
restore_new = '''    meterPhotos=snapshot.meterPhotos&&typeof snapshot.meterPhotos==="object"?JSON.parse(JSON.stringify(snapshot.meterPhotos)):{electric:[],water:[],gas:[]};
    savedSignatureState={
      tenant:snapshot.signatures?.tenant||"",
      landlord:snapshot.signatures?.landlord||"",
      tenantPlace:snapshot.fields?.tenantSignaturePlace||"",
      landlordPlace:snapshot.fields?.landlordSignaturePlace||"",
      date:snapshot.fields?.signatureDate||""
    };
    currentRoom=snapshot.currentRoom||selectedRooms[0]||"Flur";'''
assert restore_marker in s, 'restore marker not found'
s = s.replace(restore_marker, restore_new, 1)

old_stop = '''  const stop=()=>{drawing=false;};
  c.addEventListener("pointerup",stop);
  c.addEventListener("pointercancel",stop);
  c.addEventListener("pointerleave",e=>{if(e.buttons===0)drawing=false;});'''
new_stop = '''  const stop=()=>{
    if(!drawing) return;
    drawing=false;
    storeSignatureCanvas(id,c);
    saveDraft();
    queueTransferAutosave();
  };
  c.addEventListener("pointerup",stop);
  c.addEventListener("pointercancel",stop);
  c.addEventListener("pointerleave",e=>{if(e.buttons===0)stop();});'''
assert old_stop in s, 'signature stop block not found'
s = s.replace(old_stop, new_stop, 1)

old_clear = '''function clearSignature(id){
  const c=document.getElementById(id); if(!c)return;
  c.getContext("2d").clearRect(0,0,c.width,c.height);
  saveDraft();
}'''
new_clear = '''function clearSignature(id){
  const c=document.getElementById(id); if(!c)return;
  c.getContext("2d").clearRect(0,0,c.width,c.height);
  if(id==="sigTenant") savedSignatureState.tenant="";
  if(id==="sigLandlord") savedSignatureState.landlord="";
  saveDraft();
  queueTransferAutosave();
}'''
assert old_clear in s, 'clearSignature block not found'
s = s.replace(old_clear, new_clear, 1)

setup_marker = '''  go(5);
  setupSignature("sigTenant");
  setupSignature("sigLandlord");

  const sigDate = document.getElementById("signatureDate");
  const today = new Date();
  const localToday = new Date(today.getTime() - today.getTimezoneOffset() * 60000).toISOString().slice(0,10);
  if(sigDate && !sigDate.value) sigDate.value = localToday;

  const updateSignatureDetails = () => {
    const formatted = sigDate && sigDate.value
      ? new Date(sigDate.value + "T12:00:00").toLocaleDateString("de-DE")
      : "–";
    const tenantPlace = document.getElementById("tenantSignaturePlace")?.value.trim() || "–";
    const landlordPlace = document.getElementById("landlordSignaturePlace")?.value.trim() || "–";'''
setup_new = '''  go(5);
  setupSignature("sigTenant");
  setupSignature("sigLandlord");

  const sigDate = document.getElementById("signatureDate");
  const tenantPlaceInput=document.getElementById("tenantSignaturePlace");
  const landlordPlaceInput=document.getElementById("landlordSignaturePlace");
  if(tenantPlaceInput) tenantPlaceInput.value=savedSignatureState.tenantPlace||"";
  if(landlordPlaceInput) landlordPlaceInput.value=savedSignatureState.landlordPlace||"";
  const today = new Date();
  const localToday = new Date(today.getTime() - today.getTimezoneOffset() * 60000).toISOString().slice(0,10);
  if(sigDate) sigDate.value=savedSignatureState.date||sigDate.value||localToday;
  if(savedSignatureState.tenant) restoreSignatureImage("sigTenant",savedSignatureState.tenant);
  if(savedSignatureState.landlord) restoreSignatureImage("sigLandlord",savedSignatureState.landlord);

  const updateSignatureDetails = () => {
    savedSignatureState.tenantPlace=tenantPlaceInput?.value.trim()||"";
    savedSignatureState.landlordPlace=landlordPlaceInput?.value.trim()||"";
    savedSignatureState.date=sigDate?.value||"";
    const formatted = sigDate && sigDate.value
      ? new Date(sigDate.value + "T12:00:00").toLocaleDateString("de-DE")
      : "–";
    const tenantPlace = savedSignatureState.tenantPlace || "–";
    const landlordPlace = savedSignatureState.landlordPlace || "–";'''
assert setup_marker in s, 'summary signature setup block not found'
s = s.replace(setup_marker, setup_new, 1)

start_marker = '''  try{
    clearDraft();
    selectedRooms=["Flur","Wohnzimmer","Schlafzimmer","Küche","Badezimmer"];'''
start_new = '''  try{
    clearDraft();
    resetSavedSignatureState();
    selectedRooms=["Flur","Wohnzimmer","Schlafzimmer","Küche","Badezimmer"];'''
assert start_marker in s, 'startApp marker not found'
s = s.replace(start_marker, start_new, 1)

p.write_text(s, encoding='utf-8')
