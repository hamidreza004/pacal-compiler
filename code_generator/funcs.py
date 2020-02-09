from code_generator.helper import *
from errors import *
import struct

sym_table = None
global_code = []
func_code = []
const_code = []
diff_count = 0
level = 0


def initiate(sym):
    global sym_table
    sym_table = sym


def push(token, sem_stack):
    sem_stack.append(token)


def pop(__, sem_stack):
    sem_stack.pop()


def add_code(str):
    if level == 0:
        global_code.append(str)
    else:
        tabs = '\t' * level
        func_code.append(tabs + str)


def declare_var_and_push(token, sem_stack):
    global level, func_code, global_code, diff_count
    var = sem_stack.pop()
    pre = var['pre']
    if level == var['level']:
        raise CodeGeneratorException(DOUBLE_DECLARE)
    sym_table[level][pre] = {'name': pre + "." + str(level) + "." + str(diff_count), 'pre': pre, 'level': level}
    var = sym_table[level][pre]
    var['type'] = variable_map[token]
    var['align'] = variable_size[var['type']]
    var['level'] = level
    if var['type'] == 'i8*':
        var['array'] = [10000, ]
        var['len'] = 10000
    diff_count += 1

    if level > 0:
        var['line_dec'] = len(func_code)
        var['name'] = '%' + var['name']
        add_code(f"{var['name']} = alloca {var['type']}, align {var['align']}")
    else:
        var['line_dec'] = len(global_code)
        var['name'] = '@' + var['name']
        add_code(
            f"{var['name']} = global {var['type']} {variable_default[var['type']]}, align {var['align']}")
    sem_stack.append(var)


def start_dec_array(_, sem_stack):
    global diff_count
    var = sem_stack.pop()
    pre = var['pre']
    if level == var['level']:
        raise CodeGeneratorException(DOUBLE_DECLARE)
    sym_table[level][pre] = {'name': pre + "." + str(level) + "." + str(diff_count), 'pre': pre, 'level': level}
    diff_count += 1
    var = sym_table[level][pre]
    sem_stack.append(var)
    sem_stack.append("#")


def end_dec_array_and_push(token, sem_stack):
    type = variable_map[token]
    line = str(type)
    tmp_list = []
    while True:
        ic = sem_stack.pop()
        if ic == '#':
            break
        if ic[0] != "integer":
            raise CodeGeneratorException(ARRAY_DIM_INTEGER)
        tmp_list.append(ic[1])
        line = "[" + str(ic[1]) + " x " + line + "]"
    var = sem_stack.pop()
    var['array'] = []
    for i in range(len(tmp_list)):
        var['array'].append(tmp_list[len(tmp_list) - i - 1])
    var['type'] = type
    var['align'] = variable_size[var['type']]
    if level > 0:
        var['name'] = '%' + var['name']
        add_code(f"""{var['name']} = alloca {line}, align 16""")
    else:
        var['name'] = '@' + var['name']
        add_code(f"""{var['name']} = common global {line} zeroinitializer, align 16""")
    sem_stack.append(var)


def start_access_array(_, sem_stack):
    var = sem_stack.pop()
    if 'array' not in var:
        raise CodeGeneratorException(NOT_ARRAY)
    sem_stack.append(var)
    sem_stack.append("#")


