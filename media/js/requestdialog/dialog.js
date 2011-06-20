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

goog.provide('mirosubs.requestdialog.Dialog');

/**
 * @constructor
 * @param {string} videoID
 */
mirosubs.requestdialog.Dialog = function(videoID) {
    goog.ui.Dialog.call(this, 'mirosubs-modal-lang', true);
    this.setButtonSet(null);
    this.setDisposeOnHide(true);
    this.videoID_ = videoID;
    this.model_ = null;
    this.leastLangMenuCount_ = 2;
    this.langMenuCount_ = 0;
    // The string which will denote no language selected
    this.emptyLang_ = '-------------'
    this.trackRequestLabel_ = 'Keep me posted';
    // The default content of request description text area
    this.descriptionInitial_ = 'I am requesting these subtitles because...';
    // Errors and warning which can occur in requesting subs
    this.emptyWarning_ = 'Please select at least one language.';
    this.submitError_ = 'An error occured in submitting the request.';
};
goog.inherits(mirosubs.requestdialog.Dialog, goog.ui.Dialog);

mirosubs.requestdialog.Dialog.prototype.createDom = function() {
    mirosubs.requestdialog.Dialog.superClass_.createDom.call(this);
    var $d = goog.bind(this.getDomHelper().createDom,
                       this.getDomHelper());
    var el = this.getElement();
    el.appendChild(
        $d('h3', null, 'Request subtitles'));
    this.contentDiv_ = $d('div', {'className':'mirosubs-request-div'}, "Loading...");
    el.appendChild(this.contentDiv_);
};

mirosubs.requestdialog.Dialog.prototype.enterDocument = function() {
    mirosubs.requestdialog.Dialog.superClass_.enterDocument.call(this);
    this.connectEvents_();
};

mirosubs.requestdialog.Dialog.prototype.setVisible = function(visible) {
    mirosubs.startdialog.Dialog.superClass_.setVisible.call(this, visible);
    if (visible)
        mirosubs.Rpc.call(
            'fetch_request_dialog_contents',
            { 'video_id': this.videoID_ },
            goog.bind(this.responseReceived_, this));
};

/**
 * Create a language select dropdown
 */
mirosubs.requestdialog.Dialog.prototype.makeDropdown_ = function($d){
    var options = [];
    contents = this.model_.getAllLanguages()
    options.push($d('option', {'value': ''}, this.emptyLang_));
    for (var i = 0; i < contents.length; i++){
         options.push($d('option', {'value': contents[i][0]}, contents[i][1]));
    }
    return $d('select', {'id':'mirosubs-requestlang-'+ ++this.langMenuCount_}, options);
};

/**
 * Adds the dropdown to the dialog contents.
 * Each call creats two dropdowns.
 */
mirosubs.requestdialog.Dialog.prototype.addDropdowns_ = function($d){
    dropdowns = []
    dropdowns.push(this.makeDropdown_($d));
    dropdowns.push(this.makeDropdown_($d));
    goog.dom.append(this.langDiv_, dropdowns);
};

/**
 * Add the rest of the fields (tracking request, description) to the
 * form.
 */
mirosubs.requestdialog.Dialog.prototype.addMetaForm_ = function($d){
    this.metaDiv_ = $d('div');
    this.checkBox_ = $d('input', {'type':'checkbox', 'checked':true, 'id':'mirosubs-request-track'});
    this.checkBoxLabel_ = $d('label', {'for':'mirosubs-request-track'}, this.trackRequestLabel_);
    this.description_ = $d('textarea', { 'id':'mirosubs-request-description' }, this.descriptionInitial_);
    this.metaDiv_.appendChild(this.checkBox_);
    this.metaDiv_.appendChild(this.checkBoxLabel_);
    this.metaDiv_.appendChild(this.description_);
    goog.dom.append(this.contentDiv_, this.metaDiv_);
}

mirosubs.requestdialog.Dialog.prototype.responseReceived_ = function(jsonResult) {
    this.fetchCompleted_ = true;
    // Create a Request object which will store the request relevent info.
    this.model_ = new mirosubs.requestdialog.Model(jsonResult, this.videoID_);
    goog.dom.removeChildren(this.contentDiv_);
    var $d = goog.bind(this.getDomHelper().createDom,
                       this.getDomHelper());

    // Create the form
    this.warningElem_ = $d('p', 'warning');
    this.langDiv_ = $d('div', {'class':'mirosubs-request-langs'}, $d('p', null, 'Select the languages in which subtitles are required'));
    goog.dom.append(this.contentDiv_, this.warningElem_);
    goog.dom.append(this.contentDiv_, this.langDiv_);
    goog.style.showElement(this.warningElem_, false);
    this.addDropdowns_($d);
    this.addMetaForm_($d);
    this.addLangButton_ =
    $d('a',
           {'href':'#',
            'className': "mirosubs-green-button mirosubs-big"},
            'Add Language');
    this.okButton_ =
    $d('a',
           {'href':'#',
            'className': "mirosubs-green-button mirosubs-big",
            'style':'clear:both;'},
           'Request');
    goog.dom.append(this.contentDiv_, this.okButton_);
    goog.dom.append(this.contentDiv_, this.addLangButton_);
    var clearDiv = $d('div');
    mirosubs.style.setProperty(clearDiv, 'clear', 'both');
    clearDiv.innerHTML = "&nbsp;";
    this.contentDiv_.appendChild(clearDiv);
    this.reposition();
    this.connectEvents_();
};

mirosubs.requestdialog.Dialog.prototype.connectEvents_ = function() {
    if (!this.isInDocument() || !this.fetchCompleted_)
        return;
    this.getHandler().
        listen(
            this.okButton_,
            goog.events.EventType.CLICK,
            this.okClicked_).
        listen(
            this.addLangButton_,
            goog.events.EventType.CLICK,
            this.addLangClicked_);
};

mirosubs.requestdialog.Dialog.prototype.okClicked_ = function(e) {
    e.preventDefault();
    if (this.okHasBeenClicked_)
        goog.style.showElement(this.warningElem_, false);

    this.okHasBeenClicked_ = true;

    // Stores the languages selected from the select box in the model
    for (i = 1; i < this.langMenuCount_; i++){
        var e = document.getElementById('mirosubs-requestlang-' + i);
        var lang = e.options[e.selectedIndex].value
        if (lang){
            this.model_.addRequestLanguage(lang);
        }
    }

    // Submit the request if at least one language is there
    if (this.model_.getRequestLanguages().length > 0){
        var track = document.getElementById('mirosubs-request-track').checked;
        var description = document.getElementById('mirosubs-request-description').value;
        this.model_.setTrackRequests(track);
        if (description != this.descriptionInitial_){
            this.model_.setDescription(description);
        }

        this.model_.submitRequest(goog.bind(this.requestCallback_,
                                  this));
    }
    else{
        goog.dom.setTextContent(this.warningElem_, this.emptyWarning_);
        goog.style.showElement(this.warningElem_, true);
    }
};


/**
 * Add more languages to the form
 */
mirosubs.requestdialog.Dialog.prototype.addLangClicked_ = function(e) {
    e.preventDefault();
    var $d = goog.bind(this.getDomHelper().createDom,
                       this.getDomHelper());
    this.addDropdowns_($d);
    this.reposition();
};

mirosubs.requestdialog.Dialog.prototype.requestCallback_ = function(jsonResult) {
    // If response has a key status, set to true, hide the dialog
    if (jsonResult["status"]){
        this.setVisible(false);
    }
    else{
        goog.dom.setTextContent(this.warningElem_, this.submitError_);
        goog.style.showElement(this.warningElem_, true);
    }
};
