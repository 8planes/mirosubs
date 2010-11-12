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

goog.provide('mirosubs.translate.TranslationRightPanel');
/**
* @constructor
* @extends mirosubs.RightPanel
*/

mirosubs.translate.TranslationRightPanel = function(dialog,
                                                    serverModel,
                                                    helpContents,
                                                    extraHelp,
                                                    legendKeySpecs,
                                                    showRestart,
                                                    doneStrongText,
                                                    doneText,
                                                    extraHelpHeader) {
    mirosubs.RightPanel.call(this, serverModel, helpContents, extraHelp,
                             legendKeySpecs,
                             showRestart, doneStrongText, doneText);
    this.extraHelpHeader_ = extraHelpHeader;
    this.dialog_ = dialog;
};
goog.inherits(mirosubs.translate.TranslationRightPanel, mirosubs.RightPanel);

mirosubs.translate.TranslationRightPanel.prototype.appendExtraHelpInternal =
    function($d, el)
{
    var extraDiv = $d('div', 'mirosubs-extra mirosubs-translationResources');
    extraDiv.appendChild($d('h3', {'className': 'mirosubs-resources'}, this.extraHelpHeader_));

    var lst = $d('ul', {'className': 'mirosubs-resourceList'});
    for (var i = 0; i < this.extraHelp_.length; i++) {
        var linkText = this.extraHelp_[i][0];
        var linkHref = this.extraHelp_[i][1];
        lst.appendChild($d('li', {'className': 'mirosubs-resource'},
                           $d('a', {'target':'_blank', 'href': linkHref,
                                    'className': 'mirosubs-resourceLink' },
                              linkText)));
    }
    extraDiv.appendChild(lst);
    el.appendChild(extraDiv);
    this.autoTranslateLink_ = 
        $d('a', {'href':'#'}, 'Auto-translate empty fields');
    this.changeTimingLink_ =
        $d('a', {'href':'#'}, 'Change subtitle timing');
    el.appendChild(
        $d('ul', 'mirosubs-translationOptions',
           $d('li', 'mirosubs-autoTranslate',
              this.autoTranslateLink_,
              $d('span', null, '(using google)')),
           $d('li', 'mirosubs-changeTiming',
              this.changeTimingLink_,
              $d('span', null, '(advanced users)'))));
};

mirosubs.translate.TranslationRightPanel.prototype.enterDocument = function() {
    mirosubs.translate.TranslationRightPanel.superClass_.enterDocument.call(this);
    var that = this;
    this.getHandler().listen(
        this.changeTimingLink_,
        'click',
        function(e) {
            e.preventDefault();
            that.dialog_.forkAndClose();
        });
};