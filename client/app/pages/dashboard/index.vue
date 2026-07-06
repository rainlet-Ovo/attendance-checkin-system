<template>
  <div class="dashboard-container">
    <header class="dashboard-header">
      <div class="header-left">
        <h1>员工考勤管理系统</h1>
      </div>
      <div class="header-right">
        <span class="user-info">当前登录：{{ username || '未登录' }}</span>
        <button @click="logout" class="logout-btn">退出登录</button>
      </div>
    </header>

    <main class="dashboard-main">
      <!-- 人脸识别打卡模块 -->
      <div class="module-card face-check-card">
        <h2 class="module-title">人脸识别打卡</h2>
        <div class="face-check-content">
          <div class="camera-box">
            <div id="faceCamera" class="camera-container"
              style="width: 100%; max-width: 480px; height: 360px; overflow: hidden; border-radius: 8px; background: #f5f5f5;">
              <div v-if="!cameraStream" class="camera-placeholder"
                style="width: 100%; height: 100%; display: flex; align-items: center; justify-content: center; color: #666;">
                点击「开启摄像头」开始打卡
              </div>
              <video v-show="cameraStream" id="video" autoplay playsinline
                style="width:100%;height:100%;object-fit:cover;"></video>
            </div>
            <div class="camera-btn-group">
              <button @click="startCamera" class="btn primary-btn" :disabled="cameraStream">
                开启摄像头
              </button>
              <button @click="stopCamera" class="btn default-btn" :disabled="!cameraStream">
                关闭摄像头
              </button>
              <button @click="faceCheckIn" class="btn export-btn face-check-btn" :disabled="!cameraStream || loading">
                {{ loading ? '识别中...' : '立即打卡' }}
              </button>
            </div>
          </div>
          <div class="face-tip-box">
            <div class="face-tip" :class="tipType">
              {{ faceTip }}
            </div>
            <div class="face-rule">
              <h4>打卡规则</h4>
              <ul>
                <li>请在光线充足的环境下打卡</li>
                <li>面部正对摄像头，无遮挡（口罩/帽子）</li>
                <li>识别相似度≥80分方可打卡成功</li>
                <li>仅支持本人人脸打卡，请勿代打</li>
              </ul>
            </div>
          </div>
        </div>
      </div>


      <div class="module-card">
        <h2 class="module-title">出勤记录查询</h2>
        <div class="search-form">
          <div class="form-item">
            <label>员工ID：</label>
            <input v-model="searchParams.employeeId" type="number" placeholder="请输入员工ID" class="form-input" />
          </div>
          <div class="form-item">
            <label>日期：</label>
            <input v-model="searchParams.date" type="date" class="form-input" />
          </div>
          <button @click="fetchAttendance" class="btn primary-btn">查询</button>
          <button @click="resetSearch" class="btn default-btn">重置</button>
          <button @click="exportAttendance" class="btn export-btn">导出通勤表</button>
        </div>

        <div class="table-container">
          <table class="data-table">
            <thead>
              <tr>
                <th>记录ID</th>
                <th>员工ID</th>
                <th>员工姓名</th>
                <th>日期</th>
                <th>出勤状态</th>
                <th>上班时间</th>
                <th>下班时间</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="record in displayAttendanceList" :key="record.id">
                <td>{{ record.id }}</td>
                <td>{{ record.employeeId }}</td>
                <td>{{ record.employeeName }}</td>
                <td>{{ record.date }}</td>
                <td>
                  <span class="status-tag" :class="getStatusClass(record.status)">
                    {{ record.status }}
                  </span>
                </td>
                <td>{{ record.checkIn }}</td>
                <td>{{ record.checkOut }}</td>
              </tr>
              <tr v-if="employeeList.length === 0">
                <td colspan="7" class="empty-cell">暂无数据</td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>

      <div class="module-card">
        <h2 class="module-title">员工管理</h2>
        <button @click="openAddEmployeeDialog" class="btn primary-btn mb-10">添加员工</button>
        <div class="table-container">
          <table class="data-table">
            <thead>
              <tr>
                <th>员工ID</th>
                <th>姓名</th>
                <th>工卡号</th>
                <th>部门</th>
                <th>入职日期</th>
                <th>操作</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="employee in employeeList" :key="employee.id">
                <td>{{ employee.id }}</td>
                <td>{{ employee.name }}</td>
                <td>{{ employee.cardId || '—' }}</td>
                <td>{{ employee.department }}</td>
                <td>{{ employee.hireDate }}</td>
                <td>
                  <button @click="deleteEmployee(employee.id)" class="btn danger-btn mr-5">删除</button>
                  <button @click="openAddFaceDialog(employee)" class="btn primary-btn mr-5">录入人脸</button>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </main>
  </div>

  <!-- 添加员工弹窗 -->
  <div class="dialog-mask" v-if="addDialogVisible" @click="closeAddEmployeeDialog">
    <div class="dialog-content" @click.stop>
      <div class="dialog-header">
        <h3>新增员工</h3>
        <button class="close-btn" @click="closeAddEmployeeDialog">×</button>
      </div>
      <div class="dialog-body">
        <form class="add-employee-form" @submit.prevent="submitAddEmployee">
          <div class="form-item nfc-item">
            <div class="nfc-row">
              <label class="form-label">NFC卡号：</label>
              <div class="input-group">
                <input v-model="addForm.cardId" placeholder="请刷NFC卡自动填充" class="form-input" readonly />
                <button type="button" @click="clearCardId" class="btn default-btn small-btn">清空</button>
              </div>
            </div>
            <span class="form-tip" v-if="cardTip">{{ cardTip }}</span>
          </div>
          <div class="form-item">
            <label class="form-label">登录账号：</label>
            <input v-model="addForm.username" placeholder="请输入登录账号" class="form-input" required />
          </div>
          <div class="form-item">
            <label class="form-label">员工姓名：</label>
            <input v-model="addForm.realName" placeholder="请输入员工真实姓名" class="form-input" required />
          </div>
          <div class="form-item">
            <label class="form-label">初始密码：</label>
            <div class="input-group">
              <input v-model="addForm.password" :type="showPassword ? 'text' : 'password'" placeholder="请输入初始密码"
                class="form-input" required />
              <button type="button" @click="showPassword = !showPassword" class="btn default-btn small-btn">
                {{ showPassword ? '隐藏' : '显示' }}
              </button>
            </div>
          </div>
          <div class="form-item">
            <label class="form-label">所属职位：</label>
            <select v-model="addForm.positionId" class="form-input" required>
              <option value="">请选择职位</option>
              <option v-for="pos in positionList" :key="pos.id" :value="pos.id">{{ pos.position_name }}</option>
            </select>
          </div>
        </form>
      </div>
      <div class="dialog-footer">
        <button class="btn default-btn" @click="closeAddEmployeeDialog">取消</button>
        <button class="btn primary-btn" @click="submitAddEmployee"
          :disabled="!addForm.cardId || !addForm.username || !addForm.realName || !addForm.positionId">提交添加</button>
      </div>
    </div>
  </div>

  <!-- 录入人脸弹窗 -->
  <div class="dialog-mask" v-if="addFaceDialogVisible" @click="closeAddFaceDialog">
    <div class="dialog-content" @click.stop style="width: 700px;">
      <div class="dialog-header">
        <h3>为【{{ currentFaceEmployee.name }}】录入人脸</h3>
        <button class="close-btn" @click="closeAddFaceDialog">×</button>
      </div>
      <div class="dialog-body">
        <div class="face-check-content" style="margin: 0;">
          <div class="camera-box" style="min-width: 300px; max-width: 400px;">
            <div id="addFaceCamera" class="camera-container"
              style="width: 100%; max-width: 400px; height: 300px; overflow: hidden; border-radius: 8px; background: #f5f5f5;">
              <div v-if="!addFaceCameraStream" class="camera-placeholder"
                style="width: 100%; height: 100%; display: flex; align-items: center; justify-content: center; color: #666;">
                点击「开启摄像头」开始采集
              </div>
              <video v-show="addFaceCameraStream" id="addFaceVideo" autoplay playsinline
                style="width:100%;height:100%;object-fit:cover;"></video>
            </div>
            <div class="camera-btn-group" style="margin-top: 15px;">
              <button @click="startAddFaceCamera" class="btn primary-btn" :disabled="addFaceCameraStream">
                开启摄像头
              </button>
              <button @click="stopAddFaceCamera" class="btn default-btn" :disabled="!addFaceCameraStream">
                关闭摄像头
              </button>
              <button @click="captureFace" class="btn export-btn" :disabled="!addFaceCameraStream || addFaceLoading">
                {{ addFaceLoading ? '采集录入中...' : '采集并录入' }}
              </button>
            </div>
          </div>
          <div class="face-tip-box" style="min-width: 250px;">
            <div class="face-tip" :class="addFaceTipType" style="font-size: 14px;">
              {{ addFaceTip }}
            </div>
            <div class="face-rule" style="padding: 15px;">
              <h4 style="font-size: 15px;">采集规则</h4>
              <ul style="font-size: 13px;">
                <li>光线充足，面部无遮挡（口罩/帽子/眼镜）</li>
                <li>面部正对摄像头，保持头部稳定</li>
                <li>采集后自动提交至人脸库，请勿重复操作</li>
              </ul>
            </div>
          </div>
        </div>
      </div>
      <div class="dialog-footer">
        <button class="btn default-btn" @click="closeAddFaceDialog">取消</button>
      </div>
    </div>
  </div>

