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
 * If a widget is embedded in a different domain, this is set by
 * mirosubs.widget.CrossDomainEmbed. It has two properties: siteURL
 * and mediaURL. It is non-null iff the widget is embedded in a 
 * different domain.
 */
mirosubs.siteConfig = null;

/**
 * Set when widget gets initial state from server, if user is logged in.
 * @type {string}
 */
mirosubs.currentUsername = null;

/**
 * URL to which the page should return after widget dialog closes.
 * This is a temporary setting to solve 
 * http://bugzilla.pculture.org/show_bug.cgi?id=13694 .
 * Only set for on-site widgets opened for Firefox workaround due
 * to video frame/background css performance problem.
 * @type {?string}
 */
mirosubs.returnURL = null;

/**
 * Current version of embed code. Set when widget gets inital 
 * state from server. Corresponds to value in settings.EMBED_JS_VERSION
 * in Django settings.py file.
 * @type {string}
 */
mirosubs.embedVersion = null;

/**
 * @type {string}
 * Set in widget constructor.
 */
mirosubs.videoURL = null;

mirosubs.embedCode = function() {
    return [
        '<sc',
        'ript type="text/javascript" src="',
        mirosubs.mediaURL(),
        'embed', mirosubs.embedVersion, '.js',
        '">\n',
        '({\n',
        '   video_url: "', mirosubs.videoURL, '"\n',
        '})\n',
        '</script>'].join('');
};

/**
 * Does not include trailing slash.
 */
mirosubs.siteURL = function() {
    return mirosubs.siteConfig ? mirosubs.siteConfig['siteURL'] : 
        (window.location.protocol + '//' + window.location.host);
};

/**
 * Includes trailing slash.
 */
mirosubs.mediaURL = function() {
    return mirosubs.siteConfig ? 
        mirosubs.siteConfig['mediaURL'] : window['MEDIA_URL'];
};

mirosubs.imageAssetURL = function(imageFileName) {
    return [mirosubs.mediaURL(), 'images/', imageFileName].join('');
};

/**
 * Set during loading.
 */
mirosubs.DEBUG = false;

/**
 * Set during loading.
 */
mirosubs.IS_NULL = false;

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
 * @param opt_message {String} Optional message to show at the top of the
 *     login dialog.
 */
mirosubs.login = function(opt_finishFn, opt_message) {
    if (mirosubs.currentUsername != null) {
        if (opt_finishFn)
            opt_finishFn(true);
        return;
    }

    var loginDialog = new mirosubs.LoginDialog(opt_finishFn, opt_message);
    loginDialog.setVisible(true);
};

mirosubs.LoginPopupType = {
    TWITTER: [
        '/widget/twitter_login/',
        'location=0,status=0,width=800,height=400'
    ],
    OPENID: [
        '/socialauth/openid/?next=/widget/close_window/',
        'scrollbars=yes,location=0,status=0,resizable=yes'
    ],
    GOOGLE: [
        '/socialauth/gmail_login/?next=/widget/close_window/',
        'scrollbars=yes,location=0,status=0,resizable=yes'
    ],
    NATIVE: [
        '/auth/login/?next=/widget/close_window/',
        'scrollbars=yes,location=0,status=0,resizable=yes'
    ]
};

/**
 * @param {mirosubs.LoginPopupType} loginPopupType
 * @param {function(boolean)=} opt_finishFn Will be called with true if
 *     logged in, false otherwise.
 */
mirosubs.openLoginPopup = function(loginPopupType, opt_finishFn) {
    var loginWin = window.open(mirosubs.siteURL() + loginPopupType[0],
                               mirosubs.randomString(),
                               loginPopupType[1]);
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
    mirosubs.openLoginPopup(mirosubs.LoginPopupType.NATIVE);
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

mirosubs.randomString = function() {
    var sb = [], i;
    for (i = 0; i < 10; i++)
        sb.push((10 + ~~(Math.random() * 26)).toString(36));
    return sb.join('') + (new Date().getTime() % 100000000);
};

/**
 * Checks whether we are embedded in a non-PCF domain.
 */
mirosubs.isEmbeddedInDifferentDomain = function() {
    return mirosubs.siteConfig != null;
};

mirosubs.LoginEvent = function(username) {
    this.type = mirosubs.EventType.LOGIN;
    this.username = username;
};
