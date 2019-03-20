from cirex import create_app, db
from cirex.models import Search, Database, Article, Result

app = create_app()


@app.shell_context_processor
def make_shell_context():
    return {'db': db, 'Search': Search, 'Article': Article, 'Database': Database,
            'Result': Result}
