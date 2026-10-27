#!/usr/bin/env python3
"""Motor local de indicadores SUSfácil. Veja README.md. Python 3.10+."""
import argparse
import csv
import datetime as dt
import hashlib
from functools import lru_cache
import io
import json
import math
import re
import sqlite3
import statistics
import sys
import unicodedata
import zipfile
from collections import Counter
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlparse
from lxml import etree as E

ROOT = Path(__file__).resolve().parent
NS = '{http://schemas.openxmlformats.org/spreadsheetml/2006/main}'
DESCONHECIDO = 'Não informado'
SCHEMA_VERSION = 1
DIMENSOES = {
 'ano': 'Ano', 'mes': 'Mês/ano',
 'macro_destino': 'Macrorregião de destino', 'micro_destino': 'Microrregião de destino',
 'municipio_destino': 'Município de destino', 'macro_origem': 'Macrorregião de origem',
 'micro_origem': 'Microrregião de origem', 'municipio_origem': 'Município de origem',
 'municipio_paciente': 'Município do paciente', 'procedimento': 'Procedimento registrado',
 'procedimento_realizado': 'Procedimento realizado (campo específico)',
 'diagnostico': 'Diagnóstico / CID', 'leito': 'Tipo de leito', 'clinica': 'Clínica',
 'faixa_etaria': 'Faixa etária', 'eletiva': 'Internação eletiva', 'obito': 'Óbito informado',
 'judicial': 'Mandado judicial', 'estab_origem': 'Estabelecimento de origem',
 'estab_destino': 'Estabelecimento de destino', 'central': 'Central reguladora',
 'situacao': 'Situação', 'motivo_alta': 'Motivo da alta',
 'intermunicipal': 'Destino diferente do município de origem',
 'intermacro': 'Destino diferente da macrorregião de origem'}
CAMPOS = {
 'macro_destino': 'Macro de Destino PDR data da extração',
 'micro_destino': 'Micro de Destino PDR data da extração',
 'municipio_destino': 'Município de Destino',
 'macro_origem': 'Macro de Origem PDR data da extração',
 'micro_origem': 'Micro de Origem PDR data da extração',
 'municipio_origem': 'Município de Origem', 'municipio_paciente': 'Município do Paciente',
 'procedimento': 'Procedimento', 'procedimento_realizado': 'Procedimento Realizado',
 'diagnostico': 'Diagnóstico', 'leito': 'Tipo de Leito', 'clinica': 'Clínica',
 'faixa_etaria': 'Faixa Etária', 'eletiva': 'Internação Eletiva', 'obito': 'Óbito',
 'judicial': 'Mandado Judicial', 'estab_origem': 'Estab. Origem',
 'estab_destino': 'Estabelecimento de Destino', 'central': 'Central reguladora da solicitação',
 'situacao': 'Situação', 'motivo_alta': 'Motivo da Alta'}
