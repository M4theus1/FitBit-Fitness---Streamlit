import sqlite3
import pandas as pd
import os
from datetime import datetime

<<<<<<< HEAD
# Caminhos e nomes
=======
# Pega o caminho absoluto do diretório onde este arquivo (database.py) está.
>>>>>>> 00709b86fedb65c87c40b55827377b96ee060e41
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
SQL_DIR = os.path.join(CURRENT_DIR, "sql")
APP_DIR = os.path.dirname(os.path.dirname(CURRENT_DIR))
DB_NAME = os.path.join(APP_DIR, "fitness_tracker.db")

def connect_db():
<<<<<<< HEAD
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

=======
    """Cria uma conexão com o banco de dados SQLite."""
    return sqlite3.connect(DB_NAME)

def execute_sql_from_file(filepath):
    """Lê um arquivo .sql e executa os comandos."""
    conn = connect_db()
    cursor = conn.cursor()
    with open(filepath, 'r') as f:
        sql_script = f.read()
    cursor.executescript(sql_script)
    conn.commit()
    conn.close()

def create_database_and_tables():
    """Cria o banco de dados e todas as tabelas a partir dos arquivos .sql."""
    if os.path.exists(DB_NAME):
        os.remove(DB_NAME)
    
>>>>>>> 00709b86fedb65c87c40b55827377b96ee060e41
    sql_files = [
        os.path.join(SQL_DIR, "sor_daily_activity.sql"),
        os.path.join(SQL_DIR, "sot_daily_activity.sql"),
        os.path.join(SQL_DIR, "spec_daily_activity_train.sql"),
<<<<<<< HEAD
        os.path.join(SQL_DIR, "spec_daily_activity_predict.sql"),
    ]

=======
        os.path.join(SQL_DIR, "spec_daily_activity_predict.sql")
    ]
>>>>>>> 00709b86fedb65c87c40b55827377b96ee060e41
    for filepath in sql_files:
        if not os.path.exists(filepath):
            raise FileNotFoundError(f"Arquivo SQL não encontrado: {filepath}")
        execute_sql_from_file(filepath)
<<<<<<< HEAD
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
=======
    print("Banco de dados e tabelas criados com sucesso.")

def insert_csv_to_sor(df):
    """Insere os dados de um DataFrame na tabela SOR."""
    conn = connect_db()
    # A tabela SOR é genérica, então apenas inserimos os dados de treino nela
    df.to_sql("sor_daily_activity", conn, if_exists="replace", index=False)
    conn.close()
    print("Dados inseridos na tabela SOR.")

def run_etl_sor_to_sot():
    """Executa a transformação de SOR para SOT para os dados de atividade."""
    conn = connect_db()
    df = pd.read_sql_query("SELECT * FROM sor_daily_activity", conn)

    # Lógica de Transformação para dados de atividade física
    # Converter datas para formato padrão - corrigido para aceitar múltiplos formatos
    try:
        # Primeiro tenta o formato ISO (2016-03-25 00:00:00)
        df['ActivityDate'] = pd.to_datetime(df['ActivityDate'], format='%Y-%m-%d %H:%M:%S')
    except ValueError:
        try:
            # Se falhar, tenta o formato ISO sem hora (2016-03-25)
            df['ActivityDate'] = pd.to_datetime(df['ActivityDate'], format='%Y-%m-%d')
        except ValueError:
            try:
                # Se falhar, tenta o formato americano (03/25/2016)
                df['ActivityDate'] = pd.to_datetime(df['ActivityDate'], format='%m/%d/%Y')
            except ValueError:
                # Se todos falharem, deixa o pandas inferir automaticamente
                df['ActivityDate'] = pd.to_datetime(df['ActivityDate'], errors='coerce')
    
    # Calcular métricas derivadas
    df['TotalActiveMinutes'] = df['VeryActiveMinutes'] + df['FairlyActiveMinutes'] + df['LightlyActiveMinutes']
    df['ActivityRatio'] = df['TotalActiveMinutes'] / df['SedentaryMinutes'].replace(0, 1)  # Evitar divisão por zero
    df['CaloriesPerStep'] = df['Calories'] / df['TotalSteps'].replace(0, 1)
    
    # Criar categorias de atividade
    df['ActivityLevel'] = pd.cut(df['TotalSteps'],
                               bins=[0, 5000, 10000, float('inf')],
                               labels=['Sedentary', 'Active', 'Very Active'])
    
    # Tratar valores ausentes (se houver)
    numeric_cols = df.select_dtypes(include=['number']).columns
    df[numeric_cols] = df[numeric_cols].fillna(df[numeric_cols].mean())
    
    # Converter a data de volta para string para armazenamento no SQLite
    df['ActivityDate'] = df['ActivityDate'].dt.strftime('%Y-%m-%d')
    
    # Inserir na SOT
    df.to_sql("sot_daily_activity", conn, if_exists="replace", index=False)
    conn.close()
    print("ETL de SOR para SOT concluído.")

