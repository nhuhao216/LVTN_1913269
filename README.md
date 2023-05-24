# GIỚI THIỆU PROJECT

Project xây dựng ứng dụng thực hiện chuỗi quy trình gồm: yêu cầu - tiếp nhận - tạo đơn hàng - lưu trữ hợp đồng - thanh toán & lưu trữ hoá đơn.

# CÁC CHỨC NĂNG VÀ CÁCH SỬ DỤNG

Các role user chính:

- Nhân viên các phòng ban khác (nvkhac): người được phép tạo và theo dõi yêu cầu mua hàng
- Nhân viên thu mua (nvthumua): người thực hiện yêu cầu mua hàng, tạo và quản lý các thông tin liên quan trong quá trình mua hàng
- Quản lý thu mua (qlthumua): người chịu trách nhiệm phê duyệt hợp đồng, thông tin đơn hàng trước khi nó được tiến hành và kiểm tra thanh toán cuối cùng, tạo và xuất báo cáo.
- Nhân viên kho (nvkho): người thực hiện kiểm tra đơn hàng đã được đến nơi để tạo thông tin lưu kho.
- Nhân viên kế toán (nvketoan): người thực hiện tạo và quản lý quá trình thanh toán hoá đơn của đơn hàng.
- Admin: người duy nhất được truy cập và quản trị hệ thống, cơ sở dữ liệu admin

Trang web gồm các màn hình chính:

- Mục quản lý (chung):
  - Danh sách tất cả yêu cầu mua hàng: xem thông tin tất cả yêu cầu mua hàng, được sắp xếp theo thời gian cập nhật (Trừ nvkho, nvktoan).
  - Danh sách tất cả đơn hàng: xem thông tin tất cả đơn hàng, được sắp xếp theo thời gian cập nhật.
  - Danh sách nhà cung cấp, danh sách hàng hoá, danh sách hợp đồng, danh sách thanh toán.
  - Báo cáo: báo cáo số lượng yêu cầu, đơn hàng, tổng số tiền thanh toán theo thời gian.

- Mục cá nhân:
  - Danh sách yêu cầu mua hàng cá nhân (đối với nvkhac) hay yêu cầu mua hàng được phân công phụ trách (đối với nvthumua).
  - Danh sách đơn hàng tương ứng với các yêu cầu mua hàng có trong mục cá nhân.
  - Danh sách nhà cung cấp, hợp đồng (cá nhân nvthumua tạo).

### THÔNG TIN ĐĂNG NHẬP ĐỂ THỰC HIỆN THỬ NGHIỆM CÁC QUYỀN TRUY CẬP

THÔNG TIN ĐĂNG NHẬP:

- nvkhac1 - nhanvien123(role: nhân viên khác)
- nvkhac2 - nhanvien123(role: nhân viên khác)
- nvthumua1 - nhanvien123(role: nhân viên thu mua)
- nvthumua2 - nhanvien123(role: nhân viên thu mua)
- qlthumua - quanli123 (role: quản lí thu mua)
- nvkho - nhanvien123(role: nhân viên kho)
- nvketoan - nhanvien123 (role: nhân viên kế toán)
- admin - admin (role: admin)

# MÔI TRƯỜNG THỰC THI

[![py-image]][py-url]
[![django-image]][django-url]
[![vscode-image]][vscode-url]
[![db-image]][db-url]

Environments:

- [Python >3.9, <3.10][py-url]

Code-editor:

- [VSCode][vscode-url]

Dependencies:

- [Django <= 4.0.4][django-url]
- [Django-database (default: SQLite)][db-url]
- [django-filter==21.1][dj-filter-url]
- [shortuuid==1.0.9][suuid-url]

Deployment:

Deployment dependecies:

- [whitenoise==6.0.0][wn-url]
- [gunicorn==20.1.0][gu-url]

# HƯỚNG DẪN CẤU HÌNH PROJECT TRÊN LOCAL PC

> Yêu cầu: đã cài đặt Python <3.10 / môi trường có hỗ trợ Python <3.10

Download code từ github hoặc clone project về local với lệnh git:

```git
https://github.com/nhuhao216/LVTN_1913269.git
```

Cài đặt các Package và Library cần thiết:

```terminal
cd LVTN_1913269

pip install -r requirements.txt
```

Trong trường hợp không có ý định deploy trên Heroku thì chỉ cần cài đặt các thư viện Django, django-filter và shortuuid:

```terrminal
pip install django==4.0.4 django-filter==21.1 shortuuid==1.0.9
```

Sau khi cài đặt các gói cần thiết, chạy lệnh sau để khởi động server:

```terminal
python3 manage.py runserver
```

Nếu trên terminal hiện yêu cầu migrate thì ngắt server bằng lệnh Ctrl + C và thực hiện lệnh migrate sau đó khởi động server:

```terminal
python3 manage.py migrate

python3 manage.py runserver
```

Vào trình duyệt và mở localhost ở port :8000 là đã có thể thao tác với web trên localhost: [127.0.0.1](http://127.0.0.1:8000/)

# CURRENT STATUS

Đã hoàn thành các yêu cầu  gồm:

1. Lập các danh sách: yêu cầu mua hàng, đơn hàng, hàng hoá, nhà cung cấp, hợp đồng, thanh toán.
2. Thêm yêu cầu, đơn hàng, nhà cung cấp, hợp đồng, thanh toán.
3. Phê duyệt đơn hàng, hợp đồng, cập nhật trạng thái đơn hàng, hợp đồng.

[py-image]: https://img.shields.io/badge/Python-%3E3.9%2C%20%3C3.10-yellow
[py-url]: https://www.python.org/downloads/release/python-396/
[django-image]: https://img.shields.io/badge/Django-4.0.4-green
[django-url]: https://docs.djangoproject.com/en/4.0/
[dj-filter-url]: https://django-filter.readthedocs.io/en/stable/index.html
[suuid-url]: https://github.com/skorokithakis/shortuuid
[Vscode-image]:https://img.shields.io/badge/VSCode-x64-blue
[vscode-url]: https://code.visualstudio.com/
[db-image]: https://img.shields.io/badge/Django--database-SQLite-green
[db-url]: https://docs.djangoproject.com/en/4.0/intro/tutorial02/#:~:text=By%20default%2C%20the%20configuration%20uses,else%20to%20support%20your%20database.

[wn-url]: http://whitenoise.evans.io/en/stable/
[gu-url]: https://gunicorn.org/
[this-pj-url]: https://github.com/nhuhao216/LVTN_1913269.git
