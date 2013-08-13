from django import template

from publicweb.models import Feedback

register = template.Library()

@register.filter
def get_item(dict, arg):
    """Dictionary lookup when your key is a string"""
    return dict.get(arg)

@register.filter
def get_rating_name(value):
    """Get rating name from rating value/integer"""
    return [name for integer, name in Feedback.RATING_CHOICES if integer==value][0]

@register.filter
def get_user_name_from_comment(value):
    return (value.user and value.user.username) or value.user_name or "An Anonymous Contributor"

@register.filter
def get_user_permissions(org, org_user):
    if org_user.user.is_active:
        is_editor = org_user.user.has_perm('edit_decisions_feedback', org)
        return ((('observer', 'editor')[is_editor], 'admin')[org_user.is_admin],
            'owner')[org.is_owner(org_user.user)]
    else:
        return 'inactive'
