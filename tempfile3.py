from langgraph.graph import StateGraph, END
from langgraph.types import Command, interrupt
from typing import TypedDict
from langgraph.checkpoint.memory import MemorySaver

memory = MemorySaver()
class State(TypedDict):
    text : str
    
def node_a(state: State): 
    print("node A")
    return Command(
        goto="node_b", 
        update={
            "text": state["text"] + "a"
        }
    )

def node_b(state : State):
    print("node_b")
    
    human_response = interrupt("where do you want to go c/d? Type c/d")
    print(f"human value recieved : {human_response}")
    
    if human_response == "c":
        return Command(
            goto = "node_c",
            update = {
                "text" : state["text"] + "b"
            }
        )        
        
    elif human_response == "d":
        return Command(
            goto = "node_d",
            update = {
                "text" : state["text"] + "b"
            }
        )
        
def node_c(state : State):
    print("node_c")
    return Command(
        goto = END,
        update = {
            "text" : state["text"] + "c"
        }
    )
    
def node_d(state : State):
    print("node_d")
    return Command(
        goto = END,
        update = {
            "text" : state["text"] + "d"
        }
    )
    
graph = StateGraph(State)
graph.add_node("node_a", node_a)
graph.add_node("node_b", node_b)
graph.add_node("node_c", node_c)
graph.add_node("node_d", node_d)
graph.set_entry_point("node_a")

compiled_graph = graph.compile(checkpointer = memory)
config = {"configurable" : {"thread_id" : 1}}

initialstate = {
    "text" : ""
}

first_result = compiled_graph.invoke(initialstate, config, stream_mode = "updates")
print(first_result)
print(compiled_graph.get_state(config).next)

second_result = compiled_graph.invoke(Command(resume = "c"), config = config, stream_mode = "updates")
print(second_result)
