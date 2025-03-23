from crawler import check_assignments
from notifier import send_dm

if __name__ == "__main__":
    result = check_assignments()
    if result:
        send_dm(result)
        print("과제 존재")
