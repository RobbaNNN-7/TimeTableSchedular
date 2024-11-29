from flask import Flask, request, render_template

app = Flask(__name__)

from src.GA import *

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/seatingArrangement', methods=['GET'])
def seating_arrangement_route():
    data = request.args.get('data')
    ga = GeneticAlgorithm(data['students'],data['classrooms'])
    response = ga.evolve()
    return response.to_json()

if __name__ == '__main__':
    app.run(debug=True)