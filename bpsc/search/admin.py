from django.contrib import admin
from django.contrib.auth.models import Group
from django.contrib.sites.models import Site

from bpsc.search.models import (
    HousingResource, CommunityResource, EmploymentResource, LegalResource,
    HousingTag, CommunityTag, EmploymentTag, LegalTag
)

def make_listing_otw(modeladmin, request, queryset):
    queryset.update(listing_of_the_week=True)
make_listing_otw.short_description = 'Mark selected as "Listings Of The Week"'

def remove_listing_otw(modeladmin, request, queryset):
    queryset.update(listing_of_the_week=False)
remove_listing_otw.short_description = 'Remove selected from "Listings Of The Week'

class ResourceAdmin(admin.ModelAdmin):
    list_display = ['name', 'url', 'num_used', 'auto_added']
    list_display_links = ['name',]
    readonly_fields = ['num_used', 'auto_added']


class HousingResourceAdmin(ResourceAdmin):
    list_display = ResourceAdmin.list_display + ['posted', 'outdated']


class CommunityResourceAdmin(ResourceAdmin):
    pass


class EmploymentResourceAdmin(ResourceAdmin):
    list_display = ResourceAdmin.list_display + ['posted', 'outdated', 'listing_of_the_week']
    actions = [make_listing_otw, remove_listing_otw]


class LegalResourceAdmin(ResourceAdmin):
    pass


class TagAdmin(admin.ModelAdmin):
    list_display = ['tag_type', 'value']
    list_display_links = ['value',]


class HousingTagAdmin(TagAdmin):
    pass


class CommunityTagAdmin(TagAdmin):
    pass


class EmploymentTagAdmin(TagAdmin):
    pass


class LegalTagAdmin(TagAdmin):
    pass


admin.site.unregister(Group)
admin.site.unregister(Site)
admin.site.register(HousingResource, HousingResourceAdmin)
admin.site.register(CommunityResource, CommunityResourceAdmin)
admin.site.register(EmploymentResource, EmploymentResourceAdmin)
admin.site.register(LegalResource, LegalResourceAdmin)
admin.site.register(HousingTag, HousingTagAdmin)
admin.site.register(CommunityTag, CommunityTagAdmin)
admin.site.register(EmploymentTag, EmploymentTagAdmin)
admin.site.register(LegalTag, LegalTagAdmin)