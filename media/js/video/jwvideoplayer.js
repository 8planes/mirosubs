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

goog.provide('mirosubs.video.JWVideoPlayer');

/**
 * @constructor
 * @param {mirosubs.video.YoutubeVideoSource} videoSource
 */
mirosubs.video.JWVideoPlayer = function(videoSource) {
    mirosubs.video.AbstractVideoPlayer.call(this, videoSource);
    this.logger_ = goog.debug.Logger.getLogger('mirosubs.video.JWPlayer');
    this.eventFunction_ = 'event' + mirosubs.randomString();
};
goog.inherits(mirosubs.video.JWVideoPlayer, mirosubs.video.AbstractVideoPlayer);

/**
 * This decorates an Object or Embed element.
 * @override
 * @param {Element} Object or Embed element to decorate
 */
mirosubs.video.JWVideoPlayer.prototype.decorateInternal = function(element) {
    mirosubs.video.JWVideoPlayer.superClass_.decorateInternal.call(this, element);
    this.player_ = element;
    this.playerSize_ = goog.style.getSize(element);
    this.setDimensionsKnownInternal();
    window[this.eventFunction_] = goog.bind(this.playerStateChanged_, this);
    var timer = new goog.Timer(250);
    var that = this;
    this.getHandler().listen(
        timer,
        goog.Timer.TICK,
        function(e) {
            if (that.player_['addModelListener']) {
                timer.stop();
                that.decoratedPlayerIsReady_();
            }
        });
    timer.start();
};
mirosubs.video.JWVideoPlayer.prototype.decoratedPlayerIsReady_ = function() {
    this.logger_.info('ready');
    this.player_['addModelListener']('STATE', this.eventFunction_);
};
mirosubs.video.JWVideoPlayer.prototype.getVideoSize = function() {
    return this.playerSize_;
};
mirosubs.video.JWVideoPlayer.prototype.playerStateChanged_ = function(data) {
    var newState = data['newstate'];
    this.logger_.info('statechanged: ' + newState);
};