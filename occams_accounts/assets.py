import os

from webassets import Bundle

from . import log


def includeme(config):
    """
    Loads web assets
    """
    here = os.path.dirname(os.path.realpath(__file__))

    # "resolves" the path relative to this package
    def rel(path):
        return os.path.join(here, 'static', path)

    scriptsdir = os.path.join(here, 'static/scripts')

    config.add_webasset('accounts-js', Bundle(
        # Dependency javascript libraries must be loaded in a specific order
        rel('bower_components/jquery/dist/jquery.min.js'),
        rel('bower_components/bootstrap/dist/js/bootstrap.min.js'),
        # App-specific scripts can be loaded in any order
        Bundle(
            *[os.path.join(root, filename)
                for root, dirnames, filenames in os.walk(scriptsdir)
                for filename in filenames if filename.endswith('.js')],
            filters='jsmin'),
        output=rel('gen/accounts.%(version)s.min.js')))

    config.add_webasset('accounts-css', Bundle(
        Bundle(
            rel('styles/main.less'),
            filters='less,cssmin',
            depends=rel('styles/*.less'),
            output=rel('gen/accounts-main.%(version)s.min.css')),
        output=rel('gen/accounts.%(version)s.css')))

    log.debug('Assets configurated')
