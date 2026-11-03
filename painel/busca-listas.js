/* Busca determinística em catálogos locais; nenhum texto colado sai do navegador. */
(function(root){'use strict';
const normalize=s=>String(s??'').normalize('NFD').replace(/[\u0300-\u036f]/g,'').toLowerCase();
const stop=new Set('de da do das dos em no na nos nas com para por ao a o as os e ou preciso precisa precisamos selecionar selecione procedimento procedimentos cid cids diagnostico diagnosticos exemplo etc'.split(' '));
const connectors=new Set('de da do das dos em com para por'.split(' '));
function procCode(s){return String(s).match(/\b(?:\d{2}\.\d{2}\.\d{2}\.\d{3}-\d|\d{10})\b/)?.[0].replace(/\D/g,'')||'';}
function cidCode(s){return String(s).toUpperCase().match(/\b[A-Z]\d{2}(?:\.?\d{1,2})?\b/)?.[0].replace('.','')||'';}
function words(s){return normalize(s).match(/[a-z0-9]+/g)||[];}
function textMatch(label,tokens){const text=normalize(label);return tokens.length>0&&tokens.every(t=>text.includes(t));}
function analyze(text,catalog,kind='procedimento'){
 text=String(text||'').trim();if(!text)return {items:catalog,terms:[],unmatched:[],error:null};
 if(text.length>50000)return {items:[],terms:[],unmatched:[],error:'A lista excede 50.000 caracteres. Divida o texto em partes.'};
 const codePattern=kind==='diagnostico'?/\b[A-Z]\d{2}(?:\.?\d{1,2})?\b/gi:/\b(?:\d{2}\.\d{2}\.\d{2}\.\d{3}-\d|\d{10})\b/g;
 const segments=text.split(/\r?\n/).flatMap(line=>{const codes=Array.from(line.matchAll(codePattern),m=>m[0]);return codes.length?codes:(line.match(/"[^"\n]+"|'[^'\n]+'|[^\n\r\t,;|]+/g)||[]);});
 const terms=[];
 for(let segment of segments){segment=segment.trim();if(!segment)continue;
  const quoted=/^["']/.test(segment);segment=segment.replace(/^["']|["']$/g,'').trim();
  const regex=kind==='diagnostico'?/\b[A-Z]\d{2}(?:\.?\d{1,2})?\b/gi:/\b(?:\d{2}\.\d{2}\.\d{2}\.\d{3}-\d|\d{10})\b/g;
  const codes=Array.from(segment.matchAll(regex),m=>({kind:'code',label:m[0],value:m[0].replace(/[^a-z0-9]/gi,'').toUpperCase()}));
  if(codes.length){terms.push(...codes);continue;}
  const allWords=words(segment),tokens=allWords.filter(t=>!stop.has(t));if(!tokens.length){terms.push({kind:'text',label:segment,tokens:[]});continue;}
  const expressionMatches=catalog.some(p=>textMatch(p.label,tokens));
  const separate=!quoted&&!expressionMatches&&!allWords.some(w=>connectors.has(w))&&tokens.length>1&&tokens.every(t=>catalog.some(p=>textMatch(p.label,[t])));
  if(separate)terms.push(...tokens.map(t=>({kind:'text',label:t,tokens:[t]})));else terms.push({kind:'text',label:segment,tokens});
 }
 if(terms.length>500)return {items:[],terms:[],unmatched:[],error:'Mais de 500 termos identificados. Divida a lista em partes.'};
 const unique=Array.from(new Map(terms.map(t=>[t.kind+':'+(t.value||t.tokens.join(' ')),t])).values());
 const keys=new Set();const results=unique.map(t=>{let count=0;for(const item of catalog){const ok=t.kind==='code'?(kind==='diagnostico'?item.code.startsWith(t.value):item.code===t.value):textMatch(item.label,t.tokens);if(ok){keys.add(item.key);count++;}}return {...t,count};});
 return {items:catalog.filter(p=>keys.has(p.key)),terms:results,unmatched:results.filter(t=>!t.count).map(t=>t.label),error:null};
}
const api={normalize,procCode,cidCode,analyze};root.BuscaListas=api;if(typeof module!=='undefined')module.exports=api;
})(globalThis);
