import sqlite3
import pandas as pd
import os
from datetime import datetime

# Caminhos e nomes
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
SQL_DIR = os.path.join(CURRENT_DIR, "sql")
APP_DIR = os.path.dirname(os.path.dirname(CURRENT_DIR))
DB_NAME = os.path.join(APP_DIR, "fitness_tracker.db")


# -----------------------------------------------------------
# CONEXÃO E EXECUÇÃO DE SQL
# -----------------------------------------------------------
def connect_db():
    """Cria e retorna conexão SQLite."""
    return sqlite3.connect(DB_NAME)


def execute_sql_from_file(filepath):
    """Executa um script SQL salvo em arquivo."""
    with connect_db() as conn:
        with open(filepath, "r") as f:
            sql_script = f.read()
        conn.executescript(sql_script)
        conn.commit()


def create_database_and_tables():
    """Cria o banco de dados do zero, lendo scripts .sql."""
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


# -----------------------------------------------------------
# ETAPA 1 - INSERÇÃO (SOR) - camada bruta
# -----------------------------------------------------------
def insert_csv_to_sor(df):
    """Insere o DataFrame de origem na tabela SOR."""
    df = df.loc[:, ~df.columns.duplicated()]  # remove colunas duplicadas
    with connect_db() as conn:
        df.to_sql("sor_daily_activity", conn, if_exists="replace", index=False)
    print("✅ Dados inseridos na tabela SOR.")


# -----------------------------------------------------------
# FUNÇÃO PADRÃO DE PARSE DE DATA
# -----------------------------------------------------------
def parse_date_series(series):
    """Tenta converter datas em múltiplos formatos."""
    for fmt in ("%Y-%m-%d %H:%M:%S", "%Y-%m-%d", "%m/%d/%Y"):
        try:
            return pd.to_datetime(series, format=fmt)
        except Exception:
            continue
    return pd.to_datetime(series, errors="coerce")


# -----------------------------------------------------------
# ETAPA 2 - TRANSFORMAÇÃO (SOT) - camada processada
# -----------------------------------------------------------
def run_etl_sor_to_sot():
    """Transforma dados de SOR → SOT."""
    with connect_db() as conn:
        df = pd.read_sql_query("SELECT * FROM sor_daily_activity", conn)

    # Padronização das datas
    df["ActivityDate"] = parse_date_series(df["ActivityDate"])

    # Cálculos derivados
    df["TotalActiveMinutes"] = (
        df.get("VeryActiveMinutes", 0)
        + df.get("FairlyActiveMinutes", 0)
        + df.get("LightlyActiveMinutes", 0)
    )
    df["ActivityRatio"] = df["TotalActiveMinutes"] / df["SedentaryMinutes"].replace(0, 1)
    df["CaloriesPerStep"] = df["Calories"] / df["TotalSteps"].replace(0, 1)

    df["ActivityLevel"] = pd.cut(
        df["TotalSteps"],
        bins=[0, 5000, 10000, float("inf")],
        labels=["Sedentary", "Active", "Very Active"],
    )

    # Tratamento de nulos
    numeric_cols = df.select_dtypes(include=["number"]).columns
    df[numeric_cols] = df[numeric_cols].fillna(df[numeric_cols].mean())

    df["ActivityDate"] = df["ActivityDate"].dt.strftime("%Y-%m-%d")

    with connect_db() as conn:
        df.to_sql("sot_daily_activity", conn, if_exists="replace", index=False)

    print("✅ ETL de SOR → SOT concluído.")


# -----------------------------------------------------------
# ETAPA 3 - ESPECIFICAÇÃO (SPEC TREINO) - camada de especificação
# -----------------------------------------------------------
def run_etl_sot_to_spec_train():
    """Copia dados processados da SOT para SPEC de treino."""
    with connect_db() as conn:
        df = pd.read_sql_query("SELECT * FROM sot_daily_activity", conn)

    spec_cols = [
        "Id",  # mantém ID caso exista
        "ActivityDate",
        "TotalSteps",
        "TotalDistance",
        "TrackerDistance",
        "VeryActiveMinutes",
        "FairlyActiveMinutes",
        "LightlyActiveMinutes",
        "SedentaryMinutes",
        "Calories",
        "TotalActiveMinutes",
        "ActivityRatio",
        "CaloriesPerStep",
        "ActivityLevel",
    ]

    df_spec = df[[c for c in spec_cols if c in df.columns]]

    with connect_db() as conn:
        df_spec.to_sql("spec_daily_activity_train", conn, if_exists="replace", index=False)

    print("✅ ETL de SOT → SPEC (treino) concluído.")


# -----------------------------------------------------------
# ETAPA 4 - PREVISÃO (SPEC PREDICT)
# -----------------------------------------------------------
def run_etl_for_predict_data(df_predict):
    """Executa o ETL para dados de previsão."""
    df_predict["ActivityDate"] = parse_date_series(df_predict["ActivityDate"])

    df_predict["TotalActiveMinutes"] = (
        df_predict.get("VeryActiveMinutes", 0)
        + df_predict.get("FairlyActiveMinutes", 0)
        + df_predict.get("LightlyActiveMinutes", 0)
    )

    df_predict["ActivityRatio"] = df_predict["TotalActiveMinutes"] / df_predict["SedentaryMinutes"].replace(0, 1)
    df_predict["CaloriesPerStep"] = df_predict["Calories"] / df_predict["TotalSteps"].replace(0, 1)

    df_predict["ActivityLevel"] = pd.cut(
        df_predict["TotalSteps"],
        bins=[0, 5000, 10000, float("inf")],
        labels=["Sedentary", "Active", "Very Active"],
    )

    numeric_cols = df_predict.select_dtypes(include=["number"]).columns
    df_predict[numeric_cols] = df_predict[numeric_cols].fillna(df_predict[numeric_cols].mean())

    df_predict["ActivityDate"] = df_predict["ActivityDate"].dt.strftime("%Y-%m-%d")

    predict_cols = [
        "Id",
        "ActivityDate",
        "TotalSteps",
        "TotalDistance",
        "TrackerDistance",
        "VeryActiveMinutes",
        "FairlyActiveMinutes",
        "LightlyActiveMinutes",
        "SedentaryMinutes",
        "Calories",
        "TotalActiveMinutes",
        "ActivityRatio",
        "CaloriesPerStep",
        "ActivityLevel",
    ]

    df_spec = df_predict[[c for c in predict_cols if c in df_predict.columns]]

    with connect_db() as conn:
        df_spec.to_sql("spec_daily_activity_predict", conn, if_exists="replace", index=False)

    print("✅ ETL de previsão concluído e salvo em SPEC (predict).")


# -----------------------------------------------------------
# UTILITÁRIOS
# -----------------------------------------------------------
def load_data(table_name: str):
    with connect_db() as conn:
        return pd.read_sql_query(f"SELECT * FROM {table_name}", conn)


def drop_database():
    if os.path.exists(DB_NAME):
        os.remove(DB_NAME)
        print(f"🗑️ Banco de dados '{DB_NAME}' removido.")


def get_activity_summary():
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

    df["ActivityDate"] = pd.to_datetime(df["ActivityDate"])
    return df
