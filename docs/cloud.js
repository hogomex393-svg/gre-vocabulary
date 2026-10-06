'use strict';
(() => {
  const endpoint = window.GRE_CONFIG?.cloudUrl;
  if (!endpoint) return;
  const storage = window.GRE_STORAGE;
  const deviceLoad = storage.load, deviceSave = storage.save;
  const deviceMirror = storage.mirrorKey, settingKey = deviceMirror + ':connection';
  const encoder = new TextEncoder(), decoder = new TextDecoder();
  let connection = null, pendingCode = null;
  const hex = bytes => [...new Uint8Array(bytes)].map(n => n.toString(16).padStart(2, '0')).join('');
  const hash = text => crypto.subtle.digest('SHA-256', encoder.encode(text));
  function base64(bytes) { let s='';const data=new Uint8Array(bytes);for(let i=0;i<data.length;i+=8192)s+=String.fromCharCode(...data.subarray(i,i+8192));return btoa(s); }
  function bytes(text) { return Uint8Array.from(atob(text), c=>c.charCodeAt(0)); }
  async function derive(code) {
    code=String(code).trim();
    if (!/^GRE-[A-Za-z0-9_-]{43}$/.test(code)) throw Error('连接码格式不正确');
    return { code, id:hex(await hash('id:'+code)), token:hex(await hash('auth:'+code)), key:await crypto.subtle.importKey('raw',await hash('enc:'+code),'AES-GCM',false,['encrypt','decrypt']) };
  }
  function commitConnection(c) {
    connection=c;pendingCode=null;
    try { localStorage.setItem(settingKey,c.code); } catch {}
    if (location.hash.startsWith('#sync=')) history.replaceState(null,'',location.pathname+location.search);
  }
  async function request(c,method,body) {
    let response;
    try { response=await fetch(endpoint+'/api/sync/'+c.id,{method,headers:{Authorization:'Bearer '+c.token,...(body?{'Content-Type':'application/json'}:{})},body:body?JSON.stringify(body):undefined,credentials:'omit',cache:'no-store',signal:AbortSignal.timeout(20000)}); }
    catch { throw Error('暂时无法连接云存档，进度已保留在此设备'); }
    if (!response.ok) {
      if(response.status===409)throw Object.assign(Error('另一个设备已更新，请先读取云端最新进度'),{conflict:true});
      if([401,403].includes(response.status))throw Error('连接码不正确，请重新输入');
      if(response.status===404)throw Error('云存档尚未初始化，请联系网站管理员');
      throw Error('云存档暂时不可用，进度已保留在此设备');
    }
    return response.json();
  }
  async function read(c) {
    const record=await request(c,'GET');
    let state;
    try { state=JSON.parse(decoder.decode(await crypto.subtle.decrypt({name:'AES-GCM',iv:bytes(record.iv)},c.key,bytes(record.ciphertext)))); }
    catch { throw Error('无法解密此存档，请检查连接码'); }
    if(!state||state.version!==1||!state.days||!Number.isInteger(state.activeDay))throw Error('云存档格式不正确，请保留设备备份');
    return {...state,revision:record.revision};
  }
  storage.load = async () => {
    if (!connection) return deviceLoad();
    const state=await read(connection);
    if(pendingCode)commitConnection(connection);
    return state;
  };
  storage.save = async (state,revision) => {
    if(!connection)return deviceSave(state,revision);
    const snapshot=JSON.stringify(state),iv=crypto.getRandomValues(new Uint8Array(12));
    const ciphertext=base64(await crypto.subtle.encrypt({name:'AES-GCM',iv},connection.key,encoder.encode(snapshot)));
    const result=await request(connection,'PUT',{revision,iv:base64(iv),ciphertext});
    try { const backup=await deviceLoad();await deviceSave(JSON.parse(snapshot),backup?.revision||0); } catch {}
    return result.revision;
  };
  Object.defineProperties(storage,{
    mirrorKey:{get:()=>connection?deviceMirror+':cloud':deviceMirror},
    savedMessage:{get:()=>connection?'已自动同步到云端':storage.hosted?'已自动保存到此设备':'已自动保存到电脑'},
    readyMessage:{get:()=>connection?'云端进度已同步':storage.hosted?'仅此设备 · 尚未连接云同步':'进度自动保存到电脑'}
  });
  window.GRE_CLOUD={
    enabled:true,
    get connected(){return !!connection},
    async prepare(){let code;try{code=localStorage.getItem(settingKey)}catch{}if(location.hash.startsWith('#sync='))code=decodeURIComponent(location.hash.slice(6));if(code){connection=await derive(code);pendingCode=code}},
    async connect(code){const candidate=await derive(code);const state=await read(candidate);commitConnection(candidate);return state},
    async readRemote(){if(!connection)throw Error('请先连接云存档');return read(connection)},
    get link(){if(!connection)return '';const url=new URL(location.href);url.hash='sync='+connection.code;return url.href},
  };
})();
