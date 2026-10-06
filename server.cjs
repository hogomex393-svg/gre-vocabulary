const http = require('node:http');
const fs = require('node:fs');
const path = require('node:path');
const root = __dirname, port = Number(process.env.GRE_PORT || 18765);
const saveDir=process.env.GRE_SAVE_DIR || path.join(root,'存档'); fs.mkdirSync(saveDir,{recursive:true});
const saveFile=path.join(saveDir,'学习进度.json');
const send=(res,code,data,type='application/json; charset=utf-8')=>{res.writeHead(code,{'Content-Type':type,'Cache-Control':'no-store','X-Content-Type-Options':'nosniff'});res.end(type.startsWith('application/json')?JSON.stringify(data):data)};
function readState(){if(!fs.existsSync(saveFile))return null; return JSON.parse(fs.readFileSync(saveFile,'utf8'));}
function valid(s){return s && s.version===1 && Number.isInteger(s.activeDay) && s.activeDay>=0 && s.activeDay<500 && typeof s.days==='object' && !Array.isArray(s.days) && typeof s.updated==='number';}
const mime={'.html':'text/html; charset=utf-8','.css':'text/css; charset=utf-8','.js':'text/javascript; charset=utf-8','.json':'application/json; charset=utf-8','.png':'image/png','.svg':'image/svg+xml','.pdf':'application/pdf'};
http.createServer(async(req,res)=>{
 try{
 const url=new URL(req.url,'http://localhost');
 if(url.pathname==='/api/health')return send(res,200,{app:'gre-study',version:1});
 if(url.pathname==='/api/state' && req.method==='GET')return send(res,200,{state:readState()});
 if(url.pathname==='/api/state' && req.method==='PUT'){
   if(req.headers.origin && ![`http://localhost:${port}`,`http://127.0.0.1:${port}`].includes(req.headers.origin))return send(res,403,{error:'来源不允许'});
   let body='';for await(const c of req){body+=c;if(body.length>8e6)return send(res,413,{error:'存档过大'});}
   const data=JSON.parse(body);if(!valid(data.state))return send(res,400,{error:'无效存档'});
   const prev=readState();if((prev?.revision||0)!==data.revision)return send(res,409,{error:'另一个页面更新了进度，请刷新后继续'});
   const state={...data.state,revision:(prev?.revision||0)+1};
   if(prev){fs.copyFileSync(saveFile,path.join(saveDir,'上一次进度.json'));const day=new Date().toLocaleDateString('en-CA',{timeZone:'Asia/Shanghai'}).replaceAll('/','-');const backup=path.join(saveDir,`备份-${day}.json`);if(!fs.existsSync(backup))fs.copyFileSync(saveFile,backup);}
   const temp=saveFile+'.tmp';fs.writeFileSync(temp,JSON.stringify(state,null,2));fs.renameSync(temp,saveFile);
   return send(res,200,{revision:state.revision});
 }
 if(req.method!=='GET')return send(res,405,{error:'方法不允许'});
 let target;
 if(url.pathname.startsWith('/source-image/')){const name=decodeURIComponent(url.pathname.slice(14));if(!/^(precise|rare|pairs)-\d+\.png$/.test(name))return send(res,404,{});target=path.join(root,'sources',name);}
 else if(url.pathname.startsWith('/book/')){
   const names={'full':'青山学堂GRE全能词.pdf','precise':'青山学堂GRE词表-精准释义V1.0.pdf','rare':'青山学堂GRE词表-熟词僻义V1.0.pdf','pairs':'青山学堂GRE词表-等价词对V2.0.pdf','zhen':'真经GRE等价词汇总.pdf'};const name=names[url.pathname.slice(6)];if(!name)return send(res,404,{});target=path.join(root,'资料原件',name);
 }else {target=path.resolve(root,'dist','.'+decodeURIComponent(url.pathname==='/'?'/index.html':url.pathname));if(!target.startsWith(path.resolve(root,'dist')+path.sep))return send(res,403,{});}
 if(!fs.existsSync(target)||!fs.statSync(target).isFile())return send(res,404,{error:'文件不存在'});
 res.writeHead(200,{'Content-Type':mime[path.extname(target)]||'application/octet-stream','Cache-Control':'no-cache'});fs.createReadStream(target).pipe(res);
 }catch(e){console.error(e.message);send(res,500,{error:'读取或保存失败，请保留当前页面并导出存档'});}
}).listen(port,'127.0.0.1',()=>console.log(`GRE website: http://localhost:${port}`));
