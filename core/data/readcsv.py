import pandas as pd

def read_csv(file, top_n_users=10):
    """
    Lê o CSV de atividades físicas em chunks e retorna um DataFrame limpo e preparado.
    
    Parâmetros:
        file (str): Caminho do arquivo CSV.
        top_n_users (int): Número de usuários mais frequentes a manter (outros serão categorizados como 'Other').

    Retorna:
        pd.DataFrame: DataFrame pré-processado pronto para inserção na tabela SOR.
    """
    # Lê em chunks para lidar com arquivos grandes
    chunks = pd.read_csv(file, chunksize=100000, sep=',', low_memory=False)
    df = next(chunks)

    # Colunas principais esperadas (ajuste conforme sua base)
    cols_to_keep = [
        'Id', 'ActivityDate', 'TotalSteps', 'TotalDistance', 'TrackerDistance',
        'LoggedActivitiesDistance', 'VeryActiveMinutes', 'FairlyActiveMinutes',
        'LightlyActiveMinutes', 'SedentaryMinutes', 'Calories'
    ]

    # Mantém apenas colunas que realmente existem no CSV
    df = df[[c for c in cols_to_keep if c in df.columns]]

    # Remove linhas completamente vazias ou sem TotalSteps
    df = df.dropna(subset=['TotalSteps', 'ActivityDate'], how='any')

    # Trata outliers ou dados ausentes básicos
    numeric_cols = df.select_dtypes(include=['number']).columns
    df[numeric_cols] = df[numeric_cols].fillna(df[numeric_cols].mean())

    # Normaliza a coluna de datas
    for fmt in ("%Y-%m-%d %H:%M:%S", "%Y-%m-%d", "%m/%d/%Y"):
        try:
            df['ActivityDate'] = pd.to_datetime(df['ActivityDate'], format=fmt)
            break
        except Exception:
            continue
    df['ActivityDate'] = pd.to_datetime(df['ActivityDate'], errors='coerce')

    # Garante formato YYYY-MM-DD
    df['ActivityDate'] = df['ActivityDate'].dt.strftime('%Y-%m-%d')

    # Agrupamento dos usuários mais ativos (se coluna Id existir)
    if 'Id' in df.columns:
        top_users = df['Id'].value_counts().nlargest(top_n_users).index
        df['Id'] = df['Id'].apply(lambda x: x if x in top_users else 'Other')

    # Codificação de variáveis categóricas (somente Id, se presente)
    if 'Id' in df.columns:
        df_encoded = pd.get_dummies(df, columns=['Id'], dtype=int)
    else:
        df_encoded = df.copy()

    # Limpeza de nomes de colunas
    df_encoded = df_encoded.loc[:, ~df_encoded.columns.duplicated()]
    df_encoded.columns = (
        df_encoded.columns
        .str.strip()
        .str.replace(r"[^\w]", "_", regex=True)
    )

    return df_encoded
