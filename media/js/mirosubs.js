goog.provide('mirosubs');

mirosubs.BASE_LOGIN_URL = "";

/**
 *
 * @param finishFn {Function} Called if logged in successfully.
 */
mirosubs.login = function(finishFn) {
    if (mirosubs.currentUsername != null) {
        if (finishFn)
            finishFn();
        return;
    }

    mirosubs.loginDialog_ = new goog.ui.Dialog("mirosubs-modal-dialog", true);
    var buttonContainer = new goog.ui.Component();
    buttonContainer.addChild(mirosubs.loginButton_ = 
                             new goog.ui.Button("Login"), true);
    buttonContainer.addChild(mirosubs.twitterLoginButton_ = 
                             new goog.ui.Button("Twitter Login"), true);
    buttonContainer.addChild(mirosubs.openidLoginButton_ = 
                             new goog.ui.Button("OpenID Login"), true);
    goog.array.forEach([mirosubs.loginButton_, 
                        mirosubs.twitterLoginButton_, 
                        mirosubs.openidLoginButton_],
                       function(button) {
                           goog.events.listen(button,
                                              goog.ui.Component.EventType.ACTION,
                                              function(event) {
                                                  mirosubs.loginClicked_(event, finishFn);
                                              });
                       });
    mirosubs.loginDialog_.addChild(buttonContainer, true);
    mirosubs.loginDialog_.setButtonSet(null);
    mirosubs.loginDialog_.setTitle("Login or Sign Up");
    mirosubs.loginDialog_.setVisible(true);
};

mirosubs.isLoginDialogShowing = function() {
    return (mirosubs.loginDialog_ != null && mirosubs.loginDialog_.isVisible());
};

mirosubs.logout = function() {
    mirosubs.Rpc.call('logout', {}, function(result) {
            mirosubs.currentUsername = null;
            mirosubs.updateLoginState_();
        });
};

mirosubs.loginClicked_ = function(event, finishFn) {
    var popupParams = 'location=0,status=0,width=800,height=400';
    var urlSuffix;
    if (event.target == this.loginButton_)
        urlSuffix = "login/?next=/widget/close_window/";
    else if (event.target == this.twitterLoginButton_)
        urlSuffix = "twitter_login/";
    else
        urlSuffix = "openid_login/";
    var loginWin = window.open(mirosubs.BASE_LOGIN_URL + urlSuffix,
                               "loginWindow",
                               popupParams);
    var timer = {};
    timer.interval = window.setInterval(function() {
            if (loginWin.closed) {
                window.clearInterval(timer.interval);
                mirosubs.postPossiblyLoggedIn_(finishFn);
            }
        }, 1000);
};

mirosubs.updateLoginState_ = function() {
    goog.array.forEach(mirosubs.CaptionWidget.widgets,
                       function(w) { w.updateLoginState(); });
};

mirosubs.postPossiblyLoggedIn_ = function(finishFn) {
    mirosubs.Rpc.call("getMyUserInfo", {}, function(result) {
            mirosubs.loginDialog_.setVisible(false);
            mirosubs.loginDialog_.dispose();
            mirosubs.loginDialog_ = null;
            if (result["logged_in"]) {
                mirosubs.currentUsername = result["username"];
                mirosubs.updateLoginState_();
                if (finishFn != null)
                    finishFn();
            }
        });
};

// see http://code.google.com/closure/compiler/docs/api-tutorial3.html#mixed
window["mirosubs"] = mirosubs;
mirosubs["xdSendResponse"] = goog.net.CrossDomainRpc.sendResponse;
mirosubs["xdRequestID"] = goog.net.CrossDomainRpc.PARAM_ECHO_REQUEST_ID;
mirosubs["xdDummyURI"] = goog.net.CrossDomainRpc.PARAM_ECHO_DUMMY_URI;
