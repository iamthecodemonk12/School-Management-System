
import time

from PIL import Image

from django.db.models import Model

from django.shortcuts import render
from django.urls import reverse_lazy, reverse
from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse, HttpResponseRedirect

from django.views.generic import TemplateView, ListView, DetailView, RedirectView
from django.views.generic.edit import CreateView
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.template import Context

from django.utils import timezone
from datetime import date, datetime

from django.utils.translation import gettext as _

from registration.models import Report, Class, Student, Subject, Guardian, get_recent_students
from ..forms import CreateReportForm, SubjectForm

from ..forms import *
from registration import models

from .base import *

from core import settings

# mixins #########################################################################



class RotateAndRedirect(RedirectView):
    def get(self, request, pk, angle=90):
        try:
            model = self.model.objects.get(pk=pk)
            # assumes headshot exists and has a path
            with model.headshot.open() as img:
                with Image.open(img) as pil_img:
                    with pil_img.rotate(angle) as rot_img:
                        rot_img.save(img.path)
        except self.model.DoesNotExist:
            pass
        return self.redirect(pk)

    
    def redirect(self, pk):
        '''Note: args comes from urls.py <pk> or something like that'''
        return HttpResponseRedirect("")


# mixins END #########################################################################


class ChartJsView(TemplateView):
    template_name = "custom_admin/chart.js"
    content_type = "application/javascript"



# Home #########################################################################


class IndexView(LoginRequiredMixin, TemplateView):
    template_name = "custom_admin/dashboard.html"
    login_url = reverse_lazy('custom_admin:login')
    redirect_field_name = reverse_lazy('custom_admin:home')


    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['classes'] = Class.objects.all()
        context['subjects'] = Subject.objects.all()
        context['students'] = Student.objects.all()
        context['recent_students_days'] = dt = 5
        context['recent_students'] = get_recent_students(dt)

        context.update(base_context)

        return context


# Subjects #########################################################################


class SubjectsView(LoginRequiredMixin, ListView):
    model = Subject
    template_name = "custom_admin/subject_home.html"
    context_object_name = 'subjects'
    login_url = reverse_lazy('custom_admin:login')
    redirect_field_name = reverse_lazy('custom_admin:subjects')



class SubjectAddView(LoginRequiredMixin, TemplateView):
    template_name = "custom_admin/subject_create.html"
    login_url = reverse_lazy('custom_admin:login')
    redirect_field_name = reverse_lazy('custom_admin:subject_create')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['classes'] = [Class.ALL_CLASSES_TICK] + list(Class.objects.all().order_by('name'))

        return context
    
    def post(self, request):
        form = SubjectForm(request.POST)
        try:
            subject = form.save(commit=False)
            subject.save()
        except (ValueError, AttributeError) as ex:
            # raise Exception('a') from ex
            pass
        # return render(request, 'custom_admin/test.html', {'form':form})
        return HttpResponseRedirect(reverse('custom_admin:subjects'))




class SubjectDeleteView(LoginRequiredMixin, DeleteView):
    url = reverse_lazy('custom_admin:subjects')
    model = Subject
    login_url = reverse_lazy('custom_admin:login')
    redirect_field_name = reverse_lazy('custom_admin:subject_delete')


# Classes #########################################################################


class ClassesView(LoginRequiredMixin, ListView):
    model = Class
    template_name = "custom_admin/classes_home.html"
    context_object_name = 'classes'
    login_url = reverse_lazy('custom_admin:login')
    redirect_field_name = reverse_lazy('custom_admin:classes')


class ClassCreate(LoginRequiredMixin, CreateView):
    model = Class
    fields = ["name"]
    success_url = reverse_lazy('custom_admin:classes')
    template_name = "custom_admin/class_create.html"
    login_url = reverse_lazy('custom_admin:login')
    redirect_field_name = reverse_lazy('custom_admin:class_create')
    


