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
    if (myURI.getParameterValue('debug_mirosubs_js') == 'true' &&
       window.name != DEBUG_WIN_NAME) {
        var debugWindow = new goog.debug.FancyWindow(DEBUG_WIN_NAME);
        debugWindow.setEnabled(true);
        debugWindow.init();
        mirosubs.DEBUG = true;
    }
    this.makers_ = [
        new mirosubs.widgetizer.Youtube(),
        new mirosubs.widgetizer.HTML5()
    ];
};
goog.addSingletonGetter(mirosubs.Widgetizer);

mirosubs.Widgetizer.logger_ = 
    goog.debug.Logger.getLogger('mirosubs.Widgetizer');

/**
 * Converts all videos in the page to Mirosubs widgets.
 *
 */
mirosubs.Widgetizer.prototype.widgetize = function() {
    mirosubs.Widgetizer.logger_.info('widgetize called');
    mirosubs.Widgetizer.logger_.info(
        'is dom loaded: ' +
            (mirosubs.LoadingDom.getInstance().isDomLoaded() ? 
             'true' : 'false'));
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

mirosubs.Widgetizer.prototype.videosExist = function() {
    for (var i = 0; i < this.makers_.length; i++)
        if (this.makers_[i].videosExist())
            return true;
    return false;
}

mirosubs.Widgetizer.prototype.onLoaded_ = function() {
    mirosubs.Widgetizer.logger_.info('onLoaded_ called');
    this.addHeadCss();
    this.findAndWidgetizeElements_();
};

mirosubs.Widgetizer.prototype.findAndWidgetizeElements_ = function() {
    var videoPlayers = [];
    for (var i = 0; i < this.makers_.length; i++)
        goog.array.extend(videoPlayers, 
                          this.makers_[i].makeVideoPlayers());
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

mirosubs.Widgetizer.prototype.widgetizeElem_ = function(elem, videoURL) {
    mirosubs.Widgetizer.logger_.info('widgetizeElem_ called for ' + videoURL);
    var containingElement = document.createElement('div');
    var styleElement = document.createElement('style');
    var innerStyle = mirosubs.Config.innerStyle;
    if ('textContent' in styleElement)
        styleElement.textContent = innerStyle;
    else {
        // IE
        styleElement.setAttribute("type", "text/css");
        styleElement.styleSheet.cssText = innerStyle;
    }
    containingElement.appendChild(styleElement);
    var widgetDiv = document.createElement('div');
    widgetDiv.className = 'mirosubs-widget';
    containingElement.appendChild(widgetDiv);

    var parentElem = elem.parentNode;
    parentElem.insertBefore(containingElement, elem);
    parentElem.removeChild(elem);
    var widgetConfig = { 'video_url': videoURL };
    mirosubs.widget.CrossDomainEmbed.embed(
        widgetDiv, widgetConfig, mirosubs.Config.siteConfig);
};
