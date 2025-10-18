from langchain.chat_models import init_chat_model
from langchain_core.tools import tool
from langgraph.graph import END, START, MessagesState, StateGraph
from langgraph.types import interrupt

# Initialize model
model = init_chat_model("ollama:qwen3:14b", reasoning=False)


# Define the tool
@tool(
    description="Call this function to generate a tweet on user request. The user will have the chance to review the tweet before it is sent."
)
def send_tweet(tweet: str) -> str:
    """Tool to send tweets.

    Args:
        tweet: The tweet contents.

    Returns:
        Confirmation and instruction to proceed
    """
    return f"Tweet Sent: {tweet}."


# Bind the tool to the model
model = model.bind_tools([send_tweet])


# LLM agent node
async def agent(state):
    messages = state["messages"]
    response = await model.ainvoke(messages)
    return {"messages": response}


# Tool execution node
async def send_tweet_node(state):
    tool_call = state["messages"][-1].tool_calls[0]
    result = interrupt("Do you want to send this tweet?")
    if result != "yes":
        return {
            "messages": {
                "role": "tool",
                "tool_call_id": tool_call["id"],
                "content": "User rejected request",
            }
        }

    return {
        "messages": {
            "role": "tool",
            "tool_call_id": tool_call["id"],
            "content": "sent",
        }
    }


# Control which node runs next
def should_continue(state):
    last_message = state["messages"][-1]
    if not last_message.tool_calls:
        return END

    last_tool_call = last_message.tool_calls[-1]
    if last_tool_call["name"] == "send_tweet":
        return "send_tweet"

    return END


# Build the state graph
builder = StateGraph(MessagesState)

builder.add_node("llm", agent)
builder.add_node("send_tweet", send_tweet_node)

builder.add_edge(START, "llm")
builder.add_edge("send_tweet", "llm")
builder.add_edge("llm", END)

builder.add_conditional_edges(
    "llm",
    should_continue,
    ["send_tweet", END],
)

graph = builder.compile()
