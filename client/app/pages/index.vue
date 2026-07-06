<template>
  <div class="login-page">
    <div class="login-card">
      <h2 class="login-title">员工考勤系统</h2>
      <form @submit.prevent="handleLogin" class="login-form">
        <div class="form-group">
          <label for="username" class="form-label">账号</label>
          <input v-model="username" type="text" id="username" class="form-input" placeholder="请输入登录账号" required />
          <div v-if="showError && !username" class="form-tip">账号不能为空</div>
        </div>
        <div class="form-group">
          <label for="password" class="form-label">密码</label>
          <input v-model="password" type="password" id="password" class="form-input" placeholder="请输入登录密码" required />
          <div v-if="showError && !password" class="form-tip">密码不能为空</div>
        </div>
        <div class="form-options">
          <label class="remember-label">
            <input v-model="rememberPwd" type="checkbox" />
            记住密码
          </label>
          <a href="javascript:void(0)" class="forgot-link">忘记密码？</a>
        </div>
        <button type="submit" class="login-btn" :disabled="loading">
          {{ loading ? '登录中...' : '登录' }}
        </button>
        <!-- 错误提示（后端返回非200时显示） -->
        <div v-if="loginError" class="login-error">{{ loginError }}</div>
      </form>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import { useRouter } from 'vue-router';
import request from './utils/request';

const router = useRouter();

// 响应式数据
const username = ref('');
const password = ref('');
const rememberPwd = ref(false);
const loading = ref(false);
const showError = ref(false);
const loginError = ref(''); // 存储后端返回的错误信息

// 页面加载时读取记住的密码（仅本地存储，不自动登录）
onMounted(() => {
  const savedUser = localStorage.getItem('savedUsername');
  const savedPwd = localStorage.getItem('savedPassword');
  if (savedUser && savedPwd) {
    username.value = savedUser;
    password.value = savedPwd;
    rememberPwd.value = true;
  }
});

// 核心登录逻辑：严格依赖后端响应
const handleLogin = async () => {
  showError.value = true;
  loginError.value = '';
  if (!username.value || !password.value) {
    return;
  }
  loading.value = true;
  try {
    const res = await request.post('/login', {
      username: username.value,
      password: password.value
    });
    // ✅ 登录成功：打印数据+存储信息+跳转，一步到位
    console.log('登录成功，后端返回数据：', res);
    localStorage.setItem('token', res.data.token);
    localStorage.setItem('currentUser', JSON.stringify(res.data.user));
    // 记住密码逻辑
    if (rememberPwd.value) {
      localStorage.setItem('savedUsername', username.value);
      localStorage.setItem('savedPassword', password.value);
    } else {
      localStorage.removeItem('savedUsername');
      localStorage.removeItem('savedPassword');
    }
    // ✅ 立即跳转，不受后续逻辑影响
    router.push('/dashboard');
  } catch (err) {
    // ❌ 只有登录失败时才执行这里
    loginError.value = err.message || '登录失败，请检查账号密码';
    console.error('登录失败：', err);
  } finally {
    // ✅ 无论成功/失败，都清空loading（关键！）
    loading.value = false;
  }
}

</script>

<style scoped>
.login-error {
  color: #ff4444;
  font-size: 13px;
  text-align: center;
  margin-top: 15px;
}

.login-page {
  min-height: 100vh;
  display: flex;
  justify-content: center;
  align-items: center;
  background: linear-gradient(120deg, #2c3e50, #4ca1af);
  padding: 20px;
}

.login-card {
  background: #fff;
  width: 100%;
  max-width: 500px;
  padding: 60px 40px;
  border: 2px solid #f0f0f0;
  border-radius: 16px;
  box-shadow: 0 12px 30px rgba(0, 0, 0, 0.18);
  margin: 0 auto;
}

.login-title {
  text-align: center;
  font-size: 28px;
  color: #333;
  margin-bottom: 40px;
  font-weight: 600;
}

.form-group {
  margin-bottom: 25px;
}

.form-label {
  display: block;
  margin-bottom: 10px;
  color: #555;
  font-size: 16px;
  font-weight: 500;
}

.form-input {
  width: 100%;
  padding: 15px 18px;
  border: 1px solid #ddd;
  border-radius: 8px;
  font-size: 16px;
  transition: border-color 0.3s;
  border-width: 1px;
}

.form-input:focus {
  outline: none;
  border-color: #4ca1af;
  box-shadow: 0 0 0 4px rgba(76, 161, 175, 0.1);
}

.form-tip {
  color: #ff4444;
  font-size: 13px;
  margin-top: 8px;
}

.form-options {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 30px;
  font-size: 15px;
}

.remember-label {
  color: #555;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 8px;
}

.forgot-link {
  color: #4ca1af;
  text-decoration: none;
  font-size: 15px;
}

.forgot-link:hover {
  text-decoration: underline;
}

.login-btn {
  width: 100%;
  padding: 16px;
  background: linear-gradient(to right, #2c3e50, #4ca1af);
  color: #fff;
  border: none;
  border-radius: 8px;
  font-size: 18px;
  cursor: pointer;
  transition: opacity 0.3s;
  border: 1px solid transparent;
}

.login-btn:hover:not(:disabled) {
  opacity: 0.9;
  border-color: #3a8b99;
}

.login-btn:disabled {
  background: #ccc;
  cursor: not-allowed;
}

@media (max-width: 520px) {
  .login-card {
    padding: 40px 25px;
    max-width: 100%;
  }

  .login-title {
    font-size: 24px;
  }

  .form-input {
    padding: 12px 15px;
  }

  .login-btn {
    padding: 14px;
    font-size: 16px;
  }
}
</style>