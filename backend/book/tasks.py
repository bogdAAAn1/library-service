from celery import shared_task


@shared_task
def add():
    x = 2
    y = 2
    return x + y