class ClassDeleteView(LoginRequiredMixin, DeleteView):
    url = reverse_lazy('custom_admin:classes')
    model = Class
    login_url = reverse_lazy('custom_admin:login')
    redirect_field_name = reverse_lazy('custom_admin:class_delete')




# Students #########################################################################


class StudentsView(LoginRequiredMixin, ListView):
    model = Student
    template_name = "custom_admin/student_home.html"
    context_object_name = 'students'
    login_url = reverse_lazy('custom_admin:login')
    redirect_field_name = reverse_lazy('custom_admin:students')


    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['birthday_students'] = upcomming_student_birthdays()
        return context


class StudentDeleteView(LoginRequiredMixin, DeleteView):
    url = reverse_lazy('custom_admin:students')
    model = Student
    login_url = reverse_lazy('custom_admin:login')
    redirect_field_name = reverse_lazy('custom_admin:student_delete')


class StudentDetailView(LoginRequiredMixin, DetailView):
    model = Student
    context_object_name = 'student'
    template_name = 'custom_admin/student_detail.html'
    login_url = reverse_lazy('custom_admin:login')
    redirect_field_name = reverse_lazy('custom_admin:student_detail')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['settings'] = settings
        context['guardians'] = Guardian.objects.all()
        return context


class EditCreateView(object):
    model = Student

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['classes'] = Class.objects.all().order_by('name')
        context['add_max_length'] = self.model.address.field.max_length
        return context


class StudentEditView(LoginRequiredMixin, DetailView):
    model = Student
    context_object_name = 'student'
    login_url = reverse_lazy('custom_admin:login')
    redirect_field_name = reverse_lazy('custom_admin:student_edit')

    template_name = 'custom_admin/student_edit.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['classes'] = Class.objects.all().order_by('name')
        context['modifying'] = True
        context['today'] = date.today()

        # student
        std = context['student']
        form = context['form'] = StudentForm(instance=std, initial={
            'dob': std.dob,
            'reg_date': std.registration_date,
        })
        form.klass_int = form['klass'].value()

        return context
    

    def post(self, request, pk):
        student =  get_object_or_404(Student, pk=pk)
        form = StudentForm(request.POST)
        headshot = form['headshot'] or student.headshot
        
        try:
            # if form.is_valid():
                student.dob = form["dob"].value()  #13-12-2002
                student.registration_date = form["reg_date"].value()  #13-12-2002

                # convert 13-12-2002 to date object
                year, month, day = time.strptime(student.dob, settings.DATE_INPUT_FORMATS[0])[:3]
                student.dob = date(year, month, day)

                year, month, day = time.strptime(student.registration_date, settings.DATE_INPUT_FORMATS[0])[:3]
                student.registration_date = date(year, month, day)
                updated_fields = {
                    "first_name": form["first_name"].value(),
                    "last_name": form["last_name"].value(),
                    "middle_name": form["middle_name"].value(),
                    "klass": form["klass"].value(),
                    "phone_no": form["phone_no"].value(),
                    "email": form["email"].value(),
                    "gender": form["gender"].value(),
                    "registration_date": form["reg_date"].value(),
                    "dob": form["dob"].value(),
                    "address": form["address"].value(),
                    "headshot": headshot,
                }


                # student.save()
                return HttpResponse(
                    str(updated_fields)
                )
                return HttpResponseRedirect(reverse("custom_admin:student_detail", kwargs={'pk': new_student.pk}))
            # else:
            #     raise Exception('invalid form')

        except (ValueError, AttributeError):
            if 'email' in form.errors:
                form.errors['email'].append(_('Note: this email will be used to send student results'))
                if 'Enter a valid email address' in form.errors['email'][0]:
                    form.errors['email'][0] = _('Please put a valid email address')

            val = form['klass'].value()

            if val.isdigit():
                form.klass_int = int(val)
                # form.klass.value0 = int(val)
            
            return render(request, self.template_name, ({
                    'form': form, **self.get_context_data()
                })
            )


