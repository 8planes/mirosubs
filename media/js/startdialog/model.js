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
 */
mirosubs.startdialog.Model = function(json, opt_initialLanguage) {
    /**
     * @type {Array.<string>} Array of langauge codes
     */
    this.myLanguages_ = json['my_languages'];
    this.originalLanguage_ = json['original_language'];
    /**
     * @type {Array.<mirosubs.startdialog.LanguageSummary>}
     */
    this.videoLanguages_ = goog.array.map(
        json['video_languages'],
        function(vljson) {
            return new mirosubs.startdialog.LanguageSummary(vljson);
        });
    goog.array.forEach(
        this.videoLanguages_,
        function(vl) { vl.setAll(this.videoLanguages_); },
        this);
    this.initialLanguage_ = opt_initialLanguage || null;
    this.toLanguages_ = null;
    this.selectedLanguage_ = null;
};

mirosubs.startdialog.Model.prototype.originalLanguageShown = function() {
    return !this.originalLanguage_;
};

mirosubs.startdialog.Model.prototype.toLanguages = function() {
    this.createToLanguages_();
    return this.toLanguages_;
};

mirosubs.startdialog.Model.prototype.findVideoLanguage_ = function(lang) {
    return goog.array.find(
        this.videoLanguages_,
        function(l) { return l.LANGUAGE == lang; });
};

mirosubs.startdialog.Model.prototype.createToLang_ = function(
    ranking, opt_videoLanguage, opt_language) 
{
    return {
        language: opt_videoLanguage ? opt_videoLanguage.LANGUAGE : opt_language,
        ranking: ranking,
        videoLanguage: opt_videoLanguage
    };
};

mirosubs.startdialog.Model.prototype.createNonEmptyDepToLang_ = 
    function(videoLanguage, partial, ranking) 
{
    if (videoLanguage && videoLanguage.isDependentAndNonempty(partial)) {
        var fromLanguages = [];
        for (var i = 0; i < this.myLanguages_.length; i++) {
            var possiblyFromLanguage = this.findVideoLanguage_(this.myLanguages_[i]);
            if (videoLanguage.canBenefitFromTranslation(possiblyFromLanguage))
                fromLanguages.push(possiblyFromLanguage);
        }
        if (fromLanguages.length > 0)
            return this.createToLang_(ranking, videoLanguage);
    }
    return null;
};

mirosubs.startdialog.Model.prototype.createEmptyToLang_ = function(videoLanguage, lang) {
    if (!videoLanguage || videoLanguage.isEmpty()) {
        var fromLanguages = [];
        for (var i = 0; i < this.myLanguages_.length; i++) {
            var possiblyFromLanguage = this.findVideoLanguage_(this.myLanguages_[i]);
            if (possiblyFromLanguage && possiblyFromLanguage.isDependable())
                fromLanguages.push(possiblyFromLanguage);
        }
        if (fromLanguages.length > 0)
            return this.createToLang_(2, videoLanguage, lang);
    }
    return null;
};

mirosubs.startdialog.Model.prototype.createIncompleteIndToLang_ = function(videoLanguage) {
    if (videoLanguage && !videoLanguage.DEPENDENT && !videoLanguage.IS_COMPLETE)
        return this.createToLang_(3, videoLanguage);
    return null;
}

mirosubs.startdialog.Model.prototype.createMyLanguageToLang_ = function(lang) {
    var videoLanguage = this.findVideoLanguage_(lang);
    var fromLangMeta;
    if (fromLangMeta = this.createNonEmptyDepToLang_(videoLanguage, true, 1))
        return fromLangMeta;
    if (fromLangMeta = this.createEmptyToLang_(videoLanguage, lang))
        return fromLangMeta;
    if (fromLangMeta = this.createIncompleteIndToLang_(videoLanguage))
        return fromLangMeta;
    if (fromLangMeta = this.createNonEmptyDepToLang_(videoLanguage, false, 4))
        return fromLangMeta;
    return this.createToLang_(10, videoLanguage, lang);
};

mirosubs.startdialog.Model.prototype.addMissingToLangs_ = function(languageMetas) {
    var allLangCodes = goog.array.map(
        mirosubs.languages, 
        function(l) { return l[0]; });
    var existingLanguages = new goog.structs.Set(
        goog.array.map(languageMetas, function(l) { return l.language; }));
    var missingLangCodes = goog.array.filter(
        allLangCodes,
        function(code) { return !existingLanguages.contains(code); });
    goog.array.sort(missingLangCodes);
    return goog.array.concat(languageMetas, goog.array.map(
        missingLangCodes, 
        goog.bind(this.createToLang_, null), 
        this));
};

mirosubs.startdialog.Model.prototype.createToLanguages_ = function() {
    if (goog.isDefAndNotNull(this.toLanguages_))
        return;
    var toLanguages = [];
    if (this.initialLanguage_)
        toLanguages.push(this.createMyLanguageToLang_(this.initialLanguage_));
    var myLanguagesToLangs = [];
    for (var i = 0; i < this.myLanguages_.length; i++) {
        if (this.myLanguages_[i] != this.intialLanguage_)
            myLanguagesToLangs.push(this.createMyLanguageToLang_(
                this.myLanguages_[i]));
    }
    goog.array.sort(
        myLanguagesToLangs,
        function(l0, l1) {
            return goog.array.defaultCompare(l0.ranking, l1.ranking);
        });
    toLanguages = goog.array.concat(
        toLanguages, myLanguagesToLangs);
    toLanguages = this.addMissingToLangs_(toLanguages);
    this.toLanguages_ = toLanguages;
    this.selectedLanguage_ = toLanguages[0];
};

mirosubs.startdialog.Model.prototype.getSelectedLanguage = function() {
    this.createToLanguages_();
    return this.selectedLanguage_;
};

/**
 * @param {object} language Object from toLanguages to select
 */
mirosubs.startdialog.Model.prototype.selectLanguage = function(language) {
    this.createToLanguages_();
    this.selectedLanguage_ = language;
};

/**
 * @return {Array.<mirosubs.startdialog.LanguageSummary>}
 */
mirosubs.startdialog.Model.prototype.fromLanguages = function() {
    var selectedLanguage = this.getSelectedLanguage();
    var videoLanguage = this.findVideoLanguage_(selectedLanguage.language);
    var possibleFromLanguages = this.videoLanguages_;
    if (videoLanguage)
        possibleFromLanguages = goog.array.filter(
            this.videoLanguages_,
            function(vl) { return vl != videoLanguage; });
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