# Nhật ký sử dụng AI Tool — BookNest Chapter 8

Minh hoạ nội dung Buổi 39 (AI tools landscape, prompt engineering, AI code review, ranh giới đạo đức).

## Ví dụ 1 — Sinh route `add_comment`

**Prompt gửi cho AI (Copilot/Claude):**
> "Viết route Flask POST /books/<id>/comments nhận Markdown từ form, render sang HTML và
> sanitize chống XSS trước khi lưu DB, yêu cầu người dùng phải đăng nhập."

**Code AI đề xuất (rút gọn):**
```python
@app.route("/books/<int:book_id>/comments", methods=["POST"])
@login_required
def add_comment(book_id):
    body_md = request.form.get("body_md")
    body_html = markdown.markdown(body_md)   # <-- AI ban đầu KHÔNG sanitize
    ...
```

**Review bảo mật thủ công (điểm giảng viên cần nhấn mạnh):**
- ⚠️ Code AI sinh ra **thiếu bước `bleach.clean()`** → nếu người dùng chèn `<script>` qua Markdown
  (ví dụ ảnh/link có `onerror=`), XSS vẫn xảy ra khi render bằng `|safe` trong template.
- ✅ Đã bổ sung `render_markdown()` (xem `markdown_utils.py`) dùng whitelist thẻ trước khi lưu.
- ✅ Đã thêm `.strip()` kiểm tra rỗng trước khi lưu, tránh spam comment trống.

## Ví dụ 2 — Sinh test cho Follow model

**Prompt:** "Viết test pytest kiểm tra User không thể tự follow chính mình."

AI sinh test đúng cấu trúc `pytest.fixture`, nhưng **quên seed Role** trước khi tạo `User` khiến
test lỗi `IntegrityError` — đã sửa thủ công bằng cách gọi `Role.insert_roles()` trong fixture
(xem cách làm tương tự ở `ch07-roles-permissions/tests/test_authorization.py`).

## Ranh giới đạo đức khi dùng AI trong môn học

- AI dùng để **tăng tốc phần lặp lại** (boilerplate route, test skeleton) — không dùng để làm thay
  toàn bộ bài tập cá nhân/đồ án mà không hiểu code.
- Luôn **review lại bảo mật** trước khi chấp nhận code AI sinh ra, đặc biệt với input người dùng
  (SQL, Markdown, file upload) — như ví dụ 1 ở trên.
- Ghi lại prompt + có/không chỉnh sửa (như file này) để giảng viên có thể đánh giá đúng phần
  đóng góp thật sự của sinh viên trong bài nộp có dùng AI hỗ trợ.
