PG_CONFIG = pg_config

extension_version = 0

EXTENSION = uint
MODULE_big = uint
OBJS = uint.o hash.o hex.o operators.o
DATA_built = uint--$(extension_version).sql

REGRESS = init test hash hex operators
REGRESS_OPTS = --inputdir=test

PGXS := $(shell $(PG_CONFIG) --pgxs)
include $(PGXS)

uint--$(extension_version).sql: uint.sql hash.sql hex.sql operators.sql
	cat $^ >$@

operators.c operators.sql test/sql/operators.sql: generate.py
	python $<
