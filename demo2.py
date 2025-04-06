import random

from typing import Annotated
from typing_extensions import TypedDict

from langgraph.graph import StateGraph
from langgraph.graph.message import add_messages
from langchain_openai import ChatOpenAI
from langchain.schema import SystemMessage

# OpenAI chat model
openai_model = ChatOpenAI(model="gpt-4-turbo", temperature=0.7)

# Game State
class State(TypedDict):
    object_to_guess: str
    questions_asked: Annotated[list, add_messages]
    guesses_asked: Annotated[list, add_messages]
    guess_attempts: int
    max_questions: int
    winner: str | None

# Bot 1: Asks a question
def ask_question(state: State):
    questions = [item.content for item in state['questions_asked']]
    prompt = f"""You are playing 20 Questions. You need to guess the object that the other AI is thinking of. 
    Based on previous answers: {questions}, ask a strategic Yes or No question."""
    
    response = openai_model.invoke([SystemMessage(content=prompt)])
    return {"questions_asked": [response.content]}

# Bot 2: Answers the question
def answer_question(state: State):
    last_question = state["questions_asked"][-1].content
    prompt = f"""You are playing 20 Questions. You need to answer Yes or No. The question being asked is: [{last_question}]. 
    Only answer with Yes or No. Remember, the object being guessed is: [{state["object_to_guess"].lower()}]"""
    
    response = openai_model.invoke([SystemMessage(content=prompt)])
    answer = response.content

    state["questions_asked"][-1].content = f"""{state["questions_asked"][-1].content} {answer}"""
    return {"answer": answer}

# Bot 1: Makes a guess after some questions
def make_guess(state: State):
    questions = [item.content for item in state['questions_asked']]
    guesses = [item.content for item in state['guesses_asked']]
    
    prompt = f"""You have asked these questions: {questions}. You have made the following guesses: {guesses}. 
    Now make a final guess at what the object is."""
    
    response = openai_model.invoke([SystemMessage(content=prompt)])
    
    return {"guesses_asked": response.content}

def check_game_over(state: State):
    guess_attempts = state["guess_attempts"] + 1
     
    prompt = f"""You are the judge of 20 questions. The object to guess is: [{state["object_to_guess"].lower()}]
    The guess is: [{state["guesses_asked"][-1].content}] Is the object mentioned in the guess? Please answer with Yes or No."""
    response = openai_model.invoke([SystemMessage(content=prompt)])
   
    if "Yes" in response.content:
        return {"winner": "Questioner", "guess_attempts": guess_attempts}
    else:
        return {"guess_attempts": guess_attempts}
    
# Check if game should continue
def router(state: State):
    if state["winner"]:
        return "end_game"
    elif state["guess_attempts"] >= state["max_questions"]:
        return "end_game"
    return "ask_question"

# End Game Node
def end_game(state: State):
    return {
        "message": f"Game Over! The correct answer was {state['object_to_guess']}. Winner: {state['winner'] if state['winner'] else 'No one'}"
    }

# Create Graph
builder = StateGraph(State)

# Add nodes
builder.add_node("ask_question", ask_question)
builder.add_node("answer_question", answer_question)
builder.add_node("make_guess", make_guess)
builder.add_node("check_game_over", check_game_over)
builder.add_node("end_game", end_game)

# Define flow
builder.set_entry_point("ask_question")
builder.add_edge("ask_question", "answer_question")
builder.add_edge("answer_question", "make_guess")
builder.add_edge("make_guess", "check_game_over")
builder.add_conditional_edges("check_game_over", router, {"ask_question": "ask_question", "end_game": "end_game"})

# Compile and Run
graph = builder.compile()

initial_state: State = {
    "object_to_guess": random.choice(["bird", "chair", "refrigerator", "ball", "table"]),
    "questions_asked": [],
    "guesses_asked": [],
    "guess_attempts": 0,
    "max_questions": 5,
    "winner": None,
}

graph.invoke(initial_state)