#!/usr/bin/env python3
"""Observatório SUSfácilMG — agregação local sem exposição de dados pessoais.
Executar: python gerar_agregados_v2.py 'internações realizadas 2025-01(6).xlsx' --out dados_v2
Lê XLSX via XML em streaming (somente biblioteca padrão). Não publica nomes/CPF.
Saída local NÃO deve ser hospedada sem revisão de risco de reidentificação.
"""
import argparse,collections,json,re,zipfile,xml.etree.ElementTree as ET
from pathlib import Path
from datetime import datetime, timedelta
N='{http://schemas.openxmlformats.org/spreadsheetml/2006/main}'
CAMPOS=['Nº da Internação','Data da Solicitação','Data da Internação','Data da Alta','Município do Paciente','Município de Origem','Município de Destino','Estab. Origem','Estabelecimento de Destino','Procedimento','Diagnóstico','Internação Eletiva','Situação','Macro de Origem PDR data da extração','Macro de Destino PDR data da extração','Micro de Origem PDR data da extração','Micro de Destino PDR data da extração']
def excel_rows(path):
 with zipfile.ZipFile(path) as z:
  shared=[]
  if 'xl/sharedStrings.xml' in z.namelist():
   with z.open('xl/sharedStrings.xml') as f:
    for _,e in ET.iterparse(f,events=('end',)):
     if e.tag==N+'si':
      shared.append(''.join(t.text or '' for t in e.iter(N+'t')));e.clear()
  with z.open('xl/worksheets/sheet1.xml') as f:
   for _,e in ET.iterparse(f,events=('end',)):
    if e.tag!=N+'row':continue
    data={}
    for c in e.findall(N+'c'):
     ref=c.get('r',''); col=re.match(r'[A-Z]+',ref)
     if not col:continue
     index=0
     for letter in col.group():index=index*26+ord(letter)-64
     v=c.find(N+'v');raw=v.text if v is not None else ''
     if c.get('t')=='s' and raw:raw=shared[int(raw)]
     if c.get('t')=='inlineStr':raw=''.join(t.text or '' for t in c.iter(N+'t'))
     data[index-1]=str(raw or '').strip()
    yield data
    e.clear()
def split_code(v):
 a,b=(v.split('-',1)+[''])[:2] if '-' in v else (v,'')
 return [a.strip().upper(),b.strip()]
def excel_date(v):
 try:return (datetime(1899,12,30)+timedelta(days=float(v))).isoformat(timespec='seconds')
 except:return None
def run(source,out):
 out.mkdir(parents=True,exist_ok=True)
 it=excel_rows(source)
 header=next(it); cols={v.strip():i for i,v in header.items()}
 missing=[c for c in CAMPOS if c not in cols]
 if missing:raise ValueError('Colunas obrigatórias não encontradas: '+', '.join(missing))
 def get(r,k):return r.get(cols[k],'').strip()
 cube=collections.Counter();counts=collections.Counter();codes={'cid':{},'procedimento':{},'origem':{},'destino':{}}
 unrecognized=collections.Counter();examples=collections.Counter(); seen_ids=set(); duplicate_ids=0
 for r in it:
  counts['linhas_lidas']+=1
  situacao=get(r,'Situação').upper()
  examples[situacao]+=1
  if not ('INTERNAÇÃO REALIZADA' in situacao or 'INTERNACAO REALIZADA' in situacao):
   counts['situacao_nao_realizada']+=1;continue
  id_internacao=get(r,'Nº da Internação')
  if id_internacao:
   if id_internacao in seen_ids:duplicate_ids+=1;continue
   seen_ids.add(id_internacao)
  else:counts['sem_numero_internacao']+=1
  eletiva=get(r,'Internação Eletiva').upper()
  modalidade='eletiva' if eletiva=='SIM' else 'urgencia' if eletiva in ('NÃO','NAO') else 'nao_informada'
  if modalidade=='nao_informada':unrecognized[eletiva]+=1
  cid,desc_cid=split_code(get(r,'Diagnóstico'))
  proc,desc_proc=split_code(get(r,'Procedimento'))
  origem,origem_nome=split_code(get(r,'Município de Origem'))
  destino,destino_nome=split_code(get(r,'Município de Destino'))
  moradia,_=split_code(get(r,'Município do Paciente'))
  macro_o,_=split_code(get(r,'Macro de Origem PDR data da extração'))
  macro_d,_=split_code(get(r,'Macro de Destino PDR data da extração'))
  micro_o,_=split_code(get(r,'Micro de Origem PDR data da extração'))
  micro_d,_=split_code(get(r,'Micro de Destino PDR data da extração'))
  # Chave agregada sem dados pessoais e sem identificador individual
  key=(modalidade,cid,proc,origem,destino,moradia,macro_o,macro_d,micro_o,micro_d)
  cube[key]+=1;counts['internacoes_realizadas']+=1
  if origem and destino and origem!=destino:counts['origem_solicitante_destino_diferentes']+=1
  if moradia and destino and moradia!=destino:counts['residencia_destino_diferentes']+=1
  codes['cid'][cid]=desc_cid;codes['procedimento'][proc]=desc_proc
  codes['origem'][origem]=origem_nome;codes['destino'][destino]=destino_nome
  counts['modalidade_'+modalidade]+=1
 counts['duplicidade_numero_internacao_descartada']=duplicate_ids
 rows=[list(k)+[v] for k,v in sorted(cube.items())]
 schema={'schema':2,'fonte':source.name,'modo':'local_restrito','aviso':'Não publicar diretamente. Cruzamentos e pequenas células podem permitir reidentificação.','campos':['modalidade','cid','procedimento','municipio_origem_solicitante','municipio_destino','municipio_residencia','macro_origem','macro_destino','micro_origem','micro_destino','internacoes'],'metrica':'Contagem de Nº da Internação com Situação=INTERNAÇÃO REALIZADA; IDs duplicados descartados','registros':rows}
 (out/'2025-01_local_restrito.json').write_text(json.dumps(schema,ensure_ascii=False,separators=(',',':')),encoding='utf-8')
 (out/'catalogos.json').write_text(json.dumps(codes,ensure_ascii=False,indent=2),encoding='utf-8')
 audit={'arquivo':source.name,'contagens':dict(counts),'situacoes':dict(examples),'valores_modalidade_desconhecidos':dict(unrecognized),'celulas_agregadas':len(rows),'observacoes':['CPF e nome não são lidos; pessoas distintas não calculadas.','CID e procedimento originais mantidos para validar código/descrição.','Origem solicitante, residência e destino são conceitos diferentes.','Este é um agregado local, não adequado para publicação sem análise de risco de divulgação.','Séries mensais e tempos devem ser revalidados antes de generalizar o processamento.']}
 (out/'auditoria.json').write_text(json.dumps(audit,ensure_ascii=False,indent=2),encoding='utf-8')
 print(json.dumps({'contagens':dict(counts),'celulas_agregadas':len(rows),'arquivos':[p.name for p in out.iterdir()]},ensure_ascii=False,indent=2))
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('entrada',type=Path);p.add_argument('--out',type=Path,default=Path('dados_v2'));a=p.parse_args();run(a.entrada,a.out)
