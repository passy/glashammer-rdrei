
# -*- coding: utf-8 -*-
"""
    textpress.views.admin
    ~~~~~~~~~~~~~~~~~~~~~

    This module implements the admin views. The admin interface is only
    available for admins, editors and authors but not for subscribers. For
    subscribers a simplified account management system exists at /account.

    The admin panel tries it's best to avoid CSRF attacks and some similar
    problems by using the hidden form fields from the utils package.  For
    more details see the docstrings of the `CSRFProtector` and
    `IntelligentRedirect` classes located there.  Do this before you try to
    add your own admin panel pages!

    Todo:

    -   Dashboard

    :copyright: 2007-2008 by Armin Ronacher, Christopher Grebs, Pedro Algarvio.
    :license: GNU GPL.
"""
from datetime import datetime
#from textpress.api import *
from glashammer.bundles.auth.database import User, ROLE_ADMIN, \
     ROLE_EDITOR, ROLE_AUTHOR, ROLE_SUBSCRIBER

from glashammer.utils import require_role, IntelligentRedirect, \
    render_response, sibpath, _, redirect, url_for, get_request, emit_event, \
    Pagination, CSRFProtector, make_hidden_fields, flash, build_eventmap

from glashammer.database import db
#from textpress.database import comments, posts, post_tags, post_links
#from textpress.utils import parse_datetime, format_datetime, \
#     is_valid_email, is_valid_url, get_version_info, can_build_eventmap, \
#     build_eventmap, make_hidden_fields, dump_json, load_json, flash, \
#     CSRFProtector, IntelligentRedirect, TIMEZONES
#from textpress.importers import list_import_queue, load_import_dump, \
#     delete_import_dump, perform_import
#from textpress.pluginsystem import install_package, InstallationError, \
#     SetupError
#from textpress.pingback import pingback, PingbackError
from urlparse import urlparse
from werkzeug import escape
from werkzeug.exceptions import NotFound

#: how many posts / comments should be displayed per page?

can_build_eventmap = True
PER_PAGE = 20


def simple_redirect(*args, **kwargs):
    """A function "simple redirect" that works like the redirect function
    in the views, just that it doesn't use the `IntelligentRedirect` which
    sometimes doesn't do what we want. (like redirecting to target pages
    and not using backredirects)
    """
    return redirect(url_for(*args, **kwargs))


