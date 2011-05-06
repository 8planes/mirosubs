from django.contrib import admin
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin
from models import CustomUser, Announcement
from django.contrib.auth.forms import UserCreationForm
from django import forms
from django.utils.translation import ugettext_lazy as _
from django.db import models
from django.contrib.admin import widgets

class CustomUserCreationForm(UserCreationForm):
    username = forms.RegexField(label=_("Username"), max_length=30, regex=r'^\w+$',
        help_text = _("Required. 30 characters or fewer. Alphanumeric characters only (letters, digits and underscores)."),
        error_message = _("This value must contain only letters, numbers and underscores."))
    password1 = forms.CharField(label=_("Password"), widget=forms.PasswordInput)
    password2 = forms.CharField(label=_("Password confirmation"), widget=forms.PasswordInput)
    email = forms.EmailField(label=_('Email'))
    
    class Meta:
        model = CustomUser
        fields = ("username", "email")

class CustomUserAdmin(UserAdmin):
    add_form = CustomUserCreationForm
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_staff', 'is_superuser', 'last_ip')
    search_fields = ('username', 'first_name', 'last_name', 'email', 'id')
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'email', 'password1', 'password2')}
        ),
    )

class AnnouncementAdmin(admin.ModelAdmin):
    formfield_overrides = {
        models.CharField: {'widget': widgets.AdminTextareaWidget}
    }
    list_display = ('content', 'created', 'visible')
    actions = ['make_hidden']
    
    def visible(self, obj):
        return not obj.hidden
    visible.boolean = True

    def make_hidden(self, request, queryset):
        Announcement.clear_cache()
        queryset.update(hidden=True)
    make_hidden.short_description = _(u'Hide')
    
admin.site.register(Announcement, AnnouncementAdmin)
admin.site.unregister(User)    
admin.site.register(CustomUser, CustomUserAdmin)