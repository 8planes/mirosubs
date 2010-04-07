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

goog.provide('mirosubs.YoutubeVideoSource');

mirosubs.YoutubeVideoSource = function(uuid, youtubeVideoID) {
    this.uuid_ = uuid;
    this.youtubeVideoID_ = youtubeVideoID;
};

mirosubs.YoutubeVideoSource.counter_ = 0;

mirosubs.YoutubeVideoSource.prototype.createPlayer = function() {
    return new mirosubs.YoutubeVideoPlayer(
        new mirosubs.YoutubeVideoSource(
            this.uuid_ + (mirosubs.YoutubeVideoSource.counter_++), 
            this.youtubeVideoID_));
};

mirosubs.YoutubeVideoSource.prototype.getYoutubeVideoID = function() {
    return this.youtubeVideoID_;
};

mirosubs.YoutubeVideoSource.prototype.getUUID = function() {
    return this.uuid_;
};