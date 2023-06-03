from django.forms import ModelForm, ValidationError, DateField
from django.forms import DateInput, TextInput, ModelChoiceField
from .models import *
from django.forms.widgets import DateInput

class PR_form(ModelForm):
    class Meta:
        model = PR
        fields = '__all__'
        exclude = [
            'trang_thai',
            'ngay_cap_nhat',
            'ma_nhan_vien_phu_trach'
        ]
        widgets = {
            'ma_nhan_vien_tao': TextInput(
                attrs={'readonly': True}
            )
        }
    def __init__(self, ma_NV, *args, **kwargs):
        super(PR_form,self).__init__(*args, **kwargs)
        self.fields['ma_nhan_vien_tao'].initial = ma_NV
        self.fields["ma_PR"].widget.attrs["readonly"] = True
        self.fields["ngay_tao"].widget.attrs["readonly"] = True

class PR_phancong_form(ModelForm):
    class Meta:
        model = PR
        fields = '__all__'
        exclude = [
            'trang_thai',
            'ngay_cap_nhat',
            'ngay_tao,'
        ]
        widgets = {
            'ma_nhan_vien_tao': TextInput(
                attrs={'readonly': True}
            )
        }
    def __init__(self, *args, **kwargs):
        super(PR_phancong_form,self).__init__(*args, **kwargs)
        self.fields["ma_PR"].widget.attrs["readonly"] = True
        self.fields["ten_PR"].widget.attrs["readonly"] = True
        self.fields["ma_nhan_vien_phu_trach"].queryset = NHANVIEN.objects.filter(phong_ban='Thu mua', chuc_vu='Nhân viên')

