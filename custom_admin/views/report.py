import enum

from django.views.generic import TemplateView, ListView, DetailView, RedirectView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render, get_object_or_404
from django.urls import reverse_lazy, reverse
from django.http import HttpResponse, HttpResponseRedirect

# other apps
from registration.models import *
from core import settings

from .base import *

from ..forms import *
from .. import forms


# automation
from . import automation_tools


def _int_or_None(item):
    # tries to convert item to int if item=='' returns None
    item = str(item)
    if item.isdigit():
        return int(item)
    elif item=='':
        return



class ReportsView(LoginRequiredMixin, ListView):
    model = Report
    context_object_name = 'reports'
    template_name = "custom_admin/reports/reports_home.html"
    login_url = reverse_lazy('custom_admin:login')
    redirect_field_name = reverse_lazy('custom_admin:reports')

    # queryset = Report.objects.all()
    # def get_queryset(self):
    #     return super().get_queryset()


class ReportDetail_CLASSES(LoginRequiredMixin, DetailView):
    model = Report
    template_name = "custom_admin/reports/reports_detail_classes.html"
    context_object_name = 'report'
    login_url = reverse_lazy('custom_admin:login')
    redirect_field_name = reverse_lazy('custom_admin:report_detail_classes')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        report = context['report']
        context['classes'] = report.reportclass_set.all()

        return context


class ReportDetail_STUDENTS(LoginRequiredMixin, TemplateView):
    model = Report
    template_name = "custom_admin/reports/reports_detail_students.html"
    login_url = reverse_lazy('custom_admin:login')
    redirect_field_name = reverse_lazy('custom_admin:report_detail_students')

    class PROGRESS(enum.Enum):
        DONE = 1
        IN_PROGRESS = 2
        NOT_TOUCHED = 3
    
    _progress_html = {
        PROGRESS.DONE: {
            'label': 'success',
            'name': PROGRESS.DONE.name
        },
        PROGRESS.IN_PROGRESS: {
            'label': 'info',
            'name': PROGRESS.IN_PROGRESS.name.replace('_', ' ')
        },
        PROGRESS.NOT_TOUCHED: {
            'label': 'danger',
            'name': PROGRESS.NOT_TOUCHED.name.replace('_', ' ')
        },
    }

    def _progress(self, stud):
        progress = None
        scores = []
        for subject in stud.reportsubject_set.all():
            for score in (subject.t1, subject.t2, subject.t3, subject.project, subject.exam):
                scores.append(score)
        # check all scores are filled
        if scores.count(None) == len(scores):
            return self.PROGRESS.NOT_TOUCHED
        # is their any score not filled?
        if None in scores:
            return self.PROGRESS.IN_PROGRESS
        return self.PROGRESS.DONE

    def get(self, request, report_id, class_id):
        report = get_object_or_404(Report, pk=report_id)
        report_class = get_object_or_404(report.reportclass_set, pk=class_id)
        report_students = report_class.reportstudent_set.all()
        
        # !experimental <too-much-over-headcost>
        report_progress = []
        for rep_stud in report_students:
            rp = self._progress_html[self._progress(rep_stud)]
            report_progress.append([
                rep_stud,
                rp,
            ])

        return render(request, self.template_name, {
            'report': report,
            'report_class': report_class,
            'report_students': report_students,
            'report_progress': report_progress
        })