INDICADORES = {
 'internacoes': {'nome': 'Internações', 'unidade': 'n', 'sql': 'COUNT(*)'},
 'espera_media_h': {'nome': 'Solicitação → internação: média', 'unidade': 'h', 'sql': 'AVG(espera_h)'},
 'espera_mediana_h': {'nome': 'Solicitação → internação: mediana', 'unidade': 'h', 'sql': 'MEDIANA(espera_h)'},
 'ate24_pct': {'nome': 'Internações em até 24h', 'unidade': '%', 'sql': '100.0*SUM(CASE WHEN espera_h<=24 THEN 1 ELSE 0 END)/NULLIF(COUNT(espera_h),0)'},
 'permanencia_media_d': {'nome': 'Permanência: média', 'unidade': 'dias', 'sql': 'AVG(permanencia_d)'},
 'permanencia_mediana_d': {'nome': 'Permanência: mediana', 'unidade': 'dias', 'sql': 'MEDIANA(permanencia_d)'},
 'obitos': {'nome': 'Óbitos informados', 'unidade': 'n', 'sql': "SUM(CASE WHEN obito='Sim' THEN 1 ELSE 0 END)"},
 'obitos_pct': {'nome': 'Óbito entre campos informados', 'unidade': '%', 'sql': "100.0*SUM(CASE WHEN obito='Sim' THEN 1 ELSE 0 END)/NULLIF(SUM(CASE WHEN obito IN ('Sim','Não') THEN 1 ELSE 0 END),0)"},
 'eletivas_pct': {'nome': 'Eletivas entre campos informados', 'unidade': '%', 'sql': "100.0*SUM(CASE WHEN eletiva='Sim' THEN 1 ELSE 0 END)/NULLIF(SUM(CASE WHEN eletiva IN ('Sim','Não') THEN 1 ELSE 0 END),0)"},
 'intermunicipal_pct': {'nome': 'Deslocamento intermunicipal', 'unidade': '%', 'sql': "100.0*SUM(CASE WHEN intermunicipal='Sim' THEN 1 ELSE 0 END)/NULLIF(SUM(CASE WHEN intermunicipal IN ('Sim','Não') THEN 1 ELSE 0 END),0)"},
 'intermacro_pct': {'nome': 'Deslocamento entre macrorregiões', 'unidade': '%', 'sql': "100.0*SUM(CASE WHEN intermacro='Sim' THEN 1 ELSE 0 END)/NULLIF(SUM(CASE WHEN intermacro IN ('Sim','Não') THEN 1 ELSE 0 END),0)"}}
PUBLIC_DIMS = ['mes', 'macro_destino', 'micro_destino', 'municipio_destino', 'procedimento']
BASE_METRICAS = {'internacoes': 'COUNT(*)', 'espera_validas': 'COUNT(espera_h)',
 'espera_soma_h': 'COALESCE(SUM(espera_h),0)',
 'ate24_n': 'SUM(CASE WHEN espera_h<=24 THEN 1 ELSE 0 END)',
 'permanencia_validas': 'COUNT(permanencia_d)', 'permanencia_soma_d': 'COALESCE(SUM(permanencia_d),0)'}


@lru_cache(maxsize=8192)
def norm(s):
    return ''.join(c for c in unicodedata.normalize('NFKD', str(s)) if not unicodedata.combining(c)).strip().casefold()


def texto(v):
    s = '' if v is None else str(v).strip()
    return DESCONHECIDO if norm(s) in ('', 'null', 'none', 'nan', '-', 'nao informado') else s


def booleano(v):
    s = norm(v)
    if s in ('sim','s','1','true'): return 'Sim'
    if s in ('nao','n','0','false'): return 'Não'
    return DESCONHECIDO


def data(v):
    if not str(v).strip(): return None
    try:
        n = float(v)
        if 1 < n < 100000: return dt.datetime(1899,12,30) + dt.timedelta(days=n)
    except (ValueError, TypeError): pass
    s = str(v).strip()
    for fmt in ('%d/%m/%Y %H:%M:%S','%d/%m/%Y %H:%M','%d/%m/%Y','%Y-%m-%d %H:%M:%S','%Y-%m-%d'):
        try: return dt.datetime.strptime(s, fmt)
        except ValueError: pass
    return None


def diferenca(fim, inicio, divisor):
    if fim is None or inicio is None: return None
    valor = (fim-inicio).total_seconds()/divisor
    return round(valor, 8) if valor >= 0 else None


def codigo_procedimento(p):
    m = re.match(r'^([0-9]{10}|[0-9]{2}\.[0-9]{2}\.[0-9]{2}\.[0-9]{3}-[0-9])', p)
    return re.sub(r'\D', '', m.group(1)) if m else ''


def territorial(v):
    s = texto(v)
    # Padroniza o território por código/nome, preservando os rótulos de origem.
    return s


