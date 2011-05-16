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

goog.provide('mirosubs.widgetizer.JWPlayer');

/**
 * @constructor
 *
 */
mirosubs.widgetizer.JWPlayer = function() {
    mirosubs.widgetizer.VideoPlayerMaker.call(this);
    this.VIDS_ARE_JW_ =
        window.location.hostname.match(/ocw\.mit\.edu/) != null ||
        window['UNISUBS_JW_ONLY'];
    this.logger_ =
        goog.debug.Logger.getLogger('mirosubs.widgetizer.JWPlayer');
};
goog.inherits(
    mirosubs.widgetizer.JWPlayer,
    mirosubs.widgetizer.VideoPlayerMaker);

mirosubs.widgetizer.JWPlayer.prototype.videosExist = function() {
    return this.unwidgetizedElements_().length > 0;
};

mirosubs.widgetizer.JWPlayer.prototype.makeVideoPlayers = function() {
    var elements = this.unwidgetizedElements_();
    if (goog.DEBUG) {
        this.logger_.info("Found this number of unwidgetized elements: " + 
                          elements.length);
    }
    var videoPlayers = [];
    for (var i = 0; i < elements.length; i++) {
        var videoSource = this.makeVideoSource_(elements[i]);
        var videoPlayer = new mirosubs.video.JWVideoPlayer(videoSource);
        videoPlayers.push(videoPlayer);
        videoPlayer.decorate(elements[i]);
    }
    return videoPlayers;
};

mirosubs.widgetizer.JWPlayer.prototype.makeVideoSource_ = function(elem) {
    this.logger_.info('flashvars: ' + this.flashVars(elem));
    var matches = /file=([^&]+)/.exec(this.flashVars(elem));
    this.logger_.info('matched url: ' + matches[1]);
    return mirosubs.video.YoutubeVideoSource.forURL(matches[1]);
};

mirosubs.widgetizer.JWPlayer.prototype.unwidgetizedElements_ = function() {
    return mirosubs.widgetizer.JWPlayer.superClass_.
        unwidgetizedFlashElements.call(this);
};

mirosubs.widgetizer.JWPlayer.prototype.isFlashElementAPlayer = function(element) {    
    var swfSrc = this.swfURL(element);
    var isJW = this.VIDS_ARE_JW_ && swfSrc.match(/player[^\.]*.swf$/i) != null;
    this.logger_.info(
        'encountered possible swf: ' + swfSrc + '. It is ' + 
            (isJW ? '' : 'not ') + 'a JWPlayer');
    return isJW;
};