goog.provide('mirosubs.translate.EditableTranslation');

mirosubs.translate.EditableTranslation = function(unitOfWork, captionID, 
                                                  opt_jsonTranslation) {
    this.unitOfWork_ = unitOfWork;
    this.captionID_ = captionID;
    this.jsonTranslation = opt_jsonTranslation || 
        {
            'caption_id': captionID,
            'text': ''
        };
    if (!opt_jsonTranslation)
        this.unitOfWork_.registerNew(this);
};

mirosubs.translate.EditableTranslation.prototype.setText = function(text) {
    this.jsonTranslation['text'] = text;
    this.unitOfWork_.registerUpdated(this);
};

mirosubs.translate.EditableTranslation.prototype.getText = function() {
    return this.jsonTranslation['text'];
};

mirosubs.translate.EditableTranslation.prototype.getCaptionID = function() {
    return this.jsonTranslation['caption_id'];
};