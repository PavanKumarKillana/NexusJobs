from django.urls import path
from . import views

app_name = 'jobs'

urlpatterns = [
    path('', views.job_list, name='list'),
    path('job/<int:pk>/', views.job_detail, name='detail'),
    path('job/<int:pk>/ai-summary/', views.ai_summarize_job, name='ai_summary'),
]
