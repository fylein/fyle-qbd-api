import logging

from fyle.platform.exceptions import NoPrivilegeError, RetryException, InvalidTokenError as FyleInvalidTokenError
from rest_framework.response import Response
from rest_framework.views import status
from rest_framework.exceptions import ValidationError

from apps.workspaces.models import FyleCredential, Workspace, ExportSettings, AdvancedSetting
from apps.tasks.models import AccountingExport

logger = logging.getLogger(__name__)
logger.level = logging.INFO


def handle_view_exceptions():
    def decorator(func):
        def new_fn(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except AccountingExport.DoesNotExist:
                return Response(data={'message': 'AccountingExport not found'}, status=status.HTTP_400_BAD_REQUEST)

            except FyleCredential.DoesNotExist:
                return Response(data={'message': 'Fyle credentials not found in workspace'}, status=status.HTTP_400_BAD_REQUEST)

            except FyleInvalidTokenError as exception:
                logger.info('Fyle token expired workspace_id - %s %s', kwargs['workspace_id'], {'error': exception.response})
                return Response(data={'message': 'Fyle token expired workspace_id'}, status=status.HTTP_400_BAD_REQUEST)

            except NoPrivilegeError as exception:
                logger.info('Invalid Fyle Credentials / Admin is disabled  for workspace_id%s %s', kwargs['workspace_id'], {'error': exception.response})
                return Response(data={'message': 'Invalid Fyle Credentials / Admin is disabled'}, status=status.HTTP_400_BAD_REQUEST)

            except RetryException:
                logger.info('Fyle Retry Exception for workspace_id %s', kwargs['workspace_id'])
                return Response(data={'message': 'Fyle API rate limit exceeded'}, status=status.HTTP_400_BAD_REQUEST)

            except Workspace.DoesNotExist:
                return Response(data={'message': 'Workspace with this id does not exist'}, status=status.HTTP_400_BAD_REQUEST)

            except AdvancedSetting.DoesNotExist:
                return Response(data={'message': 'Advanced Settings does not exist in workspace'}, status=status.HTTP_400_BAD_REQUEST)

            except ExportSettings.DoesNotExist:
                return Response({'message': 'Export Settings does not exist in workspace'}, status=status.HTTP_400_BAD_REQUEST)

            except ValidationError as e:
                logger.exception(e)
                return Response({"message": e.detail}, status=status.HTTP_400_BAD_REQUEST)

            except Exception as exception:
                logger.exception(exception)
                return Response(data={'message': 'An unhandled error has occurred, please re-try later'}, status=status.HTTP_400_BAD_REQUEST)

        return new_fn

    return decorator