</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue';
import { useRouter } from 'vue-router';
import request from '../utils/request';
import { ElMessage } from 'element-plus'

const router = useRouter();
const addDialogVisible = ref(false); // 弹窗显示状态
const addForm = ref({ // 新增员工表单
  cardId: '', username: '', realName: '', password: '', positionId: ''
});

const cameraStream = ref(null); // 摄像头流
const loading = ref(false); // 识别加载状态
const faceTip = ref('请开启摄像头进行人脸识别打卡'); // 打卡提示
const tipType = ref('normal'); // 提示类型：normal/success/error/warning
const currentUser = ref(null);
if (process.client) {
  currentUser.value = JSON.parse(localStorage.getItem('currentUser') || 'null');
}


// 录入人脸弹窗相关
const addFaceDialogVisible = ref(false); // 弹窗显示
const currentFaceEmployee = ref({ id: '', name: '' }); // 当前要录入的员工
const addFaceCameraStream = ref(null); // 录入人脸的摄像头流
const addFaceLoading = ref(false); // 录入加载状态
const addFaceTip = ref('请开启摄像头采集人脸'); // 录入提示
const addFaceTipType = ref('normal'); // 提示类型：normal/success/error/warning


const showPassword = ref(false); // 新增：密码可见状态（默认隐藏）
const positionList = ref([]); // 职位列表（供下拉选择）
const cardTip = ref('');      // NFC卡号提示
let nfcTimer = null;          // NFC轮询定时器
const username = ref('');
const searchParams = ref({ employeeId: '', date: '', status: '' });
const displayAttendanceList = ref([]);
const employeeList = ref([]);

