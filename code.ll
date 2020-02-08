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
@.const.real.4.2 = global float 0x4010cccc00000000, align 4
@.const.integer.0 = global i32 0, align 4
define i32 @main() {
	%a.1.0 = alloca i1, align 1
	%.tmp1 = load float, float* @.const.real.4.2, align 4
	%.tmp2 = fptosi float %.tmp1 to i1
	store i1 %.tmp2, i1* %a.1.0, align 1
	%.tmp3 = load i1, i1* %a.1.0, align 1
	call i32 (i8*, ...) @printf(i8* getelementptr inbounds ([3 x i8], [3 x i8]* @.wi1, i32 0, i32 0), i1 %.tmp3) 
	%.tmp4 = load i32, i32* @.const.integer.0, align 4
	ret i32 %.tmp4
}
