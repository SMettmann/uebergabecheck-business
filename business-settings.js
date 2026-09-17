/* ÜbergabeCheck Business — Einstellungen */
(function(){
  "use strict";
  if(window.__uebergabeCheckSettingsInstalled)return;
  window.__uebergabeCheckSettingsInstalled=true;

  const SUPABASE_URL="https://fkirkglhcpltxlcsozmd.supabase.co";
  const SUPABASE_KEY="sb_publishable_lNeX7Hrtp9-FFl3NVb_Gaw_O-21yXWr";
  const api=window.supabase?.createClient?.(SUPABASE_URL,SUPABASE_KEY)||null;

  let companyId=null;
  let settings={text_blocks_enabled:true,default_landlord:"",show_company_logo:true};
  let startWrapped=false;
  let pdfWrapped=false;

  function dashboard(){return document.getElementById("businessDashboard");}
  function actions(){return document.querySelector("#businessDashboard .dashboard-top .dashboard-actions");}

  function installStyle(){
    if(document.getElementById("ucSettingsStyles"))return;
    const style=document.createElement("style");
    style.id="ucSettingsStyles";
    style.textContent=`
      #businessTextBlocksNavButton{display:none!important}
      .uc-settings-card{grid-column:1/-1;margin:0!important}
      .uc-settings-head{margin-bottom:16px}
      .uc-settings-head h2{margin:0 0 5px;font-size:20px}
      .uc-settings-head p{margin:0;color:#73757b;font-size:13px;line-height:1.5}
      .uc-settings-grid{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:12px;margin-bottom:12px}
      .uc-settings-box{border:1px solid #e1e2e5;border-radius:14px;padding:16px;background:#fff}
      .uc-settings-box h3{margin:0 0 5px;font-size:15px}
      .uc-settings-box p{margin:0 0 14px;color:#73757b;font-size:12px;line-height:1.5}
      .uc-settings-toggle{display:flex;align-items:center;justify-content:space-between;gap:14px;margin:0;font-weight:750}
      .uc-settings-toggle input{width:18px!important;height:18px!important;min-width:18px;margin:0!important}
      .uc-settings-save{display:flex;justify-content:flex-end;margin-top:14px}
      .uc-settings-status{font-size:12px;color:#73757b;margin-right:auto;align-self:center}
      @media(max-width:760px){.uc-settings-grid{grid-template-columns:1fr}.uc-settings-save{flex-direction:column;gap:8px}.uc-settings-save button{width:100%}}
    `;
    document.head.appendChild(style);
  }

  async function resolveCompany(){
    if(!api)return null;
    const {data:{user}}=await api.auth.getUser();
    if(!user){companyId=null;return null;}
    const {data,error}=await api.from("company_members").select("company_id").eq("user_id",user.id).maybeSingle();
    if(error){console.error("Einstellungen: Firma laden",error);return null;}
    companyId=data?.company_id||null;
    return companyId;
  }

  async function loadSettings(){
    settings={text_blocks_enabled:true,default_landlord:"",show_company_logo:true};
    const cid=companyId||await resolveCompany();
    if(api&&cid){
      const {data,error}=await api.from("company_settings")
        .select("text_blocks_enabled,default_landlord,show_company_logo")
        .eq("company_id",cid)
        .maybeSingle();
      if(error)console.error("Einstellungen laden",error);
      else if(data)settings={...settings,...data};
    }
    renderSettings();
    applyModuleVisibility();
    return settings;
  }

  function ensureSettingsCard(){
    const root=dashboard();
    if(!root||document.getElementById("settingsOverviewCard"))return;
    const card=document.createElement("section");
    card.id="settingsOverviewCard";
    card.className="dashboard-card hidden uc-settings-card";
    card.innerHTML=`
      <div class="uc-settings-head">
        <h2>Einstellungen</h2>
        <p>Lege fest, welche Funktionen dein Team bei Übergaben nutzt und welche Standardwerte automatisch vorbelegt werden.</p>
      </div>
      <div class="uc-settings-grid">
        <div class="uc-settings-box">
          <h3>Module</h3>
          <p>Bereiche ausblenden, ohne gespeicherte Inhalte oder angelegte Bausteine zu löschen.</p>
          <label class="uc-settings-toggle"><span>Textbausteine verwenden</span><input id="ucSettingTextBlocks" type="checkbox"></label>
        </div>
        <div class="uc-settings-box">
          <h3>Protokoll & PDF</h3>
          <p>Steuere, wie deine automatisch erzeugten Unterlagen aussehen.</p>
          <label class="uc-settings-toggle"><span>Firmenlogo im PDF anzeigen</span><input id="ucSettingShowLogo" type="checkbox"></label>
        </div>
      </div>
      <div class="uc-settings-box">
        <h3>Standardwerte</h3>
        <p>Optional einen festen Vermieter vorbelegen. Bleibt das Feld leer, wird weiterhin der Unternehmensname verwendet.</p>
        <label for="ucSettingLandlord">Standard-Vermieter</label>
        <input id="ucSettingLandlord" type="text" placeholder="z. B. Muster Hausverwaltung GmbH">
      </div>
      <div class="uc-settings-save"><span class="uc-settings-status" id="ucSettingsStatus"></span><button type="button" class="primary" id="ucSaveSettings">Einstellungen speichern</button></div>
    `;
    const textCard=document.getElementById("textBlocksOverviewCard");
    if(textCard)root.insertBefore(card,textCard);else root.appendChild(card);
    card.querySelector("#ucSaveSettings")?.addEventListener("click",saveSettings);
    renderSettings();
  }

  function addSettingsButton(){
    const bar=actions();
    if(!bar||document.getElementById("businessSettingsButton"))return;
    const button=document.createElement("button");
    button.id="businessSettingsButton";
    button.type="button";
    button.className="secondary";
    button.textContent="⚙ Einstellungen";
    button.addEventListener("click",openSettings);
    const admin=document.getElementById("businessInternalAdminButton");
    const logout=[...bar.querySelectorAll("button")].find(b=>String(b.getAttribute("onclick")||"").includes("businessLogout"));
    if(admin)bar.insertBefore(button,admin);
    else if(logout)bar.insertBefore(button,logout);
    else bar.appendChild(button);
  }

  function renderSettings(){
    const textToggle=document.getElementById("ucSettingTextBlocks");
    const logoToggle=document.getElementById("ucSettingShowLogo");
    const landlord=document.getElementById("ucSettingLandlord");
    if(textToggle)textToggle.checked=settings.text_blocks_enabled!==false;
    if(logoToggle)logoToggle.checked=settings.show_company_logo!==false;
    if(landlord)landlord.value=settings.default_landlord||"";
  }

  async function saveSettings(){
    const cid=companyId||await resolveCompany();
    if(!api||!cid){alert("Das Firmenkonto konnte nicht geladen werden.");return;}
    const status=document.getElementById("ucSettingsStatus");
    if(status)status.textContent="Speichert …";
    const payload={
      company_id:cid,
      text_blocks_enabled:!!document.getElementById("ucSettingTextBlocks")?.checked,
      default_landlord:document.getElementById("ucSettingLandlord")?.value.trim()||"",
      show_company_logo:!!document.getElementById("ucSettingShowLogo")?.checked,
      updated_at:new Date().toISOString()
    };
    const {error}=await api.from("company_settings").upsert(payload,{onConflict:"company_id"});
    if(error){
      console.error("Einstellungen speichern",error);
      if(status)status.textContent="";
      alert("Die Einstellungen konnten nicht gespeichert werden. Nur Inhaber und Admins dürfen diese Unternehmens-Einstellungen ändern.");
      return;
    }
    settings={...settings,...payload};
    applyModuleVisibility();
    if(status){status.textContent="Gespeichert";setTimeout(()=>{if(status.textContent==="Gespeichert")status.textContent="";},1800);}
  }

  function hideNormalDashboardSections(){
    ["businessSearchCard","objectsCard","apartmentsOverviewCard","businessTransfersCard","defectsOverviewCard","objectDetailSection","apartmentDetailSection","objectFormSection","apartmentForm"].forEach(id=>document.getElementById(id)?.classList.add("hidden"));
    document.querySelector("#businessDashboard > .dashboard-main")?.classList.add("hidden");
  }

  async function openSettings(){
    ensureSettingsCard();
    const root=dashboard();
    const app=document.getElementById("appContent");
    root?.classList.remove("hidden");
    if(root)root.style.display="block";
    app?.classList.add("hidden");
    if(app)app.style.display="none";

    const hiddenTextNav=document.getElementById("businessTextBlocksNavButton");
    if(hiddenTextNav)hiddenTextNav.click();
    else hideNormalDashboardSections();

    ensureSettingsCard();
    document.getElementById("settingsOverviewCard")?.classList.remove("hidden");
    document.getElementById("textBlocksOverviewCard")?.classList.remove("hidden");
    document.querySelectorAll("#businessMainNav button").forEach(b=>b.classList.remove("active"));
    await loadSettings();
    window.scrollTo({top:0,behavior:"smooth"});
  }

  function applyModuleVisibility(){
    const builder=document.getElementById("ucTransferTextBlocks");
    if(builder)builder.classList.toggle("hidden",settings.text_blocks_enabled===false);
  }

  function installMainNavClose(){
    const nav=document.getElementById("businessMainNav");
    if(!nav||nav.dataset.ucSettingsCloseInstalled)return;
    nav.dataset.ucSettingsCloseInstalled="1";
    nav.addEventListener("click",()=>document.getElementById("settingsOverviewCard")?.classList.add("hidden"));
  }

  function wrapStartApp(){
    if(startWrapped||typeof window.startApp!=="function")return;
    startWrapped=true;
    const original=window.startApp;
    window.startApp=function(...args){
      const result=original.apply(this,args);
      applyModuleVisibility();
      const landlord=document.getElementById("landlord");
      if(landlord&&settings.default_landlord){
        landlord.value=settings.default_landlord;
        landlord.dispatchEvent(new Event("input",{bubbles:true}));
      }
      return result;
    };
  }

  function wrapPdf(){
    if(pdfWrapped||typeof window.createProtocolPdfBlob!=="function")return;
    pdfWrapped=true;
    const original=window.createProtocolPdfBlob;
    window.createProtocolPdfBlob=async function(...args){
      const profile=window.businessCompanyProfile;
      if(settings.show_company_logo===false&&profile&&profile.logo_data){
        const logo=profile.logo_data;
        profile.logo_data="";
        try{return await original.apply(this,args);}finally{profile.logo_data=logo;}
      }
      return original.apply(this,args);
    };
  }

  function syncUi(){
    installStyle();
    addSettingsButton();
    ensureSettingsCard();
    installMainNavClose();
    wrapStartApp();
    wrapPdf();
    document.getElementById("businessTextBlocksNavButton")?.style.setProperty("display","none","important");
    applyModuleVisibility();
  }

  const observer=new MutationObserver(syncUi);

  async function init(){
    installStyle();
    observer.observe(document.documentElement,{childList:true,subtree:true});
    syncUi();
    await loadSettings();
    api?.auth?.onAuthStateChange(()=>setTimeout(async()=>{companyId=null;await loadSettings();syncUi();},150));
    // UEBERGABECHECK_SETTINGS_CROSS_DEVICE_V1
    const refreshFromServer=()=>setTimeout(async()=>{companyId=null;await loadSettings();syncUi();},80);
    window.addEventListener("focus",refreshFromServer);
    document.addEventListener("visibilitychange",()=>{if(!document.hidden)refreshFromServer();});
    window.__uebergabeCheckCompanySettings=()=>({...settings});
    window.__uebergabeCheckReloadSettings=loadSettings;
  }

  if(document.readyState==="loading")document.addEventListener("DOMContentLoaded",init,{once:true});
  else init();
})();
