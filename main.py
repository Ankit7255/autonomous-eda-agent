from dotenv import load_dotenv
load_dotenv()
# arti/main.py
from core.graph import app_graph
from core.state import AutoAnalystState

def test_pipeline():
    print("Initializing test run for AutoAnalyst...")
    
    initial_state: AutoAnalystState = {
        "dataset_path": "data/sample.csv",
        "dataset_schema": "Columns: [age, salary, department]",
        "user_query": "Find the average salary per department and plot the distribution.",
        "plan": "",
        "current_code": "",
        "execution_history": [],
        "latest_error": None,
        "retry_count": 0,
        "final_report": ""
    }
    
    # Run a test pass through the graph
    result = app_graph.invoke(initial_state)
    print("Execution completed successfully!")
    print("Current Code Generated:\n", result.get("current_code"))

if __name__ == "__main__":
    test_pipeline()