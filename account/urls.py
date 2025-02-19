from django.urls import path
from .views import *

urlpatterns = [
    path('admin_login/', admin_login, name='admin_login'),
    path('upload_page/', upload_exam_results, name='upload_page'), 
    # path('clear-data/', clear_data, name='clear_data'),
    path('clear_data/', upload_exam_results, name='clear_data_test'),
    path('student_login/', student_login, name='student_login'), 
    path('results/', results, name='results'),

]
