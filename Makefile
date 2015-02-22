PG_CONFIG = pg_config

pg_version := $(word 2,$(shell $(PG_CONFIG) --version))
indexonlyscan_supported = $(filter-out 6.% 7.% 8.% 9.0% 9.1%,$(pg_version))

# Disable index-only scans here so that the regression test output is
# the same in versions that don't support it.
ifneq (,$(indexonlyscan_supported))
export PGOPTIONS = -c enable_indexonlyscan=off
endif

extension_version = 0

EXTENSION = uint
MODULE_big = uint
OBJS = uint.o hash.o hex.o magic.o operators.o aggregates.o
DATA_built = uint--$(extension_version).sql

REGRESS = init hash hex operators misc drop
REGRESS_OPTS = --inputdir=test

EXTRA_CLEAN += operators.c operators.sql test/sql/operators.sql

PGXS := $(shell $(PG_CONFIG) --pgxs)
include $(PGXS)

uint--$(extension_version).sql: uint.sql hash.sql hex.sql operators.sql
	cat $^ >$@

operators.c operators.sql test/sql/operators.sql: generate.py
	python $< $(pg_version)
