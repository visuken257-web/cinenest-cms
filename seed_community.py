# MovieNest CMS - Seed Database Script
# Tao database MovieNest_CMS tren SQL Server / SQLite + The loai + 3 Phim kem poster + 3 User + Follow + Danh gia (1-10 diem) + Blog

import os
import sys
from datetime import datetime

# Import tu thu muc goc
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from models import db, Role, User, Follow, Genre, Movie, MovieReview, BlogPost
from markdown_utils import render_markdown, COMMENT_ALLOWED_TAGS


def seed_data(app, db):
    """Nạp dữ liệu mẫu ban đầu: Roles, Users, Genres, 3 Phim, Đánh giá 1-10 điểm, Blog."""
    with app.app_context():
        db.create_all()

        # Kiểm tra nếu đã có dữ liệu thì không seed lại
        if Role.query.first() and Movie.query.first():
            return

        print("[*] Khoi tao du lieu mau MovieNest CMS...")

        # 1. Seed Roles
        Role.insert_roles()
        admin_role = Role.query.filter_by(name="Admin").first()
        critic_role = Role.query.filter_by(name="Critic").first()
        member_role = Role.query.filter_by(name="Member").first()

        # 2. Seed Users: admin, critic, user (mật khẩu pass123)
        admin = User.query.filter_by(username="admin").first()
        if not admin:
            admin = User(email="admin@movienest.vn", username="admin", is_verified=True, role=admin_role)
            admin.set_password("pass123")
            db.session.add(admin)

        critic = User.query.filter_by(username="critic").first()
        if not critic:
            critic = User(email="critic@movienest.vn", username="critic", is_verified=True, role=critic_role)
            critic.set_password("pass123")
            db.session.add(critic)

        user = User.query.filter_by(username="user").first()
        if not user:
            user = User(email="user@movienest.vn", username="user", is_verified=True, role=member_role)
            user.set_password("pass123")
            db.session.add(user)

        db.session.flush()

        # 3. Seed Follow
        if Follow.query.count() == 0:
            db.session.add_all([
                Follow(follower_id=critic.id, followed_id=admin.id),
                Follow(follower_id=critic.id, followed_id=user.id),
                Follow(follower_id=user.id, followed_id=admin.id),
            ])

        # 4. Seed Thể loại (Genres)
        genres_data = [
            "Thần thoại & Cổ trang",
            "Lịch sử & Chiến tranh",
            "Hoạt hình & Viễn tưởng",
        ]
        genres = {}
        for g_name in genres_data:
            g = Genre.query.filter_by(name=g_name).first()
            if not g:
                g = Genre(name=g_name)
                db.session.add(g)
            genres[g_name] = g
        db.session.flush()

        # 5. Seed 3 bộ phim chính kèm poster từ hình ảnh người dùng cung cấp
        movies_data = [
            {
                "title": "Tây Du Ký (1986)",
                "original_title": "西游记 (1986)",
                "release_year": 1986,
                "director": "Dương Khiết",
                "genre": genres["Thần thoại & Cổ trang"],
                "poster_url": "/static/posters/tay_du_ky.jpg",
                "description": "Kiệt tác truyền hình kinh điển của đài CCTV kể về hành trình 14 năm vượt 81 kiếp nạn sang Tây Trúc thỉnh kinh của bốn thầy trò Đường Tăng, Tôn Ngộ Không, Trư Bát Giới và Sa Tăng. Bộ phim gắn liền với tuổi thơ của hàng triệu khán giả Việt Nam và châu Á.",
                "reviews": [
                    (admin, 10, "Một **kiệt tác bất hủ** không thể thay thế! Dù kỹ xảo thời đó còn thô sơ nhưng cái hồn của từng nhân vật từ Tôn Ngộ Không của Lục Tiểu Linh Đồng đến Đường Tam Tạng đều quá xuất sắc."),
                    (critic, 10, "Tuổi thơ của mình! Mỗi dịp hè xem lại vẫn thấy cảm xúc nguyên vẹn. Âm nhạc và diễn xuất sống mãi với thời gian."),
                    (user, 9, "Một bộ phim xem đi xem lại cả chục lần không chán. Nhạc phim và bài ca mở đầu đi vào huyền thoại."),
                ]
            },
            {
                "title": "Transformers: A New Generation",
                "original_title": "Transformers One (2024)",
                "release_year": 2024,
                "director": "Josh Cooley",
                "genre": genres["Hoạt hình & Viễn tưởng"],
                "poster_url": "/static/posters/transformers.jpg",
                "description": "Tác phẩm đưa người xem trở về cội nguồn hành tinh Cybertron, khám phá câu chuyện chưa từng kể về tình anh em gắn bó keo sơn giữa Orion Pax (sau này là Optimus Prime) và D-16 (sau này là Megatron) trước khi biến cố xảy ra khiến họ đứng ở hai đầu chiến tuyến.",
                "reviews": [
                    (user, 9, "Đồ hoạ tuyệt đẹp, tiết tấu dồn dập và đặc biệt là cách xây dựng **động cơ biến chuyển tâm lý** của Megatron cực kỳ thuyết phục! Rất đáng xem tại rạp."),
                    (admin, 8, "Cốt truyện chặt chẽ, các cảnh hành động mãn nhãn. Một làn gió mới rất chất lượng cho thương hiệu Transformers."),
                    (critic, 9, "Một bước tiến vượt bậc của dòng phim Transformers. Hình ảnh trau chuốt, kịch bản giàu cảm xúc."),
                ]
            },
            {
                "title": "Mưa Đỏ",
                "original_title": "Máu xương đổ xuống đất trời lưu danh",
                "release_year": 2025,
                "director": "Đặng Thái Huyền",
                "genre": genres["Lịch sử & Chiến tranh"],
                "poster_url": "/static/posters/mua_do.jpg",
                "description": "Một tác phẩm điện ảnh xuất sắc của Điện ảnh Quân đội Nhân dân, tái hiện khúc tráng ca 81 ngày đêm chiến đấu bảo vệ Thành cổ Quảng Trị mùa hè đỏ lửa năm 1972. Từng thước phim khắc hoạ sự quả cảm, tình đồng đội thiêng liêng và sự hy sinh anh dũng của thế hệ thanh niên Việt Nam vì độc lập tự do.",
                "reviews": [
                    (admin, 10, "Bộ phim vô cùng xúc động và bi tráng! Tái hiện chân thực sự khốc liệt của chiến trường Thành cổ Quảng Trị 1972. Tự hào về lịch sử cha anh."),
                    (critic, 10, "Góc máy nghệ thuật, phục trang và bối cảnh bom đạn rất chân thực. Khán giả nghẹn ngào trong từng phân cảnh đồng đội chia tay nhau."),
                    (user, 9, "Lời thoại xúc động, truyền tải trọn vẹn thông điệp 'Máu xương đổ xuống đất trời lưu danh'."),
                ]
            },
        ]

        for m_info in movies_data:
            existing_movie = Movie.query.filter_by(title=m_info["title"]).first()
            if existing_movie:
                continue

            movie = Movie(
                title=m_info["title"],
                original_title=m_info["original_title"],
                release_year=m_info["release_year"],
                director=m_info["director"],
                genre=m_info["genre"],
                poster_url=m_info["poster_url"],
                description=m_info["description"],
                creator=admin
            )
            db.session.add(movie)
            db.session.flush()

            # Thêm đánh giá (MovieReview)
            for rev_author, rating, text_md in m_info["reviews"]:
                review = MovieReview(
                    movie=movie,
                    author=rev_author,
                    rating=rating,
                    body_md=text_md,
                    body_html=render_markdown(text_md, allowed_tags=COMMENT_ALLOWED_TAGS)
                )
                db.session.add(review)

        # 6. Seed Blog Posts (Bàn luận chuyên sâu về 3 phim này)
        if BlogPost.query.count() == 0:
            posts_data = [
                ("Giải mã cái kết bi tráng và thông điệp lịch sử trong 'Mưa Đỏ' (2025)",
                 "## Lời mở đầu\n\nBộ phim **Mưa Đỏ** của đạo diễn Đặng Thái Huyền không chỉ là một tác phẩm chiến tranh đơn thuần, mà là bản tráng ca về tinh thần dâng hiến của tuổi trẻ...\n\n### 3 điểm sáng nghệ thuật:\n1. Bối cảnh khói lửa 81 ngày đêm Thành cổ Quảng Trị chân thực\n2. Xây dựng tâm lý người lính sâu sắc và bi tráng\n3. Âm nhạc hùng tráng gợi nhiều suy ngẫm",
                 admin),
                ("Vì sao Tây Du Ký 1986 sau gần 40 năm vẫn là tượng đài bất khả chiến bại?",
                 "Gần 40 năm trôi qua, dù có hàng chục phiên bản Tây Du Ký remake với kinh phí hàng trăm triệu USD và kỹ xảo 3D hoành tráng, **bản 1986 của đạo diễn Dương Khiết** vẫn là đỉnh cao trong lòng người hâm mộ...",
                 admin),
                ("Transformers: A New Generation - Cú lội ngược dòng ngoạn mục của dòng phim người máy",
                 "Rời bỏ phong cách cháy nổ quen thuộc, phần phim này đã tập trung sâu sắc vào **tình bạn và bi kịch đối đầu** giữa Orion Pax và D-16. Đây chính xác là những gì người hâm mộ chờ đợi suốt hơn 10 năm qua...",
                 user),
                ("Góc nhìn điện ảnh: Chiều sâu kịch bản và sự chuyển biến tâm lý nhân vật",
                 "Một bộ phim thành công không chỉ ở mặt kỹ xảo mà cốt lõi nằm ở cách kết nối cảm xúc của khán giả với nhân vật trong từng khoảnh khắc quyết định...",
                 critic),
            ]

            for title, body_md, author in posts_data:
                db.session.add(BlogPost(
                    title=title,
                    body_md=body_md,
                    body_html=render_markdown(body_md),
                    author=author
                ))

        db.session.commit()
        print("[SUCCESS] Khoi tao thanh cong du lieu mau cho MovieNest CMS!")


def run():
    from app import app, DB_NAME
    from db_config import reset_database
    print(f"[*] Đang làm sạch và khởi tạo database '{DB_NAME}'...")
    try:
        reset_database(DB_NAME)
    except Exception as e:
        print(f"[!] Không thể reset SQL Server database: {e}")
    seed_data(app, db)


if __name__ == "__main__":
    run()
