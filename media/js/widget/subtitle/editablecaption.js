goog.provide('mirosubs.subtitle.EditableCaption');

/**
 * @param {mirosubs.UnitOfWork} unitOfWork UnitOfWork through which changes to 
 *     this caption can be registered.
 * @param {JSONCaption} opt_jsonCaption optional JSON caption on which we're operating.
 *     Provide this parameter iff the caption exists already in the MiroSubs system.
 */
mirosubs.subtitle.EditableCaption = function(unitOfWork, opt_jsonCaption) {
    this.unitOfWork_ = unitOfWork;
    this.jsonCaption = opt_jsonCaption || 
        { 
            'caption_id' : new Date().getTime(),
            'caption_text' : '',
            'start_time' : -1,
            'end_time' : -1
        };
    if (!opt_jsonCaption)
        this.unitOfWork_.registerNew(this);
};

// TODO: get rid of repetition here, if possible.

mirosubs.subtitle.EditableCaption.prototype.setText = function(text) {
    this.unitOfWork_.registerUpdated(this);
    this.jsonCaption['caption_text'] = text;
};
mirosubs.subtitle.EditableCaption.prototype.getText = function() {
    return this.jsonCaption['caption_text'];
};
mirosubs.subtitle.EditableCaption.prototype.setStartTime = function(startTime) {
    this.unitOfWork_.registerUpdated(this);
    this.jsonCaption['start_time'] = startTime;
};
mirosubs.subtitle.EditableCaption.prototype.getStartTime = function() {
    return this.jsonCaption['start_time'];
};
mirosubs.subtitle.EditableCaption.prototype.setEndTime = function(endTime) {
    this.unitOfWork_.registerUpdated(this);
    this.jsonCaption['end_time'] = endTime;
};
mirosubs.subtitle.EditableCaption.prototype.getEndTime = function() {
    return this.jsonCaption['end_time'];
};
mirosubs.subtitle.EditableCaption.prototype.getCaptionID = function() {
    return this.jsonCaption['caption_id'];
};