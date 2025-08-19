import re
import requests
from pythainlp.tokenize import word_tokenize
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import json

# ---------- ตั้งค่า ----------
API_KEY = '' # add Apikey
TNER_URL = 'https://api.aiforthai.in.th/tner'

# ---------- โหลด Dataset ----------
import pandas as pd
examples_df = pd.read_csv('')  # dataset 'local_word'
pronouns_df = pd.read_csv('')  # dataset 'personal pronoun 1', 'personal pronoun 2'

example_phrases = examples_df['local_word'].dropna().tolist()
pronouns_1 = pronouns_df['personal pronoun 1'].dropna().tolist()
pronouns_2 = pronouns_df['personal pronoun 2'].dropna().tolist()
pronouns_1_2 = pronouns_1 + pronouns_2

# ---------- บทความอ้างอิง ----------
reference_text = """
สื่อสังคม (Social Media) หรือที่คนทั่วไปเรียกว่า สื่อออนไลน์ หรือ สื่อสังคม ออนไลน์ นั้น เป็นสื่อหรือช่องทางที่แพร่กระจายข้อมูลข่าวสารในรูปแบบต่างๆ ได้อย่างรวดเร็วไปยังผู้คนที่อยู่ทั่วทุกมุมโลก...
"""  # ตัดให้ง่ายขึ้น

# ---------- โหลดโมเดล WangchanBERTa ----------
model = SentenceTransformer("airesearch/wangchanberta-base-att-spm-uncased")

# ---------- ฟังก์ชันตรวจแต่ละเงื่อนไข ----------
def call_tner(text):
    headers = {'Apikey': API_KEY}
    data = {'text': text}
    try:
        resp = requests.post(TNER_URL, headers=headers, data=data, timeout=10)
        if resp.status_code == 200:
            return resp.json()
    except Exception as e:
        print(f"TNER API error: {e}")
    return None

def check_summary_similarity(student_answer, reference_text, threshold=0.8):
    embeddings = model.encode([student_answer, reference_text])
    sim = cosine_similarity([embeddings[0]], [embeddings[1]])[0][0]
    return sim >= threshold

def check_examples(student_answer, example_phrases):
    violated = [phrase for phrase in example_phrases if phrase in student_answer]
    return len(violated) == 0, violated

def check_pronouns(student_answer, pronouns_list):
    words = word_tokenize(student_answer, engine='newmm')
    violated = [p for p in pronouns_list if p in words]
    return len(violated) == 0, violated

def check_abbreviations(student_answer):
    pattern = r'\b(?:[ก-ฮA-Za-z]\.){2,}'
    violated = []
    if re.search(pattern, student_answer):
        violated.append(re.search(pattern, student_answer).group())
    tner_result = call_tner(student_answer)
    if tner_result:
        for item in tner_result.get('entities', []):
            if item['type'] in ['ABB_DES', 'ABB_TTL', 'ABB_ORG', 'ABB_LOC', 'ABB']:
                violated.append(item['text'])
    return len(violated) == 0, violated

def check_summary_similarity(student_answer, reference_text, threshold=0.8):
    embeddings = model.encode([student_answer, reference_text])
    sim = cosine_similarity([embeddings[0]], [embeddings[1]])[0][0]
    violated = [] if sim >= threshold else ["ข้อความไม่สรุปใจความตรงกับบทความอ้างอิง"]
    return sim >= threshold, violated

def check_title(student_answer, forbidden_title="การใช้สื่อสังคมออนไลน์"):
    violated = [forbidden_title] if forbidden_title in student_answer else []
    return len(violated) == 0, violated

def validate_student_answer(student_answer):
    results = {}
    score = 1

    funcs = [
        ("summary_similarity", check_summary_similarity),
        ("no_example", check_examples),
        ("no_pronouns", check_pronouns),
        ("no_abbreviations", check_abbreviations),
        ("no_title", check_title)
    ]

    for name, func in funcs:
        if name == "summary_similarity":
            valid, violated = func(student_answer, reference_text)
        elif name == "no_example":
            valid, violated = func(student_answer, example_phrases)
        elif name == "no_pronouns":
            valid, violated = func(student_answer, pronouns_1_2)
        else:
            valid, violated = func(student_answer)

        # แปลง valid เป็น Python bool ปกติ
        results[name] = {"valid": bool(valid), "violated_words": violated}
        if not valid:
            score = 0

    return {
        "score": score,
        "details": results
    }


# ---------- ประเมินคำตอบนักเรียนคนเดียว ----------
def evaluate_single_student(student_answer):
    result = validate_student_answer(student_answer)
    return json.dumps(result, ensure_ascii=False, indent=2)


# ---------- ตัวอย่างเรียกใช้ ----------
student_answer = """สื่อสังคมหรือสื่อออนไลน์ เป็นช่องทางในการติดต่อ แพร่กระจายข่าวสารข้อมูลต่าง ๆ ให้ผู้คนได้รับรู้ 
แต่ข้อเสียของสื่อออนนไลน์คือหากใช้โดยไม่ระมัดระวัง เช่นการแสดงความคิดเห็นทําให้ผู้อื่นเสียหาย 
การนําเสนอสิ่งที่มีเนื้อหาล่อแหลมชักจูงผู้คน หรือการกระทําผิดทางกฎหมาย ในปัจจุบันผู้คนส่วนใหญ่นิยมใช้สื่อออนไลน์
เป็นช่องทางในการค้าขาย เพราะเข้าถึงได้ง่ายและรวดเร็ว แต่ช่องการค้าขายก็มักจะมีมิจฉาชีพหลอกผู้คนอยู่เสมอ
แม้สังคมออนไลน์ หรือสื่อออนไลน์จะมีข้อดีมากแค่ไหน แต่ก็จะมีข้อเสียปะปน ดังนั้นควรใช้สื่อออนไลน์อย่างระมัดระวัง """

result_json = validate_student_answer(student_answer)
print(json.dumps(result_json, ensure_ascii=False, indent=2))
