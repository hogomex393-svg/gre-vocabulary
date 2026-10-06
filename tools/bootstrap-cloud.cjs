const fs=require('node:fs'),path=require('node:path'),crypto=require('node:crypto');
const root=path.resolve(__dirname,'..'),endpoint='https://gre-vocabulary-sync-hogomex393.hogomex393.chatgpt.site';
const vault=JSON.parse(fs.readFileSync(path.join(root,'存档/云同步配置.private.json'),'utf8'));
const url=endpoint+'/api/sync/'+vault.id,headers={Authorization:'Bearer '+vault.token,Origin:'https://hogomex393-svg.github.io','Content-Type':'application/json'};
async function encrypt(state){const iv=crypto.randomBytes(12),key=crypto.createHash('sha256').update('enc:'+vault.code).digest();const cipher=crypto.createCipheriv('aes-256-gcm',key,iv);const encrypted=Buffer.concat([cipher.update(JSON.stringify(state),'utf8'),cipher.final(),cipher.getAuthTag()]);return {iv:iv.toString('base64'),ciphertext:encrypted.toString('base64')}}
async function run(){
 const response=await fetch(url,{headers});
 if(response.status===404){const local=await (await fetch('http://127.0.0.1:18765/api/state')).json();if(!local.state)throw Error('Local study progress unavailable');const backup=path.join(root,'存档/迁移前本地进度.json');if(!fs.existsSync(backup))fs.writeFileSync(backup,JSON.stringify(local.state,null,2));const payload=await encrypt(local.state);const put=await fetch(url,{method:'PUT',headers,body:JSON.stringify({...payload,revision:0})});if(!put.ok)throw Error('Cloud initialization failed: '+put.status+' '+await put.text());}
 else if(!response.ok)throw Error('Cloud request failed: '+response.status+' '+await response.text());
 const loaded=await fetch(url,{headers});if(!loaded.ok)throw Error('Readback failed: '+loaded.status);const record=await loaded.json();
 const key=crypto.createHash('sha256').update('enc:'+vault.code).digest(),data=Buffer.from(record.ciphertext,'base64'),decipher=crypto.createDecipheriv('aes-256-gcm',key,Buffer.from(record.iv,'base64'));decipher.setAuthTag(data.subarray(-16));const state=JSON.parse(Buffer.concat([decipher.update(data.subarray(0,-16)),decipher.final()]).toString('utf8'));
 const link='https://hogomex393-svg.github.io/gre-vocabulary/#sync='+vault.code;
 fs.writeFileSync(path.join(root,'存档/专属同步链接.txt'),link+'\n');
 fs.writeFileSync(path.join(root,'tools/cloud-bootstrap-state.json'),JSON.stringify({...state,revision:record.revision},null,2));
 console.log(JSON.stringify({cloud:'ready',revision:record.revision,learningDay:state.activeDay+1,cors:loaded.headers.get('Access-Control-Allow-Origin'),encrypted:true}));
}
run().catch(e=>{console.error(e.message);process.exitCode=1});
