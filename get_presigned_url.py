import boto3
import json
import os
import requests

session = boto3.Session(profile_name='color275+chiho.s3-user')
s3_client = session.client('s3', region_name='ap-northeast-2')

# s3_client = boto3.client('s3', region_name='ap-northeast-2')

bucket_name = 'color275-download'
object_key = 'test3.txt'

response = s3_client.list_objects(Bucket=bucket_name)
objects = response.get('Contents', [])

if objects:
    print(f"버킷 '{bucket_name}' 내의 객체 목록:")
    for obj in objects:
        print(f" - {obj['Key']}")
else:
    print(f"버킷 '{bucket_name}' 내에 객체가 없습니다.")

# Pre-signed URL 생성
presigned_url = s3_client.generate_presigned_url(
    'put_object',
    Params={'Bucket': bucket_name, 'Key': object_key},
    
    ExpiresIn=3600
)

print(presigned_url)


file_path = 'test3.txt'  # 업로드할 로컬 파일 경로

with open(file_path, 'rb') as file:
    response = requests.put(presigned_url, data=file)
print(response)

if response.status_code == 200:
    print("업로드 성공")
else:
    print("업로드 실패")
