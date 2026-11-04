# MovieNest CMS — Hệ thống Bàn Luận & Đánh Giá Phim Cá Nhân

Hệ thống CMS cá nhân về **Bàn luận & Đánh giá Điện ảnh** kế thừa toàn bộ nền tảng kiến trúc của Chapter 8 (Flask, SQL Server, Gravatar, Follow, Sanitize Markdown chống XSS, Phân trang).

---

## 🌟 Các chức năng chính

1. **Hiển thị hình ảnh Poster trên trang danh sách & trang đánh giá**:
   - Tích hợp đúng 3 bộ phim từ hình ảnh cung cấp: **Tây Du Ký (1986)**, **Transformers: A New Generation (2024)**, **Mưa Đỏ (2025)**.
   - Trang chi tiết hiển thị poster lớn sắc nét, thông tin đạo diễn, năm phát hành, thể loại và tóm tắt cốt truyện.

2. **Chấm điểm từ 1 đến 10 & Bình luận đánh giá**:
   - Khán giả chấm điểm cho tác phẩm theo thang điểm từ **1 đến 10 điểm** (⭐ 1 - 10).
   - Tự động tính điểm trung bình (Average Rating) cho phim (ví dụ `9.8 / 10`) kèm huy hiệu điểm phong cách Cinema.
   - Bình luận đánh giá chi tiết hỗ trợ định dạng **Markdown** (in đậm, in nghiêng, trích dẫn, gạch đầu dòng,...).
   - Tự động lọc sạch mã độc XSS bằng thư viện `bleach` (`render_markdown`).

3. **Hệ thống Tài khoản đầy đủ**:
   - **Tạo tài khoản mới** (`/register`): Đăng ký với Username, Email, Mật khẩu có mã hóa an toàn (`werkzeug.security`).
   - **Đăng nhập** (`/login`): Đăng nhập bằng Username/Email + Mật khẩu + Ghi nhớ đăng nhập.
   - **Đăng nhập nhanh cho demo** (`/quick-login/<username>`): Giúp giáo viên/bạn bè bấm 1 click vào ngay các tài khoản mẫu (`tam_reader`, `an_bookworm`, `binh_writer`).
   - **Đăng xuất** (`/logout`).

4. **Trang chủ cá nhân hoá với Cookie (`show_followed`)**:
   - Tab **"Tất cả bài viết"** vs **"Chỉ xem người tôi follow"** được ghi nhớ qua Cookie 30 ngày.

5. **Mạng xã hội & Quyền riêng tư (Gravatar & Follow)**:
   - Avatar người dùng tự động sinh qua **Gravatar** (hash MD5 email), bảo đảm nguyên tắc Data Privacy.
   - Theo dõi / Bỏ theo dõi (Follow/Unfollow) các nhà phê bình điện ảnh khác.
   - Trang cá nhân (`/users/<username>`) thống kê số người theo dõi và danh sách các phim người đó đã chấm điểm.

6. **Chuyên mục Bàn luận Phim (Blog CMS)**:
   - Danh sách bài phân tích phim chuyên sâu kèm phân trang (`paginate()`).
   - Đăng bài phân tích mới với trình soạn thảo Markdown (`/blog/new`).

7. **Nhật ký AI (`/ai-log`)**:
   - Tích hợp đầy đủ bài học thực tế về việc sử dụng Copilot/AI và review bảo mật thủ công.

---

## 🚀 Hướng dẫn khởi chạy

### Bước 1: Khởi tạo dữ liệu trên SQL Server
```powershell
python seed_community.py
```
*(Script sẽ tự tạo database `BookNest_Ch08` trên SQL Server, tạo các bảng và nạp đúng 3 bộ phim kèm 9 đánh giá mẫu và 3 tài khoản demo).*

### Bước 2: Chạy ứng dụng web
```powershell
python app.py
```
Truy cập trình duyệt: **`http://127.0.0.1:5000`**

---

## 🔑 Tài khoản mẫu có sẵn (Password: `pass123`)
- `admin` (Admin / Quản trị viên)
- `critic` (Critic / Nhà phê bình phim)
- `user` (Member / Khán giả, thành viên)
