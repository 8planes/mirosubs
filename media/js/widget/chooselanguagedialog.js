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
    header, callback, selectOriginal, selectLanguage, selectForked) 
{
    goog.ui.Dialog.call(this, 'mirosubs-modal-lang', true);
    this.setButtonSet(null);
    this.setDisposeOnHide(true);
    this.header_ = header;
    this.callback_ = callback;
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
    this.getElement().appendChild($d('h3', null, this.header_));
    if (this.selectLanguage_) {
        this.languageRadioButtons_ = [];
        if (this.selectOriginal_)
            this.addLanguageSelector_($d, lt.ORIGINAL, "Original Language");
        this.originalDropdown_ = this.makeDropdown_(
            $d, mirosubs.languages);
        this.metadataDropdown_ = this.makeDropdown_(
            $d, mirosubs.metadataLanguages);
        this.addLanguageSelector_(
            $d, lt.LANGUAGE, "Language: ", this.originalDropdown_);
        this.addLanguageSelector_(
            $d, lt.METADATA, "Metadata: ", this.metadataDropdown_);
        this.languageRadioButtons_[0].checked = true;
    }
    if (this.selectForked_) {
        this.forkedCheckbox_ = 
            $d('input', {'type': 'checkbox'});
        this.getElement().appendChild(
            $d('p', null, this.forkedCheckbox_, "Fork timing"));               
    }
    this.okButton_ = 
        $d('a', 
           {'href':'#', 
            'className': "mirosubs-green-button mirosubs-big"}, 
           'OK');
    this.getElement().appendChild(
        $d('p', null, this.okButton_));
};

mirosubs.widget.ChooseLanguageDialog.prototype.enterDocument = function() {
    mirosubs.widget.ChooseLanguageDialog.superClass_.enterDocument.call(this);
    this.getHandler().
        listen(this.okButton_,
               'click',
               this.okClicked_);
};

mirosubs.widget.ChooseLanguageDialog.prototype.okClicked_ = function(e) {
    e.preventDefault();
    this.setVisible(false);
    this.callback_(this.getSelectedLanguage(), this.isForkedSelected());
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
        $d, 'p', null, radioButton);
    this.getElement().appendChild(divCreator.apply(
        null, Array.prototype.slice.call(arguments, 2)));
};

mirosubs.widget.ChooseLanguageDialog.prototype.getSelectedLanguage = 
    function() 
{
    var lt = mirosubs.widget.ChooseLanguageDialog.LanguageType;
    var selectedRadio = this.selectedLanguageRadioButton_();
    if (selectedRadio != null) {
        if (selectedRadio.value == lt.ORIGINAL)
            return null;
        else if (selectedRadio.value == lt.LANGUAGE)
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
    function(header, selectOriginal, selectLanguage, selectForked, callback)
{
    var dialog = new mirosubs.widget.ChooseLanguageDialog(
        header, callback, selectOriginal, 
        selectLanguage, selectForked);
    dialog.setVisible(true);
};
