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

goog.provide('mirosubs.widget.BaseState');

/**
 * @fileoverview Provides a strongly-typed version of params passed in from page
 *
 */

/**
 * @constructor
 * @param {Object} baseStateParam parameter from the embed code on the page.
 */
mirosubs.widget.BaseState = function(baseStateParam) {
    /** 
     * @type {boolean}
     */
    this.NOT_NULL = !!baseStateParam;
    if (this.NOT_NULL) {
        /**
         * @type {string?} Either foreign language, or null means native lang.
         */
        this.LANGUAGE = baseStateParam['language'];
        if (typeof(this.LANGUAGE) == 'undefined')
            this.LANGUAGE = null;
        /**
         * @type {number?}
         */
        this.REVISION = baseStateParam['revision'];
        if (typeof(this.REVISION) == 'undefined')
            this.REVISION = null;
        /**
         * @type {boolean}
         */
        this.START_PLAYING = !!baseStateParam['start_playing'];
        this.ORIGINAL_PARAM = baseStateParam;
    }
    else {
        this.ORIGINAL_PARAM = null;
        this.REVISION = null;
        this.LANGUAGE = null;
    }
};