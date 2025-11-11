# app/rag.py
import os
import pandas as pd
from openai import OpenAI
from core.data.database import connect_db
from core.analysis.metrics import answer_from_metrics

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def retrieve_context_from_db(question: str):
    """Busca dados relevantes no SQLite com base na pergunta."""
    conn = connect_db()
    q = question.lower()

    # 🔹 1. Perguntas sobre usuários e calorias
    if "usuário" in q and "caloria" in q:
        query = """
        SELECT Id, AVG(Calories) AS AvgCalories, AVG(TotalSteps) AS AvgSteps
        FROM spec_daily_activity_train
        GROUP BY Id
        ORDER BY AvgCalories DESC
        LIMIT 5
        """
        try:
            df = pd.read_sql_query(query, conn)
        except Exception:
            # fallback: caso as colunas estejam em minúsculas
            query = """
            SELECT id AS Id, AVG(calories) AS AvgCalories, AVG(totalsteps) AS AvgSteps
            FROM spec_daily_activity_train
            GROUP BY id
            ORDER BY AvgCalories DESC
            LIMIT 5
            """
            df = pd.read_sql_query(query, conn)
        conn.close()
        return df.to_markdown(index=False)

    # 🔹 2. Perguntas sobre níveis de atividade (ajustada para usar VeryActiveMinutes)
    elif "atividade" in q or "passo" in q:
        query = """
        SELECT
            Id,
            AVG(VeryActiveMinutes) AS AvgVeryActive,
            AVG(FairlyActiveMinutes) AS AvgFairlyActive,
            AVG(LightlyActiveMinutes) AS AvgLightlyActive,
            AVG(SedentaryMinutes) AS AvgSedentary,
            AVG(Calories) AS AvgCalories
        FROM spec_daily_activity_train
        GROUP BY Id
        LIMIT 5
        """
        try:
            df = pd.read_sql_query(query, conn)
        except Exception:
            query = """
            SELECT
                id AS Id,
                AVG(veryactiveminutes) AS AvgVeryActive,
                AVG(fairlyactiveminutes) AS AvgFairlyActive,
                AVG(lightlyactiveminutes) AS AvgLightlyActive,
                AVG(sedentaryminutes) AS AvgSedentary,
                AVG(calories) AS AvgCalories
            FROM spec_daily_activity_train
            GROUP BY id
            LIMIT 5
            """
            df = pd.read_sql_query(query, conn)
        conn.close()
        return df.to_markdown(index=False)

    # 🔹 3. Caso não encontre contexto
    conn.close()
    return "Sem contexto numérico relevante para essa pergunta."

def generate_rag_answer(question: str, context: str):
    """Chama a API da OpenAI para gerar resposta contextualizada."""
    prompt = f"""
    Você é um analista de dados Fitbit. Responda com base no contexto a seguir.

    Contexto:
    {context}

    Pergunta:
    {question}

    Explique de forma clara, mencionando números ou comparações do contexto.
    """

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.3
    )
    return response.choices[0].message.content

def rag_pipeline(question):
    """Orquestra a resposta RAG (regras + contexto + IA)."""
    base_answer = answer_from_metrics(
        question,
        task="previsão de calorias",
        metrics_df_or_dict={},
        importances_df=pd.DataFrame()
    )
    context = retrieve_context_from_db(question)
    ai_answer = generate_rag_answer(question, context)

    return f"""
🧩 **Pergunta:** {question}

🔍 **Contexto (dados Fitbit):**
{context}

📊 **Resposta baseada em regras:**
{base_answer}

🤖 **Análise da OpenAI:**
{ai_answer}
"""