def ler_xlsx(path):
    """Lê a primeira planilha original por streaming; só materializa campos necessários."""
    with zipfile.ZipFile(path) as z:
        strings=[]
        if 'xl/sharedStrings.xml' in z.namelist():
            with z.open('xl/sharedStrings.xml') as f:
                for _, el in E.iterparse(f, events=('end',), tag=NS+'si'):
                    strings.append(''.join(el.itertext()).strip()); el.clear()
                    while el.getprevious() is not None: del el.getparent()[0]
        def value(c):
            v=c.find(NS+'v')
            if c.get('t')=='s': return strings[int(v.text)] if v is not None else ''
            if c.get('t')=='inlineStr': return ''.join(c.itertext()).strip()
            return v.text if v is not None else ''
        wanted={norm(v) for v in CAMPOS.values()} | {norm(v) for v in ['Nº da Internação','Data da Internação','Data da Solicitação','Data da Alta']}
        headers=None
        with z.open('xl/worksheets/sheet1.xml') as f:
            for _, row in E.iterparse(f, events=('end',), tag=NS+'row'):
                if headers is None:
                    headers={re.sub(r'\d','',c.get('r')):norm(value(c)) for c in row}
                    headers={k:v for k,v in headers.items() if v in wanted}
                    exigir_headers(set(headers.values()), str(path))
                else:
                    values=dict.fromkeys(headers.values(), '')
                    values.update({headers[col]: value(c) for c in row if (col:=re.sub(r'\d','',c.get('r'))) in headers})
                    yield values
                row.clear()
                while row.getprevious() is not None: del row.getparent()[0]


def exigir_headers(headers, origem):
    for campo in ('Nº da Internação','Data da Internação','Procedimento','Macro de Destino PDR data da extração'):
        if norm(campo) not in headers: raise ValueError(f'{origem}: coluna obrigatória ausente: {campo}')


def ler_csv(f, origem):
    sample=f.read(65536); f.seek(0)
    try: encoding='utf-8-sig'; sample.decode(encoding)
    except UnicodeDecodeError: encoding='cp1252'
    decoded=sample.decode(encoding, errors='replace')
    try: sep=csv.Sniffer().sniff(decoded,delimiters=',;\t').delimiter
    except csv.Error: sep=','
    with io.TextIOWrapper(f,encoding=encoding) as txt:
        rows=csv.reader(txt,delimiter=sep)
        header=[norm(x) for x in next(rows)]; exigir_headers(set(header),origem)
        for row in rows:
            if not any(x.strip() for x in row): continue
            if len(row)!=len(header): raise ValueError(f'{origem}: linha CSV com número incorreto de colunas')
            yield dict(zip(header,row))


def fontes(pasta):
    for p in sorted(Path(pasta).iterdir()):
        if p.name.startswith('~$') or not p.is_file(): continue
        if p.suffix.lower()=='.xlsx': yield p.name, ler_xlsx(p)
        elif p.suffix.lower()=='.csv':
            with p.open('rb') as f: yield p.name, ler_csv(f,p.name)
        elif p.suffix.lower()=='.zip':
            with zipfile.ZipFile(p) as z:
                for n in sorted(z.namelist()):
                    if n.lower().endswith('.csv') and not n.startswith('__MACOSX/'):
                        with z.open(n) as f: yield p.name+'/'+n, ler_csv(f,n)


class Mediana:
    def __init__(self): self.valores=[]
    def step(self,v):
        if v is not None: self.valores.append(v)
    def finalize(self): return statistics.median(self.valores) if self.valores else None


def conectar(path, readonly=False):
    con=sqlite3.connect('file:'+str(Path(path).resolve())+'?mode=ro', uri=True) if readonly else sqlite3.connect(path)
    con.row_factory=sqlite3.Row
    con.create_aggregate('MEDIANA',1,Mediana)
    con.create_function('NORMALIZAR',1,lambda v:norm(v or ''))
    return con


