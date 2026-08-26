from pathlib import Path

p = Path('index.html')
s = p.read_text(encoding='utf-8')


def between(start_marker, end_marker, replacement):
    global s
    start = s.find(start_marker)
    end = s.find(end_marker, start)
    assert start != -1, f'missing start: {start_marker}'
    assert end != -1, f'missing end: {end_marker}'
    s = s[:start] + replacement + s[end:]


# Avoid storing the current room photos twice in every transfer snapshot.
s = s.replace('    photoURLs:Array.isArray(photoURLs)?[...photoURLs]:[],\n', '')

# Compress new phone photos before they ever enter Supabase.
between('function fileToDataURL(file){', 'function saveRoomAndNext(){', '''function readFileAsDataURL(file){
  return new Promise((resolve,reject)=>{
    const reader=new FileReader();
    reader.onload=()=>resolve(reader.result);
    reader.onerror=reject;
    reader.readAsDataURL(file);
  });
}

function compressImageDataURL(dataUrl,maxEdge=1600,quality=.78){
  return new Promise((resolve,reject)=>{
    if(typeof dataUrl!=="string" || !dataUrl.startsWith("data:image/")){resolve(dataUrl);return;}
    const img=new Image();
    img.onload=()=>{
      try{
        const width=img.naturalWidth||img.width;
        const height=img.naturalHeight||img.height;
        const scale=Math.min(1,maxEdge/Math.max(width,height));
        if(scale>=1 && dataUrl.length<350000){resolve(dataUrl);return;}
        const canvas=document.createElement("canvas");
        canvas.width=Math.max(1,Math.round(width*scale));
        canvas.height=Math.max(1,Math.round(height*scale));
        const ctx=canvas.getContext("2d");
        ctx.fillStyle="#fff";
        ctx.fillRect(0,0,canvas.width,canvas.height);
        ctx.drawImage(img,0,0,canvas.width,canvas.height);
        resolve(canvas.toDataURL("image/jpeg",quality));
      }catch(error){reject(error);}
    };
    img.onerror=()=>reject(new Error("IMAGE_DECODE_FAILED"));
    img.src=dataUrl;
  });
}

async function fileToDataURL(file){
  const raw=await readFileAsDataURL(file);
  if(!file?.type?.startsWith("image/")) return raw;
  try{return await compressImageDataURL(raw);}catch(error){console.warn("Bildkomprimierung:",error);return raw;}
}

async function compactSnapshotMedia(snapshot){
  const cache=new Map();
  const compact=async value=>{
    if(typeof value!=="string" || !value.startsWith("data:image/") || value.length<350000) return value;
    if(cache.has(value)) return cache.get(value);
    const promise=compressImageDataURL(value).catch(()=>value);
    cache.set(value,promise);
    return promise;
  };
  for(const room of Object.values(snapshot.roomData||{})){
    if(Array.isArray(room?.photos)) room.photos=await Promise.all(room.photos.map(compact));
  }
  for(const type of ["electric","water","gas"]){
    if(Array.isArray(snapshot.meterPhotos?.[type])) snapshot.meterPhotos[type]=await Promise.all(snapshot.meterPhotos[type].map(compact));
  }
  delete snapshot.photoURLs;
  return snapshot;
}

''')

# Browser draft must stay tiny; the central Business record remains the source of truth.
between('function saveDraft(){', 'function loadDraft(){', '''function lightweightDraftSnapshot(){
  const ids=["address","date","tenant","landlord","electricNo","electric","waterNo","water","gasNo","gas","keys","notes"];
  const fields={};
  ids.forEach(id=>{const el=document.getElementById(id);fields[id]=el?(el.value??""):"";});
  fields.tenantSignaturePlace=document.getElementById("tenantSignaturePlace")?.value??storedSignatureDetails.tenantPlace??"";
  fields.landlordSignaturePlace=document.getElementById("landlordSignaturePlace")?.value??storedSignatureDetails.landlordPlace??"";
  fields.signatureDate=document.getElementById("signatureDate")?.value??storedSignatureDetails.date??"";
  const lightRooms={};
  Object.entries(roomData||{}).forEach(([name,room])=>{
    lightRooms[name]={state:room?.state||"ok",description:room?.description||"",defectStatus:room?.defectStatus||"",defectNote:room?.defectNote||"",photos:[]};
  });
  return {version:3,fields,tenantName:fields.tenant||"",tenantSurname:getTenantSurname(),selectedRooms:[...selectedRooms],roomData:lightRooms,customRooms:[...customRooms],currentRoom:currentRoom||"",currentState:currentState||"ok",savedAt:new Date().toISOString()};
}

function saveDraft(){
  try{
    sessionStorage.setItem("uebergabecheck_draft",JSON.stringify(lightweightDraftSnapshot()));
    const el=document.getElementById("saveStatus");
    if(el) el.textContent="Gespeichert";
  }catch(e){}
}
''')

