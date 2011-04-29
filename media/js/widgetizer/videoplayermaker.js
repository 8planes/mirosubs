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

goog.provide('mirosubs.widgetizer.VideoPlayerMaker');

/**
 * Abstract base class for making AbstractVideoPlayers out of 
 * video-playing elements on the page.
 * @constructor
 */
mirosubs.widgetizer.VideoPlayerMaker = function() {
};

mirosubs.widgetizer.VideoPlayerMaker.prototype.videosExist = 
    goog.abstractMethod;

mirosubs.widgetizer.VideoPlayerMaker.prototype.makeVideoPlayers =
    goog.abstractMethod;

/**
 * @protected
 * @param {Array.<Element>} videoElements
 */
mirosubs.widgetizer.VideoPlayerMaker.prototype.filterUnwidgetized = 
    function(videoElements) 
{
    return goog.array.filter(
        videoElements,
        function(elem) { return this.isUnwidgetized(elem); }, this);
};

/**
 * @protected
 * @param {Element} element
 */
mirosubs.widgetizer.VideoPlayerMaker.prototype.isUnwidgetized = function(element) {
    return !goog.array.find(
        mirosubs.video.AbstractVideoPlayer.players,
        function(p) { return p.getVideoElement() == element; });
};

mirosubs.widgetizer.VideoPlayerMaker.prototype.swfURL = function(element) {
    return element.nodeName == 'EMBED' ? element['src'] : element['data'];
};

mirosubs.widgetizer.VideoPlayerMaker.prototype.flashVars = function(element) {
    if (element.nodeName == "EMBED") {
        return element['flashvars'];
    } else {
        var paramNode = goog.dom.findNode(
            element, 
            function(n) {
                return n.nodeName == "PARAM" && n['name'] == 'flashvars';
            });
        if (paramNode) {
            return paramNode['value'];
        }
    }
    return null;
};

mirosubs.widgetizer.VideoPlayerMaker.prototype.objectContainsEmbed = function(element) {
    return !!goog.dom.findNode(
        element,
        function(node) {
            return node.nodeName == "EMBED";
        });
};