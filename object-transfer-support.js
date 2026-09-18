/* ÜbergabeCheck Business — Objektübergaben ohne Wohnung */
(function(){
  "use strict";
  if(window.__uebergabeCheckObjectTransferSupportInstalled)return;
  window.__uebergabeCheckObjectTransferSupportInstalled=true;

  function currentObject(){
    return (businessObjects||[]).find(item=>String(item?.id)===String(selectedBusinessObjectId))||null;
  }

  function objectAddress(object){
    if(!object)return "";
    const place=[object.zip,object.city].filter(Boolean).join(" ").trim();
    return [object.street,place].filter(Boolean).join(", ");
  }

  async function loadPreviousHandoverDefaults(object,apartment){
    if(!supabaseClient||!object)return null;
    try{
      let query=supabaseClient
        .from("transfers")
        .select("id,type,data,created_at")
        .eq("object_id",object.id)
        .order("created_at",{ascending:false})
        .limit(1);

      if(apartment){
        query=query.eq("apartment_id",apartment.id).eq("type","Wohnungsübergabe");
      }else{
        query=query.is("apartment_id",null).eq("type","Objektübergabe");
      }

      const {data:rows,error}=await query;
      if(error){
        console.error("Vorherige Übergabe laden:",error);
        return null;
      }

      const previous=(rows||[])[0]||null;
      if(!previous?.data)return null;

      let snapshot=previous.data;
      if(typeof snapshot==="string"){
        try{snapshot=JSON.parse(snapshot);}catch(_error){return null;}
      }
      if(snapshot?.data&&typeof snapshot.data==="object"&&!snapshot.fields)snapshot=snapshot.data;

      const fields=snapshot?.fields||{};
      return {
        transferId:previous.id,
        selectedRooms:Array.isArray(snapshot?.selectedRooms)?snapshot.selectedRooms.filter(Boolean):[],
        customRooms:Array.isArray(snapshot?.customRooms)?snapshot.customRooms.filter(Boolean):[],
        meterNumbers:{
          electricNo:String(fields.electricNo||""),
          waterNo:String(fields.waterNo||""),
          gasNo:String(fields.gasNo||"")
        }
      };
    }catch(error){
      console.error("Vorherige Übergabe übernehmen:",error);
      return null;
    }
  }

  function applyPreviousHandoverDefaults(defaults){
    if(!defaults)return false;

    if(defaults.selectedRooms.length){
      selectedRooms=[...defaults.selectedRooms];
      const derivedCustom=selectedRooms.filter(room=>!(baseRoomNames||[]).includes(room));
      customRooms=Array.from(new Set([...(defaults.customRooms||[]),...derivedCustom]));

      roomData={};
      selectedRooms.forEach(room=>{
        roomData[room]={
          state:"ok",
          description:"",
          photos:[],
          defectStatus:"open",
          defectNote:""
        };
      });
      currentRoom=selectedRooms[0]||"Flur";
      currentState="ok";
      photoURLs=[];
      if(typeof renderRooms==="function")renderRooms();
      if(typeof updateCustomRoomNote==="function")updateCustomRoomNote();
    }

    Object.entries(defaults.meterNumbers||{}).forEach(([id,value])=>{
      const input=document.getElementById(id);
      if(input&&value){
        input.value=value;
        input.dispatchEvent(new Event("input",{bubbles:true}));
      }
    });

    if(typeof saveDraft==="function")saveDraft();
    return defaults.selectedRooms.length>0||Object.values(defaults.meterNumbers||{}).some(Boolean);
  }

  window.startBusinessTransfer=function(){
    if(!requireBusinessWriteAccess())return;
    const modal=document.getElementById("transferStartModal");
    const objectSelect=document.getElementById("transferObjectSelect");
    const apartmentSelect=document.getElementById("transferApartmentSelect");
    if(!modal||!objectSelect||!apartmentSelect)return;

    if(typeof selectPendingTransferType==="function")selectPendingTransferType("handover");
    const intro=modal.querySelector(".transfer-start-box > p");
    if(intro)intro.textContent="Wähle Übergabe oder Rücknahme und anschließend das Objekt. Eine Wohnung kannst du optional auswählen.";
    const apartmentLabel=modal.querySelector('label[for="transferApartmentSelect"]');
    if(apartmentLabel)apartmentLabel.textContent="Wohnung / Einheit (optional)";

    objectSelect.innerHTML='<option value="">Objekt auswählen …</option>'+
      (businessObjects||[]).map(o=>`<option value="${escAttr(o.id)}">${esc(o.name)}</option>`).join("");
    apartmentSelect.innerHTML='<option value="">Gesamtes Objekt / Haus – ohne Wohnung</option>';

    modal.classList.remove("hidden");
    modal.style.display="flex";
  };

  window.populateTransferApartmentSelect=function(){
    const objectId=document.getElementById("transferObjectSelect")?.value||"";
    const apartmentSelect=document.getElementById("transferApartmentSelect");
    if(!apartmentSelect)return;
    const apartments=businessApartments?.[objectId]||[];
    apartmentSelect.innerHTML='<option value="">Gesamtes Objekt / Haus – ohne Wohnung</option>'+
      apartments.map(a=>`<option value="${escAttr(a.id)}">${esc(a.name)}</option>`).join("");
  };

  window.confirmTransferStart=async function(){
    if(!requireBusinessWriteAccess())return;
    const objectId=document.getElementById("transferObjectSelect")?.value||"";
    const apartmentId=document.getElementById("transferApartmentSelect")?.value||"";
    const transferMode=typeof getPendingTransferType==="function"?getPendingTransferType():normalizeTransferType(document.querySelector('input[name="transferType"]:checked')?.value);
    if(!objectId){
      alert("Bitte zuerst ein Objekt auswählen.");
      return;
    }

    selectedBusinessObjectId=objectId;
    selectedApartmentId=apartmentId||null;
    window.currentBusinessObjectId=objectId;
    window.currentBusinessApartmentId=apartmentId||null;
    window.currentBusinessTransferType=transferMode;
    closeTransferStart();
    await window.startApartmentTransfer(transferMode);
  };

  window.startApartmentTransfer=async function(requestedType){
    if(!requireBusinessWriteAccess())return;
    const transferMode=normalizeTransferType(requestedType||window.currentBusinessTransferType);
    const object=currentObject();
    if(!object){
      alert("Das ausgewählte Objekt konnte nicht gefunden werden.");
      return;
    }

    const apartment=selectedApartmentId?getSelectedApartment():null;
    if(selectedApartmentId&&!apartment){
      alert("Die ausgewählte Wohnung konnte nicht gefunden werden.");
      return;
    }

    const isReturn=transferMode==="Wohnungsrücknahme";
    const previousHandoverDefaults=isReturn
      ? await loadPreviousHandoverDefaults(object,apartment)
      : null;

    const payload={
      object_id:object.id,
      apartment_id:apartment?.id||null,
      type:apartment?(isReturn?"Wohnungsrücknahme":"Wohnungsübergabe"):(isReturn?"Objektrücknahme":"Objektübergabe"),
      status:"Neu",
      data:{transferType:transferMode}
    };

    const {data:transfer,error}=await supabaseClient
      .from("transfers")
      .insert(payload)
      .select()
      .single();

    if(error){
      console.error("Übergabe speichern:",error);
      alert("Die Übergabe konnte nicht angelegt werden.\n\n"+(error.message||"Unbekannter Fehler"));
      return;
    }

    window.currentBusinessObjectId=object.id;
    window.currentBusinessApartmentId=apartment?.id||null;
    window.currentBusinessTransferId=transfer.id;
    window.currentBusinessTransferType=transferMode;
    if(typeof applyTransferTypeUi==="function")applyTransferTypeUi();
    window.currentBusinessTransferCreatedByName=transfer.created_by_name||"";

    if(apartment){
      if(!apartmentTransfers[apartment.id])apartmentTransfers[apartment.id]=[];
      apartmentTransfers[apartment.id].push({
        id:transfer.id,
        type:transfer.type,
        created:new Date(transfer.created_at).toLocaleDateString("de-DE"),
        status:transfer.status,
        createdByName:transfer.created_by_name||"",
        openDefectCount:0
      });
    }

    await updateBusinessStats();
    await updateObjectDetailStats();
    startApp();

    if(isReturn&&previousHandoverDefaults){
      const imported=applyPreviousHandoverDefaults(previousHandoverDefaults);
      if(imported){
        const context=document.getElementById("transferContext");
        if(context&&!context.querySelector(".return-import-note")){
          const note=document.createElement("span");
          note.className="return-import-note";
          note.style.cssText="font-size:11px;font-weight:700;text-transform:none;letter-spacing:0;color:#666;margin-left:auto;";
          note.textContent="Räume & Zählernummern aus letzter Übergabe übernommen";
          context.appendChild(note);
        }
      }
    }

    const addressInput=document.getElementById("address");
    if(addressInput&&!addressInput.value){
      const address=objectAddress(object);
      if(address){
        addressInput.value=address;
        addressInput.dispatchEvent(new Event("input",{bubbles:true}));
      }
    }
  };

  window.persistCurrentTransfer=async function(){
    if(!requireBusinessWriteAccess())return false;
    const transferId=window.currentBusinessTransferId;
    if(!transferId){
      alert("Diese Übergabe ist noch nicht mit einem Objekt verknüpft.");
      return false;
    }
    let snapshot=await compactSnapshotMedia(formSnapshot());
    const metadata=buildTransferMetadata(snapshot);
    const transferDbType=typeof getCurrentTransferDbType==="function"?getCurrentTransferDbType():(normalizeTransferType(window.currentBusinessTransferType)==="Wohnungsrücknahme"?"Wohnungsrücknahme":"Wohnungsübergabe");
    const {error}=await supabaseClient.from("transfers").update({data:snapshot,status:"Gespeichert",type:transferDbType,...metadata}).eq("id",transferId);
    if(error){
      console.error("Übergabe speichern:",error);
      alert("Die Übergabe konnte nicht gespeichert werden.\n\n"+(error.message||"Unbekannter Fehler"));
      return false;
    }
    roomData=snapshot.roomData||roomData;
    meterPhotos=snapshot.meterPhotos||meterPhotos;
    photoURLs=roomData[currentRoom]?.photos||[];
    clearDraft();
    return true;
  };

  window.openBusinessTransfer=async function(transferId,objectId,apartmentId){
    const {data:transfer,error}=await supabaseClient
      .from("transfers")
      .select("id,data,status,apartment_id,object_id,created_by_name,type")
      .eq("id",transferId)
      .single();

    if(error||!transfer){
      console.error("Übergabe laden:",error);
      alert("Die Übergabe konnte nicht geladen werden.\n\n"+(error?.message||"Unbekannter Fehler"));
      return;
    }

    const resolvedObjectId=transfer.object_id||objectId||null;
    const resolvedApartmentId=transfer.apartment_id||apartmentId||null;
    let apartment=null;
    if(resolvedApartmentId){
      apartment=getApartmentById(resolvedApartmentId);
      if(!apartment){
        alert("Die Wohnung dieser Übergabe konnte nicht gefunden werden.");
        return;
      }
    }

    selectedBusinessObjectId=resolvedObjectId||selectedBusinessObjectId;
    selectedApartmentId=resolvedApartmentId||null;
    window.currentBusinessObjectId=resolvedObjectId||null;
    window.currentBusinessApartmentId=resolvedApartmentId||null;
    window.currentBusinessTransferId=transferId;
    window.currentBusinessTransferType=normalizeTransferType(transfer.type||transfer.data?.transferType);
    window.currentBusinessTransferCreatedByName=transfer.created_by_name||"";

    startApp();
    if(transfer.data)restoreTransferSnapshot(transfer.data);
    else{
      const status=document.getElementById("saveStatus");
      if(status)status.textContent="Noch keine gespeicherten Angaben";
    }
    addAutosaveListeners();
  };

  window.renderBusinessTransfers=async function(){
    const container=document.getElementById("businessTransfersList");
    if(!container)return;
    if(!supabaseClient||!supabaseUser){container.innerHTML='<div class="empty-state">Bitte zuerst anmelden.</div>';return;}

    const {data:rows,error}=await supabaseClient.from("transfers")
      .select("id,type,status,created_at,object_id,apartment_id,tenant_name,tenant_surname,open_defect_count,created_by_name,objects(id,name),apartments(id,name,number,object_id)")
      .order("created_at",{ascending:false});
    if(error){console.error("Übergaben laden:",error);container.innerHTML='<div class="empty-state">Übergaben konnten nicht geladen werden.</div>';return;}
    if(!rows?.length){container.innerHTML='<div class="empty-state">Noch keine Übergaben vorhanden.</div>';return;}

    container.innerHTML=rows.map(t=>{
      const a=t.apartments||null;
      const o=t.objects||(businessObjects||[]).find(item=>String(item.id)===String(t.object_id))||null;
      const tenantName=t.tenant_name||"";
      const tenantSurname=t.tenant_surname||"";
      const date=t.created_at?new Date(t.created_at).toLocaleDateString("de-DE"):"–";
      const displayTitle=tenantSurname?`${tenantSurname} – ${t.type||"Übergabe"}`:(t.type||"Übergabe");
      const unit=a?.name||"Gesamtes Objekt";
      return `<div class="transfer-item"><div><strong>${esc(displayTitle)}</strong><small>${esc(o?.name||"Objekt")} · ${esc(unit)}${tenantName&&tenantName!==tenantSurname?" · "+esc(tenantName):""} · ${esc(date)}${t.created_by_name?" · Erstellt von: "+esc(t.created_by_name):""}</small></div><div class="transfer-actions"><span class="status active">${esc(t.status||"Neu")}</span><button class="secondary" type="button" onclick="openBusinessTransfer('${escAttr(t.id)}','${escAttr(t.object_id||o?.id||"")}','${escAttr(t.apartment_id||a?.id||"")}')">Öffnen</button><button class="danger" type="button" onclick="deleteBusinessTransfer('${escAttr(t.id)}','${escAttr(t.apartment_id||"")}')">Löschen</button></div></div>`;
    }).join("");
  };

  window.renderDashboardCurrentTransfers=async function(){
    const container=document.getElementById("dashboardCurrentTransfers");
    if(!container||!supabaseClient||!supabaseUser)return;
    const {data:rows,error}=await supabaseClient.from("transfers")
      .select("id,type,status,created_at,object_id,apartment_id,data,created_by_name,objects(id,name),apartments(id,name)")
      .order("created_at",{ascending:false})
      .limit(5);
    if(error){console.error("Aktuelle Übergaben laden:",error);return;}
    if(!rows?.length){container.innerHTML='<div class="empty-state">Noch keine Übergaben vorhanden.<br>Starte deine erste Übergabe, um hier die Vorgänge deiner Verwaltung zu sehen.</div>';return;}

    container.innerHTML=rows.map(t=>{
      const a=t.apartments||null;
      const o=t.objects||(businessObjects||[]).find(item=>String(item.id)===String(t.object_id))||null;
      const tenantSurname=t.data?.tenantSurname||"";
      const displayTitle=tenantSurname?`${tenantSurname} – ${t.type||"Übergabe"}`:(t.type||"Übergabe");
      return `<div class="transfer-item"><div><strong>${esc(displayTitle)}</strong><small>${esc(o?.name||"Objekt")} · ${esc(a?.name||"Gesamtes Objekt")}${t.created_by_name?" · Erstellt von: "+esc(t.created_by_name):""}</small></div><div class="transfer-actions"><span class="status active">${esc(t.status||"Neu")}</span><button class="secondary" type="button" onclick="openBusinessTransfer('${escAttr(t.id)}','${escAttr(t.object_id||o?.id||"")}','${escAttr(t.apartment_id||a?.id||"")}')">Öffnen</button></div></div>`;
    }).join("");
  };

  window.updateBusinessStats=async function(){
    const stats=document.querySelectorAll(".dashboard-stat strong");
    const apartmentCount=Object.values(businessApartments||{}).reduce((total,list)=>total+(Array.isArray(list)?list.length:0),0);
    let transferCount=0;
    let defectCount=0;
    if(supabaseClient&&supabaseUser){
      const {data,error}=await supabaseClient.from("transfers").select("id,open_defect_count");
      if(!error){
        transferCount=(data||[]).length;
        defectCount=(data||[]).reduce((sum,t)=>sum+Number(t.open_defect_count||0),0);
      }
    }
    if(stats[0])stats[0].textContent=(businessObjects||[]).length;
    if(stats[1])stats[1].textContent=apartmentCount;
    if(stats[2])stats[2].textContent=transferCount;
    if(stats[3])stats[3].textContent=defectCount;
    return defectCount;
  };

  window.updateObjectDetailStats=async function(){
    if(selectedBusinessObjectId===null||selectedBusinessObjectId===undefined)return;
    const apartments=businessApartments?.[selectedBusinessObjectId]||businessApartments?.[String(selectedBusinessObjectId)]||[];
    const {data,error}=await supabaseClient.from("transfers").select("id,open_defect_count").eq("object_id",selectedBusinessObjectId);
    const rows=error?[]:(data||[]);
    const apartmentCount=document.getElementById("objectApartmentCount");
    const transferEl=document.getElementById("objectTransferCount");
    const defectEl=document.getElementById("objectOpenDefectCount");
    if(apartmentCount)apartmentCount.textContent=apartments.length;
    if(transferEl)transferEl.textContent=rows.length;
    if(defectEl)defectEl.textContent=rows.reduce((sum,t)=>sum+Number(t.open_defect_count||0),0);
  };

  window.loadBusinessDefects=async function(includeResolved=false){
    if(!supabaseClient||!supabaseUser)return [];
    let query=supabaseClient.from("transfers")
      .select("id,type,status,created_at,object_id,apartment_id,tenant_name,tenant_surname,open_defect_count,defects_summary,objects(id,name),apartments(id,name,number)")
      .order("created_at",{ascending:false});
    if(!includeResolved)query=query.gt("open_defect_count",0);
    const {data:rows,error}=await query;
    if(error){console.error("Mängel laden:",error);return [];}
    const defects=[];
    (rows||[]).forEach(t=>{
      const apartment=t.apartments||null;
      const object=t.objects||(businessObjects||[]).find(item=>String(item.id)===String(t.object_id))||null;
      (Array.isArray(t.defects_summary)?t.defects_summary:[]).forEach(defect=>{
        const defectStatus=defect?.defectStatus||"open";
        if(!includeResolved&&defectStatus==="resolved")return;
        defects.push({
          transferId:t.id,
          objectId:t.object_id||object?.id||"",
          apartmentId:t.apartment_id||apartment?.id||"",
          objectName:object?.name||"Objekt",
          apartmentName:apartment?.name||"Gesamtes Objekt",
          apartmentNumber:apartment?.number||"",
          tenantName:t.tenant_name||"",
          tenantSurname:t.tenant_surname||"",
          roomName:defect?.roomName||"Raum",
          description:defect?.description||"Mangel vorhanden",
          defectNote:defect?.defectNote||"",
          defectStatus,
          createdAt:t.created_at||""
        });
      });
    });
    return defects;
  };

  // Bestehende Seite sofort an die neue Auswahl anpassen.
  const modal=document.getElementById("transferStartModal");
  if(modal){
    const intro=modal.querySelector(".transfer-start-box > p");
    if(intro)intro.textContent="Wähle das Objekt aus. Eine Wohnung ist optional.";
    const label=modal.querySelector('label[for="transferApartmentSelect"]');
    if(label)label.textContent="Wohnung / Einheit (optional)";
  }
})();
