from state.state import State
from config import LLM
def classifier_agent(state:State):
    """ look the latest user message or query and decide which path to take."""
    user_query = state['user_query']

    prompt = f"""
                classify the following student query into exactly one category:"
                'accademic' ,'fees' , 'placement' , 'general'.

                use 'accademic' if user asks about attendence , exams , credits,sgpa , cgpa etc you could decide.

                use 'fee' for questions about tution fees , payment , refund , late charges .
                
                use 'placement' if user asks to know about placement data related query.
                
                use 'general' if user asks to about college related other information example : play , infrustrucure , events etc. 

                messages : {user_query}

return only one word : accademic , fees, placement, general
"""
    response = LLM.invoke(prompt)
    category = response.content.strip().lower()

    if "accademic" in category:
        category="accademic"
    elif "fees" in category:
        category="fees"
    elif "placement" in category:
        category="placement"
    else:
        category="general"

    return {"user_query_type" : category}
    
