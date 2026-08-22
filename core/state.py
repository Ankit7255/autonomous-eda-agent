from typing import TypedDict, List, Dict, Optional, Annotated
import operator

# Define the state schema using TypedDict
class AutoAnalystState(TypedDict):
    """
    State schema for the Autonomous EDA Agent.
    """
    dataset_path: str
    dataset_schema: str  # e.g., df.head().to_markdown() and df.info()
    user_query: str
    plan: str
    current_code: str
    # Using Annotated and operator.add to append to the history list automatically
    execution_history: Annotated[List[Dict[str, str]], operator.add] 
    latest_error: Optional[str]
    retry_count: int
    final_report: str