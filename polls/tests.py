# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import datetime

from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from django.test import TestCase
from django.utils import timezone
from django.urls import reverse
from selenium.webdriver.chrome.webdriver import WebDriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.wait import WebDriverWait

from polls.question import Question

# Create your tests here.


def create_question(question_text, days):
    time = timezone.now() + datetime.timedelta(days=days)
    q = Question(pub_date=time, question_text=question_text)
    q.save()
    return q


class QuestionModelTests(TestCase):

    def test_was_published_recently_with_future_question(self):
        """
        was_published_recently() returns False for questions whose pub_date is in the future
        """
        in_the_future = timezone.now() + datetime.timedelta(days=30)
        q = Question(pub_date=in_the_future, question_text="anything")
        self.assertIs(q.was_published_recently(), False)

    def test_was_published_recently_with_old_question(self):
        """
        was_published_recently() should return False for an old question, older that 1 day old
        """
        in_the_past = timezone.now() - datetime.timedelta(days=2)
        q = Question(pub_date=in_the_past, question_text="anything")
        self.assertIs(q.was_published_recently(), False)

    def test_was_published_recently_with_recent_question(self):
        """
        was_published_recently() should return True for a question published within the last day
        """
        in_the_past = timezone.now() - datetime.timedelta(days=1) + datetime.timedelta(seconds=1)
        q = Question(pub_date=in_the_past, question_text="anything")
        self.assertIs(q.was_published_recently(), True)


class QuestionIndexViewTests(TestCase):
    def test_no_questions(self):
        response = self.client.get(reverse('polls:index'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "No polls are available")
        self.assertQuerysetEqual(response.context['question_list'], [])

    def test_past_question(self):
        create_question("foo bar", -30)
        response = self.client.get(reverse('polls:index'))
        self.assertEqual(response.status_code, 200)
        self.assertQuerysetEqual(response.context['question_list'], ['<Question: foo bar>'])

    def test_future_question(self):
        """
        Questions with a pub_date in the future aren't displayed on
        the index page.
        """
        create_question(question_text="Future question.", days=30)
        response = self.client.get(reverse('polls:index'))
        self.assertContains(response, "No polls are available.")
        self.assertQuerysetEqual(response.context['question_list'], [])

    def test_future_question_and_past_question(self):
        """
        Even if both past and future questions exist, only past questions
        are displayed.
        """
        create_question(question_text="Past question.", days=-30)
        create_question(question_text="Future question.", days=30)
        response = self.client.get(reverse('polls:index'))
        self.assertQuerysetEqual(
            response.context['question_list'],
            ['<Question: Past question.>']
        )

    def test_two_past_questions(self):
        """
        The questions index page may display multiple questions.
        """
        create_question(question_text="Past question 1.", days=-30)
        create_question(question_text="Past question 2.", days=-5)
        response = self.client.get(reverse('polls:index'))
        self.assertQuerysetEqual(
            response.context['question_list'],
            ['<Question: Past question 2.>', '<Question: Past question 1.>']
        )


class QuestionDetailViewTests(TestCase):
    def test_future_question(self):
        future_question = create_question('foo bar', +10)
        response = self.client.get(reverse('polls:detail', args=(future_question.id,)))
        self.assertEqual(response.status_code, 404)

    def test_past_question(self):
        past_question = create_question('foo bar', -10)
        response = self.client.get(reverse('polls:detail', args=(past_question.id,)))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, past_question.question_text)


class QuestionDetailViewUi(StaticLiveServerTestCase):

    @classmethod
    def setUpClass(cls):
        super(QuestionDetailViewUi, cls).setUpClass()
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--window-size=1920x1080")
        cls.selenium = WebDriver(chrome_options=chrome_options)
        cls.selenium.implicitly_wait(10)

    @classmethod
    def tearDownClass(cls):
        cls.selenium.quit()
        super(QuestionDetailViewUi, cls).tearDownClass()

    def test_load_question_from_index(self):
        question = Question(pub_date=timezone.now() - datetime.timedelta(days=3), question_text='Foo Bar')
        question.save()

        self.selenium.get('%s%s' % (self.live_server_url, reverse('polls:index')))
        self.selenium.find_element_by_css_selector('a[data-question-id="{}"]'.format(question.id)).click()
        # Wait until the response is received
        WebDriverWait(self.selenium, 2).until(
           lambda driver: driver.find_element_by_tag_name('body'))
