from pathlib import Path

index_path=Path('index.html')
pdf_path=Path('pdf-export.js')
s=index_path.read_text(encoding='utf-8')
p=pdf_path.read_text(encoding='utf-8')


def replace_once(text, old, new, label):
    count=text.count(old)
    assert count==1, f'{label}: expected exactly once, found {count}'
    return text.replace(old,new,1)

# ---------- INDEX.HTML ----------
css_marker='  /* B2B Login */'
company_css='''  /* Unternehmensdaten / Briefkopf */
  .company-profile-overlay{position:fixed;inset:0;background:rgba(0,0,0,.42);display:flex;align-items:center;justify-content:center;padding:20px;z-index:10000}
  .company-profile-box{background:#fff;width:min(760px,100%);max-height:92vh;overflow:auto;border-radius:22px;padding:26px;box-shadow:0 20px 60px rgba(0,0,0,.2)}
  .company-profile-head{display:flex;justify-content:space-between;gap:18px;align-items:flex-start;margin-bottom:18px}
  .company-profile-head h2{margin:0 0 5px}
  .company-logo-row{display:flex;gap:16px;align-items:center;margin-top:10px;flex-wrap:wrap}
  .company-logo-preview{width:150px;height:74px;border:1px dashed #d2d3d7;border-radius:12px;background:#fafafa;display:flex;align-items:center;justify-content:center;overflow:hidden;color:#888;font-size:12px;text-align:center;padding:8px}
  .company-logo-preview img{max-width:100%;max-height:100%;object-fit:contain}
  .company-profile-actions{display:flex;justify-content:flex-end;gap:10px;margin-top:20px}
  .protocol-letterhead{display:flex;justify-content:space-between;gap:25px;align-items:flex-start;padding:4px 8px 20px;margin-bottom:8px;border-bottom:1px solid #ddd}
  .protocol-letterhead-logo{max-width:170px;max-height:70px;object-fit:contain;display:block;margin-bottom:10px}
  .protocol-letterhead-company{font-size:17px;font-weight:850;line-height:1.25}
  .protocol-letterhead-contact{text-align:right;font-size:12px;color:#666;line-height:1.55;white-space:normal}
  @media(max-width:650px){
    .company-profile-box{padding:20px 16px}
    .company-profile-head{flex-direction:column}
    .company-profile-actions{flex-direction:column-reverse}
    .company-profile-actions button{width:100%}
    .protocol-letterhead{flex-direction:column;gap:10px}
    .protocol-letterhead-contact{text-align:left}
  }

'''
s=replace_once(s,css_marker,company_css+css_marker,'insert company CSS')

modal_marker='<section class="business-dashboard hidden" id="businessDashboard">'
company_modal='''<div class="company-profile-overlay hidden" id="companyProfileOverlay" onclick="if(event.target===this) closeCompanyProfile()">
  <div class="company-profile-box" role="dialog" aria-modal="true" aria-labelledby="companyProfileTitle">
    <div class="company-profile-head">
      <div>
        <div class="dashboard-kicker">Briefkopf & Stammdaten</div>
        <h2 id="companyProfileTitle">Unternehmensdaten</h2>
        <div class="sub" style="margin:0;">Diese Angaben werden automatisch in neue Übergabeprotokolle übernommen.</div>
      </div>
      <button class="secondary" type="button" onclick="closeCompanyProfile()">Schließen</button>
    </div>
    <div class="grid">
      <div><label for="companyProfileName">Firmenname</label><input id="companyProfileName" type="text" placeholder="z. B. Müller Hausverwaltung GmbH"></div>
      <div><label for="companyProfileContact">Ansprechpartner</label><input id="companyProfileContact" type="text" placeholder="Vor- und Nachname"></div>
      <div><label for="companyProfileStreet">Straße & Hausnummer</label><input id="companyProfileStreet" type="text" placeholder="Musterstraße 12"></div>
      <div><label for="companyProfileZip">PLZ</label><input id="companyProfileZip" type="text" inputmode="numeric" placeholder="89518"></div>
      <div><label for="companyProfileCity">Ort</label><input id="companyProfileCity" type="text" placeholder="Heidenheim an der Brenz"></div>
      <div><label for="companyProfilePhone">Telefon</label><input id="companyProfilePhone" type="tel" placeholder="07321 123456"></div>
      <div><label for="companyProfileEmail">E-Mail</label><input id="companyProfileEmail" type="email" placeholder="info@hausverwaltung.de"></div>
      <div><label for="companyProfileWebsite">Website</label><input id="companyProfileWebsite" type="text" placeholder="www.hausverwaltung.de"></div>
    </div>
    <label>Firmenlogo <span style="font-weight:400;color:#777;">(optional)</span></label>
    <div class="company-logo-row">
      <div class="company-logo-preview" id="companyLogoPreview">Noch kein Logo hinterlegt</div>
      <div style="display:flex;gap:8px;flex-wrap:wrap;">
        <label class="meter-photo-button" style="margin:0!important;">Logo auswählen<input id="companyLogoInput" type="file" accept="image/png,image/jpeg,image/webp" onchange="previewCompanyLogo(this)"></label>
        <button class="secondary" type="button" onclick="removeCompanyLogo()">Logo entfernen</button>
      </div>
    </div>
    <div class="company-profile-actions">
      <button class="secondary" type="button" onclick="closeCompanyProfile()">Abbrechen</button>
      <button class="primary" id="companyProfileSaveButton" type="button" onclick="saveCompanyProfile()">Unternehmensdaten speichern</button>
    </div>
  </div>
</div>
'''
s=replace_once(s,modal_marker,company_modal+modal_marker,'insert company modal')

