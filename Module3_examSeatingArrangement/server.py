from flask import Flask, request, render_template

app = Flask(__name__)

from src.GA import *

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/seatingArrangement', methods=['POST'])
def seating_arrangement_route():
    data = request.get_json()
    classrooms = [Classroom(**c) for c in data['classrooms']]
    students = [Student(**s) for s in data['students']]
    ga = GeneticAlgorithm(students, classrooms)
    arrangement = ga.evolve()

    response = {
        "seatingArrangement": [
            {
                "classroom": classroom.name,
                "seating": [
                    [
                        student.to_dict() for student in column
                    ] for column in classroom.seating
                ]
            }
            for classroom in arrangement
        ]
    }

    return response


if __name__ == '__main__':
    app.run(debug=True)