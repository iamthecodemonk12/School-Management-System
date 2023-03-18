from django.views.generic import TemplateView, ListView, DetailView, RedirectView
from core import settings 

dummy_template = "custom_admin/dummy_template.html"


#base context

base_context = {
    # context to use for mostly all views
    "settings": settings
}


# base views to inherit

class DeleteView(RedirectView):
    def get(self, request, pk):
        try:
            model = self.model.objects.get(pk=pk)
            model.delete()
        except self.model.DoesNotExist:
            pass # do nothing
        return super().get(request)



class ExploreContext:
    def take(self, context):
        context_keys = dir(context)
        context_values = [context.getattr(k) for k in context_keys]
        context_dict = zip(context_keys, context_values)
        return context



