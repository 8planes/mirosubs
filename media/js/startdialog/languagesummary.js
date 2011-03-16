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

goog.provide('mirosubs.startdialog.LanguageSummary');

/**
 * @constructor
 */
mirosubs.startdialog.LanguageSummary = function(json) {
    this.LANGUAGE = json['language'];
    this.DEPENDENT = json['dependent'];
    this.IS_COMPLETE = json['is_complete'];
    this.PERCENT_DONE = json['percent_done'];
    this.STANDARD = json['standard'];
};

mirosubs.startdialog.LanguageSummary.prototype.setAll = function(all) {
    this.allLangs_ = all;
    if (this.STANDARD)
        this.standardLang_ = goog.array.find(
            this.allLangs_, 
            function(lang) { return lang.LANGUAGE == this.STANDARD; },
            this);
};

mirosubs.startdialog.LanguageSummary.prototype.getStandardLang = function() {
    return this.standardLang_;
};

mirosubs.startdialog.LanguageSummary.prototype.isDependentAndNonempty = function(partial) {
    if (partial)
        return this.DEPENDENT && this.PERCENT_DONE > 0 && this.PERCENT_DONE < 100;
    else
        return this.DEPENDENT && this.PERCENT_DONE == 100;
};

mirosubs.startdialog.LanguageSummary.prototype.isEmpty = function() {
    return this.DEPENDENT && this.PERCENT_DONE == 0;
};

mirosubs.startdialog.LanguageSummary.prototype.isDependable = function() {
    if (this.DEPENDENT)
        return this.getStandardLang() && this.getStandardLang().IS_COMPLETE && this.PERCENT_DONE > 10;
    else
        return this.IS_COMPLETE;
};

mirosubs.startdialog.LanguageSummary.prototype.canBenefitFromTranslation = 
    function(languageSummary) 
{
    if (!this.DEPENDENT)
        return false;
    if (languageSummary.DEPENDENT)
        return this.STANDARD = languageSummary.STANDARD;
    else
        return this.STANDARD = languageSummary;
};