// 状态样式映射
const getStatusClass = (status) => {
  switch (status) {
    case '正常': return 'status-normal';
    case '迟到': return 'status-late';
    case '早退': return 'status-early';
    case '缺勤': return 'status-absent';
    case '请假': return 'status-leave';
    case '加班': return 'status-overtime';
    default: return 'status-other';
  }
};

// 页面加载时校验登录状态
onMounted(async () => {
  // 仅在客户端执行登录状态校验
  if (process.client) {
    const token = localStorage.getItem('token');
    // 未登录/无token，强制跳转登录页
    if (!token || !currentUser.value) {
      router.push('/');
      return;
    }
  }

  // 已登录，初始化数据
  username.value = currentUser.value?.realName || '';
  try {
    await fetchEmployeeList();
    await fetchAttendance();
    await fetchPositionList();
    // 初始化视频元素
    if (process.client) {
      nextTick(() => {
        const video = document.getElementById('video');
        if (video) video.style.display = 'none'; // 避免 DOM 不存在报错
      });
    }
  } catch (err) {
    // token无效/过期，跳转登录页
    if (process.client) {
      localStorage.clear();
      router.push('/');
    }
  }
});

// 1. 查询考勤记录
const fetchAttendance = async () => {
  try {
    const params = {};
    if (searchParams.value.employeeId) params.userId = searchParams.value.employeeId;
    if (searchParams.value.date) params.date = searchParams.value.date;
    // 添加状态筛选
    // if (searchParams.value.status) params.status = searchParams.value.status;

    const res = await request.get('/attendance', { params });

    // 适配后端返回的字段格式
    displayAttendanceList.value = res.data.map(item => ({
      id: item.id,
      employeeId: item.user_id,
      employeeName: item.real_name,
      date: item.check_date,
      status: item.status,
      checkIn: item.check_in_time || '—',
      checkOut: item.check_out_time || '—'
    }));

    if (res.data.length === 0) {
      ElMessage.info('未查询到符合条件的出勤记录！');
    }
  } catch (err) {
    console.error('考勤查询失败：', err);
    ElMessage.error(err.message || '考勤查询失败，请重试');
  }
};

