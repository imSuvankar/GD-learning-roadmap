
import pandas as pd
import sqlite3
import re, os
import seaborn as sns
import matplotlib.pyplot as plt
from google import genai
from dotenv import load_dotenv
load_dotenv()

LLM_MODEL = os.getenv('LLM_MODEL')

# ---------------------------
# 📦 Load CSV Data
# ---------------------------
def load_csv_data(data_path: str) -> dict:
    """Load all CSV files from the data folder as pandas DataFrames."""
    tables = {}
    for file in os.listdir(data_path):
        if file.endswith(".csv"):
            name = file.replace(".csv", "")
            tables[name] = pd.read_csv(f"{data_path}/{file}")
    return tables


# ---------------------------
# 🧩 Create SQLite Database
# ---------------------------
def initialize_database(tables: dict):
    """Create an in-memory SQLite DB from given pandas DataFrames."""
    conn = sqlite3.connect(":memory:")
    for name, df in tables.items():
        df.to_sql(name, conn, index=False, if_exists="replace")
    return conn


# ---------------------------
# 🧠 SQL Guardrails
# ---------------------------
def is_safe_query(sql: str) -> bool:
    """Block dangerous SQL commands."""
    forbidden = ["drop", "delete", "update", "insert", "alter", "system", "schema"]
    return not any(re.search(rf"\b{kw}\b", sql.lower()) for kw in forbidden)


# ---------------------------
# 🤖 Generate SQL via Gemini
# ---------------------------
def generate_sql_from_prompt(prompt: str, tables: dict, ddl_schema: str):
    """Convert natural language question → SQL query using Gemini."""
    try:
        client = genai.Client()
        available_tables = ", ".join(tables.keys())
        schema_section = f"\n\nHere is the SQL schema for your database:\n{ddl_schema}\n" if ddl_schema else ""
        llm_prompt = f"""
            Convert this question into a valid SQLite SQL query.
            Only use these tables: {available_tables}.
            {schema_section}
            Avoid destructive queries. Make sure to complete the full query always.
            Question: {prompt}
        """
        response = client.models.generate_content(
            model=LLM_MODEL,
            contents=llm_prompt,
            config={"temperature": 0.3, "max_output_tokens": 500},
        )
        sql_query = response.text.strip() if response and response.text else ""

        if not is_safe_query(sql_query):
            return None, "⚠️ Unsafe query detected — blocked for safety."

        return sql_query, None
    except Exception as e:
        import traceback
        traceback.print_exc()
        return None, f"Error generating SQL: {e}"


# ---------------------------
# 🧮 Execute SQL on SQLite
# ---------------------------
def execute_sql_query(sql_query: str, conn):
    """Execute SQL safely and return DataFrame result."""
    try:
        if not sql_query or not isinstance(sql_query, str) or not sql_query.strip():
            return None, "SQL Execution Error: No valid SQL query provided."
        # Clean SQL before execution
        raw_sql = clean_sql(sql_query)
        if not raw_sql:
            return None, "SQL Execution Error: Cleaned SQL query is empty."
        df = pd.read_sql_query(raw_sql, conn)

        if df is None:
            return None, "SQL Execution Error: Query returned no results."

        # # Optional: mask PII (emails)
        # df = df.replace(
        #     to_replace=r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b",
        #     value="[EMAIL]",
        #     regex=True
        # )
        return df, None
    except Exception as e:
        return None, f"SQL Execution Error: {e}"


# ---------------------------
# 📊 Visualization Logic
# ---------------------------
def detect_visualization_request(prompt: str) -> bool:
    """Detect if the user asked for a plot or chart."""
    keywords = ["plot", "chart", "graph", "visualize", "bar", "line"]
    return any(word in prompt.lower() for word in keywords)

def plot_result(result_df: pd.DataFrame):
    """Plot result using Seaborn if suitable columns exist."""
    try:
        if result_df.shape[1] < 2: return None

        fig, ax = plt.subplots(figsize=(6, 4))
        sns.barplot(x=result_df.columns[0], y=result_df.columns[1], data=result_df, ax=ax)
        plt.xticks(rotation=45)
        plt.tight_layout()
        return fig
    except Exception:
        return None

# ---------------------------
# 🧹 Clean SQL
# ---------------------------
def clean_sql(sql):
    sql = re.sub(r"```[a-zA-Z]*", "", sql)
    sql = sql.replace("```", "")
    return sql.strip()
