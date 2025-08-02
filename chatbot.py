import os
from openai import OpenAI
from dotenv import load_dotenv
load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

import os, re
from openai import OpenAI


def chat_with_gpt(message, users):
    ml = message.lower()
    # add balance command
    if any(cmd in ml for cmd in ["أضف","زيادة","اضف"]):
        for u in users.values():
            if u['display_name'] in message or u['name'] in ml:
                amt = re.search(r'(\d+(\.\d+)?)', message)
                if amt:
                    val = float(amt.group(1))
                    u['balance'] += val
                    return f"تم إضافة {val}$ إلى رصيد {u['display_name']}. الرصيد الآن {u['balance']}$"
    # check balance
    if "رصيد" in ml:
        for u in users.values():
            if u['display_name'] in message or u['name'] in ml:
                return f"رصيد {u['display_name']} الحالي: {u['balance']}$"
    # check spending
    if any(w in ml for w in ["صرف","انفاق"]):
        for u in users.values():
            if u['display_name'] in message or u['name'] in ml:
                return f"مجموع ما أنفق الأسبوع الماضي لـ {u['display_name']}: {u['weekly_spent']}$"
    # fallback to GPT-4 Arabic
    resp = client.chat.completions.create(
        model="gpt-4o",
        messages=[
          {"role":"system","content":"أجب باللهجة السعودية"},
          {"role":"user","content":message}
        ]
    )
    return resp.choices[0].message.content
