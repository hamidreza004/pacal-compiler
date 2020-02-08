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
@.const.real.3.342 = global float 0x400abc6a00000000, align 4
@.const.integer.0 = global i32 0, align 4
define i32 @main() {
	%a.1.0 = alloca float, align 4
	%.tmp1 = load float, float* @.const.real.3.342, align 4
	store float %.tmp1, float* %a.1.0, align 4
	%c.1.2 = alloca i64, align 8
	%.tmp3 = load float, float* %a.1.0, align 4
	%.tmp4 = fptosi float %.tmp3 to i64
	store i64 %.tmp4, i64* %c.1.2, align 8
	%.tmp5 = load i64, i64* %c.1.2, align 8
	call i32 (i8*, ...) @printf(i8* getelementptr inbounds ([4 x i8], [4 x i8]* @.wi64, i32 0, i32 0), i64 %.tmp5) 
	%.tmp6 = load i32, i32* @.const.integer.0, align 4
	ret i32 %.tmp6
}
