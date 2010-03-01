goog.provide('mirosubs.translate.TranslationWidget');

/**
 * Subtitle in json format
 */
mirosubs.translate.TranslationWidget = function(subtitle, unitOfWork) {
    goog.ui.Component.call(this);
    this.subtitle_ = subtitle;
    this.unitOfWork_ = unitOfWork;
};
goog.inherits(mirosubs.translate.TranslationWidget, goog.ui.Component);

mirosubs.translate.TranslationWidget.prototype.createDom = function() {
    var $d = goog.bind(this.getDomHelper().createDom, this.getDomHelper());
    this.setElementInternal($d('li', null,
                               $d('div', null, this.subtitle_['caption_text']),
                               this.translateInput_ = 
                               $d('input', {'type':'text'})));
    this.getHandler().listen(this.translateInput_, 
                             goog.events.EventType.BLUR,
                             this.inputLostFocus_);
};

mirosubs.translate.TranslationWidget.prototype.inputLostFocus_ = function(event) {
    if (!this.translation_)
        this.translation_ = 
            new mirosubs.translate
            .EditableTranslation(this.unitOfWork_, this.getCaptionID());
    this.translation_.setText(this.translateInput_.value);
};

/**
 *
 * @param {mirosubs.translate.EditableTranslation} translation
 */
mirosubs.translate.TranslationWidget.prototype.setTranslation = function(translation) {
    this.translation_ = translation;
    this.translateInput_.value = translation ? translation.getText() : '';
};

mirosubs.translate.TranslationWidget.prototype.setEnabled = function(enabled) {
    this.translateInput_.disabled = !enabled;
};

mirosubs.translate.TranslationWidget.prototype.getCaptionID = function() {
    return this.subtitle_['caption_id'];
};