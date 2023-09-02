# AA ESI Status<a name="aa-esi-status"></a>

[![Version](https://img.shields.io/pypi/v/aa-esi-status?label=release)](https://pypi.org/project/aa-esi-status/)
[![License](https://img.shields.io/github/license/ppfeufer/aa-esi-status)](https://github.com/ppfeufer/aa-esi-status/blob/master/LICENSE)
[![Python](https://img.shields.io/pypi/pyversions/aa-esi-status)](https://pypi.org/project/aa-esi-status/)
[![Django](https://img.shields.io/pypi/djversions/aa-esi-status?label=django)](https://pypi.org/project/aa-esi-status/)
![pre-commit](https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit&logoColor=white)
[![Code Style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](http://black.readthedocs.io/en/latest/)
[![Discord](https://img.shields.io/discord/790364535294132234?label=discord)](https://discord.gg/zmh52wnfvM)
[![Checks](https://github.com/ppfeufer/aa-esi-status/actions/workflows/automated-checks.yml/badge.svg)](https://github.com/ppfeufer/aa-esi-status/actions/workflows/automated-checks.yml)
[![codecov](https://codecov.io/gh/ppfeufer/aa-esi-status/branch/main/graph/badge.svg?token=1PCUZRGPBT)](https://codecov.io/gh/ppfeufer/aa-esi-status)
[![Translation status](https://weblate.ppfeufer.de/widget/alliance-auth-apps/aa-esi-status/svg-badge.svg)](https://weblate.ppfeufer.de/engage/alliance-auth-apps/)
[![Contributor Covenant](https://img.shields.io/badge/Contributor%20Covenant-2.1-4baaaa.svg)](https://github.com/ppfeufer/aa-esi-status/blob/master/CODE_OF_CONDUCT.md)

[![ko-fi](https://ko-fi.com/img/githubbutton_sm.svg)](https://ko-fi.com/N4N8CL1BY)

App for Alliance Auth to show the current status of ESI and its end points.

______________________________________________________________________

<!-- mdformat-toc start --slug=github --maxlevel=6 --minlevel=1 -->

- [AA ESI Status](#aa-esi-status)
  - [Installation](#installation)
    - [Step 1: Install the App](#step-1-install-the-app)
    - [Step 2: Update Your AA Settings](#step-2-update-your-aa-settings)
    - [Step 3: Finalizing the Installation](#step-3-finalizing-the-installation)
  - [(Optional) Public Views](#optional-public-views)
  - [Updating](#updating)
  - [Changelog](#changelog)
  - [Translation Status](#translation-status)
  - [Contributing](#contributing)

<!-- mdformat-toc end -->

______________________________________________________________________

![AA ESI Status](https://raw.githubusercontent.com/ppfeufer/aa-esi-status/main/esistatus/docs/aa-esi-status.jpg)

## Installation<a name="installation"></a>

> **Note**
>
> This app is a plugin for Alliance Auth. If you don't have Alliance Auth running
> already, please install it first before proceeding. (See the official [AA
> installation guide](https://allianceauth.readthedocs.io/en/latest/installation/allianceauth.html) for details)
>
> AA ESI Status needs at least **Alliance Auth v3.6.1**. Please make sure to meet
> this condition _before_ installing this app, otherwise an update to Alliance Auth
> will be pulled in unsupervised.

### Step 1: Install the App<a name="step-1-install-the-app"></a>

Make sure you're in the virtual environment (venv) of your Alliance Auth installation.
Then install the latest version:

```shell
pip install aa-esi-status
```

### Step 2: Update Your AA Settings<a name="step-2-update-your-aa-settings"></a>

Configure your AA settings (`local.py`) as follows:

- Add `"esistatus",` to `INSTALLED_APPS`

### Step 3: Finalizing the Installation<a name="step-3-finalizing-the-installation"></a>

Run migrations & copy static files.

```shell
python manage.py collectstatic
python manage.py migrate
```

Restart your supervisor services for AA.

## (Optional) Public Views<a name="optional-public-views"></a>

This app supports AA's feature of public views, since the ESI status is not any
mission-critical information.
To allow users to view the time zone conversion page without the need to log in,
please add `"esistatus",` to the list of `APPS_WITH_PUBLIC_VIEWS` in your `local.py`:

```python
# By default, apps are prevented from having public views for security reasons.
# To allow specific apps to have public views, add them to APPS_WITH_PUBLIC_VIEWS
#   » The format is the same as in INSTALLED_APPS
#   » The app developer must also explicitly allow public views for their app
APPS_WITH_PUBLIC_VIEWS = [
    "esistatus",  # https://github.com/ppfeufer/aa-esi-status/
]
```

> **Note**
>
> If you don't have a list for `APPS_WITH_PUBLIC_VIEWS` yet, then add the whole
> block from here. This feature has been added in Alliance Auth v3.6.0 so you
> might not yet have this list in your `local.py`.

## Updating<a name="updating"></a>

To update your existing installation of AA ESI Status, first enable your virtual
environment.

Then run the following commands from your AA project directory (the one that
contains `manage.py`).

```shell
pip install -U aa-esi-status
python manage.py collectstatic
python manage.py migrate
```

Now restart your AA supervisor services.

## Changelog<a name="changelog"></a>

See [CHANGELOG.md](https://github.com/ppfeufer/aa-esi-status/blob/main/CHANGELOG.md)

## Translation Status<a name="translation-status"></a>

[![Translation status](https://weblate.ppfeufer.de/widget/alliance-auth-apps/aa-esi-status/multi-auto.svg)](https://weblate.ppfeufer.de/engage/alliance-auth-apps/)

Do you want to help translate this app into your language or improve the existing
translation? - [Join our team of translators][weblate engage]!

## Contributing<a name="contributing"></a>

Do you want to contribute to this project? That's cool!

Please make sure to read the [Contribution Guidelines](https://github.com/ppfeufer/aa-esi-status/blob/main/CONTRIBUTING.md).\
(I promise, it's not much, just some basics)

<!-- Links -->

[weblate engage]: https://weblate.ppfeufer.de/engage/alliance-auth-apps/ "Weblate Translations"
