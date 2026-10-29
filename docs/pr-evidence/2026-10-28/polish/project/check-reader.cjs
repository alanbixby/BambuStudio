// Exact reader JS executed in Node vm. DOM/jQuery, native scheduling and HTTP are doubles.
// No native engine, layout, network, actual threads or GUI is exercised.
const fs=require('node:fs'),vm=require('node:vm'),assert=require('node:assert/strict');
const root=__dirname+'/sources/';
const reader=fs.readFileSync(root+'p3__resources__web__model_new__index.js','utf8');
const cpp=fs.readFileSync(process.argv[2] || root+'candidate-Project.cpp','utf8');
const statement=cpp.slice(cpp.indexOf('const std::string script = "(function(){"'),cpp.indexOf('RunScript(script);',cpp.indexOf('const std::string script = "(function(){"')));
const literalized=statement.replace('json(id).dump()',JSON.stringify(JSON.stringify('123')));
const script=[...literalized.matchAll(/"(?:\\.|[^"\\])*"/g)].map(x=>JSON.parse(x[0])).join('');
fs.writeFileSync(__dirname+'/extracted-model-link.js',script+'\n');
function fixture(){
 let ready,domReady=false,time=0,next=1,requests=0;const timers=new Map(),elements=new Map();
 function element(id){if(!elements.has(id))elements.set(id,{text:'',html:'',classes:new Set()});return elements.get(id);}
 function $(arg){if(typeof arg==='function'){ready=arg;return;}const e=element(arg);const q={text(v){e.text=v;return q},html(v){e.html=v;return q},hide(){return q},show(){return q},css(){return q},bsGallery(){return q},hasClass(c){return e.classes.has(c)},addClass(c){e.classes.add(c);return q},removeClass(c){e.classes.delete(c);return q}};return q;}
 const ctx={$ ,console,TranslatePage(){},DecodeDescriptionFrom3MF:v=>v,DOMPurify:{sanitize:v=>v},SendWXMessage(){requests++},setTimeout(fn,delay){let id=next++;timers.set(id,{at:time+delay,fn});return id},clearTimeout(id){timers.delete(id)},document:{getElementById(id){if(!domReady)return null;const e=element('#'+id);return {classList:{toggle(c,on){on?e.classes.add(c):e.classes.delete(c)}}}}}};ctx.window=ctx;ctx.location={href:'index.html'};vm.createContext(ctx);vm.runInContext(reader,ctx);
 return {ctx,element,ready(){domReady=true;ready()},runLink(){vm.runInContext(script,ctx)},drain(){while(timers.size){let [id,t]=[...timers].sort((a,b)=>a[1].at-b[1].at)[0];timers.delete(id);time=t.at;t.fn();}},requests:()=>requests,time:()=>time,addBridge(){ctx.wx={postMessage(){}}}};
}
function payload(id=''){return {command:'show_3mf_info',model:{model:{name:'Name',author:'Author',description:'Description',model_id:id,license:'CC',upload_type:'original',preview_img:[]},profile:{name:'',author:'',description:'',preview_img:[]},file:{BOM:[],Assembly:[],Other:[]}}};}
const results=[];
function test(name,fn){fn();results.push({name,status:'PASS'});}
test('resolved link survives metadata replay before DOM ready',()=>{const f=fixture();f.addBridge();f.ctx.HandleStudio(payload());f.runLink();f.ready();f.drain();assert.equal(f.ctx.m_ModelID,'123');assert.ok(f.element('#projectName').classes.has('link'));assert.equal(f.requests(),0);});
test('DOM-ready-first update still adds the link',()=>{const f=fixture();f.ready();f.ctx.HandleStudio(payload());f.runLink();assert.equal(f.ctx.m_ModelID,'123');assert.ok(f.element('#projectName').classes.has('link'));});
test('early resolved ID replaces an older cached ID',()=>{const f=fixture();f.ctx.HandleStudio(payload('456'));f.runLink();f.ready();assert.equal(f.ctx.m_ModelID,'123');});
test('clear buffer is not converted into metadata',()=>{const f=fixture();f.ctx.HandleStudio({command:'clear_3mf_info'});f.runLink();assert.equal(f.ctx.pendingProjectMessage.command,'clear_3mf_info');assert.equal(f.ctx.pendingProjectMessage.model,undefined);f.ready();assert.equal(f.element('#projectDescription').html,'');});
test('no buffer after readiness: ordinary targeted update works',()=>{const f=fixture();f.ready();f.runLink();assert.equal(f.ctx.pendingProjectMessage,null);assert.equal(f.ctx.m_ModelID,'123');});
test('missing nested metadata is ignored safely',()=>{const f=fixture();f.ctx.pendingProjectMessage={command:'show_3mf_info',model:null};assert.doesNotThrow(()=>f.runLink());assert.equal(f.ctx.pendingProjectMessage.model,null);});
test('failed lookup leaves the local metadata available without a link',()=>{const f=fixture();f.ctx.HandleStudio(payload());f.ready();assert.equal(f.element('#projectName').text,'Name');assert.equal(f.ctx.m_ModelID,'');assert.ok(!f.element('#projectName').classes.has('link'));});
test('new document does not inherit another document model ID',()=>{const first=fixture();first.ctx.HandleStudio(payload());first.runLink();first.ready();const next=fixture();next.ctx.HandleStudio(payload('789'));next.ready();assert.equal(next.ctx.m_ModelID,'789');assert.equal(first.ctx.m_ModelID,'123');});
test('latest buffered metadata still wins',()=>{const f=fixture();const old=payload();old.model.model.name='Old';const latest=payload();latest.model.model.name='Latest';f.ctx.HandleStudio(old);f.ctx.HandleStudio(latest);f.runLink();f.ready();assert.equal(f.element('#projectName').text,'Latest');assert.equal(f.ctx.m_ModelID,'123');});
test('missing pending global is safe',()=>{const c={m_ModelID:null,document:{getElementById(){return null;}}};vm.createContext(c);assert.doesNotThrow(()=>vm.runInContext(script,c));assert.equal(c.m_ModelID,'123');});
test('non-reader document is ignored',()=>{const c={document:{getElementById(){throw new Error('wrong document');}}};vm.createContext(c);assert.doesNotThrow(()=>vm.runInContext(script,c));assert.equal(c.m_ModelID,undefined);});
test('handshake remains bounded',()=>{const f=fixture();f.addBridge();f.ready();f.drain();assert.equal(f.requests(),8);assert.equal(f.time(),15850);});
test('absent bridge receives no requests',()=>{const f=fixture();f.ready();f.drain();assert.equal(f.requests(),0);});
test('late bridge during retry window is discovered',()=>{const f=fixture();f.ready();f.addBridge();f.drain();assert.equal(f.requests(),7);});
const crypto=require('node:crypto');const sha=s=>crypto.createHash('sha256').update(s).digest('hex');
fs.writeFileSync(__dirname+'/candidate-results.json',JSON.stringify({cpp_sha256:sha(cpp),reader_sha256:sha(reader),checks:results,limits:'Exact JS/native string literals; DOM, scheduler and HTTP success are doubles. No native backend timing, GUI, networking or real-thread teardown claim.'},null,2)+'\n');
console.log('PASS: '+results.length+' source-extracted reader scheduling checks');