def importar(pasta, banco, inicio=None, fim=None):
    """Reconstrói um banco privado. Deduplica em disco pela chave lógica da análise."""
    Path(banco).parent.mkdir(parents=True,exist_ok=True)
    temporario=Path(str(banco)+'.novo')
    if temporario.exists(): temporario.unlink()
    con=conectar(temporario)
    con.execute('PRAGMA journal_mode=OFF'); con.execute('PRAGMA synchronous=OFF')
    cols=list(DIMENSOES)
    con.execute('CREATE TABLE internacoes (chave TEXT PRIMARY KEY, '+','.join(f'"{c}" TEXT' for c in cols)+', codigo_procedimento TEXT, espera_h REAL, permanencia_d REAL)')
    con.execute('CREATE TABLE auditoria (arquivo TEXT, lidas INTEGER, incluidas INTEGER, duplicadas INTEGER, data_invalida INTEGER, fora_periodo INTEGER, sem_id INTEGER, espera_invalida INTEGER, permanencia_invalida INTEGER, campos_ausentes TEXT)')
    placeholders=','.join('?' for _ in range(len(cols)+4))
    sql='INSERT OR IGNORE INTO internacoes VALUES ('+placeholders+')'
    fontes_n=0
    for origem, rows in fontes(pasta):
        fontes_n+=1; audit=Counter(); ausentes=set(); batch=[]
        def flush():
            if not batch:return
            before=con.total_changes; con.executemany(sql,batch)
            audit['incluidas']+=con.total_changes-before
            audit['duplicadas']+=len(batch)-(con.total_changes-before)
            batch.clear()
        for r in rows:
            audit['lidas']+=1
            get=lambda k:r.get(norm(k),'').strip()
            din=data(get('Data da Internação'))
            if din is None: audit['data_invalida']+=1;continue
            mes=din.strftime('%Y-%m')
            if (inicio and mes<inicio) or (fim and mes>fim): audit['fora_periodo']+=1;continue
            ident=get('Nº da Internação')
            if not ident: audit['sem_id']+=1;continue
            v={k:texto(get(campo)) for k,campo in CAMPOS.items()}
            for campo in CAMPOS.values():
                if norm(campo) not in r: ausentes.add(campo)
            for k in ('obito','eletiva','judicial'): v[k]=booleano(get(CAMPOS[k]))
            for tipo in ('macro','micro','municipio'):
                for papel in ('origem','destino'): v[f'{tipo}_{papel}']=territorial(v[f'{tipo}_{papel}'])
            for flag,base in [('intermunicipal','municipio'),('intermacro','macro')]:
                a,b=v[base+'_origem'],v[base+'_destino']
                v[flag]=DESCONHECIDO if DESCONHECIDO in (a,b) else ('Não' if norm(a)==norm(b) else 'Sim')
            v['ano']=str(din.year);v['mes']=mes
            ds=data(get('Data da Solicitação')); da=data(get('Data da Alta'))
            espera=diferenca(din,ds,3600); permanencia=diferenca(da,din,86400)
            if espera is None: audit['espera_invalida']+=1
            if permanencia is None: audit['permanencia_invalida']+=1
            codigo=codigo_procedimento(v['procedimento'])
            chave=hashlib.sha256(json.dumps([ident,din.isoformat(),codigo or v['procedimento'],v['macro_destino']],ensure_ascii=False).encode()).hexdigest()
            batch.append((chave,*(v[k] for k in cols),codigo,espera,permanencia))
            if len(batch)>=5000: flush()
        flush()
        con.execute('INSERT INTO auditoria VALUES (?,?,?,?,?,?,?,?,?,?)',(origem,*[audit[k] for k in ['lidas','incluidas','duplicadas','data_invalida','fora_periodo','sem_id','espera_invalida','permanencia_invalida']],json.dumps(sorted(ausentes),ensure_ascii=False)))
        con.commit(); print(json.dumps({'arquivo':origem,**audit},ensure_ascii=False),flush=True)
    if not fontes_n: raise ValueError('Pasta sem XLSX, CSV ou ZIP com CSV')
    for c in ('mes','macro_destino','micro_destino','municipio_destino','codigo_procedimento','macro_origem'):
        con.execute(f'CREATE INDEX idx_{c} ON internacoes ("{c}")')
    con.execute('ANALYZE');con.commit();con.close()
    temporario.replace(banco)
    with conectar(banco,True) as con: print('Banco atualizado:',con.execute('SELECT COUNT(*) FROM internacoes').fetchone()[0],'internações')


