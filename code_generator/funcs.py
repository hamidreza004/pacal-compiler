from code_generator.helper import *
from errors import *

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
        func_code.append(str)


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
    print(index, var['array'])
    while True:
        line = str(var['type'])
        for j in range(0, len(var['array']) - i):
            line = "[" + str(var['array'][len(var['array']) - j - 1]) + " x " + line + "]"
        print(line, index)
        ic = index.pop()
        add_code(f"""%.tmp{diff_count} = load {ic['type']}, {ic['type']}* {ic['name']}, align {ic['align']}""")
        add_code(f"""%.tmp{diff_count + 1} = sext {ic['type']} %.tmp{diff_count} to i64""")
        if i == 0:
            add_code(f"""%.tmp{diff_count + 2} = getelementptr inbounds {line}, {line}* {var[
                'name']}, i64 0, i64 %.tmp{diff_count + 1}""")
        else:
            add_code(
                f"""%.tmp{diff_count + 2} = getelementptr inbounds {line}, {line}* %.tmp{diff_count - 1}, i64 0, i64 %.tmp{diff_count + 1}""")
        diff_count += 3
        i += 1
        if i == len(var['array']):
            break

    sem_stack.append(
        {"name": f"%.tmp{diff_count - 1}", "type": var['type'], "level": level, "align": variable_size[var['type']]})


def load_var(var):
    global diff_count
    add_code(f"%.tmp{diff_count} = load {var['type']}, {var['type']}* {var['name']}, align {var['align']}")


def store_var(var):
    global diff_count
    add_code(f"store {var['type']} %.tmp{diff_count}, {var['type']}* {var['name']}, align {var['align']}")


def cast(var, type):
    global diff_count
    if var['type'] == type:
        return
    add_code(f"%.tmp{diff_count} = {type_cast(var['type'], type)} {var['type']} {var['name']} to {type}")


def assign(_, sem_stack):
    global diff_count
    var_a = sem_stack.pop()
    var_b = sem_stack.pop()

    if var_a['level'] == 100:
        raise CodeGeneratorException()

    if level > 0:
        if var_a['type'] == 'i8*' and 'const' in var_a:
            add_code(f"""store i8* getelementptr inbounds ([{len(var_a['value']) + 1} x i8], [{len(
                var_a['value']) + 1} x i8]* {var_a['name']}, i32 0, i32 0), i8** {var_b['name']}, align 8""")
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

            global_code[line] = f"""{var_b['name']} = global i8* getelementptr inbounds ([{len(
                var_a['value'])} x i8], [{len(
                var_a['value'])} x i8]* {var_a['name']}, i32 0, i32 0), align 8"""

        diff_count += 1
        sem_stack.append(var_b)

    diff_count += 1


const_define = {}


def var_const(token):
    if token[0] == 'string':
        hsh = 77934516
        s = token[1]
        for ch in s:
            hsh = (hsh * 1812 + ord(ch)) % 182374277514
        return '@.const.' + str(hsh)
    else:
        return '@.const.' + str(token[1])


def const_push(token, sem_stack):
    var_name = var_const(token)
    var = {'name': var_name, 'type': variable_map[token[0]], 'align': variable_size[variable_map[token[0]]],
           'value': token[1]}
    if var_name not in const_define:
        if token[0] != "string":
            const_code.append(f"{var_name} = global {var['type']} {token[1]}, align {var['align']}")
        else:
            const_code.append(
                f"""{var_name} = private unnamed_addr constant [{len(token[1]) + 1} x i8] c"{token[1]}\\00", align 1""")

        const_define[var_name] = None
    var['level'] = 0
    var['const'] = True
    sem_stack.append(var)


def write(_, sem_stack):
    global diff_count
    var = sem_stack.pop()
    load_var(var)
    add_code(
        f""" call i32 (i8*, ...) @printf(i8* getelementptr inbounds ([5 x i8], [5 x i8]* @.w{var['type']}, i32 0, i32 
        0), {var['type']} %.tmp{diff_count}) """)
    diff_count += 1


def read(_, sem_stack):
    global diff_count
    var = sem_stack.pop()
    if var['type'] == 'i64':
        add_code(
            f"""call i32 (i8*, ...) @__isoc99_scanf(i8* getelementptr inbounds ([3 x i8], [3 x i8]* @.r{var[
                'type']}, i32 0, i32 0), {var['type']}* {var['name']})""")
    else:
        add_code(
            f"""call i32 (i8*, ...) @__isoc99_scanf(i8* getelementptr inbounds ([4 x i8], [4 x i8]* @.r{var[
                'type']}, i32 0, i32 0), {var['type']}* {var['name']})""")


def start_dec_func(_, sem_stack):
    global func_code
    global level
    global sym_table
    var = sem_stack.pop()
    sym_table[level][var['pre']] = {'args': [], 'name': var['pre'], 'level': 0, 'pre': var['pre']}
    var = sym_table[level][var['pre']]
    sym_table[level][var['pre']] = var
    sem_stack.append(len(func_code))
    func_code.append("")
    sem_stack.append(var)
    level += 1


def end_dec_func(token, sem_stack):
    global func_code
    global level
    func = sem_stack.pop()
    line = sem_stack.pop()
    print(func)
    print(token)
    code_line = f"define {variable_map[token]} @{func['name']}("
    first = True
    for arg in func['args']:
        if not first:
            code_line += ','
        code_line = code_line + arg['type']
        first = False
    code_line = code_line + ") {"
    func['type'] = variable_map[token]
    func_code[int(line)] = code_line
    level -= 1


def bracket_close(_, __):
    global func_code
    func_code.append('}')


def start_dec_proc(token, sem_stack):
    start_dec_func(token, sem_stack)


def end_dec_proc(_, sem_stack):
    global func_code
    global level
    func = sem_stack.pop()
    line = sem_stack.pop()
    code_line = f"define void @{func['name']}("
    first = True
    for arg in func['args']:
        if not first:
            code_line += ','
        code_line = code_line + arg['type']
        first = False
    code_line = code_line + ") {"
    func_code[int(line)] = code_line
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


def start_access_prod(_, sem_stack):
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
        def_arg = func['args'][ind]
        if def_arg['type'] != arg['type']:
            cast(arg, def_arg['type'])
            code_line = "," + def_arg['type'] + " " + f"%.tmp{diff_count}"
            diff_count += 1
        else:
            code_line = "," + def_arg['type'] + " " + arg['name']
        ind += 1

    code_line = code_line[1:]
    code_line = f"""%.tmp{diff_count} = call {func['type']} {func['name']}({code_line})"""
    sem_stack.append(
        {'level': level, 'name': f'%.tmp{diff_count}', 'type': func['type'], 'align': variable_size[func['type']]})
    diff_count += 1
    add_code(code_line)


def return_value(_, sem_stack):
    var = sem_stack.pop()
    add_code(f"ret {var['type']} {var['name']}")
