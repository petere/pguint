import re
import sys


new_types = ['int1', 'uint1', 'uint2', 'uint4', 'uint8']
old_types = ['int2', 'int4', 'int8']

comparison_ops = ['<', '<=', '=', '<>', '>=', '>']
arithmetic_ops = ['+', '-', '*', '/', '%']

commutators = {
    '<': '>',
    '<=': '>=',
    '=': '=',
    '<>': '<>',
    '>=': '<=',
    '>': '<',

    '+': '+',
    '*': '*',

    '&': '&',
    '|': '|',
    '#': '#',
}

negators = {
    '<': '>=',
    '<=': '>',
    '=': '<>',
    '<>': '=',
    '>=': '<',
    '>': '<=',
}

restriction_estimators = {
    '=': 'eqsel',
    '<>': 'neqsel',
    '<': 'scalarltsel',
    '<=': 'scalarltsel',
    '>': 'scalargtsel',
    '>=': 'scalargtsel',
}

join_estimators = {
    '=': 'eqjoinsel',
    '<>': 'neqjoinsel',
    '<': 'scalarltjoinsel',
    '<=': 'scalarltjoinsel',
    '>': 'scalargtjoinsel',
    '>=': 'scalargtjoinsel',
}

op_words = {
    '<': 'lt', '<=': 'le', '=': 'eq', '<>': 'ne', '>=': 'ge', '>': 'gt',
    '+': 'pl', '-': 'mi', '*': 'mul', '/': 'div', '%': 'mod',
    '&': 'and', '|': 'or', '#': 'xor', '~': 'not', '<<': 'shl', '>>': 'shr',
}

c_types = {
    'boolean': 'bool',
    'int1': 'int8',
    'int2': 'int16',
    'int4': 'int32',
    'int8': 'int64',
    'uint1': 'uint8',
    'uint2': 'uint16',
    'uint4': 'uint32',
    'uint8': 'uint64',
}


def c_operator(op):
    if op == '=':
        return '=='
    elif op == '<>':
        return '!='
    elif op == '#':
        return '^'
    else:
        return op


def type_bits(typ):
    m = re.search(r'(\d+)', typ)
    return int(m.group(1)) * 8


def type_signed(typ):
    return not type_unsigned(typ)


def type_unsigned(typ):
    return typ.startswith('u')


min_values = {
    'int1': '-128',
}

max_values = {
    'int1': '127',
    'int2': '32767',
    'int4': '2147483647',
    'int8': '9223372036854775807',
    'uint1': '255',
    'uint2': '65535',
    'uint4': '4294967295',
    'uint8': '18446744073709551615',
}

too_big = {
    'int1': '200',
    'int2': '40000',
    'int4': '3000000000',
    'int8': '10000000000000000000',
    'uint1': '300',
    'uint2': '70000',
    'uint4': '5000000000',
    'uint8': '20000000000000000000',
}


def next_bigger_type(typ):
    m = re.match(r'(\w+)(\d+)', typ)
    return m.group(1) + str(int(m.group(2)) * 2)


def write_c_function(f, funcname, argtypes, rettype, body):
    f.write("""
PG_FUNCTION_INFO_V1({funcname});
Datum
{funcname}(PG_FUNCTION_ARGS)
{{
""".format(funcname=funcname))
    argnum = 0
    argvar = 0
    for argtype in argtypes:
        argvar += 1
        if argtype is None:
            continue
        f.write("\t{0} arg{1} = PG_GETARG_{2}({3});\n"
                .format(c_types[argtype],
                        argvar,
                        c_types[argtype].upper(),
                        argnum))
        argnum += 1
    f.write("\t{0} result;\n".format(c_types[rettype]))
    f.write("\n")
    f.write("\t" + body.replace("\n", "\n\t").replace("\n\t\n", "\n\n"))
    f.write("\n")
    f.write("""
\tPG_RETURN_{0}(result);
}}
""".format(c_types[rettype].upper()))


