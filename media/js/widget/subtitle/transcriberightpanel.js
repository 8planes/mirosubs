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

goog.provide('mirosubs.subtitle.TranscribeRightPanel');

mirosubs.subtitle.TranscribeRightPanel = function(serverModel,
                                            helpContents,
                                            legendKeySpecs,
                                            showRestart,
                                            doneStrongText,
                                            doneText) {
    mirosubs.RightPanel.call(this, serverModel, helpContents, legendKeySpecs, 
                             showRestart, doneStrongText, doneText);
};
goog.inherits(mirosubs.subtitle.TranscribeRightPanel, mirosubs.RightPanel);
mirosubs.subtitle.TranscribeRightPanel.AUTOPAUSE_CHANGED = 'autopausechanged';
mirosubs.subtitle.TranscribeRightPanel.prototype.appendLegendContentsInternal = 
    function($d, legendDiv) 
{
    mirosubs.subtitle.TranscribeRightPanel.superClass_
        .appendLegendContentsInternal.call(this, $d, legendDiv);
    this.autopauseCheckboxSpan_ = $d('span');
    legendDiv.appendChild($d('div', 'mirosubs-autopause', 
                             this.autopauseCheckboxSpan_,
                             goog.dom.createTextNode(' Enable Autopause')));
};

mirosubs.subtitle.TranscribeRightPanel.prototype.enterDocument = function() {
    mirosubs.subtitle.TranscribeRightPanel.superClass_.enterDocument.call(this);
    if (!this.autopauseCheckBox_) {
        // FIXME: passing true is hacky
        this.autopauseCheckBox_ = new goog.ui.Checkbox(true);
        this.autopauseCheckBox_.decorate(this.autopauseCheckboxSpan_);
        this.autopauseCheckBox_.setLabel(this.autopauseCheckBox_.getElement().parentNode);
    }
    this.getHandler().listen(this.autopauseCheckBox_, 
                             goog.ui.Component.EventType.CHANGE, 
                             this.autopauseCheckBoxChanged_);
};

mirosubs.subtitle.TranscribeRightPanel.prototype.autopauseCheckBoxChanged_ = function(event) {
    this.dispatchEvent(
        new mirosubs.subtitle.TranscribeRightPanel.AutoPauseChangeEvent(
            this.autopauseCheckBox_.getChecked()));
};

mirosubs.subtitle.TranscribeRightPanel.AutoPauseChangeEvent = function(on) {
    this.type = mirosubs.subtitle.TranscribeRightPanel.AUTOPAUSE_CHANGED;
    this.on = on;
};