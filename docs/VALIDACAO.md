# Validação da entrega

Período: janeiro–dezembro de 2025 e janeiro–abril de 2026. Conferência realizada nas 16 fontes mensais originais (12 XLSX e 4 CSV no ZIP).

## Cobertura integral importada

| Item | Resultado |
|---|---:|
| Internações em 2025 | 1.532.290 |
| Internações em 2026, janeiro–abril | 514.342 |
| Total integral | 2.046.632 |
| Macrorregiões de destino observadas | 16 |
| Microrregiões de destino observadas | 89 |
| Municípios de destino observados | 375 |
| Rótulos de procedimento registrados | 1.747 |
| Dimensões no motor local | 25 |
| Indicadores no motor local | 11 |

Os 375 municípios são aqueles com internações de destino nas fontes; não correspondem a todos os municípios mineiros. Origem e município do paciente são dimensões adicionais. Rótulos de procedimento são os nomes/códigos informados na fonte, sem catálogo SIGTAP externo.

## Conciliação com a análise anterior

Todos os agrupamentos de **mês × macrorregião × código** do recorte dos 45 procedimentos nas quatro macrorregiões foram comparados com a extração anterior. Resultado idêntico: **204.879 em 2025 + 69.190 em 2026 = 274.069 internações**. Não se trata apenas de coincidência do total: as contagens por mês, macro e procedimento coincidem.

## Pacote público

- 87.605 células agregadas disponibilizadas.
- 1.497.451 internações representadas nessas células.
- Grupos com menos de 5 registros foram omitidos, e denominadores de tempo com menos de 5 observações válidas também são omitidos.
- Os totais do painel público são parciais e **não devem ser comparados como se fossem o total integral**.
- Validador conferiu esquema permitido, ausência de campos individuais, limiares de contagem e integridade dos 16 arquivos mensais.

## Verificações

- Testes Python: filtros combinados, deduplicação, datas inválidas, denominadores, medianas, listas vazias, leitura CSV/ZIP e bloqueio de dimensões não autorizadas.
- Testes JavaScript: filtros, cálculo ponderado de médias e percentuais, períodos, ausência de dados e exportação CSV.
- Conferência da API local com dados reais: AVC em Belo Horizonte de janeiro a abril/2026 = 1.601 internações; mediana da espera individual = 5,98027778 horas; até 24h = 72,2673%.
- Conferência visual no navegador: filtros dependentes, cruzamento município × micro × procedimento, código pontuado, comparação anual, indicador de 24h, exportação CSV e restauração dos filtros.

O workflow do GitHub foi preparado conforme a documentação oficial. A publicação no repositório da usuária ainda não foi executada; a prévia foi testada em ambiente local. A interface pública foi verificada no navegador; a API local foi exercitada por HTTP.

## Atualização: seleção livre

Removido o atalho dos 45 procedimentos. Adicionada busca no catálogo com caixas de seleção e preservação de múltiplas escolhas. Teste com os códigos 0301060088 e 0310010039 na versão pública: 70.412 e 88.172 internações; consulta conjunta = 158.584. Nenhum procedimento selecionado retorna as 1.497.451 internações disponibilizadas. O universo integral continua no modo local.
