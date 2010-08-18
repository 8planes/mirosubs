from django.conf import settings

class P3PHeaderMiddleware:
    def process_response(self, request, response):
        response['P3P'] = settings.P3P_COMPACT
        return response