# Do not send the whole transfer to Supabase on every keystroke.
between('function addAutosaveListeners(){', 'function makeSignatureCanvas(id){', '''function addAutosaveListeners(){
  if(autosaveListenersBound) return;
  autosaveListenersBound=true;
  document.querySelectorAll("input, textarea, select").forEach(el=>{
    el.addEventListener("input",()=>saveDraft());
    el.addEventListener("change",()=>{saveDraft();queueTransferAutosave();});
  });
}
''')

between('function queueTransferAutosave(){', 'async function saveTransferDataToDatabase(showMessage=false){', '''function queueTransferAutosave(){
  if(!window.currentBusinessTransferId) return;
  clearTimeout(transferAutosaveTimer);
  transferAutosaveTimer=setTimeout(()=>saveTransferDataToDatabase(false),1800);
}

function buildTransferMetadata(snapshot){
  const defects=Object.entries(snapshot?.roomData||{}).filter(([,room])=>room?.state==="damage").map(([roomName,room])=>({
    roomName,
    description:room?.description||"",
    defectNote:room?.defectNote||"",
    defectStatus:room?.defectStatus||"open"
  }));
  return {
    tenant_name:snapshot?.tenantName||snapshot?.fields?.tenant||"",
    tenant_surname:snapshot?.tenantSurname||"",
    open_defect_count:defects.filter(d=>d.defectStatus!=="resolved").length,
    defects_summary:defects
  };
}

''')

between('async function saveTransferDataToDatabase(showMessage=false){', 'async function persistCurrentTransfer(){', '''async function saveTransferDataToDatabase(showMessage=false){
  const transferId=window.currentBusinessTransferId;
  if(!transferId || !supabaseClient) return false;
  try{
    let snapshot=await compactSnapshotMedia(formSnapshot());
    const metadata=buildTransferMetadata(snapshot);
    const {error}=await supabaseClient.from("transfers").update({data:snapshot,status:"Gespeichert",...metadata}).eq("id",transferId);
    if(error){
      console.error("Automatisches Speichern der Übergabe:",error);
      if(showMessage) alert("Die Übergabe konnte nicht gespeichert werden.\n\n"+(error.message||"Unbekannter Fehler"));
      return false;
    }
    roomData=snapshot.roomData||roomData;
    meterPhotos=snapshot.meterPhotos||meterPhotos;
    photoURLs=roomData[currentRoom]?.photos||[];
    const status=document.getElementById("saveStatus");
    if(status) status.textContent="Automatisch gespeichert";
    return true;
  }catch(error){
    console.error("Autosave:",error);
    if(showMessage) alert("Die Übergabe konnte nicht gespeichert werden.");
    return false;
  }
}

''')

between('async function persistCurrentTransfer(){', 'function returnToBusinessDashboard(){', '''async function persistCurrentTransfer(){
  const transferId=window.currentBusinessTransferId;
  const apartmentId=window.currentBusinessApartmentId||selectedApartmentId;
  if(!transferId||!apartmentId){alert("Diese Übergabe ist noch nicht mit einer Wohnung verknüpft.");return false;}
  let snapshot=await compactSnapshotMedia(formSnapshot());
  const metadata=buildTransferMetadata(snapshot);
  const {error}=await supabaseClient.from("transfers").update({data:snapshot,status:"Gespeichert",...metadata}).eq("id",transferId);
  if(error){
    console.error("Übergabe speichern:",error);
    alert("Die Übergabe konnte nicht gespeichert werden.\n\n"+(error.message||"Unbekannter Fehler"));
    return false;
  }
  roomData=snapshot.roomData||roomData;
  meterPhotos=snapshot.meterPhotos||meterPhotos;
  photoURLs=roomData[currentRoom]?.photos||[];
  window.currentBusinessTransferId=transferId;
  clearDraft();
  return true;
}

''')

s=s.replace('let businessDataLoading = false;', 'let businessDataLoading = false;\nlet businessDataLoadedForUser = null;')

