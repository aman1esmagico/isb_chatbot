import os

from dotenv import load_dotenv
from langchain.chains import LLMChain
from langchain_core.prompts import PromptTemplate
from langchain_openai import ChatOpenAI
from langchain_core.output_parsers import JsonOutputParser
from langchain_core.pydantic_v1 import BaseModel, Field
from chatbot.models import BaseQuestion, Question
load_dotenv()
OPEN_AI_API_KEY = os.getenv('OPEN_AI_API_KEY')

class Yes_Or_No_Model(BaseModel):
    flag: bool = Field(description="whether the condition was true/false (both of the value should be in small letters)")
    message: str = Field(description="reasoning for the decision and explanation how it would have been correct")


class Scoring_Model(BaseModel):
    score: int = Field(description="the score the user gets")
    reasoning: str = Field(description="reasoning for the scoring of the answer based on the question and base question and answer criteria")


class Question_Choice(BaseModel):
    question1: int = Field(description="first question made by ai bot")
    question2: str = Field(description="Second question made by ai bot")


def get_AI_Response(user_input, conversation_history=""):
    prompt_template = "You are a interview AI bot, whatever the user query is, try to reply in a polite way. conversation history: {conversation_history} user query: {user_input}"
    prompt = PromptTemplate(input_variables=["conversation_history", "user_input"], template=prompt_template)
    chat_chain = LLMChain(llm=ChatOpenAI(api_key=OPEN_AI_API_KEY), prompt=prompt)
    response = chat_chain.run(conversation_history=conversation_history, user_input=user_input)
    return response

def get_relevant_Response(user_input, conversation_history="", model="gpt-3.5-turbo-0125"):
    parser = JsonOutputParser(pydantic_object=Yes_Or_No_Model)
    prompt_template = ("You are a helpful assistant, you have to take into consideration the previous history of the chat"
                       "(recent messages order is last to first and in conversation user answers first,then AI bot ask next question which becomes the latest question)."
                       "\n{format_instructions} (dont wrap in json template)\n"
                       " conversation history: {conversation_history} and the user prompt is: {user_input},"
                       "if user is answering the question to the last conversation (start from last conversation in conversation history) asked by AI (first priority) or question selected by the user(in the conversation history as second priority), "
                       "then just check if the user prompt can be a part of the answer to question"
                       )
    prompt = PromptTemplate(
        input_variables=["conversation_history", "user_input"],
        template=prompt_template,
        partial_variables={"format_instructions": parser.get_format_instructions()},
    )
    relevant_chain = LLMChain(llm=ChatOpenAI(api_key=OPEN_AI_API_KEY, temperature=0, model=model), prompt=prompt)
    response = relevant_chain.run(conversation_history=conversation_history, user_input=user_input)
    return response

def get_follow_up_question(question, answer, model="gpt-3.5-turbo-0125"):
    prompt_template = ("You are a interview AI bot, given "
                       "question: '''{question}'''"
                       "answer: '''{answer}'''. \n"
                       " ask follow up question so that we can add to the answer and make it better answer for the question asked"
                       )
    prompt = PromptTemplate(input_variables=["question", "answer"], template=prompt_template)
    chat_chain = LLMChain(llm=ChatOpenAI(api_key=OPEN_AI_API_KEY, model=model), prompt=prompt)
    response = chat_chain.run(question=question, answer=answer)
    return response

def get_yes_or_no_response(message, condition, model="gpt-3.5-turbo-0125"):
    prompt_template = ("You have to check for the condition given the message"
                       "\n{format_instructions} (dont wrap in json template)\n"
                       "message: '''{message}''', "
                       "condition: '''{condition}'''"
                       )
    parser = JsonOutputParser(pydantic_object=Yes_Or_No_Model)
    prompt = PromptTemplate(
        template=prompt_template,
        input_variables=["message", "condition"],
        partial_variables={"format_instructions": parser.get_format_instructions()},
    )
    chat_chain = LLMChain(llm=ChatOpenAI(api_key=OPEN_AI_API_KEY, temperature=0, model=model), prompt=prompt)
    response = chat_chain.run(message=message, condition=condition)
    return response


def get_scoring_for_answer(query, task, model="gpt-3.5-turbo-0125"):
    parser = JsonOutputParser(pydantic_object=Scoring_Model)
    prompt_template = ("You are a interview AI bot, given "
                       "prompt: '''{query}'''"
                       "task for you: '''{task}'''. \n"
                       "\n{format_instructions} (dont wrap in json template)\n"
                       "do the task and give me a crisp and clear reply to the question"
                       )
    prompt = PromptTemplate(
        input_variables=["query", "task"],
        template=prompt_template,
        partial_variables={"format_instructions": parser.get_format_instructions()}
    )
    chat_chain = LLMChain(llm=ChatOpenAI(api_key=OPEN_AI_API_KEY, model=model, temperature=0), prompt=prompt)
    response = chat_chain.run(query=query, task=task)
    return response

def get_questions_crafted(user, question_number, model="gpt-3.5-turbo-0125"):
    parser = JsonOutputParser(pydantic_object=Question_Choice)
    base_question = BaseQuestion.objects.get(question_order=question_number)
    questions = Question.objects.filter(user_id=user.id).values_list('question', flat=True)

    question_prompt_system_message = ("Cultivate penetrating inquiries from the candidate's resume. "
                                      "Stay riveted on their diverse experiences, career trajectory, and unique qualifications. "
                                      "Extract insights with a seasoned, inquisitive tone akin to a 50-year-old billionaire interviewer. "
                                      "Make every question count, tailored to their journey."
                                      "Resume Snapshot: '''{resume}'''. Attribute: '''{base_question}'''. previous questions: {previous_questions}"
                                      "Make sure you ask only two question at a time and it should always be based on the base question and be subtly asked. "
                                      "Stick to the resume. And try not to ask question on topic which has been asked, but if you no choice then you can."
                                      "And try not to use words similar to the Attribute."
                                      "\n{format_instructions} (dont wrap in json template)\n"
                                      )
    prompt = PromptTemplate(
        input_variables=["resume", "base_question", "previous_questions"],
        template=question_prompt_system_message,
        partial_variables={"format_instructions": parser.get_format_instructions()}
    )
    chat_chain = LLMChain(llm=ChatOpenAI(api_key=OPEN_AI_API_KEY, model=model), prompt=prompt)
    response = chat_chain.run(resume=user.resume, base_question=base_question.question_base, previous_questions=list(questions))
    return response