// 2. 获取员工列表（对接后端）
const fetchEmployeeList = async () => {
  try {
    const res = await request.get('/user');
    // 适配后端返回的字段格式
    employeeList.value = res.data.map(item => ({
      id: item.id,
      name: item.real_name,
      department: item.position_name || '未分配',
      hireDate: item.create_time ? item.create_time.split(' ')[0] : '—',
      cardId: item.cardId || '未绑定'
    }));
  } catch (err) {
    console.error('获取员工列表失败：', err);
    ElMessage.error(err.message || '获取员工列表失败，请重试');
  }
};

// 获取职位列表（供添加员工下拉框使用）
const fetchPositionList = async () => {
  try {
    const res = await request.get('/position');
    if (res.code === 200) {
      positionList.value = res.data;
    }
  } catch (err) {
    console.error('获取职位列表失败：', err);
    alert('获取职位列表失败，请重试');
  }
};

// 3. 重置查询条件
const resetSearch = () => {
  searchParams.value = { employeeId: '', date: '', status: '' };
  fetchAttendance();
};

// 4. 导出考勤表（模拟）
const exportAttendance = () => alert('通勤表导出功能暂未实现！');

// 删除员工
const deleteEmployee = async (id) => {
  if (!confirm(`确定删除ID为${id}的员工吗？删除后该员工的所有考勤记录也会一并删除！`)) return;
  try {
    await request.delete(`/user/${id}`);
    await fetchEmployeeList(); // 刷新员工列表
    await fetchAttendance(); // 刷新考勤列表（避免残留已删除员工的考勤记录）
    alert('员工及关联考勤记录删除成功！');
  } catch (err) {
    console.error('删除员工失败：', err);
    alert(err.message || '删除失败，请重试');
  }
};

const openAddEmployeeDialog = () => {
  addForm.value = { cardId: '', username: '', realName: '', password: '', positionId: '' };
  cardTip.value = '请刷NFC卡自动填充卡号...';
  addDialogVisible.value = true;
  if (nfcTimer) clearInterval(nfcTimer);
  nfcTimer = setInterval(async () => { await getNfcCard(); }, 1000);
};

// 关闭弹窗
const closeAddEmployeeDialog = () => {
  addDialogVisible.value = false;
  if (nfcTimer) clearInterval(nfcTimer);
};

