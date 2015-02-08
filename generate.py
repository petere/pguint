import re


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


def type_unsigned(typ):
    return typ.startswith('u')


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


def next_bigger_type(typ):
    m = re.match(r'(\w+)(\d+)', typ)
    return m.group(1) + str(int(m.group(2)) * 2)


f_operators_c = open('operators.c', 'w')
f_operators_sql = open('operators.sql', 'w')
f_test_operators_sql = open('test/sql/operators.sql', 'w')

f_operators_c.write('#include <postgres.h>\n')
f_operators_c.write('#include <fmgr.h>\n\n')
f_operators_c.write('#include "uint.h"\n\n')


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


def write_op_c_function(f, funcname, leftarg, rightarg, op, rettype, c_check='', intermediate_type=None):
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
    if intermediate_type:
        body += "result2 = "
    else:
        body += "result = "
    if leftarg:
        if intermediate_type:
            body += "({0})".format(c_types[intermediate_type])
        body += "arg1"
    body += " " + c_operator(op) + " "
    if rightarg:
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

    write_c_function(f, funcname, [leftarg, rightarg], rettype, body)


def write_sql_operator(f, funcname, leftarg, rightarg, op, rettype):
    sql_funcname = funcname
    if op == '%':
        # SQL standard requires a "mod" function rather than % operator
        sql_funcname = 'mod'
    write_sql_function(f, funcname, [leftarg, rightarg], rettype, sql_funcname=sql_funcname)

    f.write("CREATE OPERATOR {0} (\n".format(op))
    if leftarg:
        f.write("    LEFTARG = {0},\n".format(leftarg))
    if rightarg:
        f.write("    RIGHTARG = {0},\n".format(rightarg))
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


def write_cmp_c_function(f, leftarg, rightarg):
    funcname = 'bt' + coalesce(leftarg, '') + coalesce(rightarg, '') + 'cmp'
    write_c_function(f, funcname, [leftarg, rightarg], 'int4',
                     """if (arg1 > arg2)
\tresult = 1;
else if (arg1 == arg2)
\tresult = 0;
else
\tresult = -1;""")


def write_cmp_sql_function(f, leftarg, rightarg):
    funcname = 'bt' + coalesce(leftarg, '') + coalesce(rightarg, '') + 'cmp'
    write_sql_function(f, funcname, [leftarg, rightarg], 'integer')


def write_opclasses_sql(f, typ):
    f.write("""CREATE OPERATOR CLASS {typ}_ops
    DEFAULT FOR TYPE {typ} USING btree AS
        OPERATOR        1       < ,
        OPERATOR        2       <= ,
        OPERATOR        3       = ,
        OPERATOR        4       >= ,
        OPERATOR        5       > ,
        FUNCTION        1       bt{typ}{typ}cmp({typ}, {typ});

CREATE OPERATOR CLASS {typ}_ops
    DEFAULT FOR TYPE {typ} USING hash AS
        OPERATOR        1       =,
        FUNCTION        1       hash{typ}({typ});

""".format(typ=typ))


def coalesce(*args):
    return next((a for a in args if a is not None), None)


def write_code(f_c, f_sql, leftarg, rightarg, op, rettype, c_check='', intermediate_type=None):
    funcname = coalesce(leftarg, '') + coalesce(rightarg, '') + op_words[op]
    write_op_c_function(f_c, funcname, leftarg, rightarg, op, rettype, c_check, intermediate_type)
    write_sql_operator(f_sql, funcname, leftarg, rightarg, op, rettype)


