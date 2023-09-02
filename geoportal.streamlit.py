import streamlit as st
import sqlite3
import hashlib
import os
import pandas as pd

# 创建或连接到SQLite数据库
conn = sqlite3.connect('user.db')
c = conn.cursor()

# 创建用户表
c.execute('''
    CREATE TABLE IF NOT EXISTS users (
        username TEXT PRIMARY KEY,
        password TEXT
    )
''')
conn.commit()

# 创建文件表
c.execute('''
    CREATE TABLE IF NOT EXISTS files (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT,
        filename TEXT
    )
''')
conn.commit()

# 注册页面
def register():
    st.header("用户注册")
    username = st.text_input("用户名")
    password = st.text_input("密码", type="password")
    confirm_password = st.text_input("确认密码", type="password")

    if st.button("注册"):
        if password == confirm_password:
            password_hash = hashlib.sha256(password.encode()).hexdigest()
            try:
                c.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, password_hash))
                conn.commit()
                st.success("注册成功！")
            except sqlite3.IntegrityError:
                st.error("用户名已存在！")
        else:
            st.error("密码不匹配！")

# 登录页面
def login():
    st.header("用户登录")
    username = st.text_input("用户名")
    password = st.text_input("密码", type="password")

    if st.button("登录"):
        password_hash = hashlib.sha256(password.encode()).hexdigest()
        c.execute("SELECT * FROM users WHERE username=? AND password=?", (username, password_hash))
        result = c.fetchone()
        if result:
            st.success("登录成功！")
            upload_file(username)
            show_files(username)
        else:
            st.error("用户名或密码错误！")

# 上传文件
def upload_file(username):
    st.header("上传文件")
    uploaded_file = st.file_uploader("选择要上传的CSV文件", type="csv")

    if uploaded_file is not None:
        file_path = f"uploads/{username}/{uploaded_file.name}"
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        with open(file_path, "wb") as f:
            f.write(uploaded_file.getvalue())

        c.execute("INSERT INTO files (username, filename) VALUES (?, ?)", (username, uploaded_file.name))
        conn.commit()
        st.success("文件上传成功！")

# 删除文件
def delete_file(username, filename):
    file_path = f"uploads/{username}/{filename}"
    if os.path.exists(file_path):
        os.remove(file_path)
        c.execute("DELETE FROM files WHERE username=? AND filename=?", (username, filename))
        conn.commit()
        st.success("文件删除成功！")
    else:
        st.error("文件不存在！")

# 显示文件列表
def show_files(username):
    st.header("已上传文件列表")
    c.execute("SELECT filename FROM files WHERE username=?", (username,))
    files = c.fetchall()
    if files:
        file_list = [file[0] for file in files]
        selected_file = st.selectbox("选择文件", file_list)
        if st.button("删除文件"):
            delete_file(username, selected_file)
            show_files(username)
    else:
        st.info("没有已上传的文件。")

# 主应用程序
def main():
    st.title("用户认证示例")
    menu = ["登录", "注册"]
    choice = st.sidebar.selectbox("选择操作", menu)

    if choice == "登录":
        login()
    elif choice == "注册":
        register()

if __name__ == '__main__':
    main()
