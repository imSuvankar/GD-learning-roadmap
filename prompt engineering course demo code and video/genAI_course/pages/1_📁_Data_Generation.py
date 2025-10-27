import streamlit as st
import time
import pandas as pd
import json
import os
from utils.data_generation_service import generate_from_ddl


st.set_page_config(page_title="Data Generation", layout="wide")
st.markdown("## Enter Details:")

input_prompt = st.text_input("Prompt", placeholder="Enter your prompt here...")

ddl_file = st.file_uploader("Upload DDL file", type=["ddl"])
input_ddl_content = None
if ddl_file is not None:
	input_ddl_content = ddl_file.read().decode("utf-8")
	# Save uploaded file to schema/ folder
	os.makedirs("schema", exist_ok=True)
	file_path = os.path.join("schema", ddl_file.name)
	with open(file_path, "w", encoding="utf-8") as f:
		f.write(input_ddl_content)

col1, col2 = st.columns(2)
with col1: input_temperature = st.slider("Temperature", min_value=0.1, max_value=1.0, value=0.5)
with col2: input_max_tokens = st.number_input("Max tokens (maximum 2000)", min_value=10, max_value=2000, value=1000)


# --- CSV Table and Dropdown UI ---
data_dir = "data"
os.makedirs(data_dir, exist_ok=True)
csv_files = [f for f in os.listdir(data_dir) if f.endswith(".csv")]

# --- Gemini Generation ---
if st.button("Generate Data", type="secondary", key="generate_button") and input_ddl_content and input_prompt:
	result = generate_from_ddl(
		ddl_content=input_ddl_content,
		user_prompt=input_prompt,
		temperature=input_temperature,
		max_tokens=int(input_max_tokens)
	)
	# Try to parse the result as JSON and store as DataFrames in session_state
	try:
		response_json = json.loads(result)
		# Save new tables as CSV files
		for name, rows in response_json.items():
			df = pd.DataFrame(rows)
			file_path = os.path.join(data_dir, f"{name}.csv")
			df.to_csv(file_path, index=False)
		st.success("✅ All tables saved successfully to the 'data' folder!")
		st.rerun()  # Refresh to show new files in dropdown and preview
	except Exception as e:
		st.error(f"Failed to parse Gemini output as JSON or save CSV: {e}")



# ---------------------------------
st.divider()
# ---------------------------------


# If there are CSV files, load them into DataFrames
csv_tables = {}
for f in csv_files:
	try:
		df = pd.read_csv(os.path.join(data_dir, f))
		csv_tables[f] = df
	except Exception: pass


# Show only table names (no .csv extension) in dropdown, formatted for readability
def format_table_name(name):
	return name.replace('_', ' ').title()
raw_table_names = [f[:-4] if f.endswith('.csv') else f for f in csv_files]
table_names = [format_table_name(n) for n in raw_table_names]
table_name_to_file = {format_table_name(n): f for n, f in zip(raw_table_names, csv_files)}

col_left, col_right = st.columns([3, 1])
with col_left:
    st.markdown(f"## Data Preview:")
with col_right:
    selected_table_name = st.selectbox("Select Table", options=table_names, index=0 if table_names else None, key="csv_selector")

if selected_table_name:
    selected_csv = table_name_to_file[selected_table_name]
    df_to_display = csv_tables[selected_csv]
    def sophisticated_header(col):
        return col.replace('_', ' ').title()
    df_display = df_to_display.rename(columns={col: sophisticated_header(col) for col in df_to_display.columns})
    st.dataframe(df_display, hide_index=True)
else:
    st.info("No table is present to preview.")



# ---------------------------------
st.divider()
# ---------------------------------




st.markdown("## Data Modification (All Tables):")

if not table_names:
	st.info("No tables are present to modify.")
else:
	mod_prompt = st.text_input(
		"Modification Prompt",
		placeholder="Describe how you want to modify ALL tables (e.g., add a column, update values, etc.)..."
	)
	# Inline button and success message row
	col_mod_btn, col_mod_msg = st.columns([1, 3])
	if 'mod_success' not in st.session_state:
		st.session_state['mod_success'] = False
	if 'mod_error' not in st.session_state:
		st.session_state['mod_error'] = ''
	with col_mod_btn:
		mod_clicked = st.button("Modify All Tables", key="modify_all_button")
	if mod_clicked and mod_prompt:
		# Prepare all tables' data as JSON
		all_tables_data = {k[:-4] if k.endswith('.csv') else k: v.to_dict(orient="records") for k, v in csv_tables.items()}
		try:
			mod_result = generate_from_ddl(
				ddl_content=json.dumps(all_tables_data),
				user_prompt=mod_prompt,
				temperature=input_temperature,
				max_tokens=int(input_max_tokens)
			)
			mod_json = json.loads(mod_result)
			if not isinstance(mod_json, dict):
				raise ValueError("LLM output is not a dict of tables. Raw output: " + str(mod_json))
			# Save each table
			for name, rows in mod_json.items():
				if not isinstance(rows, list) or not all(isinstance(row, dict) for row in rows):
					raise ValueError(f"Table '{name}' is not a list of records. Raw: {rows}")
				# Optionally, check all dicts have the same keys
				keys = [set(row.keys()) for row in rows]
				if len(set(map(frozenset, keys))) > 1:
					raise ValueError(f"Not all records in table '{name}' have the same columns. Raw: {rows}")
				df_mod = pd.DataFrame(rows)
				file_path = os.path.join(data_dir, f"{name}.csv")
				df_mod.to_csv(file_path, index=False)
			st.session_state['mod_success'] = True
			st.session_state['mod_error'] = ''
			st.rerun()
		except Exception as e:
			st.session_state['mod_success'] = False
			st.session_state['mod_error'] = f"Failed to modify tables: {e}\nRaw LLM output: {mod_result if 'mod_result' in locals() else ''}"
	with col_mod_msg:
		if st.session_state.get('mod_success'):
			# Show success message for 10 seconds, then rerun
			st.success("✅ All tables modified and saved!")
			time.sleep(10)
			st.session_state['mod_success'] = False
			st.rerun()
		elif st.session_state.get('mod_error'):
			st.error(st.session_state['mod_error'])

