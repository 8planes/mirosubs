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

goog.provide('mirosubs.startdialog.ToLanguage');

/**
 * @constructor
 * @param {number} ranking
 * @param {mirosubs.startdialog.VideoLanguage} opt_videoLanguage
 * @param {string=} opt_language Language code. Either provide this or opt_videoLanguage.
 */
mirosubs.startdialog.ToLanguage = function(ranking, opt_videoLanguage, opt_language) {
    var languageCode = opt_videoLanguage ? opt_videoLanguage.LANGUAGE : opt_language;
    this.LANGUAGE = languageCode;
    this.KEY = languageCode + (opt_videoLanguage ? ('' + opt_videoLanguage.PK) : '');
    this.LANGUAGE_NAME = mirosubs.languageNameForCode(languageCode);
    this.RANKING = ranking;
    this.VIDEO_LANGUAGE = opt_videoLanguage;
};

mirosubs.startdialog.ToLanguage.prototype.toString = function() {
    if (this.VIDEO_LANGUAGE)
        return this.VIDEO_LANGUAGE.toString();
    else
        return this.LANGUAGE_NAME;
};

mirosubs.startdialog.ToLanguage.rankingCompare = function(a, b) {
    var compare = goog.array.defaultCompare(
        a.RANKING, b.RANKING);
    if (compare == 0)
        compare = goog.array.defaultCompare(
            a.LANGUAGE_NAME, b.LANGUAGE_NAME);
    return compare;
};

mirosubs.startdialog.ToLanguage.userCompare = function(a, b) {
    var compare = goog.array.defaultCompare(
        a.RANKING, b.RANKING);
    if (compare == 0) {
        if (a.VIDEO_LANGUAGE && b.VIDEO_LANGUAGE){
            compare =  goog.array.defaultCompare(
                b.VIDEO_LANGUAGE.PERCENT_DONE, a.VIDEO_LANGUAGE.PERCENT_DONE);
            if (compare == 0) {
                compare = goog.array.defaultCompare(
                    a.LANGUAGE_NAME, b.LANGUAGE_NAME);
            }
        } else {
            compare = goog.array.defaultCompare(
                a.LANGUAGE_NAME, b.LANGUAGE_NAME);
        }
    }
    return compare;
};