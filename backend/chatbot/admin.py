from django.contrib import admin
from .models import BaseQuestion, Agent, Question

@admin.register(BaseQuestion)
class BaseQuestionAdmin(admin.ModelAdmin):
    list_display = ('id', 'question_order', 'question_base', 'scoring_strategy')
    search_fields = ('question',)

@admin.register(Agent)
class AgentAdmin(admin.ModelAdmin):
    list_display = ('id', 'agent_persona', 'description', 'task', 'agent_name')
    list_filter = ('task',)
    search_fields = ('agent_name',)

@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ('id', 'get_base_question', 'question', 'answer', 'retry', 'score', 'user_id')
    list_filter = ('score',)
    search_fields = ('question', 'answer')

    def get_base_question(self, obj):
        return obj.base_question.question_base