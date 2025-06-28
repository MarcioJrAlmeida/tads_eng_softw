# Changelog

Todas as mudanças notáveis à esse repositório devem ser documentadas nesse arquivo.
Esse formato de changelog é baseado no [Keep a Changelog](https://keepachangelog.com/en/1.0.0/)

## [1.1.1] - 2025-06-28
### Added
    - Criação de pasta no diretório */banco*
        - Pasta */data/
            - Contém todas as Tabelas em formato CSV, para que seja possível a consulta dos dados de modo Offline.
### Changed
    - Alteração na pasta */front/app/api*
        - Adição de novas funções de salvar, atualizar, e exclui perguntas no *perguntas_service.py*
        - Adição de novas funções de obter modelo avaliacao e listar avaliacoes no *avaliacao_service.py*
    - Alteração na pasta */front*
        - Alteração no código *forms.py*.
        - Desenvolvimento do código *edicao_forms.py*.
        - Alterado o caminho no botão "Editar Formularios" nas páginas, para *edicao_forms.py*.
        - Alterado em todos os códigos o Modo de consulta aos dados, agora é verificado se está no Modo BD ou CSV.
    - Atualizado arquivo *requirements.txt*
        - Biblioteca Flask instalada no projeto.

## [1.1.0] - 2025-06-26
### Added
    - Adição na pasta */back*
        - Pasta */config*
            - Com a configuração de Modo Desenvolvimento e dados do Banco de Dados.
        - Pasta */database*
            - Com arquivos de criação de Conexão com o Banco de Dados.
            - Arquivo com queries rapidas.
        - Pasta */services*
            - Com arquivo com teste de consulta ao Banco de Dados.
### Changed
    - Alteração na pasta */front*
        - Criação do arquivo de execução do *backend_app.py*
        - Alteração no código *forms.py*, para que seja possível consultar o Banco com as rotas de API.
    - Alteração na pasta */front/app*
        - Desenvolvimento das Rotas de API
            - *configuracao_service.py*
            - *perguntas_service.py*

## [1.1.0] - 2025-06-13
### Added
    - Adição da página "forms.py" em pages
    
## [1.0.9] - 2025-06-05
### Added
    - Adição na pasta */banco*
        - Criação da pasta */ddl*, com o arquivo "create_table.sql"
        - Criação da pasta */dml*, com os arquivos "insert_table.sql" (Dados Ficticios) e "select_table.sql"

## [1.0.8] - 2025-06-04
### Changed
    - Alteração na pasta */banco*
        - Alteração para o modelo Conceitual, pós conversa com Cliente e o Professor de Banco de Dados
        - Adição do modelo Lógico
    - Adição de Modelos em formato PDF

## [1.0.7] - 2025-05-29
### Changed
    - Alteração na pasta */banco*
        - Alteração para o modelo Conceitual, pós conversa com Cliente e o Professor de Banco de Dados
        - Adição do modelo Lógico

## [1.0.6] - 2025-05-26
### Added
    - Adição de Pastas hierarquicas e arquivos de configuração para o Frontend
        - /app
            - /assets
            - components
            - pages
            - script
            - streamlit
        login.py
        config.yaml
        requirements.txt
        run_app.py

## [1.0.5] - 2025-05-25
### Changed
    - Alteração no README
       - Adição de descrição na pasta Documentos

## [1.0.4] - 2025-05-23
### Changed
    - Alteração na pasta */documents*
        - Arquivos alterados e substituidos por novas versões
            - Cronograma - Projeto ES.xlsx
            - PROPOSTA DE PROJETO.docx
### Added
    - Adição de novo documento na pasta */documents*
        - Arquivo de apresetação
            - Sistema-de-Avaliacao-Docente-SADo.pptx

## [1.0.3] - 2025-05-02
### Changed
    - Adição na pasta */documents*
        Levantamento de Requisitos.docx
### Added
    - Adição na pasta */banco*
        *./modelos*
            modelo_ER.png, primeira versão do Modelo Entidade Relacionamento

## [1.0.2] - 2025-04-27
### Added
    - Adição na pasta */documents*
        Aprimoramento os Requisitos.docx
        Passo a Passo Requisitos.docx

## [1.0.1] - 2025-04-25
### Added
    - Adição de pastas para melhor organização de códigos e documentos
        - /front
        - /back
        - /banco
        - /documents

## [1.0.0] - 2025-04-24
### Added
    - Criação do repositório para o Projeto de Engenharia de Sofwtare
    - Criação do arquivo *CHANGELOG.md*, para aplicação de boas práticas e controle de versionamento.
### Added
    - Adição na pasta */documents*, com Cronograma, Modelo de Proposta e questão levantadas ao Dono do Produto.
