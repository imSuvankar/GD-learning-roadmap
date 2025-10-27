import streamlit as st

st.set_page_config(
    page_title="Home Page",
    page_icon="👋",
    layout="wide"
)

st.sidebar.success("Select a demo above.")

st.markdown(
    """
    ## 📝 GenAI Course Demo: User Guide

    Welcome to the [Prompt Engineering & AI Applications](https://learning.griddynamics.com/#/online-course-player/46d7924b-6020-4dbd-ac8b-f2e92cb6a3ca) Demo! 
    
    Please read these instructions carefully before using the app.


    ---

    ### 🚦 How to Use This App
    1. **Data Generation Tab**
        - Upload a valid DDL file (`.ddl`) describing your database schema.
        - Enter a prompt describing the kind of data you want to generate.
        - Adjust temperature and max tokens as needed.
        - Click **Generate Data** to create sample CSV files for each table in your schema.
        - Preview generated tables and download CSVs as needed.
        - Use the **Modification Prompt** to apply changes to all tables at once (e.g., add columns, update values, etc.).
        - After modification, all tables will be updated and saved automatically.

    2. **Talk to Your Data Tab**
        - This section is only available if both a DDL file is present in the `schema` folder and at least one CSV file is present in the `data` folder.
        - Ask questions about your data in natural language.
        - The app will generate SQL queries, execute them, and display results.
        - If your prompt requests a plot or chart, the app will attempt to visualize the results.

    ---

    ### 📂 What to Upload
    - **DDL File:** Must be a valid SQL DDL file defining all tables and relationships.
    - **No Data?** Use the Data Generation tab to create sample data from your DDL.
    - **No DDL?** You must upload a DDL file to use the app.

    ---

    ### ⚠️ Restrictions & Requirements
    - Only `.ddl` files are accepted for schema upload.
    - The app expects standard SQL DDL syntax.
    - Data generation and modification are powered by an LLM (Gemini). Output may vary based on prompt clarity.
    - Modifications apply to **all tables** at once; review changes before proceeding.
    - The chat feature is disabled unless both schema and data are present.
    - Large or complex schemas may result in longer processing times or LLM errors.
    - **Do NOT** keep more than one DDL file in the `schema` folder at a time. The app will only use the first DDL file it finds, but having multiple may confuse the LLM and cause unpredictable results.
    - If there are multiple DDL files or CSVs from different DDLs in the `data` folder, the LLM may mix contexts and generate incorrect or inconsistent data/answers.
    - **Recommended:** Before running the app or uploading a new DDL file, ensure both the `schema` and `data` folders are completely empty.
    - If you want to use a different DDL file (with different content that will create different CSV files), **delete all previous files** from both folders before proceeding.
    
    ---

    ### 💡 Tips & Best Practices
    - Use clear, specific prompts for both data generation and modification.
    - Download your CSVs after generation for backup.
    - If you encounter errors, check your DDL syntax and prompt clarity.
    - Use the **Data Generation** tab to reset or regenerate your data at any time.

    ---

    ### 🤔 What to Expect
    - **Data Generation:** The app will create sample data for each table in your schema, saved as CSV files in the `data` folder.
    - **Modification:** All tables will be updated based on your modification prompt and saved automatically.
    - **Chat:** You can ask questions about your data, get SQL queries, and see results/plots if both schema and data are present.
    - **Error Handling:** The app will display clear error messages for missing files, invalid input, or LLM issues.

    ---

    ### 📎 Additional Notes
    - All files are stored locally in the `schema` and `data` folders.
    - The app does **not** persist data between restarts unless files are saved in these folders.
    - For best results, use Chrome or Edge browsers.
    - For support, refer to the course documentation or contact the course instructor.
    - For questions related to this demo, reach out to `sudas@griddynamics.com`

    """
)