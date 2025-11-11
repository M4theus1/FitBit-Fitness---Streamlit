# app/analysis.py
import pandas as pd

def answer_from_metrics(question: str, task: str, metrics_df_or_dict, importances_df):
    """
    Responde a perguntas do usuário com base nas métricas do modelo,
    importâncias de variáveis e contexto do Fitbit Fitness Tracker Data.
    """
    q = (question or "").lower()
    ...
