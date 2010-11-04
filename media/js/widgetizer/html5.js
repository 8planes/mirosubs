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

goog.provide('mirosubs.widgetizer.HTML5');

mirosubs.widgetizer.HTML5 = function() {};

mirosubs.widgetizer.HTML5.prototype.videosExist = function() {
    return this.unwidgetizedVideos_().length > 0;
};

mirosubs.widgetizer.HTML5.prototype.makeVideoPlayers = function() {
    var videoElements = this.unwidgetizedVideos_();
    var videoPlayers = [];
    for (var i = 0; i < videoElements.length; i++) {
        var videoSource = this.makeVideoSource_(videoElements[i]);
        var videoPlayer = new mirosubs.video.Html5VideoPlayer(videoSource, false);
        videoPlayer.decorate(videoElements[i]);
        videoPlayers.push(videoPlayer);
    }
    return videoPlayers;
};

mirosubs.widgetizer.HTML5.prototype.unwidgetizedVideos_ = function() {
    return this.filterUnwidgetized_(
        document.getElementsByTagName('video'));
};

mirosubs.widgetizer.HTML5.prototype.makeVideoSource_ = 
    function(videoElement) 
{
    var fullURL = 
    if (videoElement.src)
        return mirosubs.video.Html5VideoSource.forURL(videoElement.src);
    else
        
};

mirosubs.widgetizer.HTML5.prototype.filterUnwidgetized_ = 
    function(videoElements) 
{
    var unwidgetized = [];
    for (var i = 0; i < videoElements.length; i++)
        if (this.isUnwidgetized_(videoElements[i]))
            unwidgetized.push(videoElements[i]);
    return unwidgetized;
};

mirosubs.widgetizer.HTML5.prototype.isUnwidgetized_ = function(element) {
    var players = mirosubs.video.AbstractVideoPlayer.players;
    for (var i = 0; i < players.length; i++)
        if (players[i].getVideoElement() == element)
            return false;
    return true;
};