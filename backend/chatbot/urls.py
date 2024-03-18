from .views import chatbot_controller
from django.urls import path, include

urlpatterns = [
    # todo routes
    path('talk/', chatbot_controller, name='chatbot-talk'),
]