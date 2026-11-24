# Observatório — Fase 2: origem e CID (janeiro/2025)

Esta fase acrescenta dois rankings **independentes** carregados automaticamente: macrorregião de origem do estabelecimento solicitante e capítulo CID-10.

## Arquivos para adicionar/atualizar
- `index.html` (substituir o da raiz)
- `dados/2025-01_origem_macro.json` (adicionar)
- `dados/2025-01_cid_capitulos.json` (adicionar)

Os outros arquivos já publicados permanecem iguais. Não altere o workflow do GitHub Pages.

## Cobertura e limites
- Jan/2025, somente internações com situação realizada, deduplicação pelo número da internação quando presente.
- Macro de origem: campo `Macro de Origem PDR data da extração` — **não** confundir com residência do paciente.
- CID: agrupamento por primeira letra do diagnóstico. Não é filtro por CID exato, nem substitui o catálogo CID-10 completo.
- Os rankings **não** recebem filtros de procedimento, destino ou modalidade.
- Não foram publicados CPF, nome, IDs de internação ou cruzamentos finos.
- Grupos abaixo de 20 ocorrências e não classificados foram omitidos. Esta regra isolada **não garante anonimato**: o material é candidato à publicação e requer avaliação institucional do risco de inferência, inclusive por diferença com outras tabelas já publicadas.
- Não publicar o arquivo `auditoria_fase2_INTERNA.json`; ele foi mantido fora do ZIP.

## Teste
Depois do commit no `main`, abra `/dados/2025-01_origem_macro.json` e `/dados/2025-01_cid_capitulos.json`, em seguida o site. Na tela, procure `Origem e diagnóstico · Janeiro de 2025`.

## Próximos passos
Para CID exato, município de origem e combinações completas, usar backend autenticado ou um conjunto de consultas pré-aprovadas com proteção contra reidentificação; o GitHub Pages não autentica acesso ao JSON.