def run_etl_sot_to_spec_train():
    """Copia dados da SOT para a SPEC de treino."""
    conn = connect_db()
    df = pd.read_sql_query("SELECT * FROM sot_daily_activity", conn)
    
    # Selecionar colunas relevantes para análise
    spec_cols = [
>>>>>>> 00709b86fedb65c87c40b55827377b96ee060e41
        'ActivityDate', 'TotalSteps', 'TotalDistance', 'TrackerDistance',
        'VeryActiveMinutes', 'FairlyActiveMinutes', 'LightlyActiveMinutes',
        'SedentaryMinutes', 'Calories', 'TotalActiveMinutes', 'ActivityRatio',
        'CaloriesPerStep', 'ActivityLevel'
    ]
<<<<<<< HEAD

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
=======
    
    df_spec = df[spec_cols]
    df_spec.to_sql("spec_daily_activity_train", conn, if_exists="replace", index=False)
    conn.close()
    print("ETL de SOT para SPEC (treino) concluído.")

def run_etl_for_predict_data(df_predict):
    """Executa o ETL para novos dados e salva na SPEC de previsão."""
    conn = connect_db()
    
    # Aplica as mesmas transformações dos dados de treino
    try:
        df_predict['ActivityDate'] = pd.to_datetime(df_predict['ActivityDate'], format='%Y-%m-%d %H:%M:%S')
    except ValueError:
        try:
            df_predict['ActivityDate'] = pd.to_datetime(df_predict['ActivityDate'], format='%Y-%m-%d')
        except ValueError:
            try:
                df_predict['ActivityDate'] = pd.to_datetime(df_predict['ActivityDate'], format='%m/%d/%Y')
            except ValueError:
                df_predict['ActivityDate'] = pd.to_datetime(df_predict['ActivityDate'], errors='coerce')
    
    df_predict['TotalActiveMinutes'] = df_predict['VeryActiveMinutes'] + df_predict['FairlyActiveMinutes'] + df_predict['LightlyActiveMinutes']
    df_predict['ActivityRatio'] = df_predict['TotalActiveMinutes'] / df_predict['SedentaryMinutes'].replace(0, 1)
    df_predict['CaloriesPerStep'] = df_predict['Calories'] / df_predict['TotalSteps'].replace(0, 1)
    df_predict['ActivityLevel'] = pd.cut(df_predict['TotalSteps'],
                                       bins=[0, 5000, 10000, float('inf')],
                                       labels=['Sedentary', 'Active', 'Very Active'])
    
    numeric_cols = df_predict.select_dtypes(include=['number']).columns
    df_predict[numeric_cols] = df_predict[numeric_cols].fillna(df_predict[numeric_cols].mean())
    
    # Converter a data de volta para string
    df_predict['ActivityDate'] = df_predict['ActivityDate'].dt.strftime('%Y-%m-%d')
    
    # Selecionar colunas para previsão
    predict_cols = [
>>>>>>> 00709b86fedb65c87c40b55827377b96ee060e41
        'ActivityDate', 'TotalSteps', 'TotalDistance', 'TrackerDistance',
        'VeryActiveMinutes', 'FairlyActiveMinutes', 'LightlyActiveMinutes',
        'SedentaryMinutes', 'Calories', 'TotalActiveMinutes', 'ActivityRatio',
        'CaloriesPerStep', 'ActivityLevel'
    ]
<<<<<<< HEAD

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
=======
    
    df_spec = df_predict[predict_cols]
    df_spec.to_sql("spec_daily_activity_predict", conn, if_exists="replace", index=False)
    conn.close()
    print("ETL para dados de previsão concluído e salvo na SPEC (previsão).")

def load_data(table_name: str):
    """Carrega dados de qualquer tabela especificada."""
    conn = connect_db()
    df = pd.read_sql_query(f"SELECT * FROM {table_name}", conn)
    conn.close()
    return df

def drop_database():
    """Remove o arquivo do banco de dados."""
    if os.path.exists(DB_NAME):
        os.remove(DB_NAME)
        print(f"Banco de dados '{DB_NAME}' removido.")

def get_activity_summary():
    """Retorna um resumo estatístico das atividades."""
    conn = connect_db()
    query = """
    SELECT 
        COUNT(*) as TotalRecords,
        MIN(ActivityDate) as StartDate,
        MAX(ActivityDate) as EndDate,
        AVG(TotalSteps) as AvgSteps,
        AVG(Calories) as AvgCalories,
        AVG(TotalActiveMinutes) as AvgActiveMinutes
    FROM spec_daily_activity_train
    """
    df = pd.read_sql_query(query, conn)
    conn.close()
    return df

def get_daily_activity_stats():
    """Retorna estatísticas diárias de atividade."""
    conn = connect_db()
    query = """
    SELECT 
        ActivityDate,
        SUM(TotalSteps) as DailySteps,
        SUM(Calories) as DailyCalories,
        SUM(TotalActiveMinutes) as DailyActiveMinutes,
        AVG(ActivityRatio) as AvgActivityRatio
    FROM spec_daily_activity_train
    GROUP BY ActivityDate
    ORDER BY ActivityDate
    """
    df = pd.read_sql_query(query, conn)
    conn.close()

    # Garantir que ActivityDate é datetime
    df['ActivityDate'] = pd.to_datetime(df['ActivityDate'])

>>>>>>> 00709b86fedb65c87c40b55827377b96ee060e41
    return df
