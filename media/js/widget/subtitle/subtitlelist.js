goog.provide('mirosubs.subtitle.SubtitleList');

/**
 * @param {Array.<mirosubs.subtitle.EditableCaption>} captions
 * @param {?Element} opt_helpElem first element to insert into ul element
 *     that comprises this component.
 */
mirosubs.subtitle.SubtitleList = function(captions, displayTimes, opt_helpElem) {
    goog.ui.Component.call(this);
    this.captions_ = captions;
    this.helpElem_ = opt_helpElem;
    this.displayTimes_ = displayTimes;
    this.currentActiveSubtitle_ = null;
    /**
     * A map of captionID to mirosubs.subtitle.SubtitleWidget
     */
    this.subtitleMap_ = {};
    this.currentlyEditing_ = false;
};
goog.inherits(mirosubs.subtitle.SubtitleList, goog.ui.Component);

mirosubs.subtitle.SubtitleList.prototype.createDom = function() {
    this.setElementInternal(this.getDomHelper()
                            .createDom('ul', {'className':'mirosubs-titlesList'}));
    if (this.helpElem_)
        this.getElement().appendChild(this.helpElem_);
    goog.array.forEach(this.captions_, this.addSubtitle, this);
};

/**
 *
 */
mirosubs.subtitle.SubtitleList.prototype.addSubtitle = 
    function(subtitle, opt_scrollDown) {
    var subtitleWidget = new mirosubs.subtitle
    .SubtitleWidget(subtitle, this.displayTimes_, this);
    this.addChild(subtitleWidget, true);
    this.subtitleMap_[subtitle.getCaptionID() + ''] = subtitleWidget;
    if (typeof(opt_scrollDown) == 'boolean' && opt_scrollDown)
        this.scrollToCaption(subtitle.getCaptionID());
};
mirosubs.subtitle.SubtitleList.prototype.clearActiveWidget = function() {
    if (this.currentActiveSubtitle_ != null) {
        this.currentActiveSubtitle_.setActive(false);
        this.currentActiveSubtitle_ = null;
    }
};
mirosubs.subtitle.SubtitleList.prototype.setActiveWidget = function(captionID) {
    this.scrollToCaption(captionID);
    this.clearActiveWidget();
    var subtitleWidget = this.subtitleMap_[captionID + ''];
    subtitleWidget.setActive(true);
    this.currentActiveSubtitle_ = subtitleWidget;
};
mirosubs.subtitle.SubtitleList.prototype.getActiveWidget = function() {
    return this.currentActiveSubtitle_;
};
mirosubs.subtitle.SubtitleList.prototype.scrollToCaption = function(captionID) {
    var subtitleWidget = this.subtitleMap_[captionID + ''];
    goog.style.scrollIntoContainerView(subtitleWidget.getElement(),
                                       this.getElement(), false);
};
mirosubs.subtitle.SubtitleList.prototype.updateWidget = function(captionID) {
    this.subtitleMap_[captionID + ''].updateValues();
    this.scrollToCaption(captionID);
};
mirosubs.subtitle.SubtitleList.prototype.setCurrentlyEditing = 
    function(subtitleWidget, editing) {
    this.currentlyEditing_ = editing;
};
mirosubs.subtitle.SubtitleList.prototype.isCurrentlyEditing = function() {
    return this.currentlyEditing_;
};