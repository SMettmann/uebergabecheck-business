(function(){
  "use strict";

  const JSPDF_URL="https://cdnjs.cloudflare.com/ajax/libs/jspdf/2.5.1/jspdf.umd.min.js";
  let jsPdfLoadingPromise=null;

  function loadJsPdfLibrary(){
    if(window.jspdf?.jsPDF) return Promise.resolve(window.jspdf.jsPDF);
    if(jsPdfLoadingPromise) return jsPdfLoadingPromise;

    jsPdfLoadingPromise=new Promise((resolve,reject)=>{
      const existing=document.querySelector('script[data-uebergabecheck-jspdf]');
      if(existing){
        if(window.jspdf?.jsPDF){resolve(window.jspdf.jsPDF);return;}
        existing.addEventListener("load",()=>window.jspdf?.jsPDF?resolve(window.jspdf.jsPDF):reject(new Error("PDF_UNAVAILABLE")),{once:true});
        existing.addEventListener("error",()=>reject(new Error("PDF_UNAVAILABLE")),{once:true});
        return;
      }

      const script=document.createElement("script");
      script.src=JSPDF_URL;
      script.async=true;
      script.crossOrigin="anonymous";
      script.dataset.uebergabecheckJspdf="1";
      script.onload=()=>window.jspdf?.jsPDF?resolve(window.jspdf.jsPDF):reject(new Error("PDF_UNAVAILABLE"));
      script.onerror=()=>reject(new Error("PDF_UNAVAILABLE"));
      document.head.appendChild(script);
    });

    return jsPdfLoadingPromise;
  }

  function value(id,fallback="–"){
    const raw=(document.getElementById(id)?.value||"").trim();
    return raw||fallback;
  }

  function formatDate(raw){
    if(!raw) return "–";
    try{return new Date(raw+"T12:00:00").toLocaleDateString("de-DE");}
    catch(_error){return raw;}
  }

  function safeFilePart(text){
    return String(text||"")
      .normalize("NFKD")
      .replace(/[\u0300-\u036f]/g,"")
      .replace(/ß/g,"ss")
      .replace(/[^a-zA-Z0-9_-]+/g,"-")
      .replace(/-+/g,"-")
      .replace(/^-|-$/g,"")
      .slice(0,90);
  }

  function protocolPdfFilename(){
    const address=safeFilePart(document.getElementById("address")?.value||"");
    const date=safeFilePart(document.getElementById("date")?.value||"");
    const suffix=[address,date].filter(Boolean).join("-")||"Uebergabeprotokoll";
    return `UebergabeCheck-Business-${suffix}.pdf`;
  }

  function dataUrlToJpeg(dataUrl,maxPx=1600,quality=.88){
    return new Promise(resolve=>{
      if(!dataUrl){resolve(null);return;}
      const img=new Image();
      img.onload=()=>{
        try{
          const naturalW=img.naturalWidth||img.width;
          const naturalH=img.naturalHeight||img.height;
          if(!naturalW||!naturalH){resolve(null);return;}
          const scale=Math.min(1,maxPx/Math.max(naturalW,naturalH));
          const width=Math.max(1,Math.round(naturalW*scale));
          const height=Math.max(1,Math.round(naturalH*scale));
          const canvas=document.createElement("canvas");
          canvas.width=width;
          canvas.height=height;
          const ctx=canvas.getContext("2d");
          ctx.fillStyle="#ffffff";
          ctx.fillRect(0,0,width,height);
          ctx.drawImage(img,0,0,width,height);
          resolve({data:canvas.toDataURL("image/jpeg",quality),width,height});
        }catch(_error){resolve(null);}
      };
      img.onerror=()=>resolve(null);
      img.src=dataUrl;
    });
  }

  function canvasToPng(id){
    const canvas=document.getElementById(id);
    if(!canvas) return null;
    try{return canvas.toDataURL("image/png");}
    catch(_error){return null;}
  }

  function defectStatusLabel(status){
    if(status==="resolved") return "Erledigt";
    if(status==="in_progress") return "In Bearbeitung";
    return "Offen";
  }

  async function createProtocolPdfBlob(){
    const protocol=document.querySelector("#summary .protocol");
    if(!protocol) throw new Error("NO_PROTOCOL");

    const jsPDF=await loadJsPdfLibrary();
    const doc=new jsPDF({orientation:"portrait",unit:"mm",format:"a4",compress:true,putOnlyUsedFonts:true});

    const PAGE_W=210;
    const M=14;
    const CONTENT_W=PAGE_W-(M*2);
    const BOTTOM=278;
    const TEXT=[23,24,27];
    const MUTED=[112,114,122];
    const LIGHT=[247,247,248];
    const LINE=[229,229,231];
    let y=M;
    let pageNo=1;

    const setText=(size=10,style="normal",color=TEXT)=>{
      doc.setFont("helvetica",style);
      doc.setFontSize(size);
      doc.setTextColor(...color);
    };

    const drawFooter=()=>{
      setText(7.5,"normal",[135,135,140]);
      doc.text(`ÜbergabeCheck Business · Erstellt am ${new Date().toLocaleDateString("de-DE")}`,M,289);
      doc.text(`Seite ${pageNo}`,PAGE_W-M,289,{align:"right"});
    };

    const newPage=()=>{
      drawFooter();
      doc.addPage();
      pageNo++;
      y=M;
    };

    const ensure=height=>{if(y+height>BOTTOM)newPage();};

    const split=(text,width,size=10,style="normal")=>{
      setText(size,style);
      return doc.splitTextToSize(String(text??""),Math.max(8,width));
    };

    const textHeight=(lines,size=10,lineFactor=1.25)=>
      Math.max(size*.3528*lineFactor,(Array.isArray(lines)?lines.length:1)*size*.3528*lineFactor);

    const sectionTitle=title=>{
      ensure(13);
      if(y>M+1){
        doc.setDrawColor(...LINE);
        doc.setLineWidth(.25);
        doc.line(M,y,M+CONTENT_W,y);
        y+=7;
      }
      setText(14,"bold");
      doc.text(title,M,y+4.5);
      y+=11;
    };

    const roundedInfoCard=(x,top,width,label,text)=>{
      doc.setFillColor(245,245,246);
      doc.roundedRect(x,top,width,18,3,3,"F");
      setText(7.5,"normal",MUTED);
      doc.text(label.toUpperCase(),x+4,top+6);
      const lines=split(text,width-8,10,"bold").slice(0,2);
      setText(10,"bold");
      doc.text(lines,x+4,top+12,{lineHeightFactor:1.05});
    };

    const drawTextBox=async(text,emptyText="Keine Angaben dokumentiert.",label="")=>{
      const content=text||emptyText;
      const allLines=split(content,CONTENT_W-10,9.5,"normal");
      const lineH=4.6;
      let index=0;
      while(index<allLines.length){
        if(y>BOTTOM-15){newPage();continue;}
        const labelSpace=label?5:0;
        const maxLines=Math.max(1,Math.floor((BOTTOM-y-10-labelSpace)/lineH));
        const lines=allLines.slice(index,index+maxLines);
        const h=8+labelSpace+(lines.length*lineH);
        ensure(h+2);
        doc.setFillColor(...LIGHT);
        doc.roundedRect(M,y,CONTENT_W,h,3,3,"F");
        if(label){
          setText(7.2,"bold",MUTED);
          doc.text(label.toUpperCase(),M+5,y+5);
        }
        setText(9.5,"normal");
        doc.text(lines,M+5,y+(label?10:6),{lineHeightFactor:1.22});
        y+=h+4;
        index+=lines.length;
        if(index<allLines.length)newPage();
      }
    };

    const stateStyle=state=>{
      if(state==="damage") return {fill:[255,233,233],label:"Mangel vorhanden"};
      if(state==="wear") return {fill:[255,244,217],label:"Gebrauchsspuren"};
      return {fill:[233,245,236],label:"Ohne festgestellte Mängel"};
    };

    const drawStatePill=(state,top)=>{
      const style=stateStyle(state);
      setText(7.5,"bold");
      const width=Math.min(62,doc.getTextWidth(style.label)+7);
      doc.setFillColor(...style.fill);
      doc.roundedRect(M+CONTENT_W-width,top,width,7,3.5,3.5,"F");
      doc.text(style.label,M+CONTENT_W-(width/2),top+4.7,{align:"center"});
    };

    const drawPhotos=async urls=>{
      const valid=[];
      for(const url of (urls||[])){
        const converted=await dataUrlToJpeg(url);
        if(converted) valid.push(converted);
      }
      if(!valid.length)return;

      const gap=3;
      const cellW=(CONTENT_W-(gap*2))/3;
      const cellH=34;
      for(let i=0;i<valid.length;i+=3){
        ensure(cellH+5);
        const row=valid.slice(i,i+3);
        row.forEach((img,j)=>{
          const x=M+j*(cellW+gap);
          doc.setDrawColor(220,220,222);
          doc.roundedRect(x,y,cellW,cellH,2,2,"S");
          const ratio=img.width/img.height;
          let width=cellW-2;
          let height=cellH-2;
          if(ratio>width/height)height=width/ratio;
          else width=height*ratio;
          const imageX=x+(cellW-width)/2;
          const imageY=y+(cellH-height)/2;
          try{doc.addImage(img.data,"JPEG",imageX,imageY,width,height,undefined,"FAST");}
          catch(_error){}
        });
        y+=cellH+4;
      }
    };

    const address=value("address","Adresse nicht angegeben");
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

    setText(7.5,"bold",MUTED);
    doc.text("WOHNUNGSÜBERGABE · BUSINESS",M,y+2.5);
    y+=7;
    setText(24,"bold");
    doc.text("Übergabeprotokoll",M,y+8);
    y+=13;

    const addressLines=split(address,CONTENT_W,11.5,"normal");
    setText(11.5,"normal",[80,80,84]);
    doc.text(addressLines,M,y+2,{lineHeightFactor:1.2});
    y+=Math.max(8,textHeight(addressLines,11.5,1.2)+3);

    ensure(22);
    const metaGap=4;
    const metaW=(CONTENT_W-(metaGap*2))/3;
    roundedInfoCard(M,y,metaW,"Datum",formatDate(dateRaw));
    roundedInfoCard(M+metaW+metaGap,y,metaW,"Mieter",tenant);
    roundedInfoCard(M+(metaW+metaGap)*2,y,metaW,"Vermieter",landlord);
    y+=25;
    doc.setDrawColor(...TEXT);
    doc.setLineWidth(.55);
    doc.line(M,y,M+CONTENT_W,y);
    y+=8;

    sectionTitle("Übergabeübersicht");
    const rooms=Array.isArray(selectedRooms)?selectedRooms:[];
    const photos=rooms.reduce((total,room)=>total+((roomData?.[room]?.photos||[]).length),0);
    const meterCount=["electric","water","gas"].filter(id=>(document.getElementById(id)?.value||"").trim()).length;
    const overview=[
      ["Räume",String(rooms.length)],
      ["Fotos",String(photos)],
      ["Zählerstände",String(meterCount)],
      ["Schlüssel",(document.getElementById("keys")?.value||"").trim()?"Dokumentiert":"–"]
    ];
    const overviewGap=3;
    const overviewW=(CONTENT_W-(overviewGap*3))/4;
    overview.forEach((item,index)=>roundedInfoCard(M+index*(overviewW+overviewGap),y,overviewW,item[0],item[1]));
    y+=24;

    sectionTitle("Zählerstände");
    const meters=[
      {name:"Strom",no:"electricNo",val:"electric",unit:"kWh",type:"electric"},
      {name:"Wasser",no:"waterNo",val:"water",unit:"m³",type:"water"},
      {name:"Gas",no:"gasNo",val:"gas",unit:"m³",type:"gas"}
    ];

    for(const meter of meters){
      ensure(17);
      setText(10.5,"bold");
      doc.text(meter.name,M,y+4);
      const noLines=split(`Zählernummer: ${value(meter.no)}`,CONTENT_W*.65,8,"normal").slice(0,2);
      setText(8,"normal",MUTED);
      doc.text(noLines,M,y+9,{lineHeightFactor:1.05});
      const meterValue=(document.getElementById(meter.val)?.value||"").trim();
      const valueLines=split(meterValue?`${meterValue} ${meter.unit}`:"–",CONTENT_W*.28,10.5,"bold").slice(0,2);
      setText(10.5,"bold");
      doc.text(valueLines,M+CONTENT_W,y+5,{align:"right",lineHeightFactor:1.05});
      y+=Math.max(13,8+(Math.max(noLines.length,valueLines.length)*3));
      await drawPhotos(meterPhotos?.[meter.type]||[]);
      doc.setDrawColor(...LINE);
      doc.line(M,y,M+CONTENT_W,y);
      y+=5;
    }

    sectionTitle("Schlüsselübergabe");
    await drawTextBox((document.getElementById("keys")?.value||"").trim(),"Keine Angaben dokumentiert.");

    sectionTitle("Räume & Zustand");
    for(const room of rooms){
      const data=roomData?.[room]||{state:"ok",description:"",photos:[]};
      ensure(18);
      const roomLines=split(String(room),CONTENT_W-70,12,"bold").slice(0,2);
      setText(12,"bold");
      doc.text(roomLines,M,y+4.5,{lineHeightFactor:1.05});
      drawStatePill(data.state,y);
      y+=Math.max(10,5+(roomLines.length*4.5));

      if((data.description||"").trim()){
        await drawTextBox(data.description,"","Beschreibung");
      }else if(!(data.photos||[]).length && data.state!=="damage"){
        setText(8.5,"normal",MUTED);
        doc.text("Keine zusätzlichen Angaben dokumentiert.",M,y+3.5);
        y+=8;
      }

      if(data.state==="damage"){
        const status=defectStatusLabel(data.defectStatus||"open");
        const note=(data.defectNote||"").trim();
        const defectText=note?`Status: ${status}\n${note}`:`Status: ${status}`;
        await drawTextBox(defectText,"Status: Offen","Mängelbearbeitung");
      }

      await drawPhotos(data.photos||[]);
      doc.setDrawColor(...LINE);
      doc.line(M,y,M+CONTENT_W,y);
      y+=6;
    }

    sectionTitle("Allgemeine Bemerkungen");
    await drawTextBox((document.getElementById("notes")?.value||"").trim(),"Keine weiteren Bemerkungen.");

    sectionTitle("Unterschriften");
    const signatureDate=formatDate(document.getElementById("signatureDate")?.value||"");
    setText(8,"normal",MUTED);
    doc.text(`Datum der Unterschrift: ${signatureDate}`,M,y+3);
    y+=8;
    ensure(50);

    const signatureGap=8;
    const signatureW=(CONTENT_W-signatureGap)/2;
    const signatures=[
      {x:M,title:"Mieter",place:value("tenantSignaturePlace"),image:canvasToPng("sigTenant")},
      {x:M+signatureW+signatureGap,title:"Vermieter",place:value("landlordSignaturePlace"),image:canvasToPng("sigLandlord")}
    ];

    for(const signature of signatures){
      setText(10.5,"bold");
      doc.text(signature.title,signature.x,y+4);
      doc.setDrawColor(205,205,208);
      doc.roundedRect(signature.x,y+8,signatureW,25,2,2,"S");
      if(signature.image){
        try{doc.addImage(signature.image,"PNG",signature.x+2,y+10,signatureW-4,21,undefined,"FAST");}
        catch(_error){}
      }
      setText(8,"normal",MUTED);
      const placeLines=split(`Ort: ${signature.place}`,signatureW,8,"normal").slice(0,2);
      doc.text(placeLines,signature.x,y+38,{lineHeightFactor:1.15});
      doc.text(`Datum: ${signatureDate}`,signature.x,y+46);
    }

    drawFooter();
    return {blob:doc.output("blob"),filename:protocolPdfFilename()};
  }

  function downloadBlob(blob,filename){
    const url=URL.createObjectURL(blob);
    const link=document.createElement("a");
    link.href=url;
    link.download=filename;
    link.style.display="none";
    document.body.appendChild(link);
    link.click();
    link.remove();
    setTimeout(()=>URL.revokeObjectURL(url),1500);
  }

  async function saveTransferPdfWithJsPdf(){
    try{
      if(typeof persistCurrentTransfer==="function"){
        const ok=await persistCurrentTransfer();
        if(!ok)return;
      }
      const result=await createProtocolPdfBlob();
      downloadBlob(result.blob,result.filename);
    }catch(error){
      console.error("PDF-Export:",error);
      if(error?.message==="NO_PROTOCOL"){
        alert("Bitte zuerst das Übergabeprotokoll erstellen.");
      }else{
        alert("Die PDF konnte gerade nicht erstellt werden. Bitte Seite einmal neu laden und erneut versuchen.");
      }
    }
  }

  window.createProtocolPdfBlob=createProtocolPdfBlob;
  window.saveTransferPdf=saveTransferPdfWithJsPdf;
})();
