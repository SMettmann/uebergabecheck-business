from pathlib import Path
import re

p = Path("index.html")
s = p.read_text(encoding="utf-8")

start = s.find("async function openTransferEmail(){")
end = s.find("function showSummary(){", start)
assert start != -1 and end != -1, "openTransferEmail block not found"

replacement = '''async function openTransferEmail(){
  const protocol=document.querySelector("#summary .protocol");
  if(!protocol){
    alert("Bitte zuerst das Übergabeprotokoll erstellen.");
    return;
  }

  const address=document.getElementById("address")?.value.trim()||"Wohnungsübergabe";
  const tenant=document.getElementById("tenant")?.value.trim()||"–";
  const dateRaw=document.getElementById("date")?.value||"";
  const dateFormatted=dateRaw?new Date(dateRaw+"T12:00:00").toLocaleDateString("de-DE"):"–";
  const subject=`Übergabeprotokoll – ${address}`;
  const text=`Hallo,\\r\\n\\r\\nanbei das Übergabeprotokoll zur Wohnung ${address}.\\r\\n\\r\\nDatum: ${dateFormatted}\\r\\nMieter: ${tenant}\\r\\n\\r\\nDokumentiert mit ÜbergabeCheck – einfach, vollständig und nachvollziehbar.\\r\\nwww.uebergabe-check.de\\r\\n\\r\\nViele Grüße`;

  try{
    if(typeof window.createProtocolPdfBlob!=="function") throw new Error("PDF_UNAVAILABLE");
    const saved=await persistCurrentTransfer();
    if(!saved) return;

    const {blob,filename}=await window.createProtocolPdfBlob();
    const file=new File([blob],filename,{type:"application/pdf"});

    if(navigator.share && navigator.canShare && navigator.canShare({files:[file]})){
      await navigator.share({
        title:subject,
        text,
        files:[file]
      });
      return;
    }

    const url=URL.createObjectURL(blob);
    const link=document.createElement("a");
    link.href=url;
    link.download=filename||"Uebergabeprotokoll.pdf";
    document.body.appendChild(link);
    link.click();
    link.remove();
    setTimeout(()=>URL.revokeObjectURL(url),2000);

    window.location.href=`mailto:?subject=${encodeURIComponent(subject)}&body=${encodeURIComponent(text)}`;
  }catch(err){
    if(err&&err.name==="AbortError") return;
    console.error("E-Mail/PDF-Share fehlgeschlagen:",err);
    if(err?.message==="PDF_UNAVAILABLE") alert("Die PDF-Funktion ist noch nicht verfügbar. Bitte die Seite neu laden.");
    else alert("Die PDF konnte nicht für die E-Mail vorbereitet werden. Bitte versuche es noch einmal.");
  }
}

'''

s = s[:start] + replacement + s[end:]
s = s.replace("✉ Per E-Mail senden", "📧 Per E-Mail senden")

assert "navigator.canShare({files:[file]})" in s
assert "📧 Per E-Mail senden" in s
assert "transferEmailOverlay" not in s
assert "sendTransferEmail" not in s

p.write_text(s, encoding="utf-8")

scripts = re.findall(r"<script(?:\\s+[^>]*)?>(.*?)</script>", s, re.S)
for i, script in enumerate(scripts):
    Path(f"/tmp/inline-{i}.js").write_text(script, encoding="utf-8")
