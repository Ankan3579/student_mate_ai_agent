from typing import TypedDict,Dict,Annotated
from langgraph.graph.message import add_messages

class State(TypedDict,total=False):
   
    user_query:str
    user_query_type:str=" "
    college_name:str
    semister:str=" "
    fees_result:str
    academic_result:str
    placement_result:str
    general_result:str
    input_guardrails_result:bool
    output_guardrails_result:bool
    final_response:str
    messages:Annotated[list,add_messages]