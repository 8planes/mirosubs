from django.http import HttpResponse, Http404

from anyjson import serialize as JSON_dump

from celery.app import default_app
from celery.utils import get_full_cls_name
from celery.result import AsyncResult
from celery.registry import tasks
from celery.utils.functional import wraps

# Ensure built-in tasks are loaded for task_list view
import celery.task


def task_view(task):
    """Decorator turning any task into a view that applies the task
    asynchronously. Keyword arguments (via URLconf, etc.) will
    supercede GET or POST parameters when there are conflicts.

    Returns a JSON dictionary containing the keys ``ok``, and
        ``task_id``.

    """

    def _applier(request, **options):
        kwargs = request.method == "POST" and \
            request.POST.copy() or request.GET.copy()
        kwargs = dict((key.encode("utf-8"), value)
                    for key, value in kwargs.items())
        kwargs.update(options)

        result = task.apply_async(kwargs=kwargs)
        response_data = {"ok": "true", "task_id": result.task_id}
        return HttpResponse(JSON_dump(response_data),
                            mimetype="application/json")

    return _applier


def apply(request, task_name):
    """View applying a task.

    **Note:** Please use this with caution. Preferably you shouldn't make this
        publicly accessible without ensuring your code is safe!

    """
    try:
        task = tasks[task_name]
    except KeyError:
        raise Http404("apply: no such task")
    return task_view(task)(request)


def is_task_successful(request, task_id):
    """Returns task execute status in JSON format."""
    response_data = {"task": {"id": task_id,
                              "executed": AsyncResult(task_id).successful()}}
    return HttpResponse(JSON_dump(response_data), mimetype="application/json")


def task_status(request, task_id):
    """Returns task status and result in JSON format."""
    status = default_app.backend.get_status(task_id)
    res = default_app.backend.get_result(task_id)
    response_data = dict(id=task_id, status=status, result=res)
    if status in default_app.backend.EXCEPTION_STATES:
        traceback = default_app.backend.get_traceback(task_id)
        response_data.update({"result": repr(res),
                              "exc": get_full_cls_name(res.__class__),
                              "traceback": traceback})

    return HttpResponse(JSON_dump({"task": response_data}),
            mimetype="application/json")


def registered_tasks(request):
    """
    A view returning all defined tasks as a JSON object.
    """
    response_data = {"regular": tasks.regular().keys(),
                     "periodic": tasks.periodic().keys()}
    return HttpResponse(JSON_dump(response_data), mimetype="application/json")


def task_webhook(fun):
    """Decorator turning a function into a task webhook.

    If an exception is raised within the function, the decorated
    function catches this and returns an error JSON response, otherwise
    it returns the result as a JSON response.


    Example:

    .. code-block:: python

        @task_webhook
        def add(request):
            x = int(request.GET["x"])
            y = int(request.GET["y"])
            return x + y

        >>> response = add(request)
        >>> response.content
        '{"status": "success", "retval": 100}'

    """

    @wraps(fun)
    def _inner(*args, **kwargs):
        try:
            retval = fun(*args, **kwargs)
        except Exception, exc:
            response = {"status": "failure", "reason": str(exc)}
        else:
            response = {"status": "success", "retval": retval}

        return HttpResponse(JSON_dump(response), mimetype="application/json")

    return _inner
