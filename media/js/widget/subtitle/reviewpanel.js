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

goog.provide('mirosubs.subtitle.ReviewPanel');

mirosubs.subtitle.ReviewPanel = function(subtitles, videoPlayer, 
                                         captionManager, focusableElem) {
    mirosubs.subtitle.SyncPanel.call(this, subtitles, videoPlayer, 
                                     captionManager, focusableElem);
};
goog.inherits(mirosubs.subtitle.ReviewPanel, mirosubs.subtitle.SyncPanel);
/**
 * @override
 */
mirosubs.subtitle.ReviewPanel.prototype.createHelpDom = function($d) {
    var helpLines = ['Time to review your work.  Doubleclick on any text to edit it.',
                     ['To change subtitle timing, tap spacebar to skip to the next ',
                      'subtitle immediately.  To delay, press and hold spacebar to ',
                      'keep the next subtitle from displaying until you let go.'].join('')];
    return mirosubs.subtitle.SubtitleList.createHelpLi($d, helpLines, 
                                                       'Syncing Controls', 
                                                       true, 'BEGIN');
};