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

extension_version = 0

EXTENSION = uint
MODULE_big = uint
OBJS = aggregates.o hash.o hex.o inout.o magic.o misc.o operators.o
DATA_built = uint--$(extension_version).sql

REGRESS = init hash hex operators misc drop
REGRESS_OPTS = --inputdir=test

EXTRA_CLEAN += operators.c operators.sql test/sql/operators.sql

PGXS := $(shell $(PG_CONFIG) --pgxs)
include $(PGXS)

uint--$(extension_version).sql: uint.sql hash.sql hex.sql operators.sql
	cat $^ | sed 's/@UINT8_PASSEDBYVALUE@/$(if $(use_float8_byval),PASSEDBYVALUE$(comma))/' >$@

PYTHON ?= python

operators.c operators.sql test/sql/operators.sql: generate.py
	$(PYTHON) $< $(pg_version)

python-check: generate.py
	pep8 $^
	pyflakes $^
	pylint $^