def end_access_array(_, sem_stack):
    global diff_count
    index = []
    while True:
        ic = sem_stack.pop()
        if ic == '#':
            break
        if ic['type'] != "i32":
            raise CodeGeneratorException(ARRAY_DIM_INTEGER)
        index.append(ic)
    var = sem_stack.pop()
    i = 0
    print(index, var)
    while True:
        line = str(var['type'])
        for j in range(0, len(var['array']) - i):
            line = "[" + str(var['array'][len(var['array']) - j - 1]) + " x " + line + "]"
        ic = index.pop()
        add_code(f"""%.tmp{diff_count} = load {ic['type']}, {ic['type']}* {ic['name']}, align {ic['align']}""")
        add_code(f"""%.tmp{diff_count + 1} = sext {ic['type']} %.tmp{diff_count} to i64""")
        if i == 0:
            if 'len' not in var:
                add_code(f"""%.tmp{diff_count + 2} = getelementptr inbounds {line}, {line}* {var[
                    'name']}, i64 0, i64 %.tmp{diff_count + 1}""")
            else:
                add_code(f"""%.tmp{diff_count + 3} = load i8*, i8** {var['name']}, align 8""")
                add_code(
                    f"""%.tmp{diff_count + 2} = getelementptr inbounds i8, i8* %.tmp{diff_count + 3}, i64 %.tmp{diff_count + 1}""")
        else:
            add_code(
                f"""%.tmp{diff_count + 2} = getelementptr inbounds {line}, {line}* %.tmp{diff_count - 1}, i64 0, i64 %.tmp{diff_count + 1}""")
        diff_count += 3
        i += 1
        if i == len(var['array']):
            break

    sem_stack.append(
        {"name": f"%.tmp{diff_count - 1}", "type": var['type'] if var['type'] != 'i8*' else 'i8', "level": level,
         "align": variable_size[var['type']]})

    diff_count += 1


def load_var(var):
    global diff_count
    if var['type'] != 'i8*' or 'const' not in var:
        add_code(f"%.tmp{diff_count} = load {var['type']}, {var['type']}* {var['name']}, align {var['align']}")
    else:
        add_code(f"""%.tmp{diff_count} = alloca i8*, align 8""")
        add_code(f"""store i8* getelementptr inbounds ([{var['len'] + 1} x i8], [{var['len'] + 1} x i8]* {var[
            'name']}, i32 0, i32 0), i8** %.tmp{diff_count}, align 8""")
        add_code(f"""%.tmp{diff_count + 1} = load i8*, i8** %.tmp{diff_count}, align 8""")
        diff_count += 1


def store_var(var):
    global diff_count
    add_code(f"store {var['type']} %.tmp{diff_count}, {var['type']}* {var['name']}, align {var['align']}")


def un_pointer(var):
    global diff_count
    add_code(f"%.tmp{diff_count} = alloca {var['type']}, align {var['align']}")
    add_code(f"store {var['type']} {var['name']}, {var['type']}* %.tmp{diff_count}, align {var['align']}")


def cast(var, type):
    global diff_count
    if var['type'] == type:
        return
    if type != 'i1':
        add_code(f"%.tmp{diff_count} = {type_cast(var['type'], type)} {var['type']} {var['name']} to {type}")
    else:
        if var['type'] != 'float':
            add_code(f"""%.tmp{diff_count} = icmp ne {var['type']} {var['name']}, {variable_default[var['type']]}""")
        else:
            add_code(f"""%.tmp{diff_count} = fcmp une {var['type']} {var['name']}, {variable_default[var['type']]}""")


def assign(_, sem_stack):
    global diff_count
    var_a = sem_stack.pop()
    var_b = sem_stack.pop()

    if var_a['level'] == 100:
        raise CodeGeneratorException()

    if level > 0:
        if var_a['type'] == 'i8*' and 'const' in var_a:
            var_b['len'] = var_a['len']
            var_b['array'] = var_a['array']
            add_code(f"""store i8* getelementptr inbounds ([{var_a['len'] + 1} x i8], [{var_a['len'] + 1} x i8]* {var_a[
                'name']}, i32 0, i32 0), i8** {var_b['name']}, align 8""")
        else:
            load_var(var_a)

            if var_b['type'] != var_a['type']:
                tmp_var = {'name': f'%.tmp{diff_count}', 'type': var_a['type'], 'align': var_a['align']}
                diff_count += 1
                cast(tmp_var, var_b['type'])
            store_var(var_b)
        sem_stack.append(var_b)
    else:
        line = var_b['line_dec']
        if var_b['type'] != 'i8*':
            value = var_a['value']
            if var_a['type'] == 'i8':
                value = ord(value)
            global_code[line] = f"""{var_b['name']} = global {var_b['type']} {variable_cast_func[var_b['type']](
                value)}, align {var_b['align']}"""
        else:
            var_b['len'] = var_a['len']
            var_b['array'] = var_a['array']
            global_code[line] = f"""{var_b['name']} = global i8* getelementptr inbounds ([{var_a['len'] + 1} x i8], [{
            var_a['len'] + 1} x i8]* {var_a['name']}, i32 0, i32 0), align 8"""

        diff_count += 1
        sem_stack.append(var_b)

    diff_count += 1


