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
 * @fileoverview a wrapper around mirosubs.Tracker for tracking changes
 *     to subtitles specifically.
 */

goog.provide('mirosubs.SubTracker');

/**
 * @constructor
 */
mirosubs.SubTracker = function() {
    /**
     * @type {?boolean}
     */
    this.translating_ = null;
};
goog.addSingletonGetter(mirosubs.SubTracker);

/**
 * @param {boolean} translating
 */
mirosubs.SubTracker.prototype.start = function(translating) {
    this.translating_ = translating;
    this.edited_ = {};
    this.added_ = {};
    this.numEdited_ = 0;
    this.numAdded_ = 0;
};

mirosubs.SubTracker.prototype.addIfNotPresent_ = function(id, obj) {
    id = id + '';
    if (!goog.object.containsKey(obj, id)) {
        obj[id] = true;
        return true;
    }
    else
        return false;
};

mirosubs.SubTracker.prototype.trackAdd = function(subtitleID) {
    if (this.addIfNotPresent_(subtitleID, this.added_)) {
        this.numAdded_++;
        if (this.numAdded_ == 1 || (this.numAdded_ % 5) == 0)
            mirosubs.Tracker.getInstance().track(
                this.translating_ ? "Translates_a_line" : 
                    "Creates_a_subtitle");
    }
};

mirosubs.SubTracker.prototype.trackEdit = function(subtitleID) {
    if (this.addIfNotPresent_(subtitleID, this.edited_)) {
        this.numEdited_++;
        if (this.numEdited_ == 1 || (this.numEdited_ % 5) == 0)
            mirosubs.Tracker.getInstance().track(
                this.translating_ ? "Edits_a_line_of_translation" : 
                    "Edits_a_subtitle");
    }
};