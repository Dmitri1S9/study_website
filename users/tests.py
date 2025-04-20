import datetime
from django.urls import reverse
from django.test import TestCase
from .models import User
from django.contrib.messages import get_messages


class RegistrationTestcase(TestCase):
    def setUp(self):
        """
        Создаем тестового пользователя
        """
        data = {
            'username': 'test',
            'e-mail': 'test@gmail.com',
            'password': 'test123'
        }

        self.user = User.objects.create(
            username='test',
            email='test@gmail.com',
            password='test123'
        )
        self.registration_url = reverse('register')
        response = self.client.post(self.registration_url, data)

    def test_1_user_creation(self):
        """
        Проверяем, что пользователь создается корректно
        """
        self.assertEqual(UserPlayer.objects.count(), 1)  # Убедимся, что в базе один пользователь
        self.assertEqual(self.user.username, 'test')
        self.assertEqual(self.user.email, 'test@gmail.com')

    def test_2_correct_registration(self):
        """
        Проверяем успешную регистрацию с корректными данными
        """
        data = {
            'username': 'newuser',
            'email': 'newuser@gmail.com',
            'password': 'newpass123',
        }
        response = self.client.post(self.registration_url, data)
        self.assertEqual(response.status_code, 302)  # Проверяем, что запрос успешен
        # redirect_url = response.headers['Location']  # Получаем URL перенаправления
        # print(redirect_url)  # Выводим URL для проверки
        self.assertEqual(User.objects.count(), 2)  # Теперь два пользователя в базе

    def test_3_incorrect_registration_short_name(self):
        data = {
            'username': 't',
            'email': 'test1@gmail.com',
            'password': '1234245'
        }
        response = self.client.post(self.registration_url, data)
        self.assertEqual(response.status_code, 200)  # Проверяем, что запрос успешен
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(str(messages[0]), 'Слишком короткое имя')
        self.assertEqual(User.objects.count(), 1)  # Теперь два пользователя в базе

    def test_4_incorrect_registration_uniqueness_of_name(self):
        data = {
            'username': 'test',
            'email': 'test56@gmail.com',
            'password': '12342ef45'
        }
        response = self.client.post(self.registration_url, data)
        self.assertEqual(response.status_code, 200)  # Проверяем, что запрос успешен
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(str(messages[0]), 'Имя уже используется.')
        self.assertEqual(User.objects.count(), 1)  # Теперь два пользователя в базе

    def test_5_incorrect_registration_uniqueness_of_email(self):
        data = {
            'username': 'test23',
            'email': 'test@gmail.com',
            'password': '12342ef45'
        }
        response = self.client.post(self.registration_url, data)
        self.assertEqual(response.status_code, 200)  # Проверяем, что запрос успешен
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(str(messages[0]), 'Электронная почта уже используется.')
        self.assertEqual(User.objects.count(), 1)  # Теперь два пользователя в базе



# def create_question(question_text, days):
#     """
#     Create a question with the given `question_text` and published the
#     given number of `days` offset to now (negative for questions published
#     in the past, positive for questions that have yet to be published).
#     """
#     time = timezone.now() + datetime.timedelta(days=days)
#     return Question.objects.create(question_text=question_text, pub_date=time)
#
#
# class QuestionIndexViewTests(TestCase):
#     def test_no_questions(self):
#         """
#         If no questions exist, an appropriate message is displayed.
#         """
#         response = self.client.get(reverse("users:login"))
#         self.assertEqual(response.status_code, 200)
#         self.assertContains(response, "No polls are available.")
#         self.assertQuerySetEqual(response.context["latest_question_list"], [])
#
#     def test_past_question(self):
#         """
#         Questions with a pub_date in the past are displayed on the
#         index page.
#         """
#         question = create_question(question_text="Past question.", days=-30)
#         response = self.client.get(reverse("users:login"))
#         self.assertQuerySetEqual(
#             response.context["latest_question_list"],
#             [question],
#         )
#
#     def test_future_question(self):
#         """
#         Questions with a pub_date in the future aren't displayed on
#         the index page.
#         """
#         create_question(question_text="Future question.", days=30)
#         response = self.client.get(reverse("users:login"))
#         self.assertContains(response, "No polls are available.")
#         self.assertQuerySetEqual(
#             response.context["latest_question_list"],
#             [],
#         )
#
#     def test_future_question_and_past_question(self):
#         """
#         Even if both past and future questions exist, only past questions
#         are displayed.
#         """
#         question = create_question(question_text="Past question.", days=-30)
#         create_question(question_text="Future question.", days=30)
#         response = self.client.get(reverse("users:login"))
#         self.assertQuerySetEqual(
#             response.context["latest_question_list"],
#             [question],
#         )
#
#     def test_two_past_questions(self):
#         """
#         The questions index page may display multiple questions.
#         """
#         question1 = create_question(question_text="Past question 1.", days=-30)
#         question2 = create_question(question_text="Past question 2.", days=-5)
#         response = self.client.get(reverse("users:login"))
#         self.assertQuerySetEqual(
#             response.context["latest_question_list"],
#             [question2, question1],
#         )
#
#
# class QuestionDetailViewTests(TestCase):
#     def test_future_question(self):
#         """
#         The detail view of a question with a pub_date in the future
#         returns a 404 not found.
#         """
#         future_question = create_question(question_text="Future question.", days=5)
#         url = reverse("users:detail", args=(future_question.id,))
#         response = self.client.get(url)
#         self.assertEqual(response.status_code, 404)
#
#     def test_past_question(self):
#         """
#         The detail view of a question with a pub_date in the past
#         displays the question's text.
#         """
#         past_question = create_question(question_text="Past Question.", days=-5)
#         url = reverse("users:detail", args=(past_question.id,))
#         response = self.client.get(url)
#         self.assertContains(response, past_question.question_text)
