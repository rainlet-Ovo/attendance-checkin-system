import axios from 'axios';
// 若使用Element Plus，引入提示组件
import { ElMessage } from 'element-plus';

const request = axios.create({
  baseURL: 'http://localhost:8080/api',
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json'
  }
});

// 请求拦截器：添加token
request.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    console.error('请求发送失败：', error);
    //ElMessage.error('请求发送失败，请检查网络');
    return Promise.reject(error);
  }
);

// 响应拦截器
request.interceptors.response.use(
  (response) => {
    const res = response.data;
    if (res.code !== 200) {
      //ElMessage.error(res.message || '操作失败');
      return Promise.reject(new Error(res.message || '操作失败'));
    }
    // 可选：成功提示（根据业务需求）
    // ElMessage.success(res.message || '操作成功');
    return res;
  },
  (error) => {
    const errMsg = error.response?.data?.message || '服务器异常，请稍后重试';
    console.error('响应错误：', errMsg);
    // token过期/无效，跳转登录页
    if (errMsg.includes('token无效') || errMsg.includes('未登录')) {
      localStorage.clear();
      window.location.href = '/'; // 强制跳转登录页
    }
    //ElMessage.error(errMsg);
    return Promise.reject(new Error(errMsg));
  }
);

export default request;