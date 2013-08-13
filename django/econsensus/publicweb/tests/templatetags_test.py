from django.contrib.comments.models import Comment
from django.test import TestCase

from guardian.shortcuts import assign_perm

from organizations.models import Organization
from organizations.models import OrganizationUser

from publicweb.templatetags import publicweb_filters
from publicweb.tests.factories import UserFactory

class CustomTemplateFilterTest(TestCase):

    fixtures = ['users.json', 'organizations.json']

    def setUp(self):
    	self.countrycritters = Organization.objects.get(name="Country Critters")
        self.harry = OrganizationUser.objects.get(pk=12)
        self.betty = OrganizationUser.objects.get(pk=13)
        self.charlie = OrganizationUser.objects.get(pk=14)
        self.debbie = OrganizationUser.objects.get(pk=15)
        self.zarathustra = OrganizationUser.objects.get(pk=37)
        

    def test_get_user_name_from_comment(self):
        comment = Comment(user=None, user_name='')
        self.assertEqual(publicweb_filters.get_user_name_from_comment(comment), "An Anonymous Contributor")
        comment.user_name = "Harry"
        self.assertEqual(publicweb_filters.get_user_name_from_comment(comment), "Harry")
        user = UserFactory()
        comment.user = user
        self.assertEqual(publicweb_filters.get_user_name_from_comment(comment), user.username)

    def test_get_user_permissions(self):
    	self.assertEqual('owner', publicweb_filters.get_user_permissions(self.countrycritters, self.harry))
    	self.assertEqual('admin', publicweb_filters.get_user_permissions(self.countrycritters, self.betty))
    	assign_perm('edit_decisions_feedback', self.charlie.user, self.countrycritters)
    	self.assertEqual('editor', publicweb_filters.get_user_permissions(self.countrycritters, self.charlie))
    	self.assertEqual('observer', publicweb_filters.get_user_permissions(self.countrycritters, self.debbie))
    	self.assertEqual('inactive', publicweb_filters.get_user_permissions(self.countrycritters, self.zarathustra))