def assign_and_pop(token, sem_stack):
    assign(token, sem_stack)
    pop(token, sem_stack)


const_define = {}


def var_const(token):
    if token[0] == 'string':
        hsh = 77934516
        s = token[1]
        for ch in s:
            hsh = (hsh * 1812 + ord(ch)) % 182374277514
        return '@.const.' + token[0] + '.' + str(hsh)
    else:
        return '@.const.' + token[0] + '.' + str(token[1])


def float_to_hex(token):
    if token != 0:
        return hex(struct.unpack("Q", struct.pack("d", float(token)))[0])[:-8] + '0' * 8
    else:
        return '0.0'


def const_push(token, sem_stack):
    var_name = var_const(token)
    var = {'name': var_name, 'type': variable_map[token[0]], 'align': variable_size[variable_map[token[0]]],
           'value': token[1]}
    dic_sym = {
        '\\n': '\\0A',
        '\\f': '\\0C',
        '\\r': '\\0D',
        '\\v': '\\0B',
        '\\t': '\\09'
    }
    if var_name not in const_define:
        if token[0] != "string":
            if token[0] != "real":
                if token[0] != 'character':
                    const_code.append(f"{var_name} = global {var['type']} {token[1]}, align {var['align']}")
                else:
                    const_code.append(f"{var_name} = global {var['type']} {ord(str(token[1]))}, align {var['align']}")
            else:
                const_code.append(
                    f"""{var_name} = global {var['type']} {str(float_to_hex(token[1]))}, align {var[
                        'align']}""")
        else:
            n = 0
            var['len'] = len(token[1])
            var['value'] = token[1]
            for key in dic_sym:
                n += token[1].count(key)
                var['value'] = var['value'].replace(key, dic_sym[key])
            var['len'] -= n
            var['array'] = [var['len'], ]
            const_code.append(
                f"""{var_name} = private unnamed_addr constant [{var['len'] + 1} x i8] c"{var[
                    'value']}\\00", align 1""")

        const_define[var_name] = var
    var = const_define[var_name]
    var['level'] = 0
    var['const'] = True
    sem_stack.append(var)


def write(_, sem_stack):
    global diff_count
    var = sem_stack.pop()
    load_var(var)
    if var['type'] == 'i64':
        add_code(f"""call i32 (i8*, ...) @printf(i8* getelementptr inbounds ([4 x i8], [4 x i8]* @.w{var['type'] if var[
                                                                                                                        'type'] != 'i8*' else "string"}, i32 0, i32 0), {
        var['type']} %.tmp{diff_count}) """)
    else:
        if var['type'] != 'float':
            add_code(
                f"""call i32 (i8*, ...) @printf(i8* getelementptr inbounds ([3 x i8], [3 x i8]* @.w{var['type'] if var[
                                                                                                                       'type'] != 'i8*' else "string"}, i32 0, i32 0), {
                var['type']} %.tmp{diff_count}) """)
        else:
            add_code(f"%.tmp{diff_count + 1} = fpext float %.tmp{diff_count} to double")
            diff_count += 1
            add_code(
                f"""call i32 (i8*, ...) @printf(i8* getelementptr inbounds ([3 x i8], [3 x i8]* @.w{var['type'] if var[
                                                                                                                       'type'] != 'i8*' else "string"}, i32 0, i32 0), double %.tmp{diff_count}) """)
    diff_count += 1


