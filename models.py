# MovieNest CMS - Data Models (SQL Server + SQLAlchemy)
# Ke thua kien truc Chapter 8: User, Role, Follow, BlogPost, va bo sung Movie, Genre, MovieReview (1-10 diem)

import hashlib
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from itsdangerous import URLSafeTimedSerializer

db = SQLAlchemy()


class Permission:
    """Bit flags - moi quyen la 1 bit rieng, ket hop bang OR (|) de tao Role."""
    VIEW = 1        # 00001 - xem phim, xem review, xem blog
    REVIEW = 2      # 00010 - viet danh gia (cham diem 1-10 + review)
    WRITE_POST = 4  # 00100 - viet bai blog/phan tich phim
    MODERATE = 8    # 01000 - kiem duyet noi dung
    ADMIN = 16      # 10000 - toan quyen quan tri


class Role(db.Model):
    __tablename__ = "roles"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.Unicode(30), unique=True, nullable=False)
    permissions = db.Column(db.Integer, nullable=False, default=0)

    users = db.relationship("User", back_populates="role")

    def add_permission(self, perm):
        if not self.has_permission(perm):
            self.permissions += perm

    def has_permission(self, perm):
        return (self.permissions & perm) == perm

    @staticmethod
    def insert_roles():
        roles = {
            "Member": (Permission.VIEW | Permission.REVIEW, True),
            "Critic": (Permission.VIEW | Permission.REVIEW | Permission.WRITE_POST, False),
            "Admin": (Permission.VIEW | Permission.REVIEW | Permission.WRITE_POST |
                      Permission.MODERATE | Permission.ADMIN, False),
            # Giu them Customer va Seller de tuong thich code demo cu
            "Customer": (Permission.VIEW | Permission.REVIEW, False),
            "Seller": (Permission.VIEW | Permission.REVIEW | Permission.WRITE_POST, False),
        }
        for name, (perms, is_default) in roles.items():
            role = Role.query.filter_by(name=name).first()
            if role is None:
                role = Role(name=name)
            role.permissions = perms
            db.session.add(role)
        db.session.commit()

    def __repr__(self):
        return f"<Role {self.name}>"


