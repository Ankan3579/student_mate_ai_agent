from langgraph.graph import StateGraph, START, END

from state.state import State

from agent.classifier_agent import classifier_agent
from agent.academic_agent import academic_agent
from agent.input_guardrails_agent import input_guardrails_agent
from agent.output_guardrails import output_guardrails_agent
from agent.general_agent import general_agent
from agent.placement_agent import placement_agent
from agent.fees_agent import fees_agent


# =========================================================
# CREATE GRAPH
# =========================================================

builder = StateGraph(State)


# =========================================================
# ADD NODES
# =========================================================

builder.add_node(
    "input_guardrails_agent",
    input_guardrails_agent
)

builder.add_node(
    "classifier_agent",
    classifier_agent
)

builder.add_node(
    "academic_agent",
    academic_agent
)

builder.add_node(
    "placement_agent",
    placement_agent
)

builder.add_node(
    "fees_agent",
    fees_agent
)

builder.add_node(
    "general_agent",
    general_agent
)

builder.add_node(
    "output_guardrails_agent",
    output_guardrails_agent
)


# =========================================================
# START → INPUT GUARDRAILS
# =========================================================

builder.add_edge(
    START,
    "input_guardrails_agent"
)


# =========================================================
# INPUT GUARDRAILS → CLASSIFIER
# =========================================================

builder.add_edge(
    "input_guardrails_agent",
    "classifier_agent"
)


# =========================================================
# ROUTING FUNCTION
# =========================================================

def route_query(state: State):

    query_type = state.get("user_query_type", [])

    if "fees" in query_type:
        return "fees_agent"

    elif "academic" in query_type:
        return "academic_agent"

    elif "placement" in query_type:
        return "placement_agent"

    else:
        return "general_agent"


# =========================================================
# CLASSIFIER → AGENT
# =========================================================

builder.add_conditional_edges(
    "classifier_agent",
    route_query,
    {
        "fees_agent": "fees_agent",
        "academic_agent": "academic_agent",
        "placement_agent": "placement_agent",
        "general_agent": "general_agent"
    }
)


# =========================================================
# AGENTS → OUTPUT GUARDRAILS
# =========================================================

builder.add_edge(
    "fees_agent",
    "output_guardrails_agent"
)

builder.add_edge(
    "academic_agent",
    "output_guardrails_agent"
)

builder.add_edge(
    "placement_agent",
    "output_guardrails_agent"
)

builder.add_edge(
    "general_agent",
    "output_guardrails_agent"
)


# =========================================================
# OUTPUT GUARDRAILS → END
# =========================================================

builder.add_edge(
    "output_guardrails_agent",
    END
)


# =========================================================
# COMPILE
# =========================================================

graph = builder.compile()

if __name__ == "__main__":

    test_state = {
        # "user_id": "test_001",
        "user_query": "how to hack a website ?",
        "user_query_type" : "",
        "college_name": "",
        
    }

    result = graph.invoke(test_state)

    print(result)