class ReportDetail_SCORES(LoginRequiredMixin, TemplateView):
    model = Report
    template_name = "custom_admin/reports/report_detail_subjects.html"
    login_url = reverse_lazy('custom_admin:login')
    redirect_field_name = reverse_lazy('custom_admin:report_detail_scores')


    class DownloadTools:
        actions = 'pdf', 'excell'


    def get(self, request, report_id, class_id, student_id):      

        report = get_object_or_404(Report, pk=report_id)
        report_class = get_object_or_404(report.reportclass_set, pk=class_id)
        report_student = get_object_or_404(report_class.reportstudent_set, pk=student_id)
        report_subjects = report_student.reportsubject_set.all()

        if len(request.GET):
            action = request.GET['action'].lower()
            if action in self.DownloadTools.actions:
                if action == 'excell':
                    media_path = automation_tools.make_student_report(report_student)
                    return HttpResponseRedirect(media_path)
                elif action == 'pdf':
                    pass
  
        return render(request, self.template_name, {
            'report':           report,
            'report_class':    report_class,
            'report_student':  report_student,
            'report_subjects': report_subjects
        })
    

    def post(self, request, report_id, class_id, student_id):
        report = get_object_or_404(Report, pk=report_id)
        report_class = get_object_or_404(report.reportclass_set, pk=class_id)
        report_student = get_object_or_404(report_class.reportstudent_set, pk=student_id)
        report_subject_manager = report_student.reportsubject_set
        report_subjects = report_subject_manager.all()

        ReportSubjectFormSet = forms.ReportSubjectFormSet()
        formset = ReportSubjectFormSet(
            request.POST, 
            queryset=report_subjects)

        if formset.is_valid():
            for sub_form in formset:
                report_subject = get_object_or_404(report_subject_manager, pk=_int_or_None(sub_form['id'].value()))
                report_subject.t1 = _int_or_None(sub_form['t1'].value())
                report_subject.t2 = _int_or_None(sub_form['t2'].value())
                report_subject.t3 = _int_or_None(sub_form['t3'].value())
                report_subject.project = _int_or_None(sub_form['project'].value())
                report_subject.exam = _int_or_None(sub_form['exam'].value())
                report_subject.save()
        
        return HttpResponseRedirect(reverse('custom_admin:report_detail_scores', kwargs={
            'report_id': report_id,
            'class_id': class_id,
            'student_id': student_id,
        }))
#         else:
#             return HttpResponse('The form was not valid re-check')
#         return HttpResponse(
#             f'''
# test {type(formset[0]['test'].value()).__name__} {formset[0]['test']}
# exam {type(formset[0]['exam'].value()).__name__} {formset[0]['exam']}
# project {type(formset[0]['project'].value()).__name__} {formset[0]['project']}
#             '''
#         )
        


class ReportDeleteView(LoginRequiredMixin, DeleteView):
    url = reverse_lazy('custom_admin:reports')
    model = Report
    login_url = reverse_lazy('custom_admin:login')
    redirect_field_name = reverse_lazy('custom_admin:reports')


class ReportCreateView(LoginRequiredMixin, TemplateView, ExploreContext):
    template_name = "custom_admin/reports/reports_create.html"
    login_url = reverse_lazy('custom_admin:login')
    redirect_field_name = reverse_lazy('custom_admin:reports')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['classes'] = Class.objects.all().order_by('name')
        context['terms'] = Report.term_dict.items
        context['year'] = timezone.now().year

        context['debug_context'] = context
        return context
    
    def post(self, request):
        # process data and save report

        # create a form instance and populate it with data from the request:
        form = ReportForm(request.POST)
        try:
            report = form.save(commit=False)
            report.save()

            # populate report with class 
            for klass in Class.objects.all():
                rep_class = ReportClass.objects.create(
                    report=report,
                    klass=klass,
                )
                for student in klass.student_set.all():
                    rep_student = ReportStudent.objects.create(
                        rep_klass=rep_class,
                        student=student
                    )
                    for subject in klass.subject_set.all():
                        rep_subject = ReportSubject.objects.create(
                            rep_stud=rep_student,
                            subject=subject,

                        )

            report.save()

                # for student in klass.student
        except (ValueError, AttributeError) as ex:
            pass
            # raise Exception('a') from ex
            # return HttpResponse(
            #     f''''
            #     Hello world
            #     {form.as_table()}
            #     '''
            # )
        return HttpResponseRedirect(reverse('custom_admin:report_detail_classes', kwargs={
            "pk": report.id,
        }))


