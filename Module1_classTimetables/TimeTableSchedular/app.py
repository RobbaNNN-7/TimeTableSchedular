from flask import Flask, request, jsonify, render_template, send_file
import os
import json
from TimeTable import TimeTable

app = Flask(__name__)

# Global variable to store the current timetable instance
current_timetable = None

@app.route('/')
def index():
    return render_template('timetable.html')

@app.route('/generate', methods=['POST'])
def generate_timetable():
    global current_timetable
    try:
        data = request.json
        
        # Validate input data
        if not data.get('sections') or not data.get('courses'):
            return jsonify({
                'success': False,
                'message': 'Missing required data (sections or courses)'
            }), 400

        # Create scheduler instance with provided data
        current_timetable = TimeTable(
            sections=data['sections'],
            courses=data['courses'],
            theory_rooms=data.get('theory_rooms'),
            lab_rooms=data.get('lab_rooms')
        )
        
        # Run Monte Carlo simulation
        results = current_timetable.monte_carlo_simulation(num_iterations=1000)
        
        if results['success_rate'] > 0:
            filename = "generated_timetable.xlsx"
            filepath = os.path.join(app.root_path, filename)
            current_timetable.export_to_excel(filepath)
            
            return jsonify({
                'success': True,
                'message': 'Timetable generated successfully!',
                'stats': {
                    'success_rate': f"{results['success_rate']:.2f}%",
                    'best_score': f"{results['best_score']:.2f}",
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
        filepath = os.path.join(app.root_path, filename)
        if not os.path.exists(filepath):
            return jsonify({
                'success': False,
                'message': 'Timetable file not found. Please generate a timetable first.'
            }), 404
        return send_file(filepath, as_attachment=True)
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error downloading file: {str(e)}'
        }), 500

@app.route('/add-makeup', methods=['POST'])
def add_makeup_class():
    global current_timetable
    try:
        if current_timetable is None:
            return jsonify({
                'success': False,
                'message': 'No timetable exists. Please generate a timetable first.'
            }), 400

        data = request.json
        required_fields = ['section', 'course', 'is_lab']
        if not all(field in data for field in required_fields):
            return jsonify({
                'success': False,
                'message': 'Missing required fields'
            }), 400

        success = current_timetable.add_makeup_class(
            data['section'],
            data['course'],
            data.get('is_lab', False)
        )

        if success:
            filename = "updated_timetable.xlsx"
            filepath = os.path.join(app.root_path, filename)
            current_timetable.export_to_excel(filepath)
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