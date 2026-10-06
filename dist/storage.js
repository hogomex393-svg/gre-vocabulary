'use strict';
(() => {
  const hosted = window.GRE_CONFIG?.hosted === true || !['localhost', '127.0.0.1', '[::1]'].includes(location.hostname);
  const basePath = location.pathname.replace(/index\.html$/, '').replace(/\/$/, '');
  const mirrorKey = hosted ? 'gre-study-mirror-v1:' + basePath : 'gre-study-mirror-v1';
  let connection;
  const failure = (message, conflict = false) => Object.assign(new Error(message), { conflict });
  function database() {
    if (!connection) connection = new Promise((resolve, reject) => {
      const request = indexedDB.open('gre-vocabulary-progress-v1:' + basePath, 1);
      request.onupgradeneeded = () => request.result.createObjectStore('states');
      request.onsuccess = () => {
        const db = request.result;
        db.onversionchange = () => { db.close(); connection = undefined; };
        resolve(db);
      };
      request.onerror = () => { connection = undefined; reject(failure('无法读取此设备存档，请检查浏览器存储设置')); };
      request.onblocked = () => reject(failure('请关闭此网站的其他页面后重新打开'));
    });
    return connection;
  }
  async function load() {
    if (!hosted) {
      const response = await fetch('/api/state');
      if (!response.ok) throw failure('无法读取电脑存档，请检查本地服务');
      return (await response.json()).state;
    }
    const db = await database();
    return new Promise((resolve, reject) => {
      const transaction = db.transaction('states', 'readonly');
      const request = transaction.objectStore('states').get('current');
      request.onsuccess = () => resolve(request.result || null);
      request.onerror = () => reject(failure('读取失败，请保留当前页面并导出存档'));
    });
  }
  async function save(state, revision) {
    if (!hosted) {
      const response = await fetch('/api/state', { method: 'PUT', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ state, revision }) });
      if (!response.ok) throw failure(response.status === 409 ? '另一页面已更新，请刷新' : '保存失败，请导出存档', response.status === 409);
      return (await response.json()).revision;
    }
    const db = await database();
    // Capture this exact update before the transaction starts; later clicks are saved in the next transaction.
    const snapshot = JSON.parse(JSON.stringify(state));
    return new Promise((resolve, reject) => {
      const transaction = db.transaction('states', 'readwrite');
      const store = transaction.objectStore('states');
      const request = store.get('current');
      let conflict = false;
      request.onsuccess = () => {
        const previous = request.result;
        if ((previous?.revision || 0) !== revision) { conflict = true; transaction.abort(); return; }
        if (previous) {
          store.put(previous, 'previous');
          const backupKey = 'backup-' + new Date().toLocaleDateString('en-CA', { timeZone: 'Asia/Shanghai' });
          const backup = store.get(backupKey);
          backup.onsuccess = () => { if (!backup.result) store.put(previous, backupKey); };
        }
        store.put({ ...snapshot, revision: revision + 1 }, 'current');
      };
      transaction.oncomplete = () => resolve(revision + 1);
      transaction.onerror = transaction.onabort = () => reject(failure(conflict ? '另一页面已更新，请刷新' : '保存失败，请导出存档并检查设备剩余空间', conflict));
    });
  }
  window.GRE_STORAGE = {
    hosted, mirrorKey, load, save,
    savedMessage: hosted ? '已自动保存到此设备' : '已自动保存到电脑',
    readyMessage: hosted ? '进度保存在此设备' : '进度自动保存到电脑'
  };
})();
