from code_generator.helper import variable_map, variable_size, type_cast

diff_count = 0


def push(code, token, sem_stack):
    sem_stack.append({'name': token})


def pop(code, token, sem_stack):
    sem_stack.pop()


def def_var(code, token, sem_stack):
    var = sem_stack.pop()
    var['type'] = variable_map[token]
    var['align'] = variable_size[var['type']]
    code.append(f"%{var['name']} = alloca {var['type']}, align {var['align']}")
    sem_stack.append(var)


def cast(code, type, sem_stack):
    var = sem_stack.pop()
    if var['type'] == type:
        return
    code.append(f"%tmpp{diff_count} = {type_cast(var['type'], type)} {var['type']} {var['name']} to {type}")


def assign_var(code, token, sem_stack):
    global diff_count
    var_a = sem_stack.pop()
    var_b = sem_stack.pop()

    code.append(f"%tmpp{diff_count} = load {var_a['type']}, {var_a['type']}* %{var_a['name']}, align {var_a['align']}")

    if var_b['type'] != var_a['type']:
        sem_stack.append({'name': f'tmpp{diff_count}', 'type': var_a['type'], 'align': var_a['align']})
        diff_count += 1
        cast(code, var_b['type'], sem_stack)

    code.append(f"store {var_b['type']} %tmpp{diff_count}, {var_b['type']}* %{var_b['name']}, align {var_b['align']}")
    diff_count += 1

def write(code, token, sem_stack):
    var = sem_stack.pop()


