from rest_framework import serializers
from .models import BaseQuestion, Agent, Question

class BaseQuestionSerializer(serializers.ModelSerializer):
    class Meta:
        model = BaseQuestion
        fields = '__all__'

class AgentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Agent
        fields = '__all__'

class QuestionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Question
        fields = '__all__'