class User(UserMixin, db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.Unicode(120), unique=True, nullable=False, index=True)
    username = db.Column(db.Unicode(50), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.Unicode(255), nullable=False)
    is_verified = db.Column(db.Boolean, nullable=False, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    role_id = db.Column(db.Integer, db.ForeignKey("roles.id"))
    role = db.relationship("Role", back_populates="users")

    reviews = db.relationship("MovieReview", back_populates="author", lazy="select")
    blog_posts = db.relationship("BlogPost", back_populates="author", lazy="select")

    def can(self, perm):
        return self.role is not None and self.role.has_permission(perm)

    def is_admin(self):
        return self.can(Permission.ADMIN)

    def gravatar_url(self, size=80):
        email_hash = hashlib.md5(self.email.strip().lower().encode("utf-8")).hexdigest()
        return f"https://www.gravatar.com/avatar/{email_hash}?d=identicon&s={size}"

    # Quan he Follow (self-referential many-to-many tren User)
    def follow(self, user):
        if not self.is_following(user) and user.id != self.id:
            db.session.add(Follow(follower_id=self.id, followed_id=user.id))

    def unfollow(self, user):
        f = Follow.query.filter_by(follower_id=self.id, followed_id=user.id).first()
        if f:
            db.session.delete(f)

    def is_following(self, user):
        return Follow.query.filter_by(follower_id=self.id, followed_id=user.id).first() is not None

    @property
    def followed_posts(self):
        # JOIN Follow + BlogPost: lay bai viet cua nhung nguoi minh dang follow
        return (BlogPost.query
                .join(Follow, Follow.followed_id == BlogPost.author_id)
                .filter(Follow.follower_id == self.id)
                .order_by(BlogPost.created_at.desc()))

    def set_password(self, raw_password):
        self.password_hash = generate_password_hash(raw_password)

    def check_password(self, raw_password):
        return check_password_hash(self.password_hash, raw_password)

    def generate_token(self, secret_key, salt="email-verify", expires_in=3600):
        s = URLSafeTimedSerializer(secret_key)
        return s.dumps({"user_id": self.id}, salt=salt)

    @staticmethod
    def verify_token(token, secret_key, salt="email-verify", max_age=3600):
        s = URLSafeTimedSerializer(secret_key)
        try:
            data = s.loads(token, salt=salt, max_age=max_age)
        except Exception:
            return None
        return User.query.get(data.get("user_id"))

    def __repr__(self):
        return f"<User {self.username}>"


class Follow(db.Model):
    """Bang lien ket self-referential many-to-many tren User (A follow B)."""
    __tablename__ = "follows"

    follower_id = db.Column(db.Integer, db.ForeignKey("users.id"), primary_key=True)
    followed_id = db.Column(db.Integer, db.ForeignKey("users.id"), primary_key=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class Genre(db.Model):
    """The loai phim (Hanh dong, Chien tranh, Co trang, Hoat hinh, Chinh kich,...)."""
    __tablename__ = "genres"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.Unicode(80), unique=True, nullable=False, index=True)
    movies = db.relationship("Movie", back_populates="genre", lazy="select")

    def __repr__(self):
        return f"<Genre {self.name}>"

# Alias Category = Genre de tuong thich nguoc
Category = Genre


class Movie(db.Model):
    """Thong tin phim duoc ban luan va danh gia."""
    __tablename__ = "movies"

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.Unicode(200), nullable=False, index=True)
    original_title = db.Column(db.Unicode(200), nullable=True)
    release_year = db.Column(db.Integer, nullable=True)
    director = db.Column(db.Unicode(120), nullable=True)
    poster_url = db.Column(db.Unicode(300), nullable=True)
    description = db.Column(db.UnicodeText, nullable=True)

    genre_id = db.Column(db.Integer, db.ForeignKey("genres.id"), nullable=False)
    genre = db.relationship("Genre", back_populates="movies")

    creator_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=True)
    creator = db.relationship("User", foreign_keys=[creator_id])

    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    reviews = db.relationship("MovieReview", back_populates="movie", cascade="all, delete-orphan", lazy="select", order_by="desc(MovieReview.created_at)")

    @property
    def average_rating(self):
        valid = [r.rating for r in self.reviews if r.rating is not None]
        if not valid:
            return None
        return round(sum(valid) / len(valid), 1)

    @property
    def review_count(self):
        return len(self.reviews)

    def __repr__(self):
        return f"<Movie {self.title}>"

# Alias Book = Movie
Book = Movie


class MovieReview(db.Model):
    """Danh gia phim: gom diem so tu 1 den 10 + noi dung Markdown duoc sanitize chong XSS."""
    __tablename__ = "movie_reviews"

    id = db.Column(db.Integer, primary_key=True)
    movie_id = db.Column(db.Integer, db.ForeignKey("movies.id"), nullable=False)
    author_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    rating = db.Column(db.Integer, nullable=False, default=10) # Diem so tu 1 den 10
    body_md = db.Column(db.UnicodeText, nullable=False)
    body_html = db.Column(db.UnicodeText, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    movie = db.relationship("Movie", back_populates="reviews")
    author = db.relationship("User", foreign_keys=[author_id])

    # Getter de tuong thich voi route cu
    @property
    def book_id(self):
        return self.movie_id

# Alias Comment = MovieReview
Comment = MovieReview


class BlogPost(db.Model):
    """Bai viet blog/ban luan chuyen sau ve phim - ho tro Markdown + phan trang."""
    __tablename__ = "blog_posts"

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.Unicode(200), nullable=False)
    body_md = db.Column(db.UnicodeText, nullable=False)
    body_html = db.Column(db.UnicodeText, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)

    author_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    author = db.relationship("User", back_populates="blog_posts")

    movie_id = db.Column(db.Integer, db.ForeignKey("movies.id"), nullable=True)
    movie = db.relationship("Movie")

    def __repr__(self):
        return f"<BlogPost {self.title}>"
