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

mirosubs.widgetizer.VideoPlayerMaker.prototype.logger_ = 
    goog.debug.Logger.getLogger(
        'mirosubs.widgetizer.VideoPlayerMaker');

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
        function(p) { return p.videoElementsContain(element); });
};

/**
 * To be overridden by classes that widgetize flash-based video elements.
 * @protected
 * @returns {Boolean}
 */
mirosubs.widgetizer.VideoPlayerMaker.prototype.isFlashElementAPlayer = goog.abstractMethod;

/**
 * @protected
 */
mirosubs.widgetizer.VideoPlayerMaker.prototype.unwidgetizedFlashElements = function() {
    var unwidgetizedElements = [];
    var objects = goog.dom.getElementsByTagNameAndClass('object');
    for (var i = 0; i < objects.length; i++)
        if (this.isFlashElementAPlayer(objects[i]) &&
            this.isUnwidgetized(objects[i])) {
            unwidgetizedElements.push(objects[i]);
        }
    var embeds = goog.dom.getElementsByTagNameAndClass('embed');
    for (var i = 0; i < embeds.length; i++) {
        if (this.isFlashElementAPlayer(embeds[i]) &&
            this.isUnwidgetized(embeds[i]) &&
            !goog.array.contains(unwidgetizedElements, 
                                 embeds[i].parentNode))
            unwidgetizedElements.push(embeds[i]);
    }
    return unwidgetizedElements;
};

/**
 * @protected
 */
mirosubs.widgetizer.VideoPlayerMaker.prototype.objectContainsEmbed = function(element) {
    return !!goog.dom.findNode(
        element,
        function(node) {
            return node.nodeName == "EMBED";
        });
};