
const keywords = {
  Energy:["energy","oil","gas","nuclear","solar","electricity","grid","renewable","pipeline"],
  Technology:["technology","semiconductor","artificial intelligence","cybersecurity","software","broadband","data center","telecommunications"],
  Healthcare:["health","medical","medicare","medicaid","hospital","pharmaceutical","patient"],
  Financials:["bank","finance","credit","insurance","securities","tax","investment"],
  Defense:["defense","military","veteran","aerospace","armed forces"],
  Infrastructure:["infrastructure","bridge","transportation","highway","construction","housing","water"],
  Agriculture:["agriculture","farm","food","crop","livestock","rural"],
  Trade:["trade","tariff","export","import","customs","commerce"]
};
export const TOPICS = Object.keys(keywords);
export const classify = value => {
  const s = (" " + String(value || "").toLowerCase() + " ").replace(/[^a-z0-9]+/g, " ");
  return TOPICS.filter(t => keywords[t].some(w => s.includes(" " + w + " ")));
};
export function decodeXml(s) {
  return String(s||"").replace(/<!\[CDATA\[([\s\S]*?)\]\]>/g,"$1")
   .replace(/&#x([0-9a-f]+);/gi,(_,n)=>String.fromCodePoint(parseInt(n,16)))
   .replace(/&#([0-9]+);/g,(_,n)=>String.fromCodePoint(parseInt(n,10)))
   .replace(/&(?:amp|lt|gt|quot|apos|nbsp);/g,m=>({"&amp;":"&","&lt;":"<","&gt;":">","&quot;":'"',"&apos;":"'","&nbsp;":" "})[m]);
}
function tag(item, name) {
  const m = new RegExp("<"+name+"(?:\\s[^>]*)?>([\\s\\S]*?)<\\/"+name+">","i").exec(item);
  return m ? decodeXml(m[1]).replace(/<[^>]*>/g," ").replace(/\s+/g," ").trim() : "";
}
export function parseRss(xml) {
  if(!/<rss\b/i.test(String(xml))) throw Error("Invalid GovInfo RSS");
  return (xml.match(/<item\b[^>]*>[\s\S]*?<\/item>/gi)||[]).slice(0,100).map((item,i)=>{
    const title=tag(item,"title").slice(0,500), url=tag(item,"link"), summary=tag(item,"description").slice(0,900);
    if(!title || !/^https:\/\/(www\.)?govinfo\.gov\//i.test(url)) return null;
    const time=Date.parse(tag(item,"pubDate"));
    return {id:"bill-"+i+"-"+title.slice(0,20).replace(/\W/g,"-"),type:"bill",title,url,summary,source:"GovInfo",date:Number.isFinite(time)?new Date(time).toISOString().slice(0,10):null,topics:classify(title+" "+summary)};
  }).filter(Boolean);
}
export function parseRegister(data) {
  if(!Array.isArray(data?.results)) throw Error("Invalid Federal Register API");
  return data.results.slice(0,100).map(x=>{
    if(typeof x?.title!=="string" || !/^https:\/\/www\.federalregister\.gov\//.test(x.html_url||"")) return null;
    const agency=(x.agencies||[]).map(a=>a.name).filter(Boolean).join(", ");
    const summary=String(x.abstract||x.action||agency).replace(/<[^>]*>/g," ").slice(0,900);
    return {id:"reg-"+String(x.document_number||"").slice(0,50),type:x.type==="Rule"?"rule":x.type==="Proposed Rule"?"proposed":"notice",title:x.title.slice(0,500),url:x.html_url,summary,agency,source:"Federal Register",date:/^\d{4}-\d\d-\d\d$/.test(x.publication_date||"")?x.publication_date:null,topics:classify(x.title+" "+summary)};
  }).filter(Boolean);
}
