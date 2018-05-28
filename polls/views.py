# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render, get_object_or_404
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.views import generic
from django.utils import timezone

from question import Question
from choice import Choice


class IndexView(generic.ListView):
    model = Question

    def get_queryset(self):
        """Return the last five published questions."""
        return Question.objects.filter(
            pub_date__lt=timezone.now()
        ).order_by('-pub_date')[:5]


class DetailView(generic.DetailView):
    model = Question

    def get_queryset(self):
        return Question.objects.filter(pub_date__lt=timezone.now())


class ResultsView(generic.DetailView):
    model = Question
    template_name = 'polls/question_results.html'


def vote(request, question_id):
    question = get_object_or_404(Question, pk=question_id)
    try:
        selected_choice = question.choice_set.get(pk=request.POST['choice'])
    except(KeyError, Choice.DoesNotExist):
        return render(request, 'polls/detail.html',
                      {'question': question, 'error_message': "You didn't select a choice?"})
    else:
        selected_choice.votes += 1
        selected_choice.save()
        return HttpResponseRedirect(reverse('polls:results', args=(question.id,)))
