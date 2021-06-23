import pkgutil
import pkg_resources
import os
import logging
from time import time
from werkzeug.local import LocalProxy
from flask import g, current_app

from flask_themes2 import (
    Themes, Theme, render_theme_template, get_theme
)
from jinja2 import contextfunction
from udata import assets


log = logging.getLogger(__name__)


RE_STRIP_TAGS = re.compile(r'</?(img|br|p|div|ul|li|ol)[^<>]*?>', re.I | re.M)

# Add some html5 allowed attributes
EXTRA_ATTRIBUTES = ('srcset', 'sizes')
feedparser._HTMLSanitizer.acceptable_attributes.update(set(EXTRA_ATTRIBUTES))

# Wordpress ATOM timeout
WP_TIMEOUT = 5

# Feed allowed enclosure type as thumbnails
FEED_THUMBNAIL_MIMES = ('image/jpeg', 'image/png', 'image/webp')


gouvfr_menu = nav.Bar('gouvfr_menu', [
    nav.Item(_('Data'), 'datasets.list'),
    nav.Item(_('Reuses'), 'reuses.list'),
    nav.Item(_('Organizations'), 'organizations.list'),
    nav.Item(_('Dashboard'), 'site.dashboard'),
    nav.Item(_('Documentation'), None, url='https://doc.data.gouv.fr', items=[
        nav.Item(_("Platform's documentation"), None, url='https://doc.data.gouv.fr'),
        nav.Item(_('Open data guides'), None, url='https://guides.etalab.gouv.fr'),
    ]),
    nav.Item(_('News'), 'posts.list'),
    nav.Item(_('Support'), None, url='https://support.data.gouv.fr/'),
])

theme.menu(gouvfr_menu)

footer_links = [
    nav.Item(_('News'), 'posts.list'),
    nav.Item(_('Reference Data'), 'gouvfr.spd'),
    nav.Item(_('Licences'), 'gouvfr.licences'),
    nav.Item(_('API'), None, url=current_app.config.get('API_DOC_EXTERNAL_LINK', '#')),
    nav.Item(_('Terms of use'), 'site.terms'),
    nav.Item(_('Tracking and privacy'), 'gouvfr.suivi'),
]

export_dataset_id = current_app.config.get('EXPORT_CSV_DATASET_ID')
if export_dataset_id:
    try:
        export_dataset = Dataset.objects.get(id=export_dataset_id)
    except Dataset.DoesNotExist:
        pass
    else:
        export_url = url_for('datasets.show', dataset=export_dataset,
                             _external=True)
        footer_links.append(nav.Item(_('Data catalog'), None, url=export_url))

footer_links.append(nav.Item('Thématiques à la une', 'gouvfr.show_page',
                             args={'slug': 'donnees-cles-par-sujet'}))

nav.Bar('gouvfr_footer', footer_links)

NETWORK_LINKS = [
    ('Gouvernement.fr', 'http://www.gouvernement.fr'),
    ('France.fr', 'http://www.france.fr'),
    ('Legifrance.gouv.fr', 'http://www.legifrance.gouv.fr'),
    ('Service-public.fr', 'http://www.service-public.fr'),
    ('Opendata France', 'http://opendatafrance.net'),
    ('CADA.fr', 'http://www.cada.fr'),
    ('Etalab.gouv.fr', 'https://www.etalab.gouv.fr'),
]

nav.Bar(
    'gouvfr_network',
    [nav.Item(label, label, url=url) for label, url in NETWORK_LINKS]
)

footer_support_links = [
    nav.Item(_("Platform's documentation"), None, url='https://doc.data.gouv.fr'),
    nav.Item(_('Open data guides'), None, url='https://guides.etalab.gouv.fr'),
    nav.Item(_('Support'), None, url='https://support.data.gouv.fr/')
]

nav.Bar('support_network', footer_support_links)



current = LocalProxy(get_current_theme)


@contextfunction
def theme_static_with_version(ctx, filename, external=False):
    '''Override the default theme static to add cache burst'''
    if current_app.theme_manager.static_folder:
        url = assets.cdn_for('_themes.static',
                             filename=current.identifier + '/' + filename,
                             _external=external)
    else:
        url = assets.cdn_for('_themes.static',
                             themeid=current.identifier,
                             filename=filename,
                             _external=external)
    if url.endswith('/'):  # this is a directory, no need for cache burst
        return url
    if current_app.config['DEBUG']:
        burst = time()
    else:
        burst = current.entrypoint.dist.version
    return '{url}?_={burst}'.format(url=url, burst=burst)


class ConfigurableTheme(Theme):
    context_processors = None
    defaults = None
    admin_form = None
    manifest = None
    _menu = None
    _configured = False

    def __init__(self, entrypoint):
        self.entrypoint = entrypoint
        # Compute path without loading the module
        path = pkgutil.get_loader(entrypoint.module_name).path
        path = os.path.dirname(path)
        super(ConfigurableTheme, self).__init__(path)

        self.variants = self.info.get('variants', [])
        if 'gouvfr' not in self.variants:
            self.variants.insert(0, 'gouvfr')
        self.context_processors = {}

        # Check JSON manifest
        manifest = os.path.join(path, 'manifest.json')
        if os.path.exists(manifest):
            self.manifest = manifest

    @property
    def site(self):
        from udata.core.site.models import current_site
        return current_site

    @property
    def config(self):
        return self.site.themes.get(self.identifier)

    @property
    def menu(self):
        return self._menu

    @menu.setter
    def menu(self, value):
        self._menu = value

    @property
    def variant(self):
        '''Get the current theme variant'''
        variant = current_app.config['THEME_VARIANT']
        if variant not in self.variants:
            log.warning('Unkown theme variant: %s', variant)
            return 'gouvfr'
        else:
            return variant

    def configure(self):
        if self._configured:
            return
        self.entrypoint.load()
        if self.defaults and self.identifier not in self.site.themes:
            self.site.themes[self.identifier] = self.defaults
            try:
                self.site.save()
            except Exception:
                log.exception('Unable to save theme configuration')
        self._configured = True

    def get_processor(self, context_name, default=lambda c: c):
        return self.context_processors.get(context_name, default)


def themes_loader(app):
    '''Load themes from entrypoints'''
    for entrypoint in pkg_resources.iter_entry_points('udata.themes'):
        yield ConfigurableTheme(entrypoint)


def render(template, **context):
    '''
    Render a template with uData frontend specifics

        * Theme
    '''
    theme = current_app.config['THEME']
    return render_theme_template(get_theme(theme), template, **context)


def defaults(values):
    g.theme.defaults = values


def menu(navbar):
    g.theme.menu = navbar


def context(name):
    '''A decorator for theme context processors'''
    def wrapper(func):
        g.theme.context_processors[name] = func
        return func
    return wrapper


def init_app(app):
    app.config.setdefault('THEME_VARIANT', 'gouvfr')

    themes.init_themes(app, app_identifier='udata', loaders=[themes_loader])
    # Load all theme assets
    theme = app.theme_manager.themes[app.config['THEME']]
    prefix = '/'.join(('_themes', theme.identifier))
    app.config['STATIC_DIRS'].append((prefix, theme.static_path))

    # Override the default theme_static
    app.jinja_env.globals['theme_static'] = theme_static_with_version

    # Load manifest if necessary
    if theme.manifest:
        with app.app_context():
            assets.register_manifest('theme', theme.manifest)

    # Hook into flask security to user themed auth pages
    app.config.setdefault('SECURITY_RENDER', 'udata_gouvfr.theme:render')

    @app.context_processor
    def inject_current_theme():
        return {'current_theme': current}
