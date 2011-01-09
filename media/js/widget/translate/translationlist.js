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
                                              unitOfWork) {
    goog.ui.Component.call(this);
    /**
     * Array of subtitles in json format
     */
    this.subtitles_ = subtitles;
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
    this.unitOfWork_ = unitOfWork;
};
goog.inherits(mirosubs.translate.TranslationList, goog.ui.Component);

mirosubs.translate.TranslationList.prototype.createDom = function() {
    this.setElementInternal(this.getDomHelper()
                            .createDom('ul'));
    var that = this;
    var w;
    goog.array.forEach(this.subtitles_,
                       function(subtitle) {
                           w = new mirosubs.translate.TranslationWidget(
                               subtitle, that.unitOfWork_);
                           that.addChild(w, true);
                           that.translationWidgets_.push(w);
                       });
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

mirosubs.translate.TranslationList.prototype._translateCallback = function(translations, widgets, error){
    if (error){
        //TODO: show pretty error. Pay attention: callback can be called few times 
        //and have same error. For example, incorrect language - be incorrect for all
        //requests to google translator
    }else{
        goog.array.forEach(translations, function(text, i){
            //TODO: I am sure that should be used setTranslation, but don't know
            //how create proper arguments from text
            //widgets[i].setTranslation(text);
            widgets[i].translateInput_.value = text;
        });
    }
};

mirosubs.translate.TranslationList.prototype.translateViaGoogle = function(){
    var need_tarnslating = [];
    goog.array.forEach(this.translationWidgets_, function(w){
        if (w.isEmpty()){
            need_tarnslating.push(w);
        }
    });
    
    var translate_widgets = mirosubs.translate.GoogleTranslator.translate_widgets;
    //TODO: show loading indicator
    //TODO: can't find where is original and translating languages
    need_tarnslating.length && translate_widgets(need_tarnslating, 'en', 'ru', 
        this._translateCallback);
    //TODO: hide indicator
};
