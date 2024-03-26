import json
import os

from dotenv import load_dotenv
from langchain.chains import LLMChain
from langchain_core.prompts import PromptTemplate
from langchain_openai import ChatOpenAI
from langchain_core.output_parsers import JsonOutputParser, SimpleJsonOutputParser
from langchain_core.pydantic_v1 import BaseModel, Field
from chatbot.models import BaseQuestion, Question
load_dotenv()

OPEN_AI_API_KEY = os.getenv('OPEN_AI_API_KEY')

class Relevance_model(BaseModel):
    flag: bool = Field(
        description="whether the condition was true/false")
    message: str = Field(description="message is for replying to the user prompt in cute way and remind them about the last question")


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
    prompt_template = "You are a interview AI bot, whatever the user query is, try to reply in a polite way. last 2 conversation history: '''{conversation_history}''' and reply to question is user query: '''{user_input}''', and also urge the user to bring back to the task in conversation. Respond in brief."
    prompt = PromptTemplate(input_variables=["conversation_history", "user_input"], template=prompt_template)
    chat_chain = LLMChain(llm=ChatOpenAI(api_key=OPEN_AI_API_KEY), prompt=prompt)
    response = chat_chain.run(conversation_history=conversation_history, user_input=user_input)
    return response

def get_conversation(conversation):
    json_data = eval(conversation)
    response = ""
    for item in json_data:
        for pair in item:
            for key, value in pair.items():
                response += f"{key}: {value}\n"
    return response


def get_relevant_Response(user_input, conversation_history="", model="gpt-3.5-turbo-0125"):
    parser = JsonOutputParser(pydantic_object=Relevance_model)
    prompt_template = ("You are a ai interview bot  , "
                       "you have to take into consideration the last 5 conversation of the chat "
                       "and human prompt is the answer to the last question asked by AI bot in conversation history"
                       "\n{format_instructions}\n"
                       "last 5 conversation history (messages order is bottom message is latest messages): '''{conversation_history}''' and the human prompt is: '''{user_input}''',"
                       "Condition: Do you think Human prompt fulfils all the the following things : \n  "
                       "1. It is relavant to the last question asked in conversation history\n"
                       "2. it wants to continue with the process of the interview\n"
                       )
    prompt = PromptTemplate(
        input_variables=["conversation_history", "user_input"],
        template=prompt_template,
        partial_variables={"format_instructions": parser.get_format_instructions()},
    )

    relevant_chain = LLMChain(llm=ChatOpenAI(api_key=OPEN_AI_API_KEY, temperature=0, model=model), prompt=prompt)
    response = relevant_chain.run(conversation_history=get_conversation(conversation_history), user_input=user_input)
    print(get_conversation(conversation_history))
    print("get_relevant_Response")
    print(response)
    return json.loads(response.replace('True', 'true').replace('False', 'false').replace("```json", "").replace("```", ""))

def get_follow_up_question(question, answer, model="gpt-3.5-turbo-0125"):
    prompt_template = ("You are a interview AI bot, given "
                       "question: '''{question}'''"
                       "answer: '''{answer}'''. \n"
                       " ask follow up question so that we can add to the answer and make it better answer for the question asked"
                       )
    prompt = PromptTemplate(input_variables=["question", "answer"], template=prompt_template)
    chat_chain = LLMChain(llm=ChatOpenAI(api_key=OPEN_AI_API_KEY, model=model), prompt=prompt)
    response = chat_chain.run(question=question, answer=answer)
    print("get_follow_up_question")
    print(response)
    return response

def get_yes_or_no_response(message, condition, model="gpt-3.5-turbo-0125"):
    prompt_template = ("You have to check for the condition given the message"
                       "\n{format_instructions}\n"
                       "message: '''{message}''', "
                       "condition: '''{condition}'''"
                       )
    parser = SimpleJsonOutputParser(pydantic_object=Yes_Or_No_Model)
    prompt = PromptTemplate(
        template=prompt_template,
        input_variables=["message", "condition"],
        partial_variables={"format_instructions": parser.get_format_instructions()},
    )

    chat_chain = LLMChain(llm=ChatOpenAI(api_key=OPEN_AI_API_KEY, temperature=0, model=model), prompt=prompt)
    response = chat_chain.run(message=message, condition=condition)
    print("get_yes_or_no_response")
    print(response)
    return json.loads(response.replace('True', 'true').replace('False', 'false').replace("```json", "").replace("```", ""))


def get_scoring_for_answer(query, task, model="gpt-3.5-turbo-0125"):
    parser = SimpleJsonOutputParser(pydantic_object=Scoring_Model)
    prompt_template = ("You are a interview AI bot, given "
                       "prompt: '''{query}'''"
                       "task for you: '''{task}'''. \n"
                       "\n{format_instructions}\n"
                       "do the task and give me a crisp and clear reply to the question"
                       )
    prompt = PromptTemplate(
        input_variables=["query", "task"],
        template=prompt_template,
        partial_variables={"format_instructions": parser.get_format_instructions()}
    )
    chat_chain = LLMChain(llm=ChatOpenAI(api_key=OPEN_AI_API_KEY, model=model, temperature=0), prompt=prompt)
    response = chat_chain.run(query=query, task=task)
    print("get_scoring_for_answer")
    print(response)
    return json.loads(response.replace("```json", "").replace("```", ""))

def get_questions_crafted(user, question_number, model="gpt-3.5-turbo-0125"):
    parser = SimpleJsonOutputParser(pydantic_object=Question_Choice)
    base_question = BaseQuestion.objects.get(question_order=question_number)
    questions = Question.objects.filter(user_id=user.id).values_list('question', flat=True)

    question_prompt_system_message = (
        "user's Resume: '''{resume}'''\n Attribute: '''{base_question}'''\n previous questions: '''{previous_questions}'''\n"
        "Create two subtle and contextual questions out of resume based on Attribute."
        "\n{format_instructions}\n"
        "The question's language should be simple english and asked as if it is being asked by 50-year-old wise billionaire entrepreneur who has lot of insigth in all type of business. "
        "The purpose is to find out more about the user journey and judge the user on the Attribute"
        "Make sure you make only two question at a time and always MUST use nouns or instances from the resume in the question you have to create."
        "Stick to the resume. And try not to ask questions from the same part resume as mentioned in previous questions"
        "And try not to use words similar to the Attribute or previous questions"
    )
    prompt = PromptTemplate(
        input_variables=["resume", "base_question", "previous_questions"],
        template=question_prompt_system_message,
        partial_variables={"format_instructions": parser.get_format_instructions()}
    )
    chat_chain = LLMChain(llm=ChatOpenAI(api_key=OPEN_AI_API_KEY, model=model), prompt=prompt)
    response = chat_chain.run(resume=user.resume, base_question=base_question.question_base, previous_questions=list(questions))
    print("get_questions_crafted")
    print(response)
    return json.loads(response.replace("```json", "").replace("```", ""))