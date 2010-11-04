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

goog.provide('mirosubs.widgetizer.Youtube');

mirosubs.widgetizer.Youtube = function() {
    mirosubs.widgetizer.Youtube.superClass_.call(this);
};
goog.inherits(mirosubs.widgetizer.Youtube,
              mirosubs.widgetizer.VideoPlayerMaker);

mirosubs.widgetizer.Youtube.prototype.videosExist = function() {
    
};

mirosubs.widgetizer.Youtube.prototype.makeVideoPlayers = function() {
    
};

mirosubs.widgetizer.Youtube.prototype.unwidgetizedElements_ = function() {
    if (window.location.hostname.match(/youtube\.com$/) != null)
        return this.filterUnwidgetized(
            [goog.dom.getElement('movie_player')]);
    else {
        var unwidgetizedElements = [];
        // no idea if this is best way. might want to look at object also, or both.
        var embeds = document.getElementsByTagName('embed');
        for (var i = 0; i < embeds.length; i++) {
            if (this.isYoutubeEmbed_(embeds[i]) && this.isUnwidgetized(embeds[i]))
                unwidgetizedElements.push(embeds[i]);
        }
        return unwidgetizedElements;
    }
};