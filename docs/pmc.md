# Project Model Canvas — Análise de Dados Fitness com Streamlit

## Contexto
A análise de dados de dispositivos vestíveis, como o Fitbit, tornou-se fundamental para entender os padrões de saúde e atividade física da população.
O dataset utilizado contém métricas diárias agregadas de múltiplos usuários, incluindo total de passos, distância percorrida, calorias queimadas e tempo gasto em diferentes níveis de atividade.
O objetivo educacional é utilizar este conjunto de dados para construir um dashboard interativo que permita a exploração e a classificação do nível de atividade dos usuários.

---

## Problema a ser Respondido
Como os diferentes tipos de atividade diária (passos, distância, minutos ativos) se relacionam com o gasto calórico e a classificação de um usuário como "ativo"? Podemos prever se um usuário atingirá uma meta de atividade com base em suas outras métricas diárias?

---

## Pergunta Norteadora
- Quais são as variáveis que mais influenciam na classificação de um usuário como "Ativo" (definido como >= 7500 passos/dia)?

- É possível treinar um modelo de classificação preciso para automatizar essa identificação?

- Qual é a correlação entre os minutos sedentários e o total de calorias queimadas?

---

## Solução Proposta
Desenvolver um **chatbot educacional em Streamlit** que:

1. Permita o upload do dataset do Fitbit.

2. Apresente uma Análise Exploratória de Dados (EDA) com gráficos de distribuição e correlação.

3. Treine um modelo de Random Forest Classifier para prever se um usuário é "Ativo".

4. Exiba as métricas de performance do modelo, incluindo o relatório de classificação e a matriz de confusão.

5. Mostre um gráfico com a importância de cada feature, destacando os principais preditores de atividade.

---

## Desenho de Arquitetura
O sistema será estruturado em camadas para garantir organização e manutenibilidade:

- **Interface (app/)**: Streamlit como front-end para upload de dados, visualizações e interação com o modelo.

- **Core (core/)**: Módulos Python para carregamento de dados, pré-processamento, treinamento do modelo e funções de avaliação.

- **Dados (data/)**: Pastas para armazenar o dataset bruto, dados processados e o modelo treinado e serializado (ex: model.pkl).

- **Documentação (docs/)**: Incluirá o PMC, detalhes da arquitetura, guia de deploy e a análise exploratória.

---

## Resultados Esperados
- Um modelo de classificação com alta performance (acurácia e F1-score superiores a 95%), devido à forte correlação entre as features.

- Um dashboard interativo e funcional publicado na **Streamlit Cloud**.

- Um relatório claro no dashboard que demonstre visualmente que TotalSteps é a feature mais importante, seguido por Calories e SedentaryMinutes.

---

## Observação Didática
O **PMC serve como um roteiro estratégico para este projeto**. Ele conecta um problema do mundo real (análise de dados de saúde) a uma solução de tecnologia (dashboard com machine learning), alinhando os objetivos técnicos com os resultados de negócio esperados antes do início do desenvolvimento.