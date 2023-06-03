from django.db import models
from django.contrib.auth.models import User
from shortuuid.django_fields import ShortUUIDField
from django.core.validators import MaxValueValidator, MinValueValidator

from datetime import datetime

# Create your models here.
class NHANVIEN(models.Model):
    danh_muc_phong_ban = (
        ('Thu mua', 'Thu mua'),
        ('Kho', 'Kho'),
        ('Kế toán', 'Kế toán'),
        ('R&D', 'R&D'),
        ('Production', 'Production'),
        ('Khác', 'Khác')
    )
    danh_muc_chuc_vu = (
        ('Quản lí', 'Quản lí'),
        ('Nhân viên', 'Nhân viên'),
    )

    user = models.OneToOneField(User, null=True, blank=True, on_delete=models.CASCADE)
    ma_NV = ShortUUIDField(
        verbose_name='Mã nhân viên',
        length=10,
        max_length=12,
        prefix="NV",
        alphabet="0123456789",
        primary_key=True
    )
    ho_ten = models.CharField('Họ tên', max_length = 100,blank=True, null=True)
    phong_ban = models.CharField('Phòng ban', max_length = 50, choices=danh_muc_phong_ban,blank=True, null=True)
    chuc_vu = models.CharField('Chức vụ', max_length = 50, choices=danh_muc_chuc_vu,blank=True, null=True)
    
    def __str__(self):
        line = str(self.ma_NV) + ' | ' + str(self.ho_ten)
        return line


class HANGHOA(models.Model):
    ma_HH = ShortUUIDField(
        verbose_name='Mã hàng hoá',
        length=10,
        max_length=12,
        prefix="HH",
        alphabet="0123456789",
        primary_key=True
    )
    ten_hang_hoa = models.CharField('Tên hàng hoá', max_length = 100,blank=True, null=True)
    so_luong_ton = models.IntegerField('Số lượng tồn', validators = [MinValueValidator(0)], default = 0)
    
    def __str__(self):
        line = str(self.ma_HH) + ' | ' + self.ten_hang_hoa
        return line

class NCC(models.Model):
    ma_NCC = ShortUUIDField(
        verbose_name='Mã nhà cung cấp',
        length=10,
        max_length=12,
        prefix="NC",
        alphabet="0123456789",
        primary_key=True
    )
    ma_nhan_vien_tao = models.ForeignKey(NHANVIEN, on_delete = models.SET_NULL, verbose_name = 'Mã nhân viên tạo', blank = True, null=True)
    ma_so_thue = models.CharField('Mã số thuế', max_length = 20,blank=True, null=True)
    ma_hang_hoa = models.ManyToManyField(HANGHOA, verbose_name = 'Mã hàng hoá', blank = True)
    ten_doanh_nghiep = models.CharField('Tên doanh nghiệp', max_length = 100,blank=True, null=True)
    dia_chi = models.CharField('Địa chỉ', max_length = 300,blank=True, null=True)
    nguoi_lien_he = models.CharField('Người liên hệ', max_length = 100, blank=True, null=True)
    sdt = models.CharField('Số điện thoại', max_length = 20,blank=True, null=True)
    email = models.EmailField('Email', max_length = 100, blank=True, null=True)
    stk = models.CharField('Thông tin chuyển khoản', max_length = 100, blank=True, null=True)
    giay_phep = models.CharField('Giấy phép', max_length = 100, blank=True, null=True)
    nang_luc_hang_hoa = models.CharField('Năng lực hàng hoá', max_length = 100, blank=True, null=True)
    ngay_cap_nhat = models.DateTimeField('Ngày cập nhật', default=datetime.now)
    cong_no = models.CharField('Công nợ', max_length = 500, blank=True, null=True)
    file_bao_gia =  models.CharField('File báo giá', max_length=500, blank=True, null=True)
    def __str__(self):
        line = self.ten_doanh_nghiep
        return line
    
