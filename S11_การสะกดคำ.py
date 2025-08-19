import pandas as pd
import requests
import re
from pythainlp.tokenize import word_tokenize
from pythainlp.corpus import thai_words
from pythainlp.tag import pos_tag
from pythainlp.util import normalize
import json
import difflib

# โหลด whitelist (แก้ path ตามจริง หรือใช้ set() ถ้าไม่มีไฟล์)
try:
    with open('thai_loanwords.json', 'r', encoding='utf-8') as f:
        loanwords_whitelist = set(json.load(f))
except:
    loanwords_whitelist = set()

API_KEY = '' # add Apikey
API_URL = 'https://api.longdo.com/spell-checker/proof'

custom_words = {"ประเทศไทย", "สถาบันการศึกษา", "นานาประการ"}
splitable_phrases = {
    'แม้ว่า', 'ถ้าแม้ว่า', 'แต่ถ้า', 'แต่ทว่า', 'เนื่องจาก', 'ดังนั้น', 'เพราะฉะนั้น','ตกเป็น',
    'ดีแต่', 'หรือไม่', 'ข้อมูลข่าวสาร', 'ทั่วโลก', 'ยังมี', 'ทำให้เกิด', 'เป็นโทษ', 'ไม่มี', 'ข้อควรระวัง', 'การแสดงความคิดเห็น', 'ผิดกฎหมาย', 'แสดงความคิดเห็น'
}
strict_not_split_words = {
    'มากมาย', 'ประเทศไทย', 'ออนไลน์', 'ความคิดเห็น', 'ความน่าเชื่อถือ'
}

thai_dict = set(w for w in set(thai_words()).union(custom_words) if (' ' not in w) and w.strip())

# allowed punctuation (เพิ่ม ' และ ")
allowed_punctuations = {'.', ',', '-', '(', ')', '!', '?', '%', '“', '”', '‘', '’', '"', "'", '…', 'ฯ'}

# Allow / Forbid list ไม้ยมก (เพิ่มคำที่ใช้บ่อย)
allow_list = {'ปี', 'อื่น', 'เล็ก', 'ใหญ่', 'มาก', 'หลาย', 'ช้า', 'เร็ว', 'ชัด', 'ดี', 'ผิด'}
forbid_list = {'นา', 'บางคน', 'บางอย่าง', 'บางสิ่ง', 'บางกรณี'}

explanations = [
    "1. ตรวจสอบการตัดคำผิดขณะขึ้นบรรทัดใหม่ (ถ้ามี)",
    "2. ตรวจสอบคำสะกดผิดด้วย PyThaiNLP (และขอ Longdo ช่วยกรณีสงสัย)",
    "3. ตรวจสอบการใช้เครื่องหมายวรรคตอนที่ไม่อนุญาต",
    "4. ตรวจสอบการใช้ไม้ยมก (ๆ) ถูกต้องตามบริบทหรือไม่",
    "5. ตรวจสอบการแยกคำผิด เช่น คำที่ควรติดกัน"
]

#------------------------------------------------------------------------#
def check_linebreak_issue(prev_line_tokens, next_line_tokens, max_words=3):
    last_word = prev_line_tokens[-1]
    first_word = next_line_tokens[0]
    if last_word.endswith('-') or first_word.startswith('-'):
        return False, None, None, None
    for prev_n in range(1, min(max_words, len(prev_line_tokens)) + 1):
        prev_part = ''.join(prev_line_tokens[-prev_n:])
        for next_n in range(1, min(max_words, len(next_line_tokens)) + 1):
            next_part = ''.join(next_line_tokens[:next_n])
            combined = normalize(prev_part + next_part)
            if (
                (' ' not in combined)
                and (combined not in splitable_phrases)
                and (
                    (combined in strict_not_split_words) or (
                        (combined in thai_dict)
                        and (len(word_tokenize(combined, engine='newmm')) == 1)
                    )
                )
            ):
                return True, prev_part, next_part, combined
    return False, None, None, None

def analyze_linebreak_issues(text):
    lines = text.strip().splitlines()
    issues = []
    for i in range(len(lines) - 1):
        prev_line = lines[i].strip()
        next_line = lines[i + 1].strip()
        prev_tokens = word_tokenize(prev_line)
        next_tokens = word_tokenize(next_line)
        if not prev_tokens or not next_tokens:
            continue
        issue, prev_part, next_part, combined = check_linebreak_issue(prev_tokens, next_tokens)
        if issue:
            issues.append({
                'line_before': prev_line,
                'line_after': next_line,
                'prev_part': prev_part,
                'next_part': next_part,
                'combined': combined,
                'pos_in_text': (i, len(prev_tokens))
            })
    return issues

def merge_linebreak_words(text, linebreak_issues):
    lines = text.splitlines()
    for issue in reversed(linebreak_issues):
        i, _ = issue['pos_in_text']
        lines[i] = lines[i].rstrip() + issue['combined'] + lines[i+1].lstrip()[len(issue['next_part']):]
        lines.pop(i+1)
    return "\n".join(lines)

