/* Seletores de procedimentos e diagnósticos com revisão de correspondências. */
function createCatalogPicker({prefix,labels,kind,selected,onChange}){
 const codeFn=kind==='diagnostico'?BuscaListas.cidCode:BuscaListas.procCode;
 const map=new Map();for(const label of labels){const code=codeFn(label),key=code||label;if(!map.has(key))map.set(key,{key,code,label,labels:[]});map.get(key).labels.push(label);}
 const catalog=Array.from(map.values()).sort((a,b)=>a.label.localeCompare(b.label,'pt-BR'));
 const get=id=>document.getElementById(prefix+'-'+id),node=(tag,text,cls)=>{const e=document.createElement(tag);if(text!==undefined)e.textContent=text;if(cls)e.className=cls;return e;};
 function search(){return BuscaListas.analyze(get('search').value,catalog,kind);}
 function render(){const result=search();get('choices').replaceChildren();for(const p of result.items){const label=node('label',undefined,'procedure-option'),input=node('input');input.type='checkbox';input.value=p.key;input.checked=selected.has(p.key);input.onchange=()=>{if(input.checked)selected.add(p.key);else selected.delete(p.key);render();onChange();};label.append(input,node('span',p.label));get('choices').append(label);}
 if(!result.items.length)get('choices').append(node('p',result.error||'Nenhuma correspondência. Confira o texto ou tente outro termo.','hint'));
 get('count').textContent=(selected.size?`${selected.size} selecionado(s) de ${catalog.length}`:`Sem filtro: todos os ${catalog.length} itens disponíveis`)+` · ${result.items.length} encontrado(s)`;
 get('report').replaceChildren();if(result.error)get('report').append(node('p',result.error,'unmatched'));
 if(result.terms.length){const d=node('details'),s=node('summary',`Conferir ${result.terms.length} termo(s) · ${result.unmatched.length} sem correspondência`);d.append(s);const ul=node('ul');for(const t of result.terms)ul.append(node('li',`${t.label}: ${t.count} correspondência(s)`,t.count?'':'unmatched'));d.append(ul);get('report').append(d);if(result.unmatched.length)get('report').append(node('p','Sem correspondência: '+result.unmatched.join('; '),'unmatched'));}
 get('selected').replaceChildren(...catalog.filter(p=>selected.has(p.key)).map(p=>{const b=node('button',p.label+' ×','procedure-chip');b.title='Desmarcar '+p.label;b.onclick=()=>{selected.delete(p.key);render();onChange();};return b;}));
 }
 get('search').oninput=render;
 get('mark-all').onclick=()=>{const result=search();if(result.error)return;for(const p of result.items)selected.add(p.key);render();onChange();get('status').textContent=`${result.items.length} resultado(s) marcado(s). Confira a lista antes de aplicar a consulta.`;};
 get('clear').onclick=()=>{selected.clear();get('search').value='';get('status').textContent='Seleção limpa. Sem seleção específica, todos os itens entram na consulta.';render();onChange();};
 get('find').onclick=()=>{const result=search();if(result.error){get('status').textContent=result.error;return;}if(!result.items.length){get('status').textContent='Nada foi marcado. A seleção anterior foi preservada.';render();return;}if(!get('append').checked)selected.clear();for(const p of result.items)selected.add(p.key);render();onChange();get('status').textContent=`${result.items.length} item(ns) encontrado(s) e marcado(s). Confira e ajuste os cliques antes de aplicar. ${result.unmatched.length} termo(s) sem correspondência.`;};
 render();return {catalog,render,search,key:label=>codeFn(label)||label,chosenLabels:()=>catalog.filter(p=>selected.has(p.key)).flatMap(p=>p.labels)};
}
