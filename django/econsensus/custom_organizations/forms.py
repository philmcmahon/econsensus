from django import forms

from organizations.models import Organization
from organizations.utils import create_organization
from organizations.forms import OrganizationUserForm, OrganizationUserAddForm
from guardian.shortcuts import assign, remove_perm


# Completely override OrganizationForm and OrganizationAddForm from 
# organizations.forms because we don't want to allow ownership changes via UI, 
# and we want the owner of new Organizations to be the creating user.
class CustomOrganizationForm(forms.ModelForm):
    """
    For editing Organizations.
    """

    def __init__(self, request, *args, **kwargs):
        self.request = request
        super(CustomOrganizationForm, self).__init__(*args, **kwargs)

    class Meta:
        model = Organization
        exclude = ('slug', 'users', 'is_active')

class CustomOrganizationAddForm(CustomOrganizationForm):
    """
    For creating new Organizations.
    Set the owner to be the request user. The slug, will be auto-generated 
    from the name.
    """

    def save(self, **kwargs):
        is_active = True
        user = self.request.user
        organization = create_organization(user,
                                           self.cleaned_data['name'],
                                           '',  # Empty slug to be autofilled
                                           is_active=is_active)
        assign('edit_decisions_feedback',
               organization.owner.organization_user.user,
               organization)
        return organization

class CustomOrganizationUserForm(OrganizationUserForm):
    USER_TYPES = (
        ('1', "Normal User"),
        ('2', "Admin (can edit and invite users)"),
        ('3', "Observer Only (can't add or edit information)"),
    )
    user_type = forms.ChoiceField(required=True, choices=USER_TYPES)

    def save(self, commit=True):
        self.instance.is_admin = (self.cleaned_data['user_type'] == '2')
        if self.cleaned_data['user_type'] != '3':
            assign('edit_decisions_feedback', self.instance.user, self.instance.organization)
        else:
            remove_perm('edit_decisions_feedback', self.instance.user, self.instance.organization)
        return super(CustomOrganizationUserForm, self).save(commit=commit)

class CustomOrganizationUserAddForm(OrganizationUserAddForm):
    USER_TYPES = (
        ('1', "Normal User"),
        ('2', "Admin (can edit and invite users)"),
        ('3', "Observer Only (can't add or edit information)"),
    )
    user_type = forms.ChoiceField(required=True, choices=USER_TYPES)

    def save(self, commit=True):
        self.cleaned_data['is_admin'] = (self.cleaned_data['user_type'] == '2')
        self.instance = super(CustomOrganizationUserAddForm, self).save(commit=commit)
        if self.cleaned_data['user_type'] != '3':
            assign('edit_decisions_feedback', self.instance.user, self.instance.organization)
        else:
            remove_perm('edit_decisions_feedback', self.instance.user, self.instance.organization)
        print self.instance.is_admin
        return self.instance
