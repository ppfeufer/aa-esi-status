# Change Log

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog] and this project adheres to [Semantic Versioning].

<!--
GitHub MD Syntax:
https://docs.github.com/en/get-started/writing-on-github/getting-started-with-writing-and-formatting-on-github/basic-writing-and-formatting-syntax

Highlighting:
https://docs.github.com/assets/cb-41128/mw-1440/images/help/writing/alerts-rendered.webp

> [!NOTE]
> Highlights information that users should take into account, even when skimming.

> [!IMPORTANT]
> Crucial information necessary for users to succeed.

> [!WARNING]
> Critical content demanding immediate user attention due to potential risks.
-->

## [In Development] - Unreleased

<!--
Section Order:

### Added
### Fixed
### Changed
### Deprecated
### Removed
### Security
-->

<!-- Your changes go here -->

### Added

- Panel for routes with unknown status

## [3.0.1] - 2025-11-21

### Fixed

- Uncaught exception when ESI status data is missing in the database

### Changed

- Translations updated

### Removed

- Window active check in dashboard widget auto-update, its not needed anymore since
  we run the updates in the background via a Celery task now

## [3.0.0] - 2025-11-21

### Changed

- Track the status of the new OpenAPI routes now, instead of the old Swagger endpoints
- Translations updated

### Update Information

Add the following scheduled task to your AA settings (`local.py` or `conf/local.py` for
Docker installations)

```python
# AA ESI Status - https://github.com/ppfeufer/aa-esi-status
CELERYBEAT_SCHEDULE["ESI Status :: Update"] = {
    "task": "esistatus.tasks.update_esi_status",
    "schedule": 60,
}
```

## [2.9.3] - 2025-11-04

### Fixed

- Django `makemessages` doesn't seem to recognize f-strings anymore

### Changed

- Translations updated

## [2.9.2] - 2025-10-07

### Changed

- Switch to Terser for JavaScript compression
- Translations updated

## [2.9.1] - 2025-08-14

### Fixed

- SVG sprite

## [2.9.0] - 2025-08-14

### Changed

- Use the AA framework SVG spinner for the loading animation
- Use the AA framework JS functions
- Minimum requirements
  - Alliance Auth >= 4.9.0
- Translations updated

## [2.8.4] - 2025-08-04

### Changed

- Translations updated

## [2.8.3] - 2025-07-23

### Changed

- Use an SVG sprite for the SVG icons where ever possible

## [2.8.2] - 2025-07-23

### Added

- ESI logo to dashboard widget header

## [2.8.1] - 2025-07-22

### Changed

- Using the official ESI logo in the page header
- Loading spinner animation improved
- Endpoints alphabetically sorted

## [2.8.0] - 2025-07-21

### Added

- Internal URL prefix

### Changed

- Use an Ajax call to load the ESI status instead of loading it directly in the template

## [2.7.0] - 2025-07-08

### Changed

- Code refactored and improved

## [2.6.0] - 2025-05-27

### Added

- Docker instructions to README

### Removed

- Cache breaker for static files. Doesn't work as expected with `django-sri`.
- Redundant header on public views

## [2.5.4] - 2025-05-05

### Changed

- Template code slightly refactored/improved for better readability
- Translations updated

## [2.5.3] - 2025-04-23

### Changed

- JavaScript code improved
- Use Bootstraps `text-bg-*` classes for the status colors to leverage Bootstraps
  native background/text contrast handling

## [2.5.2] - 2025-03-24

### Added

- Error message from the server response when the ESI status couldn't be loaded

### Changed

- Use AA framework page header template
- Test coverage improved
- Translations updated

## [2.5.1] - 2025-03-06

### Changed

- Templatetag code improved
- Translations updated

## [2.5.0] - 2025-01-24

### Added

- SRI hash calculation for static files

### Changed

- Set user agent according to MDN guidelines
- Translations updated
- Minimum requirements:
  - Alliance Auth>=4.6.0