# Dashboard load: fetch only tiny metadata, never every photo/signature JSON payload.
between('async function loadBusinessData(user){', 'function hideAuthAuxForms(){', '''async function loadBusinessData(user){
  if(!user||!supabaseClient) return;
  if(businessDataLoadedForUser===user.id){renderBusinessObjects();updateBusinessStats();return;}
  if(businessDataLoading) return;
  businessDataLoading=true;
  try{
    const companyId=await ensureBusinessCompany(user);
    const {data:objects,error:objectError}=await supabaseClient.from("objects").select("id,company_id,name,street,zip,city,note,created_at").eq("company_id",companyId).order("created_at",{ascending:true});
    if(objectError) throw objectError;
    businessObjects=objects||[];
    businessApartments={};
    apartmentTransfers={};
    const objectIds=businessObjects.map(o=>o.id);
    if(objectIds.length){
      const {data:apartments,error:apartmentError}=await supabaseClient.from("apartments").select("id,object_id,name,number,rooms,area,note,created_at").in("object_id",objectIds).order("created_at",{ascending:true});
      if(apartmentError) throw apartmentError;
      (apartments||[]).forEach(a=>{if(!businessApartments[a.object_id]) businessApartments[a.object_id]=[];businessApartments[a.object_id].push(a);});
      const apartmentIds=(apartments||[]).map(a=>a.id);
      if(apartmentIds.length){
        const {data:transfers,error:transferError}=await supabaseClient.from("transfers").select("id,apartment_id,type,status,created_at,tenant_name,tenant_surname,open_defect_count").in("apartment_id",apartmentIds).order("created_at",{ascending:true});
        if(transferError) throw transferError;
        (transfers||[]).forEach(t=>{
          if(!apartmentTransfers[t.apartment_id]) apartmentTransfers[t.apartment_id]=[];
          apartmentTransfers[t.apartment_id].push({id:t.id,type:t.type,created:t.created_at?new Date(t.created_at).toLocaleDateString("de-DE"):"",status:t.status,tenantName:t.tenant_name||"",tenantSurname:t.tenant_surname||"",openDefectCount:Number(t.open_defect_count||0)});
        });
      }
    }
    businessDataLoadedForUser=user.id;
    renderBusinessObjects();
    updateBusinessStats();
  }catch(error){
    businessDataLoadedForUser=null;
    console.error("Business-Daten:",error);
    alert("Die Business-Daten konnten nicht geladen werden. Bitte prüfe die Supabase-Datenbank.");
  }finally{businessDataLoading=false;}
}

''')

# Apartment transfer list also stays metadata-only until a transfer is explicitly opened.
between('async function renderApartmentTransfers(){', 'async function openObject(id){', '''async function renderApartmentTransfers(){
  const list=document.getElementById("apartmentTransfers");
  if(!list || selectedApartmentId===null) return;
  if(!supabaseClient || !supabaseUser){list.innerHTML='<div class="empty-state">Bitte zuerst anmelden.</div>';return;}
  list.innerHTML='<div class="empty-state">Übergaben werden geladen …</div>';
  const {data:rows,error}=await supabaseClient.from("transfers").select("id,type,status,created_at,apartment_id,tenant_name,tenant_surname,open_defect_count").eq("apartment_id",selectedApartmentId).order("created_at",{ascending:false});
  if(error){console.error("Wohnungsübergaben laden:",error);list.innerHTML='<div class="empty-state">Übergaben konnten nicht geladen werden.</div>';return;}
  apartmentTransfers[selectedApartmentId]=(rows||[]).map(t=>({id:t.id,type:t.type||"Wohnungsübergabe",created:t.created_at?new Date(t.created_at).toLocaleDateString("de-DE"):"–",status:t.status||"Neu",tenantName:t.tenant_name||"",tenantSurname:t.tenant_surname||"",openDefectCount:Number(t.open_defect_count||0)}));
  if(!rows?.length){list.innerHTML='<div class="empty-state">Noch keine Übergaben für diese Wohnung vorhanden.</div>';return;}
  const objectId=selectedBusinessObjectId;
  list.innerHTML=rows.map(t=>{
    const type=t.type||"Wohnungsübergabe";
    const date=t.created_at?new Date(t.created_at).toLocaleDateString("de-DE"):"–";
    const status=t.status||"Neu";
    const displayTitle=t.tenant_surname?`${t.tenant_surname} – ${type}`:type;
    return `<div class="transfer-item" style="cursor:pointer;" onclick="openBusinessTransfer('${escAttr(t.id)}','${escAttr(objectId)}','${escAttr(selectedApartmentId)}')"><div><strong>${esc(displayTitle)}</strong><small>Erstellt am ${esc(date)}</small></div><div class="transfer-actions"><span class="status active">${esc(status)}</span><button type="button" class="secondary" onclick="event.stopPropagation();openBusinessTransfer('${escAttr(t.id)}','${escAttr(objectId)}','${escAttr(selectedApartmentId)}')">Öffnen</button><button type="button" class="danger" onclick="event.stopPropagation();deleteBusinessTransfer('${escAttr(t.id)}','${escAttr(selectedApartmentId)}')">Löschen</button></div></div>`;
  }).join("");
  updateBusinessStats();
}

''')

