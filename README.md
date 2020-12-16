# AA ESI Status

[![Version](https://img.shields.io/pypi/v/aa-esi-status?label=release)](https://pypi.org/project/aa-esi-status/)
[![License](https://img.shields.io/badge/license-GPLv3-green)](https://pypi.org/project/aa-esi-status/)
[![Python](https://img.shields.io/pypi/pyversions/aa-esi-status)](https://pypi.org/project/aa-esi-status/)
[![Django](https://img.shields.io/pypi/djversions/aa-esi-status?label=django)](https://pypi.org/project/aa-esi-status/)
[![Code Style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](http://black.readthedocs.io/en/latest/)

App for Alliance Auth to show the current status of ESI and its end points.

![AA ESI Status](https://raw.githubusercontent.com/ppfeufer/aa-esi-status/main/esistatus/docs/aa-esi-status.jpg)

## Contents

- [Installation](#installation)
- [Updating](#updating)
- [Change Log](CHANGELOG.md)


## Installation

**Important**: This app is a plugin for Alliance Auth. If you don't have
Alliance Auth running already, please install it first before proceeding.
(see the official [AA installation guide](https://allianceauth.readthedocs.io/en/latest/installation/allianceauth.html) for details)


### Step 1 - Install app

Make sure you are in the virtual environment (venv) of your Alliance Auth installation.
Then install the latest version:

```bash
pip install aa-esi-status
```


### Step 2 - Update your AA settings

Configure your AA settings (`local.py`) as follows:

- Add `'esistatus',` to `INSTALLED_APPS`


### Step 3 - Finalize the installation

Run migrations & copy static files

```bash
python manage.py collectstatic
python manage.py migrate
```

Restart your supervisor services for AA


### Step 4 - Setup permissions

Now you can setup permissions in Alliance Auth for your users.
Add ``esistatus|esi status|Can access ths app`` to the states and/or groups you would
like to have access.


## Updating

To update your existing installation of AA Time Zones first enable your virtual environment.

Then run the following commands from your AA project directory (the one that contains `manage.py`).

```bash
pip install -U aa-esi-status
```

```bash
python manage.py collectstatic
```

```bash
python manage.py migrate
```

Now restart your AA supervisor services.