def render_admin_response(template_name, _active_menu_item=None, **values):
    """Works pretty much like the normal `render_response` function but
    it emits some events to collect navigation items and injects that
    into the template context. This also gets the flashes messages from
    the user session and injects them into the template context after the
    plugins have provided theirs in the `before-admin-response-rendered`
    event.

    The second parameter can be the active menu item if wanted. For example
    ``'options.overview'`` would show the overview button in the options
    submenu. If the menu is a standalone menu like the dashboard (no
    child items) you can also just use ``'dashboard'`` to highlight that.
    """
    request = get_request()

    # set up the core navigation bar
    navigation_bar = [
        ('dashboard', url_for('admin/index'), _('Dashboard'), []),
        #('posts', url_for('admin/show_posts'), _('Posts'), [
        #    ('overview', url_for('admin/show_posts'), _('Overview')),
        #    ('write', url_for('admin/new_post'), _('Write Post'))
        #]),
        #('comments', url_for('admin/show_comments'), _('Comments'), [
        #    ('overview', url_for('admin/show_comments'), _('Overview')),
        #    ('unmoderated', url_for('admin/show_unmoderated_comments'),
        #     _('Awaiting Moderation (%d)') %
        #     Comment.objects.unmoderated().count()),
        #    ('spam', url_for('admin/show_spam_comments'),
        #     _('Spam (%d)') % Comment.objects.spam().count())
        #]),
        #('tags', url_for('admin/show_tags'), _('Tags'), [
        #    ('overview', url_for('admin/show_tags'), _('Overview')),
        #    ('edit', url_for('admin/new_tag'), _('Edit Tag'))
        #])
    ]

    # set up the administration menu bar
    if request.user.role == ROLE_ADMIN:
        navigation_bar += [
            ('users', url_for('admin/show_users'), _('Users'), [
                ('overview', url_for('admin/show_users'), _('Overview')),
                ('edit', url_for('admin/new_user'), _('Edit User'))
            ]),
            ('configuration', url_for('admin/configuration'),
            _    ('Configuration'), []),
            ]
            #,
            #('options', url_for('admin/options'), _('Options'), [
            #    ('basic', url_for('admin/basic_options'), _('Basic')),
            #    ('urls', url_for('admin/urls'), _('URLs')),
            #    ('theme', url_for('admin/theme'), _('Theme')),
            #    ('plugins', url_for('admin/plugins'), _('Plugins')),
            #   ('cache', url_for('admin/cache'), _('Cache')),
            #    ('configuration', url_for('admin/configuration'),
           #      _('Configuration Editor'))
            #]),
            #('maintenance', url_for('admin/maintenance'), _('Maintenance'), [
            #    ('overview', url_for('admin/maintenance'), _('Overview')),
            #    ('import', url_for('admin/import'), _('Import')),
            #    ('export', url_for('admin/export'), _('Export'))
            #])
        #]

    # add the about items to the navigation bar
    about_items = [
        ('system', url_for('admin/about'), _('System')),
    #    ('textpress', url_for('admin/about_textpress'), _('TextPress'))
    ]
    if can_build_eventmap:
        about_items.insert(1, ('eventmap', url_for('admin/eventmap'),
                               _('Event Map')))
    navigation_bar.append(('about', url_for('admin/about'), _('About'),
                          about_items))

    #! allow plugins to extend the navigation bar
    emit_event('modify-admin-navigation-bar', request, navigation_bar)

    # find out which is the correct menu and submenu bar
    active_menu = active_submenu = None
    if _active_menu_item is not None:
        p = _active_menu_item.split('.')
        if len(p) == 1:
            active_menu = p[0]
        else:
            active_menu, active_submenu = p
    for id, url, title, subnavigation_bar in navigation_bar:
        if id == active_menu:
            break
    else:
        subnavigation_bar = []

    # if we are in maintenance_mode the user should know that, no matter
    # on which page he is.
    #if request.app.conf['maintenance_mode']:
    #    flash(_('TextPress is in maintenance mode. Don\'t forget to '
    #            'turn it off again once you finish your changes.'))

    # check for broken plugins if we have the plugin guard enabled
    #if request.app.cfg['plugin_guard']:
    #    for plugin in request.app.plugins.itervalues():
    #        if plugin.active and plugin.setup_error is not None:
    #            plugin.deactivate()
    #            exc_type, exc_value, tb = plugin.setup_error
    #            if exc_type is SetupError:
    #                msg = _(u'Could not activate plugin “%s”: %s') % (
    #                    plugin.html_display_name,
    #                    exc_value.message
    #                )
    #            else:
    #                msg =_(u'The plugin guard detected that the plugin “%s” '
    #                       u'causes problems (%s in %s, line %s) and '
    #                       u'deactivated it.  If you want to debug it, '
    #                       u'disable the plugin guard.') % (
    #                    plugin.html_display_name,
    #                    escape(str(plugin.setup_error[1]).
    #                           decode('utf-8', 'ignore')),
    #                    plugin.setup_error[2].tb_frame.
    #                        f_globals.get('__file__', _('unknown file')),
    #                    plugin.setup_error[2].tb_lineno
    #                )
    #            flash(msg, 'error')
