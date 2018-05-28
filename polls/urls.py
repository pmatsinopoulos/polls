from django.conf.urls import url

import views

app_name = 'polls'
urlpatterns = [
    url(r'^$', views.IndexView.as_view(), name='index'),
    # /polls/5/
    url('^(?P<pk>[0-9]+)/$', views.DetailView.as_view(), name='detail'),
    # /polls/5/results/
    url('^(?P<pk>[0-9]+)/results/$', views.ResultsView.as_view(), name='results'),
    # /polls/5/vote/
    url('^(?P<question_id>[0-9]+)/vote/$', views.vote, name='vote'),
]
