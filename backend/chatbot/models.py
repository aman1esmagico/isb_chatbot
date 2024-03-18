from django.db import models

# Create your models here.

from django.db import models

class BaseQuestion(models.Model):
    question_order = models.IntegerField(default=3)
    question_base = models.CharField(max_length=350)
    scoring_strategy = models.TextField()

class Agent(models.Model):
    class TaskChoices(models.TextChoices):
        QUESTION_CREATOR = 'question_creator', 'Question Creator'
        SCORER = 'scorer', 'Scorer'
        PERSONALITY_JUDGE = 'personality_judge', 'Personality Judge'

    agent_persona = models.TextField()
    description = models.CharField(max_length=350)
    task = models.CharField(max_length=20, choices=TaskChoices.choices)
    agent_name = models.CharField(max_length=100)

class Question(models.Model):
    base_question = models.ForeignKey(BaseQuestion, on_delete=models.CASCADE)
    question = models.TextField()
    retry = models.IntegerField(default=3)
    score = models.IntegerField(default=0)
    score_reasoning = models.TextField()
    answer = models.TextField()
    # asked_by = models.ForeignKey(Agent, on_delete=models.CASCADE, related_name='questions_asked')
    user_id = models.IntegerField()
