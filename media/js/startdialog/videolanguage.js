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

goog.provide('mirosubs.startdialog.VideoLanguage');

/**
 * @constructor
 */
mirosubs.startdialog.VideoLanguage = function(json) {
    this.PK = json['pk'];
    this.LANGUAGE = json['language'];
    this.DEPENDENT = json['dependent'];
    this.IS_COMPLETE = json['is_complete'];
    this.PERCENT_DONE = json['percent_done'];
    this.STANDARD_PK = json['standard_pk'];
    this.SUBTITLE_COUNT = json['subtitle_count'];
};

mirosubs.startdialog.VideoLanguage.prototype.toString = function() {
    var name = mirosubs.languageNameForCode(this.LANGUAGE);
    var numSubs = this.SUBTITLE_COUNT + ' sub' + 
        (this.SUBTITLE_COUNT == 1 ? ')' : 's)');
    if (!this.DEPENDENT)
        return name + (this.IS_COMPLETE ? " (complete, " : " (incomplete, ") + numSubs;
    else
        return name + " (" + this.PERCENT_DONE + "%, " + numSubs;    
};

mirosubs.startdialog.VideoLanguage.prototype.setAll = function(all) {
    this.allLangs_ = all;
    if (this.STANDARD_PK)
        this.standardLang_ = goog.array.find(
            this.allLangs_, 
            function(lang) { return lang.PK == this.STANDARD_PK; },
            this);
};

mirosubs.startdialog.VideoLanguage.prototype.getStandardLang = function() {
    return this.standardLang_;
};

mirosubs.startdialog.VideoLanguage.prototype.isDependentAndNonempty = function(partial) {
    if (partial)
        return this.DEPENDENT && this.PERCENT_DONE > 0 && this.PERCENT_DONE < 100;
    else
        return this.DEPENDENT && this.PERCENT_DONE == 100;
};

mirosubs.startdialog.VideoLanguage.prototype.isEmpty = function() {
    return this.DEPENDENT && this.PERCENT_DONE == 0;
};

mirosubs.startdialog.VideoLanguage.prototype.isDependable = function() {
    if (this.DEPENDENT)
        return this.getStandardLang() && this.getStandardLang().IS_COMPLETE && this.PERCENT_DONE > 10;
    else
        return this.IS_COMPLETE;
};

mirosubs.startdialog.VideoLanguage.prototype.canBenefitFromTranslation = 
    function(languageSummary) 
{
    if (!this.DEPENDENT)
        return false;
    if (languageSummary.DEPENDENT)
        return this.STANDARD_PK == languageSummary.STANDARD_PK;
    else
        return this.STANDARD_PK == languageSummary.PK;
};