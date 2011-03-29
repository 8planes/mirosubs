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

goog.provide('mirosubs.startdialog.VideoLanguages');

/**
 * @constructor
 */
mirosubs.startdialog.VideoLanguages = function(jsonVideoLanguages) {
    var videoLanguages = goog.array.map(
        jsonVideoLanguages,
        function(vljson) {
            return new mirosubs.startdialog.VideoLanguage(vljson);
        });
    /**
     * @type {Array.<mirosubs.startdialog.VideoLanguage>}
     */
    this.videoLanguages_ = goog.array.filter(
        videoLanguages,
        function(l) {
            return !!mirosubs.languageNameForCode(l.LANGUAGE);
        });
    goog.array.forEach(
        this.videoLanguages_,
        function(vl) { vl.setAll(this.videoLanguages_); },
        this);
    this.languageMap_ = null;
    this.pkMap_ = null;
};

mirosubs.startdialog.VideoLanguages.prototype.forEach = function(f, opt_obj) {
    goog.array.forEach(this.videoLanguages_, f, opt_obj);
};

/**
 * @param {string} language Language code
 * @returns {Array.<mirosubs.startdialog.VideoLanguage>} List of video langauges for language.
 */
mirosubs.startdialog.VideoLanguages.prototype.findForLanguage = function(language) {
    if (!this.languageMap_) {
        this.languageMap_ = {};
        var vl;
        for (var i = 0; i < this.videoLanguages_.length; i++) {
            vl = this.videoLanguages_[i];
            if (!this.languageMap_[vl.LANGUAGE])
                this.languageMap_[vl.LANGUAGE] = [vl];
            else
                this.languageMap_[vl.LANGUAGE].push(vl);
        }
    }
    return this.languageMap_[language] ? this.languageMap_[language] : [];
};

mirosubs.startdialog.VideoLanguages.prototype.findForPK = function(pk) {
    if (!this.pkMap_) {
        this.pkMap_ = {};
        goog.array.forEach(
            this.videoLanguages_,
            function(vl) { this.pkMap_[vl.PK] = vl; },
            this);
    }
    return this.pkMap_[pk];
};