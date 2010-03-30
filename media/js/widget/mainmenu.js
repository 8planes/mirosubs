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

goog.provide('mirosubs.MainMenu');

/**
 *
 * @param {boolean} isSubtitled
 * @param {Array.<Object<string, string>>=} Optional array of 
 *     json translation languages, where each language
 *     has a code and name.
 */
mirosubs.MainMenu = function(videoID, nullWidget, 
                             isSubtitled, opt_translationLanguages) {
    goog.ui.PopupMenu.call(this);
    // FIXME: is there a better way to do this rather than setting globals?
    goog.ui.MenuRenderer.CSS_CLASS = 'mirosubs-langmenu';
    goog.ui.MenuItemRenderer.CSS_CLASS = goog.getCssName('mirosubs-langmenuitem');
    goog.ui.MenuSeparatorRenderer.CSS_CLASS = goog.getCssName('mirosubs-langmenusep');
    this.videoID_ = videoID;
    this.nullWidget_ = nullWidget;
    this.isSubtitled_ = isSubtitled;
    this.translationLanguages_ = opt_translationLanguages || [];
    this.currentLangCode_ = null;
    this.showDownloadSRT_ = false;
    this.setToggleMode(true);
};
goog.inherits(mirosubs.MainMenu, goog.ui.PopupMenu);
mirosubs.MainMenu.MenuValues_ = {
    ADD_SUBTITLES: 'addsubs',
    ORIGINAL_LANG: 'originallang',
    NEW_LANG: 'newlang',
    LOGIN: 'login',
    CREATE_ACCOUNT: 'createaccount',
    LOGOUT: 'logout',
    SHARETHIS: 'sharethis'
};
mirosubs.MainMenu.EventType = {
    ADD_SUBTITLES: 'addsubs',
    LANGUAGE_SELECTED: 'langselected',
    ADD_NEW_LANGUAGE: 'newlanguage'
};
/**
 * Sets current language code -- used to add SRT download link to menu.
 * @param {?langCode} The current language code selected, or null to indicate
 *     original language.
 */
mirosubs.MainMenu.prototype.setCurrentLangCode = function(langCode) {
    this.currentLangCode_ = langCode;
};
mirosubs.MainMenu.prototype.showDownloadSRT = function(show) {
    this.showDownloadSRT_ = show;
};
mirosubs.MainMenu.prototype.onActionTaken_ = function(event) {
    var selectedValue = event.target.getModel();
    var mv = mirosubs.MainMenu.MenuValues_;
    var et = mirosubs.MainMenu.EventType;
    if (selectedValue == mv.ADD_SUBTITLES)
        this.dispatchEvent(et.ADD_SUBTITLES);
    else if (selectedValue == mv.ORIGINAL_LANG)
        this.dispatchEvent(
            new mirosubs.MainMenu
                .LanguageSelectedEvent());
    else if (selectedValue == mv.NEW_LANG)
        this.dispatchEvent(et.ADD_NEW_LANGUAGE);
    else if (selectedValue == mv.LOGIN)
        mirosubs.login();
    else if (selectedValue == mv.CREATE_ACCOUNT)
        alert('not yet implemented');
    else if (selectedValue == mv.LOGOUT)
        mirosubs.logout();
    else if (selectedValue == mv.SHARETHIS)
        alert('not yet implemented');
    else
        this.dispatchEvent(
            new mirosubs.MainMenu
                .LanguageSelectedEvent(selectedValue));
};
mirosubs.MainMenu.prototype.setTranslationLanguages = function(langs) {
    this.translationLanguages_ = langs;
};
mirosubs.MainMenu.prototype.setSubtitled = function() {
    this.isSubtitled_ = true;
};
mirosubs.MainMenu.prototype.enterDocument = function() {
    mirosubs.MainMenu.superClass_.enterDocument.call(this);
    this.getHandler().listen(
        this, goog.ui.Component.EventType.ACTION, this.onActionTaken_);
};
mirosubs.MainMenu.prototype.showMenu = function(target, x, y) {
    if (!this.isVisible() && !this.wasRecentlyHidden())
        this.setMenuItems_();
    mirosubs.MainMenu.superClass_.showMenu.call(this, target, x, y);
};
mirosubs.MainMenu.prototype.setMenuItems_ = function() {
    this.removeChildren(true);
    var mv = mirosubs.MainMenu.MenuValues_;
    if (this.isSubtitled_) {
        this.addChild(new goog.ui.MenuItem('Original',
            mv.ORIGINAL_LANG), true);
        var that = this;
        goog.array.forEach(this.translationLanguages_, function(lang) {
            that.addChild(new goog.ui.MenuItem(
                lang['name'], lang['code']), true);
        });
        this.addChild(new goog.ui.MenuItem(
            'Add new', mv.NEW_LANG), true);
    }
    else {
        this.addChild(new goog.ui.MenuItem('Add Subtitles', 
                                           mv.ADD_SUBTITLES), true);
    }
    this.addChild(new goog.ui.MenuSeparator(), true);
    if (mirosubs.currentUsername == null) {
        this.addChild(new goog.ui.MenuItem('Login', mv.LOGIN), true);
        this.addChild(new goog.ui.MenuItem('Create Account', 
                                           mv.CREATE_ACCOUNT), true);
    }
    else
        this.addChild(new goog.ui.MenuItem('Logout',
                                           mv.LOGOUT), true);
    this.addChild(new goog.ui.MenuSeparator(), true);
    this.addChild(new goog.ui.MenuItem('Share this',
                                       mv.SHARETHIS), true);
    if (this.showDownloadSRT_) {
        this.addChild(new goog.ui.MenuSeparator(), true);
        this.addChild(this.createDownloadSRTLink_(), true);
    }
};
mirosubs.MainMenu.prototype.createDownloadSRTLink_ = function() {
    var url = [mirosubs.BASE_URL,
               "/widget/download_", 
               (this.nullWidget_ ? "null_" : ""),
               "srt/?video_id=",
               '' + this.videoID_].join('');
    if (this.currentLangCode_)
        url += ['&lang_code=', this.currentLangCode_].join('')
    var $d = goog.bind(this.getDomHelper().createDom, 
                       this.getDomHelper());
    var menuItem = new goog.ui.MenuItem(
        $d('a', {'href':url}, 'Download SRT'));
    menuItem.setSelectable(false);
    menuItem.setEnabled(false);
    return menuItem;
};
mirosubs.MainMenu.LanguageSelectedEvent = function(opt_languageCode) {
    this.type = mirosubs.MainMenu.EventType.LANGUAGE_SELECTED;
    /**
     * The language code selected, or null to signify original 
     * language.
     * @type {?string}
     */
    this.languageCode = opt_languageCode;
};