#
    #! used to flash messages, add links to stylesheets, modify the admin
    #! context etc.
    emit_event('before-admin-response-rendered', request, values)

    # the admin variables is pushed into the context after the event was
    # sent so that plugins can flash their messages. If we would emit the
    # event afterwards all flashes messages would appear in the request
    # after the current request.
    values['admin'] = {
        'navbar': [{
            'id':       id,
            'url':      url,
            'title':    title,
            'active':   active_menu == id
        } for id, url, title, children in navigation_bar],
        'ctxnavbar': [{
            'id':       id,
            'url':      url,
            'title':    title,
            'active':   active_submenu == id
        } for id, url, title in subnavigation_bar],
        'messages': [{
            'type':     type,
            'msg':      msg
        } for type, msg in request.session.pop('admin/flashed_messages', [])]
    }
    return render_response(template_name, **values)


@require_role(ROLE_AUTHOR)
def do_index(request):
    """Show the admin interface index page which is a wordpress inspired
    dashboard (doesn't exist right now).

    Once it's finished it should show the links to the most useful pages
    such as "new post", etc. and the recent blog activity (unmoderated
    comments etc.)
    """
    return render_admin_response('admin/index.html', 'dashboard',
    )


@require_role(ROLE_ADMIN)
def do_show_users(request, page):
    """Show all users in a list."""
    users = User.objects.query.limit(PER_PAGE).offset(PER_PAGE * (page - 1)).all()
    pagination = Pagination('admin/show_users', page, PER_PAGE,
                            User.objects.count())
    if not users and page != 1:
        raise NotFound()
    return render_admin_response('admin/show_users.html', 'users.overview',
                                 users=users,
                                 pagination=pagination)


@require_role(ROLE_ADMIN)
def do_edit_user(request, user_id=None):
    """
    Edit a user.  This can also create a user.  If a new user is created the
    dialog is simplified, some unimportant details are left out.
    """
    user = None
    errors = []
    form = dict.fromkeys(['username', 'first_name', 'last_name',
                          'display_name', 'description', 'email'], u'')
    form['role'] = ROLE_AUTHOR
    csrf_protector = CSRFProtector()
    redirect = IntelligentRedirect()

    if user_id is not None:
        user = User.objects.get(user_id)
        print user_id, user
        if user is None:
            raise NotFound()
        form.update(
            username=user.username,
            first_name=user.first_name,
            last_name=user.last_name,
            #display_name=user._display_name,
            description=user.description,
            email=user.email,
            role=user.role
        )
    new_user = user is None

    if request.method == 'POST':
        csrf_protector.assert_safe()
        if request.form.get('cancel'):
            return redirect('admin/show_users')
        elif request.form.get('delete') and user:
            return simple_redirect('admin/delete_user', user_id=user.user_id)

        username = form['username'] = request.form.get('username')
        if not username:
            errors.append(_('Username is required.'))
        elif new_user and User.objects.filter_by(username=username).first() \
             is not None:
            errors.append(_(u'Username “%s” is taken.') % username)
        password = form['password'] = request.form.get('password')
        if new_user and not password:
            errors.append(_('You have to provide a password.'))
        first_name = form['first_name'] = request.form.get('first_name')
        last_name = form['last_name'] = request.form.get('last_name')
        display_name = form['display_name'] = request.form.get('display_name')
        description = form['description'] = request.form.get('description')
        email = form['email'] = request.form.get('email', '')
        if not is_valid_email(email):
            errors.append(_('The user needs a valid mail address.'))
        try:
            role = form['role'] = int(request.form.get('role', ''))
            if role not in xrange(ROLE_ADMIN + 1):
                raise ValueError()
        except ValueError:
            errors.append(_('Invalid user role.'))

        if not errors:
            if new_user:
                user = User(username, password, email, first_name,
                            last_name, description, role)
                user.display_name = display_name or '$username'
                msg = 'User %s created successfully.'
                icon = 'add'
            else:
                user.username = username
                if password:
                    user.set_password(password)
                user.email = email
                user.first_name = first_name
                user.last_name = last_name
                user.display_name = display_name or '$username'
                user.description = description
                user.role = role
                msg = 'User %s edited successfully.'
                icon = 'info'
            db.commit()
            html_user_detail = u'<a href="%s">%s</a>' % (
                escape(url_for(user)),
                escape(user.username)
            )
            flash(msg % html_user_detail, icon)
            if request.form.get('save'):
                return redirect('admin/show_users')
            return simple_redirect('admin/edit_user', user_id=user.user_id)

    if not new_user:
        display_names = [
            ('$nick', user.username),
        ]
        if user.first_name:
            display_names.append(('$first', user.first_name))
        if user.last_name:
            display_names.append(('$last', user.last_name))
        if user.first_name and user.last_name:
            display_names.extend([
                ('$first $last', u'%s %s' % (user.first_name, user.last_name)),
                ('$last $first', u'%s %s' % (user.last_name, user.first_name)),
                (u'$first “$nick” $last', u'%s “%s” %s' % (
                    user.first_name,
                    user.username,
                    user.last_name
                ))
            ])
    else:
        display_names = None

    for error in errors:
        flash(error, 'error')

    return render_admin_response('admin/edit_user.html', 'users.edit',
        new_user=user is None,
        user=user,
        form=form,
        display_names=display_names,
        roles=[
            (ROLE_ADMIN, _('Administrator')),
            (ROLE_EDITOR, _('Editor')),
            (ROLE_AUTHOR, _('Author')),
            (ROLE_SUBSCRIBER, _('Subscriber'))
        ],
        hidden_form_data=make_hidden_fields(csrf_protector, redirect)
    )


