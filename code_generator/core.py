from code_generator import funcs
from scanner.core import sym_table

sem_stack = []
code = []


def initiate():
    code.append("""@.wi1 = private unnamed_addr constant[5 x i8] c"%d \0A\00", align 1""")
    code.append("""@.wi8 = private unnamed_addr constant[5 x i8] c"%c \0A\00", align 1""")
    code.append("""@.wi32 = private unnamed_addr constant[5 x i8] c"%d \0A\00", align 1""")
    code.append("""@.wi64 = private unnamed_addr constant[5 x i8] c"%ld\0A\00", align 1""")
    code.append("""@.wfloat = private unnamed_addr constant[5 x i8] c"%f \0A\00", align 1""")
    code.append("""@.wstring = private unnamed_addr constant[5 x i8] c"%s \0A\00", align 1""")
    code.append("""@.ri1 = private unnamed_addr constant[3 x i8] c"%d\00", align 1""")
    code.append("""@.ri8 = private unnamed_addr constant[3 x i8] c"%c\00", align 1""")
    code.append("""@.ri32 = private unnamed_addr constant[3 x i8] c"%d\00", align 1""")
    code.append("""@.ri64 = private unnamed_addr constant[4 x i8] c"%ld\00", align 1""")
    code.append("""@.rfloat = private unnamed_addr constant[3 x i8] c"%f\00", align 1""")
    code.append("""@.rstring = private unnamed_addr constant[3 x i8] c"%s\00", align 1""")
    code.append("""declare i32 @printf(i8*, ...)""")
    code.append("""declare i32 @__isoc99_scanf(i8*, ...)""")


def generate(op, token):
    getattr(funcs, op)(code, sym_table, token)
