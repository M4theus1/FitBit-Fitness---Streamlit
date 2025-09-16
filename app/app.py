import streamlit as st
import pandas as pd
import os
import pickle
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# --- Importações do Projeto ---
from core.data.io import load_daily_activity
from core.data.database import (
    create_database_and_tables,
    insert_csv_to_sor,
    run_etl_sor_to_sot,
    run_etl_sot_to_spec_train,
    run_etl_for_predict_data,
    load_data,
    drop_database,
    get_activity_summary,
    get_daily_activity_stats
)
from core.features.preprocess import make_preprocess_pipeline
from core.models.train import train_regressor
from core.models.predict import evaluate_regressor
from core.explain.coefficients import extract_linear_importances
from core.chatbot.rules import answer_from_metrics

# --- Configurações da Página e Estado ---
st.set_page_config(page_title="Análise de Atividade Física - Dashboard Interativo", layout="wide")

# Estado da sessão
if "model_trained" not in st.session_state:
    st.session_state.model_trained = False
if "predictions_made" not in st.session_state:
    st.session_state.predictions_made = False
if "prediction_df" not in st.session_state:
    st.session_state.prediction_df = None
if "chat_messages" not in st.session_state:
    st.session_state.chat_messages = [{"role": "assistant", "content": "Olá! Treine um modelo ou carregue um modelo salvo para começar."}]
if "metrics" not in st.session_state:
    st.session_state.metrics = None
if "importances" not in st.session_state:
    st.session_state.importances = None

# --- Diretórios ---
MODEL_DIR = "model"
if not os.path.exists(MODEL_DIR):
    os.makedirs(MODEL_DIR)
MODEL_PATH = os.path.join(MODEL_DIR, "regressor_model.pickle")

# --- Funções Auxiliares ---
@st.cache_data
def convert_df_to_csv(df):
    return df.to_csv(index=False).encode('utf-8')

# --- Título e Sidebar ---
st.title("🏃‍♂️ Análise de Atividade Física - Dashboard Interativo")

