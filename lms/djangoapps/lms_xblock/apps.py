"""
lms_xblock Application Configuration
"""
from __future__ import absolute_import

from django.apps import AppConfig

import xmodule.x_module
from .runtime import handler_url, local_resource_url


class LMSXBlockConfig(AppConfig):
    """
    Default configuration for the "lms.djangoapps.lms_xblock" Django application.
    """
    name = u'lms.djangoapps.lms_xblock'
    verbose_name = u'LMS XBlock'

    def ready(self):
        # In order to allow modules to use a handler url, we need to
        # monkey-patch the x_module library.
        # TODO: Remove this code when Runtimes are no longer created by modulestores
        # https://openedx.atlassian.net/wiki/display/PLAT/Convert+from+Storage-centric+runtimes+to+Application-centric+runtimes
        xmodule.x_module.descriptor_global_handler_url = handler_url
        xmodule.x_module.descriptor_global_local_resource_url = local_resource_url
