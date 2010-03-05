goog.provide('mirosubs.ControlTabPanel');
goog.provide('mirosubs.ControlTabPanel.EventType');

mirosubs.ControlTabPanel = function(uuid, showTab, videoID, 
                                    translationLanguages, nullWidget) {
    goog.events.EventTarget.call(this);
    
    this.videoID_ = videoID;
    var $ = goog.dom.$;
    this.controlTabDiv_ = $(uuid + "_menu");
    this.controlTabLoadingImage_ = $(uuid + "_loading");
    if (showTab == 0 || showTab == 1) {
        this.subtitleMeLink_ = 
            $(uuid + (showTab == 0 ? "_tabSubtitleMe" : "_tabContinue"));
        goog.events.listen(this.subtitleMeLink_, 'click', 
                           this.subtitleMeListener_, false, this);
    }
    this.tabSelectLanguageLink_ = $(uuid + "_tabSelectLanguage");
    this.nullWidget_ = nullWidget;

    goog.ui.MenuRenderer.CSS_CLASS = 'mirosubs-langmenu';
    goog.ui.MenuItemRenderer.CSS_CLASS = goog.getCssName('mirosubs-langmenuitem');
    this.popupMenu_ = new goog.ui.PopupMenu();
    this.popupMenu_.addChild(new goog.ui.MenuItem('Original', 
                             mirosubs.ControlTabPanel.LANGUAGE_ORIGINAL));
    this.popupMenu_.addChild(new goog.ui.MenuItem(
        'Add new', mirosubs.ControlTabPanel.LANGUAGE_NEW));
    this.setAvailableLanguages(translationLanguages);
    this.popupMenu_.render(document.body);
    this.popupMenu_.setToggleMode(true);
    this.popupMenu_.attach(this.tabSelectLanguageLink_,
                           goog.positioning.Corner.BOTTOM_LEFT,
                           goog.positioning.Corner.TOP_LEFT);

    goog.events.listen(this.tabSelectLanguageLink_, 'click',
                       function(event) {
                           event.preventDefault();
                       });
    goog.events.listen(this.popupMenu_, 'action', 
                       this.languageSelected_, false, this);
};
goog.inherits(mirosubs.ControlTabPanel, goog.events.EventTarget);

mirosubs.ControlTabPanel.LANGUAGE_ORIGINAL = 'originallang';
mirosubs.ControlTabPanel.LANGUAGE_NEW = 'newlang';


mirosubs.ControlTabPanel.EventType = {
    SUBTITLEME_CLICKED: 'subtitlemeclicked',
    LANGUAGE_SELECTED: 'langselected',
    ADD_NEW_LANGUAGE: 'newlanguage'
};

mirosubs.ControlTabPanel.prototype.subtitleMeListener_ = function(event) {
    this.dispatchEvent(mirosubs.ControlTabPanel.EventType.SUBTITLEME_CLICKED);
    event.preventDefault();
};

mirosubs.ControlTabPanel.prototype.showLoading = function(loading) {
    this.controlTabLoadingImage_.style.display = loading ? '' : 'none';
};

mirosubs.ControlTabPanel.prototype.setAvailableLanguages = function(langs) {
    this.translationLanguages_ = langs;
    var i;
    while (this.popupMenu_.getChildCount() > 2)
        this.popupMenu_.removeChildAt(1);
    for (i = 0; i < langs.length; i++)
        this.popupMenu_.addChildAt(new goog.ui.MenuItem(
            langs[i]['name'], langs[i]['code']), i + 1);
};

mirosubs.ControlTabPanel.prototype.showSelectLanguage = function() {
    if (this.subtitleMeLink_)
        this.subtitleMeLink_.style.display = 'none';
    this.tabSelectLanguageLink_.style.display = '';
};

mirosubs.ControlTabPanel.prototype.languageSelected_ = function(event) {
    if (event.target.getModel() == mirosubs.ControlTabPanel.LANGUAGE_ORIGINAL) {
        var that = this;
        this.showLoading(true);
        mirosubs.Rpc.call('fetch_captions' + (this.nullWidget_ ? '_null' : ''), 
                          { 'video_id' : this.videoID_ },
                          function(captions) {
                              goog.dom.setTextContent(that.tabSelectLanguageLink_, 
                                                      'Original');
                              that.showLoading(false);
                              that.dispatchEvent(new mirosubs.ControlTabPanel
                                                 .LanguageSelectedEvent('', captions)); 
                          });
    }
    else if (event.target.getModel() == mirosubs.ControlTabPanel.LANGUAGE_NEW) {
        var that = this;
        this.showLoading(true);
        mirosubs.Rpc.call('fetch_captions_and_open_languages' + 
                          (this.nullWidget_ ? '_null' : ''), 
                          { 'video_id': this.videoID_ },
                          function(result) {
                              that.showLoading(false);
                              that.dispatchEvent(new mirosubs.ControlTabPanel.
                                                 AddNewLanguageEvent(result['captions'],
                                                                     result['languages']));
                          });
    }
    else {
        var languageCode = event.target.getModel();
        var language = 
        goog.array.find(this.translationLanguages_,
                        function(tl) {
                            return tl['code'] == languageCode;
                        });
        var that = this;
        this.showLoading(true);
        mirosubs.Rpc.call('fetch_translations' + 
                          (this.nullWidget_ ? '_null' : ''), 
                          { 'video_id' : this.videoID_,
                            'language_code': languageCode }, 
                          function(captions) {
                              goog.dom.setTextContent(that.tabSelectLanguageLink_, 
                                                      language['name']);
                              that.showLoading(false);
                              that.dispatchEvent(new mirosubs.ControlTabPanel
                                                 .LanguageSelectedEvent(languageCode, 
                                                                        captions));
            });        
    }
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

mirosubs.ControlTabPanel.LanguageSelectedEvent = function(languageCode, captions) {
    this.type = mirosubs.ControlTabPanel.EventType.LANGUAGE_SELECTED;
    this.languageCode = languageCode;
    this.captions = captions;
};
goog.inherits(mirosubs.ControlTabPanel.LanguageSelectedEvent, goog.events.Event);

mirosubs.ControlTabPanel.AddNewLanguageEvent = function(captions, languages) {
    this.type = mirosubs.ControlTabPanel.EventType.ADD_NEW_LANGUAGE;
    this.captions = captions;
    this.languages = languages;
};
goog.inherits(mirosubs.ControlTabPanel.AddNewLanguageEvent, goog.events.Event);