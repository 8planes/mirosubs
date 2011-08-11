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

goog.provide('mirosubs.widgetizer.Vimeo');

/**
 * @constructor
 */
mirosubs.widgetizer.Vimeo = function() {
    mirosubs.widgetizer.VideoPlayerMaker.call(this);
    /**
     * @const
     */
    this.ON_VIMEO_SITE =
        window.location.hostname.match(/vimeo\.com$/) != null;
};
goog.inheirts(mirosubs.widgetizer.Vimeo,
              mirosubs.widgetizer.VideoPlayerMaker);

mirosubs.widgetizer.Vimeo.prototype.logger_ = 
    goog.debug.Logger.getLogger('mirosubs.widgetizer.Vimeo');

mirosubs.widgetizer.Vimeo.prototype.unwidgetizedElement_ = function() {
    if (this.ON_VIMEO_SITE) {
        var moviePlayer = goog.dom.getElementsByTagAndClassName('object');
        
    }
};