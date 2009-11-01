goog.provide('mirosubs.CaptionManager');

/**
 * Constructor.
 *
 * @param {Function} playheadFn Optional function that returns the current 
 *     playhead time of the video, in seconds.
 */
mirosubs.CaptionManager = function(playheadFn) {
    goog.events.EventTarget.call(this);
    this.captions_ = [];
    this.captionCompare_ = function(a, b) {
        return a['start_time'] > b['start_time'] ? 
            1 : a['start_time'] < b['start_time'] ? -1 : 0;
    };
    this.playheadFn_ = playheadFn;
    var that = this;
    this.timerInterval_ = window.setInterval(function() { that.timerTick_(); }, 100);
    this.currentCaptionIndex_ = -1;
    this.lastCaptionDispatched_ = null;
};
goog.inherits(mirosubs.CaptionManager, goog.events.EventTarget);

mirosubs.CaptionManager.CAPTION_EVENT = 'caption';

/**
 * Adds captions to be displayed.
 * @param {Array} captions Array of captions. Each caption must be an 
 *     object with a 'start_time' property set to the start time for 
 *     that caption and an 'end_time' property set to the end time.
 */
mirosubs.CaptionManager.prototype.addCaptions = function(captions) {
    // TODO: perhaps use a more efficient implementation in the future, if 
    // that is appealing. For example, sort-merge.
    var i;
    for (i = 0; i < captions.length; i++)
        this.captions_.push(captions[i]);
    goog.array.sort(this.captions_, this.captionCompare_);
    this.currentCaptionIndex_ = -1;
    this.timerTick_();
};

mirosubs.CaptionManager.prototype.timerTick_ = function() {
    if (this.playheadFn_ != null)
        this.sendEventsForPlayheadTime_(this.playheadFn_());
};

mirosubs.CaptionManager.prototype.sendEventsForPlayheadTime_ = function(playheadTime) {
    if (this.captions_.length == 0)
        return;
    if (this.currentCaptionIndex_ == -1 && 
        playheadTime < this.captions_[0]['start_time'])
        return;
    var curCaption = this.currentCaptionIndex_ > -1 ? 
        this.captions_[this.currentCaptionIndex_] : null;
    if (this.currentCaptionIndex_ > -1 && 
        playheadTime >= curCaption['start_time'] && 
        playheadTime < curCaption['end_time'])
        return;
    var nextCaption = this.currentCaptionIndex_ < this.captions_.length - 1 ? 
        this.captions_[this.currentCaptionIndex_ + 1] : null;
    if (nextCaption != null && 
        playheadTime >= nextCaption['start_time'] &&
        playheadTime < nextCaption['end_time']) {
        this.currentCaptionIndex_++;
        this.dispatchCaptionEvent_(nextCaption);
        return;
    }
    if ((nextCaption == null || playheadTime < nextCaption['start_time']) &&
        playheadTime >= curCaption['start_time']) {
        this.dispatchCaptionEvent_(null);
        return;
    }
    this.sendEventForRandomPlayheadTime_(playheadTime);
};

mirosubs.CaptionManager.prototype.sendEventForRandomPlayheadTime_ = function(playheadTime) {
    var lastCaptionIndex = goog.array.binarySearch(this.captions_, 
        { 'start_time' : playheadTime }, this.captionCompare_);
    if (lastCaptionIndex < 0)
        lastCaptionIndex = -lastCaptionIndex - 2;
    this.currentCaptionIndex_ = lastCaptionIndex;
    if (lastCaptionIndex >= 0 && 
        playheadTime >= this.captions_[lastCaptionIndex]['start_time'] &&
        playheadTime <= this.captions_[lastCaptionIndex]['end_time']) {
        this.dispatchCaptionEvent_(this.captions_[lastCaptionIndex]);
    }
    else {        
        this.dispatchCaptionEvent_(null);
    }
};

mirosubs.CaptionManager.prototype.dispatchCaptionEvent_ = function(caption) {
    if (caption == this.lastCaptionDispatched_)
        return;
    this.lastCaptionDispatched_ = caption;
    var event = new goog.events.Event(mirosubs.CaptionManager.CAPTION_EVENT, this);
    event.caption = caption;
    this.dispatchEvent(event);
};

mirosubs.CaptionManager.prototype.dispose = function() {
    mirosubs.CaptionManager.superClass_.disposeInternal.call(this);
    goog.events.removeAll(this);
    /**
     * Stop the timer.
     */
    window.clearInterval(this.timerInterval_);
};