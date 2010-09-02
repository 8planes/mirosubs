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

goog.provide('mirosubs.widget.DropDown');

/**
 *
 * @param {string} videoID
 * @param {boolean} isSubtitled
 * @param {Array.<Object<string, string>>=} Optional array of
 *     json translation languages, where each language
 *     has a code and name.
 */
mirosubs.widget.DropDown = function(videoID, isSubtitled, opt_translationLanguages) {
    //goog.ui.PopupMenu.call(this, null, new mirosubs.widget.DropDownRenderer());
    goog.ui.Component.call(this);
    
    //goog.ui.MenuRenderer.CSS_CLASS = 'mirosubs-dropdown';
    //goog.ui.MenuItemRenderer.CSS_CLASS = goog.getCssName('mirosubs-langmenuitem');
    //goog.ui.MenuSeparatorRenderer.CSS_CLASS = goog.getCssName('mirosubs-langmenusep');

    this.videoID = videoID;
    this.isSubtitled = isSubtitled;
    this.translationLanguages_ = opt_translationLanguages || [];
    
    //this.setToggleMode(true);
};

goog.inherits(mirosubs.widget.DropDown, goog.ui.Component);

mirosubs.widget.DropDown.prototype.createDom = function() {
    mirosubs.widget.DropDown.superClass_.createDom.call(this);
    var $d = goog.bind(this.getDomHelper().createDom, this.getDomHelper());
    this.getElement().className = 'mirosubs-dropdown';
    
    this.languageListContainer_ = $d('div', {'className': 'mirosubs-languageList'});
    this.actions_ = $d('div', {'className': 'mirosubs-actions'});

    this.languageList_ = $d('ul', null,
        $d('li', {'className': 'mirosubs-hintTranslate'}, 'Missing sections translated by Google Translate'),
        $d('li', {'className': 'mirosubs-activeLanguage'}, 
           $d('a', {'href': '#'}, 'Original language')));
    // TODO: add other stuff
    this.languageListContainer_.appendChild(this.languageList_);
    this.actions_.appendChild($d('h5', {'className': 'mirosubs-uniLogo'}, 'Universal Subtitles'));
    this.actions_.appendChild($d('h4', null, 'THIS VIDEO'));
    this.actions_.appendChild($d('ul', null, $d('li', {'className': 'mirosubs-addTranslation'}, $d('a', {'href': '#'}, 'Add New Translation'))));
    this.actions_.appendChild($d('h4', null, 'MY SETTINGS'));
    
    this.getElement().appendChild(this.languageListContainer_);
    this.getElement().appendChild(this.actions_);
};

mirosubs.widget.DropDown.prototype.enterDocument = function() {
    mirosubs.widget.DropDown.superClass_.enterDocument.call(this);
    this.getHandler().listen(
        this, goog.ui.Component.EventType.ACTION, this.onActionTaken_);
};

mirosubs.widget.DropDown.MenuValues_ = {
    ADD_SUBTITLES: 'addsubs',
    EDIT_SUBTITLES: 'editsubs',
    ORIGINAL_LANG: 'originallang',
    NEW_LANG: 'newlang',
    LOGIN: 'login',
    CREATE_ACCOUNT: 'createaccount',
    LOGOUT: 'logout',
    TURNOFFSUBS: 'turnoffsubs'
};

mirosubs.widget.DropDown.Selection = {
    ADD_SUBTITLES: 'addsubs',
    EDIT_SUBTITLES: 'editsubs',
    LANGUAGE_SELECTED: 'langselected',
    ADD_NEW_LANGUAGE: 'newlanguage',
    TURN_OFF_SUBS: 'turnoffsubs'
};

mirosubs.widget.DropDown.prototype.showMenu = function(target, x, y) {
    if (!this.isVisible() && !this.wasRecentlyHidden())
        this.setMenuItems_();

    if (mirosubs.BrokenWarning.needsWarning()) {
        var warning = new mirosubs.BrokenWarning();
        warning.setVisible(true);
        return;
    }

    this.showMenuInternal_(target, x, y);
};
mirosubs.widget.DropDown.prototype.showMenuInternal_ = function(target, x, y) {
    mirosubs.widget.DropDown.superClass_.showMenu.call(this, target, x, y);
};
mirosubs.widget.DropDown.prototype.createItem_ = function(caption, data) {
    return new goog.ui.MenuItem(caption, data, null,
                                new mirosubs.widget.DropDownItemRenderer());
};
mirosubs.widget.DropDown.prototype.setMenuItems_ = function() {
    this.removeChildren(true);
    var mv = mirosubs.widget.DropDown.MenuValues_;
    var $i = goog.bind(this.createItem_, this);
    if (this.showingSubs_) {
        if (this.isSubtitled_)
            this.addChild($i('Edit subs', mv.EDIT_SUBTITLES), true);
        this.addChild($i('Turn off subs', mv.TURNOFFSUBS), true);
        this.addChild(new goog.ui.MenuSeparator(), true);
    }
    if (this.isSubtitled_) {
        this.addChild($i('Original', mv.ORIGINAL_LANG), true);
        var that = this;
        goog.array.forEach(this.translationLanguages_, function(lang) {
            that.addChild($i(lang['name'], lang['code']), true);
        });
        this.addChild($i('Add a translation', mv.NEW_LANG), true);
    }
    else {
        this.addChild($i('Add Subtitles', mv.ADD_SUBTITLES), true);
    }
    this.addChild(new goog.ui.MenuSeparator(), true);
    if (mirosubs.currentUsername == null) {
        this.addChild($i('Login', mv.LOGIN), true);
        this.addChild($i('Create Account', mv.CREATE_ACCOUNT), true);
    }
    else
        this.addChild($i('Logout', mv.LOGOUT), true);
    this.addChild(new goog.ui.MenuSeparator(), true);
    if (this.showingSubs_) {
        this.addChild(new goog.ui.MenuSeparator(), true);
        this.addChild(this.createDownloadSRTLink_(), true);
    }
};

mirosubs.widget.DropDown.prototype.onActionTaken_ = function(event) {
    var selectedValue = event.target.getModel();
    var mv = mirosubs.MainMenu.MenuValues_;
    var et = mirosubs.MainMenu.Selection;
    if (selectedValue == mv.ADD_SUBTITLES)
        this.dispatchEvent(et.ADD_SUBTITLES);
    else if (selectedValue == mv.EDIT_SUBTITLES)
        this.dispatchEvent(et.EDIT_SUBTITLES);
    else if (selectedValue == mv.ORIGINAL_LANG)
        this.dispatchEvent(
            new mirosubs.MainMenu
                .LanguageSelectedEvent());
    else if (selectedValue == mv.NEW_LANG)
        this.dispatchEvent(et.ADD_NEW_LANGUAGE);
    else if (selectedValue == mv.LOGIN)
        mirosubs.login();
    else if (selectedValue == mv.CREATE_ACCOUNT)
        mirosubs.createAccount();
    else if (selectedValue == mv.LOGOUT)
        mirosubs.logout();
    else if (selectedValue == mv.TURNOFFSUBS)
        this.dispatchEvent(et.TURN_OFF_SUBS);
    else
        this.dispatchEvent(
            new mirosubs.MainMenu
                .LanguageSelectedEvent(selectedValue));
};