import pandas as pd
import os  # Adicionar esta linha

def load_daily_activity(path="data/dailyActivity_merged.csv"):
    """
    Carrega e pré-processa o dataset dailyActivity_merged.csv.
    """
    try:
        # Verifica se o arquivo existe
        if not os.path.exists(path):
            print(f"Erro: O arquivo não foi encontrado no caminho '{path}'")
            return None
        
        # Verifica se o arquivo não está vazio
        if os.path.getsize(path) == 0:
            print(f"Erro: O arquivo '{path}' está vazio")
            return None
        
        # Tenta carregar o CSV com diferentes encodings
        encodings = ['utf-8', 'latin-1', 'iso-8859-1', 'cp1252']
        
        for encoding in encodings:
            try:
                df = pd.read_csv(path, encoding=encoding)
                # Verifica se o DataFrame não está vazio
                if df.empty:
                    print(f"Aviso: DataFrame vazio com encoding {encoding}")
                    continue
                    
                # Tenta converter a coluna de data
                try:
                    df['ActivityDate'] = pd.to_datetime(df['ActivityDate'], format='%Y-%m-%d %H:%M:%S')
                except (ValueError, KeyError):
                    try:
                        df['ActivityDate'] = pd.to_datetime(df['ActivityDate'], format='%Y-%m-%d')
                    except (ValueError, KeyError):
                        try:
                            df['ActivityDate'] = pd.to_datetime(df['ActivityDate'], format='%m/%d/%Y')
                        except (ValueError, KeyError):
                            df['ActivityDate'] = pd.to_datetime(df['ActivityDate'], errors='coerce')
                
                print(f"Arquivo carregado com sucesso usando encoding: {encoding}")
                return df
                
            except (pd.errors.EmptyDataError, UnicodeDecodeError) as e:
                print(f"Falha com encoding {encoding}: {e}")
                continue
            except Exception as e:
                print(f"Erro inesperado com encoding {encoding}: {e}")
                continue
        
        print("Todos os encodings falharam. Tentando carregar sem especificar encoding...")
        try:
            df = pd.read_csv(path)
            if not df.empty:
                # Tenta converter a data
                try:
                    df['ActivityDate'] = pd.to_datetime(df['ActivityDate'], errors='coerce')
                except KeyError:
                    print("Coluna 'ActivityDate' não encontrada no arquivo")
                
                return df
            else:
                print("DataFrame ainda está vazio")
                return None
        except Exception as e:
            print(f"Erro final ao tentar carregar arquivo: {e}")
            return None
            
    except FileNotFoundError:
        print(f"Erro: O arquivo não foi encontrado no caminho '{path}'")
        return None
    except Exception as e:
        print(f"Erro inesperado ao carregar arquivo: {e}")
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