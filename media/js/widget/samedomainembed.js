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

goog.provide('mirosubs.widget.SameDomainEmbed');

mirosubs.widget.SameDomainEmbed = {};

mirosubs.widget.SameDomainEmbed.embed = function(widgetDiv, widgetConfig) {
    if (widgetConfig['debug_js']) {
        var debugWindow = new goog.debug.FancyWindow('main');
        debugWindow.setEnabled(true);
        debugWindow.init(); 
        mirosubs.DEBUG = true;
    }
    if (widgetConfig['returnURL'])
        mirosubs.returnURL = widgetConfig['returnURL'];
    var widget = new mirosubs.widget.Widget(widgetConfig);
    widget.decorate(widgetDiv);
    return widget;
};

(function() {
    goog.exportSymbol("mirosubs.widget.SameDomainEmbed.embed", 
                      mirosubs.widget.SameDomainEmbed.embed);

    goog.exportSymbol("mirosubs.video", mirosubs.video);
    var v = mirosubs.video;
    v["supportsVideo"] = v.supportsVideo;
    v["supportsH264"] = v.supportsH264;
    v["supportsOgg"] = v.supportsOgg;
    v["supportsWebM"] = v.supportsWebM;

    goog.exportSymbol(
        "mirosubs.widget.Widget.prototype.selectMenuItem",
        mirosubs.widget.Widget.prototype.selectMenuItem);

    goog.exportSymbol(
        "mirosubs.MainMenu.Selection",
        mirosubs.MainMenu.Selection);
    var s = mirosubs.MainMenu.Selection;
    s['ADD_SUBTITLES'] = s.ADD_SUBTITLES;
    s['EDIT_SUBTITLES'] = s.EDIT_SUBTITLES;
    s['LANGUAGE_SELECTED'] = s.LANGUAGE_SELECTED;
    s['ADD_NEW_LANGUAGE'] = s.ADD_NEW_LANGUAGE;
    s['TURN_OFF_SUBS'] = s.TURN_OFF_SUBS;
})();
