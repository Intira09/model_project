import re
import requests
import json
import openai
import time

# ---------------- Typhoon API ----------------
client = openai.OpenAI(
    api_key="", # add Apikey
    base_url="https://api.opentyphoon.ai/v1"
)

# ---------------- AI for Thai API ----------------
aiforthai_url = "https://api.aiforthai.in.th/qaiapp"
aiforthai_headers = {
    'Content-Type': "application/json",
    'apikey': "", # add Apikey
}

# ---------------- ฟังก์ชัน Typhoon ----------------
def ask_typhoon(question, document):
    response = client.chat.completions.create(
        model="typhoon-v2-70b-instruct",
        messages=[
            {"role": "system", "content": "You are a helpful assistant that extracts parts of Thai sentences."},
            {"role": "user", "content": f"{question} จากประโยค:\n{document}"}
        ],
        temperature=0,
        max_tokens=1000
    )
    return response.choices[0].message.content.strip()

# ---------------- ฟังก์ชัน AI for Thai ----------------
def ask_aiforthai_until_answer(question, document, wait_sec=2):
    question_clean = " ".join(question.split())
    attempt = 0
    while True:
        attempt += 1
        payload = json.dumps({"question": question_clean, "document": document})
        try:
            response = requests.post(aiforthai_url, data=payload, headers=aiforthai_headers, timeout=10)
        except requests.exceptions.RequestException as e:
            print(f"⚠️ API Error: {e} (retry {attempt})")
            time.sleep(wait_sec)
            continue

        if response.status_code == 200:
            result = response.json()
            answer = result.get("answer", "").strip()
            if answer and ("ไม่พบ" not in answer) and ("ไม่สามารถตรวจได้" not in answer):
                return answer
        time.sleep(wait_sec)

# ---------------- คำถาม ----------------
q1 = "หาประธาน กริยา กรรมในประโยคทั้งหมด ของแต่ละประโยค ตอบเป็นคำ"
q2 = "ประโยคที่ไม่สื่อความหมายหรือไม่เข้าใจที่จะสื่อ"

# ---------------- ฟังก์ชันประเมินนักเรียน 1 คน ----------------
def evaluate_single_student(student_answer):
    # ทำความสะอาดข้อความ
    student_answer = re.sub(r'[\s\n\-]+', ' ', str(student_answer)).strip()

    # เรียก API
    ans1 = ask_typhoon(q1, student_answer)
    ans2 = ask_aiforthai_until_answer(q2, student_answer)

    # คำนวณคะแนน
    score = 2.0
    missing_count = len(re.findall(r"\(ไม่ระบุ\)", ans1))
    score -= 0.5 * missing_count

    wrong_q2 = 0
    if ans2.strip() and not ans2.strip().startswith("ไม่มี"):
        wrong_q2 = 1
        score -= 0.5

    score = max(score, 0)

    # สร้าง JSON ผลลัพธ์
    result = {
        "score": score,
        "Q1_answer": ans1,
        "Q2_answer": ans2,
        "missing_in_Q1": missing_count,
        "wrong_Q2": wrong_q2
    }
    return json.dumps(result, ensure_ascii=False, indent=2)

# ---------------- ตัวอย่างเรียกใช้ ----------------
student_answer = """เห็นด้วยเพราะ เดี๋ยวผู้คนที่สื่อออนไลน์ ไม่จำเป็นต้องเป็นผู้ใหญ่เท่านั้นอย่างเดียว
แล้ว เด็กๆ ก็ใช้สื่อออนไลน์ได้ เพราะทุกคนมีโทรศัพท์มือถือ เฉพาะนั้นเราควร
ที่จะป้องกันความเสี่ยงที่เด็ก หรือ ผู้ใหญ่ จะถูกหลอกนำข้อมูลหรือถูกหลอกให้
โอนเงินให้กับแก็งค์คลอเซ็นเตอร์ อินเตอร์เน็ตหรือสื่อออนไลน์มีทั้งข้อดีและ
ข้อเสีย เราควรใช้อย่างถูกวิธีและเป็นประโยชน์"""

result_json = evaluate_single_student(student_answer)
print(result_json)