def read(_, sem_stack):
    global diff_count
    var = sem_stack.pop()
    if var['type'] == 'i64':
        add_code(
            f"""call i32 (i8*, ...) @__isoc99_scanf(i8* getelementptr inbounds ([4 x i8], [4 x i8]* @.r{var['type'] if
            var['type'] != 'i8*' else "string"}, i32 0, i32 0), {var['type']}* {var['name']})""")
    else:
        if var['type'] != 'i8*':
            add_code(f"""call i32 (i8*, ...) @__isoc99_scanf(i8* getelementptr inbounds ([3 x i8], [3 x i8]* @.r{var[
                'type'] if var['type'] != 'i8*' else "string"}, i32 0, i32 0), {var['type']}* {var['name']})""")
        else:
            add_code(f"""%.tmp{diff_count} = load i8*, i8** {var['name']}, align 8""")
            add_code(f"""call i32 (i8*, ...) @__isoc99_scanf(i8* getelementptr inbounds ([3 x i8], [3 x i8]* @.r{var[
                'type'] if var['type'] != 'i8*' else "string"}, i32 0, i32 0), i8* %.tmp{diff_count})""")
            diff_count += 1


glob_func = None


def start_dec_func(_, sem_stack):
    global func_code
    global level
    global sym_table
    var = sem_stack.pop()
    sym_table[level][var['pre']] = {'args': [], 'name': '@' + var['pre'], 'level': 0, 'pre': var['pre']}
    var = sym_table[level][var['pre']]
    sym_table[level][var['pre']] = var
    sem_stack.append(len(func_code))
    func_code.append("")
    sem_stack.append(var)
    level += 1


def end_dec_func(token, sem_stack):
    global func_code
    global level
    global glob_func
    func = sem_stack.pop()
    line = sem_stack.pop()
    code_line = f"define {variable_map[token]} {func['name']}("
    first = True
    for arg in func['args']:
        if not first:
            code_line += ','
        code_line = code_line + arg['type']
        first = False
    code_line = code_line + ") {"
    func['type'] = variable_map[token]
    func_code[int(line)] = code_line
    sem_stack.append(func)
    glob_func = func
    level -= 1


def bracket_close(_, sem_stack):
    global func_code
    func = sem_stack.pop()
    if 'type' not in func:
        func_code.append('ret void')
    else:
        if func['type'] == 'i8*':
            const_push(('string', ""), sem_stack)
            func_code.append(
                f"""ret i8* getelementptr inbounds ([1 x i8], [1 x i8]* {sem_stack.pop()['name']}, i32 0, i32 0) """)
        else:
            func_code.append(f"""ret {func['type']} {variable_default[func['type']]}""")
    func_code.append('}')


def start_dec_proc(token, sem_stack):
    start_dec_func(token, sem_stack)


def end_dec_proc(_, sem_stack):
    global func_code
    global level
    global glob_func
    func = sem_stack.pop()
    line = sem_stack.pop()
    code_line = f"define void {func['name']}("
    first = True
    for arg in func['args']:
        if not first:
            code_line += ','
        code_line = code_line + arg['type']
        first = False
    code_line = code_line + ") {"
    func_code[int(line)] = code_line
    sem_stack.append(func)
    glob_func = func
    level -= 1


def declare_var_and_push_and_store(token, sem_stack):
    declare_var_and_push(token, sem_stack)
    arg = sem_stack.pop()
    func = sem_stack.pop()
    num_inp = len(func['args'])
    add_code(f"""store {arg['type']} %{num_inp}, {arg['type']}* {arg['name']}, align {arg['align']}""")
    func['args'].append(arg)
    sem_stack.append(func)


def enter_block(_, __):
    global level
    level += 1


def out_block(_, __):
    global level
    sym_table[level].clear()
    level -= 1


