# Hướng dẫn Deploy MovieNest CMS lên Vercel Cloud (Có Link Public)

Dự án đã được cấu hình tối ưu 100% để chạy trên **Vercel Serverless Python**. Khi deploy lên Vercel, hệ thống tự động:
- Nhận diện môi trường Cloud Serverless.
- Tự động tạo cơ sở dữ liệu SQLite trong `/tmp` và nạp sẵn 3 bộ phim (*Tây Du Ký 1986*, *Transformers: A New Generation*, *Mưa Đỏ*), poster phim, hệ thống đánh giá 1-10 điểm, blog bàn luận và 3 tài khoản demo.
- Bất kỳ ai mở link cũng có thể truy cập, xem phim, đăng nhập, chấm điểm và viết review ngay lập tức!

---

## CÁCH TRIỂN KHAI NHANH NHẤT QUA GITHUB (KHUYÊN DÙNG)

Quy trình chuẩn và phổ biến nhất của Vercel là kết nối qua GitHub:

### Bước 1: Đưa mã nguồn lên GitHub
1. Truy cập [github.com](https://github.com) và đăng nhập (hoặc tạo tài khoản nếu chưa có).
2. Nhấn nút **"New repository"** (hoặc dấu `+` ở góc trên bên phải $\rightarrow$ *New repository*).
3. Đặt tên Repo (ví dụ: `cinenest-cms`), chọn chế độ **Public**, rồi nhấn **Create repository**.
4. Tải code lên GitHub:
   - **Cách giao diện web**: Trong trang repository mới tạo, bấm vào dòng chữ *"uploading an existing file"*, kéo thả toàn bộ các file trong thư mục `C:\Users\dvien\pyhton\ch08-community-features` vào (lưu ý kéo đủ thư mục `api`, `static`, `templates`, file `app.py`, `vercel.json`, `requirements.txt`...) rồi bấm **Commit changes**.
   - **Cách Git CLI** (nếu máy đã cài Git):
     ```bash
     cd C:\Users\dvien\pyhton\ch08-community-features
     git init
     git add .
     git commit -m "Deploy MovieNest CMS to Vercel"
     git branch -M main
     git remote add origin https://github.com/<tên_tài_khoản_github>/cinenest-cms.git
     git push -u origin main
     ```

---

### Bước 2: Deploy lên Vercel (1 Click)
1. Truy cập [vercel.com](https://vercel.com) và nhấn **Sign Up** / **Log In** bằng tài khoản **GitHub**.
2. Tại màn hình Dashboard, nhấn nút **"Add New..."** ở góc phải $\rightarrow$ chọn **"Project"**.
3. Bạn sẽ thấy repository `cinenest-cms` vừa tạo hiển thị ở mục *Import Git Repository* $\rightarrow$ nhấn nút **"Import"**.
4. Ở màn hình cấu hình:
   - **Project Name**: Giữ nguyên hoặc đặt tên theo ý muốn (ví dụ: `cinenest-cms`).
   - **Framework Preset**: Chọn **Other**.
   - **Root Directory**: Giữ nguyên `./`.
5. Nhấn nút **"Deploy"** màu xanh.
6. Chờ khoảng 1 phút để Vercel build và deploy.

---

### Bước 3: Lấy Link chia sẻ cho mọi người
Sau khi deploy hoàn tất, màn hình sẽ hiện thông báo chúc mừng kèm hình ảnh website và một đường link công khai:
👉 `https://cinenest-cms.vercel.app` (hoặc `https://<tên-project>.vercel.app`).

Bạn chỉ cần copy đường link này gửi cho giáo viên, bạn bè hoặc bất kỳ ai. Mọi người từ điện thoại, máy tính đều có thể truy cập được ngay lập tức!

---

## TÀI KHOẢN DEMO SẴN TRÊN LINK DEPLOY

Người truy cập có thể dùng tính năng **Quick Login** hoặc đăng nhập bằng:
- **Admin**: `admin@movienest.vn` / mật khẩu: `pass123`
- **Critic**: `critic@movienest.vn` / mật khẩu: `pass123`
- **Member**: `user@movienest.vn` / mật khẩu: `pass123`
*(Hoặc tự bấm **Đăng ký tài khoản mới**)*

---

## TÙY CHỌN: KẾT NỐI DATABASE CLOUD LÂU DÀI (POSTGRESQL)

Mặc định trên Vercel, ứng dụng dùng SQLite tự khởi tạo dữ liệu mẫu. Nếu bạn muốn các đánh giá hoặc bài viết của người khác lưu trữ vĩnh viễn không bao giờ bị reset:
1. Tạo 1 database PostgreSQL miễn phí trên [Neon.tech](https://neon.tech) hoặc [Supabase.com](https://supabase.com).
2. Copy chuỗi kết nối (`postgresql://user:password@host/dbname`).
3. Vào dự án trên Vercel $\rightarrow$ **Settings** $\rightarrow$ **Environment Variables**:
   - Name: `DATABASE_URL`
   - Value: `<chuỗi_kết_nối_postgres>`
4. Nhấn **Save** và **Redeploy**. Hệ thống sẽ tự động chuyển sang lưu trữ trên Cloud PostgreSQL!