old_actions='''<button class="secondary" onclick="goBusinessHome()" type="button">⌂ Dashboard</button>
<button class="secondary" onclick="businessLogout()" type="button">Abmelden</button>
<button class="primary" onclick="startBusinessTransfer()" type="button">＋ Neue Übergabe</button>'''
new_actions='''<button class="secondary" onclick="goBusinessHome()" type="button">⌂ Dashboard</button>
<button class="secondary" onclick="openCompanyProfile()" type="button">🏢 Unternehmensdaten</button>
<button class="secondary" onclick="businessLogout()" type="button">Abmelden</button>
<button class="primary" onclick="startBusinessTransfer()" type="button">＋ Neue Übergabe</button>'''
s=replace_once(s,old_actions,new_actions,'add company profile button')

state_marker='let businessCompanyId = null;'
company_state='''let businessCompanyId = null;
let businessCompanyProfile={name:"",contact_name:"",street:"",zip:"",city:"",phone:"",email:"",website:"",logo_data:""};
window.businessCompanyProfile=businessCompanyProfile;
'''
s=replace_once(s,state_marker,company_state,'company state')

load_marker='async function loadBusinessData(user){'
company_functions=r'''function normalizeCompanyProfile(row={}){
  return {
    name:row.name||"",
    contact_name:row.contact_name||"",
    street:row.street||"",
    zip:row.zip||"",
    city:row.city||"",
    phone:row.phone||"",
    email:row.email||"",
    website:row.website||"",
    logo_data:row.logo_data||""
  };
}

function updateCompanyLogoPreview(){
  const preview=document.getElementById("companyLogoPreview");
  if(!preview)return;
  const logo=businessCompanyProfile.logo_data||"";
  preview.innerHTML=logo?`<img src="${logo}" alt="Firmenlogo">`:"Noch kein Logo hinterlegt";
}

async function loadBusinessCompanyProfile(companyId){
  if(!companyId||!supabaseClient)return businessCompanyProfile;
  const {data,error}=await supabaseClient
    .from("companies")
    .select("id,name,contact_name,street,zip,city,phone,email,website,logo_data")
    .eq("id",companyId)
    .single();
  if(error)throw error;
  businessCompanyProfile=normalizeCompanyProfile(data||{});
  if(!businessCompanyProfile.email && supabaseUser?.email) businessCompanyProfile.email=supabaseUser.email;
  window.businessCompanyProfile=businessCompanyProfile;
  const dashboardCompany=document.getElementById("dashboardCompany");
  if(dashboardCompany){
    dashboardCompany.textContent=businessCompanyProfile.name
      ? businessCompanyProfile.name+" · Zentrale Verwaltung"
      : "Dein Unternehmen auf einen Blick.";
  }
  return businessCompanyProfile;
}

function openCompanyProfile(){
  const map={
    companyProfileName:"name",
    companyProfileContact:"contact_name",
    companyProfileStreet:"street",
    companyProfileZip:"zip",
    companyProfileCity:"city",
    companyProfilePhone:"phone",
    companyProfileEmail:"email",
    companyProfileWebsite:"website"
  };
  Object.entries(map).forEach(([id,key])=>{
    const el=document.getElementById(id);
    if(el)el.value=businessCompanyProfile[key]||"";
  });
  const input=document.getElementById("companyLogoInput");
  if(input)input.value="";
  updateCompanyLogoPreview();
  document.getElementById("companyProfileOverlay")?.classList.remove("hidden");
  document.body.style.overflow="hidden";
}

function closeCompanyProfile(){
  document.getElementById("companyProfileOverlay")?.classList.add("hidden");
  document.body.style.overflow="";
}

async function previewCompanyLogo(input){
  const file=input?.files?.[0];
  if(!file)return;
  if(file.size>5*1024*1024){alert("Bitte ein Logo mit maximal 5 MB auswählen.");input.value="";return;}
  try{
    let data=await readFileAsDataURL(file);
    if(typeof compressImageDataURL==="function") data=await compressImageDataURL(data,700,.84);
    businessCompanyProfile.logo_data=data;
    window.businessCompanyProfile=businessCompanyProfile;
    updateCompanyLogoPreview();
  }catch(error){
    console.error("Firmenlogo:",error);
    alert("Das Logo konnte nicht verarbeitet werden.");
  }
}

function removeCompanyLogo(){
  businessCompanyProfile.logo_data="";
  window.businessCompanyProfile=businessCompanyProfile;
  const input=document.getElementById("companyLogoInput");
  if(input)input.value="";
  updateCompanyLogoPreview();
}

async function saveCompanyProfile(){
  if(!businessCompanyId||!supabaseClient){alert("Das Unternehmenskonto ist noch nicht vollständig geladen.");return;}
  const name=document.getElementById("companyProfileName")?.value.trim()||"";
  if(!name){alert("Bitte einen Firmennamen eingeben.");document.getElementById("companyProfileName")?.focus();return;}
  const payload={
    name,
    contact_name:document.getElementById("companyProfileContact")?.value.trim()||"",
    street:document.getElementById("companyProfileStreet")?.value.trim()||"",
    zip:document.getElementById("companyProfileZip")?.value.trim()||"",
    city:document.getElementById("companyProfileCity")?.value.trim()||"",
    phone:document.getElementById("companyProfilePhone")?.value.trim()||"",
    email:document.getElementById("companyProfileEmail")?.value.trim()||"",
    website:document.getElementById("companyProfileWebsite")?.value.trim()||"",
    logo_data:businessCompanyProfile.logo_data||""
  };
  const button=document.getElementById("companyProfileSaveButton");
  if(button){button.disabled=true;button.textContent="Wird gespeichert …";}
  const {data,error}=await supabaseClient
    .from("companies")
    .update(payload)
    .eq("id",businessCompanyId)
    .select("name,contact_name,street,zip,city,phone,email,website,logo_data")
    .single();
  if(button){button.disabled=false;button.textContent="Unternehmensdaten speichern";}
  if(error){console.error("Unternehmensdaten speichern:",error);alert("Die Unternehmensdaten konnten nicht gespeichert werden.\n\n"+(error.message||"Unbekannter Fehler"));return;}
  businessCompanyProfile=normalizeCompanyProfile(data||payload);
  window.businessCompanyProfile=businessCompanyProfile;
  const dashboardCompany=document.getElementById("dashboardCompany");
  if(dashboardCompany)dashboardCompany.textContent=businessCompanyProfile.name+" · Zentrale Verwaltung";
  closeCompanyProfile();
  alert("Unternehmensdaten gespeichert.");
}

function companyLetterheadHtml(){
  const c=businessCompanyProfile||{};
  const contact=[
    c.street||"",
    [c.zip,c.city].filter(Boolean).join(" "),
    c.phone?"Tel. "+c.phone:"",
    c.email||"",
    c.website||""
  ].filter(Boolean);
  if(!c.name && !c.logo_data && !contact.length)return "";
  return `<div class="protocol-letterhead">
    <div>
      ${c.logo_data?`<img class="protocol-letterhead-logo" src="${c.logo_data}" alt="Firmenlogo">`:""}
      ${c.name?`<div class="protocol-letterhead-company">${esc(c.name)}</div>`:""}
      ${c.contact_name?`<div class="muted">${esc(c.contact_name)}</div>`:""}
    </div>
    <div class="protocol-letterhead-contact">${contact.map(esc).join("<br>")}</div>
  </div>`;
}

'''
s=replace_once(s,load_marker,company_functions+load_marker,'company functions')

