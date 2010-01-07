goog.provide('mirosubs.CaptionManager');

/**
 * Constructor.
 *
 * @param {Function} playheadFn Optional function that returns the current 
 *     playhead time of the video, in seconds.
 */
mirosubs.CaptionManager = function(playheadFn) {
    console.log(playheadFn);
    goog.events.EventTarget.call(this);
    this.captions_ = [];
    this.captionCompare_ = function(a, b) {
        return a['start_time'] > b['start_time'] ? 
            1 : a['start_time'] < b['start_time'] ? -1 : 0;
    };
    this.playheadFn_ = playheadFn;
    var that = this;
    this.timerInterval_ = window.setInterval(function() { that.timerTick_(); }, 100);
    this.currentCaption_ = null;
    this.nextCaption_ = null;
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
    this.timerTick_();
};

mirosubs.CaptionManager.prototype.timerTick_ = function() {
    if (this.playheadFn_ == null)
        return;
    var playheadTime = (this.playheadFn_)();
    if (this.currentCaption_ != null && 
        playheadTime >= this.currentCaption_['start_time'] && 
        playheadTime <= this.currentCaption_['end_time'])
        return;
    // TODO: perhaps keep track of more state in future (e.g. next caption)
    // to eliminate some binary searches. For now, keeping it simple at the 
    // expense of performance.
    if (this.captions_.length > 0) {
        var lastCaptionIndex = 
            goog.array.binarySearch(this.captions_, 
                                    { 'start_time' : playheadTime },
                                    this.captionCompare_);
        if (lastCaptionIndex < 0)
            lastCaptionIndex = -lastCaptionIndex - 2;
        if (lastCaptionIndex >= 0 && 
            playheadTime >= this.captions_[lastCaptionIndex]['start_time'] &&
            playheadTime <= this.captions_[lastCaptionIndex]['end_time']) {
            this.currentCaption_ = this.captions_[lastCaptionIndex];
            this.dispatchCaptionEvent_(this.currentCaption_);
        }
        else {
            this.currentCaption_ = null;
            this.dispatchCaptionEvent_(this.currentCaption_);
        }
    }
};

mirosubs.CaptionManager.prototype.dispatchCaptionEvent_ = function(caption) {
    var event = new goog.events.Event(mirosubs.CaptionManager.CAPTION_EVENT, this);
    event.caption = caption;
    this.dispatchEvent(event);
};

mirosubs.CaptionManager.prototype.disposeInternal = function() {
    mirosubs.CaptionManager.superClass_.disposeInternal.call(this);
    goog.events.removeAll(this);
    /**
     * Stop the timer.
     */
    window.clearInterval(this.timerInterval_);
};