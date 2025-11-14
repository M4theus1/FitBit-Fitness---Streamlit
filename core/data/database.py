import sqlite3
import pandas as pd
import os
from datetime import datetime

# Caminhos e nomes
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
SQL_DIR = os.path.join(CURRENT_DIR, "sql")
APP_DIR = os.path.dirname(os.path.dirname(CURRENT_DIR))
DB_NAME = os.path.join(APP_DIR, "fitness_tracker.db")

def connect_db():
    """Cria e retorna conexão SQLite."""
    return sqlite3.connect(DB_NAME)

def execute_sql_from_file(filepath):
    """Executa um script SQL salvo em arquivo."""
    with connect_db() as conn:
        with open(filepath, 'r') as f:
            sql_script = f.read()
        conn.executescript(sql_script)
        conn.commit()

def create_database_and_tables():
    """Cria o banco de dados do zero, lendo os scripts .sql."""
    if os.path.exists(DB_NAME):
        os.remove(DB_NAME)

    sql_files = [
        os.path.join(SQL_DIR, "sor_daily_activity.sql"),
        os.path.join(SQL_DIR, "sot_daily_activity.sql"),
        os.path.join(SQL_DIR, "spec_daily_activity_train.sql"),
        os.path.join(SQL_DIR, "spec_daily_activity_predict.sql"),
    ]

    for filepath in sql_files:
        if not os.path.exists(filepath):
            raise FileNotFoundError(f"Arquivo SQL não encontrado: {filepath}")
        execute_sql_from_file(filepath)
    print("✅ Banco de dados e tabelas criados com sucesso.")

# -----------------------------
# ETAPA 1 - INSERÇÃO (SOR)
# -----------------------------
def insert_csv_to_sor(df):
    """Insere o DataFrame de origem na tabela SOR."""
    df = df.loc[:, ~df.columns.duplicated()]  # remove colunas duplicadas
    with connect_db() as conn:
        df.to_sql("sor_daily_activity", conn, if_exists="replace", index=False)
    print("✅ Dados inseridos na tabela SOR.")

# -----------------------------
# ETAPA 2 - TRANSFORMAÇÃO (SOT)
# -----------------------------
def run_etl_sor_to_sot():
    """Transforma dados de SOR → SOT."""
    with connect_db() as conn:
        df = pd.read_sql_query("SELECT * FROM sor_daily_activity", conn)

    # Padronização de datas
    for fmt in ("%Y-%m-%d %H:%M:%S", "%Y-%m-%d", "%m/%d/%Y"):
        try:
            df['ActivityDate'] = pd.to_datetime(df['ActivityDate'], format=fmt)
            break
        except Exception:
            continue
    df['ActivityDate'] = pd.to_datetime(df['ActivityDate'], errors='coerce')

    # Cálculos derivados
    df['TotalActiveMinutes'] = (
        df.get('VeryActiveMinutes', 0)
        + df.get('FairlyActiveMinutes', 0)
        + df.get('LightlyActiveMinutes', 0)
    )
    df['ActivityRatio'] = df['TotalActiveMinutes'] / df['SedentaryMinutes'].replace(0, 1)
    df['CaloriesPerStep'] = df['Calories'] / df['TotalSteps'].replace(0, 1)

    # Categorias
    df['ActivityLevel'] = pd.cut(
        df['TotalSteps'],
        bins=[0, 5000, 10000, float('inf')],
        labels=['Sedentary', 'Active', 'Very Active']
    )

    # Tratamento de nulos
    numeric_cols = df.select_dtypes(include=['number']).columns
    df[numeric_cols] = df[numeric_cols].fillna(df[numeric_cols].mean())

    df['ActivityDate'] = df['ActivityDate'].dt.strftime('%Y-%m-%d')

    with connect_db() as conn:
        df.to_sql("sot_daily_activity", conn, if_exists="replace", index=False)
    print("✅ ETL de SOR → SOT concluído.")

# -----------------------------
# ETAPA 3 - ESPECIFICAÇÃO (SPEC TREINO)
# -----------------------------
def run_etl_sot_to_spec_train():
    """Copia dados processados da SOT para SPEC de treino."""
    with connect_db() as conn:
        df = pd.read_sql_query("SELECT * FROM sot_daily_activity", conn)

    spec_cols = [
        'Id',  # ✔️ RECUPERAR ID DO USUÁRIO
        'ActivityDate', 'TotalSteps', 'TotalDistance', 'TrackerDistance',
        'VeryActiveMinutes', 'FairlyActiveMinutes', 'LightlyActiveMinutes',
        'SedentaryMinutes', 'Calories', 'TotalActiveMinutes', 'ActivityRatio',
        'CaloriesPerStep', 'ActivityLevel'
    ]

    df_spec = df[spec_cols]

    with connect_db() as conn:
        df_spec.to_sql("spec_daily_activity_train", conn, if_exists="replace", index=False)
    print("✅ ETL de SOT → SPEC (treino) concluído.")


