import streamlit as st
import sqlite3
import hashlib
import os

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
    username_input = st.empty()
    password_input = st.empty()
    confirm_password_input = st.empty()

    username = username_input.text_input("用户名", key="register-username")
    password = password_input.text_input("密码", type="password", key="register-password")
    confirm_password = confirm_password_input.text_input("确认密码", type="password", key="register-confirm-password")

    if st.button("注册", key="register-button"):
        if password == confirm_password:
            password_hash = hashlib.sha256(password.encode()).hexdigest()
            try:
                c.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, password_hash))
                conn.commit()
                st.success("注册成功！")
                username_input.empty()
                password_input.empty()
                confirm_password_input.empty()
                login_form.empty()  # 隐藏登陆表单
            except sqlite3.IntegrityError:
                st.error("用户名已存在！")
        else:
            st.error("密码不匹配！")

# 登录页面
def login():
    st.header("用户登录")
    username = st.text_input("用户名")
    password = st.text_input("密码", type="password")

    if st.button("登录", key="login-button"):
        password_hash = hashlib.sha256(password.encode()).hexdigest()
        c.execute("SELECT * FROM users WHERE username=? AND password=?", (username, password_hash))
        result = c.fetchone()
        if result:
            st.success("登录成功！")
            upload_file()
            show_files()
        else:
            st.error("用户名或密码错误！")

# 上传文件
def upload_file():
    st.header("上传文件")
    uploaded_file = st.file_uploader("选择要上传的文件")

    if uploaded_file is not None:
        file_path = f"uploads/{uploaded_file.name}"
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        with open(file_path, "wb") as f:
            f.write(uploaded_file.getvalue())

        c.execute("INSERT INTO files (username, filename) VALUES (?, ?)", (uploaded_file.name, uploaded_file.name))
        conn.commit()
        st.success("文件上传成功！")

# 删除文件
def delete_file(filename):
    file_path = f"uploads/{filename}"
    if os.path.exists(file_path):
        os.remove(file_path)
        c.execute("DELETE FROM files WHERE username=? AND filename=?", (filename, filename))
        conn.commit()
        st.success("文件删除成功！")
    else:
        st.error("文件不存在！")

# 显示文件列表
def show_files():
    st.header("已上传文件列表")
    c.execute("SELECT filename FROM files")
    files = c.fetchall()
    if files:
        file_list = [file[0] for file in files]
        selected_file = st.selectbox("选择文件", file_list)
        if st.button("删除文件", key="delete-button"):
            delete_file(selected_file)
            show_files()
    else:
        st.info("没有已上传的文件。")

# 主应用程序
def main():
    st.title("用户认证示例")

    with st.form(key="login-form"):
        login_form = st.form_submit_button("登录")
        if login_form:
            login()
        st.form_submit_button("注册", on_click=register)

    if st.button("刷新"):
        st.experimental_rerun()

if __name__ == '__main__':
    main()
