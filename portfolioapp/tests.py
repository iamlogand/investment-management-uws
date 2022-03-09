from django.test import TestCase
from django.urls import reverse

from portfolioapp.models import *


class AccessControlTests(TestCase):

    def test_portfolio_overview_not_logged_in(self):
        """
        If not logged in, a request for the overview page should redirect to the login page.
        """
        response = self.client.get(reverse("portfolioapp:overview"))
        self.assertRedirects(response, "/accounts/login/?next=%2F")

    def test_portfolio_overview_logged_in(self):
        """
        If logged in, and the user has a selected portfolio, a request for the overview page should successfully
        display the overview page
        """

        # Create and login a user instance
        test_user = User.objects.create_user(username="testuser", email="testuser@email.com", password="Ad4mqQnCui")
        login_response = self.client.login(username="testuser", password="Ad4mqQnCui")
        self.assertTrue(login_response)

        # Create and select a portfolio instance
        test_portfolio = Portfolio.create(owner=test_user, name="Test Portfolio")
        test_portfolio.set_selected()
        test_portfolio.save()

        # Request the Overview page and check for evidence of successful display
        view_response = self.client.get(reverse("portfolioapp:overview"))
        self.assertContains(view_response, "Portfolio Overview")
        self.assertContains(view_response, "Test Portfolio")
        self.assertContains(view_response, "There are no investment accounts in the selected portfolio.")