// 读取NFC卡号
const getNfcCard = async () => {
  if (!addDialogVisible.value) return;
  try {
    const res = await request.get('/nfc/get-and-clear');
    if (res.code === 200 && res.data?.cardId) {
      addForm.value.cardId = res.data.cardId;
      cardTip.value = `✅ 已读取卡号：${res.data.cardId}`;
    }
  } catch (err) {
    console.error('读取NFC失败：', err);
    cardTip.value = '❌ 读取卡号失败，请检查设备';
  }
};
// 清空卡号
const clearCardId = () => {
  addForm.value.cardId = '';
  cardTip.value = '请重新刷NFC卡...';
};

// 提交添加员工
const submitAddEmployee = async () => {
  if (!addForm.value.cardId) { cardTip.value = '❌ 请先刷NFC卡！'; return; }
  if (!addForm.value.username) { alert('请输入登录账号！'); return; }
  if (!addForm.value.realName) { alert('请输入员工姓名！'); return; }
  if (!addForm.value.positionId) { alert('请选择所属职位！'); return; }
  try {
    const res = await request.post('/user/add', {
      username: addForm.value.username,
      real_name: addForm.value.realName,
      password: addForm.value.password,
      position_id: addForm.value.positionId,
      card_id: addForm.value.cardId,
      role: 'employee',
      status: 1
    });
    // 后端返回 code=200 时触发成功逻辑
    if (res.code === 200) {
      alert('员工添加成功！');
      closeAddEmployeeDialog(); // 关闭弹窗
      await fetchEmployeeList(); // 刷新员工列表
    }
  } catch (err) {
    console.error('添加员工失败：', err);
    // 错误信息由 request.js 拦截器自动提示（无需额外处理）
  }
};


// 打开录入人脸弹窗
const openAddFaceDialog = (employee) => {
  currentFaceEmployee.value = employee;
  addFaceDialogVisible.value = true;
  addFaceTip.value = '请开启摄像头采集人脸';
  addFaceTipType.value = 'normal';
};
// 关闭录入人脸弹窗
const closeAddFaceDialog = () => {
  addFaceDialogVisible.value = false;
  stopAddFaceCamera(); // 关闭摄像头
};

// 开启录入人脸的摄像头
const startAddFaceCamera = async () => {
  try {
    if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
      addFaceTip.value = '您的浏览器不支持摄像头功能，请更换现代浏览器';
      addFaceTipType.value = 'error';
      return;
    }
    const devices = await navigator.mediaDevices.enumerateDevices();
    const videoDevices = devices.filter(d => d.kind === 'videoinput');
    const laptopCamera = videoDevices.find(d => d.label.includes('Integrated Camera'));
    if (!laptopCamera) {
      addFaceTip.value = '未找到笔记本自带摄像头，请检查设备';
      addFaceTipType.value = 'error';
      return;
    }
    const stream = await navigator.mediaDevices.getUserMedia({
      video: {
        deviceId: { exact: laptopCamera.deviceId },
        width: { ideal: 400 },
        height: { ideal: 300 }
      },
      audio: false
    });
    const video = document.getElementById('addFaceVideo');
    if (video) video.srcObject = stream;
    addFaceCameraStream.value = stream;
    addFaceTip.value = '摄像头已开启，请正对摄像头点击「采集并录入」';
    addFaceTipType.value = 'success';
  } catch (err) {
    console.error('开启录入人脸摄像头失败：', err);
    addFaceTip.value = `摄像头开启失败：${err.message}`;
    addFaceTipType.value = 'error';
  }
};
// 关闭录入人脸的摄像头
const stopAddFaceCamera = () => {
  if (addFaceCameraStream.value) {
    addFaceCameraStream.value.getTracks().forEach(track => track.stop());
    addFaceCameraStream.value = null;
  }
  const video = document.getElementById('addFaceVideo');
  if (video) {
    video.srcObject = null;
  }
  addFaceTip.value = '摄像头已关闭';
  addFaceTipType.value = 'normal';
};

