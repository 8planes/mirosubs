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
    var widget = new mirosubs.widget.Widget(widgetConfig);
    widget.decorate(widgetDiv);
};

// see http://code.google.com/closure/compiler/docs/api-tutorial3.html#mixed
window["mirosubs"] = mirosubs;
mirosubs["widget"] = mirosubs.widget;
mirosubs.widget["SameDomainEmbed"] = mirosubs.widget.SameDomainEmbed;
mirosubs.widget.SameDomainEmbed["embed"] = 
    mirosubs.widget.SameDomainEmbed.embed;