def start_access_func(_, sem_stack):
    sem_stack.append("#")
    pass


def start_access_proc(_, sem_stack):
    start_access_func(_, sem_stack)


def end_access_func(_, sem_stack):
    global diff_count
    code_line = ""
    inp_args = []
    while True:
        arg = sem_stack.pop()
        if arg == "#":
            break
        inp_args.append(arg)
    func = sem_stack.pop()
    ind = 0
    for arg in inp_args:
        def_arg = func['args'][len(inp_args) - ind - 1]
        if def_arg['type'] != arg['type']:
            add_code(f"%.tmp{diff_count} = load {arg['type']}, {arg['type']}* {arg['name']}, align {arg['align']}")
            new_var = {'name': f'%.tmp{diff_count}', 'type': arg['type'], 'align': arg['align']}
            diff_count += 1
            cast(new_var, def_arg['type'])
            code_line = "," + def_arg['type'] + " " + f"%.tmp{diff_count}" + code_line
            diff_count += 1
        else:
            load_var(arg)
            code_line = "," + def_arg['type'] + " " + f"%.tmp{diff_count}" + code_line
            diff_count += 1
        ind += 1

    code_line = code_line[1:]
    code_line = f"""%.tmp{diff_count} = call {func['type']} {func['name']}({code_line})"""
    add_code(code_line)
    ret_var = {'level': level, 'name': f'%.tmp{diff_count}', 'type': func['type'], 'align': variable_size[func['type']]}
    diff_count += 1
    un_pointer(ret_var)
    sem_stack.append(
        {'level': level, 'name': f'%.tmp{diff_count}', 'type': func['type'], 'align': variable_size[func['type']]})
    diff_count += 1


def end_access_proc(_, sem_stack):
    global diff_count
    code_line = ""
    inp_args = []
    while True:
        arg = sem_stack.pop()
        if arg == "#":
            break
        inp_args.append(arg)
    func = sem_stack.pop()
    if 'type' in func:
        sem_stack.append(func)
        sem_stack.append("#")
        for arg in reversed(inp_args):
            sem_stack.append(arg)
        end_access_func(_, sem_stack)
        sem_stack.pop()
        return
    ind = 0
    for arg in inp_args:
        def_arg = func['args'][len(inp_args) - ind - 1]
        if def_arg['type'] != arg['type']:
            add_code(f"%.tmp{diff_count} = load {arg['type']}, {arg['type']}* {arg['name']}, align {arg['align']}")
            new_var = {'name': f'%.tmp{diff_count}', 'type': arg['type'], 'align': arg['align']}
            diff_count += 1
            cast(new_var, def_arg['type'])
            code_line = "," + def_arg['type'] + " " + f"%.tmp{diff_count}" + code_line
            diff_count += 1
        else:
            load_var(arg)
            code_line = "," + def_arg['type'] + " " + f"%.tmp{diff_count}" + code_line
            diff_count += 1
        ind += 1

    code_line = code_line[1:]
    code_line = f"""call void {func['name']}({code_line})"""
    add_code(code_line)


def return_value(_, sem_stack):
    global diff_count, glob_func
    var = sem_stack.pop()
    func = sem_stack.pop()
    sem_stack.append(func)
    func = glob_func
    print(func)
    print(var, func)
    if var['type'] != func['type']:
        add_code(f"%.tmp{diff_count} = load {var['type']}, {var['type']}* {var['name']}, align {var['align']}")
        new_var = {'name': f'%.tmp{diff_count}', 'type': var['type'], 'align': var['align']}
        diff_count += 1
        cast(new_var, func['type'])
        add_code(f"ret {func['type']} %.tmp{diff_count}")
        diff_count += 1
    else:
        if var['type'] == 'i8*' and 'const' in var:
            tmp = diff_count
            add_code(f"""%.tmp{tmp} = alloca i8*, align 8""")
            sem_stack.append({'name': f"%.tmp{tmp}", 'level': level, 'type': 'i8*', 'align': 8})
            sem_stack.append(var)
            assign(_, sem_stack)
            sem_stack.pop()
            add_code(f"%.tmp{diff_count} = load i8*, i8** %.tmp{tmp}, align 8")
            add_code(f"ret {var['type']} %.tmp{diff_count}")
            diff_count += 1
        else:
            add_code(f"%.tmp{diff_count} = load {var['type']}, {var['type']}* {var['name']}, align {var['align']}")
            add_code(f"ret {var['type']} %.tmp{diff_count}")
            diff_count += 1


