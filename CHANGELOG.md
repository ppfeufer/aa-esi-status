# Change Log

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](http://keepachangelog.com/)
and this project adheres to [Semantic Versioning](http://semver.org/).


## [In Development] - Unreleased


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

- Category with names containing a space couldn't be opened (e.g. Faction Warfare)

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


## [1.0.3] - 2021-01-11

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

- Warning when ESI status couldn't be loaded, for what ever reason


## [0.1.0-alpha.2] - 2020-10-11

### Changed

- Link to image in README updated since GitHub changed the default **master** branch to _main_. Fucking stupid change ...


## [0.1.0-alpha.1] - 2020-10-11

### Added

- initial version for testing purposes
