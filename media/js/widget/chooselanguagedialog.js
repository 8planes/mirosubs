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

goog.provide('mirosubs.widget.ChooseLanguageDialog');

/**
 * @constructor
 */
mirosubs.widget.ChooseLanguageDialog = function(
    selectOriginal, selectLanguage, selectForked) 
{
    goog.ui.Dialog.call(this, 'mirosubs-modal-lang', true);
    this.selectOriginal_ = selectOriginal;
    this.selectLanguage_ = selectLanguage;
    this.selectForked_ = selectForked;
    this.selectedLanguage_ = null;
    this.isForkedSelected_ = false;
};
goog.inherits(mirosubs.widget.ChooseLanguageDialog, goog.ui.Dialog);

mirosubs.widget.ChooseLanguageDialog.LanguageType = {
    ORIGINAL: "original",
    LANGUAGE: "language",
    METADATA: "metadata"
};

mirosubs.widget.ChooseLanguageDialog.prototype.createDom = function() {
    mirosubs.widget.ChooseLanguageDialog.superClass_.createDom.call(this);
    var $d = goog.bind(this.getDomHelper().createDom, this.getDomHelper());
    var lt = mirosubs.widget.ChooseLanguageDialog.LanguageType;
    if (this.selectLanguage_) {
        this.languageRadioButtons_ = [];
        if (this.selectOriginal_)
            this.addLanguageSelector_($d, lt.ORIGINAL, "Original");
        this.originalDropdown_ = this.makeDropdown_(
            $d, mirosubs.languages);
        this.metadataDropdown_ = this.makeDropdown_(
            $d, mirosubs.metadataLanguages);
        this.addLanguageSelector_(
            $d, lt.LANGUAGE, "Language: ", this.originalDropdown_);
        this.addLanguageSelector_(
            $d, lt.METADATA, "Metadata: ", this.metadataDropdown_);
    }
    if (this.selectForked_) {
        this.forkedCheckbox_ = 
            $d('input', {'type': 'checkbox'});
        this.getElement().appendChild(
            $d('div', null, this.forkedCheckbox_, "Forked"));               
    }
};

mirosubs.widget.ChooseLanguageDialog.prototype.makeDropdown_ = 
    function($d, contents) 
{
    var options = []
    for (var i = 0; i < contents.length; i++)
        options.push(
            $d('option', {'value': contents[i][0]}, contents[i][1]));
    return $d('select', null, options);
};

mirosubs.widget.ChooseLanguageDialog.prototype.addLanguageSelector_ =
    function($d, value, var_children)
{
    var radioButton = $d('input', {'type': 'radio', 
                                   'name': 'langtype',
                                   'value': value})
    this.languageRadioButtons_.push(radioButton);
    var divCreator = goog.partial(
        $d, 'div', null, radioButton);
    this.getElement().appendChild(divCreator.apply(arguments.slice(2)));
};

mirosubs.widget.ChooseLanguageDialog.prototype.getSelectedLanguage = 
    function() 
{
    var lt = mirosubs.widget.ChooseLanguageDialog.LanguageType;
    var selectedRadio = this.selectedLanguageRadioButton_();
    if (selectedRadio != null) {
        if (selectedRadio.name == lt.ORIGINAL)
            return null;
        else if (selectedRadio.name == lt.LANGUAGE)
            return this.originalDropdown_.value;
        else
            return this.metadataDropdown_.value;
    }
    return null;
};

mirosubs.widget.ChooseLanguageDialog.prototype.selectedLanguageRadioButton_ =
    function() 
{
    if (this.languageRadioButtons_)
        for (var i = 0; i < this.languageRadioButtons_.length; i++)
            if (this.languageRadioButtons_[i].checked)
                return this.languageRadioButtons_[i];
    return null;
};

mirosubs.widget.ChooseLanguageDialog.prototype.isForkedSelected =
    function() 
{
    return this.forkedCheckbox_ && this.forkedCheckbox_.checked;
};

mirosubs.widget.ChooseLanguageDialog.show = 
    function(selectOriginal, selectLanguage, selectForked, callback)
{
    var dialog = new mirosubs.widget.ChooseLanguageDialog(
        selectOriginal, selectLanguage, selectForked);
    dialog.setVisible(true);
    goog.events.listenOnce(
        dialog, goog.ui.Dialog.EventType.AFTER_HIDE,
        function(e) {
            callback(dialog.getSelectedLanguage(), dialog.isForkedSelected());
        });
};
