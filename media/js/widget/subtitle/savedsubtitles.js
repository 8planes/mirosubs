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

mirosubs.widget.SavedSubtitles.saveInitial = function(savedSubs) {
    mirosubs.widget.SavedSubtitles.save_(0, savedSubs);
};

mirosubs.widget.SavedSubtitles.saveLatest = function(savedSubs) {
    mirosubs.widget.SavedSubtitles.save_(1, savedSubs);
};

mirosubs.widget.SavedSubtitles.fetchInitial = function() {
    return mirosubs.widget.SavedSubtitles.fetchSaved_(0);
};

mirosubs.widget.SavedSubtitles.fetchLatest = function() {
    return mirosubs.widget.SavedSubtitles.fetchSaved_(1);
};

mirosubs.widget.SavedSubtitles.save_ = function(index, savedSubs) {
    var key = mirosubs.widget.SavedSubtitles.STORAGEKEY_ + index;
    var value = savedSubs.serialize();
    mirosubs.saveInLocalStorage(key, value);
};

mirosubs.widget.SavedSubtitles.fetchSaved_ = function(index) {
    var savedSubsText = mirosubs.fetchFromLocalStorage(
        mirosubs.widget.SavedSubtitles.STORAGEKEY_ + index);
    if (savedSubsText)
        return mirosubs.widget.SavedSubtitles.deserialize(savedSubsText);
    else
        return null;
};