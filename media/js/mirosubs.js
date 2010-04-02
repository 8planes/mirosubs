// Universal Subtitles, universalsubtitles.org
// 
// Copyright (C) 2010 Participatory Culture Foundation
// 
// This program is free software: you can redistribute it and/or modify
// it under the terms of the GNU Affero General Public License as
// published by the Free Software Foundation, either version 3 of the
// License, or (at your option) any later version.
// 
// This program is distributed in the hope that it will be useful,
// but WITHOUT ANY WARRANTY; without even the implied warranty of
// MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
// GNU Affero General Public License for more details.
// 
// You should have received a copy of the GNU Affero General Public License
// along with this program.  If not, see 
// http://www.gnu.org/licenses/agpl-3.0.html.

goog.provide('mirosubs');

/**
 * This ends up getting set when widget first loads. It contains the url 
 * for ms server, without trailing slash.
 */
mirosubs.BASE_URL = "";

mirosubs.NATIVE_LOGIN_URL_SUFFIX = "/auth/login/?next=/widget/close_window/";

mirosubs.EventType = {
    LOGIN : 'login',
    LOGOUT : 'logout'
};

mirosubs.userEventTarget = new goog.events.EventTarget();

/**
 * @type {boolean}
 */
mirosubs.loginAttemptInProgress_ = false;

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
                             new goog.ui.Button("Login/Create Account"), true);
    buttonContainer.addChild(mirosubs.twitterLoginButton_ = 
                             new goog.ui.Button("Twitter Login"), true);
    buttonContainer.addChild(mirosubs.openidLoginButton_ = 
                             new goog.ui.Button("OpenID Login"), true);
    goog.array.forEach(
        [mirosubs.loginButton_, 
         mirosubs.twitterLoginButton_, 
         mirosubs.openidLoginButton_],
        function(button) {
            goog.events.listen(
                button, goog.ui.Component.EventType.ACTION,
                function(event) {
                    mirosubs.loginClicked_(event, finishFn);
                });
        });
    mirosubs.loginDialog_.addChild(buttonContainer, true);
    mirosubs.loginDialog_.setButtonSet(null);
    mirosubs.loginDialog_.setTitle("Login or Sign Up");
    mirosubs.loginDialog_.setVisible(true);
};

mirosubs.isLoginAttemptInProgress = function() {
    return mirosubs.loginAttemptInProgress_ ||
        (mirosubs.loginDialog_ != null && 
         mirosubs.loginDialog_.isVisible());
};

mirosubs.createAccount = function() {
    mirosubs.loginAttemptInProgress_ = true;
    mirosubs.openLoginPopup_(mirosubs.NATIVE_LOGIN_URL_SUFFIX);
};

mirosubs.logout = function() {
    mirosubs.Rpc.call('logout', {}, function(result) {
        mirosubs.currentUsername = null;
        mirosubs.userEventTarget.dispatchEvent(mirosubs.EventType.LOGOUT);
    });
};

mirosubs.loginClicked_ = function(event, finishFn) {
    var urlSuffix;
    if (event.target == this.loginButton_)
        urlSuffix = mirosubs.NATIVE_LOGIN_URL_SUFFIX;
    else if (event.target == this.twitterLoginButton_)
        urlSuffix = "/widget/twitter_login/";
    else
        urlSuffix = "/socialauth/openid/?next=/widget/close_window/";    
    mirosubs.openLoginPopup_(urlSuffix, finishFn);
};

mirosubs.openLoginPopup_ = function(urlSuffix, opt_finishFn) {
    var popupParams = 'location=0,status=0,width=800,height=400';
    var loginWin = window.open(mirosubs.BASE_URL + urlSuffix,
                               "loginWindow",
                               popupParams);
    var timer = {};
    timer.interval = window.setInterval(function() {
        if (loginWin.closed) {
            window.clearInterval(timer.interval);
            mirosubs.postPossiblyLoggedIn_(opt_finishFn);
        }
    }, 1000);
};

mirosubs.postPossiblyLoggedIn_ = function(opt_finishFn) {
    mirosubs.Rpc.call("getMyUserInfo", {}, function(result) {
        if (mirosubs.loginDialog_ != null) {
            mirosubs.loginDialog_.setVisible(false);
            mirosubs.loginDialog_.dispose();
        }
        mirosubs.loginAttemptInProgress_ = false;
        mirosubs.loginDialog_ = null;
        if (result["logged_in"]) {
            mirosubs.currentUsername = result["username"];
            mirosubs.userEventTarget.dispatchEvent(
                new mirosubs.LoginEvent(mirosubs.currentUsername));
            if (opt_finishFn != null)
                opt_finishFn();
        }
    });
};

mirosubs.LoginEvent = function(username) {
    this.type = mirosubs.EventType.LOGIN;
    this.username = username;
};

// see http://code.google.com/closure/compiler/docs/api-tutorial3.html#mixed
window["mirosubs"] = mirosubs;
mirosubs["xdSendResponse"] = goog.net.CrossDomainRpc.sendResponse;
mirosubs["xdRequestID"] = goog.net.CrossDomainRpc.PARAM_ECHO_REQUEST_ID;
mirosubs["xdDummyURI"] = goog.net.CrossDomainRpc.PARAM_ECHO_DUMMY_URI;
