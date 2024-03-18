
import pytest
from unittest import mock

from python_http_client.exceptions import HTTPError

from apps.fyle.models import Expense
from apps.fyle.tasks import import_credit_card_expenses, import_reimbursable_expenses
from apps.tasks.models import AccountingExport

from apps.qbd.tasks import (
    create_bills_iif_file,
    create_credit_card_purchases_iif_file,
    create_journals_iif_file
)

from tests.test_fyle.fixtures import fixtures as fyle_fixtures


@pytest.mark.django_db(databases=['default'])
def test_create_bills_iif_file_report(
        create_temp_workspace, add_accounting_export_bills, 
        add_accounting_export_expenses, add_fyle_credentials, 
        add_export_settings, add_field_mappings, add_advanced_settings,
        mocker
    ):
    """
    Test import reimbursable expenses task
    Plaform connector expenses calls to be mocked
    
    Requires the following DB Fixtures
    * apps.workspaces.models.Workspace
    * apps.workspacs.models.FyleCredential
    * apps.workspaces.models.ExportSettings

    * apps.tasks.models.AccountingExport
    """
    mocker.patch(
        'fyle.platform.apis.v1beta.admin.Expenses.list_all',
        return_value=fyle_fixtures['reimbursable_expenses']
    )

    mocker.patch(
        'fyle.platform.apis.v1beta.admin.Files.create_file',
        return_value=fyle_fixtures['create_file']
    )

    mocker.patch(
        'fyle.platform.apis.v1beta.admin.Files.bulk_generate_file_urls',
        return_value=fyle_fixtures['generate_file_urls']
    )

    mocker.patch(
        'fyle.platform.apis.v1beta.admin.Files.upload_file_to_aws',
        return_value=None
    )

    mocker.patch(
        'sendgrid.SendGridAPIClient.send',
        return_value=None
    )

    workspace_id = 1
    accounting_export = AccountingExport.objects.get(workspace_id=workspace_id, type='FETCHING_REIMBURSABLE_EXPENSES')
    accounting_export.workspace.org_id = 'orNoatdUnm1w'
    accounting_export.workspace.save()
    import_reimbursable_expenses(workspace_id, accounting_export)

    accounting_export = AccountingExport.objects.get(
        workspace_id=workspace_id, type='EXPORT_BILLS', status='ENQUEUED'
    )

    create_bills_iif_file(workspace_id, accounting_export)

    expenses = Expense.objects.filter(workspace_id=workspace_id, exported=False)

    assert expenses.count() == 0
    assert accounting_export.status == 'COMPLETE'
    assert accounting_export.bills.count() == 4

    for bill in accounting_export.bills.all():
        assert bill.workspace_id == workspace_id
        assert bill.accounting_export_id == accounting_export.id
        assert bill.bill_lineitems.count() >= 1


@pytest.mark.django_db(databases=['default'])
def test_create_bills_iif_file_report_fail(
        create_temp_workspace, add_accounting_export_bills, 
        add_accounting_export_expenses, add_fyle_credentials, 
        add_export_settings, add_advanced_settings, mocker
    ):
    """
    Test import reimbursable expenses task
    Plaform connector expenses calls to be mocked
    
    Requires the following DB Fixtures
    * apps.workspaces.models.Workspace
    * apps.workspacs.models.FyleCredential
    * apps.workspaces.models.ExportSettings

    * apps.tasks.models.AccountingExport
    """
    mocker.patch(
        'fyle.platform.apis.v1beta.admin.Expenses.list_all',
        return_value=fyle_fixtures['reimbursable_expenses']
    )

    mocker.patch(
        'fyle.platform.apis.v1beta.admin.Files.create_file',
        return_value=fyle_fixtures['create_file']
    )

    mocker.patch(
        'fyle.platform.apis.v1beta.admin.Files.bulk_generate_file_urls',
        return_value=fyle_fixtures['generate_file_urls']
    )

    mocker.patch(
        'fyle.platform.apis.v1beta.admin.Files.upload_file_to_aws',
        return_value=None
    )

    mocker.patch(
        'sendgrid.SendGridAPIClient.send',
        return_value=None
    )

    workspace_id = 1
    accounting_export = AccountingExport.objects.get(workspace_id=workspace_id, type='FETCHING_REIMBURSABLE_EXPENSES')
    accounting_export.workspace.org_id = 'orNoatdUnm1w'
    accounting_export.workspace.save()
    import_reimbursable_expenses(workspace_id, accounting_export)

    accounting_export = AccountingExport.objects.get(
        workspace_id=workspace_id, type='EXPORT_BILLS', status='ENQUEUED'
    )

    create_bills_iif_file(workspace_id, accounting_export)

    assert accounting_export.bills.count() == 0
    assert accounting_export.errors == {
        'message': 'FieldMapping matching query does not exist.'
    }
    assert accounting_export.status == 'FAILED'


