{% extends "jstesting/base_test.html" %}
{% block testscript %}

var MS_model = null;

function makeBaseModel(opt_initialLanguage) {
    return new mirosubs.startdialog.Model(
        opt_initialLanguage || null, {
            'my_languages': ['en', 'fr'],
            'original_language': 'en',
            'video_languages': [
                { 'language': 'en', 'dependent': false, 'is_complete': true },
                { 'language': 'fr', 'dependent': false, 'is_complete': false }
            ]
        });
}

function test0() {
    var model = makeBaseModel();

    assertFalse(model.originalLanguageShown());
    languages = model.toLanguages();
    assertEquals('fr', languages[0].language);
    assertEquals('en', languages[1].language);
    assertEquals('fr', model.defaultToLanguage().language);
    assertEquals(0, model.fromLanguages().length);

    model.selectLanguage(languages[1]);
    assertEquals(0, model.fromLanguages().length);
}

{% endblock %}