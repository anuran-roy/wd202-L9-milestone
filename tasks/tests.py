from django.test import TestCase, Client
from tasks import utils, models, views, tasks
from task_manager.celery import every_30_seconds
from django.core import mail


class QuestionModelTests(TestCase):
    def test_authenticated(self):
        """
        Try to GET the tasks listing page, expect the response to redirect to the login page
        """
        response = self.client.get("/tasks/")
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, "/user/login?next=/tasks/")

    def test_isDiff(self):
        self.assertEqual(utils.IsDiff("hello", "hello"), False)

    def test_404(self):
        response = self.client.get("/rrubepfguwt/")
        self.assertEqual(response.status_code, 404)

    def test_correspondence(self):
        users = models.User.objects.all().count()
        profiles = models.UserProfile.objects.all().count()

        self.assertEqual(users, profiles)

    def test_slashAdd(self):
        response = self.client.get("/tasks")
        self.assertEqual(response.status_code, 301)
        self.assertEqual(response.url, "/tasks/")

    def test_choices(self):
        choices = models.STATUS_CHOICES
        self.assertEqual(len(choices), 4)

    def test_status_integrity(self):
        completed = models.Task.objects.filter(status="COMPLETED").count()
        cancelled = models.Task.objects.filter(status="CANCELLED").count()
        in_progress = models.Task.objects.filter(status="IN_PROGRESS").count()
        pending = models.Task.objects.filter(status="PENDING").count()
        all_obj = models.Task.objects.all().count()

        self.assertEqual(completed + cancelled + in_progress + pending, all_obj)

    def test_endpoints_authenticated(self):
        """
        Try to GET the tasks listing page, expect the response to redirect to the login page
        """
        response = self.client.get("/add-task/")
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, "/user/login?next=/add-task/")

        response = self.client.get("/completed_tasks/")
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, "/user/login?next=/completed_tasks/")

        response = self.client.get("/delete-task/1/")
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, "/user/login?next=/delete-task/1/")

        response = self.client.get("/update-task/1/")
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, "/user/login?next=/update-task/1/")

        response = self.client.get("/complete_task/1/")
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, "/user/login?next=/complete_task/1/")

    def test_session_storage(self):
        self.user = models.User.objects.create_user(
            email="a@a.co", password="1234", username="user1"
        )
        self.client.force_login(self.user)

        response = self.client.get("/")
        self.assertEqual(response.url, "/tasks")

        response = self.client.get("/sessiontest/")
        for i in range(10):
            response = self.client.get("/sessiontest/")

        self.assertEqual("10" in response._container[0].decode("utf-8"), True)

        response = self.client.get("/add-task")
        self.assertEqual(response.status_code, 301)

        response = self.client.get("/tasks/?search=lol")
        self.assertEqual(response.context_data["is_paginated"], False)
        # self.assertEqual(str(response), "django.template.response.TemplateResponse")

        response = self.client.get("/add-task/")
        self.assertEqual(
            "p-4 m-4 bg-gray-200/75" in response._container[0].decode("utf-8"), True
        )

        # response = self.client.get("/update-task/")
        # self.assertEqual(
        #     "p-4 m-4 bg-gray-200/75" in response._container[0].decode("utf-8"), True
        # )

        response = self.client.get("/user/logout/")
        self.assertEqual(response.url, "/")

        response = self.client.get("/user/login/")
        self.assertEqual(
            "p-4 m-4 bg-gray-200/75" in response._container[0].decode("utf-8"), True
        )

        response = self.client.get("/user/signup/")
        self.assertEqual(
            "p-4 m-4 bg-gray-200/75" in response._container[0].decode("utf-8"), True
        )

        tasks.mail_user(self.user)
        self.assertEqual(len(mail.outbox), 1)

        self.assertEqual(tasks.monitor_mail_times(), 1)

    def test_signup(self):
        response = self.client.get("/user/signup")
        self.assertEqual(response.url, "/user/signup/")

    def mail_time(self):
        obj = views.MailTimeUpdateView()
        self.assertTemplateUsed(obj.get(), "modify_mail_time.html")

    def test_celery(self):
        self.assertEqual(every_30_seconds(), "Running Every 30 Seconds!")
