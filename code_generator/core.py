from code_generator import funcs
from scanner.core import sym_table

sem_stack = []
code = []


def initiate():
    code.append("""@.i32 = private unnamed_addr constant[4 x i8] c"%d\0A\00", align 1""")
    code.append("""@.i64 = private unnamed_addr constant[4 x i8] c"%d\0A\00", align 1""")
    code.append("""@.i8 = private unnamed_addr constant[4 x i8] c"%d\0A\00", align 1""")
    code.append("""@.i16 = private unnamed_addr constant[4 x i8] c"%d\0A\00", align 1""")



def generate(op, token):
    result = getattr(funcs, op)(code, sym_table, token)
