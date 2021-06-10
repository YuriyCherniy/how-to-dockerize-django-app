from django.urls import path

from demo.views import DemoObjectCreate


urlpatterns = [
    path('', DemoObjectCreate.as_view(), name='create_object'),
]