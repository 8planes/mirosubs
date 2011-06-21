{% extends "jstesting/base_test.html" %}
{% block testscript %}


/* a few helper methods to avoid typing too much */

function captionJSON(startTime, endTime, captionID, subOrder) {
    return {'start_time' : startTime,
	    'end_time': endTime,
	    'subtitle_id': captionID,
            'sub_order': subOrder};
}

function timesToString(startTime){
    var buffer = new goog.string.StringBuffer();
    mirosubs.SRTWriter.writeSrtTime_(
        startTime, buffer);
    return buffer.toString();

}
/* the tests */

function setUp() {
    mirosubs.Tracker.getInstance().dontReport();
    mirosubs.SubTracker.getInstance().start(false);
}


function testHourWiter(){
    assertEquals("00:00:20,000", timesToString(20));
    assertEquals("99:59:59,000", timesToString(
        mirosubs.subtitle.EditableCaption.TIME_UNDEFINED_SERVER));
}

{% endblock %}
