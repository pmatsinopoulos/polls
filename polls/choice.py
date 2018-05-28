from django.db import models

import question


class Choice(models.Model):
    question = models.ForeignKey(question.Question, on_delete=models.CASCADE)
    choice_text = models.CharField(max_length=200)
    votes = models.IntegerField(default=0)

    def __str__(self):
        return self.choice_text
