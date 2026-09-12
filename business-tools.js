/* ÜbergabeCheck Business — Support & Admin launcher */
(function(){
  "use strict";
  if(window.__uebergabeCheckBusinessToolsInstalled)return;
  window.__uebergabeCheckBusinessToolsInstalled=true;

  const SUPABASE_URL="https://fkirkglhcpltxlcsozmd.supabase.co";
  const SUPABASE_KEY="sb_publishable_lNeX7Hrtp9-FFl3NVb_Gaw_O-21yXWr";
  let client=null;

  function db(){
    if(client)return client;
    if(!window.supabase?.createClient)return null;
    client=window.supabase.createClient(SUPABASE_URL,SUPABASE_KEY);
    return client;
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

  async function sync(){
    const api=db();if(!api)return;
    addSupportButton();
    try{
      const {data:{user}}=await api.auth.getUser();
      if(!user){removeAdminButton();return;}
      const {data,error}=await api.from("app_admins").select("user_id").eq("user_id",user.id).maybeSingle();
      if(!error&&data)addAdminButton();else removeAdminButton();
    }catch(_error){removeAdminButton();}
  }

  const observer=new MutationObserver(()=>{
    if(dashboardActions()){
      addSupportButton();
      setTimeout(sync,20);
    }
  });

  function init(){
    observer.observe(document.documentElement,{childList:true,subtree:true});
    sync();
    const api=db();
    api?.auth?.onAuthStateChange(()=>setTimeout(sync,100));
    setTimeout(sync,500);
  }

  if(document.readyState==="loading")document.addEventListener("DOMContentLoaded",init,{once:true});
  else init();
})();