@require_role(ROLE_ADMIN)
def do_delete_user(request, user_id):
    """
    Like all other delete screens just that it deletes a user.
    """
    user = User.objects.get(user_id)
    csrf_protector = CSRFProtector()
    redirect = IntelligentRedirect()

    if user is None:
        return redirect('admin/show_users')
    elif user == request.user:
        flash(_('You cannot delete yourself.'), 'error')
        return redirect('admin/show_users')

    if request.method == 'POST':
        csrf_protector.assert_safe()
        if request.form.get('cancel'):
            return redirect('admin/edit_user', user_id=user.user_id)
        elif request.form.get('confirm'):
            redirect.add_invalid('admin/edit_user', user_id=user.user_id)
            action = request.form.get('action')
            action_val = None
            if action == 'reassign':
                action_val = request.form.get('reassign_user', type=int)
                db.execute(posts.update(posts.c.author_id == user_id), dict(
                    author_id=action_val
                ))
            #! plugins can use this to react to user deletes.  They can't stop
            #! the deleting of the user but they can delete information in
            #! their own tables so that the database is consistent afterwards.
            #! Additional to the user object an action and action val is
            #! provided.  The action can be one of the following values:
            #!  "reassign":     Reassign the objects to the user with the
            #!                  user_id of "action_val".
            #!  "delete":       Delete related objects.
            #! More actions might be added in the future so plugins should
            #! ignore unknown actions.  If an unknown action is provided
            #! the plugin should treat is as "delete".
            emit_event('before-user-deleted', user, action, action_val)
            db.delete(user)
            flash(_('User %s deleted successfully.') %
                  escape(user.username), 'remove')
            db.commit()
            return redirect('admin/show_users')

    return render_admin_response('admin/delete_user.html', 'users.edit',
        user=user,
        other_users=User.objects.filter(User.user_id != user_id).all(),
        hidden_form_data=make_hidden_fields(csrf_protector, redirect)
    )


@require_role(ROLE_ADMIN)
def do_options(request):
    """
    So far just a redirect page, later it would be a good idea to have
    a page that shows all the links to configuration things in form of
    a simple table.
    """
    return simple_redirect('admin/basic_options')


