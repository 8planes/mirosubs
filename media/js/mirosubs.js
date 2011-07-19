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
 * Set when widget gets initial state from server. All available languages.
 * Each member is a two-element array, with language code first then 
 * language name.
 * @type {Array.<Array>}
 */
mirosubs.languages = null;

/**
 * Set when widget gets initial state from server. All available languages.
 * Each member is a two-element array, with language code first then 
 * language name.
 * @type {Array.<Array>}
 */
mirosubs.metadataLanguages = null;

mirosubs.languageMap_ = null;

/**
 * some languages, like metadata languages, are forked by default.
 *
 */
mirosubs.isForkedLanguage = function(languageCode) {
    return null != goog.array.find(
        mirosubs.metadataLanguages,
        function(lang) { return lang[0] == languageCode; });
};

mirosubs.languageNameForCode = function(code) {
    if (mirosubs.languageMap_ == null) {
        mirosubs.languageMap_ = {};
        for (var i = 0; i < mirosubs.languages.length; i++)
            mirosubs.languageMap_[mirosubs.languages[i][0]] = 
                mirosubs.languages[i][1];
        for (var i = 0; i < mirosubs.metadataLanguages.length; i++)
            mirosubs.languageMap_[mirosubs.metadataLanguages[i][0]] =
                mirosubs.metadataLanguages[i][1];
    }
    return mirosubs.languageMap_[code];
};

mirosubs.dateString = function() {
    return new Date().toUTCString();
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
 * Set during loading. If true, this means we are supposed to open the fancy 
 * debug window. Note that the window will not open if goog.DEBUG is false 
 * (we set this to false in an option passed to the compiler for production)
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
 * @param {function()=} opt_errorFn Will be called if post-call to
 *     fetch user info errors out.
 */
mirosubs.openLoginPopup = function(loginPopupType, opt_finishFn, opt_errorFn) {
    var loginWin = window.open(mirosubs.siteURL() + loginPopupType[0],
                               mirosubs.randomString(),
                               loginPopupType[1]);
    var timer = new goog.Timer(250);
    goog.events.listen(
        timer, goog.Timer.TICK,
        function(e) {
            if (loginWin.closed) {
                timer.dispose();
                mirosubs.postPossiblyLoggedIn_(opt_finishFn, opt_errorFn);
            }
        });
    timer.start();
    return loginWin;
};
mirosubs.postPossiblyLoggedIn_ = function(opt_finishFn, opt_errorFn) {
    mirosubs.Rpc.call(
        'get_my_user_info', {},
        function(result) {
            mirosubs.loginAttemptInProgress_ = false;
            if (result['logged_in'])
                mirosubs.loggedIn(result['username']);
            if (opt_finishFn)
                opt_finishFn(result['logged_in']);
        },
        function() {
            if (opt_errorFn)
                opt_errorFn();
        });
};

mirosubs.loggedIn = function(username) {
    mirosubs.currentUsername = username;
    mirosubs.userEventTarget.dispatchEvent(
        new mirosubs.LoginEvent(mirosubs.currentUsername));
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
 *
 * @param {Element} topElem
 * @param {Element} bottomElem should have display: hidden when 
 *     this is called.
 */
mirosubs.attachToLowerLeft = function(topElem, bottomElem) {
    // This is a little hacky so that we can position with minimal
    // flicker.
    mirosubs.style.setVisibility(bottomElem, false);
    mirosubs.style.showElement(bottomElem, true);
    mirosubs.repositionToLowerLeft(topElem, bottomElem);
    mirosubs.style.setVisibility(bottomElem, true);
};

mirosubs.repositionToLowerLeft = function(anchorElement, movableElement) {
    // a lot of this code is from goog.positioning.positionAtAnchor.
    
    // Ignore offset for the BODY element unless its position is non-static.
    // For cases where the offset parent is HTML rather than the BODY (such as in
    // IE strict mode) there's no need to get the position of the BODY as it
    // doesn't affect the page offset.
    var moveableParentTopLeft;
    var parent = movableElement.offsetParent;
    if (parent) {
        var isBody = parent.tagName == goog.dom.TagName.HTML ||
            parent.tagName == goog.dom.TagName.BODY;
        if (!isBody ||
            goog.style.getComputedPosition(parent) != 'static') {
            // Get the top-left corner of the parent, in page coordinates.
            moveableParentTopLeft = goog.style.getPageOffset(parent);

            if (!isBody) {
                moveableParentTopLeft = goog.math.Coordinate.difference(
                    moveableParentTopLeft,
                    new goog.math.Coordinate(
                        parent.scrollLeft, parent.scrollTop));
            }
        }
    }

    // here is where this significantly differs from goog.positioning.atAnchor.
    var anchorRect = goog.style.getBounds(anchorElement);

    // Translate anchorRect to be relative to movableElement's page.
    goog.style.translateRectForAnotherFrame(
        anchorRect,
        goog.dom.getDomHelper(anchorElement),
        goog.dom.getDomHelper(movableElement));

    var absolutePos = new goog.math.Coordinate(
        anchorRect.left, anchorRect.top + anchorRect.height);

    // Translate absolutePos to be relative to the offsetParent.
    if (moveableParentTopLeft) {
        absolutePos =
            goog.math.Coordinate.difference(absolutePos, moveableParentTopLeft);
    }

    return goog.positioning.positionAtCoordinate(
        absolutePos, movableElement, goog.positioning.Corner.TOP_LEFT);
};

/**
 * Checks whether we are embedded in a non-PCF domain.
 */
mirosubs.isEmbeddedInDifferentDomain = function() {
    return mirosubs.siteConfig != null;
};

mirosubs.isReturnURLInDifferentDomain = function() {
    if (!mirosubs.returnURL)
        return false;
    var uri = new goog.Uri(mirosubs.returnURL);
    var myURI = new goog.Uri(window.location);
    return uri.getDomain().toLowerCase() != 
        myURI.getDomain().toLowerCase();
};

mirosubs.isFromDifferentDomain = function() {
    return mirosubs.isEmbeddedInDifferentDomain() || 
        mirosubs.isReturnURLInDifferentDomain();
};

/**
 * @constructor
 */
mirosubs.LoginEvent = function(username) {
    this.type = mirosubs.EventType.LOGIN;
    this.username = username;
};

mirosubs.getSubtitleHomepageURL = function(videoID) {
    return [mirosubs.siteURL(), "/videos/", videoID].join('');
};

mirosubs.getVolunteerPageURL = function(){
    return [mirosubs.siteURL(), "/videos/volunteer/"].join('');
}

mirosubs.createLinkButton = function($d, text, opt_className) {
    var atts = { 'href': 'javascript:void(0);' };
    if (opt_className)
        atts['className'] = opt_className;
    return $d('a', atts, text);
};

mirosubs.saveInLocalStorage = function(key, value) {
    if (goog.DEBUG) {
        mirosubs.logger_.info(
            "Saving local storage, key: " + key + 
                " and value " + value);
    }
    window['localStorage']['setItem'](key, value);
};

mirosubs.fetchFromLocalStorage = function(key) {
    if (goog.DEBUG) {
        mirosubs.logger_.info(
            "Fetching local storage, key: " + key + 
                " and value " + 
                window['localStorage']['getItem'](key));
    }
    return window['localStorage']['getItem'](key);
};

mirosubs.removeFromLocalStorage = function(key) {
    if (goog.DEBUG) {
        mirosubs.logger_.info("Removing " + key + " from localStorage.");
    }
    window['localStorage']['removeItem'](key);
};

if (goog.DEBUG) {
    mirosubs.logger_ = goog.debug.Logger.getLogger('mirosubs');
}
