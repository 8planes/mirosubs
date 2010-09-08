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

goog.provide('mirosubs.Extension');

mirosubs.Extension = function() {
    this.shown_ = false;
    if (window[mirosubs.Extension.LOADED_FUN])
        goog.Timer.callOnce(window[mirosubs.Extension.LOADED_FUN]);
};
goog.addSingletonGetter(mirosubs.Extension);

mirosubs.Extension.LOADED_FUN = 'onUnisubsExtensionLoaded';
mirosubs.Extension.TOGGLE_FUN = 'onUnisubsExtensionToggled';

/**
 * Called by jetpack code whenever the page is loaded.
 * @param {boolean} enabled whether the extension is enabled or not
 */
mirosubs.Extension.prototype.show = function(enabled) {
    if (this.shown_)
        return;
    this.shown_ = true;
    if (mirosubs.Widgetizer.getInstance().videosExist())
        this.addElementToPage_(enabled);
};

mirosubs.Extension.prototype.addElementToPage_ = function(enabled) {
    this.enabled_ = enabled;
    mirosubs.Widgetizer.getInstance().addHeadCss();
    var $d = goog.dom.createDom;
    var $t = goog.dom.createTextNode;
    this.enableLink_ = this.createEnableLink_($d, enabled);
    this.reportProblemLink_ = this.createReportProblemLink_(enabled);
    this.learnMoreLink_ = this.createLearnMoreLink_(enabled);
    var div = $d('div', 'mirosubs-extension mirosubs-extension-' + 
                 (enabled ? 'enabled' : 'disabled'),
                 $d('span', null, 
                    'Universal Subtitles Addon ' + 
                    (enabled ? 'Enabled!' : 'Disabled')),
                 this.enableLink_,
                 $t(' / '),
                 this.reportProblemLink_,
                 $d(' / '),
                 this.learnMoreLinkLink_);
};

mirosubs.Extension.prototype.createEnableLink_ = function($d, enabled) {
    var link = $d('a', {'href':'#'}, enabled ? 'disable' : 'enable');
    return link;
};

mirosubs.Extension.prototype.createReportProblemLink_ = function($d) {
    
};

mirosubs.Extension.prototype.createLearnMoreLink_ = function($d) {
    
};