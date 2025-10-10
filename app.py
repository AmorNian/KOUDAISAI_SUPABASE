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

@app.route("/get_number", methods=['POST'])
def get_number():
    data = request.json
    name = data["name"]
    if len(name) == 0:
        return {"status": 1}
    # 获取当前最大号码
    res = supabase.table("User").select("id").order("id", desc=True).limit(1).execute()
    max_number = res.data[0]["id"] if res.data else 0

    new_number = max_number + 1
    supabase.table("User").insert({"name": name, "id": new_number, "status": 0, "time_start":"10:10"}).execute()
    return {"number": new_number, "status": 0}

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
    port = int(os.environ.get("PORT", 5000))  # Render 会提供 PORT 环境变量
    app.run(host="0.0.0.0", port=port)
'''
@app.route('/')
def hello_world():
    return 'hello world'

if __name__ == '__main__':
    app.run(debug=True)
'''