for leftarg in new_types + old_types:
    for op in comparison_ops + arithmetic_ops:
        f_test_operators_sql.write("""\
SELECT '2'::{typ} {op} 5;
SELECT 2 {op} '5'::{typ};
SELECT '5'::{typ} {op} 2;
SELECT 5 {op} '2'::{typ};
""".format(typ=leftarg, op=op))
    for rightarg in new_types + old_types:
        if leftarg in old_types and rightarg in old_types:
            continue
        for op in comparison_ops:
            write_code(f_operators_c, f_operators_sql, leftarg, rightarg, op, rettype='boolean')
            f_test_operators_sql.write("""\
SELECT '1'::{lefttype} {op} '1'::{righttype};
SELECT '5'::{lefttype} {op} '2'::{righttype};
SELECT '3'::{lefttype} {op} '4'::{righttype};
""".format(lefttype=leftarg, op=op, righttype=rightarg))
        f_test_operators_sql.write("\n")

        write_cmp_c_function(f_operators_c, leftarg, rightarg)
        write_cmp_sql_function(f_operators_sql, leftarg, rightarg)
        f_test_operators_sql.write("""\
SELECT bt{lefttype}{righttype}cmp('1'::{lefttype}, '1'::{righttype});
SELECT bt{lefttype}{righttype}cmp('5'::{lefttype}, '2'::{righttype});
SELECT bt{lefttype}{righttype}cmp('3'::{lefttype}, '4'::{righttype});
""".format(lefttype=leftarg, righttype=rightarg))

        for op in arithmetic_ops:
            args = sorted([leftarg, rightarg], key=lambda x: (type_bits(x), type_unsigned(x)))
            rettype = args[-1]
            if type_unsigned(rettype):
                if op == '+':
                    c_check = 'result < arg1 || result < arg2'
                elif op == '-':
                    c_check = 'result > arg1'
                else:
                    c_check = ''
            else:
                if op == '+':
                    c_check = 'SAMESIGN(arg1, arg2) && !SAMESIGN(result, arg1)'
                elif op == '-':
                    c_check = '!SAMESIGN(arg1, arg2) && !SAMESIGN(result, arg1)'
                else:
                    c_check = ''
            if op == '*':
                if type_bits(rettype) < 64:
                    intermediate_type = next_bigger_type(rettype)
                    c_check = '({0}) result2 != result2'.format(c_types[rettype])
                elif type_unsigned(rettype):
                    c_check = '(arg1 != ((uint32) arg1) || arg2 != ((uint32) arg2))' \
                              ' && (arg2 != 0 && ((arg2 == -1 && arg1 < 0 && result < 0) || result / arg2 != arg1))'
                else:
                    c_check = '(arg1 != ((int32) arg1) || arg2 != ((int32) arg2))' \
                              ' && (arg2 != 0 && ((arg2 == -1 && arg1 < 0 && result < 0) || result / arg2 != arg1))'
            else:
                intermediate_type = None
            write_code(f_operators_c, f_operators_sql, leftarg, rightarg, op, rettype, c_check, intermediate_type)
            f_test_operators_sql.write("""\
SELECT pg_typeof('1'::{lefttype} {op} '1'::{righttype});
SELECT '1'::{lefttype} {op} '1'::{righttype};
SELECT '3'::{lefttype} {op} '4'::{righttype};
SELECT '5'::{lefttype} {op} '2'::{righttype};
""".format(lefttype=leftarg, op=op, righttype=rightarg))
            if op in ['+', '*']:
                f_test_operators_sql.write("SELECT '{max_left}'::{lefttype} {op} '{max_right}'::{righttype};\n"
                                           .format(lefttype=leftarg, op=op, righttype=rightarg,
                                                   max_left=max_values[leftarg],
                                                   max_right=max_values[rightarg]))
            if op in ['/', '%']:
                f_test_operators_sql.write("SELECT '5'::{lefttype} {op} '0'::{righttype};\n"
                                           .format(lefttype=leftarg, op=op, righttype=rightarg))
            if op in ['%']:
                f_test_operators_sql.write("SELECT mod('5'::{lefttype}, '2'::{righttype});\n"
                                           .format(lefttype=leftarg, righttype=rightarg))
        f_test_operators_sql.write("\n")

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

