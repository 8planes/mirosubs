goog.provide('mirosubs.CaptionMenu');

mirosubs.CaptionMenu = function(videoID) {
    goog.ui.Component.call(this);
    
};
goog.inherits(mirosubs.CaptionMenu, goog.ui.Component);
mirosubs.CaptionMenu.prototype.createDom = function() {
    this.decorateInternal(this.dom_.createDom('div'));
};
mirosubs.CaptionMenu.prototype.decorateInternal = function(element) {
    mirosubs.CaptionMenu.superClass_.decorateInternal.call(this, element);
    // TODO: in future, grab available languages from server here.
    var editTrans = this.dom_.createDom('div');
    var editTransA = this.dom_.createDom('a', {'href': '#'},
                                         'Add new language');
    editTrans.appendChild(editTransA);
    this.getElement().appendChild(editTrans);
    var origLang = this.dom_.createDom('div');
    var origLangA = this.dom_.createDom('a', {'href': '#'}, 
                                        'Original Language');
    origLang.appendChild(origLangA);
    this.getElement().appendChild(origLang);
    var that = this;
    goog.events.listenOnce(origLangA, 'click', 
                           function(event) {
                               event.preventDefault();
                               that.origLangClicked_();
                           });
};
mirosubs.CaptionMenu.prototype.origLangClicked_ = function() {
    this.dispatchEvent(mirosubs.CaptionMenu.SELECTION_EVENT);
};
mirosubs.CaptionMenu.SELECTION_EVENT = "captionsselected";