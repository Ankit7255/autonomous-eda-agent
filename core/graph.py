from google import genai
from langgraph.graph import StateGraph, END
from core.state import AutoAnalystState
from core.prompts import PLANNER_PROMPT, build_coder_prompt, REPORTER_PROMPT
from core.executor import execute_generated_code

# Mock function for now - we will build the real Gemini integration next
# Initialize the client. It automatically detects GEMINI_API_KEY from your environment.
client = genai.Client()

def call_gemini(prompt: str) -> str:
    """Calls the Gemini model for reasoning and coding."""
    try:
        response = client.models.generate_content(
            model='gemini-3.1-flash-lite', 
            contents=prompt,
        )
        return response.text
    except Exception as e:
        print(f"API Error: {e}")
        return ""

MAX_RETRIES = 3

def planner_node(state: AutoAnalystState) -> dict:
    prompt = PLANNER_PROMPT.format(
        dataset_schema=state.get("dataset_schema", ""),
        user_query=state.get("user_query", "")
    )
    plan = call_gemini(prompt)
    return {"plan": plan, "retry_count": 0, "latest_error": None}

def coder_node(state: AutoAnalystState) -> dict:
    prompt = build_coder_prompt(state)
    code = call_gemini(prompt)
    
    # Clean up markdown code blocks if the LLM hallucinated them
    code = code.replace("```python", "").replace("```", "").strip()
    return {"current_code": code}

def executor_node(state: AutoAnalystState) -> dict:
    code = state["current_code"]
    result = execute_generated_code(code, state["dataset_path"])
    
    # Format as a list to append to the Annotated state history
    history_entry = [{
        "code": code,
        "output": result["output"],
        "error": result["error"]
    }]
    
    return {
        "latest_error": result["error"],
        "execution_history": history_entry,
        "retry_count": state.get("retry_count", 0) + 1
    }

def route_execution(state: AutoAnalystState) -> str:
    """Conditional router: decides whether to self-correct or finish."""
    if state.get("latest_error"):
        if state.get("retry_count", 0) >= MAX_RETRIES:
            return "fail"
        return "reflect"
    return "success"

def reporter_node(state: AutoAnalystState) -> dict:
    """Synthesizes the raw execution output into a final Markdown report."""
    if not state.get("execution_history"):
        return {"final_report": "No execution data available to report."}
        
    last_output = state["execution_history"][-1]["output"]
    prompt = REPORTER_PROMPT.format(
        user_query=state.get("user_query", ""),
        console_output=last_output
    )
    
    report = call_gemini(prompt)
    return {"final_report": report}

# --- Build the LangGraph ---
workflow = StateGraph(AutoAnalystState)

# 1. Add all nodes to the graph
workflow.add_node("planner", planner_node)
workflow.add_node("coder", coder_node)
workflow.add_node("executor", executor_node)
workflow.add_node("reporter", reporter_node) # <-- ADDED THIS LINE

# 2. Define the starting point and standard edges
workflow.set_entry_point("planner")
workflow.add_edge("planner", "coder")
workflow.add_edge("coder", "executor")

# 3. Define the conditional routing logic
workflow.add_conditional_edges(
    "executor",
    route_execution,
    {
        "reflect": "coder",     # Loop back to fix the code
        "success": "reporter",  # <-- CHANGED 'END' TO 'reporter'
        "fail": END             # Stop if we exceed max retries
    }
)

# 4. End the graph after the report is generated
workflow.add_edge("reporter", END) # <-- ADDED THIS LINE

# Compile the graph into an executable application
app_graph = workflow.compile()