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
    this.TITLE = title;
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

mirosubs.widget.SavedSubtitles.STORAGEKEY_ = '_unisubs_work';
mirosubs.widget.SavedSubtitles.logger_ = 
    goog.debug.Logger.getLogger('mirosubs.widget.SavedSubtitles');

mirosubs.widget.SavedSubtitles.prototype.serialize = function() {
    return goog.json.serialize(
        { sessionPK: this.SESSION_PK,
          title: this.TITTLE,
          isComplete: this.IS_COMPLETE,
          captionSet: this.CAPTION_SET.makeJsonSubs() });
};

mirosubs.widget.SavedSubtitles.deserialize = function(json) {
    var obj = goog.json.parse(json);
    return new mirosubs.widget.SavedSubtitles(
        obj.sessionPK, obj.title, obj.isComplete, 
        new mirosubs.subtitle.EditableCaptionSet(obj.captionSet));
};

mirosubs.widget.SavedSubtitles.save = function(index, savedSubs) {
    var key = mirosubs.widget.SavedSubtitles.STORAGEKEY_ + index;
    var value = savedSubs.serialize();
    if (goog.DEBUG) {
        mirosubs.widget.SavedSubtitles.logger_.info(
            "Saving subs to " + key);
        mirosubs.widget.SavedSubtitles.logger_.info(
            "Saved subs:" + value);
    }
    window['localStorage']['setItem'](key, value);
};

mirosubs.widget.SavedSubtitles.fetchSaved = function(index) {
    var savedSubsText = window['localStorage']['getItem'](
        mirosubs.widget.SavedSubtitles.STORAGEKEY_ + index);
    if (savedSubsText)
        return mirosubs.widget.SavedSubtitles.deserialize(savedSubsText);
    else
        return null;
};