# Object/dashboard counts are calculated from already-loaded metadata, not another database download.
between('async function updateObjectDetailStats(){', 'function resetObjectForm(){', '''async function updateObjectDetailStats(){
  if(selectedBusinessObjectId===null || selectedBusinessObjectId===undefined) return;
  const objectId=String(selectedBusinessObjectId);
  const apartments=businessApartments[selectedBusinessObjectId]||businessApartments[objectId]||[];
  const transferCount=apartments.reduce((sum,a)=>sum+(apartmentTransfers[a.id]||apartmentTransfers[String(a.id)]||[]).length,0);
  const defectCount=apartments.reduce((sum,a)=>sum+(apartmentTransfers[a.id]||apartmentTransfers[String(a.id)]||[]).reduce((n,t)=>n+Number(t.openDefectCount||0),0),0);
  const apartmentCount=document.getElementById("objectApartmentCount");
  const transferEl=document.getElementById("objectTransferCount");
  const defectEl=document.getElementById("objectOpenDefectCount");
  if(apartmentCount) apartmentCount.textContent=apartments.length;
  if(transferEl) transferEl.textContent=transferCount;
  if(defectEl) defectEl.textContent=defectCount;
}

''')

between('async function updateBusinessStats(){', 'function defectMetaText(d){', '''async function updateBusinessStats(){
  const stats=document.querySelectorAll(".dashboard-stat strong");
  const apartmentCount=Object.values(businessApartments||{}).reduce((total,list)=>total+(Array.isArray(list)?list.length:0),0);
  const transfers=Object.values(apartmentTransfers||{}).flatMap(list=>Array.isArray(list)?list:[]);
  const defectCount=transfers.reduce((sum,t)=>sum+Number(t.openDefectCount||0),0);
  if(stats[0]) stats[0].textContent=businessObjects.length;
  if(stats[1]) stats[1].textContent=apartmentCount;
  if(stats[2]) stats[2].textContent=transfers.length;
  if(stats[3]) stats[3].textContent=defectCount;
  return defectCount;
}

''')

# Defect overview reads only the tiny defect summary column.
between('async function loadBusinessDefects(includeResolved=false){', 'async function updateBusinessStats(){', '''async function loadBusinessDefects(includeResolved=false){
  if(!supabaseClient || !supabaseUser) return [];
  let query=supabaseClient.from("transfers").select("id,type,status,created_at,apartment_id,tenant_name,tenant_surname,open_defect_count,defects_summary,apartments(id,name,number,object_id,objects(id,name))").order("created_at",{ascending:false});
  if(!includeResolved) query=query.gt("open_defect_count",0);
  const {data:rows,error}=await query;
  if(error){console.error("Mängel laden:",error);return [];}
  const defects=[];
  (rows||[]).forEach(t=>{
    const apartment=t.apartments;
    const object=apartment?.objects;
    (Array.isArray(t.defects_summary)?t.defects_summary:[]).forEach(defect=>{
      const defectStatus=defect?.defectStatus||"open";
      if(!includeResolved && defectStatus==="resolved") return;
      defects.push({transferId:t.id,objectId:object?.id||apartment?.object_id||"",apartmentId:apartment?.id||t.apartment_id||"",objectName:object?.name||"Objekt",apartmentName:apartment?.name||"Wohnung",apartmentNumber:apartment?.number||"",tenantName:t.tenant_name||"",tenantSurname:t.tenant_surname||"",roomName:defect?.roomName||"Raum",description:defect?.description||"Mangel vorhanden",defectNote:defect?.defectNote||"",defectStatus,createdAt:t.created_at||""});
    });
  });
  return defects;
}

''')

