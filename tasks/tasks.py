from tasks.models import Task, UserProfile
from datetime import datetime, timedelta
import time

from django.contrib.auth.models import User
from django.core.mail import send_mail

from celery.decorators import periodic_task
from celery.schedules import crontab
from task_manager.celery import app


def mail_user(user: User):
    tasks = Task.objects.filter(user=user)
    pending = tasks.filter(status="PENDING").count()
    in_progress = tasks.filter(status="IN_PROGRESS").count()
    completed = tasks.filter(status="COMPLETED").count()
    cancelled = tasks.filter(status="CANCELLED").count()

    message = f"""Hey {user.username}!
    You have {pending} tasks pending, {in_progress} in progress and you have {completed} completed tasks. You also have cancelled {cancelled} tasks.

    You have recorded a total of {tasks.count()} tasks from your account. Thanks for using Task Manager!
    """
    send_mail("Task notifications", message, "admin@taskmanager.com", [user.email])


@periodic_task(run_every=timedelta(hours=1))
def monitor_mail_times():
    print("Fetching mail addresses and configuring send times...")
    times = UserProfile.objects.all().order_by("user_id")
    users = User.objects.all().order_by("id")

    for i, element in enumerate(users):
        if times[i].hour == datetime.now().hour:
            # app.add_periodic_task(
            #     crontab(hour=datetime.now().hour, minute=datetime.now().minute + 1),
            #     mail_user(element),
            # )
            mail_user(element)

    return users.count()
