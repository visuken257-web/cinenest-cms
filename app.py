# MovieNest CMS - Hệ thống CMS Cá nhân Bàn luận & Đánh giá Phim
# Kế thừa đầy đủ kiến trúc Chapter 8:
#   - Identity qua Avatar Gravatar (MD5 hash)
#   - Follow (self-referential many-to-many), Trang chủ cá nhân hoá với Cookie 'show_followed'
#   - Đánh giá phim kèm chấm điểm từ 1 đến 10 điểm, Markdown + Sanitize (bleach) chống XSS
#   - Danh sách & Trang chi tiết phim hiển thị hình ảnh poster
#   - Đăng nhập, Đăng ký tài khoản đầy đủ + Đăng nhập nhanh cho demo
#   - Blog/CMS bàn luận chuyên sâu, phân trang (paginate)
#   - Nhật ký sử dụng AI (/ai-log)

import os
import sys
from flask import (
    Flask, render_template, redirect, url_for, request,
    flash, make_response, abort, send_from_directory
)
from flask_bootstrap import Bootstrap
from flask_login import (
    LoginManager, login_required, current_user, login_user, logout_user
)

from models import (
    db, User, Role, Follow, Genre, Movie, MovieReview, BlogPost, Permission
)
from markdown_utils import render_markdown, COMMENT_ALLOWED_TAGS

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
# Hỗ trợ tìm db_config ở cả ../shared và thư mục hiện tại
sys.path.insert(0, os.path.join(BASE_DIR, "..", "shared"))
sys.path.insert(0, BASE_DIR)
from db_config import get_database_uri  # noqa: E402

DB_NAME = "BookNest_Ch08"

STATIC_DIR = os.path.join(BASE_DIR, "static")
TEMPLATE_DIR = os.path.join(BASE_DIR, "templates")

app = Flask(__name__, static_folder=STATIC_DIR, template_folder=TEMPLATE_DIR)
Bootstrap(app)

@app.route("/static/<path:filename>")
def serve_static(filename):
    """Phục vụ file tĩnh (posters, css, js) tương thích hoàn toàn môi trường Vercel."""
    return send_from_directory(STATIC_DIR, filename)

app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "cinenest-dev-secret-key-2026")
app.config["SQLALCHEMY_DATABASE_URI"] = get_database_uri(DB_NAME)
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db.init_app(app)

# Tự động khởi tạo bảng và dữ liệu mẫu nếu chưa có (cần thiết cho Cloud Serverless / Vercel / SQLite)
with app.app_context():
    try:
        db.create_all()
        from seed_community import seed_data
        seed_data(app, db)
    except Exception as e:
        print(f"[Notice] Auto-init database notice: {e}")

login_manager = LoginManager()
login_manager.login_view = "login"
login_manager.login_message = "Vui lòng đăng nhập để thực hiện chức năng này."
login_manager.login_message_category = "warning"
login_manager.init_app(app)


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


# ==============================================================================
# 1. HỆ THỐNG XÁC THỰC: ĐĂNG KÝ, ĐĂNG NHẬP, ĐĂNG XUẤT & QUICK-LOGIN
# ==============================================================================
@app.route("/register", methods=["GET", "POST"])
def register():
    """Tạo tài khoản mới đầy đủ."""
    if current_user.is_authenticated:
        return redirect(url_for("home"))

    if request.method == "POST":
        username = request.form.get("username", "").strip()
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        confirm_password = request.form.get("confirm_password", "")

        errors = []
        if not username or len(username) < 3:
            errors.append("Tên đăng nhập phải có ít nhất 3 ký tự.")
        if not email or "@" not in email:
            errors.append("Email không hợp lệ.")
        if not password or len(password) < 6:
            errors.append("Mật khẩu phải có ít nhất 6 ký tự.")
        if password != confirm_password:
            errors.append("Mật khẩu xác nhận không khớp.")

        if User.query.filter_by(username=username).first():
            errors.append("Tên đăng nhập đã được sử dụng.")
        if User.query.filter_by(email=email).first():
            errors.append("Email đã được đăng ký.")

        if errors:
            for err in errors:
                flash(err, "danger")
            return render_template("register.html", username=username, email=email)

        # Mặc định gán vai trò Member
        member_role = Role.query.filter_by(name="Member").first()
        new_user = User(
            username=username,
            email=email,
            is_verified=True,
            role=member_role
        )
        new_user.set_password(password)
        db.session.add(new_user)
        db.session.commit()

        login_user(new_user)
        flash(f"Chúc mừng {username}! Tài khoản của bạn đã được tạo thành công.", "success")
        return redirect(url_for("home"))

    return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    """Đăng nhập bằng Username/Email và Mật khẩu."""
    if current_user.is_authenticated:
        return redirect(url_for("home"))

    if request.method == "POST":
        identifier = request.form.get("identifier", "").strip()
        password = request.form.get("password", "")
        remember = bool(request.form.get("remember"))

        # Tìm theo username hoặc email
        user = User.query.filter(
            (User.username == identifier) | (User.email == identifier.lower())
        ).first()

        if user and user.check_password(password):
            login_user(user, remember=remember)
            flash(f"Chào mừng trở lại, {user.username}!", "success")
            next_page = request.args.get("next")
            return redirect(next_page or url_for("home"))
        else:
            flash("Tên đăng nhập hoặc mật khẩu không chính xác.", "danger")

    return render_template("login.html")


