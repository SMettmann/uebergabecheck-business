(function(){
  "use strict";

  let cachedRole=null;
  let rolePromise=null;

  function accessDenied(message){
    window.alert(message);
  }

  async function loadCurrentRole(force=false){
    if(!force && cachedRole) return cachedRole;
    if(!force && rolePromise) return rolePromise;

    rolePromise=(async()=>{
      try{
        if(typeof initSupabase==="function") initSupabase();
        if(typeof supabaseClient==="undefined" || !supabaseClient) return null;

        let user=(typeof supabaseUser!=="undefined" ? supabaseUser : null);
        if(!user){
          const {data}=await supabaseClient.auth.getSession();
          user=data?.session?.user||null;
        }
        if(!user) return null;

        const {data,error}=await supabaseClient
          .from("company_members")
          .select("role")
          .eq("user_id",user.id)
          .maybeSingle();

        if(error){
          console.error("ÜbergabeCheck Rollenprüfung:",error);
          return null;
        }

        cachedRole=data?.role||null;
        window.businessCurrentRole=cachedRole;
        return cachedRole;
      }catch(error){
        console.error("ÜbergabeCheck Rollenprüfung:",error);
        return null;
      }finally{
        rolePromise=null;
      }
    })();

    return rolePromise;
  }

  async function requireManager(){
    const role=await loadCurrentRole();
    if(role==="owner" || role==="admin") return true;
    if(role==="member"){
      accessDenied("Keine Berechtigung – nur Inhaber und Admins können Objekte und Wohnungen verwalten.");
      return false;
    }
    accessDenied("Deine Benutzerrolle konnte gerade nicht geprüft werden. Bitte lade die Seite neu und versuche es erneut.");
    return false;
  }

  async function requireTransferDelete(){
    const role=await loadCurrentRole();
    if(role==="owner" || role==="admin") return true;
    if(role==="member"){
      accessDenied("Keine Berechtigung – nur Inhaber und Admins können Übergaben löschen. Du kannst Übergaben weiterhin bearbeiten.");
      return false;
    }
    accessDenied("Deine Benutzerrolle konnte gerade nicht geprüft werden. Bitte lade die Seite neu und versuche es erneut.");
    return false;
  }

  async function requireOwner(){
    const role=await loadCurrentRole();
    if(role==="owner") return true;
    if(role==="admin" || role==="member"){
      accessDenied("Keine Berechtigung – nur der Inhaber kann die Unternehmensdaten ändern.");
      return false;
    }
    accessDenied("Deine Benutzerrolle konnte gerade nicht geprüft werden. Bitte lade die Seite neu und versuche es erneut.");
    return false;
  }

  function wrapFunction(name,permissionCheck){
    const original=window[name];
    if(typeof original!=="function") return;
    if(original.__uebergabeRoleGuard) return;

    const wrapped=async function(...args){
      if(!(await permissionCheck())) return;
      return original.apply(this,args);
    };
    wrapped.__uebergabeRoleGuard=true;
    wrapped.__uebergabeOriginal=original;
    window[name]=wrapped;
  }

  function installGuards(){
    [
      "showObjectForm",
      "editObject",
      "saveObject",
      "deleteObject",
      "showApartmentForm",
      "editApartment",
      "saveApartment",
      "deleteApartment"
    ].forEach(name=>wrapFunction(name,requireManager));

    wrapFunction("deleteBusinessTransfer",requireTransferDelete);
    wrapFunction("saveCompanyProfile",requireOwner);
  }

  function init(){
    installGuards();
    loadCurrentRole(true);

    try{
      if(typeof supabaseClient!=="undefined" && supabaseClient?.auth){
        supabaseClient.auth.onAuthStateChange(()=>{
          cachedRole=null;
          setTimeout(()=>loadCurrentRole(true),0);
        });
      }
    }catch(error){
      console.error("ÜbergabeCheck Rollen-Hotfix:",error);
    }
  }

  if(document.readyState==="loading") document.addEventListener("DOMContentLoaded",init,{once:true});
  else init();
})();
