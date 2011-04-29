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

goog.provide('mirosubs.widget.DropDownContents');

/**
 * @constructor
 */
mirosubs.widget.DropDownContents = function(languages, subtitleCount) {
    /**
     * Array of {mirosubs.startdialog.VideoLanguage}
     * @type {Array.<Array>}
     */
    this.LANGUAGES = goog.array.map(languages, function(l){
        return new mirosubs.startdialog.VideoLanguage(l);
    });
    /**
     * Number of subtitles for this video.
     * @type {Number}
     */
    this.SUBTITLE_COUNT = subtitleCount;
};

mirosubs.widget.DropDownContents.fromJSON = function(json) {
    return new mirosubs.widget.DropDownContents(
        json['languages'], json['subtitle_count']);
};
