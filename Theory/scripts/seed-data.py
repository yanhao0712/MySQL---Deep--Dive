import pymysql
from faker import Faker
import time

# 1. 初始配置（密码记得改！）
db_config = {
    "host": "localhost",
    "user": "root",
    "password": "123456" 
}

fake = Faker('zh_CN')

def init_db():
    # 建立一个不指定数据库的连接，先去创建库
    conn = pymysql.connect(**db_config)
    cursor = conn.cursor()
    # 如果不存在 test_db 就创建它
    cursor.execute("CREATE DATABASE IF NOT EXISTS test_db;")
    cursor.execute("USE test_db;")
    
    # 紧接着创建表
    cursor.execute("DROP TABLE IF EXISTS users")
    cursor.execute("""
        CREATE TABLE users (
            id INT AUTO_INCREMENT PRIMARY KEY,
            name VARCHAR(50),
            email VARCHAR(100),
            address TEXT,
            created_at DATETIME,
            KEY idx_email (email)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
    """)
    conn.commit()
    return conn

def batch_insert(conn, count=100000, batch_size=2000):
    cursor = conn.cursor()
    cursor.execute("USE test_db;") # 确保在 test_db 下操作
    
    print(f"🚀 开始造数，目标 {count} 条...")
    start_time = time.time()
    data = []
    for i in range(1, count + 1):
        data.append((fake.name(), fake.email(), fake.address(), fake.date_time_this_year()))
        
        if i % batch_size == 0:
            cursor.executemany(
                "INSERT INTO users (name, email, address, created_at) VALUES (%s, %s, %s, %s)", 
                data
            )
            conn.commit()
            data = []
            print(f"已插入 {i} 条...")

    print(f"✅ 任务完成！总耗时: {time.time() - start_time:.2f}s")

if __name__ == "__main__":
    # 执行初始化和插入
    connection = init_db()
    batch_insert(connection)
    connection.close()