@pytest.mark.django_db(databases=['default'])
def test_create_bills_iif_file_report_fatal(
        create_temp_workspace, add_accounting_export_bills, 
        add_accounting_export_expenses, add_fyle_credentials, 
        add_export_settings, add_field_mappings, add_advanced_settings,
        mocker
    ):
    """
    Test import reimbursable expenses task
    Plaform connector expenses calls to be mocked
    
    Requires the following DB Fixtures
    * apps.workspaces.models.Workspace
    * apps.workspacs.models.FyleCredential
    * apps.workspaces.models.ExportSettings

    * apps.tasks.models.AccountingExport
    """
    mocker.patch(
        'fyle.platform.apis.v1beta.admin.Expenses.list_all',
        return_value=fyle_fixtures['reimbursable_expenses']
    )

    mocker.patch(
        'fyle.platform.apis.v1beta.admin.Files.create_file',
        return_value=fyle_fixtures['create_file']
    )

    mocker.patch(
        'sendgrid.SendGridAPIClient.send',
        return_value=None
    )

    workspace_id = 1
    accounting_export = AccountingExport.objects.get(workspace_id=workspace_id, type='FETCHING_REIMBURSABLE_EXPENSES')
    accounting_export.workspace.org_id = 'orNoatdUnm1w'
    accounting_export.workspace.save()
    import_reimbursable_expenses(workspace_id, accounting_export)

    accounting_export = AccountingExport.objects.get(
        workspace_id=workspace_id, type='EXPORT_BILLS', status='ENQUEUED'
    )

    create_bills_iif_file(workspace_id, accounting_export)

    assert accounting_export.bills.count() == 0
    assert accounting_export.errors is not None
    assert accounting_export.status == 'FATAL'


@pytest.mark.django_db(databases=['default'])
def test_create_bills_iif_file_expense(
        create_temp_workspace, add_accounting_export_bills, 
        add_accounting_export_expenses, add_fyle_credentials, 
        add_export_settings, add_field_mappings, add_advanced_settings,
        mocker
    ):
    """
    Test import reimbursable expenses task
    Plaform connector expenses calls to be mocked
    
    Requires the following DB Fixtures
    * apps.workspaces.models.Workspace
    * apps.workspacs.models.FyleCredential
    * apps.workspaces.models.ExportSettings

    * apps.tasks.models.AccountingExport
    """
    mocker.patch(
        'fyle.platform.apis.v1beta.admin.Expenses.list_all',
        return_value=fyle_fixtures['reimbursable_expenses']
    )

    mocker.patch(
        'fyle.platform.apis.v1beta.admin.Files.create_file',
        return_value=fyle_fixtures['create_file']
    )

    mocker.patch(
        'fyle.platform.apis.v1beta.admin.Files.bulk_generate_file_urls',
        return_value=fyle_fixtures['generate_file_urls']
    )

    mocker.patch(
        'fyle.platform.apis.v1beta.admin.Files.upload_file_to_aws',
        return_value=None
    )

    mocker.patch(
        'sendgrid.SendGridAPIClient.send',
        return_value=None
    )

    workspace_id = 3
    accounting_export = AccountingExport.objects.get(workspace_id=workspace_id, type='FETCHING_REIMBURSABLE_EXPENSES')
    accounting_export.workspace.org_id = 'orNoatdUnm1w'
    accounting_export.workspace.save()
    import_reimbursable_expenses(workspace_id, accounting_export)

    accounting_export = AccountingExport.objects.get(
        workspace_id=workspace_id, type='EXPORT_BILLS', status='ENQUEUED'
    )

    create_bills_iif_file(workspace_id, accounting_export)

    expenses = Expense.objects.filter(workspace_id=workspace_id, exported=False)

    assert expenses.count() == 0
    assert accounting_export.status == 'COMPLETE'
    assert accounting_export.bills.count() == 5
    assert accounting_export.file_id == 'fimNloQVF0D8'

    for bill in accounting_export.bills.all():
        assert bill.workspace_id == workspace_id
        assert bill.accounting_export_id == accounting_export.id
        assert bill.bill_lineitems.count() == 1


