import csv
import io
import json
import sys
import tempfile
import unittest
import zipfile
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import analise as a

class MotorTest(unittest.TestCase):
 def setUp(self):
  self.t=tempfile.TemporaryDirectory();self.root=Path(self.t.name);self.dados=self.root/'dados';self.dados.mkdir();self.banco=self.root/'b.sqlite'
  self.header=['Nº da Internação','Data da Internação','Data da Solicitação','Data da Alta','Procedimento','Macro de Destino PDR data da extração','Micro de Destino PDR data da extração','Município de Destino','Município de Origem','Internação Eletiva','Óbito']
  self.rows=[]
  for i in range(6):self.rows.append([str(i),'02/01/2025 12:00','01/01/2025 12:00','04/01/2025 12:00','0303040149-AVC','3103-CENTRO','CENTRO A','Belo Horizonte','Contagem','Não','Não'])
  self.rows.append(['9','03/01/2025 12:00','04/01/2025 12:00','','0303040149-AVC','3108-NORTE DE MINAS','NORTE A','Montes Claros','','',''])
  self.rows.append(self.rows[0]) # duplicata exata
  self.rows.append(['10','data inválida','','','0303040149-AVC','3103-CENTRO','','','','',''])
  with (self.dados/'amostra.csv').open('w',encoding='cp1252',newline='') as f:
   w=csv.writer(f);w.writerow(self.header);w.writerows(self.rows)
  a.importar(self.dados,self.banco)
 def tearDown(self):self.t.cleanup()
 def test_contagens_e_denominadores(self):
  r=a.consultar(self.banco,{'agrupar':['macro_destino','municipio_destino'],'indicador':'internacoes'})
  self.assertEqual(r['total']['internacoes'],7);self.assertEqual(r['total']['espera_validas'],6)
  self.assertEqual(r['total']['espera_mediana_h'],24);self.assertEqual(r['total']['ate24_pct'],100)
  self.assertEqual(r['total']['permanencia_media_d'],2);self.assertEqual(r['grupos'],2)
  self.assertEqual(r['total']['intermunicipal_pct'],100)
 def test_filtros_combinados(self):
  r=a.consultar(self.banco,{'agrupar':['mes'],'filtros':{'macro_destino':['3103-CENTRO'],'codigo_procedimento':['0303040149']},'inicio':'2025-01','fim':'2025-01'})
  self.assertEqual(r['total']['internacoes'],6)
  r=a.consultar(self.banco,{'agrupar':['mes'],'filtros':{'macro_destino':['inexistente']}})
  self.assertEqual(r['total']['internacoes'],0);self.assertIsNone(r['total']['ate24_pct'])
 def test_rejeita_sql_injection(self):
  with self.assertRaises(ValueError):a.consultar(self.banco,{'agrupar':['mes;DROP TABLE internacoes']})
  with self.assertRaises(ValueError):a.consultar(self.banco,{'filtros':{'invalido':['x']}})
 def test_publicacao(self):
  out=self.root/'public';a.publicar_agregados(self.banco,out)
  meta=json.loads((out/'manifest.json').read_text());rows=json.loads((out/'2025-01.json').read_text())
  self.assertEqual(len(rows),1);self.assertEqual(rows[0][meta['colunas'].index('internacoes')],6)
  self.assertNotIn('diagnostico',meta['colunas']);self.assertNotIn('chave',meta['colunas'])
  with self.assertRaises(ValueError):a.publicar_agregados(self.banco,out,1)
 def test_csv_zip(self):
  z=self.dados/'copy.zip'
  with zipfile.ZipFile(z,'w') as f:f.write(self.dados/'amostra.csv','2026/amostra.csv')
  a.importar(self.dados,self.banco)
  self.assertEqual(a.consultar(self.banco,{'agrupar':[]})['total']['internacoes'],7)
 def test_booleanos(self):
  self.assertEqual(a.booleano('não'),'Não');self.assertEqual(a.booleano(''),'Não informado')

if __name__=='__main__':unittest.main()
