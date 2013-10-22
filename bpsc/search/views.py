# Create your views here.
from django.contrib import messages
from django.core.urlresolvers import reverse
from django.shortcuts import get_object_or_404, redirect
from django.views.generic import DetailView, FormView ListView
from django.views.generic import ListView

from bspc.search.forms import ResourceListForm
from bpsc.search.models import (
    Tag, HousingTag, CommunityTag, EmploymentTag, LegalTag, Resource,
    HousingResource, CommunityResource, EmploymentResource, LegalResource
)

class BaseResourceDetailView(DetailView):
    model = Resource

    def get_object(self, queryset=None):
        pk = self.kwargs.get(self.pk_url_kwarg, None)
        return get_object_or_404(self.model, pk=pk)

class HousingResourceDetailView(BaseResourceDetailView):
    model = HousingResource
    context_object_name = 'housing_resource'
    template_name = 'housing_resource_detail.html'


class CommunityResourceDetailView(BaseResourceDetailView):
    model = CommunityResource
    context_object_name = 'community_resource'
    template_name = 'community_resource_detail.html'


class EmploymentResourceDetailView(BaseResourceDetailView):
    model = EmploymentResource
    context_object_name = 'employment_resource'
    template_name = 'employment_resource_detail.html'


class LegalResourceDetailView(BaseResourceDetailView):
    model = LegalResource
    context_object_name = 'legal_resource'
    template_name = 'legal_resource_detail.html'

class BaseResourceListView(ListView):
    model = Resource
    tag = Tag

    def get_context_data(self, **kwargs):
        context = super(BaseResourceListView, self).get_context_data(**kwargs)
        # Retrieve all the related tags for this Resource
        context['tags'] = self.tag.objects.all()

    def post(self, request, *args, **kwargs):
        self.object_list = self.get_queryset()
        # Use: <input type="checkbox" name="resources" value="{{ resource.id }}"/>
        # in template to render checkboxes next to each resource
        selected_resources = request.POST.getlist('resources')
        if not selected_resources:
            messages.error(request, 'No resources selected')
            context = self.get_context_data(object_list=self.object_list)
            return self.render_to_response(context)
        else:
            confirm_url = request.build_absolute_uri() + 'print/'
            resource_params = '&'.join(['?resourceid=%s' % resource_id for resource_id in selected_resources])
            return redirect(confirm_url + resource_params)

