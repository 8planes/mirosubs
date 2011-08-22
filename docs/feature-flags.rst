==============
Feature flags
==============

In order to make working with features that take longer to develop than our release schedule, we have feature flags on the source code, that enable features with a setting.

At present time, the system is very simple, but it can be extended to make it more configurable  and even have an admin like interface as in http://blog.disqus.com/post/789540337/partial-deployment-with-feature-switches.

Our app that controls that is called 'doorman'.


Creating feature flags
======================

Add a flag name to the settings.FEATURE_FLAGS dict, for example::

    FEATURE_FLAGS  = {
        "MODERATION": False
    }

This means that the featured identified by 'MODERATION' is turned off.
The setting can either be a boolean, or a callable that takes a request as a parameter and returns a boolean.

In templates
============

You can use the switch_feature as a if tag in django templated::

    {% load doorman %}
    {% switch_feature MODERATION request %}
        // whatever if moderation is on, including django template tags
    {% endswitch_feature %}

In python code
==============

In regular python code::

    from doorman import feature_is_on

    if feature_is_on('MODERATION', request):
       // do something here



.. automodule:: doorman
    :members:
