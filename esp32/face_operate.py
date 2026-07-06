import base64
import os
import sys
import json
from tencentcloud.common import credential
from tencentcloud.common.exception.tencent_cloud_sdk_exception import TencentCloudSDKException
from tencentcloud.iai.v20200303 import iai_client, models

# 强制UTF-8编码，解决乱码
sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

# 腾讯云配置
SECRET_ID = os.environ.get("TENCENT_SECRET_ID", "your_tencent_secret_id")
SECRET_KEY = os.environ.get("TENCENT_SECRET_KEY", "your_tencent_secret_key")
GROUP_ID = "attendance_group"
FACE_MATCH_THRESHOLD = 80


def init_iai_client():
    """初始化腾讯云人脸识别客户端"""
    try:
        cred = credential.Credential(SECRET_ID, SECRET_KEY)
        client = iai_client.IaiClient(cred, "ap-beijing")
        return client
    except TencentCloudSDKException as err:
        return None


def add_face(client, base64_image, person_id, person_name):
    """
    动态录入人脸到腾讯云库
    :param client: 腾讯云客户端
    :param base64_image: 前端传的Base64人脸图片（无header）
    :param person_id: 员工ID（作为腾讯云PersonId，唯一）
    :param person_name: 员工姓名
    :return: 执行结果JSON
    """
    try:
        req = models.CreatePersonRequest()
        req.GroupId = GROUP_ID
        req.PersonId = str(person_id)  # 与员工表id一致，便于关联
        req.PersonName = person_name
        req.Image = base64_image
        resp = client.CreatePerson(req)
        return {
            "success": True,
            "person_id": str(person_id),
            "face_id": resp.FaceId,
            "message": "人脸录入成功"
        }
    except TencentCloudSDKException as err:
        err_str = str(err)
        if "PersonIdAlreadyExist" in err_str:
            return {
                "success": False,
                "error_msg": "该员工已录入人脸，无需重复操作"
            }
        else:
            return {
                "success": False,
                "error_msg": f"人脸录入失败：{err_str}"
            }


def verify_face(client, base64_image):
    """原有验证人脸逻辑，无修改"""
    try:
        req = models.SearchFacesRequest()
        req.GroupIds = [GROUP_ID]
        req.Image = base64_image
        req.MaxFaceNum = 1
        req.FaceMatchThreshold = FACE_MATCH_THRESHOLD
        resp = client.SearchFaces(req)
        if resp.Results and len(resp.Results) > 0:
            first_face = resp.Results[0]
            if first_face.Candidates and len(first_face.Candidates) > 0:
                best_match = first_face.Candidates[0]
                if best_match.Score >= FACE_MATCH_THRESHOLD:
                    return {
                        "success": True,
                        "tencent_face_id": best_match.PersonId,
                        "score": float(best_match.Score),
                        "person_name": best_match.PersonName
                    }
                else:
                    return {
                        "success": False,
                        "error_msg": f"人脸相似度不足（{best_match.Score:.2f}分，阈值{FACE_MATCH_THRESHOLD}分）"
                    }
            else:
                return {"success": False, "error_msg": "腾讯云人脸库中未匹配到人员"}
        else:
            return {"success": False, "error_msg": "图片中未检测到有效人脸"}
    except TencentCloudSDKException as err:
        return {"success": False, "error_msg": f"人脸识别失败：{str(err)}"}


if __name__ == "__main__":
    try:
        # 接收后端传的参数：操作类型(add/verify) + Base64图片 + 员工信息（仅add需要）
        data = json.loads(sys.stdin.read())
        operate_type = data.get("type")
        base64_image = data.get("image")
        client = init_iai_client()

        if not client:
            print(json.dumps({"success": False, "error_msg": "腾讯云客户端初始化失败"}))
            sys.exit(1)
        if not operate_type or not base64_image:
            print(json.dumps({"success": False, "error_msg": "参数缺失"}))
            sys.exit(1)

        # 执行对应操作
        if operate_type == "add":
            person_id = data.get("person_id")
            person_name = data.get("person_name")
            if not person_id or not person_name:
                print(json.dumps({"success": False, "error_msg": "录入人脸需传入员工ID和姓名"}))
                sys.exit(1)
            result = add_face(client, base64_image, person_id, person_name)
        elif operate_type == "verify":
            result = verify_face(client, base64_image)
        else:
            result = {"success": False, "error_msg": "不支持的操作类型，仅支持add/verify"}

        print(json.dumps(result, ensure_ascii=False))
        sys.exit(0)
    except Exception as e:
        print(json.dumps({"success": False, "error_msg": f"脚本执行异常：{str(e)}"}))
        sys.exit(1)
