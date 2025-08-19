import requests
import json
from pythainlp.tokenize import word_tokenize

# ---------- ตั้งค่า ----------
TNER_API_KEY = '' # add Apikey
CYBERBULLY_API_KEY = '' # add Apikey

personal_pronoun_1 = {"หนู", "ข้า", "กู"}
personal_pronoun_2 = {"คุณ", "แก", "เธอ", "ตัวเอง", "เอ็ง", "มึง"}
all_personal_pronouns = personal_pronoun_1.union(personal_pronoun_2)

# ---------- ฟังก์ชันตรวจ ----------
def check_named_entities(text):
    url = "https://api.aiforthai.in.th/tner"
    headers = {"Apikey": TNER_API_KEY}
    data = {"text": text}
    try:
        response = requests.post(url, headers=headers, data=data)
        if response.status_code == 200:
            ner_result = response.json()
            bad_tags = {'ABB_DES', 'ABB_TTL', 'ABB_ORG', 'ABB_LOC', 'ABB'}
            bad_entities = [ent['word'] for ent in ner_result.get("entities", []) if ent['tag'] in bad_tags]
            if bad_entities:
                return True, bad_entities
    except:
        pass
    return False, []

def check_cyberbully(text):
    url = "https://api.aiforthai.in.th/cyberbully"
    headers = {"Apikey": CYBERBULLY_API_KEY}
    data = {"text": text}
    try:
        response = requests.post(url, headers=headers, data=data)
        if response.status_code == 200:
            result = response.json()
            if result.get("bully", "no") == "yes":
                bully_words = result.get("bully_words") or result.get("bully_phrases") or [text]
                return True, bully_words
    except:
        pass
    return False, []

def check_personal_pronouns(text):
    tokens = word_tokenize(text, engine="newmm")
    found_pronouns = [token for token in tokens if token in all_personal_pronouns]
    if found_pronouns:
        return True, found_pronouns
    return False, []

# ---------- ตรวจคำตอบนักเรียน 1 คน ----------
def score_single_student_answer(answer_text):
    mistakes = []

    ne_flag, ne_words = check_named_entities(answer_text)
    if ne_flag:
        mistakes.append({"type": "Named Entity", "words": ne_words})

    bully_flag, bully_words = check_cyberbully(answer_text)
    if bully_flag:
        mistakes.append({"type": "Cyberbully", "words": bully_words})

    pronoun_flag, pronouns = check_personal_pronouns(answer_text)
    if pronoun_flag:
        mistakes.append({"type": "Personal Pronoun", "words": pronouns})

    # กำหนดคะแนน
    mistake_count = len(mistakes)
    if mistake_count == 0:
        score = 2
    elif mistake_count == 1:
        score = 1
    else:
        score = 0

    output = {
        "student_answer": answer_text,
        "score": score,
        "mistakes": mistakes if mistakes else "ไม่มีข้อผิดพลาด"
    }

    # แสดงผล JSON
    print(json.dumps(output, ensure_ascii=False, indent=2))

# ---------- ตัวอย่างการเรียกใช้งาน ----------
student_answer = """เห็นด้วย เพราะ ถ้าเราใช้สื่อ ออนไลน์ไม่ถูกต้องหรือแสดงความคิดเห็นในทางที่ไม่ถูกต้อง
อาจทำให้ฝ่ายที่ได้รับความคิดเห็นนั้นไม่สบายใจหรือกังวลในปัญหาของตนเอง
ทำให้เกิดความไม่มั่นใจในตัวเองจนทำให้เกิดความเข้าใจผิดและสร้างความเสื่อมเสีย
ให้แก่ผู้อื่น ดังนั้นการใช้สื่อสารออนไลน์ด้วยเจตนาแอบแฝงจึงมีผลกระทบทางด้านอื่นๆ"""

score_single_student_answer(student_answer)
