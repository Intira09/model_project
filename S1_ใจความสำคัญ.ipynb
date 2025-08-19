{
  "nbformat": 4,
  "nbformat_minor": 0,
  "metadata": {
    "colab": {
      "provenance": []
    },
    "kernelspec": {
      "name": "python3",
      "display_name": "Python 3"
    },
    "language_info": {
      "name": "python"
    }
  },
  "cells": [
    {
      "cell_type": "code",
      "source": [
        "import re\n",
        "import json\n",
        "\n",
        "# --- ฟังก์ชันนับ keyword ---\n",
        "def find_keywords(text, keywords):\n",
        "    return any(kw in text for kw in keywords)\n",
        "\n",
        "def score_group_1(text):\n",
        "    media_keywords = [\"สื่อสังคมออนไลน์\", \"สื่อสังคม\", \"สื่อออนไลน์\"]\n",
        "    usage_keywords = [\"เป็นช่องทาง\", \"แพร่กระจาย\", \"ช่องทาง\", \"ค้นหา\", \"รับข้อมูลข่าวสาร\", \"เผยแพร่\"]\n",
        "\n",
        "    found_media = find_keywords(text, media_keywords)\n",
        "    found_usage = find_keywords(text, usage_keywords)\n",
        "\n",
        "    score = 1 if (found_media and found_usage) else 0\n",
        "    return score\n",
        "\n",
        "def score_group_2(text):\n",
        "    keypoints_1 = [\"ไม่ระวัง\", \"ไม่ระมัดระวัง\", \"ขาดความรับผิดชอบ\"]\n",
        "    keypoints_2 = [\"โทษ\", \"ผลเสีย\", \"ข้อเสีย\", \"เกิดผลกระทบ\", \"สิ่งไม่ดี\"]\n",
        "\n",
        "    found_1 = find_keywords(text, keypoints_1)\n",
        "    found_2 = find_keywords(text, keypoints_2)\n",
        "\n",
        "    score = 1 if (found_1 and found_2) else 0\n",
        "    return score\n",
        "\n",
        "def score_group_3(text):\n",
        "    keypoints = [\"รู้เท่าทัน\", \"รู้ทัน\", \"ผู้ใช้ต้องรู้เท่าทัน\", \"รู้ทันสืื่อสังคม\"]\n",
        "    found = find_keywords(text, keypoints)\n",
        "    score = 1 if found else 0\n",
        "    return score\n",
        "\n",
        "def score_group_4(text):\n",
        "    media_use_keywords = [\"ใช้สื่อสังคม\", \"ใช้สื่อออนไลน์\", \"ใช้สื่อสังคมออนไลน์\", \"การใช้สื่อ\"]\n",
        "    hidden_intent_keywords = [\"เจตนาแอบแฝง\", \"ผลกระทบต่อ\", \"ผลกระทบ\"]\n",
        "    credibility_keywords = [\"ความน่าเชื่อถือของข่าวสาร\", \"ความน่าเชื่อถือของข้อมูลข่าวสาร\"]\n",
        "\n",
        "    found_media_use = find_keywords(text, media_use_keywords)\n",
        "    found_hidden_intent = find_keywords(text, hidden_intent_keywords)\n",
        "    found_credibility = find_keywords(text, credibility_keywords)\n",
        "\n",
        "    score = 1 if (found_media_use and found_hidden_intent and found_credibility) else 0\n",
        "    return score\n",
        "\n",
        "# --- ฟังก์ชันประเมินคำตอบคนเดียวและคืน JSON ---\n",
        "def evaluate_answer(answer_text):\n",
        "    score1 = score_group_1(answer_text)\n",
        "    score2 = score_group_2(answer_text)\n",
        "    score3 = score_group_3(answer_text)\n",
        "    score4 = score_group_4(answer_text)\n",
        "\n",
        "    result = {\n",
        "        \"score_1\": score1,\n",
        "        \"score_2\": score2,\n",
        "        \"score_3\": score3,\n",
        "        \"score_4\": score4,\n",
        "        \"total_score\": score1 + score2 + score3 + score4\n",
        "    }\n",
        "\n",
        "    return json.dumps(result, ensure_ascii=False, indent=2)\n",
        "\n",
        "# --- ตัวอย่างการใช้งาน ---\n",
        "answer = \"\"\"\n",
        "สื่อสังคม หรือที่เรียกว่า สื่อออนไลน์เป็นสื่อหรือช่องทางที่แพร่\n",
        "กระจาย ข้อมูลข่าวสารในแบบต่างๆได้อย่างรวดเร็วขึ้นไปยังทั่วโลกที่สัญ\n",
        "ญาณโทรศัพท์เข้าถึง เช่น ทั่วโลก เช่น การนำ เสนอข้อมูลและข้อ\n",
        "ดีประเภทสิน ค้า ชั้นนำ สินค้าพื้นเมืองให้เข้าถึงผู้ซื้อได้ทั่วโลก\n",
        "และการนำเสนอข่าวอย่างตรงไปมาไห้เกิดผลดีและนำเสนอข้อเท็จจริง\"\"\"\n",
        "\n",
        "print(evaluate_answer(answer))\n"
      ],
      "metadata": {
        "colab": {
          "base_uri": "https://localhost:8080/"
        },
        "collapsed": true,
        "id": "ucVu8wW2A-Lj",
        "outputId": "aacff396-d537-460c-9c4f-78cb7ee6f69a"
      },
      "execution_count": 3,
      "outputs": [
        {
          "output_type": "stream",
          "name": "stdout",
          "text": [
            "{\n",
            "  \"score_1\": 1,\n",
            "  \"score_2\": 0,\n",
            "  \"score_3\": 0,\n",
            "  \"score_4\": 0,\n",
            "  \"total_score\": 1\n",
            "}\n"
          ]
        }
      ]
    }
  ]
}