###### EXPRESION :
def multiple_expr_command(sem_stack, var_a, var_b, type, command):
    global diff_count, level
    load_var(var_a)
    if var_a['type'] != type:
        diff_count += 1
        cast({'name': f'%.tmp{diff_count - 1}', 'type': var_a['type'], 'align': var_a['type']}, type)
    aa = diff_count
    diff_count += 1
    load_var(var_b)
    if var_b['type'] != type:
        diff_count += 1
        cast({'name': f'%.tmp{diff_count - 1}', 'type': var_b['type'], 'align': var_b['type']}, type)
    bb = diff_count
    diff_count += 1
    add_code(f"%.tmp{diff_count} = {command} {type} %.tmp{aa}, %.tmp{bb}")
    diff_count += 1
    un_pointer({'name': f'%.tmp{diff_count - 1}', 'type': type, 'align': variable_size[type], 'level': level})
    sem_stack.append({'name': f'%.tmp{diff_count}', 'type': type, 'align': variable_size[type], 'level': level})
    diff_count += 1


def logical_or(_, sem_stack):
    var_b = sem_stack.pop()
    var_a = sem_stack.pop()
    multiple_expr_command(sem_stack, var_a, var_b, 'i1', 'or')


def logical_and(_, sem_stack):
    var_b = sem_stack.pop()
    var_a = sem_stack.pop()
    multiple_expr_command(sem_stack, var_a, var_b, 'i1', 'and')


def bitwise_cast(type_a, type_b):
    if type_a == 'i64' or type_b == 'i64':
        type = 'i64'
    elif type_a == 'i32' or type_b == 'i32':
        type = 'i32'
    elif type_a == 'i8' or type_b == 'i8':
        type = 'i8'
    elif type_a == 'i1' or type_b == 'i1':
        type = 'i1'
    else:
        type = 'i32'
    return type


def logical_xor(_, sem_stack):
    var_b = sem_stack.pop()
    var_a = sem_stack.pop()
    multiple_expr_command(sem_stack, var_a, var_b, 'i1', 'xor')


def bitwise_or(_, sem_stack):
    var_b = sem_stack.pop()
    var_a = sem_stack.pop()
    multiple_expr_command(sem_stack, var_a, var_b, bitwise_cast(var_a['type'], var_b['type']), 'or')


def bitwise_xor(_, sem_stack):
    var_b = sem_stack.pop()
    var_a = sem_stack.pop()
    multiple_expr_command(sem_stack, var_a, var_b, bitwise_cast(var_a['type'], var_b['type']), 'xor')


def bitwise_and(_, sem_stack):
    var_b = sem_stack.pop()
    var_a = sem_stack.pop()
    multiple_expr_command(sem_stack, var_a, var_b, bitwise_cast(var_a['type'], var_b['type']), 'and')


def arithmetic_cast(type_a, type_b):
    if type_a == 'float' or type_b == 'float':
        type = 'float'
    elif type_a == 'i64' or type_b == 'i64':
        type = 'i64'
    elif type_a == 'i32' or type_b == 'i32':
        type = 'i32'
    elif type_a == 'i8' or type_b == 'i8':
        type = 'i8'
    elif type_a == 'i1' or type_b == 'i1':
        type = 'i1'
    else:
        type = 'i32'
    return type