# The all-transfers view is metadata-only as well.
between('async function renderBusinessTransfers(){', 'async function renderDashboardCurrentTransfers(){', '''async function renderBusinessTransfers(){
  const container=document.getElementById("businessTransfersList");
  if(!container) return;
  if(!supabaseClient || !supabaseUser){container.innerHTML='<div class="empty-state">Bitte zuerst anmelden.</div>';return;}
  const {data:rows,error}=await supabaseClient.from("transfers").select("id,type,status,created_at,apartment_id,tenant_name,tenant_surname,open_defect_count,apartments(id,name,number,object_id,objects(id,name))").order("created_at",{ascending:false});
  if(error){console.error("Übergaben laden:",error);container.innerHTML='<div class="empty-state">Übergaben konnten nicht geladen werden.</div>';return;}
  if(!rows?.length){container.innerHTML='<div class="empty-state">Noch keine Übergaben vorhanden.</div>';return;}
  container.innerHTML=rows.map(t=>{
    const a=t.apartments;const o=a?.objects;
    const tenantName=t.tenant_name||"";const tenantSurname=t.tenant_surname||"";
    const date=t.created_at?new Date(t.created_at).toLocaleDateString("de-DE"):"–";
    const displayTitle=tenantSurname?`${tenantSurname} – ${t.type||"Wohnungsübergabe"}`:(t.type||"Wohnungsübergabe");
    return `<div class="transfer-item"><div><strong>${esc(displayTitle)}</strong><small>${esc(o?.name||"Objekt")} · ${esc(a?.name||"Wohnung")}${tenantName&&tenantName!==tenantSurname?" · "+esc(tenantName):""} · ${esc(date)}</small></div><div class="transfer-actions"><span class="status active">${esc(t.status||"Neu")}</span><button class="secondary" type="button" onclick="openBusinessTransfer('${escAttr(t.id)}','${escAttr(o?.id||"")}','${escAttr(a?.id||t.apartment_id||"")}')">Öffnen</button></div></div>`;
  }).join("");
}

''')

# Don't flash false zeros while the first lightweight query is still running.
between('function showBusinessDashboard(user=null){', 'function backToBusinessDashboard(){', '''function showBusinessDashboard(user=null){
  markBusinessDashboardHistory();
  const landing=document.getElementById("landing");
  const dashboard=document.getElementById("businessDashboard");
  const app=document.getElementById("appContent");
  landing.style.display="none";landing.classList.add("hidden");
  dashboard.classList.remove("hidden");dashboard.style.display="block";
  app.classList.add("hidden");app.style.display="none";
  document.getElementById("apartmentsOverviewCard")?.classList.add("hidden");
  document.getElementById("defectsOverviewCard")?.classList.add("hidden");
  document.getElementById("businessTransfersCard")?.classList.add("hidden");
  document.getElementById("objectsCard")?.classList.remove("hidden");
  document.querySelector(".dashboard-main")?.classList.remove("hidden");
  document.getElementById("businessSearchCard")?.classList.remove("hidden");
  document.querySelectorAll("#businessMainNav button").forEach(b=>b.classList.remove("active"));
  document.querySelector("#businessMainNav button")?.classList.add("active");
  const searchInput=document.getElementById("businessGlobalSearch");
  const searchResults=document.getElementById("businessSearchResults");
  if(searchInput) searchInput.value="";
  if(searchResults) searchResults.innerHTML='<div class="empty-state">Suchbegriff eingeben, um Treffer zu sehen.</div>';
  const activeUser=user||supabaseUser;
  const company=activeUser?.user_metadata?.company_name||document.getElementById("companyName")?.value.trim()||"";
  const dashboardCompany=document.getElementById("dashboardCompany");
  if(dashboardCompany) dashboardCompany.textContent=company?company+" · Zentrale Verwaltung":"Dein Unternehmen auf einen Blick.";
  if(businessDataLoadedForUser===activeUser?.id){renderBusinessObjects();updateBusinessStats();}
  else{
    document.querySelectorAll(".dashboard-stat strong").forEach(el=>el.textContent="…");
    const list=document.getElementById("objectsList");
    if(list) list.innerHTML='<div class="empty-state">Daten werden geladen …</div>';
    loadBusinessData(activeUser);
  }
  window.scrollTo({top:0,behavior:"smooth"});
}

''')

# Keep metadata in sync after defect edits.
s = s.replace('.update({\n      data:snapshot,\n      status:"Gespeichert"\n    })\n    .eq("id",transferId);', '.update({\n      data:snapshot,\n      status:"Gespeichert",\n      ...buildTransferMetadata(snapshot)\n    })\n    .eq("id",transferId);')
s = s.replace('.update({data:snapshot,status:"Gespeichert"})\n    .eq("id",transferId);', '.update({data:snapshot,status:"Gespeichert",...buildTransferMetadata(snapshot)})\n    .eq("id",transferId);')

# A different login must always receive its own fresh cache.
s = s.replace('  supabaseUser = null;\n\n  const dashboard=', '  supabaseUser = null;\n  businessDataLoadedForUser = null;\n  businessCompanyId = null;\n\n  const dashboard=')

p.write_text(s, encoding='utf-8')
