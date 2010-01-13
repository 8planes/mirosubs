goog.provide('mirosubs');

mirosubs.BASE_LOGIN_URL = "";

/**
 *
 * @param finishFn {Function} either called with username (if 
 *     logged in successfully), or null otherwise.
 */
mirosubs.login = function(finishFn) {
    var html = ['<div><iframe marginwidth="0" marginheight="0" hspace="0" ',
                'vspace="0" frameborder="0" allowtransparency="true" src="', 
                base_url,
                '"</iframe></div>'].join('');
    var dialog = new goog.ui.Dialog("mirosubs-modal-dialog", true);
    dialog.setButtonSet(null);
    dialog.setContent(html);
    dialog.setTitle("Login or Sign Up");
    dialog.setVisible(true);
};

mirosubs.twitter_login = function(twitter_login_url) {
    var popupParams = 'location=0,status=0,width=800,height=400';
    var twitterWin = window.open(twitter_login_url, 'twitterWindow', popupParams);
    var timer = {};
    timer.interval = window.setInterval(function() {
            if (twitterWin.closed) {
                window.clearInterval(timer.interval);
                window.location.reload();
            }
        }, 1000);
};

// see http://code.google.com/closure/compiler/docs/api-tutorial3.html#mixed
window["mirosubs"] = mirosubs;
mirosubs["xdSendResponse"] = goog.net.CrossDomainRpc.sendResponse;
mirosubs["xdRequestID"] = goog.net.CrossDomainRpc.PARAM_ECHO_REQUEST_ID;
mirosubs["xdDummyURI"] = goog.net.CrossDomainRpc.PARAM_ECHO_DUMMY_URI;
