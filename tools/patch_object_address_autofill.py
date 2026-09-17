from pathlib import Path

path = Path("business-tools.js")
text = path.read_text(encoding="utf-8")
marker = "UEBERGABECHECK_OBJECT_ADDRESS_AUTOFILL_V1"

if marker in text:
    print("Address autofill already installed.")
    raise SystemExit(0)

old = '''    const originalStartApp=window.startApp;
    if(typeof originalStartApp==="function"){
      window.startApp=function(...args){
        appliedTextBlocks=[];
        const result=originalStartApp.apply(this,args);
        ensureTransferTextBlockBuilder();
        renderAppliedTextBlocks();
        return result;
      };
    }
'''

new = '''    const originalStartApp=window.startApp;
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
'''

if old not in text:
    raise SystemExit("Expected startApp wrapper not found; no file changed.")

path.write_text(text.replace(old, new, 1), encoding="utf-8")
print("Installed automatic object address transfer.")
