from django.urls import path
from django.views.generic import View
from .views import *

from django.contrib.auth import views as auth_views

app_name = "custom_admin" # namespacing urls

def filterSubClass(baseClass):
    # filters classes in this modules that are subclasses *baseclass
    for object in globals().values():
        if isinstance(object, type) and issubclass(object, baseClass):
            yield object


def addMethodToViews(methodName, method):
    # add specific method to all views
    # eg. methodName='globalvar' method=<globalvar>
    for view in filterSubClass(View):
        setattr(view, methodName, method)



import core.settings
addMethodToViews('globals', {
    "settings": core.settings,
    'var': 'this is the value of var',
})


urlpatterns = [
    path('', IndexView.as_view(), name='home'),

    path('login/', auth_views.LoginView.as_view(template_name='custom_admin/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(template_name='custom_admin/logout.html'), name='logout'),

    path("reports/",         ReportsView.as_view(),          name="reports"),
    path("reports/create/",  ReportCreateView.as_view(),     name="report_create"),
    path('reports/<pk>/del/',ReportDeleteView.as_view(),     name="report_delete"),
    path("reports/<pk>/",    ReportDetail_CLASSES.as_view(),     name="report_detail_classes"), #report_detail_classes
    path("reports/<int:report_id>/class/<int:class_id>/",ReportDetail_STUDENTS.as_view(),     name="report_detail_students"),  #report_detail_students
    path("reports/<int:report_id>/class/<int:class_id>/student/<int:student_id>/", ReportDetail_SCORES.as_view(),     name="report_detail_scores"), #report_detail_scores

    # remove this
    path("js/chart.js/",     ChartJsView.as_view(),          name="pie_chart"),

    path('classes/',         ClassesView.as_view(),          name='classes'),
    path('classes/add/',     ClassCreate.as_view(),          name='class_create'),
    path("classes/<pk>/",    ClassDeleteView.as_view(),     name="class_delete"),

    path('students/',               StudentsView.as_view(),         name='students'),
    path('student/create/',         StudentCreateView.as_view(),   name='student_create'),
    path("students/<pk>/del/",      StudentDeleteView.as_view(),  name="student_delete"),
    path("students/<pk>/",          StudentDetailView.as_view(),    name="student_detail"),
    path("students/<pk>/edit/",     StudentEditView.as_view(),    name="student_edit"),
    path("students/<pk>/rotate/",   StudentRotateView.as_view(),    name="student_rotate_profile"),
    path("students/<pk>/gaurdian/create/",   GaurdianCreate.as_view(),    name="add_gaurdian"),
    path("students/<pk>/gaurdian/edit/<int:guardian_id>",   GaurdianModify.as_view(),    name="edit_gaurdian"),
    path("students/<pk>/gaurdian/delete/<int:guardian_id>",   DeleteGuardianView.as_view(),    name="delete_gaurdian"),

    
    path("subjects/",        SubjectsView.as_view(),    name="subjects"),
    path("subjects/add/",    SubjectAddView.as_view(),    name="subject_create"),
    path("subjects/<pk>/del/",SubjectDeleteView.as_view(),    name="subject_delete"),

    path('copyrights/', Copyright.as_view(), name="copyright"),

]
