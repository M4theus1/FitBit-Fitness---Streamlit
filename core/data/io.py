import pandas as pd

def load_daily_activity(path="data/dailyActivity_merged.csv"):
    """
    Carrega e pré-processa o dataset dailyActivity_merged.csv.
    """
    try:
        # Carrega o CSV, a função read_csv_smart já está embutida no read_csv padrão
        # mas vamos ser explícitos para garantir que a separação seja correta.
        df = pd.read_csv(path)
        
        # Converte a coluna de data para o formato datetime
        # Isso é crucial para qualquer análise temporal
        df['ActivityDate'] = pd.to_datetime(df['ActivityDate'], format='%m/%d/%Y')
        
        return df
    except FileNotFoundError:
        print(f"Erro: O arquivo não foi encontrado no caminho '{path}'")
        return None

def get_most_active_users_calories(df, top_n=10):
    """
    Calcula a média de calorias dos usuários mais ativos, baseados no total de passos.
    """
    if df is None:
        return None
    
    # Agrupa por Id e soma o total de passos de cada usuário
    user_steps = df.groupby('Id')['TotalSteps'].sum()
    
    # Seleciona os IDs dos top_n usuários com mais passos
    most_active_users_ids = user_steps.nlargest(top_n).index
    
    # Filtra o DataFrame original para obter apenas os dados dos mais ativos
    most_active_df = df[df['Id'].isin(most_active_users_ids)]
    
    # Calcula a média de calorias para esses usuários
    average_calories = most_active_df['Calories'].mean()
    
    return average_calories