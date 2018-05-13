def uwsgi_reloading() -> None:
    try:
        import uwsgi
        from uwsgidecorators import timer
        from django.utils import autoreload

        @timer(3)
        def change_code_gracefull_reload(sig):
            if autoreload.code_changed():
                print("RELOADING...")
                uwsgi.reload()

        print("UWSGI RELOADING ENABLED")
    except Exception as e:
        print("WSGI RELOADING NOT AVAILABLE: {}".format(e))
        return


def init() -> None:
    uwsgi_reloading()
