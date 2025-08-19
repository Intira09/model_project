import requests
import json
import time

# ---------------------- ตั้งค่า ----------------------
url = "https://api.aiforthai.in.th/qaiapp"
headers = {
    'Content-Type': "application/json",
    'apikey': "", # add Apikey
}

# คำตอบของนักเรียน
student_answer = """สื่อสังคม (Social Media) เป็นสื่อหรือช่องทางการเผยแพร่ข้อมูลข่าวสารในรูปแบบต่างๆได้อย่างรวดเร็ว
ไปยังคนทั่วโลกที่สัญญาณ โทรศัพท์เข้าถึงเราสามารถใช้สื่อออนไลน์เพื่อค้นหาและรับข้อมูลข่าวสารที่เป็นประโยชน์ได้ผู้คนมาก
มายใช้สื่อออนไลน์เพื่อทำธุรกิจต่างๆมากมายอย่างไรก็ตามหากใช้อย่างไม่ระมัดระวังไม่ว่าจะเป็นการโพสลงสื่อ
ทำให้ผู้อื่นเสียหายหรือโปรโมทการพนันหรือสิ่งผิดกฎหมายกลุ่มคนทุกเพศทุกวัย สามารถใช้สื่อสังคมออน
ไลน์ได้และตกเป็นเหยื่อของมิจฉาชีพพวกหนี้ทำให้คนบางกลุ่มรู้หรอกควรมีการเตือนภัยใช้คนกลุ่มได้รับรู้"""

# คำถาม + เงื่อนไขการตรวจ
questions = [
    {"question": "เป็นไปตามเหตุและผล ตอบ ใช่ หรือ ไม่ใช่",
     "check": lambda ans: ans.strip() == "ใช่"},
    {"question": "มีการเรียงลำดับความคิด",
     "check": lambda ans: not ans.strip().startswith("ไม่มี")},
    {"question": "มีเนื้อความซ้ำ",
     "check": lambda ans: "ไม่มี" in ans.strip()},
    {"question": "มีเนื้อความไม่สัมพันธ์กัน",
     "check": lambda ans: "ไม่มี" in ans.strip()},
    {"question": "มีเนื้อความขาด",
     "check": lambda ans: "ไม่มี" in ans.strip()},
]

results = []
wrong_count = 0

# ---------------------- รันทีละคำถาม ----------------------
for q in questions:
    while True:
        payload = json.dumps({
            "question": q["question"],
            "document": student_answer
        })

        try:
            response = requests.post(url, data=payload, headers=headers, timeout=10)
        except requests.exceptions.RequestException as e:
            time.sleep(1)
            continue

        if response.status_code == 200:
            result = response.json()
            answer = result.get("answer", "").strip()

            if answer and answer.lower() not in ["", "ไม่พบคำตอบ"]:
                is_correct = q["check"](answer)
                results.append({
                    "question": q["question"],
                    "answer": answer,
                    "correct": is_correct
                })
                if not is_correct:
                    wrong_count += 1
                break
            else:
                time.sleep(0.5)
        else:
            time.sleep(0.5)

# ---------------------- คำนวณคะแนน ----------------------
if wrong_count == 0:
    score = 2
elif wrong_count == 1:
    score = 1
else:
    score = 0

# ---------------------- แสดงผลเป็น JSON ----------------------
output = {
    "results": results,
    "score": score
}

print(json.dumps(output, ensure_ascii=False, indent=2))
