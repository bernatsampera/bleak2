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


class Question(BaseModel):
    """Represents a question to be asked to the user."""

    id: str  # Unique identifier for the question
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
    questions: List[Question]


# Initialize the LLM
llm = init_chat_model("google_genai:gemini-2.5-flash-lite")
# llm = init_chat_model("ollama:qwen3:14b")
# llm = init_chat_model("ollama:gemma3:4b")


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
        {{"id": "q1", "question": "question1", "type": "radio", "options":["option1", "option2", "option3"]}},
        {{"id": "q2", "question": "question2", "type": "input"}},
    ]

    Format your response as a JSON array of questions with:
    - "id": a unique identifier (like "q1", "q2", etc.)
    - "question": the question text
    - "type": either "radio" for multiple choice or "input" for open text
    - "options": an array of options for radio questions. CRITICAL: Radio questions MUST have at least 2 options, preferably 3-5 options.
    - For "input" type questions, the options array should be empty []

    IMPORTANT:
    - If you use "radio" type, you MUST provide a non-empty options array with at least 2 choices
    - If you use "input" type, the options array should be empty []
    - All radio questions must have meaningful, distinct options
    - Each question MUST have a unique id

    If the user's request is already clear enough, return an empty array [].
    """

    # Generate questions using structured output
    structured_llm = llm.with_structured_output(QuestionsOutput)
    response = await structured_llm.ainvoke([{"role": "user", "content": prompt}])

    print(response)

    if not response.need_clarification:  # No questions needed, proceed to completion
        return Command(
            goto=END,
            update={"questions": []},
        )

    answers = interrupt({"questions": response.questions})

    print("answers", answers)
    # Use interrupt to wait for human input - send all questions at once
    return Command(
        goto="ask_user_input",
        update={
            "questions": response.questions,
            "answers": answers,
        },
    )


async def ask_user_input(state: State) -> Command[Literal["__end__"]]:
    questions = state.get("questions", [])
    messages = state.get("messages", [])
    answers = state.get("answers", {})

    # Format the answers for the prompt
    formatted_answers = []
    for question in questions:
        question_id = question.id
        answer_text = answers.get(question_id, "") if isinstance(answers, dict) else ""
        formatted_answers.append({"question": question.question, "answer": answer_text})

    prompt = f"""
        Provide a complete answer to the user based on the original question and the user's answers.

        Original Messages:
        {messages}

        User Answers to Clarifying Questions:
        {formatted_answers}

        Return just a brief answer, no more questions.
    """

    complete_response = await llm.ainvoke(prompt)

    # Proceed to process the answers (or complete if all done)
    return Command(
        goto=END,
        update={
            "messages": [complete_response.content],
        },
    )


# Build the graph
graph_builder = StateGraph(State, input=InputState)
graph_builder.add_node("generate_questions", generate_questions)
graph_builder.add_node("ask_user_input", ask_user_input)

graph_builder.add_edge(START, "generate_questions")

checkpointer = MemorySaver()
# graph = graph_builder.compile(checkpointer=checkpointer)  ## use without langgraph stdio
graph = graph_builder.compile()
