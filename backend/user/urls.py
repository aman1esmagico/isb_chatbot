from django.urls import path
from .views import SignUpView, LoginView,GreetView

urlpatterns = [
    path('signup/', SignUpView.as_view(), name='signup'),
    path('login/', LoginView.as_view(), name='login'),
    path('greet', GreetView.as_view(), name='greet')
]