company_load_old='''    const companyId=await ensureBusinessCompany(user);
    const {data:objects,error:objectError}=await supabaseClient.from("objects")'''
company_load_new='''    const companyId=await ensureBusinessCompany(user);
    await loadBusinessCompanyProfile(companyId);
    const {data:objects,error:objectError}=await supabaseClient.from("objects")'''
s=replace_once(s,company_load_old,company_load_new,'load company profile')

summary_marker='''    <div class="protocol">
      <div class="protocol-cover">'''
summary_new='''    <div class="protocol">
      ${companyLetterheadHtml()}
      <div class="protocol-cover">'''
s=replace_once(s,summary_marker,summary_new,'letterhead in summary')

start_app_marker='''    const dateInput=document.getElementById("date");
    if(dateInput && !dateInput.value){
      dateInput.value=new Date().toISOString().slice(0,10);
    }'''
start_app_new='''    const dateInput=document.getElementById("date");
    if(dateInput && !dateInput.value){
      dateInput.value=new Date().toISOString().slice(0,10);
    }
    const landlordInput=document.getElementById("landlord");
    if(landlordInput && !landlordInput.value && businessCompanyProfile?.name){
      landlordInput.value=businessCompanyProfile.name;
    }'''
s=replace_once(s,start_app_marker,start_app_new,'prefill landlord')

