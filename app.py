import streamlit as st
import pandas as pd
import os
from dotenv import load_dotenv

# 1. Load the API key into the environment FIRST
load_dotenv()
from core.graph import app_graph
from core.state import AutoAnalystState

# --- UI Configuration ---
st.set_page_config(page_title="Auto-Analyst AI", layout="wide")
st.title("🤖 Autonomous Data Science Agent")
st.markdown("Upload a dataset and let the agent autonomously plan, write code, and execute an EDA pipeline.")

# --- Ensure Directories Exist ---
os.makedirs("data", exist_ok=True)
os.makedirs("artifacts", exist_ok=True)

# --- File Uploader ---
uploaded_file = st.file_uploader("Upload a CSV dataset", type=["csv"])

if uploaded_file:
    # 1. Save the file locally so the execution engine can read it
    file_path = os.path.join("data", uploaded_file.name)
    with open(file_path, "wb") as f:
        f.write(uploaded_file.getbuffer())
    
    # 2. Extract schema for the LLM Planner
    df = pd.read_csv(file_path)
    schema = f"Columns: {df.columns.tolist()}\n\nSample Data:\n{df.head(3).to_markdown()}"
    
    st.write("### Dataset Preview")
    st.dataframe(df.head())

    # 3. User Query Input
    user_query = st.text_input(
        "What do you want to analyze?", 
        "Perform a comprehensive exploratory data analysis, handle missing values, and generate visual distributions of key metrics."
    )

    if st.button("Run Autonomous Analysis"):
        with st.spinner("Agent is planning, coding, and executing..."):
            
            # Clear old artifacts to avoid mixing previous run images
            for file in os.listdir("artifacts"):
                os.remove(os.path.join("artifacts", file))

            # Initialize the state
            initial_state: AutoAnalystState = {
                "dataset_path": file_path,
                "dataset_schema": schema,
                "user_query": user_query,
                "plan": "",
                "current_code": "",
                "execution_history": [],
                "latest_error": None,
                "retry_count": 0,
                "final_report": ""
            }
            
            # Run the LangGraph state machine
            result = app_graph.invoke(initial_state)
            
            st.success("Analysis Complete!")
            
            # --- Display Results ---
            col1, col2 = st.columns(2)
            
            with col1:
                st.subheader("💻 Generated Python Code")
                st.code(result.get("current_code", ""), language="python")
                
                st.subheader("🖥️ Console Output")
                if result.get("execution_history"):
                    st.text(result["execution_history"][-1]["output"])
                
                if result.get("latest_error"):
                    st.error(f"Final Error State: {result['latest_error']}")
                
                # --- ADD THESE THREE LINES ---
                st.subheader("📝 Executive Summary")
                if result.get("final_report"):
                    st.markdown(result["final_report"])
            
            with col2:
                st.subheader("📊 Generated Artifacts")
                artifact_files = [f for f in os.listdir("artifacts") if f.endswith(".png")]
                
                if not artifact_files:
                    st.info("No visual artifacts were generated during this run.")
                
                for file in artifact_files:
                    st.image(os.path.join("artifacts", file))