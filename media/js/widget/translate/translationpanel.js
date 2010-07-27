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

goog.provide('mirosubs.translate.TranslationPanel');

/**
 *
 *
 *
 */
mirosubs.translate.TranslationPanel = function(subtitles, allLanguages,
                                               unitOfWork, serverModel,
                                               opt_initialLanguageCode,
                                               opt_initialTranslations) {
    goog.ui.Component.call(this);
    this.subtitles_ = subtitles;
    this.languages_ = allLanguages;
    this.unitOfWork_ = unitOfWork;
    this.serverModel_ = serverModel;
    this.contentElem_ = null;
    this.initialLanguageCode_ = opt_initialLanguageCode;
    this.initialTranslations_ = opt_initialTranslations;
};
goog.inherits(mirosubs.translate.TranslationPanel, goog.ui.Component);

mirosubs.translate.TranslationPanel.NO_LANGUAGE = 'NONE';

mirosubs.translate.TranslationPanel.prototype.getContentElement = function() {
    return this.contentElem_;
};
mirosubs.translate.TranslationPanel.prototype.createLanguageSelect_ =
    function($d)
{
    var selectOptions = [ $d('option', 
                             {'value': mirosubs.translate.TranslationPanel.NO_LANGUAGE},
                             'Select Language...') ];
    var initialSelectedIndex = -1;
    var i;
    for (i = 0; i < this.languages_.length; i++) {
        selectOptions.push(
            $d('option',
               {'value':this.languages_[i]['code']},
                this.languages_[i]['name']));
        if (this.initialLanguageCode_ &&
            this.languages_[i]['code'] == this.initialLanguageCode_)
            initialSelectedIndex = i + 1;
    }
    var languageSelect = $d('select', null, selectOptions);
    if (this.initialLanguageCode_)
        languageSelect.selectedIndex = initialSelectedIndex;
    return languageSelect;
};
mirosubs.translate.TranslationPanel.prototype.createDom = function() {
    mirosubs.translate.TranslationPanel.superClass_.createDom.call(this);
    var el = this.getElement();
    var $d = goog.bind(this.getDomHelper().createDom, this.getDomHelper());
    this.languageSelect_ = this.createLanguageSelect_($d)
    el.appendChild($d('div', 'mirosubs-langDrop',
                      goog.dom.createTextNode('To begin translating: '),
                      this.languageSelect_));    
    el.appendChild(this.contentElem_ = $d('div'));
    this.translationList_ =
        new mirosubs.translate.TranslationList(
            this.subtitles_, this.unitOfWork_);
    this.addChild(this.translationList_, true);
    this.translationList_.getElement().className =
        "mirosubs-titlesList";
    if (this.initialTranslations_)
        this.startEditing_(this.initialTranslations_);
    else
        this.translationList_.setEnabled(false);
};
mirosubs.translate.TranslationPanel.prototype.enterDocument = function() {
    mirosubs.translate.TranslationPanel.superClass_.enterDocument.call(this);
    this.getHandler().listen(
        this.languageSelect_, goog.events.EventType.CHANGE,
        this.languageSelected_);
};
mirosubs.translate.TranslationPanel.prototype.languageSelected_ =
    function(event)
{
    var languageCode = this.languageSelect_.value;
    if (languageCode == mirosubs.translate.TranslationPanel.NO_LANGUAGE) {
        this.serverModel_.stopTranslating();
        this.translationList_.setEnabled(false);
        return;
    }
    var that = this;
    // TODO: show loading animation
    this.translationList_.setEnabled(false);
    this.serverModel_.startTranslating(languageCode,
        function(success, result) {
            if (!success)
                alert(result);
            else
                that.startEditing_(result);
        });
};
mirosubs.translate.TranslationPanel.prototype.startEditing_ =
    function(existingTranslations)
{
    var uw = this.unitOfWork_;
    var editableTranslations =
        goog.array.map(
            existingTranslations,
            function(transJson) {
                return new mirosubs.translate.EditableTranslation(
                    uw, transJson['caption_id'], transJson);
            });
    this.translationList_.setTranslations(editableTranslations);
    this.translationList_.setEnabled(true);
};
