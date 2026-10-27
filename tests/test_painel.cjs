const assert=require('node:assert/strict');
const C=require('../painel/core.js');
const rows=[{mes:'2025-01',ano:'2025',macro_destino:'A',procedimento:'0303040149-AVC',internacoes:10,espera_validas:10,espera_soma_h:100,ate24_n:9,permanencia_validas:10,permanencia_soma_d:20},
 {mes:'2025-02',ano:'2025',macro_destino:'A',procedimento:'0303040149-AVC',internacoes:20,espera_validas:20,espera_soma_h:800,ate24_n:5,permanencia_validas:20,permanencia_soma_d:100}];
let r=C.query(rows,{agrupar:['macro_destino'],indicador:'espera_media_h',limite:0});
assert.equal(r.total.internacoes,30);assert.equal(r.total.espera_media_h,30);assert.equal(r.total.ate24_pct,100*14/30);
assert.equal(r.linhas[0].permanencia_media_d,4); // média ponderada, não média das médias
r=C.query(rows,{inicio:'2025-02',fim:'2025-02',agrupar:['mes'],filtros:{codigo_procedimento:['0303040149']}});
assert.equal(r.total.internacoes,20);
r=C.query(rows,{agrupar:['mes'],filtros:{macro_destino:['B']}});assert.equal(r.total.internacoes,0);assert.equal(r.total.espera_media_h,null);
assert.deepEqual(C.months('2025-12','2026-02'),['2025-12','2026-01','2026-02']);
assert.equal(C.previous({inicio:'2026-01',fim:'2026-04'}).inicio,'2025-01');
assert.ok(C.csv([{x:'=1+1'}],['x']).includes("'=1+1"));
console.log('Testes do painel: filtros, médias ponderadas, denominadores, períodos e exportação OK.');