@pytest.mark.django_db(databases=['default'])
def test_create_credit_card_purchases_iif_file_expense_vendor(
    create_temp_workspace, add_accounting_export_bills,
    add_accounting_export_expenses, add_fyle_credentials,
    add_export_settings, add_field_mappings, add_advanced_settings,
    mocker
):
    """
    Test create credit card purchases iif file
    """
    mocker.patch(
        'fyle.platform.apis.v1beta.admin.Expenses.list_all',
        return_value=fyle_fixtures['credit_card_expenses']
    )

    mocker.patch(
        'fyle.platform.apis.v1beta.admin.Files.create_file',
        return_value=fyle_fixtures['create_file']
    )

    mocker.patch(
        'fyle.platform.apis.v1beta.admin.Files.bulk_generate_file_urls',
        return_value=fyle_fixtures['generate_file_urls']
    )

    mocker.patch(
        'fyle.platform.apis.v1beta.admin.Files.upload_file_to_aws',
        return_value=None
    )

    mocker.patch(
        'sendgrid.SendGridAPIClient.send',
        return_value=None
    )

    workspace_id = 1

    accounting_export = AccountingExport.objects.get(workspace_id=workspace_id, type='FETCHING_CREDIT_CARD_EXPENSES')
    accounting_export.workspace.org_id = 'orNoatdUnm1w'
    accounting_export.workspace.save()

    import_credit_card_expenses(workspace_id, accounting_export)

    accounting_export = AccountingExport.objects.get(
        workspace_id=workspace_id, type='EXPORT_CREDIT_CARD_PURCHASES', status='ENQUEUED'
    )

    create_credit_card_purchases_iif_file(workspace_id, accounting_export)

    expenses = Expense.objects.filter(workspace_id=workspace_id, exported=False)

    assert accounting_export.status == 'COMPLETE'
    assert expenses.count() == 0
    assert accounting_export.credit_card_purchases.count() == 5
    assert accounting_export.credit_card_purchases.first().name == 'Credit Card Misc'
    assert accounting_export.file_id == 'fimNloQVF0D8'

    for credit_card_purchase in accounting_export.credit_card_purchases.all():
        assert credit_card_purchase.workspace_id == workspace_id
        assert credit_card_purchase.accounting_export_id == accounting_export.id
        assert credit_card_purchase.lineitems.count() == 1


@pytest.mark.django_db(databases=['default'])
def test_create_credit_card_purchases_iif_file_expense_employee(
    create_temp_workspace, add_accounting_export_bills,
    add_accounting_export_expenses, add_fyle_credentials,
    add_export_settings, add_field_mappings, add_advanced_settings,
    mocker
):
    """
    Test create credit card purchases iif file
    """
    mocker.patch(
        'fyle.platform.apis.v1beta.admin.Expenses.list_all',
        return_value=fyle_fixtures['credit_card_expenses']
    )

    mocker.patch(
        'fyle.platform.apis.v1beta.admin.Files.create_file',
        return_value=fyle_fixtures['create_file']
    )

    mocker.patch(
        'fyle.platform.apis.v1beta.admin.Files.bulk_generate_file_urls',
        return_value=fyle_fixtures['generate_file_urls']
    )

    mocker.patch(
        'fyle.platform.apis.v1beta.admin.Files.upload_file_to_aws',
        return_value=None
    )

    mocker.patch(
        'sendgrid.SendGridAPIClient.send',
        return_value=None
    )

    workspace_id = 2

    accounting_export = AccountingExport.objects.get(workspace_id=workspace_id, type='FETCHING_CREDIT_CARD_EXPENSES')
    accounting_export.workspace.org_id = 'orNoatdUnm1w'
    accounting_export.workspace.save()

    import_credit_card_expenses(workspace_id, accounting_export)

    accounting_export = AccountingExport.objects.get(
        workspace_id=workspace_id, type='EXPORT_CREDIT_CARD_PURCHASES', status='ENQUEUED'
    )

    expense = Expense.objects.filter(workspace_id=workspace_id, exported=False).first()

    expense.corporate_card_id = 'bacc1DHywC3YAd'
    expense.save()

    create_credit_card_purchases_iif_file(workspace_id, accounting_export)

    expenses = Expense.objects.filter(workspace_id=workspace_id, exported=False)

    assert accounting_export.status == 'COMPLETE'
    assert expenses.count() == 0
    assert accounting_export.credit_card_purchases.count() == 5
    assert accounting_export.credit_card_purchases.first().name == 'Ashwin'
    assert accounting_export.file_id == 'fimNloQVF0D8'

    for credit_card_purchase in accounting_export.credit_card_purchases.all():
        assert credit_card_purchase.workspace_id == workspace_id
        assert credit_card_purchase.accounting_export_id == accounting_export.id
        assert credit_card_purchase.lineitems.count() == 1