with st.sidebar:
    st.header("1. Upload dos Dados")
    uploaded_files = st.file_uploader(
        "Envie o arquivo 'DailyActivityMerged.csv'",
        type=["csv"],
        accept_multiple_files=True
    )
    
    st.header("2. Ações do Pipeline")
    
    # --- AÇÃO 1: Treinar um novo modelo ---
    st.subheader("Treinar Novo Modelo")
    test_size = st.slider("Tamanho do conjunto de teste (validação)", 0.1, 0.4, 0.2, 0.05)
    target_variable = st.selectbox(
        "Variável Alvo para Previsão",
        ["Calories", "TotalSteps", "TotalActiveMinutes", "SedentaryMinutes"]
    )
    
    if st.button("Executar Treinamento"):
        df_data = None
        for file in uploaded_files:
            if "daily" in file.name.lower() or "activity" in file.name.lower():
                # Salva o arquivo temporariamente e carrega
                try:
                    # Salva o arquivo uploadado temporariamente
                    temp_path = f"temp_{file.name}"
                    with open(temp_path, "wb") as f:
                        f.write(file.getbuffer())
                    
                    # Carrega o arquivo
                    df_data = load_daily_activity(temp_path)
                    
                    # Remove o arquivo temporário
                    os.remove(temp_path)
                    
                    if df_data is not None and not df_data.empty:
                        break
                        
                except Exception as e:
                    st.error(f"Erro ao processar arquivo {file.name}: {e}")
                    continue
        
        if df_data is not None and not df_data.empty:
            with st.spinner("Processando dados e treinando o modelo..."):
                try:
                    # Executa o pipeline ETL
                    create_database_and_tables()
                    insert_csv_to_sor(df_data)
                    run_etl_sor_to_sot()
                    run_etl_sot_to_spec_train()
                    
                    # Carrega dados processados
                    df_spec_train = load_data("spec_daily_activity_train")
                    
                    # Prepara dados para treino
                    y = df_spec_train[target_variable]
                    X = df_spec_train.drop(columns=[target_variable])
                    
                    # Preprocessamento e treino
                    pre = make_preprocess_pipeline(X)
                    model, X_test, y_test = train_regressor(X, y, pre, test_size=test_size)
                    
                    # Salva o modelo
                    with open(MODEL_PATH, "wb") as f:
                        pickle.dump(model, f)
                    
                    # Avalia o modelo
                    st.session_state.metrics = evaluate_regressor(model, X_test, y_test)
                    st.session_state.importances = extract_linear_importances(model, X.columns, pre)
                    st.session_state.model_trained = True
                    st.session_state.predictions_made = False
                    st.session_state.target_variable = target_variable
                    
                    st.success(f"Modelo treinado para prever '{target_variable}' e salvo com sucesso!")
                    
                except Exception as e:
                    st.error(f"Erro durante o treinamento: {e}")
        else:
            st.warning("Nenhum dado válido de atividade física foi encontrado nos arquivos uploadados.")

    # --- AÇÃO 2: Fazer previsões com novos dados ---
    st.subheader("Fazer Previsões com Novos Dados")
    if st.button("Carregar Modelo e Fazer Previsões"):
        if not os.path.exists(MODEL_PATH):
            st.error("Nenhum modelo treinado foi encontrado! Por favor, execute o treinamento primeiro.")
        else:
            df_new_data = None
            for file in uploaded_files:
                if "daily" in file.name.lower() or "activity" in file.name.lower():
                    df_new_data = load_daily_activity(file)
            
            if df_new_data is not None:
                with st.spinner("Processando dados e fazendo previsões..."):
                    # Processa os dados para previsão
                    run_etl_for_predict_data(df_new_data)
                    df_spec_predict = load_data("spec_daily_activity_predict")
                    
                    # Carrega o modelo
                    with open(MODEL_PATH, 'rb') as f:
                        model = pickle.load(f)

                    # Faz a previsão (remove a variável alvo se existir)
                    X_predict = df_spec_predict.drop(columns=[st.session_state.target_variable], errors='ignore')
                    predictions = model.predict(X_predict)
                    
                    # Prepara resultado
                    result_df = df_spec_predict.copy()
                    result_df[f'Predicted_{st.session_state.target_variable}'] = predictions
                    st.session_state.prediction_df = result_df
                    st.session_state.predictions_made = True
                st.success("Previsões geradas com sucesso!")
            else:
                st.warning("Arquivo de atividade física não encontrado.")
    
    # --- AÇÃO 3: Limpeza ---
    st.header("3. Manutenção")
    if st.button("Limpar Tudo"):
        drop_database()
        if os.path.exists(MODEL_PATH):
            os.remove(MODEL_PATH)
        st.session_state.clear()
        st.info("Banco de dados, modelo salvo e sessão resetados.")
        st.rerun()

# --- Abas Principais ---
tab_overview, tab_train, tab_predict, tab_analytics, tab_chat = st.tabs([
    "📊 Visão Geral", "🤖 Resultados do Treino", "🚀 Previsões", "📈 Analytics", "💬 Chat com o Modelo"
])

