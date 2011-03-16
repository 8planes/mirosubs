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
mirosubs.startdialog.Model = function(initialLanguage, json) {
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
    this.initialLanguage_ = initialLanguage;
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

mirosubs.startdialog.Model.prototype.createNonEmptyDepMeta_ = 
    function(videoLanguage, partial, ranking) 
{
    if (videoLanguage && videoLanguage.isDependent(partial)) {
        var fromLanguages = [];
        for (var i = 0; i < this.myLanguages_.length; i++) {
            var possiblyFromLanguage = this.findVideoLanguage_(this.myLanguages_[i]);
            if (videoLanguage.canBenefitFromTranslation(possiblyFromLanguage))
                fromLanguages.push(possiblyFromLanguage);
        }
        if (fromLanguages.length > 0)
            return {
                language: videoLanguage.LANGUAGE,
                ranking: ranking,
                fromLanguages: fromLanguages
            };
    }
    return null;
};

mirosubs.startdialog.Model.prototype.createEmptyMeta_ = function(videoLanguage, lang) {
    if (!videoLanguage || videoLanguage.isEmpty()) {
        var fromLanguages = [];
        for (var i = 0; i < this.myLanguages_.length; i++) {
            var possiblyFromLanguage = this.findVideoLanguage_(this.myLanguages_[i]);
            if (possiblyFromLanguage && possiblyFromLanguage.isDependable())
                fromLanguages.push(possiblyFromLanguage);
        }
        if (fromLanguages.length > 0)
            return {
                language: lang,
                ranking: 2,
                fromLanguages: fromLanguages
            };
    }
    return null;
};

mirosubs.startdialog.Model.prototype.createIncompleteIndMeta_ = function(videoLanguage) {
    if (videoLanguage && !videoLanguage.DEPENDENT && !videoLanguage.IS_COMPLETE)
        return {
            language: videoLanguage.LANGUAGE,
            ranking: 3,
            fromLanguages: []
        };
    return null;
}

mirosubs.startdialog.Model.prototype.createMyLanguageMeta_ = function(lang) {
    var videoLanguage = this.findVideoLanguage_(lang);
    var fromLangMeta;
    if (fromLangMeta = this.createNonEmptyDepMeta_(videoLanguage, true, 1))
        return fromLangMeta;
    if (fromLangMeta = this.createEmptyMeta_(videoLanguage, lang))
        return fromLangMeta;
    if (fromLangMeta = this.createIncompleteIndMeta_(videoLanguage))
        return fromLangMeta;
    if (fromLangMeta = this.createNonEmptyDepMeta_(videoLanguage, false, 4))
        return fromLangMeta;
    return {
        language: lang,
        ranking: 10,
        fromLanguages: []
    };
};

mirosubs.startdialog.Model.prototype.createToLanguages_ = function() {
    if (goog.isDefAndNotNull(this.toLanguages_))
        return;
    var toLanguages = [];
    if (this.initialLanguage_)
        toLanguages.push(this.createMyLanguageMeta_(this.initialLanguage_));
    var myLanguagesMeta = [];
    for (var i = 0; i < this.myLanguages_.length; i++) {
        if (this.myLanguages_[i] != this.intialLanguage_)
            myLanguagesMeta.push(this.createMyLanguageMeta_(
                this.myLanguages_[i]));
    }
    goog.array.sort(
        myLanguagesMeta,
        function(l0, l1) {
            return goog.array.defaultCompare(l0.ranking, l1.ranking);
        });
    toLanguages = goog.array.concat(
        toLanguages, myLanguagesMeta);
    this.toLanguages_ = toLanguages;
    this.defaultToLanguage_ = toLanguages[0];
    this.selectedLanguage_ = this.defaultToLanguage_;
};

mirosubs.startdialog.Model.prototype.defaultToLanguage = function() {
    this.createToLanguages_();
    return this.defaultToLanguage_;
};

mirosubs.startdialog.Model.prototype.getSelectedLanguage = function() {
    this.createToLanguages_();
    return this.selectedLanguage_;
};

/**
 * @param {object} language Element from toLanguages to select
 */
mirosubs.startdialog.Model.prototype.selectLanguage = function(language) {
    this.createToLanguages_();
    this.selectedLanguage_ = language;
};

mirosubs.startdialog.Model.prototype.fromLanguages = function() {
    var selectedLanguage = this.getSelectedLanguage();
    var videoLanguage = this.findVideoLanguage_(selectedLanguage.language);
    if (videoLanguage && !videoLanguage.DEPENDENT)
        return [];
    else {
        // TODO: write me.
    }
};