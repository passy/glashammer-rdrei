


def create_middleware(app, log_filename='repozeprofile.log',
        discard_first_request=True, flush_at_shutdown=True,
        path='/__profile__'):

    from repoze.profile.profiler import AccumulatingProfileMiddleware
    return AccumulatingProfileMiddleware(app,
        log_filename=log_filename,
        discard_first_request=discard_first_request,
        flush_at_shutdown=flush_at_shutdown,
        path=path
    )


def setup_repozeprofile(app):
    app.add_middleware(create_middleware)

