#!/usr/bin/env python3
"""Gera camada de modalidade (candidata pública) e diagnósticos de divulgação.
Uso: python gerar_camadas_observatorio.py arquivo.xlsx --out saida
Não envia dados ou arquivos a serviços externos.
"""
import argparse, collections, json, re, sys, zipfile, xml.etree.ElementTree as ET
from pathlib import Path
N='{http://schemas.openxmlformats.org/spreadsheetml/2006/main}'
def linhas_xlsx(path):
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
    r={}
    for c in e.findall(N+'c'):
     mat=re.match(r'[A-Z]+',c.get('r',''))
     if not mat:continue
     i=0
     for a in mat.group():i=i*26+ord(a)-64
     v=c.find(N+'v'); s=v.text if v is not None else ''
     if c.get('t')=='s' and s:s=shared[int(s)]
     if c.get('t')=='inlineStr':s=''.join(t.text or '' for t in c.iter(N+'t'))
     r[i-1]=str(s or '').strip()
    yield r
    e.clear()
def code(s):return str(s).split('-',1)[0].strip().upper()
def gerar(entrada,out,mes=None):
 mes=mes or re.search(r'20\d{2}-\d{2}',entrada.name).group()
 out.mkdir(parents=True,exist_ok=True)
 it=linhas_xlsx(entrada);header=next(it);cols={v.strip():k for k,v in header.items()}
 required=['Nº da Internação','Situação','Internação Eletiva','Diagnóstico','Município de Origem','Município de Destino','Procedimento']
 missing=[c for c in required if c not in cols]
 if missing:raise ValueError('Campos ausentes: '+', '.join(missing))
 def g(r,k):return r.get(cols[k],'').strip()
 counts=collections.Counter();mod=collections.Counter();cid=collections.Counter();orig=collections.Counter();flux=collections.Counter();procs=collections.Counter();seen=set()
 unknown=collections.Counter()
 for row in it:
  counts['linhas_lidas']+=1
  sit=g(row,'Situação').upper()
  if 'INTERNAÇÃO REALIZADA' not in sit and 'INTERNACAO REALIZADA' not in sit:
   counts['nao_realizadas']+=1;continue
  ident=g(row,'Nº da Internação')
  if ident and ident in seen:counts['duplicatas']+=1;continue
  if ident:seen.add(ident)
  else:counts['sem_numero_internacao']+=1
  v=g(row,'Internação Eletiva').upper()
  m='eletiva' if v=='SIM' else 'urgencia' if v in ('NÃO','NAO') else 'nao_informada'
  if m=='nao_informada':unknown[v]+=1
  mod[m]+=1;counts['realizadas']+=1
  c=code(g(row,'Diagnóstico'));o=code(g(row,'Município de Origem'));d=code(g(row,'Município de Destino'));p=code(g(row,'Procedimento'))
  cid[c]+=1;orig[o]+=1;flux[(o,d)]+=1;procs[p]+=1
 public={'schema':1,'periodo':mes,'fonte':'SUSfácilMG — internações realizadas','status':'CANDIDATO_A_PUBLICACAO_SUJEITO_VALIDACAO','dimensoes':['mes','modalidade'],'indicador':'internacoes_realizadas','criterios':['Situação contém INTERNAÇÃO REALIZADA','Nº da Internação duplicado descartado quando presente','Internação Eletiva=SIM é eletiva; NÃO é urgência; outros valores são não informada'],'registros':[[mes,m,n] for m,n in sorted(mod.items())],'total':sum(mod.values())}
 (out/f'{mes}_modalidade_CANDIDATO.json').write_text(json.dumps(public,ensure_ascii=False,indent=2),encoding='utf-8')
 def risk(counter):return {'grupos':len(counter),'grupos_com_1_a_4':sum(1 for n in counter.values() if n<5),'grupos_com_5_a_19':sum(1 for n in counter.values() if 5<=n<20),'menor_contagem':min(counter.values(),default=0)}
 audit={'mes':mes,'contagens':dict(counts),'modalidade':dict(mod),'modalidade_desconhecida':dict(unknown),'consistencia':{'modalidades_somam_realizadas':sum(mod.values())==counts['realizadas'],'origens_somam_realizadas':sum(orig.values())==counts['realizadas'],'cids_somam_realizadas':sum(cid.values())==counts['realizadas']},'risco_de_divulgacao':{'cid':risk(cid),'origem':risk(orig),'origem_destino':risk(flux),'procedimento':risk(procs)},'politica':'CID, origem e fluxos NÃO são exportados neste pacote. Necessária avaliação de células pequenas, cruzamentos, margens e ataques por diferença antes de publicar em repositório aberto.'}
 (out/f'{mes}_auditoria_INTERNA.json').write_text(json.dumps(audit,ensure_ascii=False,indent=2),encoding='utf-8')
 print(json.dumps({'mes':mes,'realizadas':counts['realizadas'],'modalidade':dict(mod),'risco':audit['risco_de_divulgacao']},ensure_ascii=False,indent=2))
if __name__=='__main__':
 parser=argparse.ArgumentParser();parser.add_argument('entrada',type=Path);parser.add_argument('--out',type=Path,default=Path('saida'));parser.add_argument('--mes');a=parser.parse_args();gerar(a.entrada,a.out,a.mes)