class HOPDONG(models.Model):
    danh_muc_trang_thai = (
        ('Chờ phê duyệt', 'Chờ phê duyệt'),
        ('Đã duyệt', 'Đã duyệt'),
        ('Đang có hiệu lực', 'Đang có hiệu lực'),
        ('Đã hết hạn', 'Đã hết hạn'),
    )
    ma_HD = ShortUUIDField(
        verbose_name='Mã hợp đồng',
        length=10,
        max_length=12,
        prefix="HD",
        alphabet="0123456789",
        primary_key=True
    )
    ma_hang_hoa = models.ManyToManyField(HANGHOA, verbose_name = 'Mã hàng hoá', blank = True)
    ma_nhan_vien_tao = models.ForeignKey(NHANVIEN, on_delete = models.SET_NULL, verbose_name = 'Mã nhân viên tạo', related_name = 'nv_tao_HD', blank = True, null=True)
    ma_quan_ly_duyet = models.ForeignKey(NHANVIEN, on_delete = models.SET_NULL, verbose_name = 'Mã quản lý duyệt', related_name = 'quan_ly_HD', blank = True, null=True)
    ma_ncc = models.ForeignKey(NCC, on_delete = models.SET_NULL, verbose_name = 'Nhà cung cấp',blank=True, null=True)
    ngay_tao = models.DateTimeField('Ngày tạo', default = datetime.now)
    ngay_cap_nhat = models.DateTimeField('Ngày cập nhật', default = datetime.now)
    ngay_hieu_luc = models.DateField('Ngày hiệu lực', editable=True, blank=True, null=True)
    ngay_het_han = models.DateField('Ngày hết hạn', editable=True, blank=True, null=True)
    file_hop_dong = models.CharField('File hợp đồng', max_length=500,blank=True, null=True)
    phu_luc_hop_dong = models.CharField('Phụ lục hợp đồng', max_length=20000, blank=True, null=True)
    trang_thai = models.CharField('Trạng thái hợp đồng', max_length=100, choices=danh_muc_trang_thai, default='Chờ phê duyệt',blank=True, null=True)

    def __str__(self):
        line = str(self.ma_HD) + ' | ' + str(self.ma_ncc.ten_doanh_nghiep)
        return line

class PR(models.Model):
    danh_muc_trang_thai = (
        ('Chờ phân công', 'Chờ phân công'),
        ('Đang thực hiện', 'Đang thực hiện'),
        ('Đã hoàn thành', 'Đã hoàn thành'),
    )
    ma_PR = ShortUUIDField(
        verbose_name='Mã PR',
        length=10,
        max_length=12,
        prefix="PR",
        alphabet="0123456789",
        primary_key=True
    )
    ma_nhan_vien_tao = models.ForeignKey(NHANVIEN, on_delete = models.CASCADE, verbose_name = 'Mã nhân viên tạo', related_name = 'nv_tao_PR', blank=True, null=True)
    ma_nhan_vien_phu_trach = models.ForeignKey(NHANVIEN, on_delete = models.SET_NULL, verbose_name = 'Mã nhân viên phụ trách',  related_name = 'nv_phutrach_PR', blank=True, null=True)
    ngay_tao = models.DateTimeField('Ngày tạo', default = datetime.now)
    ngay_cap_nhat = models.DateField('Ngày cập nhật', default = datetime.now)
    ten_PR = models.CharField('Tên PR', max_length = 300)
    trang_thai = models.CharField('Trạng thái PR', max_length = 100, choices=danh_muc_trang_thai, default='Chờ phân công',blank=True, null=True)

    def __str__(self):
        line = str(self.ma_PR) + ' | ' + self.ten_PR
        return line

class PR_HH(models.Model):
    danh_muc_trang_thai = (
        ('Chờ phân công', 'Chờ phân công'),
        ('Đang thực hiện', 'Đang thực hiện'),
        ('Đã hoàn thành', 'Đã hoàn thành'),
    )
    ma_PR = models.ForeignKey(PR, on_delete = models.CASCADE, verbose_name = 'Mã PR', blank=True, null=True)
    ma_hang_hoa = models.ForeignKey(HANGHOA, on_delete=models.SET_NULL, verbose_name = 'Mã hàng hoá',blank=True, null=True)
    so_luong = models.IntegerField('Số lượng', validators = [MinValueValidator(0)], default = 0)
    ngay_can_hang = models.DateField('Ngày cần hàng', editable = True, blank=True, null=True)
    ngay_cap_nhat = models.DateField('Ngày cập nhật', default = datetime.now)
    yeu_cau = models.CharField('Yêu cầu', max_length = 300, blank=True, null=True)
    trang_thai = models.CharField('Trạng thái PR', max_length = 100, choices=danh_muc_trang_thai, default='Chờ phân công',blank=True, null=True)
    
    def __str__(self):
        line = str(self.ma_PR) + ' | ' + str(self.ma_hang_hoa)
        return line
    
