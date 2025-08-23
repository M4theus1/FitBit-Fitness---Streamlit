Arquitetura de Software --- Análise de Dados Fitness com Streamlit Este
documento descreve a arquitetura lógica, a organização em camadas e o
fluxo de dados do projeto, além de instruções detalhadas para desenhar o
diagrama no draw.io (diagrams.net) e exportá-lo para o repositório.

1.  Objetivos de Arquitetura Separação de responsabilidades: A interface
    do usuário (Streamlit) é completamente isolada da lógica de negócio
    (core/) e dos dados (data/).

Simplicidade (MVP): Estrutura com poucos componentes, baixo acoplamento
e convenções claras para facilitar o entendimento e a manutenção.

Reprodutibilidade: O pipeline de análise e treinamento do modelo é
encapsulado para garantir resultados consistentes.

Evolução: A arquitetura permite adicionar facilmente novas
visualizações, modelos de machine learning ou fontes de dados no futuro.

Governança: Espaços dedicados para configurações (configs/) e
documentação (docs/) mantêm o projeto organizado.

2.  Visão em Camadas Usuário (navegador) ↓ \[ app/ \] → Streamlit UI
    (Dashboard) ↓ \[ core/ \] ├─ data/ → Leitura e validação do CSV ├─
    features/ → Pré-processamento e seleção de features └─ models/ →
    Treino, avaliação e predição do modelo ↓ \[ data/ \] ├─ raw/ →
    Dataset bruto do Fitbit ├─ processed/ → Dados limpos e preparados └─
    models/ → Modelo treinado salvo em .pkl

3.  Componentes e Responsabilidades app/ Camada de apresentação:
    Constrói a interface do usuário com Streamlit.

Responsável pelo upload do arquivo CSV.

Exibe os gráficos da análise exploratória (EDA), as métricas de
performance do modelo (matriz de confusão, etc.) e a importância das
features.

core/data/ Funções de I/O para carregar o dataset a partir de um arquivo
CSV.

Validação básica do schema (verificação de colunas essenciais e tipos de
dados).

core/features/ Funções para o pré-processamento dos dados.

Criação da variável alvo (ActiveUser) e seleção das features para o
modelo.

core/models/ Treinamento do modelo (RandomForestClassifier).

Avaliação do modelo com métricas de classificação (acurácia, F1-score,
etc.).

Funções para gerar previsões e extrair a importância das features.

data/ raw/: Armazena o dataset original do Fitbit sem modificações.

processed/: Guarda versões tratadas do dataset, se necessário.

models/: Contém os artefatos do modelo treinado e salvo (ex:
random_forest_model.pkl).

configs/ Arquivos de configuração, como parâmetros de modelos ou
configurações de logging.

docs/ Documentação completa do projeto: PMC, arquitetura, análise de
dados, guia de deploy e testes.

4.  Fluxo de Execução O usuário acessa a aplicação Streamlit pelo
    navegador.

Na interface, o usuário faz o upload do dataset do Fitbit (.csv).

A camada app/ envia os dados para core/data/, que realiza a leitura e
validação.

O módulo core/features/ processa os dados, criando a variável alvo e
selecionando as features.

core/models/ usa os dados tratados para treinar e avaliar o
RandomForestClassifier.

As métricas de avaliação e a importância das features são calculadas.

Os resultados (gráficos, tabelas de métricas) são enviados de volta para
a camada app/ e exibidos no dashboard para o usuário.

O modelo treinado pode ser salvo na pasta data/models/.

5.  Como desenhar no draw.io Acesse draw.io.

Crie caixas para representar cada camada principal:

Usuário (Navegador) no topo.

app/ logo abaixo, com o rótulo "Streamlit Dashboard".

core/ no centro, com subdivisões para data, features e models.

data/ na base, com as subpastas raw, processed e models.

configs/ e docs/ podem ser posicionados ao lado, como componentes de
suporte.

Conecte as caixas com setas para ilustrar o fluxo de dados principal:
Usuário → app → core → data.

Adicione rótulos nas setas para descrever as ações, como "Upload CSV",
"Processar Dados", "Treinar Modelo" e "Exibir Resultados".

Salve o diagrama no formato .drawio (para futuras edições) e exporte uma
versão em .png.

No seu repositório, coloque a imagem em docs/images/architecture.png e
adicione a seguinte linha neste arquivo para exibi-la:

![Arquitetura](./images/architecture.png)

Esta arquitetura modular e bem definida é ideal para um projeto de
portfólio, pois demonstra boas práticas de engenharia de software
aplicadas à ciência de dados.
