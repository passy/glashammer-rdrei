
from glashammer.utils import render_response, redirect_to

from models import Page, Revision, session


def _get_page(name):
    return session.query(Page).get(name)


def view_index(req):
    pages = session.query(Page)
    return render_response('index.jinja', pages=pages)


def view_show(req, page_name):
    page = _get_page(page_name)
    if page is None:
        return redirect_to('edit', page_name=page_name)
    return render_response('show.jinja', page=page)


def view_edit(req, page_name):
    page = _get_page(page_name)
    if req.method == 'POST':
        if page is None:
            page = Page(name=page_name)
            session.add(page)
        rev = Revision(page=page, text=req.form.get('text'))
        session.add(rev)
        session.commit()
        return redirect_to('show', page_name=page.name)
    else:
        if page is not None:
            page_name = page.name
        return render_response('edit.jinja', page=page, page_name=page_name)


def view_new(req):
    page_name = req.args.get('page_name')
    if page_name:
        return redirect_to('edit', page_name=page_name)
    else:
        return redirect_to('index')