class PO(models.Model):
    danh_muc_trang_thai = (
        ('Chờ phê duyệt', 'Chờ phê duyệt'),
        ('Đang thực hiện', 'Đang thực hiện'),
        ('Đã nhận hàng', 'Đã nhận hàng'),
        ('Đã hoàn thành', 'Đã hoàn thành'),
    )
    ma_PO = ShortUUIDField(
        verbose_name='Mã PO',
        length=10,
        max_length=12,
        prefix="PO",
        alphabet="0123456789",
        primary_key=True
    )
    ma_PR = models.ForeignKey(PR, on_delete = models.CASCADE, verbose_name = 'Mã PR', blank=True, null=True)
    ma_hang_hoa = models.ForeignKey(HANGHOA, on_delete = models.CASCADE, verbose_name = 'Mã hàng hoá', blank=True, null=True)
    so_luong = models.IntegerField('Số lượng', validators = [MinValueValidator(0)], default = 0)
    ma_hop_dong = models.ForeignKey(HOPDONG, on_delete = models.SET_NULL, verbose_name = 'Mã hợp đồng', blank=True, null=True)
    ma_nhan_vien_tao = models.ForeignKey(NHANVIEN, on_delete=models.SET_NULL, verbose_name = 'Mã nhân viên tạo', related_name = 'nv_tao_PO',blank=True, null=True)
    ma_ncc = models.ForeignKey(NCC, on_delete = models.SET_NULL, verbose_name = 'Mã nhà cung cấp', blank=True, null=True)
    ngay_tao = models.DateTimeField('Ngày tạo', default = datetime.now)
    ngay_cap_nhat = models.DateTimeField('Ngày cập nhật', default = datetime.now)
    ngay_du_kien_nhan = models.DateTimeField('Ngày dự kiến nhận', blank=True, null=True)
    so_tien_thanh_toan = models.PositiveBigIntegerField('Số tiền thanh toán', validators=[MinValueValidator(0)], default = 0)
    trang_thai = models.CharField('Trạng thái PO', max_length = 100, choices=danh_muc_trang_thai, default='Chờ phê duyệt', blank=True, null=True)
    ma_quan_ly_duyet = models.ForeignKey(NHANVIEN, on_delete = models.SET_NULL, verbose_name = 'Mã quản lý duyệt', related_name = 'quan_ly', blank=True, null=True)

    def __str__(self):
        line = str(self.ma_PO) + ' | ' + str(self.ma_PR) + ' | ' + str(self.ma_hang_hoa)
        return line

class NHAPKHO(models.Model):
    ma_NK = ShortUUIDField(
        verbose_name='Mã PO',
        length=10,
        max_length=12,
        prefix="NK",
        alphabet="0123456789",
        primary_key=True
    )
    ma_nhan_vien_kho = models.ForeignKey(NHANVIEN, on_delete = models.SET_NULL, verbose_name = 'Mã nhân viên kho', blank=True, null=True)
    ma_PO = models.ForeignKey(PO, on_delete = models.SET_NULL, verbose_name = 'Mã PO', blank=True, null=True)
    ngay_tao = models.DateTimeField('Ngày tạo', default = datetime.now)
    danh_gia_chat_luong = models.CharField('Đánh giá chất lượng', max_length = 50, blank=True, null=True)
    so_luong_nhap_kho = models.IntegerField('Số lượng nhập kho', validators = [MinValueValidator(0)], default = 0)
    vi_tri_luu_kho = models.CharField('Vị trí lưu kho', max_length = 300, blank=True, null=True)

    def __str__(self):
        line = str(self.ma_NK) + ' | ' + str(self.ma_PO)
        return line
    
class THANHTOAN(models.Model):
    danh_muc_trang_thai = (
        ('Đang chờ thanh toán', 'Đang chờ thanh toán'),
        ('Đã thanh toán lần 1', 'Đã thanh toán lần 1'),
        ('Đã hoàn thành', 'Đã hoàn thành')
    )
    ma_TT = ShortUUIDField(
        verbose_name='Mã thanh toán',
        length=10,
        max_length=12,
        prefix="TT",
        alphabet="0123456789",
        primary_key=True
    )
    ma_nhan_vien_tao = models.ForeignKey(NHANVIEN, on_delete = models.SET_NULL, verbose_name = 'Mã nhân viên tạo', related_name = 'nv_tao_tt', blank=True, null=True)
    ma_nhan_vien_tt = models.ForeignKey(NHANVIEN, on_delete = models.SET_NULL, verbose_name = 'Mã nhân viên thanh toán', related_name = 'nv_tt', blank=True, null=True)
    ma_PO = models.ForeignKey(PO, on_delete = models.SET_NULL, verbose_name = 'Mã PO', blank=True, null=True)
    ma_HD = models.ForeignKey(HOPDONG, on_delete = models.SET_NULL, verbose_name = 'Mã hợp đồng', blank=True, null=True)
    ngay_tao = models.DateTimeField('Ngày tạo', auto_now_add = True)
    so_tien = models.PositiveBigIntegerField('Số tiền đã thanh toán', validators = [MinValueValidator(0)], default = 0)
    ngay_cap_nhat = models.DateTimeField('Ngày cập nhật', default = datetime.now)
    trang_thai = models.CharField('Trạng thái thanh toán', max_length = 100, choices=danh_muc_trang_thai, default = 'Đang chờ thanh toán')
    chung_tu_thanh_toan = models.ImageField('Chứng từ thanh toán', max_length = 200, blank=True, null=True)
    
    def __str__(self):
        line = str(self.ma_TT) + ' | ' + str(self.ma_PO)
        return line
