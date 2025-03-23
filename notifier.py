import re
from venv import logger
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
from dotenv import load_dotenv
import os

'''
param = [
        {course_title: "",
            todos: [
                {
                    todo_title: "",
                    todo_count: 0
                },
                {
                    todo_title: "",
                    todo_count: 1
                },
            ]
        }, 
    ]
'''

def send_dm(param):
    load_dotenv()
    SLACK_BOT_TOKEN = os.getenv("SLACK_BOT_TOKEN")

    client = WebClient(token=SLACK_BOT_TOKEN)

    # ID of the channel you want to send the message to
    channel_id = "D08JQR5NQ7Q"

    message = create_message(param)

    try:
        # Call the chat.postMessage method using the WebClient
        result = client.chat_postMessage(
            channel=channel_id,
            text=message
        )
        logger.info(result)

    except SlackApiError as e:
        logger.error(f"Error posting message: {e}")


def create_message(param):
    lines = []

    for assign in param:
        course = assign["course_title"]
        course = re.sub(r"\s*\(.*\)", "", course)
        todos = assign["todos"]
        
        # 각 과목의 할 일들을 "타입 개수" 형식으로 묶음
        todo_texts = [f'{todo["todo_title"]} {todo["todo_count"]}' for todo in todos]
        line = f'📚{course} - {", ".join(todo_texts)}'
        lines.append(line)
    
    # 최종 메시지 구성
    message = "\n".join(lines)
    return message