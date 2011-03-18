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

goog.provide('mirosubs.startdialog.Dialog');

/**
 * @constructor
 * @param {string} videoID
 * @param {?string} initialLanguage
 * @param {function(?string, string, ?string)} callback When OK button is 
 *     clicked, this will be called with: arg0: original language. This is
 *     non-null if and only if the user is presented with the original language
 *     dropdown in the dialog. arg1: to language: the code for the language 
 *     to which we are translating. arg2: from language: the code for the language
 *     to translate from. This will be null iff the user intends to make 
 *     forked/original.
 */
mirosubs.startdialog.Dialog = function(videoID, initialLanguage, callback) {
    goog.ui.Dialog.call(this, 'mirosubs-modal-lang', true);
    this.setButtonSet(null);
    this.setDisposeOnHide(true);
    this.videoID_ = videoID;
    this.fetchCompleted_ = false;
    this.model_ = null;
    this.initialLanguage_ = initialLanguage;
    this.callback_ = callback;
};
goog.inherits(mirosubs.startdialog.Dialog, goog.ui.Dialog);

mirosubs.startdialog.Dialog.prototype.createDom = function() {
    mirosubs.startdialog.Dialog.superClass_.createDom.call(this);
    var $d = goog.bind(this.getDomHelper().createDom, 
                       this.getDomHelper());
    var el = this.getElement();
    el.appendChild(
        $d('h3', null, 'Create subtitles'));
    this.contentDiv_ = $d('div', null, "Loading...");
    el.appendChild(this.contentDiv_);
};

mirosubs.startdialog.Dialog.prototype.enterDocument = function() {
    mirosubs.startdialog.Dialog.superClass_.enterDocument.call(this);
    this.connectEvents_();
};

mirosubs.startdialog.Dialog.prototype.setVisible = function(visible) {
    mirosubs.startdialog.Dialog.superClass_.setVisible.call(this, visible);
    if (visible)
        mirosubs.Rpc.call(
            'fetch_start_dialog_contents',
            { 'video_id': this.videoID_ },
            goog.bind(this.responseReceived_, this));
};

mirosubs.startdialog.Dialog.prototype.makeDropdown_ = 
    function($d, contents) 
{
    var options = []
    for (var i = 0; i < contents.length; i++)
        options.push(
            $d('option', {'value': contents[i][0]}, contents[i][1]));
    return $d('select', null, options);
};

mirosubs.startdialog.Dialog.prototype.responseReceived_ = function(jsonResult) {
    this.fetchCompleted_ = true;
    this.model_ = new mirosubs.startdialog.Model(
        jsonResult, this.initialLanguage_);
    goog.dom.removeChildren(this.contentDiv_);
    var $d = goog.bind(this.getDomHelper().createDom,
                       this.getDomHelper());
    this.addOriginalLanguageSection_($d);
    this.addToLanguageSection_($d);
    this.addFromLanguageSection_($d);
    this.setFromContents_();
    this.okButton_ = 
        $d('a', 
           {'href':'#', 
            'className': "mirosubs-green-button mirosubs-big"}, 
           'Continue');
    this.contentDiv_.appendChild(this.okButton_);
    var clearDiv = $d('div');
    mirosubs.style.setProperty(clearDiv, 'clear', 'both');
    clearDiv.innerHTML = "&nbsp;";
    this.contentDiv_.appendChild(clearDiv);
    this.reposition();
    this.connectEvents_();
};

mirosubs.startdialog.Dialog.prototype.setFromContents_ = function() {
    var fromLanguages = this.model_.fromLanguages();
    goog.style.showElement(
        this.fromLanguageSection_, fromLanguages.length > 0);
    if (fromLanguages.length > 0) {
        var fromLanguageContents = goog.array.map(
            this.model_.fromLanguages(),
            function(l) {
                return [l.LANGUAGE, l.toString()];
            });;
        var $d = goog.bind(this.getDomHelper().createDom,
                           this.getDomHelper());
        this.fromLanguageDropdown_ = this.makeDropdown_(
            $d, fromLanguageContents);
        goog.dom.removeChildren(this.fromContainer_);
        this.fromContainer_.appendChild(this.fromLanguageDropdown_);
    }
    else
        this.fromLanguageDropdown_ = null;
};

mirosubs.startdialog.Dialog.prototype.addToLanguageSection_ = function($d) {
    var toLanguageContents = goog.array.map(
        this.model_.toLanguages(),
        function(l) {
            if (l.videoLanguage)
                return [l.language, l.videoLanguage.toString()];
            else
                return [l.language, mirosubs.languageNameForCode(l.language)];
        });
    this.toLanguageDropdown_ = this.makeDropdown_($d, toLanguageContents);
    this.contentDiv_.appendChild(
        $d('p', null, 
           $d('span', null, 'Subtitle into: '),
           this.toLanguageDropdown_));
};

mirosubs.startdialog.Dialog.prototype.addFromLanguageSection_ = function($d) {
    this.fromContainer_ = $d('span');
    this.forkCheckbox_ = $d('input', {'type':'checkbox'});
    this.fromLanguageSection_ =
        $d('div', null,
           $d('p', null,
              $d('span', null, 'Translate from: '),
              this.fromContainer_),
           $d('p', null, 
              this.forkCheckbox_, 
              $d('span', null, ' Direct from video (more work)')));
    this.contentDiv_.appendChild(this.fromLanguageSection_);
};

mirosubs.startdialog.Dialog.prototype.addOriginalLanguageSection_ = function($d) {
    if (this.model_.originalLanguageShown()) {
        this.originalLangDropdown_ = this.makeDropdown_(
            $d, mirosubs.languages);
        this.originalLangDropdown_.value = 'en';
        this.contentDiv_.appendChild(
            $d('p', null, 
               $d('span', null, 'This video is in: '), 
               this.originalLangDropdown_));
    }
    else
        this.contentDiv_.appendChild(
            $d('p', null, "This video is in " + 
               mirosubs.languageNameForCode(
                   this.model_.getOriginalLanguage())));
};

mirosubs.startdialog.Dialog.prototype.connectEvents_ = function() {
    if (!this.isInDocument() || !this.fetchCompleted_)
        return;
    this.getHandler().
        listen(
            this.toLanguageDropdown_,
            goog.events.EventType.CHANGE,
            this.toLanguageChanged_).
        listen(
            this.okButton_,
            goog.events.EventType.CLICK,
            this.okClicked_).
        listen(
            this.forkCheckbox_,
            goog.events.EventType.CHANGE,
            this.forkCheckboxChange_);
};

mirosubs.startdialog.Dialog.prototype.forkCheckboxChange_ = function(e) {
    this.fromLanguageDropdown_.disabled = this.forkCheckbox_.checked;
};

mirosubs.startdialog.Dialog.prototype.toLanguageChanged_ = function(e) {
    this.model_.selectLanguage(this.toLanguageDropdown_.value);
    this.setFromContents_();
};

mirosubs.startdialog.Dialog.prototype.okClicked_ = function(e) {
    e.preventDefault();
    var fromLanguage = null;
    if (this.fromLanguageDropdown_ && !this.forkCheckbox_.checked)
        fromLanguage = this.fromLanguageDropdown_.value;
    this.callback_(
        this.model_.originalLanguageShown() ? 
            this.originalLangDropdown_.value : null,
        this.toLanguageDropdown_.value,
        fromLanguage
    );
    this.setVisibility(false);
};
