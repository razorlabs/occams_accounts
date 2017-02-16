from pyramid.httpexceptions import HTTPFound
from pyramid.security import forget
from pyramid.view import view_config
import wtforms
import wtforms.fields.html5

from occams_datastore import models as datastore

from .. import _


class LoginForm(wtforms.Form):

    # Doesn't actually validate email input, just generates the
    #  <input type="email" field. So we still need to do a bit of
    # input validation in case input is from other sources such as a
    # curl script
    login = wtforms.fields.html5.EmailField(
        _(u'Login'),
        validators=[
            wtforms.validators.InputRequired(),
            # Emails can only be 254 characters long:
            #   http://stackoverflow.com/a/1199238
            wtforms.validators.Length(min=10, max=254),
            # Validate 99.99% of acceptable email formats
            wtforms.validators.Regexp(
                r'(^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$)',
                message='Invalid email format'
            ),
        ])

    password = wtforms.PasswordField(
        _(u'Password'),
        validators=[
            wtforms.validators.InputRequired(),
            # Enforce a limit on password lengh input to prevent
            # submissions of excessively long paragraphs
            # https://www.owasp.org/index.php/Authentication_Cheat_Sheet
            wtforms.validators.Length(max=128)
        ])


@view_config(route_name='accounts.login', renderer='../templates/login.pt')
def login(request):

    db_session = request.db_session
    form = LoginForm(request.POST)

    if request.method == 'POST' and form.validate():
        # XXX: Hack for this to work on systems that have not set the
        # environ yet. Pyramid doesn't give us access to the policy
        # publicly, put it's still available throught this private
        # variable and it's usefule in leveraging repoze.who's
        # login mechanisms...
        who_api = request._get_authentication_policy()._getAPI(request)

        authenticated, headers = who_api.login(form.data)

        if not authenticated:
            request.session.flash(_(u'Invalid credentials'), 'danger')
        else:
            user = (
                db_session.query(datastore.User)
                .filter_by(key=form.login.data)
                .first())
            if not user:
                user = datastore.User(key=form.login.data)
                db_session.add(user)

            referrer = request.GET.get('referrer')
            if not referrer or request.route_path('accounts.login') in referrer:
                # TODO: Maybe send the user to their user dashboard instead?
                referrer = request.route_path('occams.index')

            return HTTPFound(location=referrer, headers=headers)

    # forcefully forget any credentials
    request.response.headerlist.extend(forget(request))

    return {'form': form}
