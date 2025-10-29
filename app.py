from flask import Flask, request, jsonify, render_template
import os
from supabase import create_client, Client
from datetime import datetime

app = Flask(__name__)

url = "https://ngfkaxoxnsukgntmrtur.supabase.co"
key = "sb_secret_4MHsA0C2_W_MXEiCFyp5lQ_7l6i0uQO"
supabase: Client = create_client(url, key)
adminpassword = "Sakaguchi2025"

@app.route("/")
def home():
    return render_template("index.html")

@app.route('/adminlogin')
def adminlogin():
    return render_template("adminlogin.html")

@app.route('/adminpage')
def adminpage():
    return render_template("adminpage.html")

# ===== 新用户注册 =====
@app.route("/get_number", methods=['POST'])
def get_number():
    data = request.json
    name = data["name"]
    # 没有输入名字
    if len(name) == 0:
        return {"status": 1}
    
    res = supabase.table("User").select("*").eq("name", name).execute()
    if res.data:
        # 重名了
        return {"status": 2}
    else:
        # 增加一个用户
        res = supabase.table("User").select("id").order("id", desc=True).limit(1).execute()
        max_number = res.data[0]["id"] if res.data else 0
        new_number = max_number + 1
        supabase.table("User")\
            .insert({"name": name, "id": new_number, "status": "waiting", \
                     "time_reception": datetime.now().strftime("%Y-%m-%d %H:%M:%S")}).execute()
        return {"number": new_number, "status": 0}

# ===== 查询前方人数接口 =====
@app.route("/check_position", methods=['POST'])
def check_position():
    data = request.json
    name = data["name"]

    # 查找用户的号码
    res = supabase.table("User").select("").eq("name", name).execute()
    # 查看状态
    if not res.data:
        return {"status": "no user"}
    if res.data[0]["status"] == "passed":
        return {"status": "passed"}
    if res.data[0]["status"] == "expired":
        return {"status": "expired"}
    
    user_number = res.data[0]["id"]
    # 查找前方还在等待的人
    res2 = supabase.table("User").select("id")\
        .lt("id", user_number).in_("status", ["waiting", "passed"]).execute()
    waiting_count = len(res2.data)

    return {"number": user_number, "waiting": waiting_count}

# ===== 管理员登录 =====
@app.route("/admin_login", methods=['POST'])
def admin_login():
    data = request.json
    pwd = data["password"]
    if pwd == adminpassword:
        return {"status": 0}
    else:
        return {"status": 1}
    
# ===== 查询叫号名单 =====
@app.route("/get_waiting_list", methods=['POST'])
def get_waiting_list():
    num_limit = 5
    waiting_list = supabase.table("User").select("*")\
        .in_("status", ["waiting", "passed"]).order("id", desc=False).limit(num_limit).execute()
    return waiting_list

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))  # Render 会提供 PORT 环境变量
    app.run(host="0.0.0.0", port=port)

""" 
if __name__ == "__main__":
    app.run(debug=True) """

