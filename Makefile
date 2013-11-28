PG_CONFIG = pg_config

extension_version = 0

EXTENSION = uint
MODULE_big = uint
OBJS = uint.o
DATA_built = uint--$(extension_version).sql

REGRESS = init test
REGRESS_OPTS = --inputdir=test

PGXS := $(shell $(PG_CONFIG) --pgxs)
include $(PGXS)

uint--$(extension_version).sql: uint.sql
	cp $< $@
