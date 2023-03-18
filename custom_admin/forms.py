from django import forms
from django.forms import modelformset_factory
from django.utils.translation import gettext as _

from registration.models import Report, Class, Student, Subject, _model_exist, Guardian
from registration import models

from django.core.exceptions import ValidationError


def _are_digits(*args, allow=''):
    # returns true if all args are digits
    return all([str(arg).isdigit() or str(arg)==allow  for arg in args])

class NameField(forms.CharField):
    def validate(self, value):
        value = value.strip()
        super().validate(value) # base validation is quick
        if len(value.split()) > 1:
            raise forms.ValidationError(_("Name must not contain whitespaces"))


class CreateReportForm(forms.Form):
    klass = forms.CharField(max_length=100, required=True)
    term = forms.CharField(max_length=100, required=True)

    def is_valid(self, *a, **kw):
        if super().is_valid(*a, **kw):
            klass = self.cleaned_data['klass'].upper()
            term = self.clean_data['term'].upper()
            if klass in Class.class_dict.values() and term in Report.termm_dict.values():
                return True
        return False    


# class StudentAddForm(forms.Form):
#     first_name =    NameField(max_length=Student.first_name.field.max_length, required=True)
#     last_name =     NameField(max_length=Student.last_name.field.max_length, required=True)
#     middle_name =   NameField(max_length=Student.middle_name.field.max_length, required=False)
#     dob =           forms.DateField(required=True)
#     admission_no =  forms.CharField(max_length=Student.admission_no.field.max_length, required=False)
#     klass =         forms.CharField(max_length=Class.name.field.max_length, required=False)
#     phone_no =      forms.CharField( max_length=Student, required=False)
#     email =         forms.EmailField(required=False)
#     # gender =        forms.CharField(max_length=, required=False)


class SubjectForm(forms.ModelForm):
    class Meta:
        model = Subject
        fields = (
            "name", "klass",
        )


    # subject_name = forms.CharField(required=False)
    # class_name = forms.CharField(required=False)

    # def is_valid(self, *a, **kw):
    #     class_name = self['class_name'].value().strip()
    #     subject_name = self['subject_name'].value().strip()
    #     if super().is_valid(*a, **kw):
    #         # so now this class  with valid class name exists
    #         # does a subject already have it
    #         if not class_name or not subject_name:
    #             return False
    #         if not self.validate_subject(subject_name, class_name):
    #             return False

    # def clean(self):
    #     cleaned_data = super().clean()
    #     class_name = cleaned_data['class_name'].strip()
    #     subject_name = cleaned_data['subject_name'].strip()

    #     if not self.validate_subject(subject_name, class_name):
    #             raise ValidationError(_('subject with this classname already exists'))

    # def validate_subject(subject_name, class_name):
    #     # check if subject with subject_name and class_name already exists

    #     # first get class
    #     klass = Class.objects.get_or_create(
    #         name=class_name
    #     )

    #     if class_name == Class.ALL_CLASSES_TICK:
    #         return bool(_model_exist(Subject, klass=None, name=subject_name, for_all_class=True))
    #     else:
    #         return bool(_model_exist(Subject, klass=klass, name=subject_name))

    # def clean_class_name(self):
    #     # !idempotent
    #     data = self.cleaned_data['class_name'].strip()
    #     if not data:
    #         raise ValidationError(_('Invalid Class name nothing was passed'))
    #     if data not in Class.class_dict.values() or data != Class.ALL_CLASSES_TICK:
    #         raise ValidationError(_('Invalid Class name'))
        
    #     if data != Class.ALL_CLASSES_TICK:
    #         return None
        
    #     d = Class.class_dict        
    #     cn = dict(zip(d.values(), d.keys()))
    #     return Class.objects.get_or_create(
    #         name=cn
    #     )[0]
        
    # def clean_for_all_class(self):
    #     if self.clean_class_name() is None:
    #         return False
    #     return True


class StudentForm(forms.ModelForm):
    dob = forms.DateField(required=True, input_formats=['%d-%m-%Y'])
    reg_date = forms.DateField(required=True, input_formats=['%d-%m-%Y'])
    class Meta:
        model = Student
        fields = (
            "first_name", "last_name", "middle_name", 
            "klass", "phone_no", "email", "gender", 
            "address", "headshot"
        )


class ReportForm(forms.ModelForm):
    
    class Meta:
        model = Report
        fields = (
            "term", "year", "session", "grading"
        )


class ReportSubjectForm(forms.ModelForm):
    
    class Meta:
        model = models.ReportSubject
        fields = (
            "id","t1", "t2", "t3", "project", "exam",
        )
    

    def is_valid(self):
        # super().is_valid()
        return _are_digits(self['id'].value(), self["t1"].value(), self["t2"].value(), self["t3"].value(), self["project"].value(), self["exam"].value(),)


ReportSubjectFormSet = lambda *a, **k: modelformset_factory(models.ReportSubject, *a, extra=3, form=ReportSubjectForm, **k)



# Guardian


class GuardianForm(forms.ModelForm):
    
    class Meta:
        model = Guardian
        fields = ("full_name", "relationship", "phone_no", "email", "gender", "address", "occupation")
