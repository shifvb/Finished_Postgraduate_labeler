import os


def load_patient_remark(path: str) -> str:
    if os.path.exists(path) and os.path.isfile(path):
        with open(path, 'r', encoding='utf-8') as f:
            return f.read()
    else:
        return str()


def save_patient_remark(path: str, text: str):
    with open(path, 'w', encoding='utf-8') as f:
        f.write(text)