def pythainlp_spellcheck(tokens, pos_tags, dict_words=None, ignore_words=None):
    if dict_words is None:
        dict_words = thai_dict
    if ignore_words is None:
        ignore_words = set()
    misspelled = []
    for i, w in enumerate(tokens):
        if not w.strip() or w in dict_words or w in ignore_words or len(w) == 1 or 'ๆ' in w:
            continue
        misspelled.append({
            'word': w,
            'pos': pos_tags[i][1] if i < len(pos_tags) else None,
            'index': i
        })
    return misspelled

def longdo_spellcheck_batch(words):
    results = {}
    if not words:
        return results
    try:
        headers = {'Content-Type': 'application/json'}
        payload = {"key": API_KEY, "text": "\n".join(words)}
        response = requests.post(API_URL, headers=headers, json=payload, timeout=6)
        if response.status_code == 200:
            result = response.json()
            for e in result.get("result", []):
                if e.get("suggestions"):
                    results[e["word"]] = e["suggestions"]
    except Exception as e:
        print(f"Exception calling longdo: {e}")
    return results

def check_loanword_spelling(tokens, whitelist):
    mistakes = []
    for tok in tokens:
        # Find close matches with a lower cutoff for loanwords
        matches = difflib.get_close_matches(tok, list(whitelist), n=1, cutoff=0.7) # Lowered cutoff
        if matches and tok not in whitelist:
            mistakes.append({'found': tok, 'should_be': matches[0]})
    return mistakes


def find_unallowed_punctuations(text):
    pattern = f"[^{''.join(re.escape(p) for p in allowed_punctuations)}a-zA-Z0-9ก-๙\\s]"
    return set(re.findall(pattern, text))

def separate_maiyamok(text):
    return re.sub(r'(\S+?)ๆ', r'\1 ๆ', text)

def analyze_maiyamok(tokens, pos_tags):
    results = []
    found_invalid = False
    VALID_POS = {'NCMN', 'NNP', 'VACT', 'VNIR', 'CLFV', 'ADVN', 'ADVI', 'ADVP', 'PRP', 'ADV'}
    for i, token in enumerate(tokens):
        if token == 'ๆ':
            prev_idx = i - 1
            prev_word = tokens[prev_idx] if prev_idx >= 0 else None
            prev_tag = pos_tags[prev_idx][1] if prev_idx >= 0 else None
            if prev_word is None or prev_word == 'ๆ':
                verdict = "❌ ไม้ยมกไม่ควรขึ้นต้นประโยค/คำ"
            elif prev_word in forbid_list:
                verdict = '❌ ไม่ควรใช้ไม้ยมกกับคำนี้'
            elif (prev_tag in VALID_POS) or (prev_word in allow_list):
                verdict = '✅ ถูกต้อง (ใช้ไม้ยมกซ้ำคำได้)'
            else:
                verdict = '❌ ไม่ควรใช้ไม้ยมok นอกจากกับคำนาม/กริยา/วิเศษณ์'
            context = tokens[max(0, i-2):min(len(tokens), i+3)]
            results.append({
                'คำก่อนไม้ยมก': prev_word or '',
                'POS คำก่อน': prev_tag or '',
                'บริบท': ' '.join(context),
                'สถานะ': verdict
            })
            if verdict.startswith('❌'):
                found_invalid = True
    return results, found_invalid

def detect_split_errors(tokens, custom_words=None):
    check_dict = set(thai_words()).union(custom_words or [])
    check_dict = {w for w in check_dict if (' ' not in w) and w.strip()}
    errors = []
    for i in range(len(tokens) - 1):
        combined = tokens[i] + tokens[i + 1]
        if (' ' not in combined) and (combined in check_dict) and (combined not in splitable_phrases):
            errors.append({
                "split_pair": (tokens[i], tokens[i+1]),
                "suggested": combined
            })
    return errors

