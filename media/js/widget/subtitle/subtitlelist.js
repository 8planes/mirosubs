goog.provide('mirosubs.subtitle.SubtitleList');

/**
 * @param {Array.<mirosubs.subtitle.EditableCaption>} captions
 * @param {?Element} opt_helpElem first element to insert into ul element
 *     that comprises this component.
 */
mirosubs.subtitle.SubtitleList = function(captions, opt_helpElem) {
    goog.ui.Component.call(this);
    this.captions_ = captions;
    this.helpElem_ = opt_helpElem;
};
goog.inherits(mirosubs.subtitle.SubtitleList, goog.ui.Component);

mirosubs.subtitle.SubtitleList.prototype.createDom = function() {
    this.setElementInternal(this.getDomHelper()
                            .createDom('ul', {'className':'MiroSubs-titlesList'}));
    if (this.helpElem_)
        this.getElement().appendChild(this.helpElem_);
    goog.array.forEach(this.captions_, this.addSubtitle, this);
};


/**
 *
 * @param {mirosubs.subtitle.EditableCaption} subtitle
 */
mirosubs.subtitle.SubtitleList.prototype.addSubtitle = function(subtitle) {
    this.addChild(new mirosubs.subtitle.Subtitle(subtitle), true);
};

mirosubs.subtitle.Subtitle = function(subtitle) {
    goog.ui.Component.call(this);
    this.subtitle_ = subtitle;
    this.keyHandler_ = null;
};
goog.inherits(mirosubs.subtitle.Subtitle, goog.ui.Component);
mirosubs.subtitle.Subtitle.prototype.createDom = function() {
    var $d = goog.bind(this.getDomHelper().createDom, this.getDomHelper());
    this.setElementInternal($d('li', null,
                               this.timestampElem_ = 
                               $d('span', {'className':'mirosubs-timestamp'}),
                               this.titleElem_ = 
                               $d('span', {'className':'mirosubs-title'},
                                  this.titleElemInner_ = 
                                  $d('span'))));
    this.textareaElem_ = null;
    this.keyHandler_ = null;
    this.setValues_();
};
mirosubs.subtitle.Subtitle.prototype.enterDocument = function() {
    this.addDoubleClickListener_();    
};
mirosubs.subtitle.Subtitle.prototype.setActive = function(active) {
    var c = goog.dom.classes;
    if (active)
        this.getElement().add('active');
    else
        this.getElement().remove('active');
};

mirosubs.subtitle.Subtitle.prototype.addDoubleClickListener_ = function() {
    this.getHandler().listenOnce(this.titleElemInner_,
                                 goog.events.EventType.DBLCLICK,
                                 this.titleDoubleClicked_, false, this);
};

mirosubs.subtitle.Subtitle.prototype.titleDoubleClicked_ = function(event) {
    goog.dom.removeNode(this.titleElemInner_);
    this.textareaElem_ = this.getDomHelper().createElement('textarea');
    this.titleElem_.appendChild(this.textareaElem_);
    this.textareaElem_.value = this.subtitle_.getText();
    this.disposeKeyHandler();
    this.keyHandler_ = new goog.events.KeyHandler(this.textareaElem_);
    this.getHandler().listen(this.keyHandler_,
                             goog.events.KeyHandler.EventType.KEY,
                             this.handleKey_, false, this);
    event.stopPropagation();
    event.preventDefault();
};
mirosubs.subtitle.Subtitle.prototype.handleKey_ = function(event) {
    if (event.keyCode == goog.events.KeyCodes.ENTER) {
        this.getHandler().unlisten(this.keyHandler_);
        this.subtitle_.setText(this.textareaElem_.value);
        goog.dom.removeNode(this.textareaElem_);
        this.titleElem_.appendChild(this.titleElemInner_);
        this.setValues_();
        this.addDoubleClickListener_();
        event.stopPropagation();
        event.preventDefault();
    }
};
mirosubs.subtitle.Subtitle.prototype.setValues_ = function() {
    var $t = goog.dom.setTextContent;
    var time = this.subtitle_.getStartTime();
    if (time == -1)
        $t(this.timestampElem_, " ");
    else
        $t(this.timestampElem_, this.formatTime_(time));
    $t(this.titleElemInner_, this.subtitle_.getText());    
};
mirosubs.subtitle.Subtitle.prototype.formatTime_ = function(time) {
    var pad = function(number) {
        return (number < 10 ? "0" : "") + number;
    };

    var hours = time / 3600;
    var minutes = (time / 60) % 60;
    var seconds = Math.floor(time) % 60;
    var frac = (time - Math.floor(time)) * 100;

    return [[pad(hours), pad(minutes), pad(seconds)].join(':'),
            pad(frac)].join('.');        
};
mirosubs.subtitle.Subtitle.prototype.disposeKeyHandler = function() {
    if (this.keyHandler_) {
        this.getHandler().removeAll(this.keyHandler_);
        this.keyHandler_.dispose();
        this.keyHandler_ = null;
    }
};
mirosubs.subtitle.Subtitle.prototype.disposeInternal = function() {
    mirosubs.subtitle.Subtitle.superClass_.disposeInternal.call(this);
    this.disposeKeyHandler();
};