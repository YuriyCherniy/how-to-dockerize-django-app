from django.views.generic import CreateView
from django.urls import reverse_lazy
from demo.models import DemoObjectModel


class DemoObjectCreate(CreateView):
    model = DemoObjectModel
    fields = ['demo_entry']
    template_name = 'demo/object_create_form.html'
    success_url = reverse_lazy('create_object')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['object_list'] = DemoObjectModel.objects.all()
        return context
