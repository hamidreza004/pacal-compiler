from code_generator import funcs

sem_stack = []
code = None
global_code = []
func_code = []
const_code = []


def initiate(src_code, sym_table):
    global code
    code = src_code
    const_code.append("""target triple = "x86_64-pc-linux-gnu" """)
    const_code.append("""@.wi1 = private unnamed_addr constant[3 x i8] c"%d\\00", align 1""")
    const_code.append("""@.wi8 = private unnamed_addr constant[3 x i8] c"%c\\00", align 1""")
    const_code.append("""@.wi32 = private unnamed_addr constant[3 x i8] c"%d\\00", align 1""")
    const_code.append("""@.wi64 = private unnamed_addr constant[4 x i8] c"%ld\\00", align 1""")
    const_code.append("""@.wfloat = private unnamed_addr constant[3 x i8] c"%f\\00", align 1""")
    const_code.append("""@.wstring = private unnamed_addr constant[3 x i8] c"%s\\00", align 1""")
    const_code.append("""@.ri1 = private unnamed_addr constant[3 x i8] c"%d\\00", align 1""")
    const_code.append("""@.ri8 = private unnamed_addr constant[3 x i8] c"%c\\00", align 1""")
    const_code.append("""@.ri32 = private unnamed_addr constant[3 x i8] c"%d\\00", align 1""")
    const_code.append("""@.ri64 = private unnamed_addr constant[4 x i8] c"%ld\\00", align 1""")
    const_code.append("""@.rfloat = private unnamed_addr constant[3 x i8] c"%f\\00", align 1""")
    const_code.append("""@.rstring = private unnamed_addr constant[3 x i8] c"%s\\00", align 1""")
    const_code.append("""declare i32 @printf(i8*, ...)""")
    const_code.append("""declare i32 @__isoc99_scanf(i8*, ...)""")
    funcs.global_code = global_code
    funcs.const_code = const_code
    funcs.func_code = func_code
    funcs.initiate(sym_table)


def generate(op, token):
    if op == "NoSem":
        return
    try:
        print(op)
        getattr(funcs, op[1:])(token, sem_stack)
    except AttributeError:
        print("No Function Available for ", op)
        pass


def build_code():
    global code
    for line in const_code:
        code.append(line)
    for line in global_code:
        code.append(line)
    for line in func_code:
        code.append(line)
    if len(sem_stack) > 0:
        print("WARNING!!!!! SemStack is not empty: ", len(sem_stack), sem_stack.pop())
    else:
        print("CodeGenerator is fine and stack is empty correctly.")