@pytest.mark.django_db(databases=['default'])
def test_create_credit_card_purchases_iif_file_expense_fail(
    create_temp_workspace, add_accounting_export_bills,
    add_accounting_export_expenses, add_fyle_credentials,
    add_export_settings, add_advanced_settings, mocker
):
    """
    Test create credit card purchases iif file
    """
    mocker.patch(
        'fyle.platform.apis.v1beta.admin.Expenses.list_all',
        return_value=fyle_fixtures['credit_card_expenses']
    )

    mocker.patch(
        'fyle.platform.apis.v1beta.admin.Files.create_file',
        return_value=fyle_fixtures['create_file']
    )

    mocker.patch(
        'fyle.platform.apis.v1beta.admin.Files.bulk_generate_file_urls',
        return_value=fyle_fixtures['generate_file_urls']
    )

    mocker.patch(
        'fyle.platform.apis.v1beta.admin.Files.upload_file_to_aws',
        return_value=None
    )

    workspace_id = 1

    accounting_export = AccountingExport.objects.get(workspace_id=workspace_id, type='FETCHING_CREDIT_CARD_EXPENSES')
    accounting_export.workspace.org_id = 'orNoatdUnm1w'
    accounting_export.workspace.save()

    import_credit_card_expenses(workspace_id, accounting_export)

    accounting_export = AccountingExport.objects.get(
        workspace_id=workspace_id, type='EXPORT_CREDIT_CARD_PURCHASES', status='ENQUEUED'
    )

    create_credit_card_purchases_iif_file(workspace_id, accounting_export)

    expenses = Expense.objects.filter(workspace_id=workspace_id, exported=False)

    assert expenses.count() == 5
    assert accounting_export.credit_card_purchases.count() == 0

    assert accounting_export.errors == {
        'message': 'FieldMapping matching query does not exist.'
    }
    assert accounting_export.status == 'FAILED'


@pytest.mark.django_db(databases=['default'])
def test_create_credit_card_purchases_iif_file_expense_fatal(
    create_temp_workspace, add_accounting_export_bills, 
    add_accounting_export_expenses, add_fyle_credentials,
    add_export_settings, add_field_mappings, add_advanced_settings,
    mocker
):
    """
    Test create credit card purchases iif file
    """
    mocker.patch(
        'fyle.platform.apis.v1beta.admin.Expenses.list_all',
        return_value=fyle_fixtures['credit_card_expenses']
    )

    mocker.patch(
        'fyle.platform.apis.v1beta.admin.Files.create_file',
        return_value=fyle_fixtures['create_file']
    )

    mocker.patch(
        'fyle.platform.apis.v1beta.admin.Files.upload_file_to_aws',
        return_value=None
    )

    workspace_id = 1

    accounting_export = AccountingExport.objects.get(workspace_id=workspace_id, type='FETCHING_CREDIT_CARD_EXPENSES')
    accounting_export.workspace.org_id = 'orNoatdUnm1w'
    accounting_export.workspace.save()

    import_credit_card_expenses(workspace_id, accounting_export)

    accounting_export = AccountingExport.objects.get(
        workspace_id=workspace_id, type='EXPORT_CREDIT_CARD_PURCHASES', status='ENQUEUED'
    )

    create_credit_card_purchases_iif_file(workspace_id, accounting_export)

    expenses = Expense.objects.filter(workspace_id=workspace_id, exported=False)

    assert accounting_export.credit_card_purchases.count() == 0
    assert expenses.count() == 5
    assert accounting_export.errors is not None
    assert accounting_export.status == 'FATAL'


