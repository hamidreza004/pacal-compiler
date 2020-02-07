from code_generator.helper import *

diff_count = 0
level = 0


def push(_, token, sem_stack):
    sem_stack.append(token)


def pop(_, __, sem_stack):
    sem_stack.pop()


def declare_var_and_push(code, token, sem_stack):
    global level
    var = sem_stack.pop()
    var['type'] = variable_map[token]
    var['align'] = variable_size[var['type']]
    if level > 0:
        var['name'] = '%' + var['name']
        code.append(f"{var['name']} = alloca {var['type']}, align {var['align']}")
    else:
        var['name'] = '@' + var['name']
        code.append(
            f"{var['name']} = common global {var['type']} {variable_default[var['type']]}, align {var['align']}")
    sem_stack.append(var)


def load_var(code, var):
    global diff_count
    code.append(f"%.tmp{diff_count} = load {var['type']}, {var['type']}* {var['name']}, align {var['align']}")


def store_var(code, var):
    global diff_count
    code.append(f"store {var['type']} %.tmp{diff_count}, {var['type']}* {var['name']}, align {var['align']}")


def cast(code, var, type):
    global diff_count
    if var['type'] == type:
        return
    code.append(f"%.tmp{diff_count} = {type_cast(var['type'], type)} {var['type']} {var['name']} to {type}")


def assign(code, _, sem_stack):
    global diff_count
    var_a = sem_stack.pop()
    var_b = sem_stack.pop()

    load_var(code, var_a)

    if var_b['type'] != var_a['type']:
        tmp_var = {'name': f'.tmp{diff_count}', 'type': var_a['type'], 'align': var_a['align']}
        diff_count += 1
        cast(code, tmp_var, var_b['type'])

    store_var(code, var_b)
    diff_count += 1
    sem_stack.append(var_b)


const_define = {}


def var_const(token):
    if token[0] == 'string':
        hsh = 77934516
        s = token[1]
        for ch in s:
            hsh = (hsh * 1812 + ch) % 182374277514
        return '@.const.' + str(hsh)
    else:
        return '@.const.' + str(token[1])


def const_push(code, token, sem_stack):
    var_name = var_const(token)
    var = {'name': var_name, 'type': variable_map[token[0]], 'align': variable_size[variable_map[token[0]]]}
    if var_name not in const_define:
        code.append(f"{var_name} = global {var['type']} {token[1]}, align {var['align']}")
        const_define[var_name] = None
    sem_stack.append(var)


def write(code, _, sem_stack):
    global diff_count
    var = sem_stack.pop()
    load_var(code, var)
    code.append(
        f""" call i32 (i8*, ...) @printf(i8* getelementptr inbounds ([5 x i8], [5 x i8]* @.w{var['type']}, i32 0, i32 
        0), {var['type']} %.tmp{diff_count}) """)
    diff_count += 1


def read(code, _, sem_stack):
    global diff_count
    var = sem_stack.pop()
    if var['type'] == 'i64':
        code.append(
            f"""call i32 (i8*, ...) @__isoc99_scanf(i8* getelementptr inbounds ([3 x i8], [3 x i8]* @.r{var[
                'type']}, i32 0, i32 0), {var['type']}* {var['name']})""")
    else:
        code.append(
            f"""call i32 (i8*, ...) @__isoc99_scanf(i8* getelementptr inbounds ([4 x i8], [4 x i8]* @.r{var[
                'type']}, i32 0, i32 0), {var['type']}* {var['name']})""")