with tab_overview:
    st.header("Visão Geral dos Dados de Atividade")
    if uploaded_files:
        for file in uploaded_files:
            if "daily" in file.name.lower() or "activity" in file.name.lower():
                try:
                    # Salva o arquivo temporariamente
                    temp_path = f"temp_overview_{file.name}"
                    with open(temp_path, "wb") as f:
                        f.write(file.getbuffer())
                    
                    # Carrega o arquivo
                    df_overview = load_daily_activity(temp_path)
                    
                    # Remove o arquivo temporário
                    os.remove(temp_path)
                    
                    if df_overview is not None and not df_overview.empty:
                        st.subheader(f"Arquivo: {file.name}")
                        st.dataframe(df_overview.head())
                        
                        st.subheader("Estatísticas descritivas")
                        st.dataframe(df_overview.describe())
                        
                        st.subheader("Informações do dataset")
                        st.write(f"**Formato:** {df_overview.shape[0]} linhas × {df_overview.shape[1]} colunas")
                        if 'ActivityDate' in df_overview.columns:
                            st.write(f"**Período:** {df_overview['ActivityDate'].min()} até {df_overview['ActivityDate'].max()}")
                        break
                    else:
                        st.warning(f"O arquivo {file.name} está vazio ou não pôde ser carregado.")
                        
                except Exception as e:
                    st.error(f"Erro ao carregar arquivo {file.name}: {e}")
    else:
        st.info("Faça upload do arquivo DailyActivityMerged.csv para ver a visão geral.")

with tab_train:
    st.header("Métricas e Importância do Modelo")
    if not st.session_state.model_trained and st.session_state.metrics is None:
        st.info("Execute o treinamento na barra lateral para ver os resultados.")
    else:
        st.subheader(f"📈 Métricas para previsão de {st.session_state.target_variable}")
        st.json(st.session_state.metrics)
        st.subheader("🔎 Importâncias das Variáveis")
        st.dataframe(st.session_state.importances.head(15), use_container_width=True)
        
        # Visualização das importâncias
        if not st.session_state.importances.empty:
            st.subheader("📊 Gráfico de Importâncias")
            importance_chart_data = st.session_state.importances.head(10).sort_values('importance', ascending=True)
            st.bar_chart(importance_chart_data.set_index('feature')['importance'])

with tab_predict:
    st.header("Previsões para Novos Dados")
    if not st.session_state.predictions_made:
        st.info("Faça uma previsão na barra lateral para ver os resultados.")
    else:
        st.subheader(f"Previsões de {st.session_state.target_variable}")
        st.dataframe(st.session_state.prediction_df)
        
        csv_data = convert_df_to_csv(st.session_state.prediction_df)
        st.download_button(
           label="Download das Previsões em CSV",
           data=csv_data,
           file_name='activity_predictions.csv',
           mime='text/csv',
        )

with tab_analytics:
    st.header("Análises e Estatísticas")
    if st.session_state.model_trained:
        try:
            activity_summary = get_activity_summary()
            daily_stats = get_daily_activity_stats()
            
            st.subheader("📋 Resumo das Atividades")
            st.dataframe(activity_summary)
            
            st.subheader("📈 Estatísticas Diárias")
            st.dataframe(daily_stats.head(10))
            
            # Gráficos simples
            col1, col2 = st.columns(2)
            with col1:
                st.line_chart(daily_stats.set_index('ActivityDate')['DailySteps'])
                st.caption("Passos Diários")
            
            with col2:
                st.line_chart(daily_stats.set_index('ActivityDate')['DailyCalories'])
                st.caption("Calorias Diárias")
                
        except Exception as e:
            st.warning(f"Não foi possível carregar análises: {e}")
    else:
        st.info("Treine um modelo primeiro para ver as análises.")

with tab_chat:
    st.header("Converse com o Assistente do Modelo")
    if not st.session_state.model_trained and st.session_state.metrics is None:
        st.info("Treine um modelo primeiro para poder conversar sobre seus resultados.")
    else:
        for message in st.session_state.chat_messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])
        if prompt := st.chat_input(f"Pergunte sobre a previsão de {st.session_state.target_variable}..."):
            st.session_state.chat_messages.append({"role": "user", "content": prompt})
            response = answer_from_metrics(
                question=prompt,
                task="Regressão",
                metrics_df_or_dict=st.session_state.metrics,
                importances_df=st.session_state.importances,
                target_variable=st.session_state.target_variable
            )
            st.session_state.chat_messages.append({"role": "assistant", "content": response})
            st.rerun()