// 采集人脸并提交至后端
const captureFace = async () => {
  addFaceLoading.value = true;
  addFaceTip.value = '🔍 正在采集人脸并提交，请稍候...';
  addFaceTipType.value = 'warning';
  try {
    const video = document.getElementById('addFaceVideo');
    const canvas = document.createElement('canvas');
    const scale = 400 / video.videoWidth;
    canvas.width = 400;
    canvas.height = video.videoHeight * scale;
    const ctx = canvas.getContext('2d');
    ctx.drawImage(video, 0, 0, canvas.width, canvas.height);
    // 转Base64（去掉header，仅保留编码）
    const base64Image = canvas.toDataURL('image/jpeg', 0.8).split(';base64,').pop();
    // 调用后端人脸录入接口
    const res = await request.post('/face/add', {
      image: base64Image,
      employeeId: currentFaceEmployee.value.id,
    });
    // 录入成功
    addFaceTip.value = '✅ 人脸录入成功！该员工可进行人脸打卡';
    addFaceTipType.value = 'success';
    ElMessage.success(res.message);
    // 3秒后自动关闭弹窗
    setTimeout(() => {
      closeAddFaceDialog();
    }, 3000);
  } catch (err) {
    console.error('人脸录入失败：', err);
    addFaceTip.value = `❌ 录入失败：${err.message || '服务器异常'}`;
    addFaceTipType.value = 'error';
  } finally {
    addFaceLoading.value = false;
  }
};


// 页面卸载停止NFC轮询
onUnmounted(() => {
  if (nfcTimer) clearInterval(nfcTimer);
  stopCamera();
  stopAddFaceCamera(); // 新增录入人脸摄像头
});

// 人脸识别打卡
const startCamera = async () => {
  try {
    if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
      faceTip.value = '您的浏览器不支持摄像头功能，请更换现代浏览器';
      tipType.value = 'error';
      return;
    }
    const devices = await navigator.mediaDevices.enumerateDevices();
    const videoDevices = devices.filter(d => d.kind === 'videoinput');
    const laptopCamera = videoDevices.find(d => d.label.includes('Integrated Camera'));
    if (!laptopCamera) {
      faceTip.value = '未找到笔记本自带摄像头，请检查设备';
      tipType.value = 'error';
      return;
    }
    const stream = await navigator.mediaDevices.getUserMedia({
      video: {
        deviceId: { exact: laptopCamera.deviceId },
        width: { ideal: 480 },
        height: { ideal: 360 }
      },
      audio: false
    });
    // 赋值stream前先设置video
    const video = document.getElementById('video');
    if (video) video.srcObject = stream;
    cameraStream.value = stream; // v-show触发显示video
    faceTip.value = '摄像头已开启，请正对摄像头点击「立即打卡」';
    tipType.value = 'success';
  } catch (err) {
    console.error('开启摄像头失败：', err);
    faceTip.value = `摄像头开启失败：${err.message}`;
    tipType.value = 'error';
  }
};

// 2. 关闭摄像头
const stopCamera = () => {
  if (cameraStream.value) {
    cameraStream.value.getTracks().forEach(track => track.stop());
    cameraStream.value = null; // 置空后，v-show隐藏video
  }
  const video = document.getElementById('video');
  if (video) {
    video.srcObject = null;
  }
  faceTip.value = '摄像头已关闭';
  tipType.value = 'normal';
};

