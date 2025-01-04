import boto3
import botocore.config
import json
from datetime import datetime
import logging
import uuid
import os

# Set up logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)
# NEW: Configure clients with timeouts
bedrock_config = botocore.config.Config(
    connect_timeout=120,    # Increased to 120 seconds
    read_timeout=300,      # Increased to 300 seconds (5 minutes)
    retries={
        'max_attempts': 3,  # Increased retry attempts
        'mode': 'adaptive'  # Added adaptive retry mode
    }
)
s3_config = botocore.config.Config(
    connect_timeout=60,
    read_timeout=60,
    retries={
        'max_attempts': 3,
        'mode': 'adaptive'
    }
)
bedrock_client = boto3.client("bedrock-runtime",region_name = "us-east-1",
                              config=bedrock_config )

s3_client = boto3.client('s3', 
                        region_name="us-east-1",
                        config=s3_config)

import boto3
import botocore.config
import json
from datetime import datetime
import logging
import uuid

# Set up logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)
# NEW: Configure clients with timeouts
bedrock_config = botocore.config.Config(
    connect_timeout=20,    # NEW: Explicit timeout settings
    read_timeout=20,
    retries={'max_attempts': 2}
)

s3_config = botocore.config.Config(
    connect_timeout=20,
    read_timeout=20,
    retries={'max_attempts': 2}
)

# NEW: Initialize clients outside the handler for better performance
bedrock_client = boto3.client("bedrock-runtime", 
                            region_name="us-east-1",
                            config=bedrock_config)
s3_client = boto3.client('s3', 
                        region_name="us-east-1",
                        config=s3_config)

                        
def story_generator(storytopic: str) -> str:
    try:
        # Define the request body
        body = {
            "prompt": f"Write a story with {storytopic}",
            "maxTokens": 8000,
            "temperature": 0.8,
            "topP": 0.9,
            "stopSequences":["\n\n"]
            }

        logger.info(f"Attempting to generate story with topic: {storytopic}")
        logger.info(f"Request body: {json.dumps(body)}")

        # Create a Bedrock Runtime client
        client = boto3.client("bedrock-runtime", region_name="us-east-1")

        # Invoke the Jurassic-2 Mid model
        response = bedrock_client.invoke_model(
            modelId="ai21.j2-ultra-v1",  # Correct model ID for Jurassic-2 Mid
            body=json.dumps(body),
            contentType="application/json",
            accept="application/json"
        )
        
        response_body = json.loads(response["body"].read())
        logger.info(f"Raw response: {response_body}")

        # Extract the generated story
        story_details = response_body["completions"][0]["data"]["text"]
        if story_details:
            logger.info(f"Story generation completed. Length: {len(story_details)}")
            # Parse the response
            logger.info(f"Successfully generated story: {story_details[:100]}...")
            return story_details
        else:
            logger.error("No story was generated in the response.")
            return ""

    except botocore.exceptions.ClientError as e:
        # IMPROVED: More specific error handling
        logger.error(f"Bedrock API error: {str(e)}")
        raise
    except json.JSONDecodeError as e:
        logger.error(f"JSON parsing error: {str(e)}")
        raise
    except Exception as e:
        logger.error(f"Unexpected error in story generation: {str(e)}")
        raise





def save_to_s3(text_content: str, s3_bucket: str) -> dict:
    """
    Save text content to S3 bucket as a .txt file
    """
    try:
        # Create S3 client with specific configuration
        
        # Generate filename
        timestamp = datetime.utcnow().strftime('%Y%m%d_%H%M%S')
        file_id = str(uuid.uuid4())[:8]
        s3_key = f"stories/{timestamp}_{file_id}.txt"

        logger.info(f"Attempting to save file to S3: {s3_key}")
        logger.info(f"Bucket: {s3_bucket}")
        logger.info(f"Content length: {len(text_content)}")

        # Encode content
        text_content_bytes = text_content.encode('utf-8')

        # CHANGED: Using pre-initialized client
        response = s3_client.put_object(
            Bucket=s3_bucket,
            Key=s3_key,
            Body=text_content_bytes,
            ContentType='text/plain',
            Metadata={
                'timestamp': timestamp,
                'generator': 'lambda-bedrock'
            }
        )

        logger.info(f"S3 upload response: {response}")

        # Verify upload success
        if response['ResponseMetadata']['HTTPStatusCode'] == 200:
            return {
                "success": True,
                "message": "File saved successfully",
                "file_location": f"s3://{s3_bucket}/{s3_key}",
                "s3_key": s3_key
            }
        else:
            raise Exception(f"S3 upload failed with response: {response}")

    except botocore.exceptions.ClientError as e:
        error_code = e.response['Error']['Code']
        error_message = e.response['Error']['Message']
        logger.error(f"AWS S3 error: {error_code} - {error_message}")
        logger.error(f"Full error: {str(e)}")
        return {
            "success": False,
            "error": f"S3 error: {error_code} - {error_message}"
        }
    except Exception as e:
        logger.error(f"Unexpected error saving to S3: {str(e)}")
        return {
            "success": False,
            "error": f"Unexpected error: {str(e)}"
        }

def lambda_handler(event, context):
    logger.info(f"Received event: {event}")

    try:
        # Handle both string and dict body
        if isinstance(event['body'], str):
            try:
                body = json.loads(event['body'])
            except json.JSONDecodeError as e:
                logger.error(f"Failed to parse request body: {str(e)}")
                return {
                    'statusCode': 400,
                    'headers': {
                        'Content-Type': 'application/json',
                           'Access-Control-Allow-Origin': '*'
                    },
                    'body': json.dumps({
                        'error': 'Invalid JSON in request body',
                        'details': str(e)
                    })
                }
        else:
            body = event['body']

        # Validate story_topic
        storytopic = body.get('story_topic')
        if not storytopic:
            logger.error("Missing story_topic in request")
            return {
                'statusCode': 400,
                'headers': {
                    'Content-Type': 'application/json',
                       'Access-Control-Allow-Origin': '*'
                },
                'body': json.dumps({
                    'error': 'Missing story_topic in request'
                })
            }

        # Generate story
        generate_story = story_generator(storytopic=storytopic)
        if not generate_story:
            return {
                'statusCode': 500,
                'headers': {'Content-Type': 'application/json',   'Access-Control-Allow-Origin': '*'},
                'body': json.dumps({'error': 'Story generation failed'})
            }
        if generate_story:
            
            s3_bucket = os.environ.get('BUCKET_NAME')
            # Save to S3
            
            s3_response = save_to_s3(generate_story, s3_bucket)
            if not s3_response['success']:
                logger.error(f"Failed to save to S3: {s3_response.get('error')}")
                return {
                    'statusCode': 500,
                    'headers': {
                        'Content-Type': 'application/json',
                           'Access-Control-Allow-Origin': '*'
                    },
                    'body': json.dumps({
                        'error': f"Failed to save story to S3: {s3_response.get('error')}",
                        'story': generate_story
                    })
                }
                
            # Success response
            return {
                'statusCode': 200,
                'headers': {
                    'Content-Type': 'application/json',
                       'Access-Control-Allow-Origin': '*'
                },
                'body': json.dumps({
                    'message': 'Story generated and saved successfully',
                    'story': generate_story,
                    's3_location': s3_response['file_location']
                })
            }
    
    except Exception as e:
        logger.error(f"Error in lambda_handler: {str(e)}")
        return {
            'statusCode': 500,
            'headers': {
                'Content-Type': 'application/json',
                   'Access-Control-Allow-Origin': '*'},
            'body': json.dumps({
                'error': 'Internal server error',
                'details': str(e)
            })
        }
