# Observatório de Regulação Assistencial · SUSfácilMG

Interface de consulta dos **agregados públicos preexistentes**, organizados por mês (janeiro/2025 a abril/2026). Setor responsável: **CGIT — Coordenação de Gestão da Informação e Transparência**.

## Publicação no GitHub Pages

1. Crie um repositório ou faça o upload do conteúdo **desta pasta** para a raiz de seu repositório do observatório.
2. Em **Settings → Pages → Build and deployment**, escolha **Deploy from a branch**, `main` e `/ (root)`.
3. Acesse a URL gerada pelo GitHub Pages. Pode levar alguns minutos até o primeiro deploy aparecer.

Para testar localmente: `python -m http.server 8000` e abra `http://localhost:8000`.

## Cobertura, segurança e limitações

- O painel consulta apenas os dados já classificados como `modo: publico` no `dados/manifest.json`, com mínimo de cinco internações por célula.
- A supressão simples de células pequenas **não é garantia suficiente de privacidade** quando há múltiplos filtros e cruzamentos. Antes de divulgação institucional, revisar supressão complementar, riscos de diferença entre consultas e autorização para publicação dos agregados existentes.
- Esses totais são parciais; não podem ser tratados como total estadual de internações.
- Não há nos JSONs públicos CID, origem, residência ou modalidade. Os controles correspondentes não são apresentados como funcionais.
- Não publicar as planilhas originais, dados pessoais ou o novo agregado `*_local_restrito.json`.
- O gerador em `tools/` é para execução local restrita, não produz dados públicos prontos para publicação.
- Módulo CORE Saúde MG ainda não integrado.
- Logos foram incluídas a partir dos arquivos fornecidos para o protótipo; confirmar uso institucional antes de divulgação oficial.

## Atualização

Atualize `dados/manifest.json` e as partições mensais públicas preservando o esquema descrito no manifesto. Valide totais, os indicadores e a política de divulgação antes de substituir arquivos públicos.
