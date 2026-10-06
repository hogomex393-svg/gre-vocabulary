import { DatabaseSync } from 'node:sqlite';
import { webcrypto, randomBytes, createHash } from 'node:crypto';
import { readFileSync, readdirSync } from 'node:fs';
import assert from 'node:assert/strict';
import { handleSync } from '../lib/sync-api.mjs';
const db=new DatabaseSync(':memory:');
for(const name of readdirSync(new URL('../drizzle/',import.meta.url)).filter(n=>n.endsWith('.sql')))db.exec(readFileSync(new URL('../drizzle/'+name,import.meta.url),'utf8'));
const adapter={
  prepare(sql){
    return {
      bind(...args){
        const stmt=db.prepare(sql);
        return {
          async first(){return stmt.get(...args)||null},
          async run(){const result=stmt.run(...args);return {meta:{changes:Number(result.changes)}}}
        };
      }
    };
  }
};
const token=randomBytes(32).toString('hex'),id=randomBytes(32).toString('hex');
const env={DB:adapter,VAULT_ID:id,AUTH_DIGEST:createHash('sha256').update(token).digest('hex')};
const url='https://sync.test/api/sync/'+id;
const call=(method,body,auth=token,origin='https://hogomex393-svg.github.io')=>handleSync(new Request(url,{method,headers:{Origin:origin,Authorization:'Bearer '+auth,...(body?{'Content-Type':'application/json'}:{})},body:body?JSON.stringify(body):undefined}),env);
assert.equal((await call('GET')).status,404);
assert.equal((await call('GET',null,randomBytes(32).toString('hex'))).status,403);
assert.equal((await call('GET',null,token,'https://other.test')).status,403);
assert.equal((await call('OPTIONS')).status,204);
assert.equal((await call('PUT',{revision:0,iv:'bad',ciphertext:'bad'})).status,400);
const valid={revision:0,iv:randomBytes(12).toString('base64'),ciphertext:randomBytes(48).toString('base64')};
assert.equal((await call('PUT',valid)).status,200);
assert.equal((await call('PUT',valid)).status,409);
const before=await (await call('GET')).json();assert.equal(before.revision,1);assert.equal(before.ciphertext,valid.ciphertext);
assert.equal((await call('PUT',{...valid,revision:1})).status,200);
const after=await (await call('GET')).json();assert.equal(after.revision,2);
const backup=db.prepare('SELECT previous_ciphertext FROM study_states').get();assert.equal(backup.previous_ciphertext,valid.ciphertext);
assert.equal((await call('GET')).headers.get('Access-Control-Allow-Origin'),'https://hogomex393-svg.github.io');
console.log('PASS: authorization, CORS, encrypted payloads, optimistic concurrency and previous-state backup.');
