# Metodologia dos indicadores

## Unidade, território e tempo

- Contagem por registro de internação, com competência da **Data da Internação**.
- Deduplicação: número da internação + data/hora + código do procedimento registrado + macro de destino; mesmo critério da análise anterior. Conflitos nessa chave preservam a primeira ocorrência pela ordem de leitura e são auditados como duplicatas. Isso não prova que toda duplicata seja uma atualização idêntica; fontes conflitantes devem ser investigadas.
- Dados sem número ou data de internação válida são excluídos e auditados. O importador falha se a fonte não contém colunas obrigatórias.
- Macro/micro: PDR da **data da extração**, conforme fontes. Não houve atualização territorial por tabela externa. Município de origem é o estabelecimento solicitante; município do paciente é outra dimensão.
- Destino é o filtro geográfico padrão. As dimensões de origem não substituem as de destino silenciosamente.
- Categorias ausentes são “Não informado”; não são “Não”.
- Datas brasileiras e seriais Excel são interpretados sem inferir um fuso que a fonte não informou.

## Fórmulas

| Indicador | Fórmula e denominador |
|---|---|
| Internações | Contagem de registros após filtros e deduplicação |
| Espera média em horas | Soma(internação − solicitação)/nº de pares de datas válidos |
| Espera mediana em horas | Mediana dos tempos individuais válidos; modo local |
| Internações em até 24h (%) | 100 × nº de tempos entre 0 e 24h, inclusive / nº de tempos válidos |
| Permanência média em dias | Soma(alta − internação)/nº de pares válidos |
| Permanência mediana em dias | Mediana das permanências individuais válidas; modo local |
| Óbitos informados | Quantidade com campo Óbito = Sim |
| Óbito entre campos informados (%) | 100 × Óbito = Sim / Óbito em {Sim, Não} |
| Eletivas entre campos informados (%) | 100 × Eletiva = Sim / Eletiva em {Sim, Não} |
| Deslocamento intermunicipal (%) | 100 × origem diferente de destino / registros com ambos os municípios conhecidos |
| Deslocamento intermacro (%) | 100 × origem diferente de destino / registros com ambas as macros conhecidas |

Diferenças temporais negativas ou com datas ausentes/inválidas não entram nos indicadores de tempo. A internação continua na contagem geral quando sua data de internação e identificador são válidos. Não há corte arbitrário para tempos altos: inspecione possíveis outliers antes de uso decisório. Óbito informado não é mortalidade ajustada, e solicitação → internação não equivale a tempo de trabalho do regulador.

O banco armazena o tempo com precisão de oito casas decimais. Medianas são calculadas a partir dos registros individuais. O painel público calcula médias ponderadas pelas observações válidas; nunca faz média simples das médias de grupos. Denominador zero retorna ausência de resultado, não zero.

## Comparação de períodos

O botão de comparação desloca o intervalo de meses exatamente um ano, mantendo os demais filtros. Se faltarem fontes mensais no período anterior, não apresenta variação relativa. Filtros explícitos de ano/mês precisam ser retirados para evitar interseção contraditória. Variação = 100 × (atual − anterior)/anterior. Denominador zero não gera variação; mudanças de indicadores percentuais são variações relativas, não pontos percentuais.

A presença de uma fonte mensal não demonstra completude do mês; confira o processo de extração. No público, a composição das células suprimidas pode diferir por período: compare com essa limitação.

## O que não é calculável apenas com estas fontes

Não há campo financeiro; não há população denominadora nem capacidade/ocupação de leitos. A base de internações realizadas exclui solicitações que não resultaram em internação. Portanto, não mede resolutividade de todas as solicitações, taxa de atendimento da fila, eficiência causal da regulação ou demanda reprimida. Não há inferência automática de vaga zero a partir da urgência ou da não eletividade.

## Divulgação

A exportação pública usa um único cubo de destino por mês e procedimento. Todas as visualizações derivam de células com n ≥ 5; totais integrais e dados por registro não são publicados. Tempos de grupos com menos de 5 observações válidas também são omitidos. A supressão simples reduz exposição, mas não constitui prova formal de anonimização contra informação externa ou diferenças entre versões.

A análise completa permanece local. CPF, paciente, data de nascimento e número original da internação não são persistidos pelo importador. A chave SHA-256 serve à deduplicação e não deve ser divulgada. Resultados locais detalhados ainda requerem tratamento institucional adequado.
