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
def login(session):
    st.header("用户登录")
    username = st.text_input("用户名")
    password = st.text_input("密码", type="password")

    if st.button("登录"):
        password_hash = hashlib.sha256(password.encode()).hexdigest()
        c.execute("SELECT * FROM users WHERE username=? AND password=?", (username, password_hash))
        result = c.fetchone()
        if result:
            session.logged_in = True
            session.username = username
            st.success("登录成功！")
            upload_file(session)
            show_files(session)
        else:
            st.error("用户名或密码错误！")

# 上传文件
def upload_file(session):
    st.header("上传文件")
    uploaded_file = st.file_uploader("选择要上传的CSV文件")

    if uploaded_file is not None:
        file_path = f"uploads/{session.username}/{uploaded_file.name}"
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        with open(file_path, "wb") as f:
            f.write(uploaded_file.getvalue())

        c.execute("INSERT INTO files (username, filename) VALUES (?, ?)", (session.username, uploaded_file.name))
        conn.commit()
        st.success("文件上传成功！")

# 删除文件
def delete_file(session, filename):
    file_path = f"uploads/{session.username}/{filename}"
    if os.path.exists(file_path):
        os.remove(file_path)
        c.execute("DELETE FROM files WHERE username=? AND filename=?", (session.username, filename))
        conn.commit()
        st.success("文件删除成功！")
    else:
        st.error("文件不存在！")

# 显示文件列表
def show_files(session):
    st.header("已上传文件列表")
    c.execute("SELECT filename FROM files WHERE username=?", (session.username,))
    files = c.fetchall()
    if files:
        file_list = [file[0] for file in files]
        selected_file = st.selectbox("选择文件", file_list)
        if st.button("删除文件"):
            delete_file(session, selected_file)
            show_files(session)
    else:
        st.info("没有已上传的文件。")

# 注销
def logout(session):
    session.logged_in = False
    session.username = None

# 主应用程序
def main():
    session_state = st.session_state

    st.title("用户认证示例")

    if "logged_in" not in session_state:
        session_state.logged_in = False
        session_state.username = None

    if not session_state.logged_in:
        login(session_state)
        st.sidebar.empty()
    else:
        st.sidebar.button("注销", on_click=logout, args=(session_state,))
        upload_file(session_state)
        show_files(session_state)

if __name__ == '__main__':
    main()
