# Observatório de Regulação Assistencial — processamento v2

## Primeira execução: janeiro de 2025

Base: `internações realizadas 2025-01(6).xlsx` (cópia sem nome e CPF).

Comando:

```bash
python gerar_agregados_v2.py "internações realizadas 2025-01(6).xlsx" --out dados_v2
```

Somente Python 3, sem bibliotecas externas. Os dados são lidos em streaming diretamente do XLSX.

## Arquivos gerados

- `dados_v2/2025-01_local_restrito.json`: dados agrupados por modalidade, CID, procedimento, município de origem solicitante, município de destino, município de residência, macro/micro origem e destino.
- `dados_v2/catalogos.json`: catálogo extraído dos próprios registros, com código e descrição de CID e procedimento e códigos/nomes de municípios.
- `dados_v2/auditoria.json`: conferência de quantidade de registros, modalidades, situações e duplicidades.

## Auditoria resumida de janeiro de 2025

- 119.256 registros lidos.
- 119.192 registros com situação “INTERNAÇÃO REALIZADA”.
- 64 excluídos por situação diferente.
- 99.661 urgências e 19.531 eletivas realizadas.
- 17.488 internações com município solicitante diferente do município de destino.
- 43.863 internações com município de residência diferente do município de destino.
- 0 números de internação duplicados entre as realizadas.

## Regras e limites

1. Não existe cálculo de pessoas distintas nesta versão, pois a amostra enviada não contém os identificadores pessoais. Nome e CPF jamais devem ser publicados.
2. A classificação de modalidade usa `Internação Eletiva`: SIM = eletiva; NÃO = urgência; outros valores = não informada.
3. A contagem é por número de internação distinto cuja `Situação` contém `INTERNAÇÃO REALIZADA`. Validar essa regra contra a metodologia oficial antes de usar em relatório.
4. Município do paciente (residência), município de origem (solicitante) e município de destino são três campos independentes.
5. CID e procedimento são extraídos das respectivas colunas; o catálogo é o observado na base, **não uma validação externa da CID-10 ou da SIGTAP**.
6. O JSON gerado é **LOCAL E RESTRITO**. Mesmo sem dados identificáveis diretos, a combinação de atributos com pequenas contagens pode permitir inferência. **Não subir esses arquivos no GitHub Pages**. Para publicação, criar cubos públicos separados, com supressão primária/complentar e análise de risco de reidentificação/diferenciação entre consultas.
7. O gerador foi executado e verificado para janeiro de 2025. Para outros meses, ajustar primeiro o nome do arquivo de saída e comparar o esquema de campos. Os JSONs públicos atuais de 2025-01 a 2026-04 continuam intactos.

## Próximas etapas

- Ligar a camada local à interface aprovada com seletor de CID e procedimento por colagem de lista.
- Conferir classificação de CID principal e procedimento indicado/realizado, e se há outras colunas nos diferentes períodos.
- Estabelecer a política de cubos públicos e camada local restrita antes de publicação.
- Desenvolver consulta e relatório interativos apoiados nos dados verificados.
