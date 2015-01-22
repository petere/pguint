PG_CONFIG = pg_config

extension_version = 0

EXTENSION = uint
MODULE_big = uint
OBJS = uint.o compare.o
DATA_built = uint--$(extension_version).sql

REGRESS = init test compare
REGRESS_OPTS = --inputdir=test

PGXS := $(shell $(PG_CONFIG) --pgxs)
include $(PGXS)

uint--$(extension_version).sql: uint.sql compare.sql
	cat $^ >$@

compare.c compare.sql test/sql/compare.sql: generate.py
	python $<
