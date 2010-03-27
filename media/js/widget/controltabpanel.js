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

goog.provide('mirosubs.ControlTabPanel');

mirosubs.ControlTabPanel = function(uuid, showTab, videoID, 
                                    translationLanguages, nullWidget) {
    goog.events.EventTarget.call(this);
    
    this.videoID_ = videoID;
    this.nullWidget_ = nullWidget;
    this.translationLanguages_ = translationLanguages;
    var $ = goog.dom.$;
    this.controlTabDiv_ = $(uuid + "_menu");
    this.controlTabLoadingImage_ = $(uuid + "_loading");
    if (showTab == 0 || showTab == 1 || showTab == 3) {
        this.mainMenuLink_ = $(uuid + "_tabMainMenu");
        this.popupMenu_ = new mirosubs.MainMenu(
            showTab == 3, translationLanguages);
        this.popupMenu_.render(document.body);
        this.popupMenu_.attach(this.mainMenuLink_,
                               goog.positioning.Corner.BOTTOM_LEFT,
                               goog.positioning.Corner.TOP_LEFT);
        goog.events.listen(this.mainMenuLink_, 'click',
                           function(event) {
                               console.log('clicked');
                               event.preventDefault();
                           });        
        goog.events.listen(this.popupMenu_, 
                           goog.object.getValues(mirosubs.MainMenu.EventType), 
                           this.menuEvent_, false, this);
    }
};
goog.inherits(mirosubs.ControlTabPanel, goog.events.EventTarget);

mirosubs.ControlTabPanel.prototype.showLoading = function(loading) {
    this.controlTabLoadingImage_.style.display = loading ? '' : 'none';
};

mirosubs.ControlTabPanel.prototype.setAvailableLanguages = function(langs) {
    this.translationLanguages_ = langs;
    this.popupMenu_.setTranslationLanguages(langs);
};

mirosubs.ControlTabPanel.prototype.showSelectLanguage = function() {
    // FIXME: this text is duplicated from templates/widget/widget.html
    this.setMainMenuLinkText_("Choose Language...");
    this.popupMenu_.setSubtitled();
};

mirosubs.ControlTabPanel.prototype.menuEvent_ = function(event) {
    if (event.type == mirosubs.MainMenu.EventType.LANGUAGE_SELECTED) {
        var linkText = "Original";
        if (event.languageCode) {
            var language =
                goog.array.find(this.translationLanguages_,
                                function(tl) {
                                    return tl['code'] == event.languageCode;
                                });
            linkText = language['name'];
        }
        this.setMainMenuLinkText_(linkText);
    }
    // have to propagate event manually
    this.dispatchEvent(event);
};

mirosubs.ControlTabPanel.prototype.setMainMenuLinkText_ = function(text) {
    goog.dom.setTextContent(this.mainMenuLink_, text);
};

mirosubs.ControlTabPanel.prototype.setVisible = function(visible) {
    this.controlTabDiv_.style.display = visible ? '' : 'none';
};

mirosubs.ControlTabPanel.prototype.disposeInternal = function() {
    mirosubs.ControlTabPanel.superClass_.disposeInternal.call(this);
    if (this.subtitleMeLink_)
        goog.events.unlisten(this.subtitleMeLink_, 'click', 
                             this.subtitleMeListener_, false, this);
};
