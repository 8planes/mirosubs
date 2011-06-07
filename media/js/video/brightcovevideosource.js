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

goog.provide('mirosubs.video.BrightcoveVideoSource');
/**
 * @constructor
 * @implements {mirosubs.video.VideoSource}
 * @param {string} playerID Brightcove player id
 * @param {string} playerKey Brightcove player key
 * @param {string} videoID Brightcove video id* 
 * @param {Object.<string, *>=} opt_videoConfig Params to use for 
 *     brightCove query string, plus optional 'width' and 'height' 
 *     parameters.
 */
mirosubs.video.BrightcoveVideoSource = function(playerID, playerKey, videoID, opt_videoConfig) {
    this.playerID_ = playerID;
    this.videoID_ = videoID;
    this.playerKey_ = playerKey;
    this.uuid_ = mirosubs.randomString();
    this.videoConfig_ = opt_videoConfig;
};

/* @const
 * @type {string} 
 */
mirosubs.video.BrightcoveVideoSource.BASE_DOMAIN = "brightcove.com";

mirosubs.video.BrightcoveVideoSource.forURL = 
    function(videoURL, opt_videoConfig) 
{
    
    if (mirosubs.video.BrightcoveVideoSource.isBrightcove(videoURL)){
        var uri = new goog.Uri(videoURL);
        var playerKey = uri.getParameterValue("bckey");
        var videoID = uri.getParameterValue("bctid");
        var playerID;
        try{
             playerID =  /bcpid([\d])+/.exec(videoURL)[0].substring(5);
        }catch(e){
            
        }
        if (!opt_videoConfig){
            opt_videoConfig = {};
        }
        opt_videoConfig["uri"] = videoURL;
        if (playerID){
            return new mirosubs.video.BrightcoveVideoSource(
                playerID, playerKey, videoID, opt_videoConfig);    
        }
        
    }
    return null;
};

mirosubs.video.BrightcoveVideoSource.isBrightcove = function(videoURL) {
    var uri = new goog.Uri(videoURL);
    return   goog.string.caseInsensitiveEndsWith(
        uri.getDomain(),
        mirosubs.video.BrightcoveVideoSource.BASE_DOMAIN);
};

mirosubs.video.BrightcoveVideoSource.prototype.createPlayer = function() {
    return this.createPlayer_(false);
};

mirosubs.video.BrightcoveVideoSource.prototype.createControlledPlayer = 
    function() 
{
    return new mirosubs.video.ControlledVideoPlayer(this.createPlayer_(true));
};

mirosubs.video.BrightcoveVideoSource.prototype.createPlayer_ = function(forDialog) {
    return new mirosubs.video.BrightcoveVideoPlayer(
        new mirosubs.video.BrightcoveVideoSource(
            this.playerID_, this.playerKey_, this.videoID_, this.videoConfig_), 
        forDialog);
};

mirosubs.video.BrightcoveVideoSource.prototype.getPlayerID = function() {
    return this.playerID_;
};

mirosubs.video.BrightcoveVideoSource.prototype.getVideoID = function() {
    return this.videoID_;
};

mirosubs.video.BrightcoveVideoSource.prototype.getPlayerKey = function() {
     return this.playerKey_;
};

mirosubs.video.BrightcoveVideoSource.prototype.getUUID = function() {
    return this.uuid_;
};

mirosubs.video.BrightcoveVideoSource.prototype.getVideoConfig = function() {
    return this.videoConfig_;
};

mirosubs.video.BrightcoveVideoSource.prototype.setVideoConfig = function(config) {
    this.videoConfig_ = config;
};


mirosubs.video.BrightcoveVideoSource.prototype.getVideoURL = function() {
    return this.videoConfig_["url"];
};

mirosubs.video.BrightcoveVideoSource.EMBED_SOURCE = "http://c.brightcove.com/services/viewer/federated_f9?isVid=1&isUI=1";
mirosubs.video.BrightcoveVideoSource.prototype.toString = function() {
    return "BrightcoveVideoSource " + this.videoID_;
}
