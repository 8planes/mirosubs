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

goog.provide('mirosubs.widget.SavedSubtitles');

/**
 * @constructor
 * @param {!number} sessionPK
 * @param {?string} title
 * @param {?boolean} isComplete
 * @param {!mirosubs.subtitle.EditableCaptionSet} captionSet
 */
mirosubs.widget.SavedSubtitles = function(sessionPK, title, isComplete, captionSet) {
    /**
     * @const
     * @type {!number}
     */
    this.SESSION_PK = sessionPK;
    /**
     * @const
     * @type {?string}
     */
    this.TITLE_ = title;
    /**
     * @const
     * @type {?boolean}
     */
    this.IS_COMPLETE = isComplete;
    /**
     * @const
     * @type {!mirosubs.subtitle.EditableCaptionSet}
     */
    this.CAPTION_SET = captionSet;
};

mirosubs.widget.SavedSubtitles.prototype.serialize = function() {
    return goog.json.serialize(
        { sessionPK: this.sessionPK_,
          title: this.title,
          isComplete: this.isComplete_,
          captionSet: this.captionSet_.makeJsonSubs() });
};

mirosubs.widget.SavedSubtitles.STORAGEKEY_ = '_unisubs_work';

mirosubs.widget.SavedSubtitles.deserialize = function(json) {
    var obj = goog.json.deserialize(json);
    return new mirosubs.widget.SavedSubtitles(
        obj.sessionPK, obj.title, obj.isComplete, 
        new mirosubs.subtitle.EditableCaptionSet(obj.captionSet));
};

mirosubs.widget.SavedSubtitles.save = function(index, savedSubs) {
    window['localStorage']['setItem'](
        mirosubs.widget.SavedSubtitles.STORAGEKEY_ + index,
        savedSubs.serialize());
};

mirosubs.widget.SavedSubtitles.fetchSaved = function(index) {
    var savedSubsText = window['localStorage']['getItem'](
        mirosubs.widget.SavedSubtitles.STORAGEKEY_ + index);
    if (savedSubsText)
        return mirosubs.widget.SavedSubtitles.deserialize(savedSubsText);
    else
        return null;
};