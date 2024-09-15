from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import pandas as pd
import pickle
import json
import os
from datetime import datetime
from pymongo import MongoClient
from bson.objectid import ObjectId

app = Flask(__name__)
CORS(app)

client = MongoClient("mongodb+srv://admin:admin@cluster0.cvj0l.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0")
db = client["cluster0"]  
collection = db["values"]  

with open('model.pkl', 'rb') as model_file:
    model = pickle.load(model_file)

@app.route("/",methods=['GET'])
def home():
    return jsonify("Hello World DiabTech Backend!!! ")

# Test route to check the connection
@app.route('/test', methods=['GET'])
def test():
    return jsonify({"message": "Connection successful"}), 200

@app.route('/read', methods=['GET'])
def read_records():
    records = list(collection.find())  
    for record in records:
        record["_id"] = str(record["_id"])
    return jsonify(records), 200

@app.route("/data",methods=['POST'])
def demo():
    data = request.json
    print("data recived from ardino: "+data)
    return jsonify({"data":data}),400

# @app.route('/send_json',methods=['GET'])
# def send_json_file():
#     json_file_path = './public/glucose_results.json'
#     with open(json_file_path, 'r') as f:
#         json_data = json.load(f)

#     return jsonify(json_data)

@app.route("/check-glucose", methods=['POST'])
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

        output = {
            "input": float_data,
            "result": result[0],
            "timestamp": datetime.now().isoformat()
        }

        file_path = './public/glucose_results.json'
        with open(file_path, 'a') as f:
            json.dump(output, f)
            f.write("\n")

        mongo_document = {
            "input": float_data,
            "predicted_result": result[0],
            "timestamp": datetime.now().isoformat()
        }
        
        unique_id = "66e6ec78caff0600c6e447e3"

        collection.update_one(
            {"_id": unique_id},
            {"$set": mongo_document},  
            upsert=True  
        )
        
        return jsonify({"result": result[0]}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)