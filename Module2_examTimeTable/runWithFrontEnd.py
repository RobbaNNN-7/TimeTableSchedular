from flask import Flask, render_template, request, jsonify, send_file
import pandas as pd
import json
from run import main  

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/submit', methods=['POST'])
def submit():
    try:
        input_data = request.json
        with open('input.json', 'w') as file:
            json.dump(input_data, file, indent=4)

        
        main()  # Run the main function from run.py

        return jsonify({"status": "success", "filename": "best_exam_schedule.xlsx"})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})

@app.route('/download/<filename>')
def download_file(filename):
    return send_file(filename, as_attachment=True)

if __name__ == '__main__':
    app.run(debug=True)