@require_role(ROLE_ADMIN)
def do_basic_options(request):
    """
    The dialog for basic options such as the blog title etc.
    """
    cfg = request.app.cfg
    form = {
        'blog_title':           cfg['blog_title'],
        'blog_tagline':         cfg['blog_tagline'],
        'blog_email':           cfg['blog_email'],
        'timezone':             cfg['timezone'],
        'datetime_format':      cfg['datetime_format'],
        'date_format':          cfg['date_format'],
        'session_cookie_name':  cfg['session_cookie_name'],
        'comments_enabled':     cfg['comments_enabled'],
        'pings_enabled':        cfg['pings_enabled'],
        'default_parser':       cfg['default_parser'],
        'comment_parser':       cfg['comment_parser'],
        'posts_per_page':       cfg['posts_per_page'],
        'use_flat_comments':    cfg['use_flat_comments']
    }
    errors = []
    csrf_protector = CSRFProtector()

    if request.method == 'POST':
        csrf_protector.assert_safe()
        form['blog_title'] = blog_title = request.form.get('blog_title')
        if not blog_title:
            errors.append(_('You have to provide a blog title'))
        form['blog_tagline'] = blog_tagline = request.form.get('blog_tagline')
        form['blog_email'] = blog_email = request.form.get('blog_email', '')
        if blog_email and not is_valid_email(blog_email):
            errors.append(_('You have to provide a valid e-mail address '
                            'for the blog e-mail field.'))
        form['timezone'] = timezone = request.form.get('timezone')
        if timezone not in TIMEZONES:
            errors.append(_(u'Unknown timezone “%s”') % timezone)
        form['datetime_format'] = datetime_format = \
            request.form.get('datetime_format')
        form['date_format'] = date_format = \
            request.form.get('date_format')
        form['session_cookie_name'] = session_cookie_name = \
            request.form.get('session_cookie_name')
        form['comments_enabled'] = comments_enabled = \
            'comments_enabled' in request.form
        form['pings_enabled'] = pings_enabled = \
            'pings_enabled' in request.form
        form['default_parser'] = default_parser = \
            request.form.get('default_parser')
        if default_parser not in request.app.parsers:
            errors.append(_('Unknown parser %s.') % default_parser)
        form['comment_parser'] = comment_parser = \
            request.form.get('comment_parser')
        if comment_parser not in request.app.parsers:
            errors.append(_('Unknown parser %s.') % comment_parser)
        form['posts_per_page'] = request.form.get('posts_per_page', '')
        try:
            posts_per_page = int(form['posts_per_page'])
            if posts_per_page < 1:
                errors.append(_('Posts per page must be at least 1'))
        except ValueError:
            errors.append(_('Posts per page must be a valid integer'))
        form['use_flat_comments'] = use_flat_comments = \
            'use_flat_comments' in request.form
        form['maintenance_mode'] = maintenance_mode = \
            'maintenance_mode' in request.form
        if not errors:
            if blog_title != cfg['blog_title']:
                cfg['blog_title'] = blog_title
            if blog_tagline != cfg['blog_tagline']:
                cfg['blog_tagline'] = blog_tagline
            if timezone != cfg['timezone']:
                cfg['timezone'] = timezone
            if datetime_format != cfg['datetime_format']:
                cfg['datetime_format'] = datetime_format
            if date_format != cfg['date_format']:
                cfg['date_format'] = date_format
            if session_cookie_name != cfg['session_cookie_name']:
                cfg['session_cookie_name'] = session_cookie_name
            if comments_enabled != cfg['comments_enabled']:
                cfg['comments_enabled'] = comments_enabled
            if pings_enabled != cfg['pings_enabled']:
                cfg['pings_enabled'] = pings_enabled
            if default_parser != cfg['default_parser']:
                cfg['default_parser'] = default_parser
            if comment_parser != cfg['comment_parser']:
                cfg['comment_parser'] = comment_parser
            if posts_per_page != cfg['posts_per_page']:
                cfg['posts_per_page'] = posts_per_page
            if use_flat_comments != cfg['use_flat_comments']:
                cfg['use_flat_comments'] = use_flat_comments
            flash(_('Configuration altered successfully.'), 'configure')
            return simple_redirect('admin/basic_options')

        for error in errors:
            flash(error, 'error')

    return render_admin_response('admin/basic_options.html', 'options.basic',
        form=form,
        timezones=sorted(TIMEZONES),
        parsers=request.app.list_parsers(),
        hidden_form_data=make_hidden_fields(csrf_protector)
    )




