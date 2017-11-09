from urlparse import urlparse

import attr
from django.conf import settings
from django.core.urlresolvers import reverse
from django.utils.http import urlquote, urlencode

from edxmako.shortcuts import marketing_link
from openedx.core.djangoapps.site_configuration.models import SiteConfiguration
from openedx.core.djangoapps.theming.helpers import get_current_site


def get_base_template_context(site):
    """Dict with entries needed for all templates that use the base template"""
    return {
        # Platform information
        'homepage_url': encode_url(marketing_link('ROOT')),
        'dashboard_url': absolute_url(site, reverse('dashboard')),
        'template_revision': settings.EDX_PLATFORM_REVISION,
        'platform_name': settings.PLATFORM_NAME,
        'contact_mailing_address': settings.CONTACT_MAILING_ADDRESS,
        'social_media_urls': encode_urls_in_dict(getattr(settings, 'SOCIAL_MEDIA_FOOTER_URLS', {})),
        'mobile_store_urls': encode_urls_in_dict(getattr(settings, 'MOBILE_STORE_URLS', {})),
    }


def encode_url(url):
    # Sailthru has a bug where URLs that contain "+" characters in their path components are misinterpreted
    # when GA instrumentation is enabled. We need to percent-encode the path segments of all URLs that are
    # injected into our templates to work around this issue.
    parsed_url = urlparse(url)
    modified_url = parsed_url._replace(path=urlquote(parsed_url.path))
    return modified_url.geturl()


def absolute_url(site, relative_path):
    """
    Add site.domain to the beginning of the given relative path.

    If the given URL is already absolute (has a netloc part), then it is just returned.
    """
    if bool(urlparse(relative_path).netloc):
        # Given URL is already absolute
        return relative_path
    root = site.domain.rstrip('/')
    relative_path = relative_path.lstrip('/')
    return encode_url(u'https://{root}/{path}'.format(root=root, path=relative_path))


def encode_urls_in_dict(mapping):
    urls = {}
    for key, value in mapping.iteritems():
        urls[key] = encode_url(value)
    return urls


@attr.s
class GoogleAnalyticsTrackingPixel(object):
    ANONYMOUS_USER_CLIENT_ID = 555

    site = attr.ib(default=None)

    version = attr.ib(default=1, metadata={'param_name': 'v'})
    hit_type = attr.ib(default='event', metadata={'param_name': 't'})

    campaign_source = attr.ib(default='ace', metadata={'param_name': 'cs'})
    campaign_medium = attr.ib(default='email', metadata={'param_name': 'cm'})
    campaign_name = attr.ib(default=None, metadata={'param_name': 'cn'})

    event_category = attr.ib(default='email', metadata={'param_name': 'ec'})
    event_action = attr.ib(default='edx.bi.email.opened', metadata={'param_name': 'ea'})
    event_label = attr.ib(default=None, metadata={'param_name': 'el'})

    document_path = attr.ib(default=None, metadata={'param_name': 'dp'})

    user_id = attr.ib(default=None, metadata={'param_name': 'uid'})
    client_id = attr.ib(default=None, metadata={'param_name': 'cid'})

    @property
    def image_url(self):
        parameters = {}
        for attribute in attr.fields(self.__class__):
            value = getattr(self, attribute.name, None)
            if value is not None and 'param_name' in attribute.metadata:
                parameter_name = attribute.metadata['param_name']
                parameters[parameter_name] = str(value)

        parameters['tid'] = self._get_value_from_settings("GOOGLE_ANALYTICS_TRACKING_ID")

        user_id_dimension = self._get_value_from_settings("GOOGLE_ANALYTICS_USER_ID_CUSTOM_DIMENSION")
        if user_id_dimension is not None and self.user_id is not None:
            parameter_name = 'cd{0}'.format(user_id_dimension)
            parameters[parameter_name] = self.user_id

        if self.user_id is None and self.client_id is None:
            parameters['cid'] = self.ANONYMOUS_USER_CLIENT_ID

        return u"https://www.google-analytics.com/collect?{params}".format(params=urlencode(parameters))

    def _get_value_from_settings(self, name):
        site = self.site
        if self.site is None:
            site = get_current_site()

        site_configuration = None
        try:
            site_configuration = getattr(site, "configuration", None)
        except SiteConfiguration.DoesNotExist:
            pass

        value_from_settings = getattr(settings, name, None)
        if site_configuration is not None:
            return site_configuration.get_value(name, default=value_from_settings)
        else:
            return value_from_settings