def multiple_comparator_command(sem_stack, var_a, var_b, type, command):
    global diff_count, level
    load_var(var_a)
    if var_a['type'] != type:
        diff_count += 1
        cast({'name': f'%.tmp{diff_count - 1}', 'type': var_a['type'], 'align': var_a['type']}, type)
    aa = diff_count
    diff_count += 1
    load_var(var_b)
    if var_b['type'] != type:
        diff_count += 1
        cast({'name': f'%.tmp{diff_count - 1}', 'type': var_b['type'], 'align': var_b['type']}, type)
    bb = diff_count
    diff_count += 1
    add_code(f"%.tmp{diff_count} = {command} {type} %.tmp{aa}, %.tmp{bb}")
    diff_count += 1
    un_pointer({'name': f'%.tmp{diff_count - 1}', 'type': 'i1', 'align': variable_size[type], 'level': level})
    sem_stack.append({'name': f'%.tmp{diff_count}', 'type': 'i1', 'align': variable_size[type], 'level': level})
    diff_count += 1


def equal(_, sem_stack):
    var_b = sem_stack.pop()
    var_a = sem_stack.pop()
    type = arithmetic_cast(var_a['type'], var_b['type'])
    if type == "float":
        multiple_comparator_command(sem_stack, var_a, var_b, type, 'fcmp oeq')
    else:
        multiple_comparator_command(sem_stack, var_a, var_b, type, 'icmp eq')


def not_equal(_, sem_stack):
    var_b = sem_stack.pop()
    var_a = sem_stack.pop()
    type = arithmetic_cast(var_a['type'], var_b['type'])
    if type == "float":
        multiple_comparator_command(sem_stack, var_a, var_b, type, 'fcmp une')
    else:
        multiple_comparator_command(sem_stack, var_a, var_b, type, 'icmp ne')


def greater(_, sem_stack):
    var_b = sem_stack.pop()
    var_a = sem_stack.pop()
    type = arithmetic_cast(var_a['type'], var_b['type'])
    if type == "float":
        multiple_comparator_command(sem_stack, var_a, var_b, type, 'fcmp ogt')
    else:
        multiple_comparator_command(sem_stack, var_a, var_b, type, 'icmp sgt')


def less(_, sem_stack):
    var_b = sem_stack.pop()
    var_a = sem_stack.pop()
    type = arithmetic_cast(var_a['type'], var_b['type'])
    if type == "float":
        multiple_comparator_command(sem_stack, var_a, var_b, type, 'fcmp olt')
    else:
        multiple_comparator_command(sem_stack, var_a, var_b, type, 'icmp slt')


def greater_equal(_, sem_stack):
    var_b = sem_stack.pop()
    var_a = sem_stack.pop()
    type = arithmetic_cast(var_a['type'], var_b['type'])
    if type == "float":
        multiple_comparator_command(sem_stack, var_a, var_b, type, 'fcmp oge')
    else:
        multiple_comparator_command(sem_stack, var_a, var_b, type, 'icmp sge')


def less_equal(_, sem_stack):
    var_b = sem_stack.pop()
    var_a = sem_stack.pop()
    type = arithmetic_cast(var_a['type'], var_b['type'])
    if type == "float":
        multiple_comparator_command(sem_stack, var_a, var_b, type, 'fcmp ole')
    else:
        multiple_comparator_command(sem_stack, var_a, var_b, type, 'icmp sle')


def add(_, sem_stack):
    var_b = sem_stack.pop()
    var_a = sem_stack.pop()
    type = arithmetic_cast(var_a['type'], var_b['type'])
    if type == "float":
        multiple_expr_command(sem_stack, var_a, var_b, type, 'fadd')
    else:
        multiple_expr_command(sem_stack, var_a, var_b, type, 'add')


def div(_, sem_stack):
    var_b = sem_stack.pop()
    var_a = sem_stack.pop()
    type = arithmetic_cast(var_a['type'], var_b['type'])
    if type == "float":
        multiple_expr_command(sem_stack, var_a, var_b, type, 'fdiv')
    else:
        multiple_expr_command(sem_stack, var_a, var_b, type, 'sdiv')


