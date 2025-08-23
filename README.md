# Análise de Dados Fitness com Streamlit (Fitbit)

Dashboard interativo para análise exploratória de dados do Fitbit, classificação de atividade de usuários e visualização de padrões de saúde, utilizando Streamlit e Scikit-learn.

📖 **Documentação**

A documentação completa do projeto, incluindo a análise exploratória inicial (EDA), detalhes do modelo e arquitetura, está na pasta `docs/`:

  * Análise Exploratória de Dados (EDA)
  * Arquitetura do Projeto
  * Treinamento do Modelo de Classificação
  * Governança de Dados
  * Testes
  * Deploy

🖥️ **Como rodar o projeto no Visual Studio Code**

**1. Abrir o projeto**

  * Abra o **VS Code**.
  * Vá em `File` → `Open Folder` e escolha a pasta do seu projeto, por exemplo, `fitbit_streamlit_analysis/`.

**2. Criar e ativar ambiente virtual**

No terminal integrado do VS Code (`Ctrl`+`'`):

```bash
# Criar ambiente virtual
python3 -m venv .venv

# Ativar no Linux/Mac
source .venv/bin/activate

# Ativar no Windows (PowerShell)
.venv\Scripts\Activate.ps1
```

⚠️ **Importante:** No canto inferior direito do VS Code, clique para selecionar o interpretador Python e escolha a opção que aponta para a pasta `.venv`.

**3. Instalar dependências**

Com o ambiente virtual já ativo no terminal:

```bash
pip install -r requirements.txt
```

**4. Rodar o Streamlit**

Ainda no terminal do VS Code:

```bash
streamlit run app/dashboard.py
```

O aplicativo será aberto automaticamente no seu navegador, no endereço `http://localhost:8501`.

**5. Trabalhar com o código**

  * **Front-end:** `app/dashboard.py` (contém a interface do usuário criada com Streamlit).
  * **Back-end:** `core/` (módulos para carregamento de dados, processamento, treinamento e avaliação do modelo).
  * **Notebooks:** `notebooks/01_eda_fitbit.ipynb` (contém a análise exploratória inicial dos dados).

**6. Rodar testes**

Para garantir a qualidade e o funcionamento do código:

```bash
pytest tests/
```

📂 **Estrutura de pastas**

```
fitbit-streamlit-analysis/
├─ app/            # Interface com o usuário (Streamlit Dashboard)
├─ core/           # Lógica de negócio (dados, features, modelo)
├─ configs/        # Arquivos de configuração
├─ data/           # Dados brutos, processados e modelos salvos (.pkl)
├─ notebooks/      # Notebooks de exploração e análise (EDA)
├─ tests/          # Testes unitários e de integração
├─ docs/           # Documentação detalhada do projeto
├─ requirements.txt
└─ README.md
```

🚀 **Deploy**

Para publicar seu dashboard na web, consulte o guia em `docs/deploy.md`.
