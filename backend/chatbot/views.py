import json

from rest_framework.decorators import api_view
from rest_framework.response import Response

from chatbot.models import Question, BaseQuestion
from user.models import User

from chatbot.chatbotService.chartBotService import (get_relevant_Response,
                                                    get_yes_or_no_response,
                                                    get_questions_crafted,
                                                    get_follow_up_question,
                                                    get_scoring_for_answer,
                                                    get_AI_Response,
                                                    get_conversation)


@api_view(['POST'])
def chatbot_controller(request):
        try:
            user_input = request.data['prompt']
            user_id = request.data['userId']
            user = User.objects.get(id=user_id)
            if not user:
                return Response({
                    'message': ['User not found! \n please try to login and comeback']},
                    status=400)
            # preprocessing

            if user.started_conversation:
                conversation_history = str(user.conversation)
                relavant_response = get_relevant_Response(user_input, conversation_history, model="gpt-4-0125-preview")
                print(type(relavant_response))
                if not relavant_response['flag']:
                    print("returning the response for irrelavant user response")
                    return Response({"message": relavant_response['message'][:-1].split(".")}, status=200)
            else:
                CREATE_INTRO = [
                    "Hello! I am an AI bot designed to conduct a swift, smart, and precise interview process.",
                    "I will begin by generating a unique question based on the resume you provide.",
                    "Please provide the candidate's resume text of at least 100 characters for a productive conversation:"
                ]
                conversation_history = [{"Human": user_input}, {"AI": "".join(CREATE_INTRO)}]
                user.conversation.append(conversation_history)
                user.started_conversation = True
                user.task = ("Human task is to provide his resume which contains work history, their role, responsibility, education background, hobbies and acchievement."
                             "It should be with enough context to create atleast 10 different interview question")
                user.save()
                return Response({"message": CREATE_INTRO}, status=200)

            # for processing the state and get the response from the user
            print("Relevance of user Input is passed")
            response = handle_state(user, user_input)
            # after processing
            conversation_history =[{"Human": user_input},{"AI": ".".join(response["message"])}]
            user.conversation.append(conversation_history)
            user.conversation = user.conversation[-5:]
            user.save()
            return Response(response, status=200)

        except Exception as e:
            print('err:', e)
            return Response('error', status=500)


def handle_state(user, user_input):
    user_state = user.state
    state_reminder = user_state % 3
    state = user_state / 3
    # Moving on to the states
    if user_state == 0 :
        condition = ("Check if the text in message is resume of the user, which MUST have all the following three things -\n"
                     "1. Work history, including job titles, the name of the company, the role and responsibility of the user.\n"
                     "2. Education background of the user.\n"
                     "3. personal details of the user.\n"
                )
        yes_or_no_dict = get_yes_or_no_response(user_input, condition, model="gpt-4-0125-preview")

        if yes_or_no_dict["flag"] and len(user_input) > 200:
            user.state = user.state + 1
            user.resume = user_input
            user.task = ("Human task is to select one out of the two question, which was created by Ai interview bot")
            user.save()
            return{"message": ["resume is accepted", "are you ready for interview?"]}
        else:
            print("Ask for the resume again")
            return {"message": [yes_or_no_dict["message"], "Can you please enter another resume with more details?"]}

    if user_state == 13: # last state FIXME: change it env variable
        print("the interview is over. Do you have any question"
              "related to the course or job requirement")
        return {"message": ["Interview is Done", "You can close the interview", "Have a great day ahead"]}

    match state_reminder:
        case 0: # state for the answer acceptance and
            question = Question.objects.filter(user_id=user.id).last()
            task = ("question selected by the user is:" +
                    str(question.question) + "and last 2 conversation : " + get_conversation(str(user.conversation[-2:])) +
                    " and the reply given by user to last question is '''" + str(user_input) +
                    "'''. Do you think the user's input can be a part of the answer to the question by AI bot?")

            yes_or_no = get_yes_or_no_response(user_input, task)
            if not yes_or_no['flag']:
                response = get_AI_Response(user_input, get_conversation(str(user.conversation[-2:])))
                print("have to ask user to be relevant to the question asked")
                return {"message": response[:-1].split(".")}
            else:
                question.answer = str(question.answer) + str(user_input)
                question.save()
            user_answer = question.answer
            if len(user_answer) < 100:
                if question.retry < 2:
                    user.state = user.state + 1
                    user.task = ("Human task is to select one out of the two question, which was created by AI interview bot")
                    user.save()
                    question.retry = question.retry - 1
                    score_the_user_answer(question)
                    return {"message": ["thanks for trying to answer the question", "Lets move on to next question", "Let me know whenever you are ready!"]}
                question.retry = question.retry - 1
                question.save()
                follow_up_question = get_follow_up_question(question.question, user_answer)
                return {"message": [follow_up_question]}

            scoring_criteria = question.base_question.scoring_strategy
            answer_task = f"""Do you think it is enough for you to judge based on the criteria: {scoring_criteria} for the question {question.question}.?"""
            yes_or_no_answer = get_yes_or_no_response(user_answer, answer_task)
            if (not yes_or_no_answer['flag']) and len(user_answer.split(" ")) < 100:
                follow_up_question = get_follow_up_question(question.question, user_answer)
                if question.retry < 2:
                    user.state = user.state + 1
                    user.task = (
                        "Human task is to select one out of the two question, which was created by AI interview bot")
                    user.save()
                    question.retry = question.retry - 1
                    score_the_user_answer(question)
                    return {"message": ["thanks for trying to answer the question", "Lets move on to next question",
                                        "Let me know whenever you are ready!"]}
                question.retry = question.retry - 1
                question.save()
                return {"message": [follow_up_question]}

            score_the_user_answer(question)
            user.state = user.state + 1
            user.task = (
                "Human task is to tell the Ai bot for whenever they is ready!")
            user.save()
            return {"message": ["thanks for the answer.", "lets move on to next question.",
                                "let me know whenever you are ready!"]}

        case 1:
            response = get_questions_crafted(user, state+1, model='gpt-4-turbo-preview')
            user.conversation_summary = str(response)
            questions = response
            user.state = user.state + 1
            user.task = ("Human task is to answer the question, that was selected ")
            user.save()
            return {"message": ["Please copy and paste any one of the following question you want to answer", questions['question1'], questions['question2']] }
        case 2:
            questions = eval(user.conversation_summary)
            if not (user_input == questions['question1'] or user_input == questions['question2']):
                return {"message": ["Please copy and paste any one of the question mentioned only", questions["question1"], questions["question2"]]}
            base_question = BaseQuestion.objects.get(question_order=state + 1)
            question = Question.objects.create(base_question=base_question, question=user_input, answer="", user_id=user.id)
            user.task = ("Human task is to let us know, whenever he is ready to continue the interview")
            user.state = user.state + 1
            return {"message": ["Have registered the question you selected", "Please answer the following question", question.question]}

    return{"message": ["Can you please try again??"]}


def score_the_user_answer(question):
    scoring_task = f"""
                    for the above answer to the question: {question.question} where the base question is {question.base_question.question_base}
                    please score and return your reason for the scoring based on the criteria: {question.base_question.scoring_strategy}. Score should be between 1-5.
                    Also be mindful, the number of hints that candidates needed to come to this answer is {3-question.retry}.
                    """
    scoring_response = get_scoring_for_answer(question.answer, scoring_task, model="gpt-4-turbo-preview")
    score = scoring_response['score']
    reason_for_score = scoring_response['reasoning']
    question.score = score
    question.score_reasoning = reason_for_score
    question.save()