@app.route("/logout")
def logout():
    """Đăng xuất khỏi hệ thống."""
    logout_user()
    flash("Bạn đã đăng xuất thành công.", "info")
    return redirect(url_for("home"))


@app.route("/quick-login/<username>")
def quick_login(username):
    """Đăng nhập nhanh tiện lợi cho demo giảng đường."""
    user = User.query.filter_by(username=username).first_or_404()
    login_user(user)
    flash(f"Đã đăng nhập nhanh với tài khoản '{username}' (demo).", "success")
    return redirect(url_for("home"))


# ==============================================================================
# 2. TRANG CHỦ & CÁ NHÂN HOÁ BẰNG COOKIE
# ==============================================================================
@app.route("/")
def home():
    """Trang chủ: Top phim điểm cao + Bài thảo luận cá nhân hoá qua cookie show_followed."""
    show_param = request.args.get("show")
    if show_param in ("followed", "all"):
        show_followed = (show_param == "followed")
    else:
        show_followed = request.cookies.get("show_followed", "0") == "1"

    # Lấy danh sách phim nổi bật (top 6 phim có điểm cao nhất)
    all_movies = Movie.query.all()
    # Sắp xếp theo average_rating giảm dần, nếu chưa có rating thì xếp sau
    top_movies = sorted(
        all_movies,
        key=lambda m: (m.average_rating is not None, m.average_rating or 0, m.review_count),
        reverse=True
    )[:6]

    # Danh sách bài viết blog bàn luận
    if current_user.is_authenticated and show_followed:
        posts = current_user.followed_posts.all()
    else:
        posts = BlogPost.query.order_by(BlogPost.created_at.desc()).all()

    resp = make_response(render_template(
        "home.html",
        top_movies=top_movies,
        posts=posts,
        show_followed=show_followed
    ))

    if show_param in ("followed", "all"):
        resp.set_cookie("show_followed", "1" if show_followed else "0", max_age=30 * 24 * 3600)
    return resp


# ==============================================================================
# 3. DANH SÁCH PHIM, CHI TIẾT & ĐÁNH GIÁ (CHẤM ĐIỂM 1 - 10)
# ==============================================================================
@app.route("/movies")
def movie_list():
    """Danh sách phim có tìm kiếm và lọc theo thể loại."""
    genre_id = request.args.get("genre", type=int)
    search_query = request.args.get("q", "").strip()

    query = Movie.query
    if genre_id:
        query = query.filter_by(genre_id=genre_id)
    if search_query:
        query = query.filter(
            (Movie.title.ilike(f"%{search_query}%")) |
            (Movie.director.ilike(f"%{search_query}%"))
        )

    movies = query.order_by(Movie.release_year.desc()).all()
    genres = Genre.query.all()
    return render_template(
        "movie_list.html",
        movies=movies,
        genres=genres,
        current_genre=genre_id,
        search_query=search_query
    )


@app.route("/movies/<int:movie_id>")
def movie_detail(movie_id):
    """Trang chi tiết phim: Hiện poster to, thông tin, điểm trung bình và các đánh giá."""
    movie = Movie.query.get_or_404(movie_id)
    # Lấy đánh giá của người dùng hiện tại nếu đã đăng nhập
    user_review = None
    if current_user.is_authenticated:
        user_review = MovieReview.query.filter_by(
            movie_id=movie.id, author_id=current_user.id
        ).first()

    return render_template(
        "movie_detail.html",
        movie=movie,
        user_review=user_review
    )


@app.route("/movies/<int:movie_id>/reviews", methods=["POST"])
@login_required
def add_review(movie_id):
    """Gửi đánh giá phim: Điểm số từ 1 đến 10 + Bình luận Markdown đã sanitize chống XSS."""
    movie = Movie.query.get_or_404(movie_id)

    try:
        rating = int(request.form.get("rating", 10))
        if rating < 1 or rating > 10:
            rating = 10
    except (ValueError, TypeError):
        rating = 10

    body_md = request.form.get("body_md", "").strip()
    if not body_md:
        flash("Nội dung đánh giá không được để trống.", "warning")
        return redirect(url_for("movie_detail", movie_id=movie_id))

    # Sanitize nội dung Markdown chống XSS bằng bleach
    body_html = render_markdown(body_md, allowed_tags=COMMENT_ALLOWED_TAGS)

    # Kiểm tra xem user đã từng đánh giá phim này chưa
    existing_review = MovieReview.query.filter_by(
        movie_id=movie.id, author_id=current_user.id
    ).first()

    if existing_review:
        existing_review.rating = rating
        existing_review.body_md = body_md
        existing_review.body_html = body_html
        flash(f"Đã cập nhật đánh giá của bạn ({rating}/10 điểm) cho phim '{movie.title}'.", "success")
    else:
        new_review = MovieReview(
            movie_id=movie.id,
            author_id=current_user.id,
            rating=rating,
            body_md=body_md,
            body_html=body_html
        )
        db.session.add(new_review)
        flash(f"Đã gửi đánh giá ({rating}/10 điểm) cho phim '{movie.title}'. Cảm ơn bạn!", "success")

    db.session.commit()
    return redirect(url_for("movie_detail", movie_id=movie_id))


