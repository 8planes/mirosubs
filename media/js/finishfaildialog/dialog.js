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

goog.provide('mirosubs.finishfaildialog.Dialog');

/**
 * @constructor
 */
mirosubs.finishfaildialog.Dialog = function(logger, status, saveFn) {
    goog.ui.Dialog.call(this, null, true);
    this.setButtonSet(null);
    this.setDisposeOnHide(true);
    this.logger_ = logger;
    this.status_ = status;
    this.saveFn_ = saveFn;
};
goog.inherits(mirosubs.finishfaildialog.Dialog, goog.ui.Dialog);

/**
 * Called to show the finish fail dialog.
 * @param {mirosubs.subtitle.Logger} logger
 * @param {?number} status
 * @param {function()} saveFn
 */
mirosubs.finishfaildialog.Dialog.show = function(logger, status, saveFn) {
    var dialog = new mirosubs.finishfaildialog.Dialog(logger, status, saveFn);
    dialog.setVisible(true);
};

/**
 * Called by dialog if failure occurs again after calling save function
 * again.
 * @param {?number} status Either null if no status was returned 
 *     (probably timeout), 2xx if success but bad response, and otherwise
 *     if huge potentially weird server failure.
 */
mirosubs.finishfaildialog.Dialog.prototype.failedAgain = function(status) {
    
};

mirosubs.finishfaildialog.Dialog.prototype.createDom = function() {
    mirosubs.finishfaildialog.Dialog.superClass_.createDom.call(this);
    if (goog.isDefAndNotNull(this.status_))
        this.panel_ = new mirosubs.finishfaildialog.ErrorPanel();
    else
        this.panel_ = new mirosubs.finishfaildialog.CopyPanel();
    this.addChild(this.panel_, true);
};

