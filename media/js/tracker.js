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

goog.provide('mirosubs.Tracker');

/**
 * @constructor
 */
mirosubs.Tracker = function() {
    this.loadingMixpanel_ = false;
    this.mpmetrics_ = null;
    this.toCallOnLoad_ = [];
    this.logger_ = goog.debug.Logger.getLogger('mirosubs.Tracker');
};

goog.addSingletonGetter(mirosubs.Tracker);

mirosubs.Tracker.prototype.track = function(event, opt_props) {
    this.logger_.info(event);
    var props = opt_props || {};
    props['onsite'] = mirosubs.isFromDifferentDomain() ? 'no' : 'yes';
    this.callOrLoad_('track', [event, props]);
};

mirosubs.Tracker.prototype.callOrLoad_ = function(method, args) {
    if (this.mpmetrics_)
        this.call_(method, args);
    else {
        this.toCallOnLoad_.push([method, args]);
        this.loadMixpanel_();
    }
};

mirosubs.Tracker.prototype.call_ = function(method, args) {
    this.mpmetrics_[method].apply(this.mpmetrics_, args);
};

mirosubs.Tracker.prototype.checkMixpanel_ = function() {
    if (window['MixpanelLib']) {
        var mpname = 'mpmetricsunisubs';
        this.mpmetrics_ = window[mpname] = 
            new window['MixpanelLib'](
                '44205f56e929f08b602ccc9b4605edc3', mpname);
        for (var i = 0; i < this.toCallOnLoad_.length; i++)
            this.call_(this.toCallOnLoad_[i][0], this.toCallOnLoad_[i][1]);
        this.toCallOnLoad_ = [];
        return true;
    }
    else
        return false;
};

mirosubs.Tracker.prototype.loadMixpanel_ = function() {
    if (this.loadingMixpanel_)
        return;
    if (this.checkMixpanel_())
        return;
    this.loadingMixpanel_ = true;
    var scriptElem = goog.dom.createDom(
        'scr'+'ipt', {
            'type': 'text/javascript',
            'src': 'http://api.mixpanel.com/site_media/js/api/mixpanel.js'
        });
    var head = goog.dom.getElementsByTagNameAndClass('head')[0];
    head.appendChild(scriptElem);
    goog.Timer.callOnce(this.checkLoad_, 250, this);
};

mirosubs.Tracker.prototype.checkLoad_ = function() {
    if (!this.checkMixpanel_())
        goog.Timer.callOnce(this.checkLoad_, 250, this);
};