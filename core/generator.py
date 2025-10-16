# app/core/generator.py
from langgraph.graph import StateGraph, START, END
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage, SystemMessage
from pydantic import BaseModel, Field
from typing import TypedDict, Literal, Annotated
import operator, os
from dotenv import load_dotenv

load_dotenv()

# Initialize LLMs
#gemini-2.5-flash-lite 
#gemini-1.5-flash 
generator_llm = ChatGoogleGenerativeAI(model='gemini-2.5-flash-lite')
evaluator_llm = ChatGoogleGenerativeAI(model='gemini-2.5-flash-lite')
optimizer_llm = ChatGoogleGenerativeAI(model='gemini-2.5-flash-lite')

class TweetEvaluation(BaseModel):
    evaluation: Literal["approved", "needs_improvement"]
    feedback: str

structured_evaluator_llm = evaluator_llm.with_structured_output(TweetEvaluation)

class TweetState(TypedDict):
    topic: str
    tweet: str
    evaluation: Literal["approved", "needs_improvement"]
    feedback: str
    iteration: int
    max_iterations: int
    tweet_history: Annotated[list[str], operator.add]
    feedback_history: Annotated[list[str], operator.add]

def generate_tweet(state: TweetState) -> TweetState:
    messages = [
        SystemMessage(content="You are a funny and clever Twitter/X influencer."),
        HumanMessage(content=f"""Write a short, original, hilarious tweet on: "{state['topic']}"...""")
    ]
    response = generator_llm.invoke(messages).content
    return {'tweet': response, 'tweet_history': [response]}

def evaluate_tweet(state: TweetState) -> TweetState:
    messages = [
        SystemMessage(content="You are a ruthless tweet critic."),
        HumanMessage(content=f"""Evaluate this tweet: "{state['tweet']}" ...""")
    ]
    response = structured_evaluator_llm.invoke(messages)
    return {'evaluation': response.evaluation, 'feedback': response.feedback, 'feedback_history': [response.feedback]}

def optimize_tweet(state: TweetState) -> TweetState:
    messages = [
        SystemMessage(content="You improve tweets for virality."),
        HumanMessage(content=f"""Improve tweet based on feedback: "{state['feedback']}" ...""")
    ]
    response = optimizer_llm.invoke(messages).content
    iteration = state['iteration'] + 1
    return {'tweet': response, 'iteration': iteration}

def route_evaluation(state: TweetState) -> str:
    if state['evaluation'] == 'approved' or state['iteration'] >= state['max_iterations']:
        return 'approved'
    return 'needs_improvement'

def create_tweet_workflow():
    graph = StateGraph(TweetState)
    graph.add_node('generate', generate_tweet)
    graph.add_node('evaluate', evaluate_tweet)
    graph.add_node('optimize', optimize_tweet)
    graph.add_edge(START, 'generate')
    graph.add_edge('generate', 'evaluate')
    graph.add_conditional_edges('evaluate', route_evaluation, {'approved': END, 'needs_improvement': 'optimize'})
    graph.add_edge('optimize', 'evaluate')
    return graph.compile()

workflow = create_tweet_workflow()

def run_tweet_generation(topic: str):
    initial_state = {'topic': topic, 'iteration': 1, 'max_iterations': 5}
    result = workflow.invoke(initial_state)
    return result
