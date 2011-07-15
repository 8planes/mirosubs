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
goog.require("goog.string");
goog.require("goog.fx");
goog.require("goog.dom");
goog.require("goog.dom.forms");
goog.require("goog.ui.Dialog");

goog.provide('mirosubs.subtitle.ConfirmRejectiondDialog');

/**
 * @constructor
 * @private
 */
mirosubs.subtitle.ConfirmRejectiondDialog = function( callback) {
    goog.ui.Dialog.call(this, 'mirosubs-modal-completed', true);
    this.setButtonSet(null);
    this.setDisposeOnHide(true);
    this.callback_ = callback;
};
goog.inherits(mirosubs.subtitle.ConfirmRejectiondDialog, goog.ui.Dialog);

mirosubs.subtitle.ConfirmRejectiondDialog.prototype.createDom = function() {
    mirosubs.subtitle.ConfirmRejectiondDialog.superClass_.createDom.call(this);
    var $d = goog.bind(this.getDomHelper().createDom, this.getDomHelper());
    this.getElement().appendChild($d('h3', null, "Rollback to the latest approved version?"));
    this.checkboxSpan_ = $d('span');
    this.getElement().appendChild(
        $d('div', null,
           $d('p', null, 
              this.checkboxSpan_,
              goog.dom.createTextNode(
                  ["You have chosen to decline this version. This version will be rolled back to the last approved version."  + "Please offer some words of encouragement to your contributors. Tell them why you have not approved this version and give them some points to improve on. Your comments will be displayed in the comments area."].join("</p")
                  ))));
    this.commentContent_ = 
        $d('textarea', 
           {'href':'#', 
            'className': "rejection-comment"}); 

    this.getElement().appendChild(this.commentContent_);
    this.okButton_ = 
        $d('a', 
           {'href':'#', 
            'className': "mirosubs-green-button mirosubs-big"}, 
           'Rollback to last approved version');
    this.cancelButton_ = 
        $d('a', 
           {'href':'#', 
            'className': "mirosubs-green-button mirosubs-big"}, 
           'Cancel');
    
    this.getElement().appendChild(this.cancelButton_);
    this.getElement().appendChild(this.okButton_);
    var clearDiv = $d('div');
    mirosubs.style.setProperty(clearDiv, 'clear', 'both');
    clearDiv.innerHTML = "&nbsp;";
    this.getElement().appendChild(clearDiv);
};

mirosubs.subtitle.ConfirmRejectiondDialog.prototype.enterDocument = function() {
    mirosubs.subtitle.ConfirmRejectiondDialog.superClass_.enterDocument.call(this);
    var that = this;
    this.getHandler().listen(
        this.okButton_, 'click', this.okClicked_);
    this.getHandler().listen(
        this.cancelButton_, 'click', this.cancelClicked_);
};
mirosubs.subtitle.ConfirmRejectiondDialog.prototype.cancelClicked_ = function(e) {
    e.preventDefault();
    this.hideDialog();
}
mirosubs.subtitle.ConfirmRejectiondDialog.prototype.okClicked_ = function(e) {
    e.preventDefault();
    var comment = goog.string.collapseWhitespace(goog.dom.forms.getValue(this.commentContent_));
    this.callback_({'comment':comment});
    this.hideDialog();
};

mirosubs.subtitle.ConfirmRejectiondDialog.prototype.hideDialog = function(e){
    var that = this;
    var anim = new goog.fx.dom.FadeOutAndHide(this.getElement(), 200);
    anim.hide  = function (){
        that.setVisible(false);
    };
    anim.play();
    
}
/**
 * @param {boolean} completed
 * @param {function(boolean)} callback
 */
mirosubs.subtitle.ConfirmRejectiondDialog.show = function( callback) {
    var dialog = new mirosubs.subtitle.ConfirmRejectiondDialog(callback);
    dialog.setVisible(true);
};
