import boto3
import json

s3_client = boto3.client('s3', region_name='ap-northeast-2')

def generate_presigned_url(bucket_name, object_key, get_put, expiration=3600):
    try:
        presigned_url = s3_client.generate_presigned_url(
            get_put,
            Params={
                'Bucket': bucket_name,
                'Key': object_key,
            },
            ExpiresIn=expiration  # URL의 만료 시간(초)을 조정할 수 있습니다.
        )
        return presigned_url
    except Exception as e:
        print(f"Error: {str(e)}")
        return None

def lambda_handler(event, context):
    try:
        # API Gateway로부터 전달된 요청 파라미터를 가져옵니다.
        body = json.loads(event['body'])
        bucket_name = body['bucket_name']
        get_put = body['get_put']
        object_key = body['object_key']

        # Pre-signed URL 생성
        presigned_url = generate_presigned_url(bucket_name, object_key, get_put)

        if presigned_url:
            # Pre-signed URL을 반환
            print(presigned_url)
            response_body = {'presigned_url': presigned_url}
            return {
                'statusCode': 200,
                'body': json.dumps(response_body)
            }
        else:
            return {
                'statusCode': 500,
                'body': json.dumps({'error_message': 'Failed to generate presigned URL'})
            }
    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps({'error_message': str(e)})
        }
