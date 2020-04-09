from flask import Flask
from werkzeug.exceptions import NotFound
from flask import make_response
import json

from boto3 import resource
from boto3.dynamodb.conditions import Key
import datetime

app = Flask(__name__)

# code here to open the DynamoDB table. If the table is not there, create it

def create_table(table_name):
    ''' create a table and return the table object'''
    dynamodb_resource = resource('dynamodb')
    # create the greetings table with attributes (gid, date, content, timestamp), where timestamp is the time the record saved to DynamoDb, 
    # different from the greeting date
    # return the table object

    # Only the key attributes are specified at table creation
    attributes = [{'AttributeName': 'gid', 'AttributeType': 'S'}]
    keys = [{'AttributeName': 'gid', 'KeyType': 'HASH'}]

    provisioned_throughput = {'ReadCapacityUnits': 150, 'WriteCapacityUnits': 150}
    
    table = dynamodb_resource.create_table(AttributeDefinitions=attributes, TableName=table_name, KeySchema=keys, ProvisionedThroughput=provisioned_throughput)

    table.wait_until_exists()

    return table

def get_table(table_name):
    dynamodb_resource = resource('dynamodb')
    # return the table object, when the table is already created, 
    # otherwise create and return the table object
    for table in dynamodb_resource.tables.all():
        if table.table_name == table_name:
            print("Table found")
            return table

    return create_table(table_name)

greetings_table = get_table('greetings')

def root_dir():
    """ Returns root director for this project """
    return os.path.dirname(os.path.realpath(__file__ + '/..'))

def nice_json(arg):
    response = make_response(json.dumps(arg, sort_keys = True, indent=4))
    response.headers['Content-type'] = "application/json"
    return response


@app.route("/", methods=['GET'])
def hello():
    return nice_json({
        "uri": "/",
        "subresource_uris": {
            "greetings": "/greetings",
            "add_greeting": "/addgreeting/<id>/<date>/<content>",
        }
    })

@app.route("/greetings", methods=['GET'])
def greetings():
    # return all greetings records in json format
    # to do
    return nice_json(greetings_table.scan()['Items'])

@app.route("/addgreeting/<gid>/<date>/<content>", methods=['POST', 'PUT'])
def add_greeting(gid, date, content):
    # use the methods in dynamo.py and add a greeting to DynamoDB
    col_dict = {'gid': gid, 'date': date, 'content': content, 'timestamp': datetime.datetime.now().strftime("%m/%d/%y, %H:%M:%S")}
    response = greetings_table.put_item(Item=col_dict)

    return response

if __name__ == "__main__":
    app.run(port=5001, debug=True)