def write_sql_function(f, funcname, argtypes, rettype, sql_funcname=None, strict=True):
    if not sql_funcname:
        sql_funcname = funcname
    f.write("CREATE FUNCTION {sql_funcname}({argtypes}) RETURNS {rettype}"
            " IMMUTABLE{strict} LANGUAGE C AS '$libdir/uint', '{funcname}';\n\n"
            .format(sql_funcname=sql_funcname,
                    argtypes=', '.join([x for x in argtypes if x]),
                    rettype=rettype,
                    strict=(" STRICT" if strict else ""),
                    funcname=funcname))


def write_op_c_function(f, funcname, lefttype, righttype, op, rettype, c_check='', intermediate_type=None):
    body = ""
    if intermediate_type:
        body += "{0} result2;\n\n".format(c_types[intermediate_type])
    if op in ['/', '%']:
        body += """if (arg2 == 0)
{
\tereport(ERROR,
\t\t(errcode(ERRCODE_DIVISION_BY_ZERO),
\t\t errmsg("division by zero")));
\tPG_RETURN_NULL();
}

"""
    if op == '%' and not type_unsigned(righttype):
        body += """if (arg2 == -1)
\tPG_RETURN_{0}(0);

""".format(c_types[rettype].upper())
    if intermediate_type:
        body += "result2 = "
    else:
        body += "result = "
    if lefttype:
        if intermediate_type:
            body += "({0})".format(c_types[intermediate_type])
        body += "arg1"
    body += " " + c_operator(op) + " "
    if righttype:
        if intermediate_type:
            body += "({0})".format(c_types[intermediate_type])
        body += "arg2"
    body += ";"
    if c_check:
        body += """

if ({0})
\tereport(ERROR,
\t\t(errcode(ERRCODE_NUMERIC_VALUE_OUT_OF_RANGE),
\t\t errmsg("integer out of range")));""".format(c_check)
    if intermediate_type:
        body += "\nresult = result2;"

    write_c_function(f, funcname, [lefttype, righttype], rettype, body)


def write_sql_operator(f, funcname, lefttype, righttype, op, rettype):
    sql_funcname = funcname
    if op == '%':
        # SQL standard requires a "mod" function rather than % operator
        sql_funcname = 'mod'
    write_sql_function(f, funcname, [lefttype, righttype], rettype, sql_funcname=sql_funcname)

    f.write("CREATE OPERATOR {0} (\n".format(op))
    if lefttype:
        f.write("    LEFTARG = {0},\n".format(lefttype))
    if righttype:
        f.write("    RIGHTARG = {0},\n".format(righttype))
    if op in commutators:
        f.write("    COMMUTATOR = {0},\n".format(commutators[op]))
    if op in negators:
        f.write("    NEGATOR = {0},\n".format(negators[op]))
    if op in restriction_estimators:
        f.write("    RESTRICT = {0},\n".format(restriction_estimators[op]))
    if op in join_estimators:
        f.write("    JOIN = {0},\n".format(join_estimators[op]))
    if op in ['=']:
        f.write("    HASHES,\n")
        f.write("    MERGES,\n")
    f.write("    PROCEDURE = {0}\n);\n\n".format(sql_funcname))


def write_cmp_c_function(f, lefttype, righttype):
    funcname = 'bt' + coalesce(lefttype, '') + coalesce(righttype, '') + 'cmp'
    write_c_function(f, funcname, [lefttype, righttype], 'int4',
                     """if (arg1 > arg2)
\tresult = 1;
else if (arg1 == arg2)
\tresult = 0;
else
\tresult = -1;""")


def write_cmp_sql_function(f, lefttype, righttype):
    funcname = 'bt' + coalesce(lefttype, '') + coalesce(righttype, '') + 'cmp'
    write_sql_function(f, funcname, [lefttype, righttype], 'integer')


def write_sortsupport_c_function(f, typ):
    f.write("""
static int
bt{typ}fastcmp(Datum x, Datum y, SortSupport ssup)
{{
\t{ctype} a = DatumGet{Ctype}(x);
\t{ctype} b = DatumGet{Ctype}(y);

\tif (a > b)
\t\treturn 1;
\telse if (a == b)
\t\treturn 0;
\telse
\t\treturn -1;
}}

PG_FUNCTION_INFO_V1(bt{typ}sortsupport);
Datum
bt{typ}sortsupport(PG_FUNCTION_ARGS)
{{
\tSortSupport ssup = (SortSupport) PG_GETARG_POINTER(0);

\tssup->comparator = bt{typ}fastcmp;
\tPG_RETURN_VOID();
}}
""".format(typ=typ, ctype=c_types[typ], Ctype=c_types[typ].replace('u', 'U').replace('i', 'I')))


