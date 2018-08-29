from django.utils import translation

from base.tests.factories.user import UserFactory
from base.tests.functional.models.base_model import FunctionalTestCase
from django.utils.translation import ugettext as _

from base.tests.functional.models.user_type import StudentMixin, TutorMixin, PhdMixin, AdministratorMixin


class BasicLoginTestCase(FunctionalTestCase):

    def setUp(self):
        super(BasicLoginTestCase, self).setUp()
        self.valid_user = UserFactory()

    def test_login_page(self):
        """
        As a not connected user
        I should see the login page
        """
        self.openUrl('login')
        self.check_page_title('Login')

    def test_valid_login(self):
        """
        As a registered user with valid password
        I should be able to connect
        """
        self.login(self.valid_user.username, 'password123')
        self.check_page_title(self.config.get('DASHBOARD').get('PAGE_TITLE'))

    def test_invalid_login(self):
        """
        As a registered user with wrong password
        I scould not be able to connect
        """
        self.login(self.valid_user.username, 'wrong_password')
        translation.activate('en')
        string = _('msg_error_username_password_not_matching')
        self.check_page_contains_string(string)


class StudentLoginTestCase(FunctionalTestCase, StudentMixin):

    @classmethod
    def setUpClass(cls):
        super(StudentLoginTestCase, cls).setUpClass()
        cls.dashboard_config = cls.config.get('DASHBOARD')

    def setUp(self):
        super(StudentLoginTestCase, self).setUp()
        self.student = self.create_student()

    def test_student_login(self):
        """
        As a student
         - I should be able to connect
         - I should see the student links
         - I should not see the tutor links
         - I should no see the admin links
        """
        self.login(self.student.person.user.username, 'password123')
        self.check_page_contains_ids(self.dashboard_config.get('STUDENT_LINKS'))
        self.check_page_not_contains_ids(self.dashboard_config.get('TUTOR_LINKS'))
        self.check_page_not_contains_ids(self.dashboard_config.get('ADMIN_LINKS'))


class TutorLoginTestCase(FunctionalTestCase, TutorMixin):

    @classmethod
    def setUpClass(cls):
        super(TutorLoginTestCase, cls).setUpClass()
        cls.dashboard_config = cls.config.get('DASHBOARD')

    def setUp(self):
        super(TutorLoginTestCase, self).setUp()
        self.tutor = self.create_tutor()

    def test_tutor_login(self):
        """
        As a tutor
        - I should be able to connect
        - I should see the tutor links
        - I should not see the student links
        - I shoul not see the admin links
        :return:
        """
        self.login(self.tutor.person.user.username, 'password123')
        self.check_page_contains_ids(self.dashboard_config.get('TUTOR_LINKS'))
        self.check_page_not_contains_ids(self.dashboard_config.get('STUDENT_LINKS'))
        self.check_page_not_contains_ids(self.dashboard_config.get('ADMIN_LINKS'))


class PhdLoginTestCase(FunctionalTestCase, PhdMixin):

    @classmethod
    def setUpClass(cls):
        super(PhdLoginTestCase, cls).setUpClass()
        cls.dashboard_config = cls.config.get('DASHBOARD')

    def setUp(self):
        super(PhdLoginTestCase, self).setUp()
        self.phd_person = self.create_phd()

    def test_phd_login(self):
        """
        As a phd
        - I should be able to connect
        - I should see the tutor links
        - I should see the student links
        - I shoul not see the admin links
        :return:
        """
        self.login(self.phd_person.user.username, 'password123')
        self.check_page_contains_ids(self.dashboard_config.get('TUTOR_LINKS'))
        self.check_page_contains_ids(self.dashboard_config.get('STUDENT_LINKS'))
        self.check_page_not_contains_ids(self.dashboard_config.get('ADMIN_LINKS'))


class AdminLoginTestCase(FunctionalTestCase, AdministratorMixin):

    @classmethod
    def setUpClass(cls):
        super(AdminLoginTestCase, cls).setUpClass()
        cls.dashboard_config = cls.config.get('DASHBOARD')

    def setUp(self):
        super(AdminLoginTestCase, self).setUp()
        self.admin = self.create_admin()

    def test_admin_login(self):
        """
        As an administrator
        - I should be able to connect
        - I should see the tutor links
        - I should see the student links
        - I shoul see the admin links
        :return:
        """
        self.login(self.admin.user.username, 'password123')
        self.check_page_contains_ids(self.dashboard_config.get('TUTOR_LINKS'))
        self.check_page_contains_ids(self.dashboard_config.get('STUDENT_LINKS'))
        self.check_page_contains_ids(self.dashboard_config.get('ADMIN_LINKS'))

