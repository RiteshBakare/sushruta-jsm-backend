from flask import Flask, request, jsonify
from flask_cors import CORS
import pandas as pd
import pickle

app = Flask(__name__)
CORS(app)

with open('model.pkl', 'rb') as model_file:
    model = pickle.load(model_file)

@app.route("/",methods=['GET'])
def home():
    return jsonify("Hello World DiabTech Backend!!! ")

@app.route("/check-glucose",methods=['POST'])
def predictGlucose():
    try:
        data = request.json

        if not isinstance(data, list) or len(data) != 14:
            return jsonify({"error": "Input must be an array of 14 floats"}), 400

        float_data = []
        for value in data:
            try:
                float_value = float(value)
                float_data.append(float_value)
            except ValueError:
                return jsonify({"error": f"'{value}' is not a valid float"}), 400

        result = model.predict([float_data])  

        # print(float_data)
        # print(result)

        return jsonify({"glucose result: ":result[0]}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)