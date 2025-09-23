def answer_from_metrics(question: str, task: str, metrics_df_or_dict, importances_df):
    """
    Responde a perguntas do usuário com base nas métricas do modelo,
    importâncias de variáveis e contexto do Fitbit Fitness Tracker Data.
    """
    q = (question or "").lower()

    # Variáveis mais influentes
    if "importan" in q or "importân" in q or "variáve" in q or "features" in q:
        if importances_df is not None and not importances_df.empty:
            top = importances_df.head(5)[["feature"]].to_dict("records")
            top_str = ", ".join([t["feature"] for t in top])
            return f"No modelo de {task}, as variáveis mais influentes foram: {top_str}. (Com base nos coeficientes do modelo)"
        else:
            return "Ainda não tenho dados de importância das variáveis para mostrar."

    # Métricas de avaliação
    if "métric" in q or "score" in q or "acur" in q or "rmse" in q or "erro" in q:
        return f"As métricas do modelo de {task} foram: {metrics_df_or_dict}"

    # Perguntas sobre o pipeline
    if "como foi treinado" in q or "pipeline" in q or "treinament" in q:
        return (
            "O pipeline aplicado neste projeto inclui:\n"
            "- Tratamento de valores ausentes (imputação)\n"
            "- Codificação one-hot para variáveis categóricas\n"
            "- Padronização dos dados numéricos\n"
            "- Treinamento usando um modelo de Regressão Linear para prever calorias gastas"
        )

    # Perguntas sobre privacidade
    if "privacid" in q or "lgpd" in q or "dados sensívei" in q:
        return (
            "O dataset do Fitbit não contém dados pessoais identificáveis. "
            "Em um ambiente real, seguiríamos a LGPD, garantindo consentimento expresso, "
            "minimização de dados e rastreabilidade de acessos."
        )

    # Perguntas típicas sobre usuários mais ativos
    if "usuário" in q and ("ativo" in q or "ativos" in q):
        return (
            "Os usuários mais ativos foram identificados com base nos maiores valores de "
            "TotalSteps e VeryActiveMinutes. Em geral, esses usuários também apresentam "
            "maior gasto calórico médio."
        )

    # Perguntas sobre calorias
    if "caloria" in q or "gasto energét" in q:
        return (
            "O gasto calórico no Fitbit é fortemente influenciado pelos minutos em atividade "
            "muito intensa (VeryActiveMinutes), pela quantidade total de passos (TotalSteps) "
            "e pela distância percorrida (TotalDistance)."
        )

    return "Desculpe, não entendi. Você pode perguntar sobre variáveis importantes, métricas, pipeline ou usuários mais ativos."
