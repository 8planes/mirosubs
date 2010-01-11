{% extends "jstesting/base_test.html" %}
{% block testscript %}

var MS_dispatchedCaptions = [];
var MS_captionManager = null;

function MS_captionListener(event) {
    MS_dispatchedCaptions.push(event.caption);
}

function setUp() {
    MS_dispatchedCaptions = [];
    MS_captionManager = new mirosubs.CaptionManager(null);
    MS_captionManager.addEventListener(mirosubs.CaptionManager.CAPTION_EVENT,
                                       MS_captionListener);
    // clear window timer so we can imitate stub timer in tests
    window.clearInterval(MS_captionManager.timerInterval_);
}

function tearDown() {
    MS_captionManager.dispose();
}

function testOneCaption() {
    MS_captionManager.addCaptions([{'start_time' : 0.5, 'end_time' : 2, 
                    'caption_id' : 1}]);
    MS_captionManager.sendEventsForPlayheadTime_(0.4);
    assertEquals(0, MS_dispatchedCaptions.length);
    MS_captionManager.sendEventsForPlayheadTime_(0.6);
    assertEquals(1, MS_dispatchedCaptions.length);
    assertEquals(1, MS_dispatchedCaptions[0]['caption_id']);
}



{% endblock %}