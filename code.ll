@.wi1 = private unnamed_addr constant[3 x i8] c"%d\00", align 1
@.wi8 = private unnamed_addr constant[3 x i8] c"%c\00", align 1
@.wi32 = private unnamed_addr constant[3 x i8] c"%d\00", align 1
@.wi64 = private unnamed_addr constant[4 x i8] c"%ld\00", align 1
@.wfloat = private unnamed_addr constant[3 x i8] c"%f\00", align 1
@.wstring = private unnamed_addr constant[3 x i8] c"%s\00", align 1
@.ri1 = private unnamed_addr constant[3 x i8] c"%d\00", align 1
@.ri8 = private unnamed_addr constant[3 x i8] c"%c\00", align 1
@.ri32 = private unnamed_addr constant[3 x i8] c"%d\00", align 1
@.ri64 = private unnamed_addr constant[4 x i8] c"%ld\00", align 1
@.rfloat = private unnamed_addr constant[3 x i8] c"%f\00", align 1
@.rstring = private unnamed_addr constant[3 x i8] c"%s\00", align 1
declare i32 @printf(i8*, ...)
declare i32 @__isoc99_scanf(i8*, ...)
@.const.integer.23 = global i32 23, align 4
@a.0.0 = global i32 0, align 4
define i32 @main() {
	%b.1.1 = alloca i32, align 4
	%.tmp2 = load i32, i32* @.const.integer.23, align 4
	store i32 %.tmp2, i32* %b.1.1, align 4
	%.tmp3 = load i32, i32* @a.0.0, align 4
	call i32 (i8*, ...) @printf(i8* getelementptr inbounds ([3 x i8], [3 x i8]* @.wi32, i32 0, i32 0), i32 %.tmp3) 
}
