# Super Clever Plan - PlanParser

## Installation

1. Install python3 and python3-pip on your system (example: `apt install python3 python3-pip`)

2. Install required libraries: `pip install -r req.txt`


## Usage

`python3 main.py <domain> [options]`

## Available options
- `--timetable-engine [www/vulcan]` - force usage of specified timetable engine
- `--vulcan-timetable [file.json]` - data source for vulcan engine
- `--force-notification` - send notification to clients even if there were no changes in timetable

## Configuration
- `config/config.py` - declare general config here
- `config/targets.py` - declare target config here

## General config
- **debug_type** _(int)_
  - 0 - i have no idea, this might be unused
  - 1 - i have no idea, this might be unused
  - 2 - i have no idea, this might be unused
- **timetable_url** _(str)_ - root timetable directory for www parser
- **timetable_engine**_(str)_  - _"www"_ / _"vulcan"_
- **overrides_url** _(str)_ - "root overrides page for www parser
- **overrides_engine** _(str)_ - _"www"_ / _"vulcan"_
- **vulcan_login** _(str)_ - this should be read from secrets
- **vulcan_password** _(str)_ - this should be read from secrets
- **vulcan_access** _(str)_ - this should be read from secrets
- **overrides_stats** _(bool)_ - deprecated, same as **overrides_archiver**
- **overrides_archiver** _(bool)_ - enables saving all past overrides
- **timetable_archiver** _(bool)_ - enables saving all past timetables
- **teacher_recovery_filename** _(str)_- path to json file used to fix teacher short names after www engine import
- **teachermap_filename** _(str)_ - path to json file with teacher dict - ```{"SN":"Short Name"}```
- **timesteps_filename** _(str)_ - path to json file with defined timesteps
- **output_data_path** _(str)_ - path to json file where parsed data will be written

## Target config
Declare target as python dict:

```python
targets["known_name"] = {
	"dev": True,
	"http_rootdir_app": "/",
	"http_rootdir_manifest": "/",
	"hostname": "plan.example.com",
	"upload": True,
	"uploader": "ftp",
	"ftp": {
		"user": "user",
		"pass": "password",
		"rootdir_manifest": "/",
		"rootdir_app": "/"
	}
}
```

- **"known_name"** (str) - name used when uploading - `python3 main.py known_name`
- **"dev"** (bool) - should this target have enabled dev features
- **"http_rootdir_app"** (str) - where app will be available via HTTP
- **"http_rootdir_manifest"** (str) - where app manifest will be available via HTTP
- **"hostname"** (str) - host to upload to
- **"upload"** (bool) - should upload to this target be allowed
- **"uploader"** (str) - which uploader will be used (ftp/local/scp)
- **"ftp"** (str) - replace this with selected uploader (ftp/local/scp)
  - **"user"** (str) - username (ftp/scp only)
  - **"pass"** (str) - password (ftp/scp only)
  - **"rootdir_manifest"** (str) - where app should be uploaded, relative to selected uploader root dir
  - **"rootdir_app"** (str) - where app manifest should be uploaded, relative to selected uploader root dir