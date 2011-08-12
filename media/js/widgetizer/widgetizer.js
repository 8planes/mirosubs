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

goog.provide('mirosubs.Widgetizer');

/**
 * @constructor
 * This is a singleton, so don't call this method directly.
 */
mirosubs.Widgetizer = function() {
    mirosubs.siteConfig = mirosubs.Config.siteConfig;
    var myURI = new goog.Uri(window.location);
    var DEBUG_WIN_NAME = 'mirosubsdebuggingmain';
    if (goog.DEBUG) {
        var debugWindow = new goog.debug.FancyWindow(DEBUG_WIN_NAME);
        debugWindow.setEnabled(true);
        debugWindow.init();
        mirosubs.DEBUG = true;
    }
    this.makers_ = [
        new mirosubs.widgetizer.Youtube(),
        new mirosubs.widgetizer.HTML5(),
        new mirosubs.widgetizer.JWPlayer(),
        new mirosubs.widgetizer.YoutubeIFrame()
    ];
    this.logger_ = goog.debug.Logger.getLogger('mirosubs.Widgetizer');
};
goog.addSingletonGetter(mirosubs.Widgetizer);

/**
 * Converts all videos in the page to Mirosubs widgets.
 *
 */
mirosubs.Widgetizer.prototype.widgetize = function() {
    if (mirosubs.LoadingDom.getInstance().isDomLoaded()) {
        this.onLoaded_();
    }
    else {
        goog.events.listenOnce(
            mirosubs.LoadingDom.getInstance(),
            mirosubs.LoadingDom.DOMLOAD,
            this.onLoaded_, false, this);
    }
};

mirosubs.Widgetizer.prototype.onLoaded_ = function() {
    this.addHeadCss();
    this.widgetizeAttemptTimer_ = new goog.Timer(1000);
    this.widgetizeAttemptCount_ = 0;
    goog.events.listen(
        this.widgetizeAttemptTimer_,
        goog.Timer.TICK,
        goog.bind(this.findAndWidgetizeElements_, this));
    this.widgetizeAttemptTimer_.start();
};

mirosubs.Widgetizer.prototype.findAndWidgetizeElements_ = function() {
    this.widgetizeAttemptCount_++;
    if (this.widgetizeAttemptCount_ > 5) {
        this.widgetizeAttemptTimer_.stop();
        return;
    }
    if (goog.DEBUG) {
        this.logger_.info('finding and widgetizing elements');
    }
    var videoPlayers = [];
    for (var i = 0; i < this.makers_.length; i++)
        goog.array.extend(
            videoPlayers, 
            this.makers_[i].makeVideoPlayers());
    if (goog.DEBUG) {
        this.logger_.info('found ' + videoPlayers.length + 
                          ' new video players on the page');
    }
    for (var i = 0; i < videoPlayers.length; i++)
        mirosubs.widget.WidgetDecorator.decorate(videoPlayers[i]);
};

mirosubs.Widgetizer.prototype.addHeadCss = function() {
    if (!window.MiroCSSLoading) {
        window.MiroCSSLoading = true;
        var head = document.getElementsByTagName('head')[0];
        var css = document.createElement('link');
        css.type = 'text/css';
        css.rel = 'stylesheet';
        css.href = mirosubs.Config.siteConfig['mediaURL'] + 
            'css/mirosubs-widget.css';
        css.media = 'screen';
        head.appendChild(css);
    }
};
