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

goog.provide('mirosubs.startdialog.Model');

/**
 * @constructor
 * @param {Object} json from widget rpc
 * @param {string=} opt_initialLanguage Lang code of SubtitleLanguage to 
 *     display initially.
 */
mirosubs.startdialog.Model = function(json, opt_initialLanguageCode) {
    /**
     * @type {Array.<string>} Array of langauge codes
     */
    this.myLanguages_ = json['my_languages'];
    goog.array.removeDuplicates(this.myLanguages_);
    this.myLanguages_ = goog.array.filter(
        this.myLanguages_, function(l) { 
            return !!mirosubs.languageNameForCode(l); 
        });
    this.originalLanguage_ = json['original_language'];
    this.videoLanguages_ = new mirosubs.startdialog.VideoLanguages(
        json['video_languages']);
    this.toLanguages_ = new mirosubs.startdialog.ToLanguages(
        this.myLanguages_, this.videoLanguages_, 
        opt_initialLanguageCode);
    /**
     * @type {?string}
     */
    this.selectedOriginalLanguage_ = null;
    if (opt_initialLanguageCode){
       this.selectedLanguage_ = this.toLanguages_.forLangCode(opt_initialLanguageCode); 
    }
};

mirosubs.startdialog.Model.prototype.getOriginalLanguage = function() {
    return this.originalLanguage_;
};

mirosubs.startdialog.Model.prototype.originalLanguageShown = function() {
    return !this.originalLanguage_;
};

/**
 * @returns {Array.<mirosubs.startdialog.ToLanguage>}
 */
mirosubs.startdialog.Model.prototype.toLanguages = function() {
    return this.toLanguages_.getToLanguages();
};

/**
 * @returns {mirosubs.startdialog.ToLanguage}
 */
mirosubs.startdialog.Model.prototype.getSelectedLanguage = function() {
    if (!this.selectedLanguage_)
        this.selectedLanguage_ = this.toLanguages_.getToLanguages()[0];
    return this.selectedLanguage_;
};

/**
 * @param {string} key KEY from toLanguages to select
 */
mirosubs.startdialog.Model.prototype.selectLanguage = function(key) {
    this.selectedLanguage_ = this.toLanguages_.forKey(key);
};

/**
 * @param {string} language language code to select.
 */
mirosubs.startdialog.Model.prototype.selectOriginalLanguage = function(language) {
    this.selectedOriginalLanguage_ = language;
};

/**
 * @return {Array.<mirosubs.startdialog.LanguageSummary>}
 */
mirosubs.startdialog.Model.prototype.fromLanguages = function() {
    var originalLanguage = this.originalLanguage_;
    if (!originalLanguage)
        originalLanguage = this.selectedOriginalLanguage_;
    var selectedLanguage = this.getSelectedLanguage();
    if (selectedLanguage.LANGUAGE == originalLanguage)
        return [];
    var videoLanguages = this.videoLanguages_.findForLanguage(
        selectedLanguage.LANGUAGE);
    var possibleFromLanguages = [];
    this.videoLanguages_.forEach(function(vl) {
        if (!goog.array.contains(videoLanguages, vl))
            possibleFromLanguages.push(vl);
    });
    possibleFromLanguages = goog.array.filter(
        possibleFromLanguages,
        function(vl) { 
            return (vl.DEPENDENT && vl.PERCENT_DONE > 0) || 
                (!vl.DEPENDENT && vl.SUBTITLE_COUNT > 0); 
        });
    var myLanguages = new goog.structs.Set(this.myLanguages_);
    goog.array.sort(
        possibleFromLanguages,
        function(a, b) {
            return goog.array.defaultCompare(
                myLanguages.contains(a.LANGUAGE) ? 0 : 1, 
                myLanguages.contains(b.LANGUAGE) ? 0 : 1);
        });
    return possibleFromLanguages;
};

mirosubs.startdialog.Model.prototype.toLanguageForKey = function(key) {
    return this.toLanguages_.forKey(key);
};