@require_role(ROLE_ADMIN)
def do_cache(request):
    """Configure the cache."""
    csrf_protector = CSRFProtector()
    cfg = request.app.cfg
    form = {
        'cache_system':             cfg['cache_system'],
        'cache_timeout':            cfg['cache_timeout'],
        'enable_eager_caching':     cfg['enable_eager_caching'],
        'memcached_servers':        cfg['memcached_servers'],
        'filesystem_cache_path':    cfg['filesystem_cache_path']
    }
    errors = []

    if request.method == 'POST':
        csrf_protector.assert_safe()

        if 'clear_cache' in request.form:
            request.app.cache.clear()
            flash(_('The cache was cleared successfully.'), 'configure')
            return redirect(url_for('admin/cache'))

        form['cache_system'] = cache_system = \
            request.form.get('cache_system')
        if cache_system not in cache.systems:
            errors.append(_('Invalid cache system selected.'))
        form['cache_timeout'] = cache_timeout = \
            request.form.get('cache_timeout', '')
        if not cache_timeout.isdigit():
            errors.append(_('Cache timeout must be positive integer.'))
        else:
            cache_timeout = int(cache_timeout)
            if cache_timeout < 10:
                errors.append(_('Cache timeout must be greater than 10 '
                                'seconds.'))
        form['enable_eager_caching'] = enable_eager_caching = \
            'enable_eager_caching' in request.form
        form['memcached_servers'] = memcached_servers = \
            request.form.get('memcached_servers', '')
        form['filesystem_cache_path'] = filesystem_cache_path = \
            request.form.get('filesystem_cache_path', '')

        if not errors:
            if cache_system != cfg['cache_system']:
                cfg['cache_system'] = cache_system
            if cache_timeout != cfg['cache_timeout']:
                cfg['cache_timeout'] = cache_timeout
            if enable_eager_caching != cfg['enable_eager_caching']:
                cfg['enable_eager_caching'] = enable_eager_caching
            if memcached_servers != cfg['memcached_servers']:
                cfg['memcached_servers'] = memcached_servers
            if filesystem_cache_path != cfg['filesystem_cache_path']:
                cfg['filesystem_cache_path'] = filesystem_cache_path
            flash(_('Updated cache settings.'), 'configure')
        else:
            flash(errors[0], 'error')

    return render_admin_response('admin/cache.html', 'options.cache',
        hidden_form_data=make_hidden_fields(csrf_protector),
        form=form,
        cache_systems=[
            ('simple', _('Simple Cache')),
            ('memcached', _('memcached')),
            ('filesystem', _('Filesystem')),
            ('null', _('No Cache'))
        ]
    )


@require_role(ROLE_ADMIN)
def do_configuration(request):
    """
    Advanced configuration editor.  This is useful for development or if a
    plugin doesn't ship an editor for the configuration values.  Because all
    the values are not further checked it could easily be that TextPress is
    left in an unusable state if a variable is set to something bad.  Because
    of this the editor shows a warning and must be enabled by hand.
    """
    csrf_protector = CSRFProtector()
    if request.method == 'POST':
        csrf_protector.assert_safe()
        if request.form.get('enable_editor'):
            request.session['ace_on'] = True
        elif request.form.get('disable_editor'):
            request.session['ace_on'] = False
        else:
            already_default = set()
            for key, value in request.form.iteritems():
                key = key.replace('.', '/')
                if key.endswith('__DEFAULT'):
                    key = key[:-9]
                    request.app.cfg.revert_to_default(key)
                    already_default.add(key)
                elif key in request.app.cfg and key not in already_default:
                    request.app.cfg.set_from_string(key, value)
        return simple_redirect('admin/configuration')

    # html does not allow slashes.  Convert them to dots
    categories = []
    for category in request.app.cfg.get_detail_list():
        for item in category['items']:
            item['key'] = item['key'].replace('/', '.')
        categories.append(category)

    return render_admin_response('admin/configuration.html',
                                 'options.configuration',
        categories=categories,
        editor_enabled=request.session.get('ace_on', False),
        csrf_protector=csrf_protector
    )


