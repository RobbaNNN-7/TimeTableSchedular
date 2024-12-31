from flask import Flask, request, jsonify, render_template, send_file
from Module1_classTimetables.TimeTableSchedular.TimeTable import TimeTableCSP
import os
import json

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('timetable.html')

@app.route('/generate', methods=['POST'])
def generate_timetable():
    try:
        data = request.json
        
        # Validate input data
        if not data.get('sections') or not data.get('courses'):
            return jsonify({
                'success': False,
                'message': 'Missing required data (sections or courses)'
            }), 400

        # Create scheduler instance with provided data
        scheduler = TimeTableCSP(
            sections=data['sections'],
            courses=data['courses'],
            theory_rooms=data.get('theory_rooms'),
            lab_rooms=data.get('lab_rooms')
        )
        
        # Run Monte Carlo simulation
        results = scheduler.monte_carlo_simulation(num_iterations=1000)
        
        if results['success_rate'] > 0:
            filename = "generated_timetable.xlsx"
            scheduler.export_to_excel(filename)
            
            return jsonify({
                'success': True,
                'message': 'Timetable generated successfully!',
                'stats': {
                    'success_rate': (f"{results['success_rate']:.2f}%"),
                    'best_score': (f"{results['best_score']:.2f}"),
                    'filename': filename
                }
            })
        
        return jsonify({
            'success': False,
            'message': 'Failed to generate a valid timetable',
            'stats': results
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error: {str(e)}'
        }), 500

@app.route('/download/<filename>')
def download_file(filename):
    try:
        return send_file(filename, as_attachment=True)
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error downloading file: {str(e)}'
        }), 500

@app.route('/add-makeup', methods=['POST'])
def add_makeup_class():
    try:
        data = request.json
        required_fields = ['section', 'course', 'is_lab']
        if not all(field in data for field in required_fields):
            return jsonify({
                'success': False,
                'message': 'Missing required fields'
            }), 400

        # Load existing timetable
        scheduler = TimeTableCSP()
        success = scheduler.add_makeup_class(
            data['section'],
            data['course'],
            data.get('is_lab', False)
        )

        if success:
            filename = "updated_timetable.xlsx"
            scheduler.export_to_excel(filename)
            return jsonify({
                'success': True,
                'message': 'Makeup class added successfully!',
                'filename': filename
            })
        
        return jsonify({
            'success': False,
            'message': 'Could not find suitable slot for makeup class'
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error: {str(e)}'
        }), 500

if __name__ == '__main__':
    app.run(debug=True)