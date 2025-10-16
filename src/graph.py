from typing import List, Literal

from dotenv import load_dotenv
from langchain.chat_models import init_chat_model
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
    needs_questions: bool  # Flag to indicate if more questions are needed
    completed: bool  # Flag to indicate if the process is complete


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
llm = init_chat_model("ollama:qwen3:14b")


async def generate_questions(state: State) -> Command[Literal["__end__"]]:
    """Generate clarifying questions based on the user's initial request.

    This node analyzes the user's message and creates questions to better understand their needs.
    """
    messages = state["messages"]

    # Get the last user message
    user_message = messages[-1].content if messages else ""

    print(user_message)
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
    response = structured_llm.invoke([{"role": "user", "content": prompt}])

    if not response.need_clarification:  # No questions needed, proceed to completion
        return Command(
            goto=END,
            update={"questions": [], "needs_questions": False, "completed": True},
        )

    print(response)
    # need_clarification=True questions=[{'question': "What type of 'deep agent' are you referring to? For example, is it an AI model using deep learning techniques, a simulation, or another approach?", 'type': 'radio', 'options': ['AI model with deep learning', 'Simulation or virtual agent', 'Other (please specify)']}, {'question': 'What was the primary goal of your project? For example, did you aim to analyze historical data, reconstruct biographies, or identify patterns in historical events?', 'type': 'input'}]
    # Use interrupt to wait for human input - send all questions at once
    human_answers = interrupt(
        {
            "query": "Please answer the following questions:",
            "questions": response.questions,
        }
    )

    # Store questions and answers received from human
    answers = []
    for i, question in enumerate(response.questions):
        if i < len(human_answers):
            answers.append(
                {"question": question["question"], "answer": human_answers[i]}
            )

    # Proceed to process the answers (or complete if all done)
    return Command(
        goto=END,
        update={
            "questions": response.questions,
            "answers": answers,
            "needs_questions": False,
            "completed": True,
        },
    )


# Build the graph
graph_builder = StateGraph(State, input=InputState)
graph_builder.add_node("generate_questions", generate_questions)

graph_builder.add_edge(START, "generate_questions")

graph = graph_builder.compile()
