
const el = id => document.getElementById(id);
const TOPICS=["Energy","Technology","Healthcare","Financials","Defense","Infrastructure","Agriculture","Trade"];
const LABELS={overview:"OVERVIEW",feed:"LEGISLATIVE FEED",regulations:"REGULATORY WATCH",watchlist:"MY WATCHLIST",sources:"SOURCES"};
const state={items:[],sources:[],loaded:false,watch:readWatch(),view:"overview",status:"connecting",fetchedAt:null};
function readWatch(){try{const x=JSON.parse(localStorage.getItem("legaledge-watchlist-v2")||"[]");return Array.isArray(x)?x.filter(z=>z&&typeof z.symbol==="string"&&TOPICS.includes(z.sector)).slice(0,100):[];}catch{return[];}}
function saveWatch(){try{localStorage.setItem("legaledge-watchlist-v2",JSON.stringify(state.watch));}catch{alert("Could not save watchlist in this browser.");}}
function node(type,cls,text){const n=document.createElement(type);if(cls)n.className=cls;if(text!==undefined)n.textContent=String(text);return n;}
function showEmpty(parent,text){parent.replaceChildren(node("div","empty",text));}
function dateLabel(date){if(!date)return "Date unavailable";const d=new Date(date+"T12:00:00Z");return Number.isFinite(d.getTime())?new Intl.DateTimeFormat("en-US",{month:"short",day:"numeric",year:"numeric",timeZone:"UTC"}).format(d):"Date unavailable";}
function safeLink(value){try{const u=new URL(value);return u.protocol==="https:"&&["www.govinfo.gov","govinfo.gov","www.federalregister.gov"].includes(u.hostname)?u.toString():null;}catch{return null;}}
function record(item){
  const wrap=node("article","record"),icon=node("span","record-icon"+(item.type==="bill"?"":" reg"),item.type==="bill"?"B":"R"),content=node("div","record-content"),meta=node("div","record-meta");
  meta.append(node("span","pill",item.type==="bill"?"BILL":item.type==="rule"?"FINAL RULE":item.type==="proposed"?"PROPOSED RULE":"NOTICE"),node("span","",item.source),node("span","","·"),node("span","",dateLabel(item.date)));
  const href=safeLink(item.url),title=node(href?"a":"span","record-title",item.title);
  if(href){title.href=href;title.target="_blank";title.rel="noopener noreferrer";}
  content.append(meta,title);
  if(item.summary)content.append(node("p","record-description",item.summary));
  if(item.topics?.length){const topics=node("div","");item.topics.slice(0,3).forEach(t=>topics.append(node("span","chip",t+"  ")));content.append(topics);}
  wrap.append(icon,content,node("span","record-arrow","↗"));return wrap;
}
function renderList(id,items,limit){
  const target=el(id);target.replaceChildren();
  if(!items.length){showEmpty(target,state.loaded?"No matching records are available from the current source window.":"Loading official-source records…");return;}
  items.slice(0,limit).forEach(item=>target.append(record(item)));
}
function filtered(kind){
  const query=(el(kind==="bill"?"bill-search":"reg-search").value||"").trim().toLowerCase();
  const sector=el("bill-sector").value;
  const type=el("reg-type").value;
  return state.items.filter(item=>{
    if(kind==="bill" && item.type!=="bill")return false;
    if(kind==="reg" && item.type==="bill")return false;
    if(kind==="bill"&&sector!=="all"&&!item.topics?.includes(sector))return false;
    if(kind==="reg"&&type!=="all"&&item.type!==type)return false;
    return !query||[item.title,item.summary,item.agency,(item.topics||[]).join(" ")].join(" ").toLowerCase().includes(query);
  });
}
function renderCounts(){
  const total=state.items.length,bills=state.items.filter(x=>x.type==="bill").length,regs=total-bills,topics=state.items.filter(x=>x.topics?.length>0).length;
  [["metric-total",total],["metric-bills",bills],["metric-regs",regs],["metric-topics",topics]].forEach(([id,val])=>el(id).textContent=state.loaded?val.toLocaleString("en-US"):"—");
  if(state.fetchedAt)el("sync-time").textContent="Source check · "+new Date(state.fetchedAt).toLocaleString();
  renderList("overview-feed",state.items,5);
  const bars=el("topic-bars");bars.replaceChildren();const counts=TOPICS.map(t=>({topic:t,count:state.items.filter(i=>i.topics?.includes(t)).length})).sort((a,b)=>b.count-a.count);
  const max=Math.max(...counts.map(c=>c.count),1);
  counts.slice(0,7).forEach(({topic,count})=>{
    const outer=node("div","topic-row"),label=node("div",""),track=node("div","track"),fill=node("div","fill");
    label.append(node("span","",topic),node("span","",count));fill.style.width=(100*count/max)+"%";track.append(fill);outer.append(label,track);bars.append(outer);
  });
  if(!state.loaded)bars.append(node("p","empty","Awaiting source data…"));
}
function renderFeeds(){
  const bills=filtered("bill"),regs=filtered("reg");
  el("bill-count").textContent=bills.length+" records";el("reg-count").textContent=regs.length+" records";
  renderList("bill-list",bills,100);renderList("reg-list",regs,100);
}
function matching(holding){
  const word=holding.symbol.toLowerCase();
  return state.items.filter(x=>x.topics?.includes(holding.sector)||(word.length>=3&&new RegExp("(^|[^a-z0-9])"+word.replace(/[^a-z0-9]/g,"")+"([^a-z0-9]|$)","i").test(x.title+" "+x.summary)));
}
function renderWatch(){
  el("watch-count").textContent=state.watch.length;const target=el("watch-items");target.replaceChildren();
  if(!state.watch.length){showEmpty(target,"Your research watchlist is empty. Add a ticker or company label and its sector above.");return;}
  state.watch.forEach((w,i)=>{
    const card=node("div","watch-card"),head=node("header",""),name=node("strong","",w.symbol),remove=node("button","remove","Remove");
    remove.type="button";remove.addEventListener("click",()=>{state.watch.splice(i,1);saveWatch();renderWatch();});
    head.append(name,remove);card.append(head,node("div","chip",w.sector));
    const matches=matching(w);card.append(node("p","",matches.length+" recent record"+(matches.length===1?"":"s")+" with sector or symbol keyword overlap."));
    if(matches.length){const first=matches[0],href=safeLink(first.url),link=node("a","record-title",first.title);if(href){link.href=href;link.target="_blank";link.rel="noopener noreferrer";}card.append(link);}
    target.append(card);
  });
}
function renderSources(){
  const holder=el("source-cards");holder.replaceChildren();
  const defs=[
    {id:"bills",name:"GovInfo",description:"The U.S. Government Publishing Office's Congressional Bills RSS feed.",url:"https://www.govinfo.gov/feeds"},
    {id:"regulations",name:"Federal Register",description:"The Office of the Federal Register's keyless public documents API.",url:"https://www.federalregister.gov/developers/documentation/api/v1"}
  ];
  defs.forEach(def=>{
    const s=state.sources.find(x=>x.id===def.id),box=node("article","source-card");
    box.append(node("span","source-status"+(s&&!s.ok?" bad":""),s?(s.ok?"● Connected · "+s.count+" records":"● Temporarily unavailable"):"● Not checked"));
    box.append(node("h3","",def.name),node("p","",def.description));
    const a=node("a","","View official source ↗");a.href=def.url;a.target="_blank";a.rel="noopener noreferrer";box.append(a);holder.append(box);
  });
}
function setView(view){if(!LABELS[view])return;state.view=view;
  document.querySelectorAll("[data-panel]").forEach(n=>n.classList.toggle("hide",n.dataset.panel!==view));
  document.querySelectorAll(".nav-item").forEach(n=>n.classList.toggle("selected",n.dataset.view===view));
  el("breadcrumb").textContent=LABELS[view];history.replaceState(null,"","#"+view);window.scrollTo({top:0,behavior:"instant"});
}
function statusText(text,warning){const target=el("connection");target.replaceChildren(node("span","dot"),document.createTextNode(text));target.classList.toggle("warning",warning);}
async function loadFeed(){
  statusText("Checking sources…",false);
  try{
    const response=await fetch("/api/feed",{headers:{accept:"application/json"}}),data=await response.json();
    if(!data||!Array.isArray(data.items)||!Array.isArray(data.sources))throw Error("Invalid feed response");
    state.items=data.items;state.sources=data.sources;state.loaded=true;state.status=data.status;state.fetchedAt=data.fetchedAt;
    statusText(data.status==="live"?"Live sources":data.status==="partial"?"Partial coverage":"Sources unavailable",data.status!=="live");
  }catch{
    state.items=[];state.sources=[];state.loaded=true;state.fetchedAt=null;state.status="unavailable";
    statusText("Sources unavailable",true);
  }
  renderCounts();renderFeeds();renderWatch();renderSources();
  const previous=el("network-banner");if(previous)previous.remove();
  if(state.status!=="live"){
    const div=node("div","banner","Source coverage is "+state.status+". Missing feeds are not replaced with simulated records. Retry later or open the publisher websites.");
    div.id="network-banner";document.querySelector('[data-panel="overview"]').prepend(div);
  }
}
function exportCsv(){
  const rows=filtered("bill"),columns=["date","type","title","summary","topics","source","url"];
  const escape=value=>'"'+String(value??"").replace(/^[=+\-@\t\r]/,"'$&").replaceAll('"','""')+'"';
  const csv=[columns.join(","),...rows.map(x=>columns.map(k=>escape(k==="topics"?(x.topics||[]).join("; "):x[k])).join(","))].join("\r\n");
  const blob=new Blob([csv],{type:"text/csv;charset=utf-8"}),url=URL.createObjectURL(blob),a=node("a");
  a.href=url;a.download="legaledge-legislation.csv";a.click();setTimeout(()=>URL.revokeObjectURL(url),500);
}
TOPICS.forEach(topic=>{for(const id of ["bill-sector","watch-sector"]){const opt=node("option","",topic);opt.value=topic;el(id).append(opt);}});
document.querySelectorAll("[data-view]").forEach(button=>button.addEventListener("click",()=>setView(button.dataset.view)));
["bill-search","bill-sector","reg-search","reg-type"].forEach(id=>el(id).addEventListener(id.includes("search")?"input":"change",renderFeeds));
el("watch-form").addEventListener("submit",e=>{
  e.preventDefault();const symbol=el("watch-symbol").value.trim().toUpperCase().replace(/[^A-Z0-9 ._-]/g,"").slice(0,30),sector=el("watch-sector").value;
  if(!symbol||!TOPICS.includes(sector)||state.watch.length>=100)return;
  if(state.watch.some(w=>w.symbol===symbol&&w.sector===sector))return;
  state.watch.push({symbol,sector});saveWatch();renderWatch();el("watch-symbol").value="";
});
el("refresh").addEventListener("click",loadFeed);el("export").addEventListener("click",exportCsv);
el("today").textContent=new Intl.DateTimeFormat("en-US",{month:"long",day:"numeric",year:"numeric"}).format(new Date()).toUpperCase();
setView(location.hash.slice(1)||"overview");renderWatch();renderSources();renderCounts();loadFeed();
