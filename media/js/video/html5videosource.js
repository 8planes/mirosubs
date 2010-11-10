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

goog.provide('mirosubs.video.Html5VideoSource');

/**
 * @constructor
 * @implements {mirosubs.video.VideoSource}
 * @param {string} videoURL
 * @param {mirosubs.video.Html5VideoType} videoType
 * @param {Object.<string, string>=} opt_videoConfig Attributes to use for 
 *     video element, plus optional 'click_to_play' parameter
 */
mirosubs.video.Html5VideoSource = function(videoURL, videoType, opt_videoConfig) {
    this.videoURL_ = videoURL;
    this.videoType_ = videoType;
    this.videoConfig_ = opt_videoConfig;
};

mirosubs.video.Html5VideoSource.forURL = function(videoURL, opt_videoConfig) {
    var queryStringIndex = videoURL.indexOf('?');
    if (queryStringIndex > -1)
        videoURL = videoURL.substring(0, queryStringIndex);
    var vt = mirosubs.video.Html5VideoType;
    var videoType = null;
    if (/\.ogv$|\.ogg$/.test(videoURL))
        videoType = vt.OGG;
    else if (/\.mp4$|\.m4v$/.test(videoURL))
        videoType = vt.H264;
    else if (/\.webm$/.test(videoURL))
        videoType = vt.WEBM;
    if (videoType != null)
        return new mirosubs.video.Html5VideoSource(
            videoURL, videoType, opt_videoConfig);
    else
        return null;
};

mirosubs.video.Html5VideoSource.prototype.isBestVideoSource = function() {
    if (this.videoType_ == mirosubs.video.Html5VideoType.H264 && 
        (mirosubs.video.supportsOgg() || mirosubs.video.supportsWebM()))
        return false;
    return mirosubs.video.supportsVideoType(this.videoType_);
};

mirosubs.video.Html5VideoSource.prototype.createPlayer = function() {
    return this.createPlayer_(false);
};

mirosubs.video.Html5VideoSource.prototype.createControlledPlayer = 
    function() 
{
    return new mirosubs.video.ControlledVideoPlayer(
        this.createPlayer_(true));
};

mirosubs.video.Html5VideoSource.prototype.createPlayer_ = 
    function(forSubDialog) 
{
    if (this.videoType_ == mirosubs.video.Html5VideoType.H264 && 
        !mirosubs.video.supportsH264())
        return new mirosubs.video.FlvVideoPlayer(this, forSubDialog);
    else
        return new mirosubs.video.Html5VideoPlayer(
            new mirosubs.video.Html5VideoSource(
                this.videoURL_, this.videoType_, this.videoConfig_), 
            forSubDialog);
};

mirosubs.video.Html5VideoSource.prototype.getFlvURL = function() {
    if (this.videoType_ != mirosubs.video.Html5VideoType.H264)
        throw new Error();
    return this.videoURL_;
};

mirosubs.video.Html5VideoSource.prototype.getVideoURL = function() {
    return this.videoURL_;
};

mirosubs.video.Html5VideoSource.prototype.getVideoType = function() {
    return this.videoType_;
};

mirosubs.video.Html5VideoSource.prototype.getVideoConfig = function() {
    return this.videoConfig_;
};

mirosubs.video.Html5VideoSource.prototype.setVideoConfig = function(config) {
    this.videoConfig_ = config;
};
