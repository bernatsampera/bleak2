from typing import List, Literal

from dotenv import load_dotenv
from langchain.chat_models import init_chat_model
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import END, START, StateGraph
from langgraph.graph.message import MessagesState
from langgraph.types import Command, interrupt
from pydantic import BaseModel
from typing_extensions import TypedDict

load_dotenv()


class InputState(MessagesState):
    """Input state containing only the fields needed for initial input."""

    pass


class State(InputState):
    """The state of the chatbot with additional fields for question handling."""

    questions: List[dict]  # Stores generated questions
    answers: List[dict]  # Stores user answers


class Question(TypedDict):
    """Represents a question to be asked to the user."""

    question: str
    type: str  # "radio" or "input"
    options: List[str]  # Only for radio questions


class Answer(TypedDict):
    """Represents an answer provided by the user."""

    question: str
    answer: str


class QuestionsOutput(BaseModel):
    """Structured output for generated questions."""

    need_clarification: bool
    questions: List[dict]


# Initialize the LLM
# llm = init_chat_model("google_genai:gemini-2.5-flash-lite")
# llm = init_chat_model("ollama:qwen3:14b")
llm = init_chat_model("ollama:gemma3:4b")


async def generate_questions(
    state: State,
) -> Command[Literal["__end__", "ask_user_input"]]:
    """Generate clarifying questions based on the user's initial request.

    This node analyzes the user's message and creates questions to better understand their needs.
    """
    messages = state["messages"]

    # Get the last user message
    user_message = messages[-1].content if messages else ""

    # Simple prompt to generate questions
    prompt = f"""
    Based on this user request: "{user_message}"

    Generate 1-3 clarifying questions to better understand what the user wants.
    
    Return the questions as an array of JSON objects.
    need_clarification: bool
    questions: [
        {{"question": "question1", "type": "radio", "options":["option1", "option2"]}},
        {{"question": "question2", "type": "input"}},
    ]

    Format your response as a JSON array of questions with:
    - "question": the question text
    - "type": either "radio" for multiple choice or "input" for open text

    If the user's request is already clear enough, return an empty array [].
    """

    # Generate questions using structured output
    structured_llm = llm.with_structured_output(QuestionsOutput)
    response = await structured_llm.ainvoke([{"role": "user", "content": prompt}])

    if not response.need_clarification:  # No questions needed, proceed to completion
        return Command(
            goto=END,
            update={"questions": []},
        )

    # need_clarification=True questions=[{'question': "What type of 'deep agent' are you referring to? For example, is it an AI model using deep learning techniques, a simulation, or another approach?", 'type': 'radio', 'options': ['AI model with deep learning', 'Simulation or virtual agent', 'Other (please specify)']}, {'question': 'What was the primary goal of your project? For example, did you aim to analyze historical data, reconstruct biographies, or identify patterns in historical events?', 'type': 'input'}]
    # Use interrupt to wait for human input - send all questions at once
    return Command(
        goto="ask_user_input",
        update={"questions": response.questions},
    )


async def ask_user_input(state: State) -> Command[Literal["__end__"]]:
    questions = state.get("questions", [])
    messages = state.get("messages", [])
    answers = interrupt(
        {
            "query": "Please answer the following questions:",
            "questions": questions,
        }
    )

    prompt = f"""
        Provide a complete answer to the user based on the original question and the user's answer.
        
        Messages:
        {messages}
        
        Answers: 
        {answers}
        
        Return just a brief answer, no more questions.
    """

    complete_response = await llm.ainvoke(prompt)

    # Proceed to process the answers (or complete if all done)
    return Command(
        goto=END,
        update={
            "answers": answers,
            "messages": complete_response.content,
        },
    )


# Build the graph
graph_builder = StateGraph(State, input=InputState)
graph_builder.add_node("generate_questions", generate_questions)
graph_builder.add_node("ask_user_input", ask_user_input)

graph_builder.add_edge(START, "generate_questions")

checkpointer = MemorySaver()
graph = graph_builder.compile(checkpointer=checkpointer)  ## use without langgraph stdio
