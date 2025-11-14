# core/chatbot/rag.py
import os
from dotenv import load_dotenv
load_dotenv()
from openai import OpenAI
import pandas as pd
from core.data.database import connect_db
from core.chatbot.rules import answer_from_metrics

try:
    from openai import OpenAI
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    OPENAI_AVAILABLE = True
except Exception:
    client = None
    OPENAI_AVAILABLE = False


def retrieve_context_from_db(question: str) -> str:
    """Busca dados relevantes no SQLite com base na pergunta (com detecção automática da coluna de ID)."""
    conn = connect_db()
    q = question.lower()

    try:
        # Detecta o nome correto da coluna de ID
        table_info = pd.read_sql_query("PRAGMA table_info(spec_daily_activity_train)", conn)
        possible_ids = ["id", "Id", "user_id", "UserId", "userid"]
        id_col = next((c for c in table_info["name"] if c in possible_ids), None)

        if not id_col:
            return "Não foi possível identificar a coluna de identificação do usuário na tabela."

        # 🔹 Perguntas sobre calorias por usuário
        if "usuário" in q and "caloria" in q:
            query = f"""
                SELECT {id_col} AS Id, AVG(calories) AS AvgCalories, AVG(totalsteps) AS AvgSteps
                FROM spec_daily_activity_train
                GROUP BY {id_col}
                ORDER BY AvgCalories DESC
                LIMIT 5
            """
            df = pd.read_sql_query(query, conn)

        # 🔹 Perguntas sobre atividades e passos
        elif "atividade" in q or "passo" in q:
            query = f"""
                SELECT
                    {id_col} AS Id,
                    AVG(veryactiveminutes) AS AvgVeryActive,
                    AVG(fairlyactiveminutes) AS AvgFairlyActive,
                    AVG(lightlyactiveminutes) AS AvgLightlyActive,
                    AVG(sedentaryminutes) AS AvgSedentary,
                    AVG(calories) AS AvgCalories
                FROM spec_daily_activity_train
                GROUP BY {id_col}
                LIMIT 5
            """
            df = pd.read_sql_query(query, conn)

        # 🔹 Caso não encontre contexto
        else:
            return "Sem contexto numérico relevante para essa pergunta."

        return df.to_markdown(index=False) if not df.empty else "Nenhum dado encontrado no banco."

    except Exception as e:
        return f"Erro ao consultar banco: {e}"

    finally:
        conn.close()

def generate_rag_answer(question: str, context: str) -> str:
    """Gera resposta usando a API da OpenAI (se disponível)."""
    if not OPENAI_AVAILABLE or not os.getenv("OPENAI_API_KEY"):
        return "API da OpenAI não configurada. Forneça a variável OPENAI_API_KEY."

    prompt = f"""
    Você é um analista de dados Fitbit.
    Use o contexto abaixo para responder de forma analítica e concisa.

    Contexto:
    {context}

    Pergunta:
    {question}

    Responda mencionando números e insights dos dados.
    """

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.3,
    )
    return response.choices[0].message.content


def rag_pipeline(question: str, metrics=None, importances=None):
    """Orquestra a resposta RAG (regras + contexto + IA)."""

    metrics_df_or_dict = metrics if metrics is not None else {}
    importances_df = importances if importances is not None else pd.DataFrame()

    base_answer = answer_from_metrics(
        question,
        task="previsão de calorias",
        metrics_df_or_dict=metrics_df_or_dict,
        importances_df=importances_df,
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