# Route tương thích ngược với Chapter 8 gốc
@app.route("/books/<int:book_id>/comments", methods=["GET", "POST"])
def book_comments(book_id):
    """Tương thích ngược route cũ sang movie_detail."""
    return redirect(url_for("movie_detail", movie_id=book_id))


# ==============================================================================
# 4. TRANG CÁ NHÂN & THEO DÕI (FOLLOW / UNFOLLOW)
# ==============================================================================
@app.route("/users/<username>")
def profile(username):
    """Trang cá nhân: Avatar Gravatar, danh sách review, follower/following."""
    user = User.query.filter_by(username=username).first_or_404()
    is_following = current_user.is_authenticated and current_user.is_following(user)
    followers_count = Follow.query.filter_by(followed_id=user.id).count()
    following_count = Follow.query.filter_by(follower_id=user.id).count()

    # Các đánh giá phim của người này
    user_reviews = MovieReview.query.filter_by(author_id=user.id).order_by(
        MovieReview.created_at.desc()
    ).all()

    return render_template(
        "profile.html",
        user=user,
        is_following=is_following,
        followers_count=followers_count,
        following_count=following_count,
        user_reviews=user_reviews
    )


@app.route("/users/<username>/follow", methods=["POST"])
@login_required
def toggle_follow(username):
    """Theo dõi / Bỏ theo dõi người dùng."""
    user = User.query.filter_by(username=username).first_or_404()
    if user.id == current_user.id:
        flash("Bạn không thể tự theo dõi chính mình.", "warning")
        return redirect(url_for("profile", username=username))

    if current_user.is_following(user):
        current_user.unfollow(user)
        flash(f"Đã bỏ theo dõi @{username}.", "info")
    else:
        current_user.follow(user)
        flash(f"Đã theo dõi @{username}.", "success")
    db.session.commit()
    return redirect(url_for("profile", username=username))


# ==============================================================================
# 5. BLOG / BÀN LUẬN CHUYÊN SÂU & PHÂN TRANG (PAGINATE)
# ==============================================================================
@app.route("/blog")
def blog_list():
    """Danh sách bài viết phân tích phim có phân trang."""
    page = request.args.get("page", 1, type=int)
    posts = BlogPost.query.order_by(
        BlogPost.created_at.desc()
    ).paginate(page=page, per_page=3, error_out=False)
    return render_template("blog_list.html", posts=posts)


@app.route("/blog/<int:post_id>")
def blog_detail(post_id):
    """Chi tiết bài viết bàn luận phim."""
    post = BlogPost.query.get_or_404(post_id)
    return render_template("blog_detail.html", post=post)


@app.route("/blog/new", methods=["GET", "POST"])
@login_required
def blog_new():
    """Viết bài bàn luận phim mới (Hỗ trợ Markdown đầy đủ)."""
    if request.method == "POST":
        title = request.form.get("title", "").strip()
        body_md = request.form.get("body_md", "").strip()
        movie_id = request.form.get("movie_id", type=int)

        if not title:
            flash("Vui lòng nhập tiêu đề bài viết.", "warning")
            return redirect(url_for("blog_new"))
        if not body_md:
            flash("Vui lòng nhập nội dung bài viết.", "warning")
            return redirect(url_for("blog_new"))

        body_html = render_markdown(body_md)
        post = BlogPost(
            title=title,
            body_md=body_md,
            body_html=body_html,
            author_id=current_user.id,
            movie_id=movie_id if movie_id else None
        )
        db.session.add(post)
        db.session.commit()
        flash("Đã đăng bài viết bàn luận mới thành công!", "success")
        return redirect(url_for("blog_detail", post_id=post.id))

    movies = Movie.query.order_by(Movie.title).all()
    return render_template("blog_new.html", movies=movies)


# ==============================================================================
# 6. NHẬT KÝ SỬ DỤNG AI (COPILOT LOG)
# ==============================================================================
@app.route("/ai-log")
def ai_log():
    """Hiển thị ai_demo/copilot_log.md dưới dạng HTML."""
    import markdown
    path = os.path.join(os.path.dirname(__file__), "ai_demo", "copilot_log.md")
    with open(path, encoding="utf-8") as f:
        html = markdown.markdown(f.read(), extensions=["fenced_code"])
    return render_template("ai_log.html", content=html)


if __name__ == "__main__":
    app.run(debug=True)
