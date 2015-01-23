PG_CONFIG = pg_config

extension_version = 0

EXTENSION = uint
MODULE_big = uint
OBJS = uint.o operators.o
DATA_built = uint--$(extension_version).sql

REGRESS = init test operators
REGRESS_OPTS = --inputdir=test

PGXS := $(shell $(PG_CONFIG) --pgxs)
include $(PGXS)

uint--$(extension_version).sql: uint.sql operators.sql
	cat $^ >$@

operators.c operators.sql test/sql/operators.sql: generate.py
	python $<
