
import {parseRss,parseRegister,TOPICS} from "./feeds.js";
const catalog=[
  {id:"bills",name:"GovInfo",url:"https://www.govinfo.gov/rss/bills.xml"},
  {id:"regulations",name:"Federal Register",url:"https://www.federalregister.gov/api/v1/documents.json?per_page=75&order=newest"}
];
const reply=(obj,status=200,ttl=0)=>new Response(JSON.stringify(obj),{status,headers:{"content-type":"application/json; charset=utf-8","cache-control":ttl?"public, max-age="+ttl:"no-store","x-content-type-options":"nosniff"}});
async function getSource(source){
  const controller=new AbortController(), timer=setTimeout(()=>controller.abort(),9500);
  try {
    const result=await fetch(source.url,{signal:controller.signal,headers:{"accept":source.id==="bills"?"application/rss+xml":"application/json"}});
    if(!result.ok) throw Error("Source unavailable");
    const body=await result.text();
    if(body.length>2000000) throw Error("Response too large");
    const items=source.id==="bills"?parseRss(body):parseRegister(JSON.parse(body));
    return {id:source.id,name:source.name,ok:true,count:items.length,items};
  } catch {return {id:source.id,name:source.name,ok:false,count:0,items:[],error:"Source temporarily unavailable"};}
  finally {clearTimeout(timer);}
}
export default {
  async fetch(request){
    const url=new URL(request.url);
    if(request.method!=="GET")return reply({error:"Method not allowed"},405);
    if(url.pathname==="/api/health")return reply({status:"ok",service:"LegalEdge",version:"2.0",time:new Date().toISOString()});
    if(url.pathname==="/api/sources")return reply({sources:catalog,topics:TOPICS,storage:"Browser-local watchlist; no account registration"});
    if(url.pathname!=="/api/feed")return reply({error:"Not found"},404);
    const cache=typeof caches!=="undefined"?caches.default:null,cacheKey=new Request(url.origin+"/api/feed");
    if(cache){const hit=await cache.match(cacheKey);if(hit)return hit;}
    const all=await Promise.all(catalog.map(getSource)),working=all.filter(x=>x.ok).length;
    const data={status:working===2?"live":working===1?"partial":"unavailable",fetchedAt:new Date().toISOString(),items:all.flatMap(x=>x.items).sort((a,b)=>(b.date||"").localeCompare(a.date||"")).slice(0,175),sources:all.map(({id,name,ok,count,error})=>({id,name,ok,count,...(error?{error}:{})})),limitations:"Tags are keyword matches, not financial forecasts, legislative predictions or investment advice."};
    const response=reply(data,working?200:503,working===2?300:20);
    if(cache&&working===2){try{await cache.put(cacheKey,response.clone());}catch{}}
    return response;
  }
};
