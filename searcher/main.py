from flask import Flask, render_template, request
from engine import get_df, process_query
import logging

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)

app = Flask(__name__)
df = get_df()


@app.route('/', methods=['get', 'post'])
def index():
    if request.form:
        query = request.form.get('query')
        entries = process_query(query, df)
        logger.info('-> QUERY: {}'.format(query))
        return render_template('search.html', query=query, entries=entries)

    return render_template('search.html')


if __name__ == '__main__':
    app.run(debug=True)
