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

goog.provide('mirosubs.subtitle.FinishedRightPanel');

mirosubs.subtitle.FinishedRightPanel = function(serverModel) {
    goog.ui.Component.call(this);
    this.serverModel_ = serverModel;
};
goog.inherits(mirosubs.subtitle.FinishedRightPanel, goog.ui.Component);
mirosubs.subtitle.FinishedRightPanel.prototype.createDom = function() {
    mirosubs.subtitle.FinishedRightPanel.superClass_.createDom.call(this);

    var $d = goog.bind(this.getDomHelper().createDom, this.getDomHelper());

    this.embedCodeInput_ = $d('input', {'type':'text'});
    var embedCode = ['<sc', 'ript type="text/javascript" src="',
                     this.serverModel_.getEmbedCode(),
                     '"></script>'].join('');
    this.embedCodeInput_['value'] = embedCode;

    var flashSpan = $d('span');
    flashSpan.innerHTML = mirosubs.Clippy.getHTML(embedCode);

    var shareButton = $d('a', {'className': 'mirosubs-done', 'href': '#'},
                         $d('span', null,
                            $d('strong', null, 'Share'),
                            goog.dom.createTextNode(
                                ' this video on Facebook & Twitter')));
    this.getHandler().listen(shareButton, 'click', this.shareClicked_);

    var helpDiv = $d('div', 'mirosubs-help');
    this.getElement().appendChild(helpDiv);
    helpDiv.appendChild($d('h2', null, 'Thanks for your contribution!'));
    helpDiv.appendChild(
        $d('p', null, 
           ['Your work is now available to anyone using the widget. You ', 
            'can paste this embed code in your site:'].join('')));
    helpDiv.appendChild($d('p', null, this.embedCodeInput_, flashSpan));
    helpDiv.appendChild(shareButton);
};
mirosubs.subtitle.FinishedRightPanel.prototype.enterDocument = function() {
    mirosubs.subtitle.FinishedRightPanel.superClass_.enterDocument.call(this);
    var that = this;
    this.getHandler().listen(this.embedCodeInput_, ['focus', 'click'], 
                             this.focusEmbed_);
};
mirosubs.subtitle.FinishedRightPanel.prototype.focusEmbed_ = function() {
    var that = this;
    goog.Timer.callOnce(function() {
        that.embedCodeInput_.select();
    });
};
mirosubs.subtitle.FinishedRightPanel.prototype.shareClicked_ = function(event) {
    alert('not implemented yet');
    event.preventDefault();
};