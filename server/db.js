const mysql = require('mysql2/promise');
require('dotenv').config();

// 数据库配置（读取.env文件）
const dbConfig = {
  host: process.env.DB_HOST || 'localhost',
  user: process.env.DB_USER || 'root',
  password: process.env.DB_PASSWORD || '',
  database: process.env.DB_NAME || 'attendanceManagementSystem',
  connectionLimit: 10,
  waitForConnections: true,
  charset: 'utf8mb4',
  timezone: '+08:00',
  multipleStatements: true // ✅ 新增：允许执行多条SQL语句
};

// 创建数据库连接池
const pool = mysql.createPool(dbConfig);

// 测试数据库连接
async function testDbConnection() {
  try {
    const connection = await pool.getConnection();
    console.log('✅ 数据库连接成功！');
    connection.release();
  } catch (err) {
    console.error('❌ 数据库连接失败：', err.message);
    process.exit(1); // 连接失败则退出程序
  }
}

// 暴露连接池
module.exports = {
  pool,
  testDbConnection
};