@pytest.mark.django_db(databases=['default'])
def test_create_journals_iif_file_reimbursable_expense(
    create_temp_workspace, add_accounting_export_bills,
    add_accounting_export_expenses, add_fyle_credentials,
    add_export_settings, add_field_mappings, add_advanced_settings,
    mocker
):
    """
    Test create journals iif file
    """
    mocker.patch(
        'fyle.platform.apis.v1beta.admin.Expenses.list_all',
        return_value=fyle_fixtures['reimbursable_expenses']
    )

    mocker.patch(
        'fyle.platform.apis.v1beta.admin.Files.create_file',
        return_value=fyle_fixtures['create_file']
    )

    mocker.patch(
        'fyle.platform.apis.v1beta.admin.Files.bulk_generate_file_urls',
        return_value=fyle_fixtures['generate_file_urls']
    )

    mocker.patch(
        'fyle.platform.apis.v1beta.admin.Files.upload_file_to_aws',
        return_value=None
    )

    mocker.patch(
        'sendgrid.SendGridAPIClient.send',
        return_value=None
    )


    workspace_id = 3

    accounting_export = AccountingExport.objects.get(workspace_id=workspace_id, type='FETCHING_REIMBURSABLE_EXPENSES')
    accounting_export.workspace.org_id = 'orNoatdUnm1w'
    accounting_export.workspace.save()

    import_reimbursable_expenses(workspace_id, accounting_export)

    accounting_export = AccountingExport.objects.get(
        workspace_id=workspace_id, type='EXPORT_JOURNALS', status='ENQUEUED'
    )

    create_journals_iif_file(workspace_id, accounting_export, 'PERSONAL')

    expenses = Expense.objects.filter(
        workspace_id=workspace_id, exported=False, fund_source='PERSONAL'    
    )

    assert accounting_export.status == 'COMPLETE'
    assert expenses.count() == 0
    assert accounting_export.journals.count() == 5
    assert accounting_export.file_id == 'fimNloQVF0D8'

    for journal in accounting_export.journals.all():
        assert journal.workspace_id == workspace_id
        assert journal.accounting_export_id == accounting_export.id
        assert journal.lineitems.count() == 1


@pytest.mark.django_db(databases=['default'])
def test_create_journals_iif_file_ccc_report_vendor(
    create_temp_workspace, add_accounting_export_bills,
    add_accounting_export_expenses, add_fyle_credentials,
    add_export_settings, add_field_mappings, add_advanced_settings,
    mocker
):
    """
    Test create journals iif file
    """
    mocker.patch(
        'fyle.platform.apis.v1beta.admin.Expenses.list_all',
        return_value=fyle_fixtures['credit_card_expenses']
    )

    mocker.patch(
        'fyle.platform.apis.v1beta.admin.Files.create_file',
        return_value=fyle_fixtures['create_file']
    )

    mocker.patch(
        'fyle.platform.apis.v1beta.admin.Files.bulk_generate_file_urls',
        return_value=fyle_fixtures['generate_file_urls']
    )

    mocker.patch(
        'fyle.platform.apis.v1beta.admin.Files.upload_file_to_aws',
        return_value=None
    )

    mocker.patch(
        'sendgrid.SendGridAPIClient.send',
        return_value=None
    )

    workspace_id = 1

    accounting_export = AccountingExport.objects.get(workspace_id=workspace_id, type='FETCHING_CREDIT_CARD_EXPENSES')
    accounting_export.workspace.org_id = 'orNoatdUnm1w'
    accounting_export.workspace.save()

    import_credit_card_expenses(workspace_id, accounting_export)

    accounting_export = AccountingExport.objects.get(
        workspace_id=workspace_id, type='EXPORT_JOURNALS', status='ENQUEUED'
    )

    # Testing for entity preference as Vendor
    create_journals_iif_file(workspace_id, accounting_export, 'CCC')

    expenses = Expense.objects.filter(
        workspace_id=workspace_id, exported=False, fund_source='CCC'    
    )

    assert accounting_export.status == 'COMPLETE'
    assert expenses.count() == 0
    assert accounting_export.journals.count() == 4
    assert accounting_export.journals.first().name == 'Credit Card Misc'
    assert accounting_export.file_id == 'fimNloQVF0D8'

    for journal in accounting_export.journals.all():
        assert journal.workspace_id == workspace_id
        assert journal.accounting_export_id == accounting_export.id
        assert journal.lineitems.count() >= 1


