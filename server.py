from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from supabase import create_client, Client
import uvicorn

# ===== Supabase 连接配置 =====
url = "https://ngfkaxoxnsukgntmrtur.supabase.co"
key = "sb_secret_4MHsA0C2_W_MXEiCFyp5lQ_7l6i0uQO"
supabase: Client = create_client(url, key)

# ===== FastAPI 初始化 =====
app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 允许所有前端访问（可根据需要改）
    allow_methods=["*"],
    allow_headers=["*"],
)

# ===== 取号接口 =====
@app.post("/get_number")
async def get_number(request: Request):
    data = await request.json()
    name = data["name"]

    # 获取当前最大号码
    res = supabase.table("queue").select("number").order("number", desc=True).limit(1).execute()
    max_number = res.data[0]["number"] if res.data else 0

    new_number = max_number + 1
    supabase.table("queue").insert({"name": name, "number": new_number}).execute()
    return {"number": new_number}

# ===== 查询前方人数接口 =====
@app.post("/check_position")
async def check_position(request: Request):
    data = await request.json()
    name = data["name"]

    # 找到当前用户的号码
    res = supabase.table("queue").select("number").eq("name", name).execute()
    if not res.data:
        return {"error": "Not found"}

    user_number = res.data[0]["number"]
    # 统计前方等待人数
    res2 = supabase.table("queue").select("number").lt("number", user_number).eq("status", "waiting").execute()
    count_waiting = len(res2.data)

    return {"number": user_number, "waiting": count_waiting}

# ===== 运行 =====
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
