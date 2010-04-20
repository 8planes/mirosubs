{% extends "jstesting/base_test.html" %}
{% block testscript %}

function testFormatTime() {
    assertEquals("12.53", mirosubs.formatTime(12.53));
    assertEquals("1:00.00", mirosubs.formatTime(60));
    assertEquals("1:00.01", mirosubs.formatTime(60.01));
    assertEquals("12:02.00", mirosubs.formatTime(722));
}

{% endblock %}
