# File Loader App

### Requirements
* python 3.x
* venv
* pip

After establishing a venv - install packages
```bash
$ pip install -r requirements.txt
```

Create required directories and init sqlite db inside this directory
```bash
$ mkdir data logs data/loaded data/failed
$ touch clover.db
```


### Tests
Run tests:
```bash
$ python run.py test
```

Run coverage:
```bash
$ coverage run --source file_loader/ run.py test
$ coverage report -m
```


### Usage 

Running the parser:
```bash
# run on a single file to a sqlite backend
$ python run.py load -f testfile_2018-01-01 -b sqlite
#
# run on all the files in the data directory (dir specified in config.py)
$ python run.py load -a -b sqlite
```

