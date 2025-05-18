PG_CONFIG = pg_config

pg_version := $(word 2,$(shell $(PG_CONFIG) --version))
indexonlyscan_supported = $(filter-out 6.% 7.% 8.% 9.0% 9.1%,$(pg_version))

# Disable index-only scans here so that the regression test output is
# the same in versions that don't support it.
ifneq (,$(indexonlyscan_supported))
export PGOPTIONS = -c enable_indexonlyscan=off
endif

pg_config_h := $(shell $(PG_CONFIG) --includedir-server)/pg_config.h
use_float8_byval := $(shell grep -q 'USE_FLOAT8_BYVAL 1' $(pg_config_h) && echo yes)
comma = ,

EXTENSION = uint
MODULE_big = uint
OBJS = aggregates.o hash.o hex.o inout.o magic.o misc.o operators.o
DATA_built = uint--1.sql uint--0--1.sql \
		 uint--0.sql

REGRESS = init hash hex operators misc binary drop upgrade
REGRESS_OPTS = --inputdir=test

EXTRA_CLEAN += operators.c operators--0.sql.in test/sql/operators.sql

PGXS := $(shell $(PG_CONFIG) --pgxs)
include $(PGXS)

uint--1.sql.in: types--1.sql.in hash--0.sql.in hex--0.sql.in operators--0.sql.in
	cat $^ >$@

uint--0--1.sql.in: types--0--1.sql.in
	cat $^ >$@

uint--0.sql.in: types--0.sql.in hash--0.sql.in hex--0.sql.in operators--0.sql.in
	cat $^ >$@

uint--%.sql: uint--%.sql.in
	sed 's/@UINT8_PASSEDBYVALUE@/$(if $(use_float8_byval),PASSEDBYVALUE$(comma))/' $< >$@

PYTHON ?= python
PYFLAKES ?= pyflakes

operators.c operators--0.sql.in test/sql/operators.sql: generate.py
	$(PYTHON) $< $(pg_version)

python-check: generate.py
	pycodestyle $^
	$(PYFLAKES) $^
	pylint $^
