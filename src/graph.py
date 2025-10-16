from typing import Annotated

from dotenv import load_dotenv
from langchain.chat_models import init_chat_model
from langgraph.graph import END, START, StateGraph
from langgraph.graph.message import add_messages, MessagesState
from typing_extensions import TypedDict

load_dotenv()


class State(MessagesState):
    """
    The state of the chatbot.
    """


# Initialize the LLM
# llm = init_chat_model("ollama:llama3.1:latest")
llm = init_chat_model("google_genai:gemini-2.5-flash-lite")


# Define the chatbot node
def chatbot(state: State):
    return {"messages": [llm.invoke(state["messages"])]}


# Build the graph
graph_builder = StateGraph(State)
graph_builder.add_node("chatbot", chatbot)
graph_builder.add_edge(START, "chatbot")
graph_builder.add_edge("chatbot", END)

graph = graph_builder.compile()

