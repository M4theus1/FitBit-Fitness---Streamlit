# main.py
from app.database import create_database_and_tables, insert_csv_to_sor, run_etl_sor_to_sot, run_etl_sot_to_spec_train
import pandas as pd

if __name__ == "__main__":
    print("Criando banco de dados Fitbit...")
    create_database_and_tables()

    print("Carregando dados CSV...")
    df = pd.read_csv("data/dailyActivity_merged.csv")
    insert_csv_to_sor(df)

    print("Executando ETL...")
    run_etl_sor_to_sot()
    run_etl_sot_to_spec_train()

    print("✅ Banco e dados prontos para análise.")
    print("Agora execute:  streamlit run app/interface_streamlit.py")
