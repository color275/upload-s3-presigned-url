import requests

presigned_url = 'https://color275-download.s3.amazonaws.com/test.txt?X-Amz-Algorithm=AWS4-HMAC-SHA256&X-Amz-Credential=AKIAXC6QHEI5NVOG42EB%2F20230925%2Fap-northeast-2%2Fs3%2Faws4_request&X-Amz-Date=20230925T141948Z&X-Amz-Expires=3600&X-Amz-SignedHeaders=host&X-Amz-Signature=8dc09b9f438a24c1906fd19b63df48d5cffed6491da3cb81b6f92f4911201c6b'
file_path = 'test.txt'  # 업로드할 로컬 파일 경로

with open(file_path, 'rb') as file:
    response = requests.put(presigned_url, data=file)
print(response)

if response.status_code == 200:
    print("업로드 성공")
else:
    print("업로드 실패")