@pytest.mark.django_db(databases=['default'])
def test_create_journals_iif_file_ccc_report_employee(
    create_temp_workspace, add_accounting_export_bills,
    add_accounting_export_expenses, add_fyle_credentials,
    add_export_settings, add_field_mappings, add_advanced_settings,
    mocker
):
    """
    Test create journals iif file
    """
    mocker.patch(
        'fyle.platform.apis.v1beta.admin.Expenses.list_all',
        return_value=fyle_fixtures['credit_card_expenses']
    )

    mocker.patch(
        'fyle.platform.apis.v1beta.admin.Files.create_file',
        return_value=fyle_fixtures['create_file']
    )

    mocker.patch(
        'fyle.platform.apis.v1beta.admin.Files.bulk_generate_file_urls',
        return_value=fyle_fixtures['generate_file_urls']
    )

    mocker.patch(
        'fyle.platform.apis.v1beta.admin.Files.upload_file_to_aws',
        return_value=None
    )

    mocker.patch(
        'sendgrid.SendGridAPIClient.send',
        return_value=None
    )

    workspace_id = 2

    accounting_export = AccountingExport.objects.get(workspace_id=workspace_id, type='FETCHING_CREDIT_CARD_EXPENSES')
    accounting_export.workspace.org_id = 'orNoatdUnm1w'
    accounting_export.workspace.save()

    import_credit_card_expenses(workspace_id, accounting_export)

    accounting_export = AccountingExport.objects.get(
        workspace_id=workspace_id, type='EXPORT_JOURNALS', status='ENQUEUED'
    )

    expense = Expense.objects.filter(workspace_id=workspace_id, exported=False).first()

    expense.corporate_card_id = 'bacc1DHywC3YAd'
    expense.save()

    # Testing for entity preference as Vendor
    create_journals_iif_file(workspace_id, accounting_export, 'CCC')

    expenses = Expense.objects.filter(
        workspace_id=workspace_id, exported=False, fund_source='CCC'    
    )

    assert accounting_export.status == 'COMPLETE'
    assert expenses.count() == 0
    assert accounting_export.journals.count() == 4
    assert accounting_export.journals.first().name == 'Ashwin'
    assert accounting_export.file_id == 'fimNloQVF0D8'

    for journal in accounting_export.journals.all():
        assert journal.workspace_id == workspace_id
        assert journal.accounting_export_id == accounting_export.id
        assert journal.lineitems.count() >= 1


@pytest.mark.django_db(databases=['default'])
def test_create_journals_iif_file_ccc_report_fail(
    create_temp_workspace, add_accounting_export_bills, 
    add_accounting_export_expenses, add_fyle_credentials, 
    add_export_settings, add_advanced_settings, mocker
):
    """
    Test create journals iif file Fail
    """
    mocker.patch(
        'fyle.platform.apis.v1beta.admin.Expenses.list_all',
        return_value=fyle_fixtures['credit_card_expenses']
    )

    mocker.patch(
        'fyle.platform.apis.v1beta.admin.Files.create_file',
        return_value=fyle_fixtures['create_file']
    )

    mocker.patch(
        'fyle.platform.apis.v1beta.admin.Files.bulk_generate_file_urls',
        return_value=fyle_fixtures['generate_file_urls']
    )

    mocker.patch(
        'fyle.platform.apis.v1beta.admin.Files.upload_file_to_aws',
        return_value=None
    )

    workspace_id = 1

    accounting_export = AccountingExport.objects.get(workspace_id=workspace_id, type='FETCHING_CREDIT_CARD_EXPENSES')
    accounting_export.workspace.org_id = 'orNoatdUnm1w'
    accounting_export.workspace.save()

    import_credit_card_expenses(workspace_id, accounting_export)

    accounting_export = AccountingExport.objects.get(
        workspace_id=workspace_id, type='EXPORT_JOURNALS', status='ENQUEUED'
    )

    create_journals_iif_file(workspace_id, accounting_export, 'CCC')

    expenses = Expense.objects.filter(
        workspace_id=workspace_id, exported=False, fund_source='CCC'    
    )

    assert accounting_export.status == 'FAILED'
    assert expenses.count() == 5
    assert accounting_export.errors == {
        'message': 'FieldMapping matching query does not exist.'
    }
    assert accounting_export.journals.count() == 0
    assert accounting_export.file_id is None
    assert accounting_export.errors is not None


