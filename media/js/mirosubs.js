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

mirosubs.IMAGE_DIR = "/site_media/images/";

mirosubs.NATIVE_LOGIN_URL_SUFFIX = "/auth/login/?next=/widget/close_window/";

mirosubs.DEBUG = false;

mirosubs.EventType = {
    LOGIN : 'login',
    LOGOUT : 'logout'
};

mirosubs.userEventTarget = new goog.events.EventTarget();
mirosubs.loginAttemptInProgress_ = false;

/**
 *
 * @param opt_finishFn {function(boolean)=} Called when login process
 *     completes. Passed true if logged in successfully, false otherwise.
 */
mirosubs.login = function(opt_finishFn) {
    if (mirosubs.currentUsername != null) {
        if (opt_finishFn)
            opt_finishFn(true);
        return;
    }

    var loginDialog = new mirosubs.LoginDialog(opt_finishFn);
    loginDialog.setVisible(true);
};

/**
 *
 * @param {function(boolean)=} opt_finishFn Will be called with true if
 *     logged in, false otherwise.
 */
mirosubs.openLoginPopup = function(urlSuffix, opt_finishFn) {
    var popupParams = 'location=0,status=0,width=800,height=400';
    var loginWin = window.open(mirosubs.BASE_URL + urlSuffix,
                               "loginWindow",
                               popupParams);
    var timer = new goog.Timer(250);
    goog.events.listen(
        timer, goog.Timer.TICK,
        function(e) {
            if (loginWin.closed) {
                timer.dispose();
                mirosubs.postPossiblyLoggedIn_(opt_finishFn);
            }
        });
    timer.start();
};
mirosubs.postPossiblyLoggedIn_ = function(opt_finishFn) {
    mirosubs.Rpc.call(
        'get_my_user_info', {},
        function(result) {
            mirosubs.loginAttemptInProgress_ = false;
            if (result['logged_in']) {
                mirosubs.currentUsername = result['username'];
                mirosubs.userEventTarget.dispatchEvent(
                    new mirosubs.LoginEvent(mirosubs.currentUsername));
            }
            if (opt_finishFn)
                opt_finishFn(result['logged_in']);
        });
};

mirosubs.isLoginAttemptInProgress = function() {
    return mirosubs.loginAttemptInProgress_ ||
        mirosubs.LoginDialog.isCurrentlyShown();
};

mirosubs.createAccount = function() {
    mirosubs.loginAttemptInProgress_ = true;
    mirosubs.openLoginPopup(mirosubs.NATIVE_LOGIN_URL_SUFFIX);
};

mirosubs.logout = function() {
    mirosubs.Rpc.call('logout', {}, function(result) {
        mirosubs.currentUsername = null;
        mirosubs.userEventTarget.dispatchEvent(mirosubs.EventType.LOGOUT);
    });
};

mirosubs.formatTime = function(time, opt_excludeMs) {
    var intTime = parseInt(time);

    var timeString = '';
    var hours = (intTime / 3600) | 0;
    if (hours > 0)
        timeString += (hours + ':');
    var minutes = ((intTime / 60) | 0) % 60;
    if (minutes > 0 || hours > 0) {
        if (hours > 0)
            timeString += (goog.string.padNumber(minutes, 2) + ':');
        else
            timeString += (minutes + ':');
    }
    var seconds = intTime % 60;
    if (minutes > 0 || hours > 0)
        timeString += goog.string.padNumber(seconds, 2);
    else
        timeString += seconds;
    if (!opt_excludeMs) {
        var frac = parseInt(time * 100) % 100;
        timeString += ('.' + goog.string.padNumber(frac, 2));
    }
    return timeString;
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
