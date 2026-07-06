import serial
import time
import requests

# 配置（根据你的环境修改）
SERIAL_PORT = "COM5"  # 你的ESP32串口号
BAUDRATE = 115200
NODE_BACKEND_URL = "http://127.0.0.1:8080/api/nfc/verify"  # Node后端验证接口

# 初始化串口
ser = serial.Serial(SERIAL_PORT, BAUDRATE, timeout=1)
time.sleep(2)  # 给ESP32上电时间
print("✅ 身份验证系统已启动，等待刷卡...")


def verify_card_with_backend(card_id):
    """把卡号发给Node后端验证，返回（是否合法，失败/成功原因）"""
    try:
        res = requests.post(
            NODE_BACKEND_URL,
            json={"cardId": card_id},
            timeout=3  # 超时3秒
        )
        res_data = res.json()
        # 提取是否合法 + 原因
        is_valid = res_data.get("code") == 200 and res_data.get("isValid", False)
        message = res_data.get("message", "未知原因")
        return is_valid, message
    except Exception as e:
        print(f"❌ 连接后端失败：{e}")
        return False, f"连接失败：{e}"


while True:
    if ser.in_waiting > 0:
        card_id = ser.readline().decode("utf-8").strip()
        if not card_id:
            continue

        print(f"\n📇 检测到物理ID：{card_id}")
        # 调用后端验证卡号（获取是否合法 + 原因）
        is_valid, msg = verify_card_with_backend(card_id)

        # 新增：根据原因判断场景并打印
        if is_valid:
            print(f"✅ 身份验证成功！→ {msg}（打卡成功）")
            ser.write(b"1")  # 发送成功指令给ESP32
        else:
            # 区分“卡号未注册（可添加）”和“其他失败”
            if "卡号未注册" in msg:
                print(f"❌ 身份验证失败！→ {msg}（可在添加员工页面绑定）")
            else:
                print(f"❌ 身份验证失败！→ {msg}")
            ser.write(b"0")  # 发送失败指令给ESP32