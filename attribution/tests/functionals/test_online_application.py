from random import randint, random

import time
import tempfile
import datetime
import pendulum
from django.contrib.auth.models import Group, Permission

from django.core.urlresolvers import reverse

from attribution.business import tutor_application
from attribution.tests.factories.attribution import AttributionFactory, AttributionNewFactory
from base.models.enums import academic_calendar_type, learning_unit_year_subtypes, vacant_declaration_type, \
    learning_component_year_type, component_type
from base.tests.factories.academic_calendar import AcademicCalendarFactory
from base.tests.factories.academic_year import AcademicYearFactory
from base.tests.factories.learning_component_year import LearningComponentYearFactory
from base.tests.factories.learning_container_year import LearningContainerYearFactory
from base.tests.factories.learning_unit import LearningUnitFactory
from base.tests.factories.learning_unit_component import LearningUnitComponentFactory
from base.tests.factories.learning_unit_year import LearningUnitYearFactory
from base.tests.factories.person import PersonFactory
from base.tests.factories.tutor import TutorFactory
from base.tests.factories.user import UserFactory, SuperUserFactory
from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from urllib import request
from django.utils.translation import ugettext_lazy as _
from selenium import webdriver

try:
    import pyvirtualdisplay

    HAS_VIRTUAL_DISPLAY = True
except ImportError:
    HAS_VIRTUAL_DISPLAY = False




SIZE =(1920, 1080)
GLOBAL_ID = '0001'


class BusinessMixin:
    #crée un utilisateur avec Faker comme générateur de valeurs + passwd123
    def create_user(self):
        user = UserFactory()
        print("User {} / {} {} created".format(user.username, user.first_name, user.last_name))
        return user
    #spécifie l'utilisateur est "super user"
    def create_super_user(self):
        superUser = SuperUserFactory()
        print("User {} {} created".format(superUser.username, superUser.last_name))
        return superUser

    #ajouter l'utilisateur dans une ou plusieurs groupes
    def add_group(self, user, *group_names):
        for name in group_names:
            group, created = Group.objects.get_or_create(name=name)
            group.user_set.add(user)

    def create_tutor(self, user):
        person = PersonFactory(user=user, language='fr-be', global_id=GLOBAL_ID)
        return TutorFactory(person=person)


    def create_learning_units(self,academic_year,cnum):
        #learning_unit_year = LearningUnitYearFactory(academic_year=academic_year)
        learning_unit = LearningUnitFactory(acronym="LBIOL{}".format(cnum))
        learning_unit_year = LearningUnitYearFactory(academic_year=academic_year,learning_unit=learning_unit)
        print("learning_unit created {} {}".format(learning_unit_year.learning_unit.acronym, learning_unit_year.learning_unit.title, ))
        return learning_unit_year

    #donner à l'utilisateur une ou plusieurs permissions.
    #une permission est composée par le label et le code
    def add_permission(self, user, permission):
        label, codename = permission.split('.')
        permission = Permission.objects.get(codename=codename, content_type__app_label=label)
            #else:
            #    permission = Permission.objects.get(codename=permission)
        user.user_permissions.add(permission)

    def create_tutor_with_permission(self, user, permission):
        self.add_permission(user, permission)
        turor = self.create_tutor(user)
        print("Permission given to tutor {}, {} {} {}'".format(turor.external_id, user.last_name, user.username, user.first_name))
        return turor