# -----------------------------
# ETAPA 4 - PREVISÃO (SPEC PREDICT)
# -----------------------------
def run_etl_for_predict_data(df_predict):
    """Executa o ETL para dados de previsão."""
    for fmt in ("%Y-%m-%d %H:%M:%S", "%Y-%m-%d", "%m/%d/%Y"):
        try:
            df_predict['ActivityDate'] = pd.to_datetime(df_predict['ActivityDate'], format=fmt)
            break
        except Exception:
            continue
    df_predict['ActivityDate'] = pd.to_datetime(df_predict['ActivityDate'], errors='coerce')

    df_predict['TotalActiveMinutes'] = (
        df_predict.get('VeryActiveMinutes', 0)
        + df_predict.get('FairlyActiveMinutes', 0)
        + df_predict.get('LightlyActiveMinutes', 0)
    )
    df_predict['ActivityRatio'] = df_predict['TotalActiveMinutes'] / df_predict['SedentaryMinutes'].replace(0, 1)
    df_predict['CaloriesPerStep'] = df_predict['Calories'] / df_predict['TotalSteps'].replace(0, 1)
    df_predict['ActivityLevel'] = pd.cut(
        df_predict['TotalSteps'],
        bins=[0, 5000, 10000, float('inf')],
        labels=['Sedentary', 'Active', 'Very Active']
    )

    numeric_cols = df_predict.select_dtypes(include=['number']).columns
    df_predict[numeric_cols] = df_predict[numeric_cols].fillna(df_predict[numeric_cols].mean())
    df_predict['ActivityDate'] = df_predict['ActivityDate'].dt.strftime('%Y-%m-%d')

    predict_cols = [
        'Id',  # ✔️ RECUPERAR ID
        'ActivityDate', 'TotalSteps', 'TotalDistance', 'TrackerDistance',
        'VeryActiveMinutes', 'FairlyActiveMinutes', 'LightlyActiveMinutes',
        'SedentaryMinutes', 'Calories', 'TotalActiveMinutes', 'ActivityRatio',
        'CaloriesPerStep', 'ActivityLevel'
    ]

    df_spec = df_predict[predict_cols]

    with connect_db() as conn:
        df_spec.to_sql("spec_daily_activity_predict", conn, if_exists="replace", index=False)
    print("✅ ETL de previsão concluído e salvo em SPEC (predict).")

# -----------------------------
# UTILITÁRIOS
# -----------------------------
def load_data(table_name: str):
    """Lê qualquer tabela do banco como DataFrame."""
    with connect_db() as conn:
        return pd.read_sql_query(f"SELECT * FROM {table_name}", conn)

def drop_database():
    """Remove o banco de dados SQLite."""
    if os.path.exists(DB_NAME):
        os.remove(DB_NAME)
        print(f"🗑️ Banco de dados '{DB_NAME}' removido.")

def get_activity_summary():
    """Resumo estatístico geral das atividades."""
    query = """
        SELECT 
            COUNT(*) AS TotalRecords,
            MIN(ActivityDate) AS StartDate,
            MAX(ActivityDate) AS EndDate,
            AVG(TotalSteps) AS AvgSteps,
            AVG(Calories) AS AvgCalories,
            AVG(TotalActiveMinutes) AS AvgActiveMinutes
        FROM spec_daily_activity_train
    """
    with connect_db() as conn:
        return pd.read_sql_query(query, conn)

def get_daily_activity_stats():
    """Estatísticas diárias agregadas."""
    query = """
        SELECT 
            ActivityDate,
            SUM(TotalSteps) AS DailySteps,
            SUM(Calories) AS DailyCalories,
            SUM(TotalActiveMinutes) AS DailyActiveMinutes,
            AVG(ActivityRatio) AS AvgActivityRatio
        FROM spec_daily_activity_train
        GROUP BY ActivityDate
        ORDER BY ActivityDate
    """
    with connect_db() as conn:
        df = pd.read_sql_query(query, conn)

    df['ActivityDate'] = pd.to_datetime(df['ActivityDate'])
    return df