@pytest.mark.django_db(databases=['default'])
def test_create_journals_iif_file_ccc_report_fatal(
    create_temp_workspace, add_accounting_export_bills,
    add_accounting_export_expenses, add_fyle_credentials,
    add_export_settings, add_field_mappings, add_advanced_settings,
    mocker
):
    """
    Test create journals iif file Fatal
    """
    mocker.patch(
        'fyle.platform.apis.v1beta.admin.Expenses.list_all',
        return_value=fyle_fixtures['credit_card_expenses']
    )

    mocker.patch(
        'fyle.platform.apis.v1beta.admin.Files.create_file',
        return_value=fyle_fixtures['create_file']
    )

    mocker.patch(
        'fyle.platform.apis.v1beta.admin.Files.upload_file_to_aws',
        return_value=None
    )

    workspace_id = 1

    accounting_export = AccountingExport.objects.get(workspace_id=workspace_id, type='FETCHING_CREDIT_CARD_EXPENSES')
    accounting_export.workspace.org_id = 'orNoatdUnm1w'
    accounting_export.workspace.save()

    import_credit_card_expenses(workspace_id, accounting_export)

    accounting_export = AccountingExport.objects.get(
        workspace_id=workspace_id, type='EXPORT_JOURNALS', status='ENQUEUED'
    )

    create_journals_iif_file(workspace_id, accounting_export, 'CCC')

    expenses = Expense.objects.filter(
        workspace_id=workspace_id, exported=False, fund_source='CCC'    
    )

    assert accounting_export.status == 'FATAL'
    assert expenses.count() == 5
    assert accounting_export.journals.count() == 0
    assert accounting_export.file_id is None
    assert accounting_export.errors is not None


def assert_email_failure_error(accounting_export: AccountingExport):
    assert accounting_export.status == 'FAILED'
    assert accounting_export.journals.count() == 0
    assert accounting_export.errors == {
        'status_code': 500,
        'body': 'Internal Server Error',
        'reason': 'Internal Server Error',
        'headers': 'None'
    }


@pytest.mark.django_db(databases=['default'])
def test_email_failure(
    create_temp_workspace, add_accounting_export_bills,
    add_accounting_export_expenses, add_fyle_credentials,
    add_export_settings, add_field_mappings, add_advanced_settings,
    mocker
):
    """
    Test create journals iif file Failed for email failure
    """
    mocker.patch(
        'fyle.platform.apis.v1beta.admin.Expenses.list_all',
        return_value=fyle_fixtures['credit_card_expenses']
    )

    mocker.patch(
        'fyle.platform.apis.v1beta.admin.Files.create_file',
        return_value=fyle_fixtures['create_file']
    )

    mocker.patch(
        'fyle.platform.apis.v1beta.admin.Files.bulk_generate_file_urls',
        return_value=fyle_fixtures['generate_file_urls']
    )

    mocker.patch(
        'fyle.platform.apis.v1beta.admin.Files.upload_file_to_aws',
        return_value=None
    )

    mocker.patch(
        'sendgrid.SendGridAPIClient.send',
        side_effect=HTTPError(500, 'Internal Server Error', 'Internal Server Error', 'None')
    )

    workspace_id = 1

    accounting_export = AccountingExport.objects.get(workspace_id=workspace_id, type='FETCHING_CREDIT_CARD_EXPENSES')
    accounting_export.workspace.org_id = 'orNoatdUnm1w'
    accounting_export.workspace.save()

    import_credit_card_expenses(workspace_id, accounting_export)

    accounting_export = AccountingExport.objects.get(
        workspace_id=workspace_id, type='EXPORT_JOURNALS', status='ENQUEUED'
    )

    create_journals_iif_file(workspace_id, accounting_export, 'CCC')
    assert_email_failure_error(accounting_export)

    create_credit_card_purchases_iif_file(workspace_id, accounting_export)
    assert_email_failure_error(accounting_export)


    mocker.patch(
        'fyle.platform.apis.v1beta.admin.Expenses.list_all',
        return_value=fyle_fixtures['reimbursable_expenses']
    )
    import_reimbursable_expenses(workspace_id, accounting_export)
    create_bills_iif_file(workspace_id, accounting_export)
    assert_email_failure_error(accounting_export)