class SeleniumTest_On_Line_Application(StaticLiveServerTestCase, BusinessMixin):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.display = pyvirtualdisplay.Display(size=SIZE) #crée un virtuel display
        #cls.display = Xvfb()
        # cls.display.start()
        options = webdriver.ChromeOptions()
        cls.driver = webdriver.Chrome(chrome_options=options)
        cls.driver.implicitly_wait(10)
        cls.driver.set_window_size(*SIZE)

    def setUp(self):
        self.user = self.create_user()

        groupe_list = []
        group, created = Group.objects.get_or_create(name='tutors')
        groupe_list.append(group)

        group, created = Group.objects.get_or_create(name='authorisations_manager')
        groupe_list.append(group)

        group, created = Group.objects.get_or_create(name='administrators')
        groupe_list.append(group)

        self.add_group(self.user, *groupe_list)
        permission = 'attribution.can_access_attribution_application'

        self.tutor = self.create_tutor_with_permission(self.user, permission)

        # Create current academic year
        current_academic_year = AcademicYearFactory(year=pendulum.today().year - 1)
        # Create application year
        self.next_academic_year = AcademicYearFactory(year=pendulum.today().year)

        # Create Event to allow teacher to register
        today = datetime.datetime.today()
        start_date = today - datetime.timedelta(days=10)
        end_date = today + datetime.timedelta(days=15)
        AcademicCalendarFactory(academic_year=current_academic_year,
                                start_date=start_date,
                                end_date=end_date,
                                reference=academic_calendar_type.TEACHING_CHARGE_APPLICATION)

        self.learning_unit_dict = {}
        self.learning_container_dict = {}
        volume_lecturing = 70
        volume_practical = 70
        # 4 UE, la dernière ne sera pas vacante, l'avant dernière sera vacante, les deux premières avec une
        # possibilité de reconduction
        for counter in range(0, 4):
            acronym = "LBIOL100{}".format(counter)
            l_container_current = self.create_learning_container(acronym, current_academic_year)

            subtype = learning_unit_year_subtypes.FULL

            learning_unit_year_current = self.link_components_and_learning_unit_year_to_container(l_container_current,
                                                                                                  acronym,
                                                                                                  volume_lecturing,
                                                                                                  volume_practical,
                                                                                                  subtype)

            # type_declaration_vacant = vacant_declaration_type.RESEVED_FOR_INTERNS
            if counter < 3:
                l_container_next_year = self.create_learning_container(acronym, self.next_academic_year)

                l_container_next_year = self.link_components_and_learning_unit_year_to_container(l_container_next_year,
                                                                                                 acronym,
                                                                                                 volume_lecturing,
                                                                                                 volume_practical,
                                                                                                 subtype)
            self.learning_unit_dict[counter] = learning_unit_year_current
            self.learning_container_dict[counter] = l_container_current

        # créer des charges existantes
        applications = []
        attributions = []
        for counter in range(0, 2):
            l_container = self.learning_container_dict[counter]
            applications.append(self.get_application_example(l_container, volume_lecturing, volume_practical))
            attributions.append(self.get_attributions_example(l_container, volume_lecturing, volume_practical))

        self.create_or_update_application_creation_on_existing_user(self.tutor, attributions, applications)

        # créer un dossier temp
        self.folder_name = tempfile.mkdtemp()
        self.counter_img = 0
        self.name_img_screen = 'online_apply'
        self.ext = "png"


    @classmethod
    def tearDownClass2(cls):
        cls.driver.quit()
        # cls.display.stop()
        super().tearDownClass()

    # retourne l'url de la page
    def get_url_by_name(self, url_name, *args, **kwargs):
       return request.urljoin(self.live_server_url,
                              reverse(url_name, args=args, kwargs=kwargs))

        # permet d'aller sur une vue django
    def goto(self, url_name, *args, **kwargs):
        url = self.get_url_by_name(url_name, *args, **kwargs)
        self.driver.get(url)


    def fill_by_id(self, element_id, value):
        element = self.driver.find_element_by_id(element_id)
        element.clear()
        element.send_keys(value)

    def click_on(self, element_id):
        element = self.driver.find_element_by_id(element_id)
        element.click()


    def login(self, username, password ='password123'):
        self.fill_by_id('id_username', username)
        self.fill_by_id('id_password', password)
        self.click_on('post_login_btn')

    def open_browser_and_log_on_user(self, url, user):
        url = self.goto(url)
        self.driver.save_screenshot('/home/nizeyimana/Images/start_url.png')
        self.login(user.username)
        self.driver.save_screenshot('/home/nizeyimana/Images/login.png')
        # import pdb; pdb.set_trace()
        #assert 'OSIS' in self.driver.title

    def link_components_and_learning_unit_year_to_container(self, l_container, acronym,
                                                             volume_lecturing=None,
                                                             volume_practical_exercices=None,
                                                             subtype=learning_unit_year_subtypes.FULL):
        a_learning_unit_year = LearningUnitYearFactory(acronym=acronym, academic_year=l_container.academic_year,
                                                       specific_title=l_container.common_title, subtype=subtype)
        if volume_lecturing:
            a_component = LearningComponentYearFactory(
                learning_container_year=l_container,
                type=learning_component_year_type.LECTURING,
                volume_declared_vacant=volume_lecturing
            )
            LearningUnitComponentFactory(learning_unit_year=a_learning_unit_year, learning_component_year=a_component,
                                         type=component_type.LECTURING)
        if volume_practical_exercices:
            a_component = LearningComponentYearFactory(
                learning_container_year=l_container,
                type=learning_component_year_type.PRACTICAL_EXERCISES,
                volume_declared_vacant=volume_practical_exercices
            )
            LearningUnitComponentFactory(learning_unit_year=a_learning_unit_year, learning_component_year=a_component,
                                         type=component_type.PRACTICAL_EXERCISES)
        return a_learning_unit_year

    def create_learning_container(self,acronym, academic_year, type_declaration_vacant=vacant_declaration_type.RESEVED_FOR_INTERNS):

        l_container = LearningContainerYearFactory(acronym=acronym, academic_year=academic_year,
                                                   type_declaration_vacant=type_declaration_vacant)
        print("le conteneur créé est : {}, {}, {}".format(l_container.academic_year, l_container.acronym, l_container.type_declaration_vacant))
        return l_container




    def get_application_example(self, learning_container_year, volume_lecturing, volume_practical_exercice, flag=None):
        return {
            'remark': 'This is the remarks',
            'course_summary': 'This is the course summary',
            'charge_lecturing_asked': volume_lecturing,
            'charge_practical_asked': volume_practical_exercice,
            'acronym': learning_container_year.acronym,
            'year': learning_container_year.academic_year.year,
            'pending': flag
        }


    def get_attributions_example(self, learning_container_year, volume_lecturing, volume_practical):

        return {'year': learning_container_year.academic_year.year, 'acronym': learning_container_year.acronym ,
                'title': 'Biologie complexe', 'weight': '70.00', 'LECTURING': volume_lecturing,
                'PRACTICAL_EXERCISES':volume_practical, 'function':'HOLDER', 'end_year' : learning_container_year.academic_year.year}


    def create_or_update_application_creation_on_existing_user(self, tutor, attributions, applications):
        return AttributionNewFactory(global_id=tutor.person.global_id,
                                     attributions=attributions, applications=applications)

    def save_screen(self, folder_name, name_img_screen, counter_img, ext):
        self.driver.save_screenshot('{}/{}{}.{}'.format(folder_name, name_img_screen, counter_img, ext))

    def assert_same_message(self, msg_output, message, **kwargs):
        messr = _(message)
        print('Message à verifier : "{}"'.format(messr))
        self.assertEqual(msg_output, str(messr).format(**kwargs))


    def assert_contains_message(self, msg_output, id_message):
        print('Message verifié : "{}"'.format(_(id_message)))
        messr =str(_(id_message))
        messr = messr.replace('(', '')
        messr = messr.replace(')', '')
        msg_output = str(msg_output).replace('(', '')
        msg_output = str(msg_output).replace(')', '')
        if len(messr) > len(msg_output):
            self.assertIn(msg_output.lower(), messr.lower())
        else:
            self.assertIn(messr.lower(), msg_output.lower())


    def print_not_supported_value(self, value, error_message):
        print('Donnée invalide rejetée est : "{}" et le message de rejet est : "{}"'.format(value,
                                                                                            error_message))
    def test_01(self):

        self.open_browser_and_log_on_user('login', self.user)
        print("connected to : {}".format(self.driver.current_url))
        self.goto('applications_overview')
        element_online_appl = self.driver.find_elements_by_xpath('/ html / body / div[2] / h1')
        self.assertEquals(element_online_appl[0].text, 'Mes candidatures')
        self.click_on("lnk_submit_attribution_new")
        self.save_screen(self.folder_name, self.name_img_screen, self.counter_img, self.ext)

        element_online_appl = self.driver.find_elements_by_xpath('// *[ @ id = "pnl_charges"] / div[1]')
        self.assertEquals(element_online_appl[0].text,'Cours vacant')
        #tester si on est sur la bonne page


        for counter in range(0, 4):
            learning_unit_year_test = self.learning_unit_dict[counter]
            self.fill_by_id("id_learning_container_acronym", learning_unit_year_test.acronym)
            self.click_on("bt_submit_vacant_attributions_search")
            if counter == 3:
                alert_element = self.driver.find_element_by_css_selector("#pnl_charges > div.panel-body > div.alert.alert-info")
                not_found_message = alert_element.text
                self.assert_same_message(not_found_message, 'no_activity')
            else:
                element_submit = self.driver.find_elements_by_id('lnk_submit_attribution_new')
                el = self.driver.find_element_by_xpath(
                    '// *[ @ id = "pnl_charges"] / div[2] / table / tbody / tr / td[1] / a')
                self.assertEquals(el.text, learning_unit_year_test.acronym)
                self.assert_same_message(element_submit[0].text, 'create_an_tutor_application')
            time.sleep(3)

        #tester si on met rien
        element_input =self.driver.find_element_by_id('id_learning_container_acronym')
        element_input.clear()
        self.click_on("bt_submit_vacant_attributions_search")
        element_message = self.driver.find_element_by_css_selector ('#pnl_charges > div.panel-body > div > form > div.col-md-10 > p')
        self.assert_same_message(element_message.text, 'lu_search_explanation')
        time.sleep(3)

        # postuler sur le premier cours
        ue_key = 2
        learning_unit_year_test = self.learning_unit_dict[ue_key]
        self.fill_by_id("id_learning_container_acronym", learning_unit_year_test.acronym)
        self.click_on("bt_submit_vacant_attributions_search")
        self.click_on("lnk_submit_attribution_new")
        el = self.driver.find_element_by_xpath('//*[@id="pnl_application_form"]/div[2]/form/div[1]/div[1]')
        pos = el.text.find('\n')+len('\n')
        self.assertEquals(el.text[pos:len(el.text)], learning_unit_year_test.acronym)

        #tester d'abord le bouton "annuler"

        self.driver.find_element_by_link_text('Annuler').click()

        self.counter_img += 1
        self.save_screen(self.folder_name, self.name_img_screen, self.counter_img, self.ext)
        #retour à la nouvelle candidature pour un nouveau cours

        self.click_on("lnk_submit_attribution_new")
        self.counter_img += 1
        self.save_screen(self.folder_name, self.name_img_screen, self.counter_img, self.ext)
        self.fill_by_id("id_learning_container_acronym",  learning_unit_year_test.acronym)
        self.counter_img += 1
        self.save_screen(self.folder_name, self.name_img_screen, self.counter_img, self.ext)
        time.sleep(2)
        self.click_on("bt_submit_vacant_attributions_search")
        self.counter_img += 1
        self.save_screen(self.folder_name, self.name_img_screen, self.counter_img, self.ext)
        self.click_on("lnk_submit_attribution_new")

        volume_lecturing_asked = "aba"
        volume_practical_asked = -10
        id_element_lecturing_asked = "id_charge_lecturing_asked"
        self.fill_by_id(id_element_lecturing_asked, volume_lecturing_asked)
        id_element_practical_asked = "id_charge_practical_asked"

        self.fill_by_id(id_element_practical_asked, volume_practical_asked)
        self.click_on("bt_submit")
        self.counter_img += 1
        self.save_screen(self.folder_name, self.name_img_screen, self.counter_img, self.ext)
        time.sleep(2)

        element_error_01 = self.driver.find_element_by_css_selector(
            "#pnl_application_form > div.panel-body > form > div:nth-child(7) > div:nth-child(1) > span")
        self.assert_same_message(element_error_01.text,'Enter a number.')

        self.print_not_supported_value(volume_lecturing_asked,element_error_01.text)

        element_error_02 = self.driver.find_element_by_css_selector(
            "#pnl_application_form > div.panel-body > form > div:nth-child(7) > div:nth-child(2) > span")
        self.assert_same_message(element_error_02.text, 'Ensure this value is greater than or equal to {min_value}.',
                                 min_value=0)

        self.print_not_supported_value(volume_practical_asked, element_error_02.text)

        volume_lecturing_asked = -10
        volume_practical_asked = "abc"
        self.fill_by_id(id_element_lecturing_asked, volume_lecturing_asked)

        self.fill_by_id(id_element_practical_asked, volume_practical_asked)
        self.click_on("bt_submit")

        self.counter_img += 1
        self.save_screen(self.folder_name, self.name_img_screen, self.counter_img, self.ext)
        element_error_01 = self.driver.find_element_by_css_selector(
            "#pnl_application_form > div.panel-body > form > div:nth-child(7) > div:nth-child(1) > span")
        self.assert_same_message(element_error_01.text, 'Ensure this value is greater than or equal to {min_value}.',
                                 min_value=0)
        self.print_not_supported_value(volume_lecturing_asked, element_error_01.text)

        element_error_02 = self.driver.find_element_by_css_selector(
            "#pnl_application_form > div.panel-body > form > div:nth-child(7) > div:nth-child(2) > span")

        self.assert_same_message(element_error_02.text, 'Enter a number.')

        self.print_not_supported_value(volume_practical_asked, element_error_02.text)
        time.sleep(2)

        volume_lecturing_asked = 70.01
        volume_practical_asked = 1003
        self.fill_by_id(id_element_lecturing_asked, volume_lecturing_asked)

        self.fill_by_id(id_element_practical_asked, volume_practical_asked)
        self.click_on("bt_submit")
        self.counter_img += 1
        self.save_screen(self.folder_name, self.name_img_screen, self.counter_img, self.ext)

        element_error_01 = self.driver.find_element_by_css_selector(
            "#pnl_application_form > div.panel-body > form > div:nth-child(6) > div:nth-child(1) > span")

        self.print_not_supported_value(volume_lecturing_asked, element_error_01.text)

        element_error_02 = self.driver.find_element_by_css_selector(
            "#pnl_application_form > div.panel-body > form > div:nth-child(6) > div:nth-child(2) > span")
        self.assert_contains_message(element_error_02.text,'too_much')
        self.print_not_supported_value(volume_practical_asked, element_error_02.text)
        time.sleep(2)


        volume_lecturing_asked = 35
        volume_practical_asked = 70
        self.fill_by_id("id_charge_lecturing_asked", volume_lecturing_asked)

        self.fill_by_id("id_charge_practical_asked", volume_practical_asked)
        self.click_on("bt_submit")

        el = self.driver.find_element_by_xpath('// *[ @ id = "pnl_applications"] / div[1]')

        next_year = (self.next_academic_year.year + 1) % 100
        text_check = 'Mes candidatures {}-{}'.format(self.next_academic_year.year, next_year)
        print(text_check)
        self.assertEquals(el.text, text_check)
        el = self.driver.find_element_by_css_selector('#pnl_applications > div.panel-body > table > tbody > tr > td:nth-child(1) > span:nth-child(1)')
        self.assertEquals(el.text, learning_unit_year_test.acronym)

        self.counter_img += 1
        self.save_screen(self.folder_name, self.name_img_screen, self.counter_img, self.ext)


        tutor_application.validate_application(GLOBAL_ID, learning_unit_year_test.acronym, self.next_academic_year.year)
        #recharger pour voir si possibilité de modifier
        self.goto('applications_overview')
        self.counter_img += 1
        self.save_screen(self.folder_name, self.name_img_screen, self.counter_img, self.ext)

        time.sleep(2)
        #tester le suppression
        self.click_on("lnk_application_delete_{}".format(ue_key*3))
        alert = self.driver.switch_to.alert
        #tester l'action d'annuler (bouton popup)
        alert.dismiss()
        time.sleep(2)


        self.click_on("lnk_application_delete_{}".format(ue_key*3))
        alert = self.driver.switch_to.alert
        #tester l'action de confirmer
        alert.accept()
        time.sleep(2)
        self.counter_img += 1
        self.save_screen(self.folder_name, self.name_img_screen, self.counter_img, self.ext)

        #valider la suppression
        learning_container_year = self.learning_container_dict[ue_key]
        tutor_application.delete_application(self.tutor.person.global_id, learning_unit_year_test.acronym,
                                             learning_container_year.academic_year.year + 1)

        #pour verifier que la candidature sur l'UE est supprimée, rechercher l'UE pour verifier qu'il est vacant
        self.goto('applications_overview')
        time.sleep(2)
        #créer de nouveau une nouvelle candidature sur le mëme cours
        self.click_on("lnk_submit_attribution_new")
        self.fill_by_id("id_learning_container_acronym", learning_unit_year_test.acronym)
        self.click_on("bt_submit_vacant_attributions_search")
        time.sleep(2)
        self.click_on("lnk_submit_attribution_new")
        time.sleep(2)

        volume_lecturing_asked = 40.5
        volume_practical_asked = 29.5
        self.fill_by_id("id_charge_lecturing_asked", volume_lecturing_asked)

        self.fill_by_id("id_charge_practical_asked", volume_practical_asked)
        self.click_on("bt_submit")
        time.sleep(2)

        tutor_application.validate_application(GLOBAL_ID, learning_unit_year_test.acronym, self.next_academic_year.year)
        # recharger pour voir si possibilité de modifier
        self.goto('applications_overview')

        self.click_on("lnk_application_edit_{}".format(ue_key * 3))

        proposition = "Proposition de Test 1"
        id_element_proposion = "id_course_summary"
        self.fill_by_id(id_element_proposion, proposition)
        time.sleep(2)
        remark = "Remarque de Test 1"
        id_element_remark = "id_remark"
        self.fill_by_id("id_remark", remark)
        time.sleep(2)
        self.click_on("bt_submit")

        tutor_application.validate_application(GLOBAL_ID, learning_unit_year_test.acronym, self.next_academic_year.year)

        # recharger pour voir si possibilité de modifier
        self.goto('applications_overview')
        self.counter_img += 1
        self.save_screen(self.folder_name, self.name_img_screen, self.counter_img, self.ext)
        #puis tester la modification
        self.click_on("lnk_application_edit_{}".format(ue_key*3))
        self.counter_img += 1
        self.save_screen(self.folder_name, self.name_img_screen, self.counter_img, self.ext)
        time.sleep(2)

        #vérifier que les modif encodées ont été enregistrées

        element_proposition = self.driver.find_element_by_id(id_element_proposion)
        self.assertEqual(element_proposition.text, proposition)
        # assert(element_proposition.text==proposition)
        element_remark = self.driver.find_element_by_id(id_element_remark)
        # assert (element_remark.text == remark)
        self.assertEqual(element_remark.text, remark)

        time.sleep(2)
        self.driver.find_element_by_link_text('Annuler').click()
        self.counter_img += 1
        self.save_screen(self.folder_name, self.name_img_screen, self.counter_img, self.ext)

        print('TEST OK POUR "NOUVELLE CANDIDATURE"')

        #tester le check box tout sélectionner/déselectionner et valider

        print('DEBUT TEST POUR "RECONDUIRE CANDIDATURE"')

        print("Sélectionner tout")

        self.click_on('chb_renew_all')
        for counter in (1, 2):
            element_check = self.driver.find_element_by_id("chb_attribution_renew_{}".format(counter))
            self.assertTrue(element_check.is_selected())
            # assert(element_check.is_selected())
            print("{} {}".format(counter, element_check.text))

        print('Ok : "Sélectionner tout"')

        time.sleep(3)

        print("Désélectionner tout")

        self.click_on('chb_renew_all')
        for counter in (0, 1):
            element_check = self.driver.find_element_by_id("chb_attribution_renew_{}".format(counter + 1))
            self.assertFalse(element_check.is_selected())

        print('Ok : "Désélectionner tout"')
        time.sleep(3)

        self.click_on('chb_renew_all')
        self.click_on("bt_submit_attribution_renew")
        for counter_row in range(2, 4):
             element_in_waiting_validation = self.driver.find_elements_by_css_selector('#pnl_applications > div.panel-body > table > tbody > tr:nth-child({}) > td:nth-child(1) > span.small.font-italic'.format(counter_row))
             self.assert_contains_message(element_in_waiting_validation[0].text, 'applications_in_pending_state')

        print("Envoi du message")
        self.click_on('btn_applications_email_confirmtion')
        # Aucun message n'a été envoyé : le modèle de message applications_confirmation_html n'existe pas.

        #valider tous les candidature en attente
        #le code ci dessous ne fonctionne pas :  à voir avec Allessandro
        for counterNa in range(0, 2):
            learning_unit_year_test = self.learning_unit_dict[counterNa]
            tutor_application.validate_application(GLOBAL_ID, learning_unit_year_test.acronym, self.next_academic_year.year)
            time.sleep(5)







