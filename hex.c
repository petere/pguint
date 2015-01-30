#include <postgres.h>
#include <fmgr.h>
#include <utils/builtins.h>

#include "uint.h"

#define HEXBASE 16

static text*
_to_hex(uint64 value)
{
	char	   *ptr;
	const char *digits = "0123456789abcdef";
	char		buf[32];		/* bigger than needed, but reasonable */

	ptr = buf + sizeof(buf) - 1;
	*ptr = '\0';

	do
	{
		*--ptr = digits[value % HEXBASE];
		value /= HEXBASE;
	} while (ptr > buf && value);

	return cstring_to_text(ptr);
}

#define make_to_hex(type, BTYPE) \
PG_FUNCTION_INFO_V1(to_hex_##type); \
Datum \
to_hex_##type(PG_FUNCTION_ARGS) \
{ \
	PG_RETURN_TEXT_P(_to_hex(PG_GETARG_##BTYPE(0))); \
} \
extern int no_such_variable

make_to_hex(uint4, UINT32);
make_to_hex(uint8, UINT64);