## [2.4.3] - 2024-12-14

### Added

- Python 3.13 to the test matrix

### Changed

- Translations updated

## [2.4.2] - 2024-11-01

### Changed

- Italian translation improved

## [2.4.1] - 2024-09-19

### Fixed

- A typo in the red endpoint explanation

## [2.4.0] - 2024-09-16

### Changed

- Dependencies updated
  - `allianceauth`>=4.3.1
- Japanese translation improved
- Lingua codes updated to match Alliance Auth

## [2.3.0] - 2024-07-15

### Added

- Czech translation prepared for when AA supports it

### Fixed

- Dashboard widget Bootstrap classes

### Changed

- French translation updated
- Russian translation updated

### Removed

- Support for Python 3.8 and Python 3.9

## [2.2.1] - 2024-06-03

### Change

- German translation updated

## [2.2.0] - 2024-05-27

### Added

- Tooltips with explanation for the endpoint level

### Changed

- The minimum required AA version is now 4.1.0
- Using the AA framework template for the widget title

## [2.1.1] - 2024-05-16

### Changed

- Translations updated

## [2.1.0] - 2024-03-17

### Changed

- Dashboard widget will be auto-updated every 60 seconds when the browser tab is active

## [2.0.0] - 2024-03-16

> [!NOTE]
>
> **This version needs at least Alliance Auth v4.0.0!**
>
> Please make sure to update your Alliance Auth instance before
> you install this version, otherwise, an update to Alliance Auth will
> be pulled in unsupervised.

### Added

- Compatibility to Alliance Auth v4
  - Bootstrap 5
  - Django 4.2
- Dashboard widget for administrative users

### Removed

- Compatibility to Alliance Auth v3

## [2.0.0-beta.2] - 2024-03-08

> [!NOTE]
>
> **This version needs at least Alliance Auth v4.0.0b2!**
>
> Please make sure to update your Alliance Auth instance before
> you install this version, otherwise, an update to Alliance Auth will
> be pulled in unsupervised.

### Added

- Dashboard widget for administrative users

## [2.0.0-beta.1] - 2024-02-18

> [!NOTE]
>
> **This version needs at least Alliance Auth v4.0.0b1!**
>
> Please make sure to update your Alliance Auth instance before
> you install this version, otherwise, an update to Alliance Auth will
> be pulled in unsupervised.

### Added

- Compatibility to Alliance Auth v4
  - Bootstrap 5
  - Django 4.2

### Removed

- Compatibility to Alliance Auth v3

## [1.14.2] - 2023-09-26

> [!NOTE]
>
> **This is the last version compatible with Alliance Auth v3.**

### Added

- Last missing strings to translations

### Changed

- Translation updated and improved
- Test suite updated

## [1.14.1] - 2023-09-02

### Changed

- Korean translation improved

## [1.14.0] - 2023-08-29

### Added

- Korean translation

### Changed

- Code improvements

## [1.13.0] - 2023-08-15

### Added

- Spanish translation

## [1.12.1] - 2023-08-11

### Fixed

- Bootstrap CSS fix

## [1.12.0] - 2023-08-11

> **Warning**
>
> The update makes use of a feature introduced in Allianceauth v3.6.1, meaning this
> update will pull in Allianceauth v3.6.1 unsupervised. Please make sure to update
> Allianceauth to this version beforehand to avoid any complications.

### Added

- Support public views (see [README])

## [1.11.1] - 2023-07-30

### Added

- Bootstrap CSS fix
- Footer to promote help with the app translation

### Changed

- try/except improved in `views.index`

## [1.11.0] - 2023-06-24

### Added

- Ukrainian translation

## [1.10.0] - 2023-04-25

### Changed

- Moved the build process to PEP 621 / pyproject.toml
- Russian translation updated

## [1.9.0] - 2023-04-16

### Added

- Russian translation

## [1.8.0] - 2023-04-13

### Added

- German translation

## [1.7.2] - 2022-09-18

