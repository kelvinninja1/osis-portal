##############################################################################
#
#    OSIS stands for Open Student Information System. It's an application
#    designed to manage the core business of higher education institutions,
#    such as universities, faculties, institutes and professional schools.
#    The core business involves the administration of students, teachers,
#    courses, programs and so on.
#
#    Copyright (C) 2015-2018 Université catholique de Louvain (http://www.uclouvain.be)
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    A copy of this license - GNU General Public License - is available
#    at the root of the source code of this program.  If not,
#    see http://www.gnu.org/licenses/.
#
##############################################################################
import json
import logging
import time

from psycopg2._psycopg import OperationalError as PsycopOperationalError, InterfaceError as PsycopInterfaceError
from django.db import connection
from django.db.utils import OperationalError as DjangoOperationalError, InterfaceError as DjangoInterfaceError
from django.conf import settings

from osis_common.queue import queue_sender
from base import models as mdl_base


DELETE_OPERATION = "delete"
UPDATE_OPERATION = "update"
ERROR_EPC_FIELD = "error"
LEARNING_CONTAINER_YEAR_PREFIX_EXTERNAL_ID = "osis.learning_container_year_"
TUTOR_PREFIX_EXTERNAL_ID = "osis.tutor_"

logger = logging.getLogger(settings.DEFAULT_LOGGER)
queue_exception_logger = logging.getLogger(settings.QUEUE_EXCEPTION_LOGGER)


def send_message(operation, global_id, application):
    if operation not in (DELETE_OPERATION, UPDATE_OPERATION):
        raise ValueError('operation_not_supported')

    queue_name = settings.QUEUES.get('QUEUES_NAME', {}).get('APPLICATION_REQUEST')
    if queue_name:
        message_to_send = _convert_to_epc_application(application)
        message_to_send.update({
            'operation': operation,
            'global_id': global_id
        })
        queue_sender.send_message(queue_name, message_to_send)
        return True
    return False


def _convert_to_epc_application(application):
    acronym = application.get('acronym')
    year = application.get('year')

    return {
        'remark': application.get('remark'),
        'course_summary': application.get('course_summary'),
        'lecturing_allocation': str(application.get('charge_lecturing_asked', 0)),
        'practical_allocation': str(application.get('charge_practical_asked', 0)),
        'learning_container_year': _extract_learning_container_year_epc_info(acronym, year)
    }


def _extract_learning_container_year_epc_info(acronym, year):
    # Example of external_id osis.learning_container_year_428750_2017
    learning_container_year_info = {}
    academic_year = mdl_base.academic_year.find_by_year(year)
    l_container_year = mdl_base.learning_container_year.find_by_acronym(acronym=acronym,
                                                                        academic_year=academic_year).first()
    if academic_year and l_container_year and l_container_year.external_id:
        external_id = l_container_year.external_id.replace(LEARNING_CONTAINER_YEAR_PREFIX_EXTERNAL_ID, '')
        external_ids = external_id.split('_')
        if len(external_ids) >= 2:
            learning_container_year_info['reference'] = external_ids[0]
            learning_container_year_info['year'] = year
            learning_container_year_info['acronym'] = acronym
    return learning_container_year_info


def process_message(body):
    """
        Callback of APPLICATION_RESPONSE queue
    :param json_data:
    :return:
    """
    from attribution.business import tutor_application

    try:
        json_data = body.decode("utf-8")
        application = json.loads(json_data)

        # Check error in response from epc
        error_epc = application.get(ERROR_EPC_FIELD)
        if error_epc:
            logger.error('Error during processing tutor application in EPC: {} \n JSON: {}'.format(error_epc, str(json_data)))
            return False

        operation = application.get('operation')
        global_id = application.get('global_id')
        acronym = application.get('learning_container_year', {}).get('acronym')
        year = application.get('learning_container_year', {}).get('year')
        if not (global_id and acronym and year and operation):
            logger.error('Error during process tutor application message. Missing mandatory data')
            return False

        if operation == UPDATE_OPERATION:
            tutor_application.validate_application(global_id, acronym, year)
        elif operation == DELETE_OPERATION:
            tutor_application.delete_application(global_id, acronym, year)
        else:
            error_msg = 'Error during process tutor application message. Invalid operation {}'.format(str(operation))
            logger.error(error_msg)
    except (PsycopOperationalError, PsycopInterfaceError, DjangoOperationalError, DjangoInterfaceError):
        queue_exception_logger.exception('Postgres Error during process tutor application message => retried')
        connection.close()
        time.sleep(1)
        process_message(body)
    except Exception:
        logger.exception('(Not PostgresError) during process tutor application message. Cannot update ')