@require_role(ROLE_ADMIN)
def do_maintenance(request):
    """Enable / Disable maintenance mode."""
    cfg = request.app.cfg
    form = {
        'maintenance_mode':     cfg['maintenance_mode']
    }
    csrf_protector = CSRFProtector()
    if request.method == 'POST':
        csrf_protector.assert_safe()
        cfg['maintenance_mode'] = 'maintenance_mode' in request.form
        flash(_('Configuration altered successfully.'), 'configure')
        return simple_redirect('admin/maintenance')

    return render_admin_response('admin/maintenance.html',
                                 'maintenance.overview',
        form=form,
        hidden_form_data=make_hidden_fields(csrf_protector)
    )



@require_role(ROLE_AUTHOR)
def do_eventmap(request):
    """
    The GUI version of the `textpress-management.py eventmap` command.
    Traverses the sourcecode for emit_event calls using the python2.5
    ast compiler.  Because of that it raises an page not found exception
    for python2.4.
    """
    if not can_build_eventmap:
        raise NotFound()
    return render_admin_response('admin/eventmap.html', 'about.eventmap',
        get_map=lambda: sorted(build_eventmap(request.app).items()),
        # walking the tree can take some time, so better use stream
        # processing for this template. that's also the reason why
        # the building process is triggered from inside the template.
        # stream rendering however is buggy in wsgiref :-/
        _stream=True
    )


@require_role(ROLE_AUTHOR)
def do_about_textpress(request):
    """
    Just show the textpress license and some other legal stuff.
    """
    return render_admin_response('admin/about_textpress.html',
                                 'about.textpress')


@require_role(ROLE_AUTHOR)
def do_change_password(request):
    """
    Allow the current user to change his password.
    """
    errors = []
    csrf_protector = CSRFProtector()
    redirect = IntelligentRedirect()

    if request.method == 'POST':
        csrf_protector.assert_safe()
        if request.form.get('cancel'):
            return redirect('admin/index')
        old_password = request.form.get('old_password')
        if not old_password:
            errors.append(_('You have to enter your old password.'))
        if not request.user.check_password(old_password):
            errors.append(_('Your old password is wrong.'))
        new_password = request.form.get('new_password')
        if not new_password:
            errors.append(_('Your new password cannot be empty.'))
        check_password = request.form.get('check_password')
        if new_password != check_password:
            errors.append(_('The passwords do not match.'))
        if not errors:
            request.user.set_password(new_password)
            db.commit()
            flash(_('Password changed successfully.'), 'configure')
            return redirect('admin/index')

    # just flash the first error, that's enough for the user
    if errors:
        flash(errors[0], 'error')

    return render_admin_response('admin/change_password.html',
        hidden_form_data=make_hidden_fields(csrf_protector, redirect)
    )