### Change

- Internal code changes/improvements
- Minimum dependencies:
  - Alliance Auth>=3.0.0

## [1.7.1] - 2022-08-27

### Fixed

- Module 'requests.exceptions' has no attribute 'RequestsJSONDecodeError'

### Changed

- General code improvements

## [1.7.0] - 2022-08-02

### Changed

- Templates cleaned up
- Data handling
- Number formatting to f-strings
- Minimum dependencies:
  - Python>=3.8
  - Alliance Auth>=2.15.1

### Removed

- tox tests for AA beta version

## [1.6.0] - 2022-06-24

### Added

- Versioned static template tag

## [1.5.2] - 2022-05-02

### Fixed

- Category with names containing a space couldn't be opened (e.g., Faction Warfare)

### Changed

- Templates unified

## [1.5.1] - 2022-03-02

### Fixed

- Include the right app ...

## [1.5.0] - 2022-03-02

### Added

- Test suite for AA 3.x and Django 4

### Removed

- Deprecated settings

### Changed

- Switched to `setup.cfg` as config file, since `setup.py` is deprecated now

## [1.4.0] - 2022-02-28

### Fixed

- [Compatibility] AA 3.x / Django 4 :: ImportError: cannot import name
  'ugettext_lazy' from 'django.utils.translation'

## [1.3.0] - 2022-01-02

### Added

- Tests for Python 3.11 (still allowed failing, since Python 3.11 is still in alpha
  state)

### Changed

- Minimum requirements
  - Alliance Auth v2.9.4

### Removed

- Check for AA-GDPR, since we don't load any external resources it is not needed
- No longer needed function and file

## [1.2.0] - 2021-11-30

### Changed

- Minimum requirements
  - Python 3.7
  - Alliance Auth v2.9.3

## [1.1.0] - 2021-11-24

### Added

- Error handling on connection problems to ESI status URL
- Tests

## [1.0.5] - 2021-07-08

### Added

- Checks for compatibility with Python 3.9 and Django 3.2

## [1.0.4] - 2021-01-12

### Removed

- Support for Django 2

## [1.0.2/1.0.3] - 2021-01-11

### Fixed

- Local variable might be referenced before being initialized

## [1.0.1] - 2020-12-16

### Added

- UserAgent for calls to ESI

### Fixed

- Bootstrap classes used in template

## [1.0.0] - 2020-10-12

- first official release

## [0.1.0-alpha.3] - 2020-10-11

### Fixed

- including the right directory in MANIFEST

### Added

- Warning when ESI status couldn't be loaded, for whatever reason

## [0.1.0-alpha.2] - 2020-10-11

### Changed

- Link to image in README updated since GitHub changed the default **master** branch
  to _main_. Fucking stupid change ...

## [0.1.0-alpha.1] - 2020-10-11

### Added

- initial version for testing purposes

<!-- Links -->

