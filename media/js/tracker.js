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
    this.accountSet_ = false;
    if (goog.DEBUG) {
        this.logger_ = goog.debug.Logger.getLogger('mirosubs.Tracker');
    }
};

goog.addSingletonGetter(mirosubs.Tracker);

mirosubs.Tracker.prototype.ACCOUNT_ = 'UA-163840-22';
mirosubs.Tracker.prototype.PREFIX_ = 'usubs';

mirosubs.Tracker.prototype.gaq_ = function() {
    return window['_gaq'];
};

mirosubs.Tracker.prototype.trackEvent = function(category, action, opt_label, opt_value) {
    if (mirosubs.REPORT_ANALYTICS) {
        if (goog.DEBUG) {
            this.logger_.info('tracking event: ' + category + 
                              ' for action ' + action + 
                              (opt_label ? (' with label ' + opt_label) : ""));
        }
        this.setAccount_();
        this.gaq_().push(
            [this.PREFIX_ + "._trackEvent", category, action, opt_label, opt_value]);
    }
};

mirosubs.Tracker.prototype.trackPageview = function(pageview, opt_props) {
    if (mirosubs.REPORT_ANALYTICS) {
        if (goog.DEBUG) {
            this.logger_.info(pageview);
        }
        var props = opt_props || {};
        props['onsite'] = mirosubs.isFromDifferentDomain() ? 'no' : 'yes';
        this.setAccount_();
        this.gaq_().push([this.PREFIX_ + '._trackPageview', '/widget/' + pageview]);
    }
};

mirosubs.Tracker.prototype.setAccount_ = function() {
    if (!this.accountSet_) {
        window['_gaq'] = this.gaq_() || [];
        this.loadGA_();
        this.gaq_().push([this.PREFIX_ + '._setAccount', this.ACCOUNT_]);
        this.accountSet_ = true;
    }
};

mirosubs.Tracker.prototype.loadGA_ = function() {
    if (mirosubs.REPORT_ANALYTICS) {
        var url = ('https:' == document.location.protocol ? 'https://ssl' : 'http://www') + '.google-analytics.com/ga.js';
        mirosubs.addScript(url, true);
    }
};
