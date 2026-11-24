# Observatório de Regulação Assistencial — Integração de modalidade (24/11/2026)

## O que entra na publicação
- `index.html`: interface institucional preservada e novo painel automático de modalidade.
- `dados/2025-01_modalidade.json`: totais reais de internações realizadas em janeiro de 2025, por urgência e eletiva.
- Pasta `dados/`: 16 partições públicas originais, sem alteração.
- Pasta `assets/`: logomarcas do layout aprovado.

## Como publicar
Em Settings → Pages, fonte `Deploy from a branch`, branch `main`, pasta `/ (root)`.
Extraia o ZIP e envie o CONTEÚDO da pasta para a raiz do repositório (não envie o ZIP inteiro).
Mantenha `.github/workflows` desativado se a opção de publicação é por branch.
Teste `/dados/2025-01_modalidade.json` e recarregue a página.

## Limitações explícitas
- Modalidade é uma consulta **separada**, restrita a janeiro de 2025. NÃO cruza com filtros atuais de destino e procedimento.
- A base pública de destino é parcial (suprime grupos de contagem pequena). Totais NÃO devem ser comparados como universos equivalentes sem harmonizar regras.
- CID e origem não estão nos 16 JSONs públicos. O arquivo local restrito de janeiro NÃO deve ser publicado.
- O novo JSON é um agregado estadual com somente duas categorias, candidato à homologação institucional antes de divulgação.
- Os arquivos originais dos meses restantes são necessários para gerar a separação de modalidade de fevereiro/2025 em diante.
