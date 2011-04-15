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

/**
 * @fileoverview Meant to be used in mirosubs.finishfaildialog.Dialog. 
 *    Corresponds to 'reattempt upload' state of that dialog.
 */

goog.provide('mirosubs.finishfaildialog.ReattemptUploadPanel');

/**
 * @constructor
 * @param {function()} finishFn the function to call when we're finished.
 *     This means the dialog can be closed.
 * @param {function()} errorFn the function to call to switch to error mode.
 */
mirosubs.finishfaildialog.ReattemptUploadPanel = function(finishFn, errorFn) {
    goog.ui.Component.call(this);
    this.finishFn_ = finishFn;
    this.errorFn_ = errorFn;
};
goog.inherits(mirosubs.finishfaildialog.ReattemptUploadPanel, goog.ui.Component);
