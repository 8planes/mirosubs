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

goog.provide('mirosubs.widget.SubtitleState');

/**
 * @constructor
 */
mirosubs.widget.SubtitleState = function(json, opt_subs) {
    /**
     * Language code. Null if and only if original language.
     * @type {?string}
     */
    this.LANGUAGE = json['language_code'];
    this.LANGUAGE_PK = json['language_pk'];
    this.IS_ORIGINAL = json['is_original'];
    this.IS_COMPLETE = json['is_complete'];
    /**
     * @type {number}
     */
    this.VERSION = json['version'];
    this.SUBTITLES = json['subtitles'] || opt_subs;
    this.FORKED = json['forked'];
    this.BASE_LANGUAGE = json['base_language'];
    this.BASE_LANGUAGE_PK = json['base_language_pk'];
    this.IS_LATEST = json['is_latest'];
    this.TITLE = json['title'];
};

mirosubs.widget.SubtitleState.fromJSON = function(json) {
    if (json)
        return new mirosubs.widget.SubtitleState(json);
    else
        return null;
};

mirosubs.widget.SubtitleState.fromJSONSubs = function(subs) {
    return new mirosubs.widget.SubtitleState({}, subs);
};

mirosubs.widget.SubtitleState.prototype.baseParams = function() {
    return mirosubs.widget.BaseState.createParams(
        this.LANGUAGE, this.VERSION);
};

mirosubs.widget.SubtitleState.prototype.fork = function() {
    this.FORKED = true;
    this.BASE_LANGUAGE = null;
    this.BASE_LANGUAGE_PK = null;
};
