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

goog.provide('mirosubs.translate.TranslationList');

/**
 *
 * @param {array.<object.<string, *>>} subtitles Array of json captions.
 * @param {mirosubs.UnitOfWork} unitOfWork Used to instantiate new EditableTranslations.
 * @extends {goog.ui.Component}
 * @constructor
 */
mirosubs.translate.TranslationList = function(subtitles,
                                              unitOfWork, videoTitle) {
    goog.ui.Component.call(this);
    /**
     * Array of subtitles in json format
     */
    this.subtitles_ = subtitles;
    this.videoTitle_ = videoTitle || '';
    goog.array.sort(
        this.subtitles_,
        function(a, b) {
            return a['sub_order'] - b['sub_order'];
        });
    /**
     * @type {Array.<mirosubs.translate.TranslationWidget>}
     */
    this.translationWidgets_ = [];
    this.translations_ = [];
    this.titleTranslationWidget = null;
    this.unitOfWork_ = unitOfWork;
};
goog.inherits(mirosubs.translate.TranslationList, goog.ui.Component);

mirosubs.translate.TranslationList.prototype.createDom = function() {
    this.setElementInternal(this.getDomHelper()
                            .createDom('ul'));
    var that = this;
    var w;
    
    if (this.videoTitle_){
        this.titleTranslationWidget = 
            new mirosubs.translate.TitleTranslationWidget(this.videoTitle_, this.unitOfWork_);
        this.addChild(this.titleTranslationWidget, true);
    }
    
    goog.array.forEach(this.subtitles_,
                       function(subtitle) {
                           w = new mirosubs.translate.TranslationWidget(
                               subtitle, that.unitOfWork_);
                           that.addChild(w, true);
                           that.translationWidgets_.push(w);
                       });
};

mirosubs.translate.TranslationList.prototype.getSubsJson = function() {
    return goog.array.map(
        this.translationWidgets_,
        function(t) { return t.getSubJson(); });
};

mirosubs.translate.TranslationList.prototype.setTitleTranslation = function(value){
    this.titleTranslationWidget && this.titleTranslationWidget.setTranslation(value);
};

/**
 * This class will mutate the array as translations are added.
 * @param {Array.<mirosubs.translate.EditableTranslation>} translations
 */
mirosubs.translate.TranslationList.prototype.setTranslations = function(translations) {
    this.translations_ = translations;
    var i, translation;
    var map = {};
    for (i = 0; i < translations.length; i++)
        map[translations[i].getCaptionID()] = translations[i];
    for (i = 0; i < this.translationWidgets_.length; i++) {
        translation = map[this.translationWidgets_[i].getCaptionID()];
        this.translationWidgets_[i].setTranslation(translation ? translation : null);
    }
};

/**
 * Callback that is called by aut-translator
 * @param {Array.<string>} Array of translations
 * @param {Array.<mirosubs.translate.TranslationWidget>} widgets that were translated
 * @param {?string} error happened while translating
 */
mirosubs.translate.TranslationList.prototype.translateCallback_ = function(translations, widgets, error) {
    if (error) {
        
    } else {
        goog.array.forEach(translations, function(text, i) {
            widgets[i].setTranslationContent(text);
        });
    }
};

/**
 * Find widgets for all not translated subtitles and translate them with GoogleTranslator
 */
mirosubs.translate.TranslationList.prototype.translateViaGoogle = function(fromLang, toLang) {
    /**
     * Translation widgets that does not contain any user's translation
     * @type {Array.<mirosubs.translate.TranslationWidget>}
     */
    var needTranslating = [];

    if (this.titleTranslationWidget && this.titleTranslationWidget.isEmpty()) {
        needTranslating.push(this.titleTranslationWidget);
    };
    
    goog.array.forEach(this.translationWidgets_, function(w) {
        if (w.isEmpty()) {
            needTranslating.push(w);
        }
    });
    
    /**
     * @type {mirosubs.translate.GoogleTranslator.translateWidgets}
     */
    var translateWidgets = mirosubs.translate.GoogleTranslator.translateWidgets;

    needTranslating.length && translateWidgets(needTranslating, fromLang, toLang, 
        this.translateCallback_);
};
