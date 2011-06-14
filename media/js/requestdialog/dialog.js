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
};
goog.inherits(mirosubs.requestdialog.Dialog, goog.ui.Dialog);

mirosubs.requestdialog.Dialog.prototype.createDom = function() {
    mirosubs.requestdialog.Dialog.superClass_.createDom.call(this);
    var $d = goog.bind(this.getDomHelper().createDom,
                       this.getDomHelper());
    var el = this.getElement();
    el.appendChild(
        $d('h3', null, 'Request subtitles'));
    this.contentDiv_ = $d('div', null, "Loading...");
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
            'fetch_start_dialog_contents',
            { 'video_id': this.videoID_ },
            goog.bind(this.responseReceived_, this));
};

mirosubs.requestdialog.Dialog.prototype.responseReceived_ = function(jsonResult) {
    this.fetchCompleted_ = true;
    goog.dom.removeChildren(this.contentDiv_);
    var $d = goog.bind(this.getDomHelper().createDom,
                       this.getDomHelper());
    this.warningElem_ = $d('p', 'warning');
    goog.dom.append(this.contentDiv_, this.warningElem_);
    goog.style.showElement(this.warningElem_, false);
    this.okButton_ =
        $d('a',
           {'href':'#',
            'className': "mirosubs-green-button mirosubs-big"}, 
           'Request');
    goog.dom.append(this.contentDiv_, this.okButton_);
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
            this.okClicked_);
};

mirosubs.requestdialog.Dialog.prototype.okClicked_ = function(e) {
    e.preventDefault();
    if (this.okHasBeenClicked_)
        return;
    this.okHasBeenClicked_ = true;
    goog.dom.setTextContent(this.okButton_, "Posting Request...");
    goog.dom.classes.add(this.okButton_, "mirosubs-button-disabled");
};
