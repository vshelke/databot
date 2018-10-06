from flask import Flask, render_template, request
from query_parser import process_query
app = Flask(__name__)

@app.route('/')
def index():
    return render_template('main.html')

@app.route('/search', methods=['GET'])
def search():
    query = request.args.get('q')
    results = process_query(query)
    data = {
        'query': query,
        'results': results
    }
    if len(data['results']['rows']) > 25:
        data['results']['rows'] = data['results']['rows'][:25]
    return render_template('results.html', data=data)

if __name__ == "__main__":
    app.run(debug=True, port=8080)