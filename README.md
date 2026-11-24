# Observatório Regulação Assistencial — Gerador v3 (etapa 1)

Este pacote processa localmente planilhas originais de internações SUSfácilMG (.xlsx) e cria:

- `saida/2025-01_modalidade_CANDIDATO.json`: **candidato** a agregado público mensal com Urgência/Eletiva, sem dimensão territorial ou CID.
- `saida/2025-01_auditoria_INTERNA.json`: documento de auditoria e diagnóstico de células pequenas. Não publicar sem revisão institucional.
- `gerar_camadas_observatorio.py`: gerador Python só com biblioteca padrão. Não lê nem publica nome/CPF.

## Reproduzir

`python gerar_camadas_observatorio.py "internações realizadas 2025-01(6).xlsx" --out saida`

## Critérios e resultados de janeiro de 2025

- Situação contendo `INTERNAÇÃO REALIZADA` (com ou sem acento).
- Deduplicação por `Nº da Internação` quando preenchido.
- `Internação Eletiva = SIM` → eletiva; `NÃO` → urgência; demais casos → não informada.
- 119.256 linhas; 64 descartadas por situação; 119.192 internações realizadas.
- 99.661 urgências; 19.531 eletivas; soma confere.

## Limitações e cautelas

- Critério de internação realizada e interpretação de modalidade devem ser homologados pela área gestora.
- A versão pública do GitHub Pages expõe os JSONs a qualquer visitante. Nenhuma restrição visual no navegador impede baixar esses arquivos.
- Os cruzamentos origem×destino e CID precisam de avaliação de risco de divulgação (células pequenas, totais, consultas sobrepostas e cálculo por diferença); não são exportados aqui.
- Para distribuição de microdados ou cruzamentos completos, use hospedagem institucional com autenticação e autorização.
- Para atualizar todos os meses, são necessárias as respectivas planilhas originais; os JSONs antigos só possuem destino e procedimento.
- Não substitua o `manifest.json` público existente por este pacote; a integração da nova dimensão depende de atualização coordenada do front-end e homologação.