def write_opclasses_sql(f, typ):
    f.write("""CREATE OPERATOR CLASS {typ}_ops
    DEFAULT FOR TYPE {typ} USING btree FAMILY integer_ops AS
        OPERATOR        1       < ,
        OPERATOR        2       <= ,
        OPERATOR        3       = ,
        OPERATOR        4       >= ,
        OPERATOR        5       > ,
        FUNCTION        1       bt{typ}{typ}cmp({typ}, {typ}),
        FUNCTION        2       bt{typ}sortsupport(internal);

CREATE OPERATOR CLASS {typ}_ops
    DEFAULT FOR TYPE {typ} USING hash FAMILY integer_ops AS
        OPERATOR        1       =,
        FUNCTION        1       hash{typ}({typ});

""".format(typ=typ))


def coalesce(*args):
    return next((a for a in args if a is not None), None)


def write_code(f_c, f_sql, lefttype, righttype, op, rettype, c_check='', intermediate_type=None):
    funcname = coalesce(lefttype, '') + coalesce(righttype, '') + op_words[op]
    write_op_c_function(f_c, funcname, lefttype, righttype, op, rettype, c_check, intermediate_type)
    write_sql_operator(f_sql, funcname, lefttype, righttype, op, rettype)


sum_trans_types = {
    'int1': 'int4',
    'uint1': 'uint4',
    'uint2': 'uint8',
    'uint4': 'uint8',
    'uint8': 'uint8',
}

avg_trans_types = {
    'int1': '_int8',
    'uint1': '_int8',
    'uint2': '_int8',
    'uint4': '_int8',
    'uint8': '_int8',
}


