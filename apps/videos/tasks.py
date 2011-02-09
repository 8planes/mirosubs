from celery.decorators import task

@task()
def add(x, y):
    print 'TASK IS EXECUTED WITH ARGUMENTS %s AND %s' % (x, y)
    return x + y
