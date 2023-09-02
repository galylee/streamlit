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
                st.session_state.show_login_form = True  # 显示登录表单
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
            st.session_state.username = username  # 初始化用户名
            st.session_state.show_login_form = False  # 隐藏登录表单
            st.sidebar.button("注销", key="logout-button")
            upload_file(username)
            show_files(username)
        else:
            st.error("用户名或密码错误！")

# 上传文件
def upload_file(username):
    st.header("上传文件")
    uploaded_file = st.file_uploader("选择要上传的文件")

    if uploaded_file is not None:
        file_path = f"uploads/{username}/{uploaded_file.name}"
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        with open(file_path, "wb") as f:
            f.write(uploaded_file.getvalue())

        c.execute("INSERT INTO files (username, filename) VALUES (?, ?)", (username, uploaded_file.name))
        conn.commit()
        st.success("文件上传成功！")
        st.experimental_rerun_on_run()  # 刷新文件列表

# 删除文件
def delete_file(username, filename):
    file_path = f"uploads/{username}/{filename}"
    if os.path.exists(file_path):
        os.remove(file_path)
        c.execute("DELETE FROM files WHERE username=? AND filename=?", (username, filename))
        conn.commit()
        st.success("文件删除成功！")
        st.experimental_rerun_on_run()  # 刷新文件列表
    else:
        st.error("文件不存在！")

# 显示文件列表
def show_files(username):
    st.header("已上传文件列表")
    c.execute("SELECT filename FROM files WHERE username=?", (username,))
    files = c.fetchall()
    if files:
        file_list = [file[0] for file in files]
        selected_file = st.selectbox("选择文件", file_list, key=f"file-selectbox-{username}")
        if st.button("删除文件", key="delete-button"):
            delete_file(username, selected_file)
    else:
        st.info("没有已上传的文件。")

# 主应用程序
def main():
    st.title("用户认证示例")

    if "show_login_form" not in st.session_state:
        st.session_state.show_login_form = True

    if st.session_state.show_login_form:
        login()
        st.markdown("---")
        register_button = st.button("注册")
        if register_button:
            st.session_state.show_login_form = False  # 隐藏登录表单
            register()
    else:
        if st.sidebar.button("注销", key="logout-button"):
            st.session_state.clear()
            st.session_state.show_login_form = True
        st.markdown("---")
        upload_file(st.session_state.username)
        show_files(st.session_state.username)

if __name__ == '__main__':
    main()
