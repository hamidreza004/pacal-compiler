from code_generator.helper import *

global_code = []
func_code = []
const_code = []
diff_count = 0
level = 1


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
    global level, func_code, global_code
    var = sem_stack.pop()
    var['type'] = variable_map[token]
    var['align'] = variable_size[var['type']]
    if level > 0:
        var['line_dec'] = len(func_code)
        var['name'] = '%' + var['name']
        add_code(f"{var['name']} = alloca {var['type']}, align {var['align']}")
    else:
        var['line_dec'] = len(global_code)
        var['name'] = '@' + var['name']
        add_code(
            f"{var['name']} = common global {var['type']} {variable_default[var['type']]}, align {var['align']}")
    sem_stack.append(var)


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

    if level > 0:
        if var_a['type'] == 'i8*' and 'const' in var_a:
            add_code(f"""store i8* getelementptr inbounds ([{len(var_a['value']) + 1} x i8], [{len(
                var_a['value']) + 1} x i8]* {var_a['name']}, i32 0, i32 0), i8** {var_b['name']}, align 8""")
        else:
            load_var(var_a)

            if var_b['type'] != var_a['type']:
                tmp_var = {'name': f'.tmp{diff_count}', 'type': var_a['type'], 'align': var_a['align']}
                diff_count += 1
                cast(tmp_var, var_b['type'])
            store_var(var_b)
        sem_stack.append(var_b)
    else:
        line = var_b['line_dec']
        if var_b['type'] != 'i8*':
            global_code[line] = f"""{var_b['name']} = common global {var_b['type']} {variable_cast_func[var_b['type']](
                var_a['value'])}, align {var_b['align']}"""
        else:

            global_code[line] = f"""{var_b['name']} = global i8* getelementptr inbounds ([{len(
                var_a['value'])} x i8], [{len(
                var_a['value'])} x i8]* {var_a['name']}, i32 0, i32 0), align 8"""

        diff_count += 1
        sem_stack.append(var_b)


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
                f"""{var_name} = private unnamed_addr constant [{len(token[1]) + 1} x i8] c"{token[1]}\00", align 1""")

        const_define[var_name] = None
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
