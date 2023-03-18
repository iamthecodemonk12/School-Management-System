from django.contrib import admin

# Register your models here.
from .models import *


@admin.register(Guardian)
class GuardianAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'student', 'relationship', 'phone_no', 'email')


@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'dob', 'klass', 'admission_no', 'created_when')


@admin.register(Class)
class ClassAdmin(admin.ModelAdmin):
    list_display = ('name', )


@admin.register(Subject)
class SubjectAdmin(admin.ModelAdmin):
    list_display = ('name',)


# @admin.register(Grade)
# class GradeAdmin(admin.ModelAdmin):
#     list_display = ('grade_letter', 'description', 'start', 'end')


@admin.register(Report)
class ReportAdmin(admin.ModelAdmin):
    list_display = ('term', 'year', 'session', 'grading')


@admin.register(ReportClass)
class ReportClassAdmin(admin.ModelAdmin):
    pass


@admin.register(ReportStudent)
class ReportStudentAdmin(admin.ModelAdmin):
    pass


@admin.register(ReportSubject)
class ReportSubjectAdmin(admin.ModelAdmin):
    list_display = ("t1", "t2", "t3", 'project', 'exam')



# @admin.register(Exam)
# class ExamAdmin(admin.ModelAdmin):
#     list_display = ('name', 'report', 'student', )


# @admin.register(ExamEntry)
# class ExamEntryAdmin(admin.ModelAdmin):
#     list_display = ('subject', 'subject_score', 'exam', )

