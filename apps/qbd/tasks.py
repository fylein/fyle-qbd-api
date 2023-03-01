
import os
import logging
import traceback
from datetime import datetime

from django.core.exceptions import ObjectDoesNotExist
from django.db import transaction

from python_http_client.exceptions import HTTPError

from apps.utils.email import send_email
from apps.fyle.models import Expense
from apps.fyle.helpers import upload_iif_to_fyle

from apps.tasks.models import AccountingExport
from apps.utils.iif_generator import QBDIIFGenerator
from apps.workspaces.models import AdvancedSetting

from .helpers import (
    generate_all_bills,
    generate_all_credit_card_purchases,
    generate_all_journals
)


logger = logging.getLogger(__name__)


def email_iif_file(file_path: str, workspace_id: int):
    """
    Email IIF file to the user using sendgrid
    """
    advanced_settings = AdvancedSetting.objects.get(workspace_id=workspace_id)

    if advanced_settings.emails_selected:
        send_email(advanced_settings.emails_selected, file_path)


def create_bills_iif_file(workspace_id: int, accounting_export: AccountingExport):
    """
    Create Bills IIF file
    """
    try:
        accounting_export.status = 'IN_PROGRESS'
        accounting_export.save()

        workspace_name = accounting_export.workspace.name

        file_path = os.path.join('/tmp', '{}-{}-bills-{}.iif'.format(workspace_name, accounting_export.id, datetime.now().strftime('%Y-%m-%d')))

        expenses = Expense.objects.filter(
            workspace_id=workspace_id,
            exported=False,
            fund_source='PERSONAL'
        ).all()

        if expenses:
            with transaction.atomic():
                all_bills = generate_all_bills(expenses, accounting_export, workspace_id)
                iif_generator = QBDIIFGenerator(file_path)
                iif_generator.generate_iif_file(all_bills, 'BILL')

                file = upload_iif_to_fyle(file_path, workspace_id)

                expenses.update(exported=True)

                accounting_export.file_id = file['id']

                email_iif_file(file_path, workspace_id=workspace_id)

        accounting_export.errors = None
        accounting_export.status = 'COMPLETE'
        accounting_export.save()

    except ObjectDoesNotExist as exception:
        accounting_export.errors = {
            'message': exception.args[0]
        }
        accounting_export.status = 'FAILED'
        accounting_export.save()

    except HTTPError as e:
        logger.error('Something went wrong while sending email', e.__dict__)
        accounting_export.status = 'FAILED'
        accounting_export.save()

    except Exception:
        error = traceback.format_exc()
        accounting_export.errors = {
            'error': error
        }
        accounting_export.status = 'FATAL'
        accounting_export.save()
        logger.exception('Something unexpected happened workspace_id: %s %s', accounting_export.workspace_id, accounting_export.errors)


def create_credit_card_purchases_iif_file(workspace_id: int, accounting_export: AccountingExport):
    """
    Create Credit Card Purchases IIF file
    """
    try:
        accounting_export.status = 'IN_PROGRESS'
        accounting_export.save()

        workspace_name = accounting_export.workspace.name

        file_path = os.path.join('/tmp', '{}-{}-credit-card-purchases-{}.iif'.format(workspace_name, accounting_export.id, datetime.now().strftime('%Y-%m-%d')))
        
        expenses = Expense.objects.filter(
            workspace_id=workspace_id,
            exported=False,
            fund_source='CCC'
        ).all()

        if expenses:
            with transaction.atomic():
                all_credit_card_purchases = generate_all_credit_card_purchases(expenses, accounting_export, workspace_id)
                iif_generator = QBDIIFGenerator(file_path)
                iif_generator.generate_iif_file(all_credit_card_purchases, 'CREDIT_CARD_PURCHASE')

                file = upload_iif_to_fyle(file_path, workspace_id)

                expenses.update(exported=True)

                accounting_export.file_id = file['id']

                email_iif_file(file_path, workspace_id=workspace_id)

        accounting_export.errors = None
        accounting_export.status = 'COMPLETE'
        accounting_export.save()

    except ObjectDoesNotExist as exception:
        accounting_export.errors = {
            'message': exception.args[0]
        }
        accounting_export.status = 'FAILED'
        accounting_export.save()

    except HTTPError as e:
        logger.error('Something went wrong while sending email', e.__dict__)
        accounting_export.status = 'FAILED'
        accounting_export.save()

    except Exception:
        error = traceback.format_exc()
        logger.exception('Something unexpected happened workspace_id: %s %s', accounting_export.workspace_id, accounting_export.errors)

        accounting_export.errors = {
            'error': error
        }
        accounting_export.status = 'FATAL'
        accounting_export.save()
        logger.exception('Something unexpected happened workspace_id: %s %s', accounting_export.workspace_id, accounting_export.errors)


def create_journals_iif_file(workspace_id: int, accounting_export: AccountingExport, fund_source: str):
    """
    Create Journals IIF file
    """
    try:
        accounting_export.status = 'IN_PROGRESS'
        accounting_export.save()

        workspace_name = accounting_export.workspace.name

        file_path = os.path.join('/tmp', '{}-{}-journals-{}.iif'.format(workspace_name, accounting_export.id, datetime.now().strftime('%Y-%m-%d')))
        
        expenses = Expense.objects.filter(
            workspace_id=workspace_id,
            exported=False,
            fund_source=fund_source
        ).all()

        if expenses:
            with transaction.atomic():
                all_journals = generate_all_journals(
                    expenses, accounting_export, fund_source, workspace_id
                )
                iif_generator = QBDIIFGenerator(file_path)
                iif_generator.generate_iif_file(all_journals, 'JOURNAL_ENTRY')

                file = upload_iif_to_fyle(file_path, workspace_id)

                expenses.update(exported=True)

                accounting_export.file_id = file['id']

                email_iif_file(file_path, workspace_id=workspace_id)

        accounting_export.errors = None
        accounting_export.status = 'COMPLETE'
        accounting_export.save()

    except ObjectDoesNotExist as exception:
        accounting_export.errors = {
            'message': exception.args[0]
        }
        accounting_export.status = 'FAILED'
        accounting_export.save()

    except HTTPError as e:
        logger.error('Something went wrong while sending email', e.__dict__)
        accounting_export.status = 'FAILED'
        accounting_export.save()

    except Exception:
        error = traceback.format_exc()
        logger.exception('Something unexpected happened workspace_id: %s %s', accounting_export.workspace_id, accounting_export.errors)

        accounting_export.errors = {
            'error': error
        }
        accounting_export.status = 'FATAL'
        accounting_export.save()
        logger.exception('Something unexpected happened workspace_id: %s %s', accounting_export.workspace_id, accounting_export.errors)
