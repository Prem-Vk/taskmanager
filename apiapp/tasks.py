from taskmanager.celery import app


@app.task()
def add(x, y):
    """
    A simple task that adds two numbers.
    """
    return x + y