@require_role(ROLE_AUTHOR)
def do_about(request):
    """
    Shows some details about this TextPress installation.  It's useful for
    debugging and checking configurations.  If severe errors in a TextPress
    installation occour it's a good idea to dump this page and attach it to
    a bug report mail.
    """
    from threading import activeCount
    from jinja.defaults import DEFAULT_NAMESPACE, DEFAULT_FILTERS

    thread_count = activeCount()
    #version_info = get_version_info()

    return render_admin_response('admin/about.html', 'about.system',
        #apis=[{
        #    'name':         name,
        #    'blog_id':      blog_id,
        #    'preferred':    preferred,
        #    'endpoint':     endpoint
        #} for name, (blog_id, preferred, endpoint) in request.app.apis.iteritems()],
        endpoints=[{
            'name':         rule.endpoint,
            'rule':         unicode(rule)
        } for rule in sorted(request.app.map._rules, key=lambda x: x.endpoint)],
        #servicepoints=sorted(request.app._services.keys()),
        configuration=[{
            'key':          key,
            'default':      default,
            'value':        request.app.cfg[key]
        } for key, (_, default) in sorted(request.app.cfg.config_vars.iteritems())],
        hosting_env={
            'persistent':       not request.is_run_once,
            'multithreaded':    request.is_multithread,
            'thread_count':     thread_count,
            'multiprocess':     request.is_multiprocess,
            'wsgi_version':     '.'.join(map(str, request.environ['wsgi.version']))
        },
        #plugins=sorted(request.app.plugins.values(), key=lambda x: x.name),
        #textpress_version='.'.join(map(str, version_info[0:3])),
        #textpress_tag=version_info[3],
        #textpress_hg_node=version_info[4],
        #textpress_hg_checkout=version_info[4] is not None,
        template_globals=[name for name, obj in
                          sorted(request.app.template_env.globals.items())
                          if name not in DEFAULT_NAMESPACE],
        template_filters=[name for name, obj in
                          sorted(request.app.template_env.filters.items())
                          if name not in DEFAULT_FILTERS],
        can_build_eventmap=can_build_eventmap,
        instance_path=request.app.instance_dir,
        database_uri=str(request.app.db_engine.url)
    )


def do_login(request):
    """Show a login page."""
    if request.user.is_somebody:
        return simple_redirect('admin/index')
    error = None
    username = ''
    redirect = IntelligentRedirect()

    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password', '')
        if username:
            user = User.objects.filter_by(username=username).first()
            if user is None:
                error = _('User %s does not exist.') % escape(username)
            elif user.check_password(password):
                request.login(user, 'permanent' in request.form)
                print user
                return redirect('admin/index')
            else:
                error = _('Incorrect password.')
        else:
            error = _('You have to enter a username.')

    return render_response('admin/login.html', error=error,
                           username=username,
                           logged_out=request.values.get('logout') == 'yes',
                           hidden_redirect_field=redirect)


def do_logout(request):
    """Just logout and redirect to the login screen."""
    request.logout()
    return IntelligentRedirect()('admin/login', logout='yes')

def setup(app):

    from glashammer.bundles.auth import setup as setup_auth
    app.add_setup(setup_auth)

    app.add_url('/login', endpoint='admin/login', view=do_login)
    app.add_url('/logout', endpoint='admin/logout', view=do_logout)
    app.add_url('/admin/index', endpoint='admin/index', view=do_index)
    app.add_url('/admin/users', endpoint='admin/show_users',
                view=do_show_users, defaults={'page':1})
    app.add_url('/admin/users/page/<int:page>', endpoint='admin/show_users'),

    app.add_url('/admin/users/<int:user_id>', endpoint='admin/edit_user',
                view=do_edit_user),
    app.add_url('/admin/users/new', endpoint='admin/new_user',
                view=do_edit_user),
    app.add_url('/change_password', endpoint='admin/change_password',
                view=do_change_password)

    app.add_url('/options/configuration', endpoint='admin/configuration',
                view=do_configuration)

    app.add_url('/about/', endpoint='admin/about', view=do_about)
    app.add_url('/about/eventmap', endpoint='admin/eventmap', view=do_eventmap),
    app.add_template_searchpath(sibpath(__file__, 'templates'))
    app.add_shared('admin', sibpath(__file__, 'shared'))