def agregado_sql():
    fields={**{k:v['sql'] for k,v in INDICADORES.items()},
            'espera_validas':'COUNT(espera_h)','permanencia_validas':'COUNT(permanencia_d)',
            'obito_informado':"SUM(CASE WHEN obito IN ('Sim','Não') THEN 1 ELSE 0 END)",
            'eletiva_informada':"SUM(CASE WHEN eletiva IN ('Sim','Não') THEN 1 ELSE 0 END)",
            'origem_destino_municipios_validos':"SUM(CASE WHEN intermunicipal IN ('Sim','Não') THEN 1 ELSE 0 END)",
            'origem_destino_macros_validas':"SUM(CASE WHEN intermacro IN ('Sim','Não') THEN 1 ELSE 0 END)"}
    return ','.join(f'{v} AS "{k}"' for k,v in fields.items())


def where_query(pedido):
    clauses=[];params=[]
    for d,values in pedido.get('filtros',{}).items():
        if d not in DIMENSOES and d!='codigo_procedimento':raise ValueError('Filtro desconhecido: '+d)
        if not isinstance(values,list) or len(values)>5000:raise ValueError('Filtro deve ser uma lista de até 5000 valores')
        if values:
            clauses.append(f'"{d}" IN ({",".join("?" for _ in values)})');params.extend(str(v) for v in values)
    for k,op in [('inicio','>='),('fim','<=')]:
        if pedido.get(k):
            dt.datetime.strptime(pedido[k],'%Y-%m')
            clauses.append(f'mes {op} ?');params.append(pedido[k])
    if pedido.get('busca'):
        busca=str(pedido['busca'])
        parts=['NORMALIZAR(procedimento) LIKE ?', 'NORMALIZAR(diagnostico) LIKE ?'];params.extend(['%'+norm(busca)+'%']*2)
        if re.fullmatch(r'[\d.\-\s]+',busca):
            parts.append('codigo_procedimento LIKE ?');params.append('%'+re.sub(r'\D','',busca)+'%')
        clauses.append('('+' OR '.join(parts)+')')
    return (' WHERE '+' AND '.join(clauses)) if clauses else '', params


def consultar(banco,pedido):
    dims=pedido.get('agrupar',['macro_destino'])
    if not isinstance(dims,list) or len(set(dims))!=len(dims) or any(d not in DIMENSOES for d in dims):raise ValueError('Dimensões inválidas')
    metrica=pedido.get('indicador','internacoes')
    if metrica not in INDICADORES:raise ValueError('Indicador desconhecido')
    limite=int(pedido.get('limite',2000))
    if limite<0:raise ValueError('Limite inválido')
    where,params=where_query(pedido)
    grupos=','.join('"'+d+'"' for d in dims)
    select=(grupos+',' if grupos else '')+agregado_sql()
    sql='SELECT '+select+' FROM internacoes'+where+(' GROUP BY '+grupos if dims else '')
    with conectar(banco,True) as con:
        total=dict(con.execute('SELECT '+agregado_sql()+' FROM internacoes'+where,params).fetchone())
        count_sql='SELECT 1 FROM internacoes'+where+(' GROUP BY '+grupos if dims else ' LIMIT 1')
        n=con.execute('SELECT COUNT(*) FROM ('+count_sql+')',params).fetchone()[0]
        sql+=' ORDER BY "'+metrica+'" DESC'+(' LIMIT ?' if limite else '')
        rows=[dict(r) for r in con.execute(sql,params+([limite] if limite else []))]
        monthly=[dict(r) for r in con.execute('SELECT mes,COUNT(*) internacoes FROM internacoes'+where+' GROUP BY mes ORDER BY mes',params)]
    return {'dimensoes':dims,'indicador':metrica,'total':total,'linhas':rows,'grupos':n,'truncado':bool(limite and n>limite),'serie':monthly,'modo':'local'}


