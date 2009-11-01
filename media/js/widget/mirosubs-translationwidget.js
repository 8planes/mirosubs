goog.provide('mirosubs.trans.TranslationWidget');

/**
 *
 * @param {Array.<mirosubs.trans.EditableCaption>} captions The captions for the 
 *     video, so far.
 *
 */
mirosubs.trans.TranslationWidget = function(captions, captionManager, opt_domHelper) {
    goog.ui.Component.call(this, opt_domHelper);
    this.captions_ = captions;
    this.captionManager_ = captionManager;
    this.captionManager_.addEventListener(mirosubs.CaptionManager.CAPTION_EVENT,
                                          this.captionReached_,
                                          false, this);
};
goog.inherits(mirosubs.trans.TranslationWidget, goog.ui.Component);
mirosubs.trans.TranslationWidget.prototype.createDom = function() {
    this.decorateInternal(this.getDomHelper().createElement('div'));
};
mirosubs.trans.TranslationWidget.prototype.decorateInternal = function(element) {
    
};
mirosubs.trans.TranslationWidget.prototype.captionReached = function(jsonCaptionEvent) {
    var jsonCaption = jsonCaptionEvent.caption;
    // TODO: do we actually want to do anything here? Maybe not...
};
mirosubs.trans.TranslationWidget.prototype.disposeInternal = function() {
    this.captionManager_.removeEventListener(mirosubs.CaptionManager.CAPTION_EVENT,
                                             this.captionReached_,
                                             false, this);
};