/* Funções puras compartilhadas pelo painel e testes Node. Sem dependências. */
(function(root){
'use strict';
const metrics=['internacoes','espera_validas','espera_soma_h','ate24_n','permanencia_validas','permanencia_soma_d'];
function empty(){return Object.fromEntries(metrics.map(k=>[k,0]));}
function add(a,r){for(const k of metrics)a[k]+=Number(r[k]||0);return a;}
function finish(a){return {...a,espera_media_h:a.espera_validas?a.espera_soma_h/a.espera_validas:null,ate24_pct:a.espera_validas?100*a.ate24_n/a.espera_validas:null,permanencia_media_d:a.permanencia_validas?a.permanencia_soma_d/a.permanencia_validas:null};}
function normal(s){return String(s??'').normalize('NFD').replace(/[\u0300-\u036f]/g,'').toLowerCase();}
function code(s){const m=String(s).match(/^(\d{10}|\d{2}\.\d{2}\.\d{2}\.\d{3}-\d)/);return m?m[1].replace(/\D/g,''):'';}
function matches(r,q){if(q.inicio&&r.mes<q.inicio)return false;if(q.fim&&r.mes>q.fim)return false;
 for(const [k,vals] of Object.entries(q.filtros||{})){if(!vals.length)continue;const v=k==='codigo_procedimento'?code(r.procedimento):r[k];if(!vals.includes(v))return false;}
 if(q.busca&&!normal((r.procedimento||'')+' '+(r.diagnostico||'')).includes(normal(q.busca))){if(!/^[\d.\-\s]+$/.test(q.busca)||!code(r.procedimento).includes(q.busca.replace(/\D/g,'')))return false;}return true;}
function query(rows,q){const dims=q.agrupar||['macro_destino'],groups=new Map(),series=new Map(),total=empty();
 for(const r of rows){if(!matches(r,q))continue;add(total,r);series.set(r.mes,(series.get(r.mes)||0)+r.internacoes);
  const key=JSON.stringify(dims.map(d=>r[d]));if(!groups.has(key))groups.set(key,{...Object.fromEntries(dims.map(d=>[d,r[d]])),...empty()});add(groups.get(key),r);}
 const all=Array.from(groups.values(),finish);const metric=q.indicador||'internacoes';all.sort((a,b)=>(b[metric]??-Infinity)-(a[metric]??-Infinity));
 const limit=q.limite??2000;return {dimensoes:dims,indicador:metric,total:finish(total),linhas:limit?all.slice(0,limit):all,grupos:all.length,truncado:!!limit&&all.length>limit,serie:Array.from(series,([mes,internacoes])=>({mes,internacoes})).sort((a,b)=>a.mes.localeCompare(b.mes)),modo:'publico'};}
function months(a,b){const out=[];if(!a||!b||a>b)return out;let [y,m]=a.split('-').map(Number);while(`${y}-${String(m).padStart(2,'0')}`<=b){out.push(`${y}-${String(m).padStart(2,'0')}`);if(++m>12){y++;m=1;}}return out;}
function previous(q){const shift=s=>`${Number(s.slice(0,4))-1}${s.slice(4)}`;return {...q,inicio:shift(q.inicio),fim:shift(q.fim)};}
function csv(rows,fields){const cell=v=>{let s=v==null?'':String(v);if(/^[=+\-@]/.test(s))s="'"+s;return '"'+s.replace(/"/g,'""')+'"';};return '\ufeff'+[fields.map(cell).join(';'),...rows.map(r=>fields.map(f=>cell(r[f])).join(';'))].join('\r\n');}
const api={query,matches,normal,code,months,previous,csv};root.ObservatorioCore=api;if(typeof module!=='undefined')module.exports=api;
})(globalThis);
