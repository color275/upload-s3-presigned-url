import streamlit as st
import requests
import json
from streamlit.logger import get_logger

if 'clicked' not in st.session_state:
    st.session_state.clicked = False

def set_clicked():
    st.session_state.clicked = True

logger = get_logger(__name__)

# Presigned URL을 얻는 API Gateway 엔드포인트 URL
api_gateway_url = "https://obmtiz0wxg.execute-api.ap-northeast-2.amazonaws.com/v1/upload"

def main():
    st.title("Presigned URL을 사용한 파일 업로드 및 다운로드 예제")

    # 파일 업로드 섹션
    st.header("파일 업로드")
    uploaded_file = st.file_uploader("파일을 업로드하세요.", type=["csv", "txt", "xlsx","pdf"])

    if uploaded_file is not None:
        # 업로드된 파일의 Presigned URL 얻기
        body_data = {"bucket_name": "chiholee-download", "object_key": uploaded_file.name, "get_put": "put_object"}
        presigned_url = get_presigned_url(api_gateway_url, body_data)

        if presigned_url:
            st.success("Presigned URL을 성공적으로 얻었습니다!")

            # 파일 업로드 버튼
            st.write("아래 버튼을 클릭하여 파일을 업로드하세요.")
            if st.button("파일 업로드"):
                upload_file(presigned_url, uploaded_file)

        else:
            st.error("Presigned URL을 얻는 데 실패했습니다!")

    st.header("파일 다운로드")
    
    # 다운로드 버튼
    download_file_name = st.text_input("다운로드할 파일 이름을 입력하세요.", "파일명")
    st.button("다운로드 시작", on_click=set_clicked)
    
    logger.info("######### 1")

    # https://blog.streamlit.io/10-most-common-explanations-on-the-streamlit-forum/#1-buttons-aren%E2%80%99t-stateful
    # https://stackoverflow.com/questions/76008605/creating-a-selectbox-file-uploader-with-a-button-in-streamlit-app
    if st.session_state.clicked:
        body_data = {"bucket_name": "chiholee-download", "object_key": download_file_name, "get_put": "get_object"}
        presigned_url = get_presigned_url(api_gateway_url, body_data)
        
        response = requests.get(presigned_url)
        st.write(response.status_code)
        
        if response.status_code == 200:
            btn = st.download_button(
                    label="저장할 위치",
                    data=response.content,                      
                    file_name=download_file_name,
                    # mime="image/png"
                )
        
def download_file(presigned_url, download_file_name):
    try:
        response = requests.get(presigned_url)
        
        # st.session_state['content'] = response.content
        return response.content
    except Exception as e:
        st.error(f"파일 다운로드 중 오류 발생: {str(e)}")

    


def get_presigned_url(api_url, body_data):
    try:
        headers = {"Content-Type": "application/json"}
        response = requests.get(api_url, data=json.dumps(body_data), headers=headers)
        if response.status_code == 200:
            data = response.json()
            return data.get("presigned_url")
        else:
            return None
    except Exception as e:
        return None

def upload_file(presigned_url, uploaded_file):
    try:
        with requests.put(presigned_url, data=uploaded_file.read()) as response:
            
            if response.status_code == 200:
                st.success("파일 업로드 완료!")
            else:
                st.error("파일 업로드 실패!")
    except Exception as e:
        st.error(f"파일 업로드 중 오류 발생: {str(e)}")



if __name__ == "__main__":
    main()