// 人脸采集并打卡
const faceCheckIn = async () => {
  loading.value = true;
  faceTip.value = '🔍 正在识别人脸，请稍候...';
  tipType.value = 'warning';
  try {
    const video = document.getElementById('video');
    const canvas = document.createElement('canvas');
    const scale = 300 / video.videoWidth;
    canvas.width = 300;
    canvas.height = video.videoHeight * scale;
    const ctx = canvas.getContext('2d');
    ctx.drawImage(video, 0, 0, canvas.width, canvas.height);
    const base64Image = canvas.toDataURL('image/jpeg', 0.7).split(';base64,').pop();

    // 调用后端接口
    const res = await request.post('/face/verify', {
      image: base64Image
    });

    faceTip.value = `✅ 打卡成功！${res.data.realName}（相似度${res.data.faceScore}%），${res.data.checkType}时间：${res.data.checkTime}`;
    tipType.value = 'success';
    await fetchAttendance();
    // 3秒后自动关闭摄像头
    setTimeout(() => {
      stopCamera();
    }, 3000);
  } catch (err) {
    console.error('人脸识别打卡失败：', err);
    faceTip.value = `❌ 打卡失败：${err.message || '人脸识别失败，请重试'}`;
    tipType.value = 'error';
  } finally {
    loading.value = false;
  }
};

// 7. 退出登录
const logout = () => {
  localStorage.removeItem('token');
  localStorage.removeItem('savedUsername');
  localStorage.removeItem('savedPassword');
  router.push('/');
};
</script>

<style scoped>
.dashboard-container {
  min-height: 100vh;
  background-color: #f5f7fa;
}

.dashboard-header {
  background-color: #2c3e50;
  color: white;
  padding: 0 20px;
  height: 60px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.header-left h1 {
  font-size: 20px;
  font-weight: 600;
}

.header-right {
  display: flex;
  align-items: center;
  gap: 20px;
}

.logout-btn {
  background-color: #ff4444;
  color: white;
  border: none;
  padding: 6px 12px;
  border-radius: 4px;
  cursor: pointer;
}

.logout-btn:hover {
  background-color: #cc0000;
}

.dashboard-main {
  padding: 30px 20px;
  max-width: 1400px;
  margin: 0 auto;
}

.module-card {
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.08);
  padding: 20px;
  margin-bottom: 30px;
}

.module-title {
  font-size: 18px;
  color: #333;
  margin-bottom: 20px;
  padding-bottom: 10px;
  border-bottom: 1px solid #eee;
}

.search-form {
  display: flex;
  flex-wrap: wrap;
  gap: 15px;
  align-items: center;
  margin-bottom: 20px;
}

.form-item {
  display: flex;
  align-items: center;
  gap: 10px;
  width: 100%;
}

.btn {
  padding: 8px 16px;
  border-radius: 4px;
  border: none;
  cursor: pointer;
  font-size: 14px;
}

.primary-btn {
  background-color: #4ca1af;
  color: white;
}

.default-btn {
  background-color: #f0f0f0;
  color: #333;
}

.export-btn {
  background-color: #28a745;
  color: white;
}

.danger-btn {
  background-color: #dc3545;
  color: white;
}

.mb-10 {
  margin-bottom: 10px;
}

.table-container {
  overflow-x: auto;
}

.data-table {
  width: 100%;
  border-collapse: collapse;
}

.data-table th,
.data-table td {
  padding: 12px;
  border: 1px solid #eee;
  text-align: left;
  font-size: 14px;
}

.data-table th {
  background-color: #f8f9fa;
  font-weight: 600;
}

.empty-cell {
  text-align: center;
  color: #999;
}


.status-tag {
  padding: 4px 8px;
  border-radius: 4px;
  font-size: 12px;
  font-weight: 500;
  color: white;
}

.status-normal {
  background-color: #28a745;
}

.status-late {
  background-color: #fd7e14;
}

.status-early {
  background-color: #6f42c1;
}

.status-absent {
  background-color: #dc3545;
}

.status-leave {
  background-color: #0099ff;
}

.status-overtime {
  background-color: #0066cc;
}

.status-other {
  background-color: #6c757d;
}

.dialog-mask {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1000;
}

.dialog-content {
  width: 500px;
  background: white;
  border-radius: 8px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.15);
  overflow: hidden;
}

.dialog-header {
  padding: 15px 20px;
  background: #f8f9fa;
  border-bottom: 1px solid #eee;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.close-btn {
  background: none;
  border: none;
  font-size: 20px;
  color: #999;
  cursor: pointer;
  width: 30px;
  height: 30px;
  display: flex;
  justify-content: center;
  align-items: center;
}

