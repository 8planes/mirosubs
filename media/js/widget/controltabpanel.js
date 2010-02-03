goog.provide('mirosubs.ControlTabPanel');
goog.provide('mirosubs.ControlTabPanel.EventType');

mirosubs.ControlTabPanel = function(uuid, showTab, videoID) {
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

    // TODO: in future, load languages from server.
    goog.ui.MenuRenderer.CSS_CLASS = 'mirosubs-langmenu';
    goog.ui.MenuItemRenderer.CSS_CLASS = goog.getCssName('mirosubs-langmenuitem');
    var pm = new goog.ui.PopupMenu();
    pm.addItem(new goog.ui.MenuItem('Original', 0));
    pm.addItem(new goog.ui.MenuItem('Add new', 1));
    pm.render(document.body);
    pm.setToggleMode(true);
    pm.attach(this.tabSelectLanguageLink_,
              goog.positioning.Corner.BOTTOM_LEFT,
              goog.positioning.Corner.TOP_LEFT);

    goog.events.listen(this.tabSelectLanguageLink_, 'click',
                       function(event) {
                           event.preventDefault();
                       });
    goog.events.listen(pm, 'action', this.languageSelected_, false, this);
};
goog.inherits(mirosubs.ControlTabPanel, goog.events.EventTarget);

mirosubs.ControlTabPanel.EventType = {
    SUBTITLEME_CLICKED: 'subtitlemeclicked',
    LANGUAGE_SELECTED: 'langselected'
};

mirosubs.ControlTabPanel.prototype.subtitleMeListener_ = function(event) {
    this.dispatchEvent(mirosubs.ControlTabPanel.EventType.SUBTITLEME_CLICKED);
    event.preventDefault();
};

mirosubs.ControlTabPanel.prototype.showLoading = function(loading) {
    this.controlTabLoadingImage_.style.display = loading ? '' : 'none';
};

mirosubs.ControlTabPanel.prototype.showSelectLanguage = function() {
    if (this.subtitleMeLink_)
        this.subtitleMeLink_.style.display = 'none';
    this.tabSelectLanguageLink_.style.display = '';
};

mirosubs.ControlTabPanel.prototype.languageSelected_ = function(event) {
    if (event.target.getModel() == 0) {
        var that = this;
        this.showLoading(true);
        mirosubs.Rpc.call('fetch_captions', { 'video_id' : this.videoID_ },
                          function(captions) {
                              // TODO: in future, look up the language.
                              goog.dom.setTextContent(that.tabSelectLanguageLink_, 
                                                      'Original');
                              that.showLoading(false);
                              that.dispatchEvent(new mirosubs.ControlTabPanel
                                                 .LanguageSelectedEvent(0, captions)); 
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

mirosubs.ControlTabPanel.LanguageSelectedEvent = function(languageID, captions) {
    this.type = mirosubs.ControlTabPanel.EventType.LANGUAGE_SELECTED;
    this.languageID = languageID;
    this.captions = captions;
};
goog.inherits(mirosubs.ControlTabPanel.LanguageSelectedEvent, goog.events.Event);