def write_arithmetic_op(f_c, f_sql, f_test_sql, op, lefttype, righttype):
    argtypes = sorted([lefttype, righttype], key=lambda x: (type_bits(x), type_unsigned(x)))
    rettype = argtypes[-1]
    if type_unsigned(rettype):
        if op == '+':
            if type_signed(lefttype):
                c_check = '(arg1 < 0 && result > arg2) || (arg1 > 0 && result < arg2)'
            elif type_signed(righttype):
                c_check = '(arg2 < 0 && result > arg1) || (arg2 > 0 && result < arg1)'
            else:  # both arguments unsigned
                c_check = 'result < arg1 || result < arg2'
        elif op == '-':
            if type_signed(lefttype):
                c_check = '(arg1 < 0) || (result > arg1)'
            elif type_signed(righttype):
                c_check = '(arg2 < 0 && result < arg1) || (arg2 > 0 && result > arg1)'
            else:
                c_check = 'result > arg1'
        elif op == '/':
            if type_signed(lefttype):
                c_check = 'arg1 < 0'
            elif type_signed(righttype):
                c_check = 'arg2 < 0'
            else:
                c_check = ''
        elif op == '%':
            if type_signed(lefttype):
                c_check = 'arg1 < 0'
            elif type_signed(righttype):
                # This computation has a positive result, so it would
                # actually fit just fine, but the C implementation
                # makes a mess of it, so better prohibit it.
                c_check = 'arg2 < 0'
            else:
                c_check = ''
        else:
            c_check = ''
    else:
        if op == '+':
            c_check = 'SAMESIGN(arg1, arg2) && !SAMESIGN(result, arg1)'
        elif op == '-':
            c_check = '!SAMESIGN(arg1, arg2) && !SAMESIGN(result, arg1)'
        else:
            c_check = ''
    intermediate_type = None
    if op == '*':
        if type_bits(rettype) < 64:
            intermediate_type = next_bigger_type(rettype)
            c_check = '({0}) result2 != result2'.format(c_types[rettype])
        elif type_unsigned(rettype):
            if type_unsigned(lefttype) and type_signed(righttype):
                c_check = '(arg2 < 0) || ('
            elif type_signed(lefttype) and type_unsigned(righttype):
                c_check = '(arg1 < 0) || ('
            else:
                c_check = '('
            c_check += '(arg1 != ((uint32) arg1) || arg2 != ((uint32) arg2))'
            if type_unsigned(lefttype) or type_unsigned(righttype):
                c_check += ' && (arg2 != 0 && (result / arg2 != arg1))'
            else:
                c_check += ' && (arg2 != 0 && ((arg2 == -1 && arg1 < 0 && result < 0) || result / arg2 != arg1))'
            c_check += ')'
        else:
            c_check = '(arg1 != ((int32) arg1) || arg2 != ((int32) arg2))'
            if type_unsigned(lefttype) or type_unsigned(righttype):
                c_check += ' && (arg2 != 0 && (result / arg2 != arg1))'
            else:
                c_check += ' && (arg2 != 0 && ((arg2 == -1 && arg1 < 0 && result < 0) || result / arg2 != arg1))'
    write_code(f_c, f_sql, lefttype, righttype, op, rettype, c_check, intermediate_type)
    f_test_sql.write("""\
SELECT pg_typeof('1'::{lefttype} {op} '1'::{righttype});
SELECT '1'::{lefttype} {op} '1'::{righttype};
SELECT '3'::{lefttype} {op} '4'::{righttype};
SELECT '5'::{lefttype} {op} '2'::{righttype};
""".format(lefttype=lefttype, op=op, righttype=righttype))
    if not type_unsigned(lefttype) and op in ['+', '-', '*', '/', '%']:
        f_test_sql.write("""\
SELECT '-3'::{lefttype} {op} '4'::{righttype};
SELECT '-5'::{lefttype} {op} '2'::{righttype};
""".format(lefttype=lefttype, op=op, righttype=righttype))
    if not type_unsigned(righttype) and op in ['+', '-', '*', '/', '%']:
        f_test_sql.write("""\
SELECT '3'::{lefttype} {op} '-4'::{righttype};
SELECT '5'::{lefttype} {op} '-2'::{righttype};
""".format(lefttype=lefttype, op=op, righttype=righttype))
    if op in ['+', '*']:
        f_test_sql.write("SELECT '{max_left}'::{lefttype} {op} '{max_right}'::{righttype};\n"
                         .format(lefttype=lefttype, op=op, righttype=righttype,
                                 max_left=max_values[lefttype],
                                 max_right=max_values[righttype]))
    if op in ['/', '%']:
        f_test_sql.write("SELECT '5'::{lefttype} {op} '0'::{righttype};\n"
                         .format(lefttype=lefttype, op=op, righttype=righttype))
    if op in ['%']:
        f_test_sql.write("SELECT mod('5'::{lefttype}, '2'::{righttype});\n"
                         .format(lefttype=lefttype, righttype=righttype))