for arg in new_types:
    for op in ['&', '|', '#']:
        write_code(f_operators_c, f_operators_sql, leftarg=arg, rightarg=arg, op=op, rettype=arg)
        f_test_operators_sql.write("""\
SELECT '1'::{lefttype} {op} '1'::{righttype};
SELECT '5'::{lefttype} {op} '2'::{righttype};
SELECT '5'::{lefttype} {op} '4'::{righttype};
""".format(lefttype=arg, op=op, righttype=arg))
    for op in ['~']:
        write_code(f_operators_c, f_operators_sql, leftarg=None, rightarg=arg, op=op, rettype=arg)
        f_test_operators_sql.write("SELECT {op} '6'::{typ};\n".format(op=op, typ=arg))
    for op in ['<<', '>>']:
        write_code(f_operators_c, f_operators_sql, leftarg=arg, rightarg='int4', op=op, rettype=arg)
        f_test_operators_sql.write("""\
SELECT '6'::{typ} {op} 1;
SELECT '6'::{typ} {op} 3;
""".format(typ=arg, op=op))

    f_test_operators_sql.write("\n")

    write_opclasses_sql(f_operators_sql, arg)

    for agg, funcname, op in [('min', arg + "smaller", '<'),
                              ('max', arg + "larger", '>')]:
        write_c_function(f_operators_c, funcname, [arg]*2, arg,
                         body="result = (arg1 {op} arg2) ? arg1 : arg2;".format(op=op))
        write_sql_function(f_operators_sql, funcname, [arg]*2, arg)
        f_test_operators_sql.write("""\
SELECT {funcname}('1'::{typ}, '1'::{typ});
SELECT {funcname}('5'::{typ}, '2'::{typ});
SELECT {funcname}('3'::{typ}, '4'::{typ});
""".format(funcname=funcname, typ=arg))
        f_operators_sql.write("CREATE AGGREGATE {agg}({typ}) (SFUNC = {sfunc}, STYPE = {stype}, SORTOP = {sortop});\n\n"
                              .format(agg=agg, typ=arg, sfunc=funcname, stype=arg, sortop=op))
        f_test_operators_sql.write("SELECT {agg}(val::{typ}) FROM (VALUES (3), (5), (1), (4)) AS _ (val);\n\n"
                                   .format(agg=agg, typ=arg))

    for agg, funcname in [('bit_and', arg + arg + "and"),
                          ('bit_or', arg + arg + "or")]:
        f_operators_sql.write("CREATE AGGREGATE {agg}({typ}) (SFUNC = {sfunc}, STYPE = {stype});\n\n"
                              .format(agg=agg, typ=arg, sfunc=funcname, stype=arg))
    f_test_operators_sql.write("SELECT bit_and(val::{typ}) FROM (VALUES (3), (6), (18)) AS _ (val);\n\n"
                               .format(typ=arg))
    f_test_operators_sql.write("SELECT bit_or(val::{typ}) FROM (VALUES (9), (1), (4)) AS _ (val);\n\n"
                               .format(typ=arg))

    sfunc = "{argtype}_sum".format(argtype=arg)
    stype = sum_trans_types[arg]
    write_sql_function(f_operators_sql, sfunc, [stype, arg], stype, strict=False)
    f_operators_sql.write("CREATE AGGREGATE sum({arg}) (SFUNC = {sfunc}, STYPE = {stype});\n\n"
                          .format(arg=arg, sfunc=sfunc, stype=stype))
    f_test_operators_sql.write("""
SELECT {sfunc}(NULL::{stype}, NULL::{argtype});
SELECT {sfunc}(NULL::{stype}, 1::{argtype});
SELECT {sfunc}(2::{stype}, NULL::{argtype});
SELECT {sfunc}(2::{stype}, 1::{argtype});

SELECT sum(val::{argtype}) FROM (SELECT NULL::{argtype} WHERE false) _ (val);
SELECT sum(val::{argtype}) FROM (VALUES (1), (null), (2), (5)) _ (val);
""".format(sfunc=sfunc, argtype=arg, stype=stype))

    sfunc = "{argtype}_avg_accum".format(argtype=arg)
    stype = avg_trans_types[arg]
    write_sql_function(f_operators_sql, sfunc, [stype, arg], stype)
    f_operators_sql.write("CREATE AGGREGATE avg({arg}) (SFUNC = {sfunc}, STYPE = {stype}, FINALFUNC = int8_avg,"
                          " INITCOND = '{{0,0}}');\n\n"
                          .format(arg=arg, sfunc=sfunc, stype=stype))
    f_test_operators_sql.write("""
SELECT avg(val::{argtype}) FROM (SELECT NULL::{argtype} WHERE false) _ (val);
SELECT avg(val::{argtype}) FROM (VALUES (1), (null), (2), (5), (6)) _ (val);
""".format(sfunc=sfunc, argtype=arg, stype=stype))

# f_operators_sql.write("""
# CREATE OPERATOR FAMILY uinteger_ops USING btree;
# CREATE OPERATOR FAMILY uinteger_ops USING hash;
#
# """)

op_fam_btree_elements = []
op_fam_hash_elements = []

for lefttype in new_types + old_types:
    f_test_operators_sql.write("""
CREATE TABLE test_{typ} (x {typ});
CREATE UNIQUE INDEX test_{typ}_x_key ON test_{typ} USING btree (x);
INSERT INTO test_{typ} VALUES (1), (2), (3), (4), (5), (null);

SET enable_seqscan = off;
SET enable_bitmapscan = off;
""".format(typ=lefttype))

    for righttype in new_types + old_types:
        if lefttype in old_types and righttype in old_types:
            continue

        f_test_operators_sql.write("""
EXPLAIN (COSTS OFF) SELECT * FROM test_{typ} WHERE x = 3::{typ2};
SELECT * FROM test_{typ} WHERE x = 3;
""".format(typ=lefttype, typ2=righttype))

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
    op_fam_hash_elements.append("FUNCTION 1 hash{type1}({type1})".format(type1=lefttype))

    f_test_operators_sql.write("""
RESET enable_seqscan;
RESET enable_bitmapscan;
""")

# f_operators_sql.write("ALTER OPERATOR FAMILY uinteger_ops USING btree ADD\n"
#                       + ",\n".join(op_fam_btree_elements)
#                       + ";\n\n")
# f_operators_sql.write("ALTER OPERATOR FAMILY uinteger_ops USING hash ADD\n"
#                       + ",\n".join(op_fam_hash_elements)
#                       + ";\n\n")

f_operators_c.close()
f_operators_sql.close()
f_test_operators_sql.close()
