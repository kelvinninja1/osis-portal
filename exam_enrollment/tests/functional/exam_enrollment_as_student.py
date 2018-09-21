from base.tests.functional.models.user_type import StudentMixin
from osis_common.tests.functional.models.model import FunctionalTestCase
from osis_common.tests.functional.models.report import can_be_reported
from base.models import academic_year as mdl_academic_year, offer_enrollment as mdl_offer_enrollment


class StudentWithoutProgramResgistrationTestCase(FunctionalTestCase, StudentMixin):
    """
    Test cases for student that are no registered to any program
    """

    def setUp(self):
        super(StudentWithoutProgramResgistrationTestCase, self).setUp()
        self.init_academic_years(start_year=2018)
        self.student = self.create_student()

    @can_be_reported
    def test_warning_message_is_shown(self):
        """
        As a student
        If I have no program registration
        When I click "Exam Enrollment" link in my dashboard
         - I should stay on the dashboard page
         - I should see a warning message
        """
        self.login(self.student.person.user.username)
        self.click_element_by_id('lnk_exam_enrollment_offer_choice')
        self.check_page_contains_string(self.get_localized_message('no_offer_enrollment_found',
                                                                   self.student.person.language).format(mdl_academic_year.current_academic_year()))


class StudentWithOfferRegistrationTestCase(FunctionalTestCase, StudentMixin):
    """
    Test case for students with valid offer registration
    """

    def setUp(self):
        super(StudentWithOfferRegistrationTestCase, self).setUp()
        self.init_academic_years(start_year=2018)
        self.student = self.create_student_with_offer_registration(year=2018)

    @can_be_reported
    def test_can_access_offers_list(self):
        """
        As a student
        If I have at least one offer registration
        When I go to the "Exams Enrollment" page
        - I should see an informative message
        - I should see my offers list
        """
        self.__got_to_offer_list()
        self.wait_until_title_is('Exam Enrollment Offers Choice')
        self.check_page_contains_string(self.get_localized_message('choose_offer_for_exams_enrollment', self.student.person.language))
        offer_enrollments = mdl_offer_enrollment.find_by_student_academic_year(self.student, mdl_academic_year.current_academic_year())
        offer_enrollment_links = ["lnk_offer_enrollment_{}".format(oe.offer_year.id) for oe in offer_enrollments]
        self.check_page_contains_links(offer_enrollment_links)

    def __got_to_offer_list(self):
        self.login(self.student.person.user.username)
        self.click_element_by_id('lnk_exam_enrollment_offer_choice')