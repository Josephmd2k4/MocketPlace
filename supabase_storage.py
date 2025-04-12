import supabase
from django.conf import settings
import logging
logger = logging.getLogger(__name__)

# Initialize Supabase client
supabase_client = supabase.create_client(settings.SUPABASE_URL, settings.SUPABASE_API_KEY)

# Define the bucket name (ensure the bucket is already created)
bucket_name = "media"  # Or the name of your bucket

def upload_file(file, file_path):
    logger.info("Upload function called")

    try:
        file.seek(0)
        file_content = file.read()
        logger.info("File read successfully")

        response = supabase_client.storage.from_(bucket_name).upload(file_path, file_content)
        
        logger.info(f"Upload response: {response}")
        
        return response

    except Exception as e:
        logger.error(f"An exception occurred: {e}")
        raise


# Function to get the URL of a file
def get_file_url(file_path):
    # Get public URL of the file
    url = supabase_client.storage.from_(bucket_name).get_public_url(file_path)
    return url
