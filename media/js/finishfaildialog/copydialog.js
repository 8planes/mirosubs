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

goog.provide('mirosubs.finishfaildialog.CopyDialog');

/**
 * @constructor
 */
mirosubs.finishfaildialog.CopyDialog = function(headerText, textToCopy) {
    goog.ui.Dialog.call(this, 'mirosubs-modal-lang', true);
    this.setButtonSet(null);
    this.setDisposeOnHide(true);
    this.headerText_ = headerText;
    this.textToCopy_ = textToCopy;
};

goog.inherits(mirosubs.finishfaildialog.CopyDialog, goog.ui.Dialog);

mirosubs.finishfaildialog.CopyDialog.prototype.createDom = function() {
    mirosubs.finishfaildialog.CopyDialog.superClass_.createDom.call(this);
    var $d = goog.bind(this.getDomHelper().createDom, this.getDomHelper());
    this.textarea_ = $d('textarea', {'value': this.textToCopy_});
    goog.dom.append(
        this.getContentElement(),
        $d('p', null, this.headerText_),
        this.textarea_);
};

mirosubs.finishfaildialog.CopyDialog.prototype.enterDocument = function() {
    mirosubs.finishfaildialog.CopyDialog.superClass_.enterDocument.call(this);
    this.getHandler().listen(
        this.textarea_,
        ['focus', 'click'],
        this.focusTextarea_);
};

mirosubs.finishfaildialog.CopyDialog.prototype.focusTextarea_ = function() {
    var textarea = this.textarea_;
    goog.Timer.callOnce(function() { textarea.select(); });
};

mirosubs.finishfaildialog.CopyDialog.showForErrorLog = function(log) {
    var copyDialog = new mirosubs.finishfaildialog.CopyDialog(
        "This is the error report we generated. It would be a big help to us if you could copy and paste it into an email and send it to us at widget-logs@universalsubtitles.org. Thank you!",
        log);
    copyDialog.setVisible(true);
};

mirosubs.finishfaildialog.CopyDialog.showForSubs = function(jsonSubs) {
    var copyDialog = new mirosubs.finishfaildialog.CopyDialog(
        "Here are your subtitles. Please copy and paste them into a text file. You can email them to us at widget-logs@universalsubtitles.org.",
        mirosubs.finishfaildialog.CopyDialog.subsToString_(jsonSubs));
    copyDialog.setVisible(true);
};

mirosubs.finishfaildialog.CopyDialog.subsToString_ = function(jsonSubs) {
    var noTimes = goog.array.every(
        jsonSubs, 
        function(j) {
            return !j['start_time'] && !j['end_time'];
        });
    var baseString;
    if (noTimes)
        baseString = goog.json.serialize(jsonSubs);
    else
        baseString = mirosubs.SRTWriter.toSRT(jsonSubs);
    var serverModel = mirosubs.subtitle.MSServerModel.currentInstance;
    baseString = ['browser_id: ' + goog.net.cookies.get('unisub-user-uuid', 'n/a'), 
                  'video_id: ' + (serverModel ? 
                                  serverModel.getVideoID() : 'n/a'),
                  'session_pk: ' + (serverModel ?
                                    serverModel.getSessionPK() : 'n/a'),
                  baseString].join('\n');
    return baseString
};