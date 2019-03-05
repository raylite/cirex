from cirex import app, db
from cirex.models import Search, Database, Article, Result


@app.shell_context_processor
def make_shell_context():
    return {'db': db, 'Search': Search, 'Article': Article, 'Database': Database,
            'Result': Result}