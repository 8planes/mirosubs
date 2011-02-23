class OpenIDMiddleware(object):
    """
    Populate request.openid and request.openids with their openid. This comes 
    either from their cookie or from their session, depending on the presence 
    of OPENID_USE_SESSIONS.
    """
    def process_request(self, request):
        request.openids = request.session.get('openids', [])
        if 'sessionid' in request.COOKIES:
            print("OpenIDMiddleware sessionid: {0}".format(
                    request.COOKIES['sessionid']))
        print("OpenIDMiddleware request.path: {0}".format(request.path))
        print("OpenIDMiddleware request.openids: {0}".format(request.openids))
        if request.openids:
            request.openid = request.openids[-1] # Last authenticated OpenID
        else:
            request.openid = None
