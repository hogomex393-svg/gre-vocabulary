const allowedOrigins = new Set(['https://hogomex393-svg.github.io', 'http://localhost:18765', 'http://127.0.0.1:18765', 'http://127.0.0.1:18767']);
const encoder = new TextEncoder();
async function hash(value) { return [...new Uint8Array(await crypto.subtle.digest('SHA-256', encoder.encode(value)))].map(n=>n.toString(16).padStart(2,'0')).join(''); }
function same(a,b) { if (typeof a!=='string'||typeof b!=='string'||a.length!==b.length) return false;let difference=0;for(let i=0;i<a.length;i++)difference|=a.charCodeAt(i)^b.charCodeAt(i);return difference===0; }
export async function handleSync(request, env) {
  const origin = request.headers.get('Origin');
  const cors = { 'Content-Type':'application/json; charset=utf-8','Cache-Control':'no-store','Vary':'Origin','X-Content-Type-Options':'nosniff' };
  if (origin && allowedOrigins.has(origin)) Object.assign(cors, { 'Access-Control-Allow-Origin':origin, 'Access-Control-Allow-Methods':'GET, PUT, OPTIONS', 'Access-Control-Allow-Headers':'Authorization, Content-Type', 'Access-Control-Max-Age':'600' });
  const reply = (status,data) => new Response(status===204?null:JSON.stringify(data),{status,headers:cors});
  if (origin && !allowedOrigins.has(origin)) return reply(403,{error:'来源不允许'});
  if (request.method==='OPTIONS') return reply(204,null);
  if (!['GET','PUT'].includes(request.method)) return reply(405,{error:'方法不允许'});
  const id = new URL(request.url).pathname.split('/').filter(Boolean).at(-1);
  const token = request.headers.get('Authorization')?.replace(/^Bearer /,'');
  if (!/^[a-f0-9]{64}$/.test(id||'') || !/^[a-f0-9]{64}$/.test(token||'')) return reply(401,{error:'需要有效连接码'});
  if (!env.VAULT_ID || !env.AUTH_DIGEST || !env.DB) return reply(503,{error:'云存档服务尚未配置'});
  if (!same(id,env.VAULT_ID) || !same(await hash(token),env.AUTH_DIGEST)) return reply(403,{error:'连接码不正确'});
  try {
    const record = await env.DB.prepare('SELECT ciphertext, iv, revision, updated_at FROM study_states WHERE id = ?').bind(id).first();
    if (request.method==='GET') return record?reply(200,record):reply(404,{error:'云存档尚未创建'});
    if (Number(request.headers.get('Content-Length')||0)>1500000) return reply(413,{error:'存档过大'});
    const text = await request.text();if(text.length>1500000)return reply(413,{error:'存档过大'});
    let body;try{body=JSON.parse(text)}catch{return reply(400,{error:'无效存档'})}
    if (!body || !Number.isSafeInteger(body.revision) || body.revision<0 || !/^[A-Za-z0-9+/]{16}$/.test(body.iv||'') || typeof body.ciphertext!=='string' || body.ciphertext.length<24 || body.ciphertext.length>1400000 || !/^[A-Za-z0-9+/]+={0,2}$/.test(body.ciphertext)) return reply(400,{error:'无效加密存档'});
    if ((record?.revision||0)!==body.revision) return reply(409,{error:'另一个设备已更新进度，请重新读取',revision:record?.revision||0});
    const now=Date.now();let result;
    if (!record) result = await env.DB.prepare('INSERT OR IGNORE INTO study_states (id, ciphertext, iv, revision, created_at, updated_at) VALUES (?, ?, ?, 1, ?, ?)').bind(id,body.ciphertext,body.iv,now,now).run();
    else result=await env.DB.prepare('UPDATE study_states SET previous_ciphertext = ciphertext, previous_iv = iv, ciphertext = ?, iv = ?, revision = revision + 1, updated_at = ? WHERE id = ? AND revision = ?').bind(body.ciphertext,body.iv,now,id,body.revision).run();
    if (result.meta.changes!==1) return reply(409,{error:'另一个设备已更新进度，请重新读取'});
    return reply(200,{revision:body.revision+1,updated_at:now});
  } catch { return reply(503,{error:'云存档暂时不可用，请保留当前页面并导出备份'}); }
}
