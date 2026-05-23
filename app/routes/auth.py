from datetime import datetime
from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app
from flask_login import login_user, logout_user, login_required, current_user
from sqlalchemy import or_
from app.extensions import db
from app.models import User
from app.utils import log_activity
from app.oauth import oauth

auth_bp = Blueprint('auth', __name__, template_folder='../templates')


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('users.dashboard'))

    if request.method == 'POST':
        username = request.form['username'].strip()
        password = request.form['password']
        user = User.query.filter(
            or_(User.username == username, User.email == username)
        ).first()
        if user and user.check_password(password):
            if not user.is_active:
                flash('Tài khoản đã bị khóa.', 'danger')
            else:
                user.last_login = datetime.now()
                db.session.commit()
                log_activity('login', 'user', user.id)
                login_user(user)
                next_page = request.args.get('next')
                flash('Đăng nhập thành công!', 'success')
                return redirect(next_page or url_for('users.dashboard'))
        flash('Sai tên đăng nhập hoặc mật khẩu.', 'danger')
    return render_template('auth/login.html')


@auth_bp.route('/logout')
@login_required
def logout():
    log_activity('logout', 'user', current_user.id)
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


@auth_bp.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    if request.method == 'POST':
        full_name = request.form.get('full_name', '').strip()
        email = request.form.get('email', '').strip()
        phone = request.form.get('phone', '').strip()
        if full_name:
            current_user.full_name = full_name
        current_user.email = email
        current_user.phone = phone
        db.session.commit()
        flash('Cập nhật hồ sơ thành công!', 'success')
        return redirect(url_for('auth.profile'))
    return render_template('auth/profile.html')


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


@auth_bp.route('/login/google')
def google_login():
    if not current_app.config.get('OAUTH_ENABLED'):
        flash('Đăng nhập bằng Google chưa được cấu hình.', 'warning')
        return redirect(url_for('auth.login'))

    redirect_uri = url_for('auth.google_callback', _external=True)
    return oauth.google.authorize_redirect(redirect_uri)


@auth_bp.route('/login/google/callback')
def google_callback():
    if not current_app.config.get('OAUTH_ENABLED'):
        flash('Đăng nhập bằng Google chưa được cấu hình.', 'warning')
        return redirect(url_for('auth.login'))

    try:
        token = oauth.google.authorize_access_token()
        userinfo = token.get('userinfo')
        if not userinfo:
            userinfo = oauth.google.parse_id_token(token)

        google_id = userinfo.get('sub')
        email = userinfo.get('email', '')
        name = userinfo.get('name', '') or userinfo.get('given_name', '')

        if not google_id:
            flash('Không thể xác thực với Google.', 'danger')
            return redirect(url_for('auth.login'))

        # Check if google_id exists
        user = User.query.filter_by(google_id=google_id).first()
        if user:
            if not user.is_active:
                flash('Tài khoản đã bị khóa.', 'danger')
                return redirect(url_for('auth.login'))
            user.last_login = datetime.now()
            db.session.commit()
            log_activity('login', 'user', user.id)
            login_user(user)
            flash('Đăng nhập thành công!', 'success')
            return redirect(url_for('users.dashboard'))

        # Check if email exists (link account)
        if email:
            user = User.query.filter_by(email=email).first()
            if user:
                user.google_id = google_id
                if not user.full_name and name:
                    user.full_name = name
                user.last_login = datetime.now()
                db.session.commit()
                log_activity('login', 'user', user.id)
                login_user(user)
                flash('Đã liên kết tài khoản Google!', 'success')
                return redirect(url_for('users.dashboard'))

        # Create new user
        username = email.split('@')[0] if email else f'google_{google_id[:8]}'
        base_username = username
        counter = 1
        while User.query.filter_by(username=username).first():
            username = f'{base_username}{counter}'
            counter += 1

        from app.permissions import get_default_permissions
        import json
        user = User(
            username=username,
            full_name=name or '',
            email=email,
            google_id=google_id,
            role='user',
            permissions=json.dumps(
                list(get_default_permissions('user')),
                ensure_ascii=False),
        )
        user.set_password('')  # No password needed for Google users
        db.session.add(user)
        db.session.commit()
        log_activity('login', 'user', user.id)
        login_user(user)
        flash('Đăng nhập bằng Google thành công!', 'success')
        return redirect(url_for('users.dashboard'))

    except Exception as e:
        current_app.logger.error(f'Google OAuth error: {e}')
        flash('Có lỗi xảy ra khi đăng nhập bằng Google.', 'danger')
        return redirect(url_for('auth.login'))
