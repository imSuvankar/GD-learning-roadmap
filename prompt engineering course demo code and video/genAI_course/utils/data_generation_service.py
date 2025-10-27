import os
from google import genai
from dotenv import load_dotenv
load_dotenv()

# GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')
LLM_MODEL = os.getenv('LLM_MODEL')
client = genai.Client()



def generate_from_ddl(ddl_content, user_prompt, temperature, max_tokens):
    prompt = f"""
    I have a DDL schema for a database, that contains different tables and their relationships.
    
    Here is how the schema looks:
    ```
    {ddl_content}
    ```

    Based on this schema, generate all the tables in a relational database along with sample data for each table.
    The system should generate consistent and valid data for the provided DDL schema (5-7 Tables) and instructions [data types, null values, date and time formats, primary and foreign keys, etc].
    In each table there should be minimum 5 records, maximum 10 records, or if the user specifies otherwise in the prompt.
    The output should be in JSON format with table names as keys and list of records as values.

    Like this example:
    {{
        "table_1": [
            {{"customer_id": 1, "name": "Alice", "email": "alice@example.com"}},
            {{"customer_id": 2, "name": "Bob", "email": "bob@example.com"}}
        ],
        "table_2": [
            {{"order_id": 10, "customer_id": 1, "amount": 120.50}},
            {{"order_id": 11, "customer_id": 2, "amount": 60.00}}
        ]
    }}

    And this is the user prompt to generate data:
    {user_prompt}
    """
    response = client.models.generate_content(
        model=LLM_MODEL,
        contents=prompt,
        config={
            "response_mime_type": "application/json",
            # "temperature": temperature,
            # "max_output_tokens": max_tokens
        }
    )
    return response.text