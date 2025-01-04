## **Code Overview**

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

