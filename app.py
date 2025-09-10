# Import required packages
from flask import Flask, jsonify, request
from flask_cors import CORS
import mysql.connector
import pickle
import json

# Mysql config
app = Flask(__name__)
app.config['JSON_SORT_KEYS'] = False

# For Flask 2.3 and later use this:
app.json.sort_keys = False
CORS(app)

def is_numeric(value):
    try:
        float(value)
        return True
    except ValueError:
        return False

# 404 page
@app.errorhandler (404)
def not_found (error=None):
    response = {
        'message': 'Invalid request',
    }
    return jsonify(response)

# Prediction page
@app.route('/predict', methods = ['POST'])
def predict():
    form = request.form.values()
    data = [x for x in form if x != '']
    
    if len((data)) < 18:
        response = {
            'response' : '17 inputes expected '+str(len(data))+' received.'
        }

        return jsonify(response), 200
   
    # Remove name and class fields from list    
    predict_data = [int(e) for e in data if e not in (data[0], data[1]) or is_numeric(e)]
    
    if len((predict_data)) < 16:
        response = {
            'response' : '16 inputes expected '+str(len(predict_data))+' received.'
        }

        return jsonify(response), 200

    try:
        # Load model
        model = pickle.load(open('predictor.pickle', 'rb'))
        
        # Predict result
        rawRes = model.predict([predict_data])
    except Exception as error:
        return {
            'response': 'Someting is wrong with pickle file. Error:'+format(error)
        }
    
    # Calculate percentage
    result = rawRes[0] * 100

    # Append result in the list
    data.append(float(result))
    
    # Append client IP Address in the list
    data.append(request.remote_addr)

    try:
        # Making database connection 
        connection = mysql.connector.connect(
            host='localhost',
            user='root',
            password='',
            database='plecematepro'
        )

        # Create cursor object
        cursor = connection.cursor()

        # Make SQL Query
        sql = 'INSERT INTO data (name, class, academic_performance, technical_skills, core_knowledge, puzzle_solving, programming_skills, group_discussion_score, project,internship, backlog, coding_skills, aptitude_skills, communication_skills, presentation_skills, english_proficiency, management_skills, training, result, ip_address) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)'
        
        # Execute SQL command
        cursor.execute(sql, data)

        # Commit changes
        connection.commit()
        
        # Close connection
        if connection.is_connected():
            connection.close()

    except Exception as error:
        print("Failed to insert record into database. Error:"+format(error))

    response = {
        'result' : result
    }
    
    # Return response
    return jsonify(response), 200

# Result page
@app.route('/result', methods=['GET'])
def get_result():

    # Create response 
    response = {
        'app' : 'plecematespro',
        'request': request.remote_addr,
        'api_version' : 1.0,
        'status' : 200,
    }

    # Error handling
    try:
        # Get column names
        colsStr = 'id,name,class,academic_performance,technical_skills,core_knowledge,puzzle_solving,programming_skills,group_discussion_score,project,internship,backlog,coding_skills,aptitude_skills,communication_skills,presentation_skills,english_proficiency,management_skills,training,result'
        
        # Accept request
        filters = request.args.get('filter')

        # Request empty?
        if(filters != None):
            colsStr = filters

        # Making database connection 
        connection = mysql.connector.connect(
            host='localhost',
            user='root',
            password='',
            database='plecematepro'
        )

        # Create cursor object
        cursor = connection.cursor()

        # Execute select command to fetch data
        cursor.execute('SELECT '+colsStr+' FROM data')

        # Fetch all records
        result = cursor.fetchall()

        # Convert string into array
        colsStr =   colsStr.replace('_',' ')
        cols = colsStr.split(',')

        # Create empty dictionary for storing values
        data = {}

        # convert data in key and pair format
        i = 0
        for row in result:
            tmpdata = {}
                
            for j in range(0, len(row)):
                # Store records in key and pair format in dictionary
                tmpdata[cols[j]] = row[j]

            # Store Key pair values into list
            data[i] = tmpdata
            
            i+=1

        # Update response
        response.update({'data' : {'cols' : cols, 'record' : data}})

        # Close connection
        if connection.is_connected():
            connection.close()
        
    except Exception as error:
        print("Failed to fetch records from the database. Error:"+format(error))
    
        # Update response
        response.update({'error': 'Error while connecting to the database servers'})
        
    finally:
        return jsonify(response), 200


# Result page
@app.route('/validate', methods=['GET'])
def get_validate():
    # Error handling
    try:
        # Accept request
        nameField = request.args.get('name')
        classField = request.args.get('class')

        # Both fields received?
        if nameField == None or classField == None:
            response = {
                'response' : {
                    'error' : 'Input field cound error.',
                }
            }
            return jsonify(response), 200
        
        # Making database connection 
        connection = mysql.connector.connect(
            host='localhost',
            user='root',
            password='',
            database='plecematepro'
        )

        # Create cursor object
        cursor = connection.cursor()

        # Execute select command to fetch data
        cursor.execute('SELECT result FROM data where name="'+nameField+'" && class="'+classField+'"')

        # Fetch all records
        result = cursor.fetchall()
        
        # Iterate result
        data =  [{ 'result' : res[0] } for res in result]

        response = {
            'response' : {
                'count' : len(data),
                'data' : data
            }
        }
        return jsonify(response), 200

    except Exception as error:
         return "" 
    
if __name__ == '__main__':
    
    # Start development server
    app.run(host='127.0.0.1', port=8081)
