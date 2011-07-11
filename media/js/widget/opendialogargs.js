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

goog.provide('mirosubs.widget.OpenDialogArgs');

/**
 * @fileoverview 
 * OpenDialogArgs contains the four arguments necessary to start editing
 *     and open the subtitling dialog.
 */

/**
 * @constructor
 */
mirosubs.widget.OpenDialogArgs = function(
    subLanguageCode, 
    opt_originalLanguageCode, 
    opt_subLanguagePK,
    opt_baseLanguagePK)
{
    /**
     * The language code we are subtitling into.
     * @type {!string}
     * @const
     */
    this.LANGUAGE = subLanguageCode;
    /**
     * The original language code for the video. Only present if it was 
     * specified by user.
     * @type {?string}
     * @const
     */
    this.ORIGINAL_LANGUAGE = opt_originalLanguageCode;
    /**
     * The primary key of the server-side SubtitleLanguage that we are editing, 
     * if one was specified in the start dialog.
     * @type {?number}
     * @const
     */
    this.SUBLANGUAGE_PK = opt_subLanguagePK;
    /**
     * The primary key of the server-side base SubtitleLanguage that we are
     * translating from. Non-null iff translating.
     * @type {?number}
     * @const
     */
    this.BASELANGUAGE_PK = opt_baseLanguagePK;
};

mirosubs.widget.OpenDialogArgs.prototype.matches = function(other) {
    return this.LANGUAGE == other.LANGUAGE &&
        this.ORIGINAL_LANGUAGE == other.ORIGINAL_LANGUAGE &&
        this.SUBLANGUAGE_PK == other.SUBLANGUAGE_PK &&
        this.BASELANGUAGE_PK == other.BASELANGUAGE_PK;
};

mirosubs.widget.OpenDialogArgs.prototype.toObject = function() {
    return {
        'l': this.LANGUAGE,
        'o': this.ORIGINAL_LANGUAGE,
        's': this.SUBLANGUAGE_PK,
        'b': this.BASELANGUAGE_PK
    };
};

mirosubs.widget.OpenDialogArgs.fromObject = function(obj) {
    return new mirosubs.widget.OpenDialogArgs(
        obj['l'], obj['o'], obj['s'], obj['b']);
};

