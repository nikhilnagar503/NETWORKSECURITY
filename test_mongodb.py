import os
from dotenv import load_dotenv
from pymongo.mongo_client import MongoClient

# Load environment variables from a .env file
load_dotenv()

# Get the MongoDB connection URI from the environment variables
# The `os.getenv()` method is used to retrieve the value of an environment variable.
# We are getting the variable named 'MONGO_DB_URL' which you defined in your .env file.
uri = os.getenv("MONGO_DB_URL")

# Check if the URI was loaded successfully
if uri is None:
    print("Error: The MONGO_DB_URL environment variable was not found.")
else:
    # Create a new client and connect to the server
    client = MongoClient(uri)

    # Send a ping to confirm a successful connection
    try:
        client.admin.command('ping')
        print("Pinged your deployment. You successfully connected to MongoDB!")
    except Exception as e:
        print(e)