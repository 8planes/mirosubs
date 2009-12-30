goog.provide('mirosubs.CaptionWidget');


mirosubs.CaptionWidget = function(uuid, video_id, username, save_captions_url) {
    this.caption_div = goog.dom.$(uuid + "_captions");
    this.addCaptionLink = goog.dom.$(uuid + "_addCaption");
    this.save_captions_url = save_captions_url;
    goog.events.listen(this.addCaptionLink, 
                       goog.events.EventType.CLICK, 
                       this.addCaptionLinkClicked, 
                       false, this);
};

mirosubs.CaptionWidget.wrap = function(identifier) {
    var uuid = identifier["uuid"];
    var video_id = identifier["video_id"];
    var username = identifier["username"];
    var save_captions_url = identifier["save_captions_url"];
    new mirosubs.CaptionWidget(uuid, video_id, username, save_captions_url);
};

mirosubs.CaptionWidget.prototype.addCaptionLinkClicked = function(e) {
    var dom = goog.dom.getDomHelper(this.caption_div);
    var cd = this.caption_div;
    cd.removeChild(this.addCaptionLink);

    var time_input = dom.createElement("input");
    time_input.type = "text";
    cd.appendChild(time_input);

    var caption_input = dom.createElement("input");
    caption_input.type = "text";
    cd.appendChild(caption_input);

    var ok = dom.createElement("a");
    goog.events.listen(ok,
                       goog.events.EventType.CLICK,
                       function(e) {
                           alert("ok clicked");
                       });

    time_input.focus();
};

mirosubs["CaptionWidget"] = mirosubs.CaptionWidget;
mirosubs.CaptionWidget["wrap"] = mirosubs.CaptionWidget.wrap;

if (typeof(MiroSubsToEmbed) != 'undefined')
    for (var i = 0; i < MiroSubsToEmbed.length; i++)
        mirosubs.CaptionWidget.wrap(MiroSubsToEmbed[i]);
