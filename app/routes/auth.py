from datetime import datetime
from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_user, logout_user, login_required, current_user
from app.extensions import db
from app.models import User

auth_bp = Blueprint('auth', __name__, template_folder='../templates')


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('users.dashboard'))

    if request.method == 'POST':
        username = request.form['username'].strip()
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user and user.check_password(password):
            if not user.is_active:
                flash('Tài khoản đã bị khóa.', 'danger')
            else:
                user.last_login = datetime.now()
                db.session.commit()
                login_user(user)
                next_page = request.args.get('next')
                flash('Đăng nhập thành công!', 'success')
                return redirect(next_page or url_for('users.dashboard'))
        flash('Sai tên đăng nhập hoặc mật khẩu.', 'danger')
    return render_template('auth/login.html')


@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Đã đăng xuất.', 'info')
    return redirect(url_for('auth.login'))


@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('users.dashboard'))

    if request.method == 'POST':
        username = request.form['username'].strip()
        password = request.form['password']
        confirm = request.form.get('confirm', '')
        full_name = request.form.get('full_name', '').strip()
        email = request.form.get('email', '').strip()

        if not username or not password:
            flash('Vui lòng nhập đầy đủ thông tin.', 'danger')
        elif password != confirm:
            flash('Mật khẩu xác nhận không khớp.', 'danger')
        elif User.query.filter_by(username=username).first():
            flash('Tên đăng nhập đã tồn tại.', 'danger')
        else:
            user = User(username=username, full_name=full_name, email=email, role='user')
            user.set_password(password)
            db.session.add(user)
            db.session.commit()
            flash('Đăng ký thành công! Hãy đăng nhập.', 'success')
            return redirect(url_for('auth.login'))

    return render_template('auth/register.html')


@auth_bp.route('/change-password', methods=['GET', 'POST'])
@login_required
def change_password():
    if request.method == 'POST':
        current_pw = request.form.get('current_password', '')
        new_pw = request.form.get('new_password', '')
        confirm = request.form.get('confirm_password', '')

        if not current_user.check_password(current_pw):
            flash('Mật khẩu hiện tại không đúng.', 'danger')
        elif not new_pw:
            flash('Vui lòng nhập mật khẩu mới.', 'danger')
        elif new_pw != confirm:
            flash('Mật khẩu xác nhận không khớp.', 'danger')
        elif current_pw == new_pw:
            flash('Mật khẩu mới phải khác mật khẩu hiện tại.', 'danger')
        else:
            current_user.set_password(new_pw)
            db.session.commit()
            flash('Đổi mật khẩu thành công!', 'success')
            return redirect(url_for('users.dashboard'))

    return render_template('auth/change_password.html')