def metadados(banco):
    stat=Path(banco).stat(); assinatura=[stat.st_size,stat.st_mtime_ns,SCHEMA_VERSION]
    cache=Path(str(banco)+'.meta.json')
    if cache.exists():
        try:
            cached=json.loads(cache.read_text(encoding='utf-8'))
            if cached.get('assinatura')==assinatura:return cached['conteudo']
        except (OSError,ValueError,KeyError):pass
    with conectar(banco,True) as con:
        valores={d:[r[0] for r in con.execute(f'SELECT DISTINCT "{d}" FROM internacoes ORDER BY "{d}"')] for d in DIMENSOES}
        audit=[dict(r) for r in con.execute('SELECT * FROM auditoria')]
        q=con.execute('SELECT COUNT(*),MIN(mes),MAX(mes) FROM internacoes').fetchone()
    out={'modo':'local','dimensoes':DIMENSOES,'indicadores':{k:{a:b for a,b in v.items() if a!='sql'} for k,v in INDICADORES.items()},'valores':valores,'auditoria':audit,'registros':q[0],'inicio':q[1],'fim':q[2]}
    try:cache.write_text(json.dumps({'assinatura':assinatura,'conteudo':out},ensure_ascii=False),encoding='utf-8')
    except OSError:pass
    return out


