"""Valida o esquema público antes da publicação; não é prova de anonimização."""
import json
from pathlib import Path
root=Path(__file__).resolve().parents[1]
pasta=root/'painel';data=pasta/'data'
manifest=json.loads((data/'manifest.json').read_text(encoding='utf-8'))
permitidas=['mes','macro_destino','micro_destino','municipio_destino','procedimento','internacoes','espera_validas','espera_soma_h','ate24_n','permanencia_validas','permanencia_soma_d']
assert manifest['colunas']==permitidas,'Colunas não autorizadas no pacote público'
assert manifest['minimo_celula']>=5
esperados={'manifest.json'}
for part in manifest['particoes']:
 nome=part['arquivo'];assert Path(nome).name==nome
 esperados.add(nome)
 rows=json.loads((data/nome).read_text(encoding='utf-8'));assert len(rows)==part['celulas']
 for row in rows:
  assert len(row)==len(permitidas);r=dict(zip(permitidas,row))
  assert r['mes']==part['mes'];assert r['internacoes']>=manifest['minimo_celula']
  assert r['espera_validas']==0 or r['espera_validas']>=manifest['minimo_celula']
  assert r['permanencia_validas']==0 or r['permanencia_validas']>=manifest['minimo_celula']
  assert 0<=r['ate24_n']<=r['espera_validas']<=r['internacoes']
assert {f.name for f in data.iterdir() if f.is_file()}==esperados
for f in pasta.rglob('*'):
 if f.is_file():assert f.suffix.lower() in ('.html','.js','.css','.json') or f.name=='.nojekyll',f'Arquivo inesperado: {f}'
print('Esquema e limiar do pacote público validados.')