class StudentCreateView(LoginRequiredMixin, EditCreateView, TemplateView):
    template_name = 'custom_admin/student_create.html'
    login_url = reverse_lazy('custom_admin:login')
    redirect_field_name = reverse_lazy('custom_admin:student_create')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['today'] = date.today()
        return context
    

    def post(self, request):
        # raise Exception
        post_data = request.POST.copy()
        # if not post_data['address']:
        #     post_data['address'] = ''
        reg_form = StudentForm(post_data, request.FILES)
        try:
            new_student = reg_form.save(commit=False)
            new_student.dob = reg_form["dob"].value()  #13-12-2002
            new_student.registration_date = reg_form["reg_date"].value()  #13-12-2002

            # convert 13-12-2002 to date object
            year, month, day = time.strptime(new_student.dob, settings.DATE_INPUT_FORMATS[0])[:3]
            new_student.dob = date(year, month, day)

            year, month, day = time.strptime(new_student.registration_date, settings.DATE_INPUT_FORMATS[0])[:3]
            new_student.registration_date = date(year, month, day)

            new_student.save()

            return HttpResponseRedirect(reverse("custom_admin:student_detail", kwargs={'pk': new_student.pk}))

        except (ValueError, AttributeError):
            if 'email' in reg_form.errors:
                reg_form.errors['email'].append(_('Note: this email will be used to send student results'))
                if 'Enter a valid email address' in reg_form.errors['email'][0]:
                    reg_form.errors['email'][0] = _('Please put a valid email address')

            val = reg_form['klass'].value()

            if val.isdigit():
                reg_form.klass_int = int(val)
                # reg_form.klass.value0 = int(val)
            
            return render(request, self.template_name, ({
                    'form': reg_form, **self.get_context_data()
                })
            )


        # raise some !InternalError (at this point)


class StudentRotateView(LoginRequiredMixin, RotateAndRedirect):
    model = Student
    login_url = reverse_lazy('custom_admin:login')
    redirect_field_name = reverse_lazy('custom_admin:student_rotate_profile')

    def redirect(self, pk):
        '''Note: args comes from urls.py <pk> or something like that'''
        return HttpResponseRedirect(reverse('custom_admin:student_detail', kwargs={'pk': pk}))




# Copyrights #########################################################################

class Copyright(TemplateView):
    template_name = "custom_admin/copyrights.html"



# Other pages

class CommingSoon(TemplateView):
    template_name = "comming_soon.html"





# Utilities #########################################################################


def dob_offset(person_dob, limit_days=7):
    _now = timezone.now()
    cy = _now.year
    now = date(year=_now.year, month=_now.month, day=_now.day)
    dob_in_this_year = date(cy, person_dob.month, person_dob.day)
    dob_in_next_year = date(cy + 1, person_dob.month, person_dob.day)
    print((dob_in_this_year - now).days, '...days left :)\t' , 'where limit is', limit_days)

    days_in_year = int((dob_in_this_year - now).days)
    days_outside_year = int((dob_in_next_year - now).days)
    if 0 >=  days_in_year or days_in_year <= 7:
        return [dob_in_this_year, dob_in_this_year - now, dob_in_this_year.year - person_dob.year, days_in_year]  # bday, dob_offset_from_now, age
    elif 0 >= days_outside_year or days_outside_year <= 7 :
        return [dob_in_next_year, dob_in_next_year - now, dob_in_next_year.year - person_dob.year, days_outside_year]  # bday, dob_offset_from_now, age
    else:
        return 

def birthdays(people_class):
    days_range = 7
    for person in people_class.objects.all():
        print('trying... ', person)
        dob_offset_ = dob_offset(person.dob, days_range)
        if dob_offset_:
            bday, bday_offset, age, days = dob_offset_
            if days >= 0:
                yield {
                    'person': person,
                    'bday': bday,
                    'bday_offset': bday_offset,
                    'age': age,
                    'days': 'today' if days == 0 else f'{days} days from now',
                }

def upcomming_student_birthdays():
    for i in birthdays(Student):
        print(i)
        yield i