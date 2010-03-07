{% extends "jstesting/base_test.html" %}
{% block testscript %}

var MS_syncPanel = null;
var MS_unitOfWork = null;
var MS_editableCaptions = [];
var MS_videoPlayer = null;
var MS_captionManager = null;

// helper methods to avoid typing too much

function makeEditableCaption(unitOfWork, start, end, id) {
    var jsonCaption = {'start_time' : start, 
                       'end_time': end, 
                       'caption_id': id};
    return new mirosubs.subtitle.EditableCaption(unitOfWork, jsonCaption);
}

function setUp() {
    MS_unitOfWork = new mirosubs.UnitOfWork();
    MS_videoPlayer = new mirosubs.testing.StubVideoPlayer();
    MS_editableCaptions = 
        [makeEditableCaption(MS_unitOfWork, 0, 1, 0),
         makeEditableCaption(MS_unitOfWork, 1, 2, 1),
         makeEditableCaption(MS_unitOfWork, 2, 3, 2)];
    MS_captionManager = new mirosubs.CaptionManager(MS_videoPlayer.getPlayheadFn());
    MS_syncPanel = new mirosubs.subtitle.SyncPanel(MS_editableCaptions, 
                                                   MS_videoPlayer,
                                                   MS_captionManager);
}



function tearDown() {
    MS_unitOfWork.dispose();
    MS_captionManager.dispose();
}

{% endblock %}