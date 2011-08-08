{% extends "jstesting/base_test.html" %}
{% block testscript %}


/* a few helper methods to avoid typing too much */

function captionJSON(startTime, endTime, captionID, subOrder, text) {
    return {'start_time' : startTime,
	    'end_time': endTime,
	    'subtitle_id': captionID,
            'sub_order': subOrder, 
            'text': text };
}

/* the tests */

function setUp() {
    mirosubs.Tracker.getInstance().dontReport();
}

function testSrt() {
    var subs = [captionJSON(0.0, 5.0, 'a', 1, 'sub a'), 
                captionJSON(5.1, -1, 'b', 2, 'sub b'),
                captionJSON(-1, -1, 'c', 3, 'sub c')];
    var srtFile = mirosubs.SRTWriter.toSRT(subs);
    assertEquals(
        "1\n00:00:00,000 --> 00:00:05,000\nsub a\n\n2\n00:00:05,100 --> 99:59:59,000\nsub b\n\n3\n99:59:59,000 --> 99:59:59,000\nsub c",
        goog.string.trimRight(srtFile));
}

{% endblock %}
