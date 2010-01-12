{% extends "jstesting/base_test.html" %}
{% block testscript %}

var MS_captionManager = null;

/* stub caption listener machinery for testing */

var MS_dispatchedCaptions = [];
function MS_captionListener(event) {
    MS_dispatchedCaptions.push(event.caption);
}

/* a few helper methods to avoid typing too much */

function captionJSON(start_time, end_time, caption_id) {
    return {'start_time' : start_time, 'end_time': end_time, 'caption_id': caption_id};
}
function addCaptions(captions) {
    MS_captionManager.addCaptions(captions);
}
function sendEvents(playheadTime) {
    MS_captionManager.sendEventsForPlayheadTime_(playheadTime);
}

/* the tests */

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
    addCaptions([captionJSON(0.5, 2, 1)]);
    sendEvents(0.4);
    assertEquals(0, MS_dispatchedCaptions.length);
    sendEvents(0.6);
    assertEquals(1, MS_dispatchedCaptions.length);
    assertEquals(1, MS_dispatchedCaptions[0]['caption_id']);
}

function testTwoUpdates() {
    addCaptions([captionJSON(0.5, 2, 1)]);
    sendEvents(0.2);
    sendEvents(0.4);
    assertEquals(0, MS_dispatchedCaptions.length);
    sendEvents(0.6);
    sendEvents(0.8);
    assertEquals(1, MS_dispatchedCaptions.length);
}

function testRewind() {
    addCaptions([captionJSON(0.5, 2, 1)]);
    sendEvents(0.3);
    sendEvents(0.6);
    sendEvents(0.4);
    assertEquals(2, MS_dispatchedCaptions.length);
    assertNull(MS_dispatchedCaptions[1]);
}

function testProgressToNextCaptionAdjacent() {
    addCaptions([captionJSON(0.5, 2, 1), captionJSON(2, 3, 2)]);
    sendEvents(0.3);
    sendEvents(1);
    sendEvents(2.5);
    assertEquals(2, MS_dispatchedCaptions.length);
    assertEquals(1, MS_dispatchedCaptions[0]['caption_id']);
    assertEquals(2, MS_dispatchedCaptions[1]['caption_id']);
}

function testProgressToNextCaptionDisjoint() {
    addCaptions([captionJSON(0.5, 2, 1), captionJSON(2.5, 3, 2)]);
    sendEvents(0.3);
    sendEvents(1);
    sendEvents(2.2);
    sendEvents(2.6);
    sendEvents(3.1);
    assertEquals(4, MS_dispatchedCaptions.length);
    assertEquals(1, MS_dispatchedCaptions[0]['caption_id']);
    assertNull(MS_dispatchedCaptions[1]);
    assertEquals(2, MS_dispatchedCaptions[2]['caption_id']);
    assertNull(MS_dispatchedCaptions[3]);
}

function testInsertCaptionAfter() {
    addCaptions([captionJSON(0.5, 2, 1)]);
    sendEvents(0.3);
    sendEvents(1.3);
    sendEvents(2.1);
    addCaptions([captionJSON(2.2, 3.4, 2)]);
    sendEvents(2.4);
    assertEquals(3, MS_dispatchedCaptions.length);
    assertEquals(2, MS_dispatchedCaptions[2]['caption_id']);
}

function testInsertCaptionBefore() {
    addCaptions([captionJSON(1, 2, 1)]);
    sendEvents(0.5);
    sendEvents(1.5);
    addCaptions([captionJSON(0.2, 0.6, 2)]);
    sendEvents(0.3);
    assertEquals(2, MS_dispatchedCaptions.length);
    assertEquals(2, MS_dispatchedCaptions[1]['caption_id']);
}

function testInsertCaptionUnderCurrentPlayheadTime() {
    addCaptions([captionJSON(0.5, 2, 1)]);
    sendEvents(0.3);
    sendEvents(1.3);
    sendEvents(2.2);
    addCaptions([captionJSON(2.1, 3.4, 2)]);
    sendEvents(2.2);
    assertEquals(3, MS_dispatchedCaptions.length);
    assertEquals(2, MS_dispatchedCaptions[2]['caption_id']);
}

function testAlterCurrentCaptionTime() {
    var addedCaption = captionJSON(0.5, 2, 1);
		addCaptions([addedCaption]);
    sendEvents(0.3);
    sendEvents(1.3);
		addedCaption["end_time"]=3;
    sendEvents(2.2);
		addedCaption["start_time"]=2.5;
    sendEvents(2.3);
    assertEquals(2, MS_dispatchedCaptions.length);
    assertNull(MS_dispatchedCaptions[1]);
}

function testProgressToEnd() {
		addCaptions([captionJSON(0.5, 2, 1), captionJSON(2, 3, 2), captionJSON(3, 4, 3)]);
    sendEvents(0.3);
    sendEvents(1.3);
    sendEvents(2.3);
    sendEvents(3.3);
    sendEvents(4.3);
    assertEquals(4, MS_dispatchedCaptions.length);
    assertNull(MS_dispatchedCaptions[3]);
}

function testProgressToEndTwice() {
		addCaptions([captionJSON(0.5, 2, 1), captionJSON(2, 3, 2), captionJSON(3, 4, 3)]);
    sendEvents(0.3);
    sendEvents(1.3);
    sendEvents(2.3);
    sendEvents(3.3);
    sendEvents(4.3);
    sendEvents(4.5);
    assertEquals(4, MS_dispatchedCaptions.length);
    assertNull(MS_dispatchedCaptions[3]);
}

{% endblock %}
