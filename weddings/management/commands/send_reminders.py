import datetime
from django.core.management.base import BaseCommand
from django.core.mail import send_mail
from django.utils import timezone
from django.conf import settings
from weddings.models import Wedding, Task, Reminder


class Command(BaseCommand):
    help = 'Отправляет напоминания о предстоящих задачах для свадеб'

    def handle(self, *args, **options):
        self.stdout.write('Проверка и отправка напоминаний...')

        today = timezone.now().date()

        self.send_upcoming_task_reminders(today)

        self.send_overdue_task_reminders(today)

        self.generate_future_reminders()

        self.stdout.write(self.style.SUCCESS('Напоминания успешно обработаны!'))

    def send_upcoming_task_reminders(self, today):
        reminder_days = [1, 3, 7, 14]

        for days in reminder_days:

            reminder_date = today + datetime.timedelta(days=days)

            tasks = Task.objects.filter(
                due_date=reminder_date,
                completed=False
            )

            for task in tasks:

                reminder_exists = Reminder.objects.filter(
                    task=task,
                    send_date__date=today,
                    sent=True
                ).exists()

                if not reminder_exists:
                    self.send_reminder_email(
                        task=task,
                        days_left=days,
                        is_overdue=False
                    )

                    Reminder.objects.create(
                        task=task,
                        send_date=timezone.now(),
                        sent=True
                    )

    def send_overdue_task_reminders(self, today):
        overdue_tasks = Task.objects.filter(
            due_date__lt=today,
            completed=False
        )
        for task in overdue_tasks:
            reminder_exists = Reminder.objects.filter(
                task=task,
                send_date__date=today,
                sent=True
            ).exists()
            if not reminder_exists:

                days_overdue = (today - task.due_date).days

                if days_overdue in [1, 3, 7] or days_overdue % 7 == 0:
                    self.send_reminder_email(
                        task=task,
                        days_left=-days_overdue,
                        is_overdue=True
                    )

                    Reminder.objects.create(
                        task=task,
                        send_date=timezone.now(),
                        sent=True
                    )

    def generate_future_reminders(self):

        weddings = Wedding.objects.all()

        for wedding in weddings:
            tasks = Task.objects.filter(
                wedding=wedding,
                completed=False,
                due_date__gt=timezone.now().date()
            )

            for task in tasks:
                reminder_days = [1, 3, 7, 14]

                for days in reminder_days:
                    reminder_date = task.due_date - datetime.timedelta(days=days)

                    if reminder_date > timezone.now().date():
                        reminder, created = Reminder.objects.get_or_create(
                            task=task,
                            send_date=datetime.datetime.combine(
                                reminder_date,
                                datetime.time(9, 0)
                            ),
                            sent=False
                        )

    def send_reminder_email(self, task, days_left, is_overdue):
        user = task.wedding.user

        if is_overdue:
            subject = f'ВАЖНО: Задача "{task.title}" просрочена на {abs(days_left)} дней!'
            message = f"""
            Здравствуйте, {user.first_name or user.username}!

            Напоминаем, что задача "{task.title}" просрочена на {abs(days_left)} дней!

            Описание задачи: {task.description}
            Срок выполнения был: {task.due_date.strftime('%d.%m.%Y')}

            Пожалуйста, выполните задачу как можно скорее или обновите её статус в вашем кабинете.

            С наилучшими пожеланиями,
            Команда Wedding Planner
            """
        else:
            subject = f'Напоминание: Задача "{task.title}" должна быть выполнена через {days_left} дней'
            message = f"""
            Здравствуйте, {user.first_name or user.username}!

            Напоминаем вам о предстоящей задаче "{task.title}", которую необходимо выполнить через {days_left} дней.

            Описание задачи: {task.description}
            Срок выполнения: {task.due_date.strftime('%d.%m.%Y')}

            С наилучшими пожеланиями,
            Команда Wedding Planner
            """

        from_email = settings.DEFAULT_FROM_EMAIL
        recipient_list = [user.email]

        if settings.DEBUG:
            self.stdout.write(f"Отправка письма на {user.email}: {subject}")
            self.stdout.write(message)
        else:

            send_mail(subject, message, from_email, recipient_list)