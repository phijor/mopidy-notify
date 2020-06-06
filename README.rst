****************************
Mopidy-Notify
****************************

.. image:: https://img.shields.io/pypi/v/Mopidy-Notify
    :target: https://pypi.org/project/Mopidy-Notify/
    :alt: Latest PyPI version

.. image:: https://img.shields.io/circleci/build/gh/phijor/mopidy-notify
    :target: https://circleci.com/gh/phijor/mopidy-notify
    :alt: CircleCI build status

.. image:: https://img.shields.io/codecov/c/gh/phijor/mopidy-notify
    :target: https://codecov.io/gh/phijor/mopidy-notify
    :alt: Test coverage

Mopidy extension for showing desktop notifications


Installation
============

Install by running::

    python3 -m pip install Mopidy-Notify

See https://mopidy.com/ext/notify/ for alternative installation methods.


Configuration
=============

Before starting Mopidy, you must add configuration for
Mopidy-Notify to your Mopidy configuration file::

    [notify]
    enabled = true

The following configuration values are available:

:literal:`notify/max_icon_size`:
    Maximum icon dimensions (width/heigh) in pixels for which track images/album covers are fetched.
    For some tracks, images in multiple dimensions are available.
    Mopidy-Notify will try to use the largest image possible for a notification.
    Since some backends provide huge track images (as large as 3000x3000 pixels for Bandcamp MP3s), use this value to restrict which images are considered for display.
    If no track images are smaller than :literal:`max_icon_size`, the smallest image available will be used.

:literal:`notify/fallback_icon`:
    File path to an icon or the name of a default icon used as fallback if no track image/album cover is available for the currently playing track.

The following values are set by default:

.. include:: mopidy_notify/ext.conf


Project resources
=================

- `Source code <https://github.com/phijor/mopidy-notify>`_
- `Issue tracker <https://github.com/phijor/mopidy-notify/issues>`_
- `Changelog <https://github.com/phijor/mopidy-notify/blob/master/CHANGELOG.rst>`_


Credits
=======

- Original author: `Philipp Joram <https://github.com/phijor>`__
- Current maintainer: `Philipp Joram <https://github.com/phijor>`__
- `Contributors <https://github.com/phijor/mopidy-notify/graphs/contributors>`_
