from pathlib import Path

INDEX = Path("index.html")
PDF = Path("pdf-export.js")
MARKER = "UEBERGABECHECK_TRANSFER_CREATOR_V1"


def replace_once(text: str, old: str, new: str, label: str) -> str:
    if new in text:
        return text
    if old not in text:
        raise RuntimeError(f"Pattern not found for {label}")
    return text.replace(old, new, 1)


index = INDEX.read_text(encoding="utf-8")

if MARKER not in index:
    # Cache creator together with transfer metadata.
    index = replace_once(
        index,
        'select("id,apartment_id,type,status,created_at,tenant_name,tenant_surname,open_defect_count")',
        'select("id,apartment_id,type,status,created_at,tenant_name,tenant_surname,open_defect_count,created_by_name")',
        "initial transfer metadata select",
    )
    index = replace_once(
        index,
        'tenantSurname:t.tenant_surname||"",openDefectCount:Number(t.open_defect_count||0)});',
        'tenantSurname:t.tenant_surname||"",createdByName:t.created_by_name||"",openDefectCount:Number(t.open_defect_count||0)});',
        "initial transfer metadata mapping",
    )

    # New transfer: keep the trigger-populated creator available for protocol/PDF.
    index = replace_once(
        index,
        'window.currentBusinessApartmentId=apartment.id;\n  window.currentBusinessTransferId=transfer.id;',
        'window.currentBusinessApartmentId=apartment.id;\n  window.currentBusinessTransferId=transfer.id;\n  window.currentBusinessTransferCreatedByName=transfer.created_by_name||"";',
        "new transfer creator state",
    )
    index = replace_once(
        index,
        'status:transfer.status\n  });',
        'status:transfer.status,\n    createdByName:transfer.created_by_name||""\n  });',
        "new transfer cache creator",
    )

    # Apartment transfer list.
    index = replace_once(
        index,
        'select("id,type,status,created_at,apartment_id,tenant_name,tenant_surname,open_defect_count").eq("apartment_id",selectedApartmentId)',
        'select("id,type,status,created_at,apartment_id,tenant_name,tenant_surname,open_defect_count,created_by_name").eq("apartment_id",selectedApartmentId)',
        "apartment transfer select",
    )
    index = replace_once(
        index,
        'tenantSurname:t.tenant_surname||"",openDefectCount:Number(t.open_defect_count||0)}));',
        'tenantSurname:t.tenant_surname||"",createdByName:t.created_by_name||"",openDefectCount:Number(t.open_defect_count||0)}));',
        "apartment transfer mapping",
    )
    index = replace_once(
        index,
        '<small>Erstellt am ${esc(date)}</small>',
        '<small>Erstellt am ${esc(date)}${t.created_by_name?" · Erstellt von: "+esc(t.created_by_name):""}</small>',
        "apartment transfer creator display",
    )

    # Open transfer: load creator into a stable global for protocol/PDF generation.
    index = replace_once(
        index,
        '.select("id,data,status,apartment_id")\n    .eq("id",transferId)',
        '.select("id,data,status,apartment_id,created_by_name")\n    .eq("id",transferId)',
        "open transfer select",
    )
    index = replace_once(
        index,
        '    return;\n  }\n\n  startApp();\n\n  if(transfer?.data){',
        '    return;\n  }\n\n  window.currentBusinessTransferCreatedByName=transfer?.created_by_name||"";\n  startApp();\n\n  if(transfer?.data){',
        "open transfer creator state",
    )

    # Main transfer overview.
    index = replace_once(
        index,
        'select("id,type,status,created_at,apartment_id,tenant_name,tenant_surname,open_defect_count,apartments(id,name,number,object_id,objects(id,name))")',
        'select("id,type,status,created_at,apartment_id,tenant_name,tenant_surname,open_defect_count,created_by_name,apartments(id,name,number,object_id,objects(id,name))")',
        "main transfer select",
    )
    index = replace_once(
        index,
        '${tenantName&&tenantName!==tenantSurname?" · "+esc(tenantName):""} · ${esc(date)}</small>',
        '${tenantName&&tenantName!==tenantSurname?" · "+esc(tenantName):""} · ${esc(date)}${t.created_by_name?" · Erstellt von: "+esc(t.created_by_name):""}</small>',
        "main transfer creator display",
    )

    # Dashboard recent transfers.
    index = replace_once(
        index,
        '.select("id,type,status,created_at,apartment_id,data,apartments(id,name,object_id,objects(id,name))")',
        '.select("id,type,status,created_at,apartment_id,data,created_by_name,apartments(id,name,object_id,objects(id,name))")',
        "dashboard transfer select",
    )
    index = replace_once(
        index,
        '<small>${esc(o?.name || "Objekt")} · ${esc(a?.name || "Wohnung")}</small>',
        '<small>${esc(o?.name || "Objekt")} · ${esc(a?.name || "Wohnung")}${t.created_by_name?" · Erstellt von: "+esc(t.created_by_name):""}</small>',
        "dashboard creator display",
    )

    # Make creator visible in the on-screen protocol too.
    index = replace_once(
        index,
        '        </div>\n      </div>\n\n      <div class="protocol-section">\n        <div class="section-title"><span>Übergabeübersicht</span></div>',
        '        </div>\n        ${window.currentBusinessTransferCreatedByName?`<div class="muted" style="margin-top:10px;">Erstellt von: ${esc(window.currentBusinessTransferCreatedByName)}</div>`:""}\n      </div>\n\n      <div class="protocol-section">\n        <div class="section-title"><span>Übergabeübersicht</span></div>',
        "protocol creator display",
    )

    # Reset creator on leaving/account switch so no previous user leaks into another protocol.
    index = replace_once(
        index,
        'window.currentBusinessTransferId=null;\n\n  document.getElementById("apartmentDetailSection")',
        'window.currentBusinessTransferId=null;\n  window.currentBusinessTransferCreatedByName="";\n\n  document.getElementById("apartmentDetailSection")',
        "home creator reset",
    )
    index = replace_once(
        index,
        'window.businessSubscription = null;\n\n  const dashboard=',
        'window.businessSubscription = null;\n  window.currentBusinessTransferCreatedByName="";\n\n  const dashboard=',
        "logout creator reset",
    )

    index = index.replace("</script>\n<script>\ndocument.addEventListener", f"// {MARKER}\n</script>\n<script>\ndocument.addEventListener", 1)
    INDEX.write_text(index, encoding="utf-8")

pdf = PDF.read_text(encoding="utf-8")
if MARKER not in pdf:
    pdf = replace_once(
        pdf,
        '    const landlord=value("landlord");\n    const company=window.businessCompanyProfile||{};',
        '    const landlord=value("landlord");\n    const createdBy=String(window.currentBusinessTransferCreatedByName||"").trim();\n    const company=window.businessCompanyProfile||{};',
        "pdf creator variable",
    )
    pdf = replace_once(
        pdf,
        '    roundedInfoCard(M+(metaW+metaGap)*2,y,metaW,"Vermieter",landlord);\n    y+=25;\n    doc.setDrawColor(...TEXT);',
        '    roundedInfoCard(M+(metaW+metaGap)*2,y,metaW,"Vermieter",landlord);\n    y+=25;\n    if(createdBy){\n      setText(8.5,"normal",MUTED);\n      doc.text(`Erstellt von: ${createdBy}`,M,y);\n      y+=5;\n    }\n    doc.setDrawColor(...TEXT);',
        "pdf creator display",
    )
    pdf += f"\n// {MARKER}\n"
    PDF.write_text(pdf, encoding="utf-8")

print("Transfer creator attribution patched")
