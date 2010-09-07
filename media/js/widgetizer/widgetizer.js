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
    this.widgetizeBound_ = false;
    this.widgetized_ = false;
};
goog.addSingletonGetter(mirosubs.Widgetizer);

/**
 * Converts all videos in the page to Mirosubs widgets.
 *
 */
mirosubs.Widgetizer.prototype.widgetize = function() {
    if (this.widgetizeBound_)
        return;
    this.widgetizeBound_ = true;
    if (document.readyState == "complete")
        this.onLoaded_();
    else
        this.addReadyEventListener_();
};

mirosubs.Widgetizer.prototype.addReadyEventListener_ = function() {
    var that = this;
    if (document.addEventListener) {
        var EVENT = "DOMContentLoaded";
        document.addEventListener(
            EVENT,
            function() {
                document.removeEventListener(EVENT, arguments.callee, false);
                that.onLoaded_();
            }, false);
    }
    else if (document.attachEvent) {
        var EVENT = "onreadystatechange";
        // TODO: this code is copied from templates/widget/embed.js.
        // Possilby remove duplication in the future.
        document.attachEvent(EVENT, function() {
            if (document.readyState == "complete") {
                document.detachEvent(EVENT, arguments.callee);
                that.onLoaded_();
            }
        });
        if (document.documentElement.doScroll && window == window.top)
            (function() {
                if (that.widgetized_)
                    return;
                try {
                    // Thanks to Diego Perini: http://javascript.nwbox.com/IEContentLoaded/
                    document.documentElement.doScroll('left');
                }
                catch (error) {
                    setTimeout(arguments.callee, 0);
                    return;
                }
                that.onLoaded_();
            })();        
    }
    // in case nothing else works: load event
    goog.events.listen(window, goog.events.EventType.LOAD,
                       this.onLoaded_, false, this);
};

mirosubs.Widgetizer.prototype.onLoaded_ = function() {
    if (this.widgetized_)
        return;
    this.widgetized_ = true;
    this.addHeadCss_();
    this.findAndWidgetizeElements_();
};

mirosubs.Widgetizer.prototype.findAndWidgetizeElements_ = function() {
    // including some heuristics here for some of the bigger sites.
    if (window.location.hostname.match(/youtube\.com$/) != null) {
        this.widgetizeElem_(
            goog.dom.getElement('movie_player'),
            window.location.href);
    }
    else {
        this.widgetizeVideoElements_(
            this.filterWidgetized_(
                document.getElementsByTagName('video')));
        this.widgetizeObjectElements_(
            this.filterWidgetized_(
                document.getElementsByTagName('object')));
    }
};

mirosubs.Widgetizer.prototype.addHeadCss_ = function() {
    if (!window.MiroCSSLoading) {
        window.MiroCSSLoading = true;
        var head = document.getElementsByTagName('head')[0];
        var css = document.createElement('link');
        css.type = 'text/css';
        css.rel = 'stylesheet';
        css.href = mirosubs.WidgetizerConfig.siteConfig['mediaURL'] + 
            'css/mirosubs-widget.css';
        css.media = 'screen';
        head.appendChild(css);
    }
};

mirosubs.Widgetizer.prototype.filterWidgetized_ = function(elementArray) {
    var that = this;
    return goog.array.filter(
        elementArray,
        function(elem) {
            return !that.alreadyWidgetized_(elem);
        });
};

mirosubs.Widgetizer.prototype.alreadyWidgetized_ = function(elem) {
    // we consider it to be widgetized if it's contained in a widget div or
    // it's contained in the subtitling dialog.
    return goog.dom.getAncestorByTagNameAndClass(
        elem, 'div', 'mirosubs-widget') != null ||
        goog.dom.getAncestorByTagNameAndClass(
            elem, 'div', 'mirosubs-modal-widget') != null;
};

mirosubs.Widgetizer.prototype.widgetizeVideoElements_ = function(videoElems) {
    for (var i = 0; i < videoElems.length; i++)
        this.widgetizeElem_(videoElems[i], this.findHtml5URL_(videoElems[i]));
};

mirosubs.Widgetizer.prototype.widgetizeObjectElements_ = function(objectElems) {
    for (var i = 0; i < objectElems.length; i++) {
        var youtubeURL = this.findYoutubeURL_(objectElems[i]);
        if (youtubeURL != null)
            this.widgetizeElem_(objectElems[i], youtubeURL);
    }
};

mirosubs.Widgetizer.prototype.findHtml5URL_ = function(videoElem) {
    return videoElem.getElementsByTagName('source')[0].src;
};

mirosubs.Widgetizer.prototype.findYoutubeURL_ = function(objectElem) {
    var paramElems = objectElem.getElementsByTagName('param');
    for (var i = 0; i < paramElems.length; i++) {
        if (paramElems[i]["name"] == "movie" &&
            paramElems[i]["value"] != null &&
            mirosubs.video.VideoSource.isYoutube(paramElems[i]["value"]))
            return paramElems[i]["value"];
    }
    return null;
};

mirosubs.Widgetizer.prototype.widgetizeElem_ = function(elem, videoURL) {
    var containingElement = document.createElement('div');
    var styleElement = document.createElement('style');
    var innerStyle = mirosubs.WidgetizerConfig.innerStyle;
    if ('textContent' in styleElement)
        styleElement.textContent = innerStyle;
    else {
        // IE
        styleElement.setAttribute("type", "text/css")
        styleElement.styleSheet.cssText = innerStyle;
    }
    containingElement.appendChild(styleElement);
    var widgetDiv = document.createElement('div');
    widgetDiv.className = 'mirosubs-widget';
    containingElement.appendChild(widgetDiv);

    var parentElem = elem.parentNode;
    parentElem.insertBefore(containingElement, elem);
    parentElem.removeChild(elem);
    mirosubs.widget.CrossDomainEmbed.embed(
        widgetDiv, { 'video_url': videoURL }, mirosubs.WidgetizerConfig.siteConfig);
};

mirosubs.Widgetizer.getInstance().widgetize();