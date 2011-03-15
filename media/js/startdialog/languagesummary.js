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

goog.provide('mirosubs.startdialog.LanguageSummary');

/**
 * @constructor
 */
mirosubs.startdialog.LanguageSummary = function(json) {
    this.LANGUAGE = json['language'];
    this.FORKED = json['forked'];
    this.IS_COMPLETE = json['is_complete'];
    this.PERCENT_DONE = json['percent_done'];
    this.STANDARD = json['standard'];
};