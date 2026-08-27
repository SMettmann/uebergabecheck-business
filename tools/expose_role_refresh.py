from pathlib import Path

path=Path('tools/build_integrated_app.py')
s=path.read_text(encoding='utf-8')
old='''  function isManager(role){return role==="owner" || role==="admin";}\n\n  function resetRoleState(){'''
new='''  function isManager(role){return role==="owner" || role==="admin";}\n\n  window.refreshBusinessRole=()=>loadCurrentBusinessRole(true);\n\n  function resetRoleState(){'''
if 'window.refreshBusinessRole=()=>loadCurrentBusinessRole(true);' in s:
    print('Role refresh bridge already present')
elif old in s:
    s=s.replace(old,new,1)
    path.write_text(s,encoding='utf-8')
    print('Role refresh bridge added')
else:
    raise SystemExit('Role guard anchor not found')