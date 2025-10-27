import streamlit as st
import pandas as pd
import os
from utils.talk_to_your_data_service import (
    initialize_database,
    load_csv_data,
    generate_sql_from_prompt,
    execute_sql_query,
    detect_visualization_request,
    plot_result
)

# ---------------------------
# 🎯 Page Setup
# ---------------------------
st.set_page_config(page_title="Talk to your data", layout="wide")
st.markdown("## Talk to your data:")

# ---------------------------
# ⚙️ Load CSVs from data/
# ---------------------------
if "tables" not in st.session_state:
    st.session_state["tables"] = {}

if not st.session_state["tables"]:
    data_path = "data"
    if not os.path.exists(data_path):
        st.error("No data found! Please generate data first.")
        st.stop()

    st.session_state["tables"] = load_csv_data(data_path)
    st.success(f"Loaded {len(st.session_state['tables'])} tables from `data` directory")


# Read DDL schema from schema/ folder if present
schema_dir = "schema"
ddl_files = [f for f in os.listdir(schema_dir)] if os.path.exists(schema_dir) else []
ddl_schema = ""
if ddl_files:
    ddl_path = os.path.join(schema_dir, ddl_files[0])
    with open(ddl_path, "r", encoding="utf-8") as f:
        ddl_schema = f.read()

# Create SQLite in-memory database
conn = initialize_database(st.session_state["tables"])

# ---------------------------
# 💬 Chat UI
# ---------------------------
if "chat_history" not in st.session_state:
    st.session_state["chat_history"] = []


# Display existing messages
for msg in st.session_state["chat_history"]:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# Only show chat input if both a DDL file and at least one CSV file exist
ddl_exists = bool(ddl_files)
csv_exists = bool(st.session_state["tables"])
if ddl_exists and csv_exists:
    prompt = st.chat_input("Ask a question about your data...")
else:
    prompt = None
    st.info(
        """
        Please ensure both a DDL file is present in the 'schema' folder and at least one CSV file is present in the 'data' folder to use the chat.

        You can use the **Data Generation** tab to upload a DDL file and create other necessary files.
        """
    )

# ---------------------------
# 🚀 Process Prompt
# ---------------------------
if prompt:
    st.chat_message("user").markdown(prompt)
    st.session_state["chat_history"].append({"role": "user", "content": prompt})

    with st.chat_message("assistant"):
        with st.spinner("Analyzing your data..."):
            sql_query, error = generate_sql_from_prompt(prompt, st.session_state["tables"], ddl_schema=ddl_schema)

            if error:
                st.error(error)
                st.session_state["chat_history"].append({"role": "assistant", "content": f"❌ {error}"})
            else:
                st.code(sql_query, language="sql")

                result_df, error = execute_sql_query(sql_query, conn)
                if error:
                    st.error(error)
                    st.session_state["chat_history"].append({"role": "assistant", "content": f"❌ {error}"})
                else:
                    st.dataframe(result_df.head(), hide_index=True)

                    # Save in chat history
                    chat_text = f"```sql\n{sql_query}\n```\n\n{result_df.head().to_markdown(index=False)}"
                    st.session_state["chat_history"].append({"role": "assistant", "content": chat_text})

                    # Plot if relevant
                    if detect_visualization_request(prompt):
                        st.write("📊 Visualization")
                        fig = plot_result(result_df)
                        if fig:
                            st.pyplot(fig)
                        else:
                            st.info("Not enough numeric columns to plot.")
