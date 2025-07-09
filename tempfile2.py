import os
import sys
from typing import Annotated
from dotenv import load_dotenv
from typing_extensions import TypedDict
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langchain_openai import ChatOpenAI
from langchain_tavily import TavilySearch
from langgraph.prebuilt import ToolNode
from langgraph.checkpoint.memory import MemorySaver
from langgraph.types import Command, interrupt

load_dotenv()

class State(TypedDict):
    messages: Annotated[list, add_messages]
    approved: bool

graph_builder = StateGraph(State)

openrouter_key = os.getenv("openrouter_key")
if not openrouter_key:
    print("Error: OPENROUTER_KEY is not set in the environment.")
    sys.exit(1)

llm = ChatOpenAI(
    api_key=openrouter_key,
    base_url="https://openrouter.ai/api/v1",
    model="meta-llama/llama-3-70b-instruct",
    temperature=0.5,
)

tool = TavilySearch(max_result=2)
tools = [tool]
llm_with_tools = llm.bind_tools(tools)

def chatbot(state: State):
    return {
        "messages": [llm_with_tools.invoke(state["messages"])]
    }

def need_approval(state: State):
    last_message = state["messages"][-1]
    if hasattr(last_message, "tool_calls") and last_message.tool_calls:
        
        print(f"Tool calls detected: {last_message.tool_calls}")
        human_response = interrupt("Assistant wants to use a search tool. Approve? (yes/no): ")
        print(f"Human response received: {human_response}")
        
        if human_response and human_response.lower().strip() == "yes":
            return Command(
                goto="tools",
                update={"approved": True}
            )
            
        elif human_response and human_response.lower().strip() == "no":
            return Command(
                goto=END,
                update={"approved": False}
            )
        
        else:
            return Command(
                goto="need_approval",
                update={"approved": False}
            )
    
    return Command(goto=END)

graph_builder.add_node("chatbot", chatbot)
graph_builder.add_node("need_approval", need_approval)
tool_node = ToolNode(tools=tools)
graph_builder.add_node("tools", tool_node)

graph_builder.add_edge(START, "chatbot")
graph_builder.add_edge("chatbot", "need_approval")
graph_builder.add_edge("tools", "chatbot")

memory = MemorySaver()
graph = graph_builder.compile(checkpointer=memory)

def run_with():
    while True:
        config = {
            "configurable": {
                "thread_id": "6"
            }
        }

        user_input = input("enter your question : ")
        
        initial_state = {
            "messages": [{"role": "user", "content": user_input}],
            "approved": False
        }

        print("Starting conversation with commands and interrupts...")
        
        try:
            events = list(graph.stream(initial_state, config, stream_mode="values"))
            snapshot = graph.get_state(config=config)
            
            while snapshot.interrupts:
                print(f"\nInterrupt detected: {snapshot.interrupts[0].value}")
                
                user_response = input("Your response: ")
                print(f"Resuming with: {user_response}")
                
                events = list(graph.stream(Command(resume=user_response), config, stream_mode="values"))
                snapshot = graph.get_state(config=config)
                
                for event in events:
                    print(f"Event: {event}")
                    
            print("\nConversation completed!")
            
        except Exception as e:
            print(f"Exception occurred: {e}")
            
            snapshot = graph.get_state(config=config)
            if snapshot.interrupts:
                print(f"\nInterrupt found in exception: {snapshot.interrupts[0].value}")
                user_response = input("Your response: ")
                
                try:
                    events = list(graph.stream(Command(resume=user_response), config, stream_mode="values"))
                    for event in events:
                        print(f"Resume event: {event}")
                except Exception as resume_e:
                    print(f"Resume exception: {resume_e}")
        
        final_snapshot = graph.get_state(config=config)
        print(f"\nFinal state:")
        print(f"Next: {final_snapshot.next}")
        print(f"Interrupts: {len(final_snapshot.interrupts)}")
        
        if final_snapshot.values.get('messages'):
            print(f"Total messages: {len(final_snapshot.values['messages'])}")
            
            if final_snapshot.values['messages']:
                last_msg = final_snapshot.values['messages'][-1]
                
                if hasattr(last_msg, 'content'):
                    print(f"Last message: {last_msg.content[:100]}...")
                    
                else:
                    print(f"Last message: {str(last_msg)[:100]}...")

if __name__ == "__main__":
    run_with()