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

@app.route('/go_signagepage')
def gosignagepage():
    return render_template("signagepage.html")

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
    
# ===== 查询下一个用户 =====
@app.route("/get_next_user", methods=['POST'])
def get_next_user():
    data = request.json
    current_id = data["current_id"]
    num_limit = 1
    next_user = supabase.table("User").select("*")\
        .gt("id",current_id).in_("status", ["waiting", "passed"]).order("id", desc=False).limit(num_limit).execute()
    if not next_user.data:
        return {"status":1}
    else:
        return {"data":next_user.data,"status":0}

# ===== check当前用户 =====
@app.route("/check_current_user", methods=['POST'])
def check_current_user():
    data = request.json
    current_id = data["current_id"]
    res = supabase.table("User").select("*").eq("id",current_id).execute()
    if res.data[0]["status"] == "checked":
        return {"status":2,"data":res.data}
    res = supabase.table("User").update({"status": "checked",\
                                         "time_start":datetime.now().strftime("%Y-%m-%d %H:%M:%S")})\
                                            .eq("id", current_id).execute()
    if not res.data:
        print("update error:")
        return {"status":1}
    elif res.data[0]["status"] == "expired":
        return {"status":3,"data":res.data}
    else:
        return {"status":0,"data":res.data}
    
# ===== pass当前用户 =====
@app.route("/pass_current_user", methods=['POST'])
def pass_current_user():
    data = request.json
    current_id = data["current_id"]

    current_user = supabase.table("User").select("*")\
        .eq("id",current_id).execute()
    if current_user.data[0]["status"] == "waiting":
        res = supabase.table("User").update({"status": "passed"}).eq("id", current_id).execute()
        if res:
            return {"status":"passed","data":current_user.data}
    elif current_user.data[0]["status"] == "passed":
        res = supabase.table("User").update({"status": "expired"}).eq("id", current_id).execute()
        if res:
            return {"status":"expired","data":current_user.data}
    else:
        print("update error:")
        return {"status":"error"}
        
    print("update error:")
    return {"status":"error"}


# ===== 显示队列长度 =====
@app.route("/get_queue_length", methods=["GET"])
def get_queue_length():
    time_per_group = 10
    user_per_group = 5
    queue_list = supabase.table("User").select("*")\
        .in_("status", ["waiting", "passed"]).execute()
    queue_length = len(queue_list.data)
    if queue_length == 0:
        queue_time = 0
    else:
        queue_time = (queue_length  // user_per_group + 0.5) * time_per_group
    res = supabase.table("User").select("id").eq("status", "checked") \
        .order("id", desc=True).limit(1).execute()
    if not res.data:
        index = "Null"
    else:
        index = res.data[0]["id"]
    return {"status":0, "queue_length":queue_length,"queue_time":queue_time,"index":index}

# ===== 修改状态 =====
@app.route("/status_change", methods=["POST"])
def status_change():
    data = request.json
    new_status = data["new_status"]
    target_id = data["target_id"]
    res = supabase.table("User").select("*").eq("id",target_id).execute()
    if not res.data:
        return {"status":1}
    else:
        res = supabase.table("User").update({"status":new_status}).eq("id",target_id).execute()
        return {"status":0, "data":res.data}

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))  # Render 会提供 PORT 环境变量
    app.run(host="0.0.0.0", port=port)

""" 
if __name__ == "__main__":
    app.run(debug=True) """

