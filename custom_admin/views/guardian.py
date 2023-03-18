from django.views import generic
from .base import dummy_template

from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy, reverse

# models
from registration.models import Guardian, Student
from registration import models
from .. import forms

# not needed
# class GaurdianList(LoginRequiredMixin, generic.TemplateView):
#     template = dummy_template
#     login_url = reverse_lazy('custom_admin:login')
#     redirect_field_name = reverse_lazy('custom_admin:guardians')

#     def get_context_data(self, **kwargs):
#         context = super().get_context_data(**kwargs)
#         context['guardians'] = Guardian.objects.all()

#         return context



class GaurdianCreate(LoginRequiredMixin, generic.TemplateView):
    template_name = 'custom_admin/guardian_add.html'
    login_url = reverse_lazy('custom_admin:login')
    redirect_field_name = reverse_lazy('custom_admin:add_gaurdian')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        return context
    

    def get(self, request, pk):
        student = get_object_or_404(Student, pk=pk)

        return render(request, self.template_name, {
            'student':student,
            'Guardian': Guardian,
            # 'form': forms.GuardianForm
        })
    
    def post(self, request, pk):
        student = get_object_or_404(Student, pk=pk)
        form = forms.GuardianForm(request.POST)
        try:
            guardian = form.save(commit=False)
            guardian.student = student
            guardian.save()


        except (ValueError, AttributeError) as ex:
            return HttpResponse(
                f''''
                Hello world
                {form.as_table()}
                '''
            )

        return HttpResponseRedirect(reverse('custom_admin:student_detail', kwargs={
            "pk": pk,
        }))



class GaurdianModify(LoginRequiredMixin, generic.TemplateView):
    template_name = GaurdianCreate.template_name
    login_url = reverse_lazy('custom_admin:login')
    redirect_field_name = reverse_lazy('custom_admin:edit_gaurdian')

    def get(self, request, pk, guardian_id):
        student = get_object_or_404(Student, pk=pk)
        guardian = get_object_or_404(Guardian, pk=guardian_id)

        return render(request, self.template_name, {
            'student':student,
            'Guardian': Guardian,
            'form': forms.GuardianForm(instance=guardian),
            'guardian':guardian,
        })
    
    def post(self, request, pk, guardian_id):
        student = get_object_or_404(Student, pk=pk)
        guardian = get_object_or_404(Guardian, pk=guardian_id)

        form = forms.GuardianForm(request.POST)

        try:
            if form.is_valid():
                guardian.full_name = form['full_name'].value()
                guardian.relationship = form['relationship'].value()
                guardian.phone_no = form['phone_no'].value()
                guardian.email = form['email'].value()
                guardian.gender = form['gender'].value()
                guardian.address = form['address'].value()
                guardian.occupation = form['occupation'].value()
                guardian.save()

        except (ValueError, AttributeError) as ex:
            pass
            # raise
            # return HttpResponse(
            #     f''''
            #     Hello world
            #     {form.as_table()}
            #     '''
            # )

        return HttpResponseRedirect(reverse('custom_admin:student_detail', kwargs={
            "pk": pk,
        }))
    

class DeleteGuardianView(generic.TemplateView):
    login_url = reverse_lazy('custom_admin:login')
    redirect_field_name = reverse_lazy('custom_admin:delete_gaurdian')

    def get(self, request, pk, guardian_id):
        # student = get_object_or_404(Student, pk=pk)
        guardian = get_object_or_404(Guardian, pk=guardian_id)
        guardian.delete()        

        return HttpResponseRedirect(reverse('custom_admin:student_detail', kwargs={
            "pk": pk,
        }))
