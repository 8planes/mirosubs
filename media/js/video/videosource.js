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

/**
 * @fileoverview An interface for a video source
 *
 */

goog.provide('mirosubs.video.VideoSource');

/**
 *
 * @interface
 */
mirosubs.video.VideoSource = function() {};

/**
 * Creates a player for the page, not the widget.
 * @return {mirosubs.video.AbstractVideoPlayer} 
 */
mirosubs.video.VideoSource.prototype.createPlayer = function() {};
/**
 * Creates a player for the widget.
 * @return {mirosubs.video.ControlledVideoPlayer}
 */
mirosubs.video.VideoSource.prototype.createControlledPlayer = function() {};

/**
 * Returns null if we can't get VideoSource without asking the server
 * for more info.
 *
 */
mirosubs.video.VideoSource.videoSourceForURL = function(videoURL) {
    if (/^\s*https?:\/\/([^\.]+\.)?youtube/i.test(videoURL)) {
        var videoIDExtract = /v[\/=]([0-9a-zA-Z\-\_]+)/i.exec(videoURL);
        if (videoIDExtract)
            return new mirosubs.video.YoutubeVideoSource(
                videoIDExtract[1]);
        else
            throw new Error("Cannot parse youtube url " + videoURL);
    }
    else if (/^\s*https?:\/\/([^\.]+\.)?blip\.tv/.test(videoURL)) {
        // file/get/ paths from blip.tv are direct file accesses,
        // so give them an Html5VideoSource
        if (/^\s*https?:\/\/([^\.]+\.)?blip\.tv\/file\/get\//.test(videoURL)) {
            if (/\.flv$/.test(videoURL))
                return new mirosubs.video.FlvVideoSource(videoURL);
            else 
                return new mirosubs.video.Html5VideoSource(videoURL);
        }
        return null;
    }
    else {
        // TODO: maybe check this in the future.
        return new mirosubs.video.Html5VideoSource(videoURL);
    }
};