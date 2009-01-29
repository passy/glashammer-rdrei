# -*- coding: utf-8 -*-
"""
    glashammer.utils.webbish
    ~~~~~~~~~~~~~~~~~~~~~~~~

    :copyright: 2007-2008 by Armin Ronacher, Ali Afshar
    :license: MIT
"""
import math

from glashammer.utils.local import url_for, local



class Pagination(object):
    """Pagination helper."""

    def __init__(self, endpoint, page, per_page, total, url_args=None):
        self.endpoint = endpoint
        self.page = page
        self.per_page = per_page
        self.total = total
        self.pages = int(math.ceil(self.total / float(self.per_page)))
        self.url_args = url_args or {}
        self.necessary = self.pages > 1

    def generate(self, normal='<a href="%(url)s">%(page)d</a>',
                 active='<strong>%(page)d</strong>',
                 commata='<span class="commata">,\n</span>',
                 ellipsis=u'<span class="ellipsis">...\n</span>',
                 threshold=3, prev_link=True,
                 next_link=True, gray_prev_link=True, gray_next_link=True):
        was_ellipsis = False
        result = []
        prev = None
        next = None
        small_threshold = math.ceil(threshold / 2.0)
        get_link = lambda x: url_for(self.endpoint, page=x, **self.url_args)

        for num in xrange(1, self.pages + 1):
            if num == self.page:
                was_ellipsis = False
            if num - 1 == self.page:
                next = num
            if num + 1 == self.page:
                prev = num
            if num <= small_threshold or \
               num > self.pages - small_threshold or \
               abs(self.page - num) < threshold:
                if result and result[-1] != ellipsis:
                    result.append(commata)
                was_space = False
                link = get_link(num)
                template = num == self.page and active or normal
                result.append(template % {
                    'url':      link,
                    'page':     num
                })
            elif not was_ellipsis:
                was_ellipsis = True
                result.append(ellipsis)

        if next_link:
            if next is not None:
                result.append(u' <a href="%s">Next &raquo;</a>' %
                              get_link(next))
            elif gray_next_link:
                result.append(u' <span class="disabled">Next &raquo;</span>')
        if prev_link:
            if prev is not None:
                result.insert(0, u'<a href="%s">&laquo; Prev</a> ' %
                              get_link(prev))
            elif gray_prev_link:
                result.insert(0, u'<span class="disabled">&laquo; Prev</span> ')

        return u''.join(result)

class NavigationItem(object):
    """An item that contains navigation information"""
    def __init__(self, title, endpoint, rule_args={}, children=[],
                 nolink=False):
        self.title = title
        self.endpoint = endpoint
        self.children = children
        self.rule_args = rule_args
        self.nolink = nolink

    def get_url(self):
        return url_for(self.endpoint, **self.rule_args)

def flash(msg, type='info'):
    """Add a message to the message flash buffer.

    The default message type is "info", other possible values are
    "add", "remove", "error", "ok" and "configure". The message type affects
    the icon and visual appearance.

    The flashes messages appear only in the admin interface!
    """
    assert type in ('info', 'add', 'remove', 'error', 'ok', 'configure')
    if type == 'error':
        msg = (u'<strong>%s:</strong> ' % _('Error')) + msg
    local.session.setdefault('admin/flashed_messages', []).\
            append((type, msg))

