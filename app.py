from flask import Flask, request, jsonify, render_template
import os
from supabase import create_client, Client

app = Flask(__name__)

url = "https://ngfkaxoxnsukgntmrtur.supabase.co"
key = "sb_secret_4MHsA0C2_W_MXEiCFyp5lQ_7l6i0uQO"
supabase: Client = create_client(url, key)

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/get_number")
async def get_number(request: request):
    data = await request.json()
    name = data["name"]

    # 获取当前最大号码
    res = supabase.table("queue").select("number").order("number", desc=True).limit(1).execute()
    max_number = res.data[0]["number"] if res.data else 0

    new_number = max_number + 1
    supabase.table("queue").insert({"name": name, "number": new_number, "status": "waiting"}).execute()
    return {"number": new_number}

# ===== 查询前方人数接口 =====
@app.route("/check_position")
async def check_position(request: request):
    data = await request.json()
    name = data["name"]

    # 查找用户的号码
    res = supabase.table("queue").select("number").eq("name", name).execute()
    if not res.data:
        return {"error": "User not found"}

    user_number = res.data[0]["number"]
    # 查找前方还在等待的人
    res2 = supabase.table("queue").select("number").lt("number", user_number).eq("status", "waiting").execute()
    waiting_count = len(res2.data)

    return {"number": user_number, "waiting": waiting_count}

if __name__ == '__main__':
    app.run(debug=True)
'''
@app.route('/')
def hello_world():
    return 'hello world'

if __name__ == '__main__':
    app.run(debug=True)
'''