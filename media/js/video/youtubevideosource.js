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

goog.provide('mirosubs.video.YoutubeVideoSource');

/**
 * @constructor
 * @implements {mirosubs.video.VideoSource}
 * @param {string} youtubeVideoID Youtube video id
 * @param {Object.<string, *>=} opt_videoConfig Params to use for 
 *     youtube query string, plus optional 'width' and 'height' 
 *     parameters.
 */
mirosubs.video.YoutubeVideoSource = function(youtubeVideoID, opt_videoConfig) {
    this.youtubeVideoID_ = youtubeVideoID;
    this.uuid_ = mirosubs.randomString();
    this.videoConfig_ = opt_videoConfig;
};

mirosubs.video.YoutubeVideoSource.forURL = 
    function(videoURL, opt_videoConfig) 
{
    var videoIDExtract = /v[\/=]([0-9a-zA-Z\-\_]+)/i.exec(videoURL);
    if (videoIDExtract)
        return new mirosubs.video.YoutubeVideoSource(
            videoIDExtract[1], opt_videoConfig);
    else
        return null;
};

mirosubs.video.YoutubeVideoSource.isYoutube = function(videoURL) {
    return /^\s*https?:\/\/([^\.]+\.)?youtube/i.test(videoURL);
};

mirosubs.video.YoutubeVideoSource.prototype.createPlayer = function() {
    return this.createPlayerInternal(false);
};

mirosubs.video.YoutubeVideoSource.prototype.createControlledPlayer = 
    function() 
{
    return new mirosubs.video.ControlledVideoPlayer(this.createPlayerInternal(true));
};

/**
 * @protected
 */
mirosubs.video.YoutubeVideoSource.prototype.createPlayerInternal = function(forDialog) {
    return new mirosubs.video.YoutubeVideoPlayer(
        new mirosubs.video.YoutubeVideoSource(
            this.youtubeVideoID_, this.videoConfig_), 
        forDialog);
};

mirosubs.video.YoutubeVideoSource.prototype.getYoutubeVideoID = function() {
    return this.youtubeVideoID_;
};

mirosubs.video.YoutubeVideoSource.prototype.getUUID = function() {
    return this.uuid_;
};

mirosubs.video.YoutubeVideoSource.prototype.getVideoConfig = function() {
    return this.videoConfig_;
};

mirosubs.video.YoutubeVideoSource.prototype.setVideoConfig = function(config) {
    this.videoConfig_ = config;
};


mirosubs.video.YoutubeVideoSource.prototype.getVideoURL = function() {
    return "http://www.youtube.com/watch?v=" + this.youtubeVideoID_;
};