def evaluate_text(text):
    # วิเคราะห์
    linebreak_issues = analyze_linebreak_issues(text)
    corrected_text = merge_linebreak_words(text, linebreak_issues)
    tokens = word_tokenize(corrected_text, engine='newmm', keep_whitespace=False)
    pos_tags = pos_tag(tokens, corpus='orchid')

    # ตรวจคำทับศัพท์
    loanword_spell_errors = check_loanword_spelling(tokens, loanwords_whitelist)

    # ตรวจสะกด
    pythai_errors = pythainlp_spellcheck(tokens, pos_tags, dict_words=thai_dict, ignore_words=custom_words)
    wrong_words = [e['word'] for e in pythai_errors]
    longdo_results = longdo_spellcheck_batch(wrong_words)
    spelling_errors_legit = [
        {**e, 'suggestions': longdo_results.get(e['word'], [])}
        for e in pythai_errors if e['word'] in longdo_results
    ]

    # อื่น ๆ
    punct_errors = find_unallowed_punctuations(text)
    maiyamok_results, has_wrong_maiyamok = analyze_maiyamok(tokens, pos_tags)
    split_errors = detect_split_errors(tokens, custom_words=custom_words)

    # ==== นับจำนวนข้อผิดพลาดแต่ละประเภท ====
    error_counts = {
        "spelling": len(spelling_errors_legit) + len(loanword_spell_errors),
        "linebreak": len(linebreak_issues),
        "split": len(split_errors),
        "punct": len(punct_errors),
        "maiyamok": sum(1 for r in maiyamok_results if r['สถานะ'].startswith('❌'))
    }
    n_issue_types = sum(1 for c in error_counts.values() if c > 0)
    multi_in_single_type = any(c >= 2 for c in error_counts.values())

    # ==== เกณฑ์การให้คะแนน (ปรับใหม่) ====
    # นับจำนวน "คำผิดรวม" จากทุกประเภท
    reasons = []
    # ==== สร้าง reasons ====
    reasons = []
    if error_counts["linebreak"]:
        details = [f"{issue['prev_part']} + {issue['next_part']} → {issue['combined']}" for issue in linebreak_issues]
        reasons.append("พบการฉีกคำข้ามบรรทัด: " + "; ".join(details))
    if error_counts["split"]:
        details = [f"{e['split_pair'][0]} + {e['split_pair'][1]} → {e['suggested']}" for e in split_errors]
        reasons.append("พบการแยกคำผิด: " + "; ".join(details))
    if error_counts["spelling"]:
        error_words = [e['word'] for e in spelling_errors_legit]
        error_desc = [f"{e['found']} (ควรเป็น {e['should_be']})" for e in loanword_spell_errors]
        reasons.append(f"ตรวจเจอคำสะกดผิดหรือทับศัพท์ผิด: {', '.join(error_words + error_desc)}")
    if error_counts["punct"]:
        reasons.append(f"ใช้เครื่องหมายที่ไม่อนุญาต: {', '.join(punct_errors)}")
    if error_counts["maiyamok"]:
        wrong_desc = [x for x in maiyamok_results if x['สถานะ'].startswith('❌')]
        texts = [f"{x['คำก่อนไม้ยมก']}: {x['สถานะ']}" for x in wrong_desc]
        reasons.append("ใช้ไม้ยมกผิด: " + '; '.join(texts))
    if not reasons:
        reasons.append("ไม่มีปัญหา")
    total_errors = (
        len(spelling_errors_legit) +
        len(loanword_spell_errors) +
        len(linebreak_issues) +
        len(split_errors) +
        len(punct_errors) +
        sum(1 for r in maiyamok_results if r['สถานะ'].startswith('❌'))
    )

    if total_errors >= 4:
        score = 0
    elif total_errors == 3:
        score = 0.5
    elif total_errors == 2:
        score = 1
    elif total_errors == 1:
        score = 1.5
    else:  # ไม่มีผิดเลย
        score = 2

    return {
        'score': score,
        'linebreak_issues': linebreak_issues,
        'spelling_errors': spelling_errors_legit,
        'loanword_spell_errors': loanword_spell_errors,
        'punctuation_errors': list(punct_errors),
        'maiyamok_results': maiyamok_results,
        'split_errors': split_errors,
        'reasons': reasons,
        'explanations': explanations
    }

# แบบใส่คำตอบเดียว
student_answer = """เห็นด้วย เพราะ การใช้สื่อสังคมออนไลน์มีประโยชน์ต่อเราในโลกปัจจุบัน
ที่มีเทคโนโลยีล้ำสมัย สามารถช่วยเหลือเราในเรื่องต่างๆ ได้ เช่นการรับข่าวสาร
ค้นคว้าหาข้อมูล แต่ควรใช้อย่างระมัดระวังด้วย เราสามารใช้สื่อสังคมออนไลน์ ในการ
ทำสิ่งต่างๆ เช่นการดู สถานที่ ท่องเที่ยวร้านอาหาร เนิองจากยุคปัจจุบัน กลุ่มคนต่างๆ
ที่เป็นผู้ประกอบการหันมาใช้สื่อในการโปรโมทร้านขายของ คนบางกลุ่มใช้ในการเปิดรับ
บริจาคเพื่อช่วยเหลือคน การนำไปใช้ในชีวิตประจําวัน คือการ ส่งของออนไลน์ค้นหา
ข้อมูลเรื่องการเรียน อ่านข่าวสารเรื่องต่างๆ จาก สื่อสังคมออนไลน์
"""
result = evaluate_text(student_answer)

# ✅ แปลงผลลัพธ์เป็น JSON
output_json = json.dumps(result, ensure_ascii=False, indent=2)

print(output_json)