def publicar_agregados(banco,destino,minimo=5):
    """Um único cubo público: sem totais paralelos que revelem células omitidas."""
    if minimo<5:raise ValueError('O modo público exige mínimo de 5 registros por célula')
    out=Path(destino);out.mkdir(parents=True,exist_ok=True)
    cols=PUBLIC_DIMS+list(BASE_METRICAS)
    select=','.join('"'+d+'"' for d in PUBLIC_DIMS)+','+','.join(f'{expr} AS {k}' for k,expr in BASE_METRICAS.items())
    group=','.join('"'+d+'"' for d in PUBLIC_DIMS)
    manifest={'schema':SCHEMA_VERSION,'modo':'publico','minimo_celula':minimo,'colunas':cols,'particoes':[],
      'dimensoes':{k:DIMENSOES[k] for k in ['ano']+PUBLIC_DIMS},
      'indicadores':{k:{a:b for a,b in INDICADORES[k].items() if a!='sql'} for k in ['internacoes','espera_media_h','ate24_pct','permanencia_media_d']},
      'nota':'Consulta pública com totais parciais: grupos com menos de '+str(minimo)+' internações não são exibidos. Para contagens integrais e mais dimensões, use o modo local.',
      'gerado_em':dt.datetime.now(dt.timezone.utc).isoformat()}
    with conectar(banco,True) as con:
        for mes, in con.execute('SELECT DISTINCT mes FROM internacoes ORDER BY mes'):
            rows=[]
            for r in con.execute('SELECT '+select+' FROM internacoes WHERE mes=? GROUP BY '+group+' HAVING COUNT(*)>=?',[mes,minimo]):
                v=list(r)
                # Médias/percentuais também exigem denominador válido >= mínimo.
                i=cols.index('espera_validas')
                if v[i]<minimo:
                    for c in ['espera_validas','espera_soma_h','ate24_n']:v[cols.index(c)]=0
                i=cols.index('permanencia_validas')
                if v[i]<minimo:
                    for c in ['permanencia_validas','permanencia_soma_d']:v[cols.index(c)]=0
                rows.append(v)
            filename=mes+'.json'
            (out/filename).write_text(json.dumps(rows,ensure_ascii=False,separators=(',',':')),encoding='utf-8')
            manifest['particoes'].append({'mes':mes,'arquivo':filename,'celulas':len(rows)})
    (out/'manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2),encoding='utf-8')
    current={p['arquivo'] for p in manifest['particoes']}|{'manifest.json'}
    for f in out.glob('*.json'):
        if f.name not in current:f.unlink()
    print('Agregados públicos gerados:',len(manifest['particoes']),'meses')


def servidor(banco,porta):
    class Handler(SimpleHTTPRequestHandler):
        def __init__(self,*a,**kw):super().__init__(*a,directory=str(ROOT/'painel'),**kw)
        def log_message(self,fmt,*args):pass
        def validar(self):
            host=self.headers.get('Host','')
            if host not in (f'127.0.0.1:{porta}',f'localhost:{porta}'):
                self.send_error(403);return False
            origin=self.headers.get('Origin')
            if origin and origin not in (f'http://127.0.0.1:{porta}',f'http://localhost:{porta}'):
                self.send_error(403);return False
            return True
        def enviar(self,obj,status=200):
            raw=json.dumps(obj,ensure_ascii=False,allow_nan=False).encode()
            self.send_response(status);self.send_header('Content-Type','application/json; charset=utf-8');self.send_header('Cache-Control','no-store');self.send_header('Content-Length',str(len(raw)));self.end_headers();self.wfile.write(raw)
        def do_GET(self):
            if not self.validar():return
            if urlparse(self.path).path=='/api/meta':
                try:self.enviar(metadados(banco))
                except Exception as e:self.enviar({'erro':str(e)},500)
            else:super().do_GET()
        def do_POST(self):
            if not self.validar():return
            if urlparse(self.path).path!='/api/query':self.send_error(404);return
            size=int(self.headers.get('Content-Length',0))
            if size>1048576:self.send_error(413);return
            try:
                pedido=json.loads(self.rfile.read(size));self.enviar(consultar(banco,pedido))
            except (ValueError,TypeError,KeyError) as e:self.enviar({'erro':str(e)},400)
            except Exception as e:self.enviar({'erro':str(e)},500)
    print(f'Painel completo: http://127.0.0.1:{porta}/?modo=local',flush=True)
    ThreadingHTTPServer(('127.0.0.1',porta),Handler).serve_forever()


def main():
    p=argparse.ArgumentParser(description=__doc__); sub=p.add_subparsers(dest='cmd',required=True)
    a=sub.add_parser('importar');a.add_argument('--entrada',required=True);a.add_argument('--banco',default='privado/internacoes.sqlite');a.add_argument('--inicio');a.add_argument('--fim')
    a=sub.add_parser('consultar');a.add_argument('--banco',default='privado/internacoes.sqlite');a.add_argument('--consulta',required=True);a.add_argument('--saida',required=True)
    a=sub.add_parser('publicar-dados');a.add_argument('--banco',default='privado/internacoes.sqlite');a.add_argument('--destino',default='painel/data');a.add_argument('--minimo',type=int,default=5)
    a=sub.add_parser('servir');a.add_argument('--banco',default='privado/internacoes.sqlite');a.add_argument('--porta',type=int,default=8765)
    args=p.parse_args()
    if args.cmd=='importar':importar(args.entrada,args.banco,args.inicio,args.fim)
    elif args.cmd=='consultar':
        pedido=json.loads(Path(args.consulta).read_text(encoding='utf-8'));pedido['limite']=0
        result=consultar(args.banco,pedido);saida=Path(args.saida);saida.parent.mkdir(parents=True,exist_ok=True)
        if saida.suffix.lower()=='.csv':
            with saida.open('w',encoding='utf-8-sig',newline='') as f:
                campos=result['dimensoes']+list(INDICADORES)+['espera_validas','permanencia_validas','obito_informado','eletiva_informada','origem_destino_municipios_validos','origem_destino_macros_validas'];w=csv.DictWriter(f,fieldnames=campos,delimiter=';');w.writeheader()
                for row in result['linhas']:
                    w.writerow({k:("'"+str(v) if isinstance(v,str) and v.startswith(('=','+','-','@')) else v) for k,v in row.items()})
        else:saida.write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
        print('Consulta exportada:',saida)
    elif args.cmd=='publicar-dados':publicar_agregados(args.banco,args.destino,args.minimo)
    elif args.cmd=='servir':servidor(args.banco,args.porta)


if __name__=='__main__':main()
