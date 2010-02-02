goog.provide('mirosubs.ControlTabPanel');
goog.provide('mirosubs.ControlTabPanel.EventType');

mirosubs.ControlTabPanel = function(uuid, showTab) {
    goog.events.EventTarget.call(this);
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
    goog.events.listen(this.tabSelectLanguageLink_, 'click',
                       this.languageSelectedListener_, false, this);
};
goog.inherits(mirosubs.ControlTabPanel, goog.events.EventTarget);

mirosubs.ControlTabPanel.EventType = {
    SUBTITLEME_CLICKED : 'subtitlemeclicked',
    SELECT_LANGUAGE_CLICKED : 'selectlanguageclicked'
};

mirosubs.ControlTabPanel.prototype.subtitleMeListener_ = function(event) {
    this.dispatchEvent(mirosubs.ControlTabPanel.EventType.SUBTITLEME_CLICKED);
    event.preventDefault();
};

mirosubs.ControlTabPanel.prototype.languageSelectedListener_ = function(event) {
    this.dispatchEvent(mirosubs.ControlTabPanel.EventType.SELECT_LANGUAGE_CLICKED);    
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

mirosubs.ControlTabPanel.prototype.setVisible = function(visible) {
    this.controlTabDiv_.style.display = visible ? '' : 'none';
};

mirosubs.ControlTabPanel.prototype.disposeInternal = function() {
    mirosubs.ControlTabPanel.superClass_.disposeInternal.call(this);
    if (this.subtitleMeLink_)
        goog.events.unlisten(this.subtitleMeLink_, 'click', 
                             this.subtitleMeListener_, false, this);
    goog.events.unlisten(this.tabSelectLanguageLink_, 'click',
                         this.languageSelectedListener_, false, this);
};