def main(pgversion):
    _ = pgversion  # unused
    f_c = open('operators.c', 'w', encoding='ascii')
    f_sql = open('operators.sql', 'w', encoding='ascii')
    f_test_sql = open('test/sql/operators.sql', 'w', encoding='ascii')

    f_c.write("""\
#include <postgres.h>
#include <fmgr.h>

#include "uint.h"

#include <utils/sortsupport.h>

""")

    for typ in new_types:
        f_test_sql.write("""\
SELECT '55'::{typ};
SELECT '-55'::{typ};
SELECT ''::{typ};
SELECT 'x'::{typ};
SELECT '55 x'::{typ};
""".format(typ=typ))
        if typ in too_big:
            f_test_sql.write("SELECT '{num}'::{typ};\n".format(typ=typ, num=max_values[typ]))
            f_test_sql.write("SELECT '{num}'::{typ};\n".format(typ=typ, num=too_big[typ]))
            if not type_unsigned(typ):
                f_test_sql.write("SELECT '{num}'::{typ};\n".format(typ=typ, num=min_values[typ]))
                f_test_sql.write("SELECT '-{num}'::{typ};\n".format(typ=typ, num=too_big[typ]))
        f_test_sql.write("""\

CREATE TABLE test_{typ} (a {typ});
INSERT INTO test_{typ} VALUES ({vals[0]}), ({vals[1]}), ({vals[2]}), ({vals[3]}), ({vals[4]});
SELECT a FROM test_{typ};
SELECT a FROM test_{typ} ORDER BY a;
DROP TABLE test_{typ};

""".format(typ=typ, vals=(range(1, 6) if type_unsigned(typ) else range(-2, 3))))

    for lefttype in new_types + old_types:
        for op in comparison_ops + arithmetic_ops:
            f_test_sql.write("""\
SELECT '2'::{typ} {op} 5;
SELECT 2 {op} '5'::{typ};
SELECT '5'::{typ} {op} 2;
SELECT 5 {op} '2'::{typ};
""".format(typ=lefttype, op=op))
        for righttype in new_types + old_types:
            if lefttype in old_types and righttype in old_types:
                continue
            for op in comparison_ops:
                write_code(f_c, f_sql, lefttype, righttype, op, rettype='boolean')
                f_test_sql.write("""\
SELECT '1'::{lefttype} {op} '1'::{righttype};
SELECT '5'::{lefttype} {op} '2'::{righttype};
SELECT '3'::{lefttype} {op} '4'::{righttype};
""".format(lefttype=lefttype, op=op, righttype=righttype))
            f_test_sql.write("\n")

            write_cmp_c_function(f_c, lefttype, righttype)
            write_cmp_sql_function(f_sql, lefttype, righttype)
            f_test_sql.write("""\
SELECT bt{lefttype}{righttype}cmp('1'::{lefttype}, '1'::{righttype});
SELECT bt{lefttype}{righttype}cmp('5'::{lefttype}, '2'::{righttype});
SELECT bt{lefttype}{righttype}cmp('3'::{lefttype}, '4'::{righttype});
""".format(lefttype=lefttype, righttype=righttype))

            for op in arithmetic_ops:
                write_arithmetic_op(f_c, f_sql, f_test_sql,
                                    op, lefttype, righttype)
            f_test_sql.write("\n")

            if lefttype != righttype:
                f_test_sql.write("SELECT CAST('5'::{lefttype} AS {righttype});\n"
                                 .format(lefttype=lefttype, righttype=righttype))
                if type_bits(lefttype) > type_bits(righttype) \
                   or (type_bits(lefttype) == type_bits(righttype) and type_unsigned(lefttype)):
                    f_test_sql.write("SELECT CAST('{num}'::{lefttype} AS {righttype});\n"
                                     .format(lefttype=lefttype, righttype=righttype, num=too_big[righttype]))
                if not type_unsigned(lefttype):
                    f_test_sql.write("SELECT CAST('-5'::{lefttype} AS {righttype});\n"
                                     .format(lefttype=lefttype, righttype=righttype))
                    if (not type_unsigned(lefttype) and not type_unsigned(righttype)) \
                       and type_bits(lefttype) > type_bits(righttype):
                        f_test_sql.write("SELECT CAST('-{num}'::{lefttype} AS {righttype});\n"
                                         .format(lefttype=lefttype, righttype=righttype, num=too_big[righttype]))

                f_test_sql.write("\n")

                c_funcname = lefttype + "_to_" + righttype
                sql_funcname = righttype
                body = "result = arg1;"
                if type_bits(lefttype) >= type_bits(righttype):
                    body += """
if (({c_type}) result != arg1)
\tereport(ERROR,
\t\t(errcode(ERRCODE_NUMERIC_VALUE_OUT_OF_RANGE),
\t\t errmsg("{typ} out of range")));""".format(c_type=c_types[lefttype], typ=righttype)
                if type_unsigned(lefttype) != type_unsigned(righttype):
                    body += """
if (!SAMESIGN(result, arg1))
\tereport(ERROR,
\t\t(errcode(ERRCODE_NUMERIC_VALUE_OUT_OF_RANGE),
\t\t errmsg("{typ} out of range")));""".format(typ=righttype)
                write_c_function(f_c, c_funcname, [lefttype], righttype, body)
                write_sql_function(f_sql, c_funcname, [lefttype], righttype, sql_funcname=sql_funcname)
                f_sql.write("CREATE CAST ({lefttype} AS {righttype}) WITH FUNCTION {func}({lefttype}) AS {context};\n\n"
                            .format(lefttype=lefttype, righttype=righttype,
                                    func=sql_funcname,
                                    context=("IMPLICIT"
                                             if type_bits(lefttype) < type_bits(righttype) else "ASSIGNMENT")))

    for typ in new_types:
        for op in ['&', '|', '#']:
            write_code(f_c, f_sql, lefttype=typ, righttype=typ, op=op, rettype=typ)
            f_test_sql.write("""\
SELECT '1'::{lefttype} {op} '1'::{righttype};
SELECT '5'::{lefttype} {op} '2'::{righttype};
SELECT '5'::{lefttype} {op} '4'::{righttype};
""".format(lefttype=typ, op=op, righttype=typ))
        for op in ['~']:
            write_code(f_c, f_sql, lefttype=None, righttype=typ, op=op, rettype=typ)
            f_test_sql.write("SELECT {op} '6'::{typ};\n".format(op=op, typ=typ))
        for op in ['<<', '>>']:
            write_code(f_c, f_sql, lefttype=typ, righttype='int4', op=op, rettype=typ)
            f_test_sql.write("""\
SELECT '6'::{typ} {op} 1;
SELECT '6'::{typ} {op} 3;
""".format(typ=typ, op=op))

        f_test_sql.write("\n")

        write_sortsupport_c_function(f_c, typ)
        write_sql_function(f_sql, 'bt' + typ + 'sortsupport', ['internal'], 'void')
        write_opclasses_sql(f_sql, typ)

        for agg, funcname, op in [('min', typ + "smaller", '<'),
                                  ('max', typ + "larger", '>')]:
            write_c_function(f_c, funcname, [typ]*2, typ,
                             body="result = (arg1 {op} arg2) ? arg1 : arg2;".format(op=op))
            write_sql_function(f_sql, funcname, [typ]*2, typ)
            f_test_sql.write("""\
SELECT {funcname}('1'::{typ}, '1'::{typ});
SELECT {funcname}('5'::{typ}, '2'::{typ});
SELECT {funcname}('3'::{typ}, '4'::{typ});
""".format(funcname=funcname, typ=typ))
            f_sql.write("CREATE AGGREGATE {agg}({typ}) (SFUNC = {sfunc}, STYPE = {stype}, SORTOP = {sortop});\n\n"
                        .format(agg=agg, typ=typ, sfunc=funcname, stype=typ, sortop=op))
            f_test_sql.write("SELECT {agg}(val::{typ}) FROM (VALUES (3), (5), (1), (4)) AS _ (val);\n\n"
                             .format(agg=agg, typ=typ))

        for agg, funcname in [('bit_and', typ + typ + "and"),
                              ('bit_or', typ + typ + "or")]:
            f_sql.write("CREATE AGGREGATE {agg}({typ}) (SFUNC = {sfunc}, STYPE = {stype});\n\n"
                        .format(agg=agg, typ=typ, sfunc=funcname, stype=typ))
        f_test_sql.write("SELECT bit_and(val::{typ}) FROM (VALUES (3), (6), (18)) AS _ (val);\n\n"
                         .format(typ=typ))
        f_test_sql.write("SELECT bit_or(val::{typ}) FROM (VALUES (9), (1), (4)) AS _ (val);\n\n"
                         .format(typ=typ))

        sfunc = "{typ}_sum".format(typ=typ)
        stype = sum_trans_types[typ]
        write_sql_function(f_sql, sfunc, [stype, typ], stype, strict=False)
        f_sql.write("CREATE AGGREGATE sum({typ}) (SFUNC = {sfunc}, STYPE = {stype});\n\n"
                    .format(typ=typ, sfunc=sfunc, stype=stype))
        f_test_sql.write("""
SELECT {sfunc}(NULL::{stype}, NULL::{typ});
SELECT {sfunc}(NULL::{stype}, 1::{typ});
SELECT {sfunc}(2::{stype}, NULL::{typ});
SELECT {sfunc}(2::{stype}, 1::{typ});

SELECT sum(val::{typ}) FROM (SELECT NULL::{typ} WHERE false) _ (val);
SELECT sum(val::{typ}) FROM (VALUES (1), (null), (2), (5)) _ (val);
""".format(sfunc=sfunc, typ=typ, stype=stype))

        sfunc = "{typ}_avg_accum".format(typ=typ)
        stype = avg_trans_types[typ]
        write_sql_function(f_sql, sfunc, [stype, typ], stype)
        f_sql.write("CREATE AGGREGATE avg({typ}) (SFUNC = {sfunc}, STYPE = {stype}, FINALFUNC = int8_avg,"
                    " INITCOND = '{{0,0}}');\n\n"
                    .format(typ=typ, sfunc=sfunc, stype=stype))
        f_test_sql.write("""
SELECT avg(val::{typ}) FROM (SELECT NULL::{typ} WHERE false) _ (val);
SELECT avg(val::{typ}) FROM (VALUES (1), (null), (2), (5), (6)) _ (val);
""".format(typ=typ))

    op_fam_btree_elements = []
    op_fam_hash_elements = []

    for lefttype in new_types + old_types:
        f_test_sql.write("""
CREATE TABLE test_{typ} (x {typ});
CREATE UNIQUE INDEX test_{typ}_x_key ON test_{typ} USING btree (x);
INSERT INTO test_{typ} VALUES (1), (2), (3), (4), (5), (null);

SET enable_seqscan = off;
SET enable_bitmapscan = off;
""".format(typ=lefttype))

        for righttype in new_types + old_types:
            if lefttype in old_types and righttype in old_types:
                continue

            f_test_sql.write("""
EXPLAIN (COSTS OFF) SELECT * FROM test_{typ} WHERE x = 3::{typ2};
SELECT * FROM test_{typ} WHERE x = 3::{typ2};
""".format(typ=lefttype, typ2=righttype))

            if lefttype != righttype:
                op_fam_btree_elements.extend([s.format(type1=lefttype, type2=righttype) for s in [
                    "OPERATOR 1 <  ({type1}, {type2})",
                    "OPERATOR 2 <= ({type1}, {type2})",
                    "OPERATOR 3 =  ({type1}, {type2})",
                    "OPERATOR 4 >= ({type1}, {type2})",
                    "OPERATOR 5 >  ({type1}, {type2})",
                    "FUNCTION 1 bt{type1}{type2}cmp({type1}, {type2})",
                ]])
                op_fam_hash_elements.extend([s.format(type1=lefttype, type2=righttype) for s in [
                    "OPERATOR 1 = ({type1}, {type2})",
                ]])

        f_test_sql.write("""
RESET enable_seqscan;
RESET enable_bitmapscan;
""")

    f_sql.write("ALTER OPERATOR FAMILY integer_ops USING btree ADD\n" +
                ",\n".join(op_fam_btree_elements) +
                ";\n\n")
    f_sql.write("ALTER OPERATOR FAMILY integer_ops USING hash ADD\n" +
                ",\n".join(op_fam_hash_elements) +
                ";\n\n")

    # Unlike the other arithmetic operators, PostgreSQL supplies the %
    # operator only with same-type argument pairs and relies on type
    # promotion to support the other combinations.  Adding more
    # integer types breaks those cases, and the PostgreSQL regression
    # tests fail because of that.  We add the necessary remaining
    # cross-type operators to unbreak this.
    #
    # See also this discussion:
    # <http://www.postgresql.org/message-id/23982.1213723796@sss.pgh.pa.us>
    for lefttype, righttype in (('int2', 'int4'),
                                ('int4', 'int2'),
                                ('int8', 'int2'),
                                ('int8', 'int4')):
        write_arithmetic_op(f_c, f_sql, f_test_sql,
                            '%', lefttype, righttype)

    f_c.close()
    f_sql.close()
    f_test_sql.close()


if __name__ == '__main__':
    main(pgversion=float(sys.argv[1]))
