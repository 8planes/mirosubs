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

goog.provide('mirosubs.video.VimeoIFrameVideoPlayer');

/**
 * @constructor
 * @param {mirosubs.video.VimeoIFrameVideoSource} videoSource
 * @param {boolean=} opt_forDialog
 */
mirosubs.video.VimeoIFrameVideoPlayer = function(videoSource, opt_forDialog) {
    

};
goog.inherits(mirosubs.video.VimeoIFrameVideoPlayer, mirosubs.video.AbstractVideoPlayer);

mirosubs.video.VimeoIFrameVideoPlayer.prototype.enterDocument = function() {
    mirosubs.video.VimeoIFrameVideoPlayer.superClass_.enterDocument.call(this);
    var checkFn = function() {
        return !!goog.global['Froogaloop'];
    };
    if (checkFn()) {
        this.makePlayer_();
    }
    else {
        mirosubs.addScript(
            'http://a.vimeocdn.com/js/froogaloop2.min.js',
            checkFn,
            goog.bind(this.makePlayer_, this));
    }
};

mirosubs.video.VimeoIFrameVideoPlayer.prototype.makePlayer_ = function() {
    if (goog.DEBUG) {
        this.logger_.info('makePlayer_ called');
    }
    this.almostPlayer_ = new goog.global['Froogaloop'](this.iframe_);
    this.almostPlayer_['addEvent'](
        'ready', goog.bind(this.playerReady_, this));
};

mirosubs.video.VimeoIFrameVideoPlayer.prototype.playerReady_ = function() {
    
};