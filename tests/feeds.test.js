
import test from "node:test";
import assert from "node:assert/strict";
import {classify,decodeXml,parseRss,parseRegister} from "../src/feeds.js";
test("topics match words and not arbitrary substrings",()=>{
 assert.deepEqual(classify("Federal nuclear energy tax credits"),["Energy","Financials"]);
 assert.deepEqual(classify("Unrelated proposal"),[]);
});
test("XML is decoded and only government document links accepted",()=>{
 const xml='<rss><channel><item><title>Solar &amp; nuclear act</title><link>https://www.govinfo.gov/app/details/BILLS-119hr9ih</link><pubDate>Fri, 16 Oct 2026 01:00:00 GMT</pubDate><description><![CDATA[Energy measures]]></description></item><item><title>Bad</title><link>https://bad.example/x</link></item></channel></rss>';
 const rows=parseRss(xml);
 assert.equal(rows.length,1);
 assert.equal(rows[0].title,"Solar & nuclear act");
 assert.equal(rows[0].date,"2026-10-16");
 assert.ok(rows[0].topics.includes("Energy"));
 assert.equal(decodeXml("&lt;ok&gt;"),"<ok>");
});
test("Federal Register rows are normalized and bad links dropped",()=>{
 const rows=parseRegister({results:[{document_number:"2026-111",type:"Rule",title:"Cybersecurity standards",html_url:"https://www.federalregister.gov/documents/1",publication_date:"2026-10-15",agencies:[{name:"Department of Commerce"}]}, {title:"Injected",html_url:"javascript:alert(1)"}]});
 assert.equal(rows.length,1);assert.equal(rows[0].type,"rule");assert.ok(rows[0].topics.includes("Technology"));
});
test("malformed feeds fail clearly",()=>{assert.throws(()=>parseRss("oops"));assert.throws(()=>parseRegister({}));});
