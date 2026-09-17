/* ÜbergabeCheck Business — Support, Admin & Textbausteine */
(function(){
  "use strict";
  if(window.__uebergabeCheckBusinessToolsInstalled)return;
  window.__uebergabeCheckBusinessToolsInstalled=true;

  const SUPABASE_URL="https://fkirkglhcpltxlcsozmd.supabase.co";
  const SUPABASE_KEY="sb_publishable_lNeX7Hrtp9-FFl3NVb_Gaw_O-21yXWr";
  let client=null;
  let companyId=null;
  let textBlocks=[];
  let appliedTextBlocks=[];
  let editingTextBlockId=null;
  let wrappersInstalled=false;

  function db(){
    if(client)return client;
    if(!window.supabase?.createClient)return null;
    client=window.supabase.createClient(SUPABASE_URL,SUPABASE_KEY);
    return client;
  }

  function esc(value){
    return String(value??"").replace(/[&<>\"']/g,ch=>({"&":"&amp;","<":"&lt;",">":"&gt;",'\"':"&quot;","'":"&#039;"}[ch]));
  }

  function clone(value){
    try{return JSON.parse(JSON.stringify(value));}catch(_error){return value;}
  }

  function dashboardActions(){
    return document.querySelector("#businessDashboard .dashboard-top .dashboard-actions");
  }

  function addSupportButton(){
    const actions=dashboardActions();
    if(!actions||document.getElementById("businessSupportButton"))return;
    const button=document.createElement("button");
    button.id="businessSupportButton";
    button.type="button";
    button.className="secondary";
    button.textContent="💬 Support & Ideen";
    button.onclick=()=>{location.href="support.html";};
    const logout=[...actions.querySelectorAll("button")].find(b=>String(b.getAttribute("onclick")||"").includes("businessLogout"));
    if(logout)actions.insertBefore(button,logout);else actions.appendChild(button);
  }

  function addAdminButton(){
    const actions=dashboardActions();
    if(!actions||document.getElementById("businessInternalAdminButton"))return;
    const button=document.createElement("button");
    button.id="businessInternalAdminButton";
    button.type="button";
    button.className="secondary";
    button.textContent="◆ Admin";
    button.onclick=()=>{location.href="admin.html";};
    const logout=[...actions.querySelectorAll("button")].find(b=>String(b.getAttribute("onclick")||"").includes("businessLogout"));
    if(logout)actions.insertBefore(button,logout);else actions.appendChild(button);
  }

  function removeAdminButton(){document.getElementById("businessInternalAdminButton")?.remove();}

  function installStyles(){
    if(document.getElementById("ucTextBlockStyles"))return;
    const style=document.createElement("style");
    style.id="ucTextBlockStyles";
    style.textContent=`
      .uc-textblock-card{grid-column:1/-1;margin:0!important}
      .uc-textblock-toolbar{display:flex;justify-content:space-between;align-items:flex-start;gap:14px;margin-bottom:16px}
      .uc-textblock-toolbar p{margin:5px 0 0;color:#73757b;font-size:13px;line-height:1.5}
      .uc-textblock-form{border:1px solid #e2e3e6;background:#fafafa;border-radius:16px;padding:16px;margin-bottom:16px}
      .uc-textblock-grid{display:grid;grid-template-columns:repeat(3,1fr);gap:10px}
      .uc-textblock-form label{margin-top:10px}
      .uc-textblock-form textarea{min-height:125px}
      .uc-textblock-form-actions{display:flex;justify-content:flex-end;gap:9px;margin-top:12px}
      .uc-textblock-list{display:grid;gap:9px}
      .uc-textblock-item{border:1px solid #e1e2e5;border-radius:14px;padding:14px;background:#fff}
      .uc-textblock-item-head{display:flex;justify-content:space-between;gap:14px;align-items:flex-start}
      .uc-textblock-path{font-weight:800;font-size:13px;line-height:1.45}
      .uc-textblock-copy{font-size:12px;color:#6f7177;line-height:1.55;margin-top:6px;white-space:pre-wrap;display:-webkit-box;-webkit-line-clamp:3;-webkit-box-orient:vertical;overflow:hidden}
      .uc-textblock-actions{display:flex;gap:6px;flex:0 0 auto}
      .uc-textblock-actions button{padding:7px 9px;font-size:11px}
      .uc-textblock-builder{margin:18px 0 4px;padding:17px;border:1px solid #dfe1e5;background:#fafafa;border-radius:16px}
      .uc-textblock-builder h3{margin:0 0 5px;font-size:16px}
      .uc-textblock-builder>p{margin:0 0 12px;color:#73757b;font-size:12px;line-height:1.5}
      .uc-textblock-selects{display:grid;grid-template-columns:repeat(3,1fr);gap:9px}
      .uc-textblock-add{display:flex;justify-content:flex-end;margin-top:10px}
      .uc-applied-list{display:grid;gap:9px;margin-top:12px}
      .uc-applied-item{background:#fff;border:1px solid #dfe1e5;border-radius:13px;padding:12px}
      .uc-applied-head{display:flex;justify-content:space-between;gap:10px;align-items:center;margin-bottom:8px}
      .uc-applied-head strong{font-size:12px;line-height:1.4}
      .uc-applied-head button{padding:6px 8px;font-size:11px}
      .uc-applied-item textarea{min-height:105px;margin:0}
      @media(max-width:760px){.uc-textblock-grid,.uc-textblock-selects{grid-template-columns:1fr}.uc-textblock-toolbar{flex-direction:column}.uc-textblock-toolbar button{width:100%}.uc-textblock-item-head{flex-direction:column}.uc-textblock-actions{width:100%}.uc-textblock-actions button{flex:1}}
    `;
    document.head.appendChild(style);
  }

  async function resolveCompanyId(){
    const api=db();
    if(!api)return null;
    const {data:{user}}=await api.auth.getUser();
    if(!user){companyId=null;return null;}
    const {data,error}=await api.from("company_members").select("company_id").eq("user_id",user.id).maybeSingle();
    if(error){console.error("Textbausteine: Firma laden",error);return null;}
    companyId=data?.company_id||null;
    return companyId;
  }

  async function loadTextBlocks(){
    const api=db();
    if(!api)return [];
    const cid=companyId||await resolveCompanyId();
    if(!cid){textBlocks=[];renderTextBlockManagerList();renderTransferTextBlockSelects();return [];}
    const {data,error}=await api.from("company_text_blocks")
      .select("id,company_id,path_1,path_2,path_3,content,active,sort_order,created_at,updated_at")
      .eq("company_id",cid)
      .order("sort_order",{ascending:true})
      .order("path_1",{ascending:true})
      .order("path_2",{ascending:true})
      .order("path_3",{ascending:true});
    if(error){
      console.error("Textbausteine laden:",error);
      textBlocks=[];
      return [];
    }
    textBlocks=Array.isArray(data)?data:[];
    renderTextBlockManagerList();
    renderTransferTextBlockSelects();
    return textBlocks;
  }

  function pathLabel(block){
    return [block?.path_1,block?.path_2,block?.path_3].filter(Boolean).join(" → ");
  }

  function ensureTextBlockManager(){
    const dashboard=document.getElementById("businessDashboard");
    const nav=document.getElementById("businessMainNav");
    if(!dashboard||!nav)return;

    if(!document.getElementById("businessTextBlocksNavButton")){
      const button=document.createElement("button");
      button.id="businessTextBlocksNavButton";
      button.type="button";
      button.textContent="Textbausteine";
      button.addEventListener("click",()=>showTextBlockManager(button));
      nav.appendChild(button);
    }

    if(!document.getElementById("textBlocksOverviewCard")){
      const card=document.createElement("section");
      card.id="textBlocksOverviewCard";
      card.className="dashboard-card hidden uc-textblock-card";
      card.innerHTML=`
        <div class="uc-textblock-toolbar">
          <div><h2 style="margin:0;">Textbausteine</h2><p>Kurze Auswahl bei der Übergabe, ausführlicher Text automatisch im Protokoll. Der eingefügte Text bleibt vor der Unterschrift bearbeitbar.</p></div>
          <button type="button" class="primary" id="ucNewTextBlock">+ Textbaustein</button>
        </div>
        <div class="uc-textblock-form hidden" id="ucTextBlockForm">
          <div class="uc-textblock-grid">
            <div><label for="ucPath1">1. Auswahl / Thema *</label><input id="ucPath1" type="text" placeholder="z. B. Einbauküche"></div>
            <div><label for="ucPath2">2. Auswahl</label><input id="ucPath2" type="text" placeholder="z. B. Eigentum bisheriger Mieter"></div>
            <div><label for="ucPath3">3. Auswahl</label><input id="ucPath3" type="text" placeholder="z. B. darf zunächst verbleiben"></div>
          </div>
          <label for="ucTextBlockContent">Ausführlicher Text für das Protokoll *</label>
          <textarea id="ucTextBlockContent" placeholder="Hier den vollständigen Text hinterlegen, der später automatisch ins Protokoll übernommen wird."></textarea>
          <label style="display:flex;align-items:center;gap:8px;font-weight:600;"><input id="ucTextBlockActive" type="checkbox" checked style="width:auto;"> Baustein aktiv und bei Übergaben auswählbar</label>
          <div class="uc-textblock-form-actions"><button type="button" class="secondary" id="ucCancelTextBlock">Abbrechen</button><button type="button" class="primary" id="ucSaveTextBlock">Speichern</button></div>
        </div>
        <div class="uc-textblock-list" id="ucTextBlockList"><div class="empty-state">Textbausteine werden geladen …</div></div>
      `;
      dashboard.appendChild(card);
      card.querySelector("#ucNewTextBlock")?.addEventListener("click",()=>openTextBlockForm());
      card.querySelector("#ucCancelTextBlock")?.addEventListener("click",closeTextBlockForm);
      card.querySelector("#ucSaveTextBlock")?.addEventListener("click",saveTextBlock);
    }
  }

  function hideKnownDashboardSections(){
    ["businessSearchCard","objectsCard","apartmentsOverviewCard","businessTransfersCard","defectsOverviewCard","objectDetailSection","apartmentDetailSection","objectFormSection","apartmentForm"].forEach(id=>document.getElementById(id)?.classList.add("hidden"));
    document.querySelector("#businessDashboard > .dashboard-main")?.classList.add("hidden");
  }

  async function showTextBlockManager(button){
    ensureTextBlockManager();
    const dashboard=document.getElementById("businessDashboard");
    const app=document.getElementById("appContent");
    dashboard?.classList.remove("hidden");
    if(dashboard)dashboard.style.display="block";
    app?.classList.add("hidden");
    if(app)app.style.display="none";
    hideKnownDashboardSections();
    document.getElementById("textBlocksOverviewCard")?.classList.remove("hidden");
    document.querySelectorAll("#businessMainNav button").forEach(b=>b.classList.remove("active"));
    button?.classList.add("active");
    await loadTextBlocks();
    window.scrollTo({top:0,behavior:"smooth"});
  }

  function renderTextBlockManagerList(){
    const out=document.getElementById("ucTextBlockList");
    if(!out)return;
    if(!textBlocks.length){
      out.innerHTML='<div class="empty-state">Noch keine Textbausteine angelegt. Über „+ Textbaustein“ kannst du die erste Auswahlregel erstellen.</div>';
      return;
    }
    out.innerHTML=textBlocks.map(block=>`
      <div class="uc-textblock-item" data-id="${esc(block.id)}">
        <div class="uc-textblock-item-head">
          <div><div class="uc-textblock-path">${esc(pathLabel(block))}${block.active?"":' <span style="color:#999;font-weight:600;">(inaktiv)</span>'}</div><div class="uc-textblock-copy">${esc(block.content)}</div></div>
          <div class="uc-textblock-actions"><button type="button" class="secondary" data-edit="${esc(block.id)}">Bearbeiten</button><button type="button" class="danger" data-delete="${esc(block.id)}">Löschen</button></div>
        </div>
      </div>
    `).join("");
    out.querySelectorAll("[data-edit]").forEach(btn=>btn.addEventListener("click",()=>openTextBlockForm(btn.dataset.edit)));
    out.querySelectorAll("[data-delete]").forEach(btn=>btn.addEventListener("click",()=>deleteTextBlock(btn.dataset.delete)));
  }

  function openTextBlockForm(id=null){
    editingTextBlockId=id||null;
    const block=id?textBlocks.find(item=>String(item.id)===String(id)):null;
    const form=document.getElementById("ucTextBlockForm");
    if(!form)return;
    document.getElementById("ucPath1").value=block?.path_1||"";
    document.getElementById("ucPath2").value=block?.path_2||"";
    document.getElementById("ucPath3").value=block?.path_3||"";
    document.getElementById("ucTextBlockContent").value=block?.content||"";
    document.getElementById("ucTextBlockActive").checked=block?.active!==false;
    form.classList.remove("hidden");
    document.getElementById("ucPath1")?.focus();
  }

  function closeTextBlockForm(){
    editingTextBlockId=null;
    document.getElementById("ucTextBlockForm")?.classList.add("hidden");
  }

  async function saveTextBlock(){
    const api=db();
    const cid=companyId||await resolveCompanyId();
    if(!api||!cid){alert("Das Firmenkonto konnte nicht geladen werden.");return;}
    const path1=document.getElementById("ucPath1")?.value.trim()||"";
    const path2=document.getElementById("ucPath2")?.value.trim()||"";
    const path3=document.getElementById("ucPath3")?.value.trim()||"";
    const content=document.getElementById("ucTextBlockContent")?.value.trim()||"";
    const active=!!document.getElementById("ucTextBlockActive")?.checked;
    if(!path1||!content){alert("Bitte mindestens die erste Auswahl und den ausführlichen Protokolltext ausfüllen.");return;}

    const payload={company_id:cid,path_1:path1,path_2:path2,path_3:path3,content,active,updated_at:new Date().toISOString()};
    let error=null;
    if(editingTextBlockId){
      ({error}=await api.from("company_text_blocks").update(payload).eq("id",editingTextBlockId).eq("company_id",cid));
    }else{
      ({error}=await api.from("company_text_blocks").insert(payload));
    }
    if(error){
      console.error("Textbaustein speichern:",error);
      if(String(error.code||"")==="23505")alert("Diese Auswahlkombination gibt es bereits. Bitte den vorhandenen Baustein bearbeiten oder die Auswahl ändern.");
      else alert("Der Textbaustein konnte nicht gespeichert werden.\n\n"+(error.message||"Unbekannter Fehler"));
      return;
    }
    closeTextBlockForm();
    await loadTextBlocks();
  }

  async function deleteTextBlock(id){
    const block=textBlocks.find(item=>String(item.id)===String(id));
    if(!block||!confirm(`Textbaustein „${pathLabel(block)}“ wirklich löschen?`))return;
    const api=db();
    const cid=companyId||await resolveCompanyId();
    if(!api||!cid)return;
    const {error}=await api.from("company_text_blocks").delete().eq("id",id).eq("company_id",cid);
    if(error){console.error("Textbaustein löschen:",error);alert("Der Textbaustein konnte nicht gelöscht werden.");return;}
    await loadTextBlocks();
  }

  function unique(values){return [...new Set(values.filter(Boolean))].sort((a,b)=>a.localeCompare(b,"de"));}

  function ensureTransferTextBlockBuilder(){
    const step=document.getElementById("step4");
    const notes=document.getElementById("notes");
    if(!step||!notes||document.getElementById("ucTransferTextBlocks"))return;
    const box=document.createElement("div");
    box.id="ucTransferTextBlocks";
    box.className="uc-textblock-builder";
    box.innerHTML=`
      <h3>Textbausteine & Vereinbarungen</h3>
      <p>Kurze Auswahl treffen. Der hinterlegte Langtext wird übernommen und kann vor der Unterschrift noch angepasst werden.</p>
      <div class="uc-textblock-selects">
        <select id="ucTransferPath1"><option value="">1. Auswahl / Thema</option></select>
        <select id="ucTransferPath2" disabled><option value="">2. Auswahl</option></select>
        <select id="ucTransferPath3" disabled><option value="">3. Auswahl</option></select>
      </div>
      <div class="uc-textblock-add"><button type="button" class="secondary" id="ucApplyTextBlock" disabled>Text übernehmen</button></div>
      <div class="uc-applied-list" id="ucAppliedTextBlocks"></div>
    `;
    const label=notes.previousElementSibling?.tagName==="LABEL"?notes.previousElementSibling:notes;
    step.insertBefore(box,label);
    document.getElementById("ucTransferPath1")?.addEventListener("change",()=>renderTransferTextBlockSelects(2));
    document.getElementById("ucTransferPath2")?.addEventListener("change",()=>renderTransferTextBlockSelects(3));
    document.getElementById("ucTransferPath3")?.addEventListener("change",updateApplyButton);
    document.getElementById("ucApplyTextBlock")?.addEventListener("click",applySelectedTextBlock);
    renderTransferTextBlockSelects();
    renderAppliedTextBlocks();
  }

  function activeBlocks(){return textBlocks.filter(block=>block.active!==false);}

  function fillSelect(select,placeholder,values,current=""){
    if(!select)return;
    select.innerHTML=`<option value="">${esc(placeholder)}</option>`+values.map(value=>`<option value="${esc(value)}"${value===current?" selected":""}>${esc(value)}</option>`).join("");
    select.disabled=!values.length;
  }

  function renderTransferTextBlockSelects(changedLevel=1){
    const p1=document.getElementById("ucTransferPath1");
    const p2=document.getElementById("ucTransferPath2");
    const p3=document.getElementById("ucTransferPath3");
    if(!p1||!p2||!p3)return;
    const blocks=activeBlocks();
    const old1=p1.value, old2=p2.value, old3=p3.value;
    const values1=unique(blocks.map(b=>b.path_1));
    fillSelect(p1,"1. Auswahl / Thema",values1,old1);
    const v1=p1.value;
    const values2=unique(blocks.filter(b=>b.path_1===v1).map(b=>b.path_2));
    fillSelect(p2,"2. Auswahl",values2,changedLevel>1?old2:"");
    const v2=p2.value;
    const values3=unique(blocks.filter(b=>b.path_1===v1 && (b.path_2||"")===(v2||"")).map(b=>b.path_3));
    fillSelect(p3,"3. Auswahl",values3,changedLevel>2?old3:"");
    updateApplyButton();
  }

  function selectedRule(){
    const p1=document.getElementById("ucTransferPath1")?.value||"";
    const p2=document.getElementById("ucTransferPath2")?.value||"";
    const p3=document.getElementById("ucTransferPath3")?.value||"";
    if(!p1)return null;
    const candidates=activeBlocks().filter(b=>b.path_1===p1);
    if(!candidates.length)return null;
    const level2Values=unique(candidates.map(b=>b.path_2));
    if(level2Values.length && !p2)return null;
    const level3Candidates=candidates.filter(b=>(b.path_2||"")===(p2||""));
    const level3Values=unique(level3Candidates.map(b=>b.path_3));
    if(level3Values.length && !p3)return null;
    return level3Candidates.find(b=>(b.path_3||"")===(p3||""))||null;
  }

  function updateApplyButton(){
    const button=document.getElementById("ucApplyTextBlock");
    if(button)button.disabled=!selectedRule();
  }

  function applySelectedTextBlock(){
    const rule=selectedRule();
    if(!rule)return;
    appliedTextBlocks.push({
      id:crypto.randomUUID?crypto.randomUUID():String(Date.now())+Math.random(),
      source_id:rule.id,
      path_1:rule.path_1||"",
      path_2:rule.path_2||"",
      path_3:rule.path_3||"",
      content:rule.content||""
    });
    renderAppliedTextBlocks();
    try{if(typeof window.saveDraft==="function")window.saveDraft();}catch(_error){}
    try{if(typeof window.queueTransferAutosave==="function")window.queueTransferAutosave();}catch(_error){}
  }

  function renderAppliedTextBlocks(){
    const out=document.getElementById("ucAppliedTextBlocks");
    if(!out)return;
    if(!appliedTextBlocks.length){out.innerHTML='<div style="font-size:12px;color:#888;">Noch kein Textbaustein übernommen.</div>';return;}
    out.innerHTML=appliedTextBlocks.map((item,index)=>`
      <div class="uc-applied-item">
        <div class="uc-applied-head"><strong>${esc(pathLabel(item))}</strong><button type="button" class="danger" data-remove-applied="${index}">Entfernen</button></div>
        <textarea data-applied-content="${index}" aria-label="Textbaustein bearbeiten">${esc(item.content||"")}</textarea>
      </div>
    `).join("");
    out.querySelectorAll("[data-remove-applied]").forEach(button=>button.addEventListener("click",()=>{
      appliedTextBlocks.splice(Number(button.dataset.removeApplied),1);
      renderAppliedTextBlocks();
      try{if(typeof window.saveDraft==="function")window.saveDraft();}catch(_error){}
      try{if(typeof window.queueTransferAutosave==="function")window.queueTransferAutosave();}catch(_error){}
    }));
    out.querySelectorAll("[data-applied-content]").forEach(area=>area.addEventListener("input",()=>{
      const index=Number(area.dataset.appliedContent);
      if(appliedTextBlocks[index])appliedTextBlocks[index].content=area.value;
      try{if(typeof window.saveDraft==="function")window.saveDraft();}catch(_error){}
    }));
    out.querySelectorAll("[data-applied-content]").forEach(area=>area.addEventListener("change",()=>{
      try{if(typeof window.queueTransferAutosave==="function")window.queueTransferAutosave();}catch(_error){}
    }));
  }

  function setAppliedFromSnapshot(snapshot){
    let source=snapshot;
    try{if(typeof source==="string")source=JSON.parse(source);}catch(_error){}
    if(source?.data && typeof source.data==="object" && !source.fields)source=source.data;
    appliedTextBlocks=Array.isArray(source?.textBlocks)?clone(source.textBlocks):[];
    renderAppliedTextBlocks();
  }

  function injectTextBlocksIntoSummary(){
    document.getElementById("ucProtocolTextBlocks")?.remove();
    if(!appliedTextBlocks.length)return;
    const protocol=document.querySelector("#summary .protocol");
    if(!protocol)return;
    const signature=protocol.querySelector(".signature-section");
    const section=document.createElement("div");
    section.id="ucProtocolTextBlocks";
    section.className="protocol-section";
    section.innerHTML=`<div class="section-title"><span>Vereinbarungen & Textbausteine</span></div>`+appliedTextBlocks.map(item=>`
      <div class="protocol-detail" style="margin-bottom:10px;white-space:pre-wrap;"><strong>${esc(pathLabel(item))}</strong>${esc(item.content||"")}</div>
    `).join("");
    if(signature)protocol.insertBefore(section,signature);else protocol.appendChild(section);
  }

  function composedPdfNotes(originalNotes){
    if(!appliedTextBlocks.length)return originalNotes;
    const blockText=appliedTextBlocks.map(item=>{
      const path=pathLabel(item);
      return `${path ? path+"\n" : ""}${String(item.content||"").trim()}`.trim();
    }).filter(Boolean).join("\n\n");
    return [String(originalNotes||"").trim(),blockText].filter(Boolean).join("\n\n");
  }

  async function createPdfWithTextBlocks(originalCreate,args){
    const notes=document.getElementById("notes");
    if(!notes)return originalCreate(...args);
    const originalValue=notes.value;
    notes.value=composedPdfNotes(originalValue);
    try{return await originalCreate(...args);}finally{notes.value=originalValue;}
  }

  function downloadPdfBlob(blob,filename){
    const url=URL.createObjectURL(blob);
    const link=document.createElement("a");
    link.href=url;
    link.download=filename||"UebergabeCheck-Business.pdf";
    link.style.display="none";
    document.body.appendChild(link);
    link.click();
    link.remove();
    setTimeout(()=>URL.revokeObjectURL(url),1500);
  }

  // UEBERGABECHECK_TRANSFER_OVERVIEW_DELETE_V1
  function addTransferOverviewDeleteButtons(){
    const list=document.getElementById("businessTransfersList");
    if(!list)return;
    list.querySelectorAll(".transfer-item").forEach(item=>{
      const actions=item.querySelector(".transfer-actions");
      const openButton=actions?.querySelector('button[onclick*="openBusinessTransfer"]');
      if(!actions||!openButton||actions.querySelector(".uc-transfer-delete"))return;
      const onclick=String(openButton.getAttribute("onclick")||"");
      const match=onclick.match(/openBusinessTransfer\('([^']*)','([^']*)','([^']*)'\)/);
      if(!match)return;
      const transferId=match[1], apartmentId=match[3];
      const button=document.createElement("button");
      button.type="button";
      button.className="danger uc-transfer-delete";
      button.textContent="Löschen";
      button.addEventListener("click",async()=>{
        if(typeof window.deleteBusinessTransfer!=="function")return;
        await window.deleteBusinessTransfer(transferId,apartmentId);
        if(typeof window.renderBusinessTransfers==="function")await window.renderBusinessTransfers();
      });
      actions.appendChild(button);
    });
  }

  function installWrappers(){
    if(wrappersInstalled)return;
    wrappersInstalled=true;

    const originalRenderBusinessTransfers=window.renderBusinessTransfers;
    if(typeof originalRenderBusinessTransfers==="function"){
      window.renderBusinessTransfers=async function(...args){
        const result=await originalRenderBusinessTransfers.apply(this,args);
        addTransferOverviewDeleteButtons();
        return result;
      };
    }

    const originalNavigate=window.navigateBusinessTab;
    if(typeof originalNavigate==="function"){
      window.navigateBusinessTab=async function(...args){
        document.getElementById("textBlocksOverviewCard")?.classList.add("hidden");
        return originalNavigate.apply(this,args);
      };
    }

    const originalShowDashboard=window.showBusinessDashboard;
    if(typeof originalShowDashboard==="function"){
      window.showBusinessDashboard=function(...args){
        document.getElementById("textBlocksOverviewCard")?.classList.add("hidden");
        return originalShowDashboard.apply(this,args);
      };
    }

    const originalStartApp=window.startApp;
    if(typeof originalStartApp==="function"){
      window.startApp=function(...args){
        appliedTextBlocks=[];
        const result=originalStartApp.apply(this,args);
        ensureTransferTextBlockBuilder();
        renderAppliedTextBlocks();

        // UEBERGABECHECK_OBJECT_ADDRESS_AUTOFILL_V1
        try{
          const addressInput=document.getElementById("address");
          let objectId=(typeof selectedBusinessObjectId!=="undefined")?selectedBusinessObjectId:null;

          if(!objectId && typeof selectedApartmentId!=="undefined" && selectedApartmentId && typeof businessApartments!=="undefined"){
            for(const [candidateObjectId,apartments] of Object.entries(businessApartments||{})){
              if(Array.isArray(apartments) && apartments.some(apartment=>String(apartment?.id)===String(selectedApartmentId))){
                objectId=candidateObjectId;
                break;
              }
            }
          }

          const objects=(typeof businessObjects!=="undefined" && Array.isArray(businessObjects))?businessObjects:[];
          const object=objects.find(item=>String(item?.id)===String(objectId));

          if(addressInput && object){
            const street=String(object.street||"").trim();
            const place=[object.zip,object.city].filter(Boolean).join(" ").trim();
            const address=[street,place].filter(Boolean).join(", ");
            if(address){
              addressInput.value=address;
              addressInput.dispatchEvent(new Event("input",{bubbles:true}));
              addressInput.dispatchEvent(new Event("change",{bubbles:true}));
            }
          }
        }catch(error){
          console.warn("Objektadresse konnte nicht automatisch übernommen werden:",error);
        }

        return result;
      };
    }

    const originalFormSnapshot=window.formSnapshot;
    if(typeof originalFormSnapshot==="function"){
      window.formSnapshot=function(...args){
        const snapshot=originalFormSnapshot.apply(this,args)||{};
        snapshot.version=Math.max(Number(snapshot.version)||0,4);
        snapshot.textBlocks=clone(appliedTextBlocks);
        return snapshot;
      };
    }

    const originalLightweight=window.lightweightDraftSnapshot;
    if(typeof originalLightweight==="function"){
      window.lightweightDraftSnapshot=function(...args){
        const snapshot=originalLightweight.apply(this,args)||{};
        snapshot.version=Math.max(Number(snapshot.version)||0,4);
        snapshot.textBlocks=clone(appliedTextBlocks);
        return snapshot;
      };
    }

    const originalLoadDraft=window.loadDraft;
    if(typeof originalLoadDraft==="function"){
      window.loadDraft=function(...args){
        const result=originalLoadDraft.apply(this,args);
        try{
          const raw=sessionStorage.getItem("uebergabecheck_draft");
          if(raw)setAppliedFromSnapshot(JSON.parse(raw));
        }catch(_error){}
        return result;
      };
    }

    const originalRestore=window.restoreTransferSnapshot;
    if(typeof originalRestore==="function"){
      window.restoreTransferSnapshot=function(snapshot,...rest){
        const result=originalRestore.call(this,snapshot,...rest);
        setAppliedFromSnapshot(snapshot);
        return result;
      };
    }

    const originalSummary=window.showSummary;
    if(typeof originalSummary==="function"){
      window.showSummary=function(...args){
        const result=originalSummary.apply(this,args);
        injectTextBlocksIntoSummary();
        return result;
      };
    }

    const originalCreatePdf=window.createProtocolPdfBlob;
    if(typeof originalCreatePdf==="function"){
      window.createProtocolPdfBlob=function(...args){return createPdfWithTextBlocks(originalCreatePdf,args);};
      window.saveTransferPdf=async function(){
        try{
          if(typeof window.persistCurrentTransfer==="function"){
            const ok=await window.persistCurrentTransfer();
            if(!ok)return;
          }
          const result=await window.createProtocolPdfBlob();
          downloadPdfBlob(result.blob,result.filename);
        }catch(error){
          console.error("PDF-Export:",error);
          alert(error?.message==="NO_PROTOCOL"?"Bitte zuerst das Übergabeprotokoll erstellen.":"Die PDF konnte gerade nicht erstellt werden. Bitte Seite einmal neu laden und erneut versuchen.");
        }
      };
    }

    window.__uebergabeCheckAppliedTextBlocks=()=>clone(appliedTextBlocks);
  }

  async function sync(){
    const api=db();if(!api)return;
    installStyles();
    ensureTextBlockManager();
    ensureTransferTextBlockBuilder();
    addSupportButton();
    try{
      const {data:{user}}=await api.auth.getUser();
      if(!user){companyId=null;textBlocks=[];removeAdminButton();renderTransferTextBlockSelects();return;}
      await resolveCompanyId();
      await loadTextBlocks();
      const {data,error}=await api.from("app_admins").select("user_id").eq("user_id",user.id).maybeSingle();
      if(!error&&data)addAdminButton();else removeAdminButton();
    }catch(_error){removeAdminButton();}
  }

  const observer=new MutationObserver(()=>{
    if(dashboardActions()){
      installStyles();
      ensureTextBlockManager();
      ensureTransferTextBlockBuilder();
      addSupportButton();
    }
  });

  function init(){
    installStyles();
    installWrappers();
    observer.observe(document.documentElement,{childList:true,subtree:true});
    sync();
    const api=db();
    api?.auth?.onAuthStateChange(()=>setTimeout(sync,120));
    setTimeout(sync,500);
  }

  if(document.readyState==="loading")document.addEventListener("DOMContentLoaded",init,{once:true});
  else init();
})();