class PR_HH_form(ModelForm):
    class Meta:
        model = PR_HH

        # fields = '__all__'
        fields=['ma_hang_hoa','so_luong','ngay_can_hang','yeu_cau']

        widgets = {
            'ngay_can_hang': DateInput(
            attrs={'type': 'date'},
            format="%Y-%m-%d"
            ),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["yeu_cau"].required = False
        
class PO_form(ModelForm):
    class Meta:
        model = PO
        fields = '__all__'
        exclude = ['ngay_cap_nhat','ngay_tao','trang_thai','ma_quan_ly_duyet']
        widgets = {
            'ma_nhan_vien_tao': TextInput(
                attrs={'readonly': True}
            ),
            'ma_PR': TextInput(
                attrs={'readonly': True}
            ),
            'ma_hang_hoa': TextInput(
                attrs={'readonly': True}
            ),
            'ngay_du_kien_nhan': DateInput(
            attrs={'type': 'date'},
            format="%Y-%m-%d"
            ),
        }
    def __init__(self, ma_NV, ma_PR, ma_HH, *args, **kwargs):
        super(PO_form,self).__init__(*args, **kwargs)
        self.fields['ma_PO'].widget.attrs["readonly"] = True
        self.fields['ma_nhan_vien_tao'].initial = ma_NV
        self.fields['ma_PR'].initial = ma_PR
        self.fields['ma_hang_hoa'].initial = ma_HH
        self.fields["ma_ncc"].queryset = NCC.objects.filter(ma_hang_hoa=ma_HH)
        self.fields["ma_hop_dong"].queryset = HOPDONG.objects.filter(ma_hang_hoa = ma_HH)

class PO_form_2(ModelForm):
    class Meta:
        model = PO
        fields = '__all__'
        exclude = ['ngay_cap_nhat','ngay_tao','trang_thai','ma_quan_ly_duyet']

        widgets = {
            'ma_nhan_vien_tao': TextInput(
                attrs={'readonly': True}
            ),
            'ngay_du_kien_nhan': DateInput(
            attrs={'type': 'date'},
            format="%Y-%m-%d"
            ),
        }

    def __init__(self, ma_NV, *args, **kwargs):
        super(PO_form_2,self).__init__(*args, **kwargs)
        self.fields['ma_PR'].queryset = PR.objects.filter(ma_nhan_vien_phu_trach=ma_NV)
        self.fields['ma_PO'].widget.attrs["readonly"] = True
        self.fields['ma_nhan_vien_tao'].initial = ma_NV
    
    def clean(self):
        pr_hh = PR_HH.objects.filter(
            ma_PR = self.cleaned_data.get('ma_PR'),
            ma_hang_hoa = self.cleaned_data.get('ma_hang_hoa')
        )
        if not pr_hh.exists():
            raise ValidationError("Yêu cầu mua hàng hoá này không tồn tại")

class NCC_form(ModelForm):
    class Meta:
        model = NCC
        fields = '__all__'
        exclude = ['ngay_cap_nhat','ngay_tao']
        widgets = {
            'ma_nhan_vien_tao': TextInput(
                attrs={'readonly': True}
            )
        }
    def __init__(self, ma_NV, *args, **kwargs):
        super(NCC_form,self).__init__(*args, **kwargs)
        self.fields['ma_nhan_vien_tao'].initial = ma_NV
        self.fields["ma_NCC"].widget.attrs["readonly"] = True

class HOPDONG_form(ModelForm):
    class Meta:
        model = HOPDONG
        fields = '__all__'
        exclude = ['ngay_cap_nhat','ngay_tao','ma_quan_ly_duyet','trang_thai']
        widgets = {
            'ma_nhan_vien_tao': TextInput(
                attrs={'readonly': True}
            ),
            'ngay_hieu_luc': DateInput(
            attrs={'type': 'date'},
            format="%Y-%m-%d"
            ),
            'ngay_het_han': DateInput(
            attrs={'type': 'date'},
            format="%Y-%m-%d"
            ),
        }

    def __init__(self, ma_NV, *args, **kwargs):
        super(HOPDONG_form,self).__init__(*args, **kwargs)
        self.fields['ma_nhan_vien_tao'].initial = ma_NV
        self.fields["ma_HD"].widget.attrs["readonly"] = True

class THANHTOAN_form(ModelForm):
    class Meta:
        model = THANHTOAN
        fields = '__all__'
        exclude = ['ngay_tao','ngay_cap_nhat','ma_nhan_vien_tt','so_tien','trang_thai']
        widgets = {
            'ma_nhan_vien_tao': TextInput(
                attrs={'readonly': True}
            ),
        }
        
    
    def __init__(self, ma_NV, *args, **kwargs):
        super(THANHTOAN_form,self).__init__(*args, **kwargs)
        self.fields["ma_nhan_vien_tao"].initial = ma_NV
        self.fields["ma_TT"].widget.attrs["readonly"] = True

# class THANHTOAN_update_form(ModelForm):
#     class Meta:
#         model = THANHTOAN
#         fields = ['so_tien','trang_thai']
    
#     def __init__(self, ma_NV, *args, **kwargs):
#         super(THANHTOAN_update_form,self).__init__(*args, **kwargs)
#         self.fields["ma_nhan_vien_tt"].initial = ma_NV
#         self.fields["ma_TT"].widget.attrs["readonly"] = True

# class benhnhan_form(ModelForm):
#     ngay_sinh = DateField(
#         label='Ngày sinh',
#         widget=DateInput(format="%d/%m/%Y"),
#         input_formats=['%d/%m/%Y']
#     )
#     class Meta:
#         model = BENHNHAN
#         fields = '__all__'
#         widgets = {
#             'ngay_sinh': DateInput(format="%d/%m/%Y"),
#         }
#     def clean(self):
#         benhnhan = BENHNHAN.objects.filter(
#             ho_ten=self.cleaned_data.get("ho_ten"),
#             ngay_sinh=self.cleaned_data.get("ngay_sinh"),
#             gioi_tinh=self.cleaned_data.get("gioi_tinh"),
#             dia_chi=self.cleaned_data.get("dia_chi"),
#             )
#         if benhnhan.exists():
#             raise ValidationError("Bệnh nhân đã tồn tại")
#     def __init__(self, *args, **kwargs):
#         super().__init__(*args, **kwargs)
#         self.fields["id"].widget.attrs["readonly"] = True
