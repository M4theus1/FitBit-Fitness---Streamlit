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
from core.chatbot.rag import rag_pipeline

# --- Configurações da Página ---
st.set_page_config(page_title="🏃‍♂️ Análise de Atividade Física", layout="wide")

# --- Estado da Sessão ---
if "model_trained" not in st.session_state:
    st.session_state.model_trained = False
if "predictions_made" not in st.session_state:
    st.session_state.predictions_made = False
if "prediction_df" not in st.session_state:
    st.session_state.prediction_df = None
if "chat_messages" not in st.session_state:
    st.session_state.chat_messages = [
        {"role": "assistant", "content": "Olá! Faça upload dos dados e treine um modelo para começar."}
    ]
if "metrics" not in st.session_state:
    st.session_state.metrics = None
if "importances" not in st.session_state:
    st.session_state.importances = pd.DataFrame(columns=["feature", "importance"])

# --- Diretórios ---
MODEL_DIR = "model"
os.makedirs(MODEL_DIR, exist_ok=True)
MODEL_PATH = os.path.join(MODEL_DIR, "regressor_model.pickle")

# --- Funções Auxiliares ---
@st.cache_data(ttl=600, show_spinner=False)
def convert_df_to_csv(df):
    return df.to_csv(index=False).encode("utf-8")

# --- Interface ---
st.title("🏃‍♂️ Dashboard Interativo - Análise de Atividade Física")

with st.sidebar:
    st.header("1️⃣ Upload dos Dados")
    uploaded_files = st.file_uploader(
        "Envie o arquivo 'DailyActivityMerged.csv'",
        type=["csv"],
        accept_multiple_files=True
    )

    st.header("2️⃣ Pipeline de Treinamento")
    test_size = st.slider("Tamanho do conjunto de teste", 0.1, 0.4, 0.2, 0.05)
    target_variable = st.selectbox("Variável alvo", ["Calories"])

    if st.button("🚀 Treinar Modelo"):
        df_data = None
        for file in uploaded_files:
            if "daily" in file.name.lower() or "activity" in file.name.lower():
                try:
                    temp_path = f"temp_{file.name}"
                    with open(temp_path, "wb") as f:
                        f.write(file.getbuffer())
                    df_data = load_daily_activity(temp_path)
                    os.remove(temp_path)
                except Exception as e:
                    st.error(f"Erro ao processar {file.name}: {e}")
                    continue

        if df_data is not None and not df_data.empty:
            with st.spinner("Executando pipeline ETL e treino do modelo..."):
                try:
                    create_database_and_tables()
                    insert_csv_to_sor(df_data)
                    run_etl_sor_to_sot()
                    run_etl_sot_to_spec_train()

                    df_spec_train = load_data("spec_daily_activity_train")

                    y = df_spec_train[target_variable]
                    X = df_spec_train.drop(columns=[target_variable])

                    pre = make_preprocess_pipeline(X)
                    model, X_test, y_test = train_regressor(X, y, pre, test_size=test_size)

                    with open(MODEL_PATH, "wb") as f:
                        pickle.dump(model, f)

                    st.session_state.metrics = evaluate_regressor(model, X_test, y_test)
                    st.session_state.importances = extract_linear_importances(model, X.columns, pre)
                    st.session_state.model_trained = True
                    st.session_state.target_variable = target_variable
                    st.session_state.df_overview = df_data

                    st.success(f"✅ Modelo treinado com sucesso para prever '{target_variable}'!")

                except Exception as e:
                    st.error(f"Erro durante o treinamento: {e}")
        else:
            st.warning("Nenhum dado válido foi encontrado.")

    st.header("3️⃣ Limpeza e Reset")
    if st.button("🧹 Limpar Tudo"):
        drop_database()
        if os.path.exists(MODEL_PATH):
            os.remove(MODEL_PATH)
        st.session_state.clear()
        st.info("Sessão, banco e modelo foram limpos.")
        st.rerun()

# --- Abas ---
tab_overview, tab_train, tab_analytics, tab_chat = st.tabs([
    "📊 Visão Geral", "🤖 Treinamento", "📈 Analytics", "💬 Chat"
])

with tab_overview:
    st.header("Visão Geral dos Dados")
    if "df_overview" in st.session_state and st.session_state.df_overview is not None:
        df = st.session_state.df_overview
        st.dataframe(df.head())
        st.subheader("Estatísticas Descritivas")
        st.dataframe(df.describe())
    else:
        st.info("Faça upload e treine um modelo para visualizar os dados.")

with tab_train:
    st.header("Métricas e Importâncias")
    if not st.session_state.model_trained or st.session_state.metrics is None:
        st.info("Treine o modelo para ver as métricas.")
    else:
        st.json(st.session_state.metrics)
        st.dataframe(
            st.session_state.importances.head(20),
            width='stretch'   # ✔️ Correção aqui
        )

with tab_analytics:
    st.header("Estatísticas do Banco de Dados")
    if st.session_state.model_trained:
        try:
            summary = get_activity_summary()
            stats = get_daily_activity_stats()
            st.subheader("Resumo das Atividades")
            st.dataframe(summary)
            st.subheader("Atividades Diárias")
            st.dataframe(stats.head(10))
        except Exception as e:
            st.warning(f"Erro ao carregar estatísticas: {e}")
    else:
        st.info("Treine um modelo primeiro.")

with tab_chat:
    st.header("Chat com o Modelo 📬")
    if not st.session_state.model_trained:
        st.info("Treine um modelo primeiro.")
    else:
        for msg in st.session_state.chat_messages:
            with st.chat_message(msg["role"]):
                st.markdown(msg["content"])
        if prompt := st.chat_input("Pergunte sobre métricas ou variáveis..."):
            st.session_state.chat_messages.append({"role": "user", "content": prompt})
            response = rag_pipeline(
                prompt,
                metrics=st.session_state.metrics,
                importances=st.session_state.importances
            )
            st.session_state.chat_messages.append({"role": "assistant", "content": response})
            st.rerun()