[0.1.0-alpha.1]: https://github.com/ppfeufer/aa-esi-status/commits/v0.1.0-alpha.1 "v0.1.0-alpha.1"
[0.1.0-alpha.2]: https://github.com/ppfeufer/aa-esi-status/compare/v0.1.0-alpha.1...v0.1.0-alpha.2 "v0.1.0-alpha.2"
[0.1.0-alpha.3]: https://github.com/ppfeufer/aa-esi-status/compare/v0.1.0-alpha.2...v0.1.0-alpha.3 "v0.1.0-alpha.3"
[1.0.0]: https://github.com/ppfeufer/aa-esi-status/compare/v0.1.0-alpha.3...v1.0.0 "v1.0.0"
[1.0.1]: https://github.com/ppfeufer/aa-esi-status/compare/v1.0.0...v1.0.1 "v1.0.1"
[1.0.2/1.0.3]: https://github.com/ppfeufer/aa-esi-status/compare/v1.0.1...v1.0.2 "v1.0.2/1.0.3"
[1.0.4]: https://github.com/ppfeufer/aa-esi-status/compare/v1.0.2...v1.0.4 "v1.0.4"
[1.0.5]: https://github.com/ppfeufer/aa-esi-status/compare/v1.0.4...v1.0.5 "v1.0.5"
[1.1.0]: https://github.com/ppfeufer/aa-esi-status/compare/v1.0.5...v1.1.0 "v1.1.0"
[1.10.0]: https://github.com/ppfeufer/aa-esi-status/compare/v1.9.0...v1.10.0 "v1.10.0"
[1.11.0]: https://github.com/ppfeufer/aa-esi-status/compare/v1.10.0...v1.11.0 "v1.11.0"
[1.11.1]: https://github.com/ppfeufer/aa-esi-status/compare/v1.11.0...v1.11.1 "v1.11.1"
[1.12.0]: https://github.com/ppfeufer/aa-esi-status/compare/v1.11.1...v1.12.0 "v1.12.0"
[1.12.1]: https://github.com/ppfeufer/aa-esi-status/compare/v1.12.0...v1.12.1 "v1.12.1"
[1.13.0]: https://github.com/ppfeufer/aa-esi-status/compare/v1.12.1...v1.13.0 "v1.13.0"
[1.14.0]: https://github.com/ppfeufer/aa-esi-status/compare/v1.13.0...v1.14.0 "v1.14.0"
[1.14.1]: https://github.com/ppfeufer/aa-esi-status/compare/v1.14.0...v1.14.1 "v1.14.1"
[1.14.2]: https://github.com/ppfeufer/aa-esi-status/compare/v1.14.1...v1.14.2 "v1.14.2"
[1.2.0]: https://github.com/ppfeufer/aa-esi-status/compare/v1.1.0...v1.2.0 "v1.2.0"
[1.3.0]: https://github.com/ppfeufer/aa-esi-status/compare/v1.2.0...v1.3.0 "v1.3.0"
[1.4.0]: https://github.com/ppfeufer/aa-esi-status/compare/v1.3.0...v1.4.0 "v1.4.0"
[1.5.0]: https://github.com/ppfeufer/aa-esi-status/compare/v1.4.0...v1.5.0 "v1.5.0"
[1.5.1]: https://github.com/ppfeufer/aa-esi-status/compare/v1.5.0...v1.5.1 "v1.5.1"
[1.5.2]: https://github.com/ppfeufer/aa-esi-status/compare/v1.5.1...v1.5.2 "v1.5.2"
[1.6.0]: https://github.com/ppfeufer/aa-esi-status/compare/v1.5.2...v1.6.0 "v1.6.0"
[1.7.0]: https://github.com/ppfeufer/aa-esi-status/compare/v1.6.0...v1.7.0 "v1.7.0"
[1.7.1]: https://github.com/ppfeufer/aa-esi-status/compare/v1.7.0...v1.7.1 "v1.7.1"
[1.7.2]: https://github.com/ppfeufer/aa-esi-status/compare/v1.7.1...v1.7.2 "v1.7.2"
[1.8.0]: https://github.com/ppfeufer/aa-esi-status/compare/v1.7.2...v1.8.0 "v1.8.0"
[1.9.0]: https://github.com/ppfeufer/aa-esi-status/compare/v1.8.0...v1.9.0 "v1.9.0"
[2.0.0]: https://github.com/ppfeufer/aa-esi-status/compare/v1.14.2...v2.0.0 "v2.0.0"
[2.0.0-beta.1]: https://github.com/ppfeufer/aa-esi-status/compare/v1.14.2...v2.0.0-beta.1 "v2.0.0-beta.1"
[2.0.0-beta.2]: https://github.com/ppfeufer/aa-esi-status/compare/v2.0.0-beta.1...v2.0.0-beta.2 "v2.0.0-beta.2"
[2.1.0]: https://github.com/ppfeufer/aa-esi-status/compare/v2.0.0...v2.1.0 "v2.1.0"
[2.1.1]: https://github.com/ppfeufer/aa-esi-status/compare/v2.1.0...v2.1.1 "v2.1.1"
[2.2.0]: https://github.com/ppfeufer/aa-esi-status/compare/v2.1.1...v2.2.0 "v2.2.0"
[2.2.1]: https://github.com/ppfeufer/aa-esi-status/compare/v2.2.0...v2.2.1 "v2.2.1"
[2.3.0]: https://github.com/ppfeufer/aa-esi-status/compare/v2.2.1...v2.3.0 "v2.3.0"
[2.4.0]: https://github.com/ppfeufer/aa-esi-status/compare/v2.3.0...v2.4.0 "v2.4.0"
[2.4.1]: https://github.com/ppfeufer/aa-esi-status/compare/v2.4.0...v2.4.1 "v2.4.1"
[2.4.2]: https://github.com/ppfeufer/aa-esi-status/compare/v2.4.1...v2.4.2 "v2.4.2"
[2.4.3]: https://github.com/ppfeufer/aa-esi-status/compare/v2.4.2...v2.4.3 "v2.4.3"
[2.5.0]: https://github.com/ppfeufer/aa-esi-status/compare/v2.4.3...v2.5.0 "v2.5.0"
[2.5.1]: https://github.com/ppfeufer/aa-esi-status/compare/v2.5.0...v2.5.1 "v2.5.1"
[2.5.2]: https://github.com/ppfeufer/aa-esi-status/compare/v2.5.1...v2.5.2 "v2.5.2"
[2.5.3]: https://github.com/ppfeufer/aa-esi-status/compare/v2.5.2...v2.5.3 "v2.5.3"
[2.5.4]: https://github.com/ppfeufer/aa-esi-status/compare/v2.5.3...v2.5.4 "v2.5.4"
[2.6.0]: https://github.com/ppfeufer/aa-esi-status/compare/v2.5.4...v2.6.0 "v2.6.0"
[2.7.0]: https://github.com/ppfeufer/aa-esi-status/compare/v2.6.0...v2.7.0 "v2.7.0"
[2.8.0]: https://github.com/ppfeufer/aa-esi-status/compare/v2.7.0...v2.8.0 "v2.8.0"
[2.8.1]: https://github.com/ppfeufer/aa-esi-status/compare/v2.8.0...v2.8.1 "v2.8.1"
[2.8.2]: https://github.com/ppfeufer/aa-esi-status/compare/v2.8.1...v2.8.2 "v2.8.2"
[2.8.3]: https://github.com/ppfeufer/aa-esi-status/compare/v2.8.2...v2.8.3 "v2.8.3"
[2.8.4]: https://github.com/ppfeufer/aa-esi-status/compare/v2.8.3...v2.8.4 "v2.8.4"
[2.9.0]: https://github.com/ppfeufer/aa-esi-status/compare/v2.8.4...v2.9.0 "v2.9.0"
[2.9.1]: https://github.com/ppfeufer/aa-esi-status/compare/v2.9.0...v2.9.1 "v2.9.1"
[2.9.2]: https://github.com/ppfeufer/aa-esi-status/compare/v2.9.1...v2.9.2 "v2.9.2"
[2.9.3]: https://github.com/ppfeufer/aa-esi-status/compare/v2.9.2...v2.9.3 "v2.9.3"
[3.0.0]: https://github.com/ppfeufer/aa-esi-status/compare/v2.9.3...v3.0.0 "v3.0.0"
[3.0.1]: https://github.com/ppfeufer/aa-esi-status/compare/v3.0.0...v3.0.1 "v3.0.1"
[in development]: https://github.com/ppfeufer/aa-esi-status/compare/v3.0.1...HEAD "In Development"
[keep a changelog]: http://keepachangelog.com/ "Keep a Changelog"
[readme]: https://github.com/ppfeufer/aa-esi-status/blob/main/README.md "README.md"
[semantic versioning]: http://semver.org/ "Semantic Versioning"
