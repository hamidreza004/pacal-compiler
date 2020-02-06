from code_generator.helper import variable_map, variable_size, type_cast

diff_count = 0


def push(_, token, sem_stack):
    sem_stack.append({'name': token})


def pop(_, __, sem_stack):
    sem_stack.pop()


def def_var(code, token, sem_stack):
    var = sem_stack.pop()
    var['type'] = variable_map[token]
    var['align'] = variable_size[var['type']]
    code.append(f"%{var['name']} = alloca {var['type']}, align {var['align']}")
    sem_stack.append(var)


def load_var(code, var):
    global diff_count
    code.append(f"%.tmp{diff_count} = load {var['type']}, {var['type']}* %{var['name']}, align {var['align']}")


def store_var(code, var):
    global diff_count
    code.append(f"store {var['type']} %.tmp{diff_count}, {var['type']}* %{var['name']}, align {var['align']}")


def cast(code, var, type):
    global diff_count
    if var['type'] == type:
        return
    code.append(f"%.tmp{diff_count} = {type_cast(var['type'], type)} {var['type']} {var['name']} to {type}")


def assign_var(code, _, sem_stack):
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
            f"""call i32 (i8*, ...) @__isoc99_scanf(i8* getelementptr inbounds ([3 x i8], [3 x i8]* @.r{var['type']}, i32 0, i32 0), {var['type']}* %{var['name']})""")
    else:
        code.append(
            f"""call i32 (i8*, ...) @__isoc99_scanf(i8* getelementptr inbounds ([4 x i8], [4 x i8]* @.r{var['type']}, i32 0, i32 0), {var['type']}* %{var['name']})""")