index_path.write_text(s,encoding='utf-8')

# ---------- PDF-EXPORT.JS ----------
pdf_marker='''    const address=value("address","Adresse nicht angegeben");
    const dateRaw=document.getElementById("date")?.value||"";
    const tenant=value("tenant");
    const landlord=value("landlord");

    setText(7.5,"bold",MUTED);'''
pdf_new=r'''    const address=value("address","Adresse nicht angegeben");
    const dateRaw=document.getElementById("date")?.value||"";
    const tenant=value("tenant");
    const landlord=value("landlord");
    const company=window.businessCompanyProfile||{};

    const companyContact=[
      company.street||"",
      [company.zip,company.city].filter(Boolean).join(" "),
      company.phone?"Tel. "+company.phone:"",
      company.email||"",
      company.website||""
    ].filter(Boolean);

    if(company.name || company.logo_data || companyContact.length){
      const headerTop=y;
      const logo=company.logo_data?await dataUrlToJpeg(company.logo_data,700,.9):null;
      let companyTextX=M;
      if(logo){
        const boxW=32, boxH=17;
        const ratio=logo.width/logo.height;
        let imageW=boxW, imageH=boxH;
        if(ratio>boxW/boxH) imageH=imageW/ratio;
        else imageW=imageH*ratio;
        try{doc.addImage(logo.data,"JPEG",M,headerTop,imageW,imageH,undefined,"FAST");}catch(_error){}
        companyTextX=M+37;
      }
      if(company.name){
        const nameLines=split(company.name,88-(companyTextX-M),11.5,"bold").slice(0,2);
        setText(11.5,"bold");
        doc.text(nameLines,companyTextX,headerTop+4,{lineHeightFactor:1.05});
        if(company.contact_name){
          setText(8,"normal",MUTED);
          doc.text(split(company.contact_name,80,8,"normal").slice(0,1),companyTextX,headerTop+13);
        }
      }
      if(companyContact.length){
        setText(8,"normal",MUTED);
        doc.text(companyContact,M+CONTENT_W,headerTop+3,{align:"right",lineHeightFactor:1.35});
      }
      y=headerTop+24;
      doc.setDrawColor(...LINE);
      doc.setLineWidth(.25);
      doc.line(M,y,M+CONTENT_W,y);
      y+=7;
    }

    setText(7.5,"bold",MUTED);'''
p=replace_once(p,pdf_marker,pdf_new,'PDF company letterhead')
pdf_path.write_text(p,encoding='utf-8')
