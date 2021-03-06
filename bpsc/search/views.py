from django.contrib import messages
from django.shortcuts import redirect
from django.views.generic import DetailView, ListView

from bpsc.search.forms import ResourcePrintForm, MapForm
from bpsc.lib import send_suitcase_email
from bpsc.search.models import (
    Tag, HousingTag, CommunityTag, EmploymentTag, LegalTag, Resource,
    HousingResource, CommunityResource, EmploymentResource, LegalResource,
    BatchHousingResource
)
from bpsc.static_pages.models import Post

from gmapi import maps

def generate_map(latitude, longitude):
    if not latitude or not longitude:
        return None
    gmap = maps.Map(opts = {
        'center': maps.LatLng(latitude, longitude),
        'mapTypeId': maps.MapTypeId.ROADMAP,
        'zoom': 12,
        'mapTypeControlOptions': {
             'style': maps.MapTypeControlStyle.DROPDOWN_MENU
        },
    })

    marker = maps.Marker(opts = {
        'map': gmap,
        'position': maps.LatLng(latitude, longitude),
    })
    maps.event.addListener(marker, 'mouseover', 'myobj.markerOver')
    maps.event.addListener(marker, 'mouseout', 'myobj.markerOut')
    info = maps.InfoWindow({
        'content': 'Hello!',
        'disableAutoPan': False
    })
    info.open(gmap, marker)
    return MapForm(initial={'map': gmap})


class MapMixin(object):
    def get_context_data(self, **kwargs):
        context = super(MapMixin, self).get_context_data(**kwargs)
        self.object.mapform = generate_map(self.object.latitude, self.object.longitude)
        return context


class BaseResourceDetailView(DetailView):
    model = Resource

    def get_object(self, queryset=None):
        pk = self.kwargs.get(self.pk_url_kwarg, None)
        resource = self.model.objects.get(pk=pk)
        return resource


class HousingResourceDetailView(MapMixin, BaseResourceDetailView):
    model = HousingResource
    context_object_name = 'resource'
    template_name = 'housing_resource_detail.html'
    resource_type = 'Housing'


class BatchHousingResourceDetailView(BaseResourceDetailView):
    model = BatchHousingResource
    context_object_name = 'resource'
    template_name = 'batch_housing_resource_detail.html'
    resource_type = 'Housing'


class CommunityResourceDetailView(MapMixin, BaseResourceDetailView):
    model = CommunityResource
    context_object_name = 'resource'
    template_name = 'community_resource_detail.html'
    resource_type = 'Community'


class EmploymentResourceDetailView(MapMixin, BaseResourceDetailView):
    model = EmploymentResource
    context_object_name = 'resource'
    template_name = 'employment_resource_detail.html'
    resource_type = 'Employment'


class LegalResourceDetailView(MapMixin, BaseResourceDetailView):
    model = LegalResource
    context_object_name = 'resource'
    template_name = 'legal_resource_detail.html'
    resource_type = 'Legal'


class BaseResourceListView(ListView):
    # Sorting will happen with Javascript on the frontend
    model = Resource
    tag = Tag
    resource_type = 'Base'

    def get_context_data(self, **kwargs):
        context = super(BaseResourceListView, self).get_context_data(**kwargs)
        tags = self.tag.objects.all()
        tag_dict = {t.tag_type: [] for t in tags}
        for t in tags:
            values_list = tag_dict.get(t.tag_type)
            values_list.append(t.value)
            tag_dict[t.tag_type] = values_list
        # Tags is a dictionary that maps a tag_type to all of its distinct values
        context['tags'] = tag_dict
        if self.request.method == 'POST':
            context['print_form'] = ResourcePrintForm(self.request.POST)
        else:
            context['print_form'] = ResourcePrintForm()
        return context

    def post(self, request, *args, **kwargs):
        self.object_list = self.get_queryset()
        # Use: <input type="checkbox" name="resources" value="{{ resource.id }}"/>
        # in template to render checkboxes next to each resource
        context = self.get_context_data(object_list=self.object_list)
        print_form = context['print_form']
        selected_resources = request.POST.getlist('resources')
        selected_batch_resources = request.POST.getlist('batch-resources')
        if print_form.is_valid():
            if not selected_resources and not selected_batch_resources:
                messages.error(request, 'No resources selected.')
                return self.render_to_response(context)
            # Eliminate any duplicate resource ids, possibly from selecting a listing of the week
            resource_params = '&'.join(['rid=%s' % resource_id for resource_id in sorted(set(selected_resources))])
            batch_resource_params = '&'.join(['brid=%s' % resource_id for resource_id in sorted(set(selected_batch_resources))])
            print_url = request.build_absolute_uri() + 'print/?' + resource_params + '&' + batch_resource_params
            for resource in context['resource_list']:
                resource.num_used += 1
                resource.save()
            email_context_dict = {
                'client_name': print_form.cleaned_data.get('client_name'),
                'client_phone': print_form.cleaned_data.get('client_phone'),
                'client_email': print_form.cleaned_data.get('client_email'),
                'resource_url': print_url,
                'resource_type': self.resource_type,
            }
            send_suitcase_email('print_resource.yml', email_context_dict,
                    [print_form.cleaned_data.get('user_email')])
            messages.success(request, 'Resources use logged successfully.')
            return redirect(print_url)
        else:
            messages.error(request, 'Error in client logging form. Please try again.')
            return self.render_to_response(context)


