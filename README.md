## **AWS Lambda Story Generator with Jurassic-2 Ultra and S3 Integration**

This project demonstrates how to set up an AWS Lambda function to generate imaginative stories using the **Jurassic-2 Ultra model** from **AWS Bedrock** and save the generated stories to an S3 bucket. The function is optimized for handling large outputs and includes timeout and error handling.

---

## **Prerequisites**

Before setting up the environment, ensure you have the following:

1. **AWS Account**: An active AWS account with access to the following services:

   * AWS Lambda  
   * Amazon S3  
   * AWS Bedrock  
   * AWS Identity and Access Management (IAM)  
2. **AWS CLI**: Installed and configured with credentials that have the necessary permissions.

   * [Install AWS CLI](https://docs.aws.amazon.com/cli/latest/userguide/install-cliv2.html)  
3. **Python**: Python 3.9 or later installed locally for testing and packaging the Lambda function.

4. **IAM Permissions**:

   * Ensure the Lambda execution role has the following permissions:  
     * `bedrock:InvokeModel` for invoking the Jurassic-2 Ultra model.  
     * `s3:PutObject` for saving files to the S3 bucket.  
     * `logs:CreateLogGroup`, `logs:CreateLogStream`, and `logs:PutLogEvents` for CloudWatch logging.

---

## **Setup Instructions**

### **1\. Create an S3 Bucket**

1. Go to the **S3 Console** in AWS.  
2. Create a new bucket (e.g., `awsbedrockstorygen`) to store the generated stories.  
3. Ensure the bucket has the necessary permissions for the Lambda function to write files:  
   * Add a bucket policy if needed (see below).

#### **Example Bucket Policy:**
'''markdown
'''json
{  
  "Version": "2012-10-17",  
  "Statement": \[  
    {  
      "Effect": "Allow",  
      "Principal": {  
        "Service": "lambda.amazonaws.com"  
      },  
      "Action": "s3:PutObject",  
      "Resource": "arn:aws:s3:::awsbedrockstorygen/\*"  
    }  
  \]  
}
'''
### **2\. Create an IAM Role for Lambda**

1. Go to the **IAM Console** and create a new role.  
2. Select **AWS Lambda** as the trusted entity.  
3. Attach the following policies:  
   * **Custom Policy** for Bedrock and S3 access:
     
'''markdown
'''json
{  
  "Version": "2012-10-17",  
  "Statement": \[  
    {  
      "Effect": "Allow",  
      "Action": \[  
        "bedrock:InvokeModel"  
      \],  
      "Resource": "\*"  
    },  
    {  
      "Effect": "Allow",  
      "Action": \[  
        "s3:PutObject"  
      \],  
      "Resource": "arn:aws:s3:::awsbedrockstorygen/\*"  
    },  
    {  
      "Effect": "Allow",  
      "Action": \[  
        "logs:CreateLogGroup",  
        "logs:CreateLogStream",  
        "logs:PutLogEvents"  
      \],  
      "Resource": "\*"  
    }  
  \]  
}

1. Save the role and note the **Role ARN**.

---

### **3\. Create the Lambda Function**

1. Go to the **Lambda Console** and create a new function.  
2. Choose **Author from scratch** and provide the following details:  
   * **Function name**: `StoryGenerator`  
   * **Runtime**: Python 3.9  
   * **Execution role**: Select the IAM role created earlier.  
3. **Set Timeout and Memory**:  
   * Go to the **Configuration** tab → **General Configuration** → **Edit**.  
   * Set the **Timeout** to **300 seconds** (5 minutes).  
   * Increase the **Memory** to **256 MB** or higher.  
4. **Upload the Code**:  
   * Package the Python code into a `.zip` file (including dependencies if any).  
   * Upload the `.zip` file in the **Code** tab of the Lambda function.

---

### **4\. Configure Environment Variables**

Add the following environment variables to the Lambda function:

* **S3\_BUCKET**: The name of your S3 bucket (e.g., `awsbedrockstorygen`).

---

### **5\. Test the Lambda Function**

1. Go to the **Test** tab in the Lambda Console.  
2. Create a test event with the following JSON:

{  
  "body": {  
    "story\_topic": "a young explorer who discovers a hidden world beneath the ocean"  
  }  
}

## **Code Overview**

This project demonstrates the use of AWS Lambda to generate stories using the **Jurassic-2 Ultra model** via AWS Bedrock and store the results in an **S3 bucket**. The function is designed with modular components, robust error handling, and a configurable setup for various use cases. 

### **Lambda Function Code**

The Lambda function consists of three main components:

1. **Story Generator**:  
   * Uses the Jurassic-2 Ultra model (`ai21.j2-ultra-v1`) via AWS Bedrock to generate a story based on the input topic.  
   * Handles timeout awareness using `context.get_remaining_time_in_millis()`.  
2. **Save to S3**:  
   * Saves the generated story as a `.txt` file in the specified S3 bucket.  
   * Includes error handling for S3 upload failures.  
3. **Lambda Handler**:  
   * Parses the input event, invokes the story generator, and saves the result to S3.

---

### **Key Configuration Parameters**

* **Jurassic-2 Ultra Model ID**: `ai21.j2-ultra-v1`  
* **Timeout**: 300 seconds (adjustable in Lambda settings).  
* **S3 Bucket**: Ensure the bucket name matches the environment variable.

---

## **Troubleshooting**

### **Common Issues**

1. **Timeout Errors**:  
   * Increase the Lambda timeout to handle longer story generation.  
   * Reduce the `maxTokens` parameter in the Jurassic-2 Ultra model request.  
2. **Access Denied Errors**:  
   * Ensure the Lambda execution role has the necessary permissions for Bedrock and S3.  
3. **Invalid Model ID**:  
   * Verify the model ID is correct: `ai21.j2-ultra-v1`.  
4. **S3 Upload Failures**:  
   * Check the bucket policy and ensure the Lambda role has `s3:PutObject` permissions.

---

## **Future Enhancements**

* Add support for other Bedrock models (e.g., Claude).  
* Implement AWS Step Functions for longer workflows.  
* Add API Gateway integration for external access.

---

## **References**

* [AWS Bedrock Documentation](https://docs.aws.amazon.com/bedrock/latest/userguide/what-is-bedrock.html)  
* [AWS Lambda Documentation](https://docs.aws.amazon.com/lambda/latest/dg/welcome.html)  
* [Boto3 Documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/index.html)

