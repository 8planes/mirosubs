{% extends "jstesting/base_test.html" %}
{% block testscript %}

/**
 * @type {mirosubs.subtitle.MSServerModel}
 */
var _serverModel;

function makeEditableCaptionSet() {
    var jsonSubs = [];
    for (var i = 0; i < 100; i++) {
        jsonSubs.push({
            "subtitle_id": "a" + i,
            "text": "text" + i,
            "start_time": i * 2,
            "end_time": i * 2 + 1,
            "sub_order": i + 1
        });
    }
    return new mirosubs.subtitle.EditableCaptionSet(jsonSubs);
}

function successCallback() {
    
}

function failureCallback() {

}

function setUp() {
    mirosubs.Tracker.getInstance().dontReport();
    mirosubs.SubTracker.getInstance().start(false);
    mirosubs.testing.TimerStub.timers = [];
    mirosubs.testing.calls = [];
    goog.Timer = mirosubs.testing.TimerStub;
    mirosubs.Rpc.call = mirosubs.testing.rpcCallStub;
    var editableCaptionSet = makeEditableCaptionSet();
    _serverModel = new mirosubs.subtitle.MSServerModel(
        150,
        2,
        "http://www.youtube.com/watch?v=ArQCkbP07Ao",
        true,
        editableCaptionSet);
    _serverModel.init();
}

function testWorkDone() {
    var captionSet = _serverModel.getCaptionSet();
    assertFalse(_serverModel.anySubtitlingWorkDone());
    var caption = captionSet.caption(2);
    var oldText = caption.getText();
    caption.setText('ccc');
    assertTrue(_serverModel.anySubtitlingWorkDone());
    caption.setText(oldText);
    assertFalse(_serverModel.anySubtitlingWorkDone());
    caption.setText('   ' + oldText + '   ');
    assertFalse(_serverModel.anySubtitlingWorkDone());
}

function testMakeSubsBlank() {
    // if all subs are blank, zero-length subs will be saved.
    var captionSet = _serverModel.getCaptionSet();
    for (var i = 0; i < 100; i++)
        captionSet.caption(i).setText('  ');
    _serverModel.finish(successCallback, failureCallback)
    assertEquals(1, mirosubs.testing.calls.length);
    var call = mirosubs.testing.calls[0];
    assertEquals('finished_subtitles', call.methodName);
    var args = call.args;
    assertEquals(0, args['subtitles'].length);
    assertEquals(undefined, args['new_title']);
    assertEquals(undefined, args['completed']);
}

function testFinishedNoChanges() {
    _serverModel.finish(successCallback, failureCallback);
    assertEquals(0, mirosubs.testing.calls.length);
}

function testFinishedNoChanges2() {
    _serverModel.finish(successCallback, failureCallback, null, true);
    assertEquals(0, mirosubs.testing.calls.length);
}

function testFinishedOnlyChange() {
    _serverModel.finish(successCallback, failureCallback, null, false);
    assertEquals(1, mirosubs.testing.calls.length);
    var call = mirosubs.testing.calls[0];
    var args = call.args;
    assertEquals(undefined, args['subtitles']);
    assertEquals(undefined, args['new_title']);
    assertEquals(false, args['completed']);
}

{% endblock %}