class HousingResourceListView(BaseResourceListView):
    model = HousingResource
    context_object_name = 'resource_list'
    template_name = 'housing_resource_list.html'
    resource_type = 'Housing'
    tag = HousingTag

    def get_context_data(self, **kwargs):
        context = super(HousingResourceListView, self).get_context_data(**kwargs)
        context['batch_resource_list'] = BatchHousingResource.objects.all()
        return context


class CommunityResourceListView(BaseResourceListView):
    model = CommunityResource
    context_object_name = 'resource_list'
    template_name = 'community_resource_list.html'
    resource_type = 'Community'
    tag = CommunityTag


class EmploymentResourceListView(BaseResourceListView):
    model = EmploymentResource
    context_object_name = 'resource_list'
    template_name = 'employment_resource_list.html'
    resource_type = 'Employment'
    tag = EmploymentTag

    def get_context_data(self, **kwargs):
        context = super(EmploymentResourceListView, self).get_context_data(**kwargs)
        context['listings_of_the_week'] = EmploymentResource.objects.filter(listing_of_the_week=True)
        return context


class LegalResourceListView(BaseResourceListView):
    model = LegalResource
    context_object_name = 'resource_list'
    template_name = 'legal_resource_list.html'
    resource_type = 'Legal'
    tag = LegalTag


class GovernmentResourceView(DetailView):
    model = Post
    context_object_name = 'resource'
    template_name = 'government_resource.html'
    resource_type = 'Government'

    def get_object(self, **kwargs):
        return Post.objects.get(url='search:government')


class BaseResourcePrintView(ListView):
    model = Resource
    context_object_name = 'resource_list'
    tag = Tag

    def dispatch(self, request, *args, **kwargs):
        self.is_logged = request.GET.get('logged') == 'true'
        return super(BaseResourcePrintView, self).dispatch(request, *args, **kwargs)

    def get_queryset(self):
        # Get the resources with the IDs in the url querystring
        resource_ids = self.request.GET.getlist('rid')
        queryset = self.model.objects.filter(pk__in=resource_ids)
        for resource in queryset:
            resource.mapform = generate_map(resource.latitude, resource.longitude)
        return queryset


class HousingResourcePrintView(BaseResourcePrintView):
    model = HousingResource
    template_name = 'housing_resource_print.html'
    list_url = 'search:housing_list'
    tag = HousingTag
    resource_type = 'Housing'

    def get_context_data(self, **kwargs):
        context = super(BaseResourcePrintView, self).get_context_data(**kwargs)
        batch_resource_ids = self.request.GET.getlist('brid')
        context['batch_resource_list'] = BatchHousingResource.objects.filter(pk__in=batch_resource_ids)
        return context


class CommunityResourcePrintView(BaseResourcePrintView):
    model = CommunityResource
    template_name = 'community_resource_print.html'
    list_url = 'search:community_list'
    tag = CommunityTag
    resource_type = 'Community'


class EmploymentResourcePrintView(BaseResourcePrintView):
    model = EmploymentResource
    template_name = 'employment_resource_print.html'
    list_url = 'search:employment_list'
    tag = EmploymentTag
    resource_type = 'Employment'


class LegalResourcePrintView(BaseResourcePrintView):
    model = LegalResource
    template_name = 'legal_resource_print.html'
    list_url = 'search:legal_list'
    tag = LegalTag
    resource_type = 'Legal'
