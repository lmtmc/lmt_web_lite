# See the README.md notes on how to use this Makefile

SHELL = /bin/bash

GIT_DIRS = lmtoy_lite

URL1  = https://github.com/astroumd/lmtoy

.PHONY:  help

## help:      This Help
help : Makefile
	@sed -n 's/^##//p' $<


## git:       Get all git repos for this install
git:  $(GIT_DIRS)
	@echo Last git: `date` >> git.log

## pull:      Update all git repos
pull:
	@echo -n "lmtoy: "; git pull
	-@for dir in $(GIT_DIRS); do\
	(echo -n "$$dir: " ;cd $$dir; git pull); done
	@echo Last pull: `date` >> git.log

status:
	@echo -n "lmtoy: "; git status -uno
	-@for dir in $(GIT_DIRS); do\
	(echo -n "$$dir: " ;cd $$dir; git status -uno); done

branch:
	@echo -n "lmtoy: "; git branch --show-current
	-@for dir in $(GIT_DIRS); do\
	(echo -n "$$dir: " ;cd $$dir; git branch --show-current); done


## config:    TBD
config:  
	./configure


lmtoy_lite:
	git clone $(URL1) lmtoy_lite

## update:    recompile what needs to be recompiled
update:
	@echo nothing here yet


## env:       make a virtual environment 
env:
	python3 -m venv env

## clean:     testing to wipe env and lmtoy_lite
clean:
	rm -rf env lmtoy_lite

## pjt:       test install env and lmtoy_lite
pjt:	lmtoy_lite env
	(source env/bin/activate; pip install -r requirements.txt)
	(source env/bin/activate; pip install --upgrade pip; pip install --no-deps -e lmtoy_lite)

## pjt2:      show where lmtoy now lives
pjt2:
	python -c 'import lmtoy; print(lmtoy.__file__)'