.dialog-body {
  padding: 20px;
}

.add-employee-form {
  display: flex;
  flex-direction: column;
  gap: 15px;
}

.form-label {
  width: 90px;
  /* 统一标签宽度，包含“NFC卡号：” */
  text-align: right;
  flex-shrink: 0;
  /* 防止标签被压缩 */
  font-size: 14px;
  color: #333;
}

.input-group {
  flex: 1;
  display: flex;
  align-items: center;
  gap: 10px;
}

.small-btn {
  padding: 6px 10px;
  font-size: 12px;
}

.form-tip {
  display: block;
  margin: 5px 0 0 100px;
  /* 左缩进和标签+输入框对齐 */
  font-size: 12px;
  color: #666;
}

.dialog-footer {
  padding: 15px 20px;
  border-top: 1px solid #eee;
  display: flex;
  justify-content: flex-end;
  gap: 10px;
}

.nfc-item {
  flex-direction: column;
  align-items: flex-start;
  gap: 8px;
}

.nfc-row {
  display: flex;
  align-items: center;
  width: 100%;
  gap: 10px;
}

.nfc-item .form-label {
  width: 80px;
  text-align: right;
  margin-right: 0;
}

.form-input {
  flex: 1;
  padding: 8px 12px;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 14px;
  width: 100%;
}

.nfc-item .form-tip {
  margin-left: 90px;
  /* 和其他表单项的提示对齐 */
}

.form-label {
  width: 80px;
  text-align: right;
  flex-shrink: 0;
}

.face-tip {
  text-align: center;
  font-size: 14px;
  color: #666;
  margin-top: 10px;
}

.face-check-card {
  grid-column: 1 / -1;
}

.face-check-content {
  display: flex;
  flex-wrap: wrap;
  gap: 30px;
  align-items: flex-start;
  justify-content: center;
}

.camera-box {
  flex: 1;
  min-width: 300px;
  max-width: 500px;
}

.camera-container {
  width: 100%;
  height: 360px;
  border: 1px solid #eee;
  border-radius: 8px;
  overflow: hidden;
  background-color: #f8f9fa;
  display: flex;
  justify-content: center;
  align-items: center;
}

.camera-placeholder {
  color: #999;
  font-size: 16px;
  text-align: center;
  padding: 20px;
}

.camera-btn-group {
  margin-top: 20px;
  display: flex;
  gap: 15px;
  flex-wrap: wrap;
}

.face-check-btn {
  flex: 1;
  min-width: 120px;
  font-size: 16px;
  padding: 10px 0;
}

.face-tip-box {
  flex: 1;
  min-width: 300px;
  max-width: 400px;
}

.face-tip {
  padding: 15px;
  border-radius: 8px;
  font-size: 16px;
  text-align: center;
  margin-bottom: 20px;
}

.face-tip.normal {
  background-color: #f8f9fa;
  color: #666;
}

.face-tip.success {
  background-color: #d4edda;
  color: #155724;
}

.face-tip.error {
  background-color: #f8d7da;
  color: #721c24;
}

.face-tip.warning {
  background-color: #fff3cd;
  color: #856404;
}

.face-rule {
  border: 1px solid #eee;
  border-radius: 8px;
  padding: 20px;
}

.face-rule h4 {
  margin-top: 0;
  font-size: 16px;
  color: #333;
  margin-bottom: 10px;
}

.face-rule ul {
  padding-left: 20px;
  margin: 0;
}

.face-rule li {
  font-size: 14px;
  color: #666;
  line-height: 1.8;
  margin-bottom: 5px;
}

.mr-5 {
  margin-right: 5px;
}

/* 响应式适配 */
@media (max-width: 768px) {
  .face-check-content {
    flex-direction: column;
    align-items: center;
  }

  .camera-box,
  .face-tip-box {
    max-width: 100%;
  }
}
</style>