def mul(_, sem_stack):
    var_b = sem_stack.pop()
    var_a = sem_stack.pop()
    type = arithmetic_cast(var_a['type'], var_b['type'])
    if type == "float":
        multiple_expr_command(sem_stack, var_a, var_b, type, 'fmul')
    else:
        multiple_expr_command(sem_stack, var_a, var_b, type, 'mul')


def minus(_, sem_stack):
    var_b = sem_stack.pop()
    var_a = sem_stack.pop()
    type = arithmetic_cast(var_a['type'], var_b['type'])
    if type == "float":
        multiple_expr_command(sem_stack, var_a, var_b, type, 'fsub')
    else:
        multiple_expr_command(sem_stack, var_a, var_b, type, 'sub')


def mod(_, sem_stack):
    var_b = sem_stack.pop()
    var_a = sem_stack.pop()
    type = bitwise_cast(var_a['type'], var_b['type'])
    multiple_expr_command(sem_stack, var_a, var_b, type, 'srem')


def neg(token, sem_stack):
    var = sem_stack.pop()
    const_push(('integer', 0), sem_stack)
    sem_stack.append(var)
    minus(token, sem_stack)


def tilda(token, sem_stack):
    var = sem_stack.pop()
    const_push(('boolean', 1), sem_stack)
    sem_stack.append(var)
    logical_xor(token, sem_stack)


def start_bulk_var(_, sem_stack):
    sem_stack.append('#')


def start_bulk_value(_, sem_stack):
    sem_stack.append('#')


def end_bulk_value(_, sem_stack):
    values = []
    vars = []
    while True:
        var = sem_stack.pop()
        if var == "#":
            break
        values.append(var)
    while True:
        var = sem_stack.pop()
        if var == "#":
            break
        vars.append(var)
    if len(vars) != len(values):
        raise CodeGeneratorException(BULK_EQUAL_NUMBER)

    for i in range(len(vars)):
        sem_stack.append(vars[len(vars) - i - 1])
        sem_stack.append(values[len(vars) - i - 1])
        assign(_, sem_stack)
        sem_stack.pop()


def check_condition_jump_if(_, sem_stack):
    global diff_count
    var = sem_stack.pop()
    if var['type'] != 'i1':
        load_var(var)
        diff_count += 1
        cast({"name": f"%.tmp{diff_count - 1}", "type": var['type'], 'align': var['align'], 'level': level}, 'i1')
    else:
        load_var(var)
    add_code(f"""br i1 %.tmp{diff_count}, label %.lbl{diff_count + 1}, label %.lbl{diff_count + 2}""")
    sem_stack.append(diff_count + 2)
    add_code(f""".lbl{diff_count + 1}:""")
    diff_count += 3


def endjump_else(_, sem_stack):
    global diff_count
    label = sem_stack.pop()
    add_code(f"""br label %.lbl{diff_count}""")
    sem_stack.append(diff_count)
    diff_count += 1
    add_code(f""".lbl{label}:""")


def set_endif(_, sem_stack):
    global diff_count
    label = sem_stack.pop()
    add_code(f"""br label %.lbl{label}""")
    add_code(f""".lbl{label}:""")


def start_while_push(_, sem_stack):
    global diff_count
    sem_stack.append(diff_count)
    add_code(f"""br label %.lbl{diff_count}""")
    add_code(f""".lbl{diff_count}:""")
    diff_count += 1


def check_condition_jump_while(_, sem_stack):
    check_condition_jump_if(_, sem_stack)


def jump_and_complete_jump(_, sem_stack):
    tmp = sem_stack.pop()
    label = sem_stack.pop()
    add_code(f"""br label %.lbl{label}""")
    sem_stack.append(tmp)
    endjump_else(_, sem_stack)
    set_endif(_, sem_stack)
