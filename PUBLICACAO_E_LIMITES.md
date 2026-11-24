# Observatório de Regulação Assistencial — entrega consolidada

## O que funciona com carregamento automático
- Destino, procedimento e período: janeiro/2025 a abril/2026, conforme agregados públicos existentes (cobertura parcial).
- Modalidade (urgência/eletiva): janeiro/2025, total estadual independente dos demais filtros.
- Macrorregião de origem do estabelecimento solicitante: janeiro/2025, ranking e pesquisa por nome/código (sem cruzamentos com destino).
- Diagnóstico CID-10: janeiro/2025, **capítulo** (primeira letra) com pesquisa de lista e exportação, não CID exato.
- A interface tem pesquisa e colagem de listas por procedimento nos agregados existentes.

## Limitações que não podem ser resolvidas apenas no site
- Não existem nos arquivos fornecidos os registros originais detalhados dos demais meses. Portanto não é correto oferecer filtros combinados de origem municipal/CID exato/modalidade/procedimento para 2025-2026.
- Os agregados antigos suprimem células menores que 5. Não somar como total oficial integral.
- Os três agregados novos de janeiro são **candidatos à divulgação** e devem ser HOMOLOGADOS pela área responsável antes de publicação no GitHub Pages público.
- Nunca enviar o JSON de análise local restrita ou arquivos com nome/CPF/identificador individual ao repositório.
- Para cruzamentos finos de dados assistenciais pela equipe, priorizar backend autenticado em ambiente institucional, em vez de JSON estático público.

## Publicação
Copiar `index.html` e os três JSONs `dados/2025-01_modalidade.json`, `dados/2025-01_origem_macro.json`, `dados/2025-01_cid_capitulos.json` para a raiz/pasta `dados` na branch `main` somente após homologação. Preservar as partições mensais já existentes, logos em `assets/` e a configuração Pages funcionando em `Deploy from a branch / main / (root)`. Não reativar workflows antigos de deploy.

## Verificação
- `/dados/manifest.json`
- `/dados/2025-01_modalidade.json`
- `/dados/2025-01_origem_macro.json`
- `/dados/2025-01_cid_capitulos.json`
- No painel: cartões de modalidade, área Origem e diagnóstico, pesquisa por lista e exportação.
