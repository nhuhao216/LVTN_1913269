from django.shortcuts import render, redirect

#models import
from .models import *

#authentication import
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.models import Group

from django.contrib.auth.decorators import login_required
from .decorators import non_admin_only, allowed_users

#utils
from datetime import datetime

#forms import
from .forms import *
from django.forms import inlineformset_factory, modelform_factory

# Create your views here.

### UTILS
def update_hd_status():
    dshd = HOPDONG.objects.all().order_by('-ngay_tao')
    now = datetime.now()
    for hd in dshd:
        if not hd.ma_quan_ly_duyet :
            hd.trang_thai = 'Chờ phê duyệt'
        elif not hd.ngay_hieu_luc or not hd.ngay_het_han:
            hd.trang_thai = 'Đã duyệt'
        elif hd.ngay_het_han < now.date():
            hd.trang_thai = 'Đã hết hạn'
        else:
            hd.trang_thai = 'Đang có hiệu lực'
        hd.save()

def update_all_po_status():
    dspo = PO.objects.all().order_by('-ngay_tao')
    for po in dspo:
        if po.ma_quan_ly_duyet and po.trang_thai == 'Chờ phê duyệt':
            po.trang_thai='Đang thực hiện'
        elif not po.ma_quan_ly_duyet and po.trang_thai != 'Chờ phê duyệt':
            po.trang_thai='Chờ phê duyệt'
        po.save()

def update_pr_status():
    dspr = PR.objects.all().order_by('-ngay_tao')

    for pr in dspr:
        pr_hhs = PR_HH.objects.filter(ma_PR = pr.ma_PR)
        for pr_hh in pr_hhs:
            po = PO.objects.filter(ma_PR=pr_hh.ma_PR, ma_hang_hoa=pr_hh.ma_hang_hoa)
            if not pr.ma_nhan_vien_phu_trach:
                pr_hh.trang_thai = 'Chờ phân công'
            elif po and (po[0].trang_thai == 'Đã nhận hàng' or po[0].trang_thai =='Đã hoàn thành'):
                pr_hh.trang_thai = 'Đã hoàn thành'
            else:
                pr_hh.trang_thai = 'Đang thực hiện'
                
            pr_hh.save()

        if any(pr_hh.trang_thai == 'Chờ phân công' for pr_hh in pr_hhs):
            pr.trang_thai = 'Chờ phân công'
        elif any(pr_hh.trang_thai == 'Đang thực hiện' for pr_hh in pr_hhs):
            pr.trang_thai = 'Đang thực hiện'
        else:
            pr.trang_thai = 'Đã hoàn thành'
        pr.save()

def get_user(request):
    user = request.user
    if user == 'admin':
        return redirect('/dspr')
    else:
        nhanvien = NHANVIEN.objects.get(user=request.user)
    return nhanvien
### Authenticate User

def loginPage(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            update_pr_status()
            update_all_po_status()
            update_hd_status()
            return redirect('/dspr')
        else:
            messages.info(request,'Username Or Password was incorrect')
    context = {}
    return render(request, 'web_core/login.html', context)

def logoutUser(request):
    logout(request)
    return redirect('login')

def home(request):
    return render(request, 'web_core/dashboard.html')

### HANGHOA

@login_required(login_url='login')
def dshh(request):
    dshh = HANGHOA.objects.all().order_by('ten_hang_hoa')
    context = {'dshh':dshh}

    return render(request, 'web_core/dshh.html', context)

### PR

@login_required(login_url='login')
def dspr(request):
    groups = request.user.groups.all()
    if groups:
        if groups[0].name == 'ketoan':
            return redirect('/dspo')
    dspr = PR.objects.all().order_by('-ngay_tao')
    update_pr_status()

    context = {'dspr':dspr}
    return render(request, 'web_core/dspr.html', context)

@non_admin_only
@login_required(login_url='login')
def dspr_canhan(request):
    update_pr_status()
    nhanvien = NHANVIEN.objects.get(user=request.user)
    if nhanvien.phong_ban != 'Thu mua':
        dspr = PR.objects.filter(ma_nhan_vien_tao=nhanvien.ma_NV).order_by('-ngay_cap_nhat')
    else:
        dspr = PR.objects.filter(ma_nhan_vien_phu_trach=nhanvien.ma_NV).order_by('-ngay_cap_nhat')
    context = {'dspr':dspr}

    return render(request, 'web_core/dspr_canhan.html', context)

@non_admin_only
@allowed_users(['khac'])
@login_required(login_url='login')
def add_pr(request):
    pr_formset= inlineformset_factory(
        PR, PR_HH,
        form=PR_HH_form,
        extra=5,
        max_num=8,
    )

    user = request.user.username
    if user == 'admin':
        return redirect('/dspr')
    else:
        nhanvien = NHANVIEN.objects.get(user=request.user)

    pr_form = PR_form(nhanvien.ma_NV)
    formset = pr_formset()
    if request.method == 'POST':
        pr_form = PR_form(nhanvien.ma_NV,request.POST)
        if pr_form.is_valid():
            pr_form.save()
        pr = PR.objects.get(ma_PR=pr_form['ma_PR'].data)
        formset = pr_formset(request.POST, instance=pr)
        if formset.is_valid():
            formset.save()
            return redirect('/dspr')
    context = {'formset':formset, 'pr_form':pr_form}
    return render(request,'web_core/add_pr.html', context)

@login_required(login_url='login')
def view_pr(request, ma_PR):
    if ma_PR is None:
        return redirect('/dspr')
    pr = PR.objects.get(ma_PR=ma_PR)
    pr_hhs = PR_HH.objects.filter(ma_PR = ma_PR)    
        
    context = {'pr':pr, 'pr_hh':pr_hhs}
    return render(request,'web_core/view_pr.html', context)

@non_admin_only
@login_required(login_url='login')
def view_pr_canhan(request, ma_PR):
    if ma_PR is None:
        return redirect('/dspr_canhan')
    pr = PR.objects.get(ma_PR=ma_PR)
    pr_hhs = PR_HH.objects.filter(ma_PR = ma_PR)
    po = []
    for pr_hh in pr_hhs:
        ma_PO = PO.objects.filter(ma_PR = ma_PR, ma_hang_hoa = pr_hh.ma_hang_hoa).values('ma_PO')
        if not ma_PO:
            po.append(None)
        else:
            po.append(ma_PO[0]['ma_PO'])
    pr_hh_po = zip(pr_hhs, po)
    context = {'pr':pr, 'pr_hh_po':pr_hh_po}
    return render(request,'web_core/view_pr_canhan.html', context)

@non_admin_only
@login_required(login_url='login')
def edit_pr_canhan(request, ma_PR, ma_HH):
    if ma_PR is None or ma_HH is None:
        return redirect('/dspr_canhan')
    pr_hh = PR_HH.objects.get(ma_PR = ma_PR, ma_hang_hoa = ma_HH)

    pr_hh_form = PR_HH_form(instance=pr_hh)

    if request.method == 'POST':
        pr_hh_form = PR_HH_form(request.POST, instance=pr_hh)
        if pr_hh_form.is_valid():
            pr_hh.ngay_cap_nhat = datetime.now()
            pr_hh_form.save()
            return redirect(f'/ca_nhan/xem_pr/{ma_PR}')
    context = {'pr_hh_form':pr_hh_form, 'ma_PR':ma_PR}
    return render(request,'web_core/edit_pr.html', context)

@allowed_users(['quanly'])
@login_required(login_url='login')
def phancong_pr(request, ma_PR):
    if ma_PR is None:
        return redirect('/dspr')
    pr = PR.objects.get(ma_PR=ma_PR)
    form = PR_phancong_form(instance = pr)
    if request.method == 'POST':
        form = PR_phancong_form(request.POST, instance=pr)
        if form.is_valid():
            pr.ngay_cap_nhat = datetime.now()
            form.save()
            return redirect(f'/xem_pr/{ma_PR}')
    context = {'form':form}
    return render(request,'web_core/phancong_pr.html', context)

### PO
@login_required(login_url='login')
def dspo(request):
    update_all_po_status()
    dspo = PO.objects.all().order_by('-ngay_tao')
    context = {'dspo':dspo}

    return render(request, 'web_core/dspo.html', context)

@non_admin_only
@login_required(login_url='login')
def dspo_canhan(request):
    update_all_po_status()
    user = request.user.username
    if user == 'admin':
        return redirect('/dspo')
    else:
        nhanvien = NHANVIEN.objects.get(user=request.user)
    if nhanvien.phong_ban != 'Thu mua':
        dspr = PR.objects.filter(ma_nhan_vien_tao=nhanvien.ma_NV).values('ma_PR')
        dspo = PO.objects.filter(ma_PR__in=dspr).order_by('-ngay_tao')
    else:
        dspo = PO.objects.filter(ma_nhan_vien_tao=nhanvien.ma_NV).order_by('-ngay_cap_nhat')
    context = {'dspo':dspo}

    return render(request, 'web_core/dspo_canhan.html', context)

@login_required(login_url='login')
def view_po(request, ma_PO):
    if ma_PO is None:
        return redirect('/dspo')
    po = PO.objects.get(ma_PO=ma_PO)
    pr_hh = PR_HH.objects.get(ma_PR = po.ma_PR.ma_PR, ma_hang_hoa = po.ma_hang_hoa.ma_HH)
    context = {'po':po, 'pr_hh':pr_hh}
    return render(request,'web_core/view_po.html', context)

@non_admin_only
@login_required(login_url='login')
def view_po_canhan(request, ma_PO):
    if ma_PO is None:
        return redirect('/dspo_canhan')
    po = PO.objects.get(ma_PO=ma_PO)
    pr_hh = PR_HH.objects.get(ma_PR = po.ma_PR.ma_PR, ma_hang_hoa = po.ma_hang_hoa.ma_HH)
    context = {'po':po, 'pr_hh':pr_hh}
    return render(request,'web_core/view_po_canhan.html', context)

@allowed_users(['thumua'])
@login_required(login_url='login')
def add_po(request, ma_PR, ma_HH):
    if ma_PR is None or ma_HH is None:
        return redirect('/dspo')
    nhanvien = NHANVIEN.objects.get(user=request.user)
    pr_hh = PR_HH.objects.get(ma_PR=ma_PR, ma_hang_hoa=ma_HH)
    form = PO_form(nhanvien.ma_NV,ma_PR,ma_HH)
    if request.method == 'POST':
        form = PO_form(nhanvien.ma_NV,ma_PR,ma_HH,request.POST)
        if form.is_valid():
            form.save()
            return redirect(f'/ca_nhan/xem_pr/{ma_PR}')
    context = {'form':form, 'pr_hh':pr_hh}
    return render(request,'web_core/add_po.html', context)


@allowed_users(['thumua'])
@login_required(login_url='login')
def add_po_2(request):
    nhanvien = NHANVIEN.objects.get(user=request.user)
    form = PO_form_2(nhanvien.ma_NV)
    if request.method == 'POST':
        form = PO_form_2(nhanvien.ma_NV,request.POST)
        if form.is_valid():
            form.save()
            return redirect('/ca_nhan/dspo')
        
    context = {'form':form}
    return render(request,'web_core/add_po_2.html', context)

@allowed_users(['thumua'])
@login_required(login_url='login')
def edit_po(request, ma_PO):
    po = PO.objects.get(ma_PO=ma_PO)
    nhanvien = NHANVIEN.objects.get(user=request.user)
    pr_hh = PR_HH.objects.get(ma_PR=po.ma_PR, ma_hang_hoa=po.ma_hang_hoa)
    form = PO_form(nhanvien.ma_NV,po.ma_PR,po.ma_hang_hoa, instance=po)
    if request.method == 'POST':
        form = PO_form(nhanvien.ma_NV,po.ma_PR,po.ma_hang_hoa,
                       request.POST,instance=po)
        if form.is_valid():
            po.ngay_cap_nhat = datetime.now()
            form.save()
            return redirect(f'/ca_nhan/xem_po/{ma_PO}')
    context = {'form':form, 'pr_hh':pr_hh}
    return render(request,'web_core/edit_po.html', context)

@allowed_users(['thumua'])
@login_required(login_url='login')
def update_po_status(request, ma_PO):
    po = PO.objects.get(ma_PO=ma_PO)
    status_form = modelform_factory(
        PO,
        fields=['ma_PO','ma_PR','trang_thai'],
        widgets={
            'ma_PO': TextInput(
                attrs={'readonly': True}
            ),
            'ma_PR': TextInput(
                attrs={'readonly': True}
            ),
        })
    form = status_form(instance=po)
    if request.method == 'POST':
        form = status_form(request.POST, instance=po)
        if form.is_valid():
            po.ngay_cap_nhat = datetime.now()
            form.save()
            return redirect(f'/ca_nhan/xem_po/{ma_PO}')
    context = {'form':form, 'ma_PO':ma_PO}
    return render(request,'web_core/update_po.html', context)

@allowed_users(['quanly'])
@login_required(login_url='login')
def duyet_po(request, ma_PO):
    po = PO.objects.get(ma_PO=ma_PO)
    user = request.user.username
    if user == 'admin':
        return redirect(f'/xem_po/{ma_PO}')
    else:
        nhanvien = NHANVIEN.objects.get(user=request.user)
    if request.method == 'GET':
        po.ma_quan_ly_duyet = nhanvien
        po.trang_thai = 'Đang thực hiện'
        po.ngay_cap_nhat = datetime.now()
        po.save()
    return redirect(f'/xem_po/{ma_PO}')

### NCC
@allowed_users(['thumua', 'quanly'])
@login_required(login_url='login')
def dsncc(request):
    dsncc = NCC.objects.all().order_by('-ngay_cap_nhat')
    context = {'dsncc':dsncc}

    return render(request, 'web_core/dsncc.html', context)

@allowed_users(['thumua'])
@login_required(login_url='login')
def dsncc_canhan(request):
    
    nhanvien = NHANVIEN.objects.get(user=request.user)

    dsncc = NCC.objects.filter(ma_nhan_vien_tao=nhanvien.ma_NV).order_by('-ngay_cap_nhat')
    context = {'dsncc':dsncc}

    return render(request, 'web_core/dsncc_canhan.html', context)

@allowed_users(['thumua', 'quanly'])
@login_required(login_url='login')
def view_ncc(request, ma_NCC):
    if ma_NCC is None:
        return redirect('/dsncc')
    ncc = NCC.objects.get(ma_NCC=ma_NCC)
    hopdong = HOPDONG.objects.filter(ma_ncc=ma_NCC)
    context = {'ncc':ncc, 'hopdong':hopdong}
    return render(request,'web_core/view_ncc.html', context)

@allowed_users(['thumua'])
@login_required(login_url='login')
def view_ncc_canhan(request, ma_NCC):
    if ma_NCC is None:
        return redirect('/dsncc')
    ncc = NCC.objects.get(ma_NCC=ma_NCC)
    hopdong = HOPDONG.objects.filter(ma_ncc=ma_NCC)
    context = {'ncc':ncc, 'hopdong':hopdong}
    return render(request,'web_core/view_ncc_canhan.html', context)

@allowed_users(['thumua'])
@login_required(login_url='login')
def add_ncc(request):
    user = request.user.username
    if user == 'admin':
        return redirect('/dsncc')
    else:
        nhanvien = NHANVIEN.objects.get(user=request.user)
    form = NCC_form(nhanvien.ma_NV)
    if request.method == 'POST':
        form = NCC_form(nhanvien.ma_NV, request.POST)
        if form.is_valid():
            form.save()
            return redirect('/dsncc')
    context = {'form':form}
    return render(request,'web_core/add_ncc.html', context)

@allowed_users(['thumua'])
@login_required(login_url='login')
def edit_ncc(request, ma_NCC):
    user = request.user.username
    if user == 'admin':
        return redirect('/dsncc')
    else:
        nhanvien = NHANVIEN.objects.get(user=request.user)
    ncc = NCC.objects.get(ma_NCC=ma_NCC)
    form = NCC_form(nhanvien.ma_NV, instance=ncc)
    if request.method == 'POST':
        form = NCC_form(nhanvien.ma_NV, request.POST, instance=ncc)
        if form.is_valid():
            ncc.ngay_cap_nhat = datetime.now()
            form.save()
            return redirect(f'/xem_ncc/{ma_NCC}')
    context = {'form':form, 'ma_NCC':ma_NCC}
    return render(request,'web_core/edit_ncc.html', context)

### HOPDONG
@allowed_users(['thumua', 'quanly','ketoan'])
@login_required(login_url='login')
def dshd(request):
    update_hd_status()
    dshd = HOPDONG.objects.all().order_by('-ngay_cap_nhat')
    context = {'dshd':dshd}

    return render(request, 'web_core/dshd.html', context)

@allowed_users(['thumua', 'quanly'])
@login_required(login_url='login')
def dshd_canhan(request):
    update_hd_status()
    nhanvien = NHANVIEN.objects.get(user=request.user)

    dshd = HOPDONG.objects.filter(ma_nhan_vien_tao=nhanvien.ma_NV).order_by('-ngay_cap_nhat')
    context = {'dshd':dshd}

    return render(request, 'web_core/dshd_canhan.html', context)

@allowed_users(['thumua', 'quanly','ketoan'])
@login_required(login_url='login')
def view_hd(request, ma_HD):
    if ma_HD is None:
        return redirect('/dshd')
    hd = HOPDONG.objects.get(ma_HD=ma_HD)
    context = {'hd':hd}
    return render(request,'web_core/view_hopdong.html', context)

@allowed_users(['thumua', 'quanly'])
@login_required(login_url='login')
def view_hd_canhan(request, ma_HD):
    if ma_HD is None:
        return redirect('/dshd')
    hd = HOPDONG.objects.get(ma_HD=ma_HD)
    context = {'hd':hd}
    return render(request,'web_core/view_hopdong_canhan.html', context)

@allowed_users(['thumua'])
@login_required(login_url='login')
def add_hd(request):
    user = request.user.username
    if user == 'admin':
        return redirect('/dshd')
    else:
        nhanvien = NHANVIEN.objects.get(user=request.user)
    form = HOPDONG_form(nhanvien.ma_NV)
    if request.method == 'POST':
        form = HOPDONG_form(nhanvien.ma_NV, request.POST)
        if form.is_valid():
            form.save()
            return redirect('/dshd')
    context = {'form':form}
    return render(request,'web_core/add_hd.html', context)

@allowed_users(['thumua', 'quanly'])
@login_required(login_url='login')
def edit_hd(request, ma_HD):
    user = request.user.username
    if user == 'admin':
        return redirect('/dshd')
    else:
        nhanvien = NHANVIEN.objects.get(user=request.user)
    hd = HOPDONG.objects.get(ma_HD=ma_HD)
    form = HOPDONG_form(nhanvien.ma_NV, instance=hd)
    if request.method == 'POST':
        form = HOPDONG_form(nhanvien.ma_NV, request.POST, instance=hd)
        if form.is_valid():
            hd.ngay_cap_nhat = datetime.now()
            form.save()
            return redirect(f'/xem_hd/{ma_HD}')
    context = {'form':form, 'ma_HD':ma_HD}
    return render(request,'web_core/edit_hd.html', context)


@allowed_users(['quanly'])
@login_required(login_url='login')
def duyet_hd(request, ma_HD):
    HD = HOPDONG.objects.get(ma_HD=ma_HD)
    user = request.user.username
    if user == 'admin':
        return redirect(f'/xem_po/{ma_HD}')
    else:
        nhanvien = NHANVIEN.objects.get(user=request.user)
    if request.method == 'GET':
        HD.ma_quan_ly_duyet = nhanvien
        HD.trang_thai = 'Đã duyệt'
        HD.ngay_cap_nhat = datetime.now()
        HD.save()
    return redirect(f'/xem_hd/{ma_HD}')

@allowed_users(['thumua', 'ketoan', 'quanly'])
@login_required(login_url='login')
def dstt(request):
    dstt = THANHTOAN.objects.all().order_by('-ngay_cap_nhat')
    context = {'dstt':dstt}

    return render(request, 'web_core/dstt.html', context)

@allowed_users(['thumua'])
@login_required(login_url='login')
def dstt_canhan(request):
    nhanvien = NHANVIEN.objects.get(user=request.user)

    dstt = THANHTOAN.objects.filter(ma_nhan_vien_tao = nhanvien.ma_NV).order_by('-ngay_cap_nhat')
    context = {'dstt':dstt}

    return render(request, 'web_core/dstt.html', context)

@allowed_users(['thumua'])
@login_required(login_url='login')
def add_tt(request):
    nhanvien = NHANVIEN.objects.get(user=request.user)

    form = THANHTOAN_form(nhanvien.ma_NV)
    if request.method == 'POST':
        form = THANHTOAN_form(nhanvien.ma_NV, request.POST)
        if form.is_valid():
            form.save()
            return redirect('/dstt')
    context = {'form':form}
    return render(request,'web_core/add_tt.html', context)

@allowed_users(['thumua', 'ketoan', 'quanly'])
@login_required(login_url='login')
def view_tt(request, ma_TT):
    tt = THANHTOAN.objects.get(ma_TT=ma_TT)
    context = {'tt':tt}

    return render(request, 'web_core/view_tt.html', context)

# @allowed_users(['ketoan'])
# @login_required(login_url='login')
# def edit_tt(request, ma_TT):
#     user = request.user.username

#     nhanvien = NHANVIEN.objects.get(user=request.user)
#     tt = THANHTOAN.objects.get(ma_TT=ma_TT)
#     form = THANHTOAN_form(nhanvien.ma_NV, instance=tt)
#     if request.method == 'POST':
#         form = THANHTOAN_form(nhanvien.ma_NV, request.POST, instance=tt)
#         if form.is_valid():
#             tt.ngay_cap_nhat = datetime.now()
#             form.save()
#             return redirect(f'/xem_hd/{ma_TT}')
#     context = {'form':form, 'ma_HD':ma_TT}
#     return render(request,'web_core/edit_hd.html', context)

@allowed_users(['ketoan'])
@login_required(login_url='login')
def update_tt_status(request, ma_TT):
    nhanvien = NHANVIEN.objects.get(user=request.user)
    tt = THANHTOAN.objects.get(ma_TT=ma_TT)
    status_form = modelform_factory(
        THANHTOAN,
        fields=['so_tien','trang_thai']
    )
    form = status_form(instance=tt)
    if request.method == 'POST':
        form = status_form(request.POST, instance=tt)
        if form.is_valid():
            tt.ngay_cap_nhat = datetime.now()
            tt.ma_nhan_vien_tt = nhanvien
            form.save()
            return redirect(f'/xem_tt/{ma_TT}')
    context = {'form':form, 'ma_TT':ma_TT, 'tt':tt}
    return render(request,'web_core/update_tt.html', context)
# # @admin_only
# def edit_benhnhan(request, id):
#     benhnhan = BENHNHAN.objects.get(id=id)
#     form = benhnhan_form(instance=benhnhan)
#     if request.method == 'POST':
#         form = benhnhan_form(request.POST, instance=benhnhan)
#         if form.is_valid():
#             form.save()
#             return redirect('/dsbn')
#     context = {'form':form}
#     return render(request,'web_core/edit_benhnhan.html', context)

# # @admin_only
# def del_benhnhan(request, id):
#     benhnhan = BENHNHAN.objects.get(id=id)
#     if request.method == 'POST':
#         benhnhan.delete()
#         return redirect('/dsbn')
#     context = {'benhnhan':benhnhan}
    # return render(request,'web_core/del_benhnhan.html', context)

# @login_required(login_url='login')
# def xuathoadon(request):
#     phieukhams = PHIEUKHAM.objects.all()
#     enum_xhd = enumerate(phieukhams,start = 1)
#     context = {'phieukhams':phieukhams, 'enum_xhd':enum_xhd}
#     return render(request, 'web_core/xuathoadon.html', context)

# @login_required(login_url='login')
# def hoadon(request, pk):
#     phieukham = PHIEUKHAM.objects.get(id=pk)
#     tienkham = THAMSO.objects.get(loai='Tiền khám').now_value
#     sdthuocs = SUDUNGTHUOC.objects.filter(id_phieukham=phieukham)  
#     enum_dsthuoc = enumerate(sdthuocs,start = 1) 
#     tienthuoc = 0
#     for sdthuoc in sdthuocs:
#         tienthuoc += sdthuoc.soluong * sdthuoc.thuoc.gia_tri
#     tong = tienkham + tienthuoc
#     context = {'phieukham':phieukham, 'tienkham':tienkham, 'tienthuoc':tienthuoc, 'tongtien':tong, 'enum_dsthuoc':enum_dsthuoc}
#     return render(request, 'web_core/hoadon.html', context)

# @login_required(login_url='login')
# def lsk(request):
#     lsk = PHIEUKHAM.objects.all().order_by('ngay_kham')
#     enum_lsk = enumerate(lsk, start = 1)
#     myFilter = LichSuKhamFilter()
#     if request.GET.__contains__('ID'):
#         myFilter = LichSuKhamFilter(request.GET,queryset=lsk)
#         lsk = myFilter.qs
#         enum_lsk = enumerate(lsk, start = 1)

#     context ={'lsk': lsk, 'myFilter':myFilter, 'enum_lsk': enum_lsk}
#     return render(request, 'web_core/lsk.html',context)

# @login_required(login_url='login')
# def lsk_guest(request):
    # lsk_guest = None
    # myFilter = LichSuKhamFilter()
    # enum_lsk_guest = None
    # if request.method == 'GET' and 'ID' in request.GET:
    #     ID = request.GET['ID']
    #     if ID :
    #         lsk_guest = PHIEUKHAM.objects.all().order_by('ngay_kham')
    #         myFilter = LichSuKhamFilter(request.GET,queryset=lsk_guest)
    #         lsk_guest = myFilter.qs
    #         enum_lsk_guest = enumerate(lsk_guest, start = 1)
    #     else:
    #         lsk_guest = None
        
    # context ={'lsk_guest': lsk_guest, 'myFilter':myFilter,'enum_lsk_guest':enum_lsk_guest}
    # context ={'lsk_guest': lsk_guest}
    # return render(request, 'web_core/lsk_guest.html')

# @login_required(login_url='login')
# def dspk(request):
#     dspk = PHIEUKHAM.objects.all().order_by('-ngay_kham')
#     enum_dspk = enumerate(dspk,start = 1)

#     context = {'enum_dspk':enum_dspk}
#     return render(request, 'web_core/dspk.html', context)

# @login_required(login_url='login')
# def add_phieukham(request):
#     sdtFormSet = inlineformset_factory(PHIEUKHAM, SUDUNGTHUOC, 
#                  fields=('id_phieukham','thuoc', 'soluong', 'don_vi', 'cach_dung'), extra=10)
#     pk_form = phieukham_form()
#     formset = sdtFormSet()
#     if request.method == 'POST':
#         pk_form = phieukham_form(request.POST)
#         if pk_form.is_valid():
#             pk_form.save()
#         pk = PHIEUKHAM.objects.get(id = pk_form['id'].data)
#         formset = sdtFormSet(request.POST, instance=pk)
#         if formset.is_valid():
#             formset.save()
#             return redirect('/dspk')
#     context = {'pk_form':pk_form, 'formset':formset}
#     return render(request,'web_core/add_phieukham.html', context)

# # @admin_only
# def del_phieukham(request, id):
#     phieukham = PHIEUKHAM.objects.get(id=id)
#     if request.method == 'POST':
#         phieukham.delete()
#         return redirect('/dspk')
#     context = {'phieukham':phieukham}
#     return render(request,'web_core/del_phieukham.html', context)

# # @admin_only
# def lap_bao_cao(request):
#     return render(request, 'web_core/lapbaocao.html')

# # @admin_only
# def baocao_doanhthuthang(request):
#     thang_nam = dt.today().date()
#     form = baocao_filter
#     if request.method == 'POST':
#         form = baocao_filter(request.POST)
#         if form.is_valid() and form['thang_bao_cao'].data != "":
#             thang_nam = dt.strptime(form['thang_bao_cao'].data, '%m/%Y')

#     queryset_dict_ngay = PHIEUKHAM.objects.values('ngay_kham').filter(ngay_kham__month=thang_nam.month).filter(ngay_kham__year=thang_nam.year)
#     ngay = []
#     so_benh_nhan = []
#     doanh_thu = []

#     for dict_ngay in queryset_dict_ngay:
#         # print(dict_ngay['ngay_kham'].strftime('%d/%m/%Y'))
#         ngay_kham = dict_ngay['ngay_kham'].date()
#         if len(ngay) > 0 and ngay_kham == ngay[-1]:
#             continue

#         ngay.append(ngay_kham)
#         phieukham_ngay = PHIEUKHAM.objects.filter(ngay_kham__date=ngay_kham)
#         so_benh_nhan.append(phieukham_ngay.count())
#         doanh_thu_ngay = 0

#         for phieu in phieukham_ngay:
#             sdthuocs = SUDUNGTHUOC.objects.filter(id_phieukham=phieu.id)
#             print(sdthuocs)
#             for sdthuoc in sdthuocs:
#                 doanh_thu_ngay += sdthuoc.soluong * sdthuoc.thuoc.gia_tri

#         doanh_thu_ngay += so_benh_nhan[-1] * THAMSO.objects.get(loai='Tiền khám').now_value
#         doanh_thu.append(doanh_thu_ngay)

#     ty_le = [round(100 * x / sum(doanh_thu), 2) for x in doanh_thu]
#     stt = [x for x in range(len(ngay))]

#     context = {'thang': thang_nam.strftime('%m/%Y'), 'stt': stt, 'ngay': ngay, 'so_benh_nhan': so_benh_nhan, 'doanh_thu': doanh_thu,
#                'ty_le': ty_le, 'form': form}
#     return render(request, 'web_core/baocaodoanhthuthang.html', context=context)

# # @admin_only
# def baocao_sudungthuoc(request):
#     thang_nam = dt.today().date()
#     form = baocao_filter
#     if request.method == 'POST':
#         form = baocao_filter(request.POST)
#         if form.is_valid() and form['thang_bao_cao'].data != "":
#             thang_nam = dt.strptime(form['thang_bao_cao'].data, '%m/%Y')

#     queryset_ngay = PHIEUKHAM.objects.filter(ngay_kham__month=thang_nam.month).filter(ngay_kham__year=thang_nam.year).values_list('id', flat=True)
#     sdthuoc = SUDUNGTHUOC.objects.filter(id_phieukham__in=queryset_ngay)

#     rows = (sdthuoc
#             .values('thuoc', 'don_vi')
#             .annotate(ten_thuoc = F('thuoc__ten'))
#             .annotate(ten_donvi = F('don_vi__ten'))
#             .annotate(so_luong=Sum('soluong'))
#             .annotate(so_lan_dung=Count('thuoc'))
#             .order_by()
#             )

#     stt = [x for x in range(len(rows))]
#     context = {'thang': thang_nam.strftime('%m/%Y'), 'stt': stt, 'rows': rows, 'form': form}
#     return render(request, 'web_core/baocaosudungthuoc.html', context=context)

# # @admin_only
# def thaydoi_quydinh(request):
#     return render(request, 'web_core/thaydoiquydinh.html')

# # @admin_only
# def thaydoi_slbn(request):
#     slbn = THAMSO.objects.get(loai='Số lượng bệnh nhân tối đa')
#     form = ThayDoiGiaTriForm(initial={'loai': slbn, 'now_value': slbn.now_value})

#     if request.method == 'POST':
#         form = ThayDoiGiaTriForm(request.POST, instance=slbn)
#         if form.is_valid():
#             form.save()
#             return redirect('/thaydoi')

#     context = {'form': form}
#     return render(request, 'web_core/thaydoi_slbn.html', context)

# # @admin_only
# def thaydoi_tienkham(request):
#     tien_kham = THAMSO.objects.get(loai='Tiền khám')
#     form = ThayDoiGiaTriForm(initial={'loai': tien_kham, 'now_value': tien_kham.now_value})

#     if request.method == 'POST':
#         form = ThayDoiGiaTriForm(request.POST, instance=tien_kham)
#         if form.is_valid():
#             form.save()
#             return redirect('/thaydoi')

#     context = {'form': form}
#     return render(request, 'web_core/thaydoi_tienkham.html', context)

# # @admin_only
# def thaydoi_loaibenh(request):
#     dslb = DANHMUC.objects.filter(loai='Bệnh')
#     context = {'dslb': dslb}
#     return render(request, 'web_core/thaydoi_loaibenh.html', context)

# # @admin_only
# def thaydoi_loaibenh_them(request):
#     benh = DANHMUC(loai='Bệnh')
#     form = DanhMucForm()

#     if request.method == 'POST':
#         form = DanhMucForm(request.POST, instance=benh)
#         if form.is_valid():
#             form.save()
#             return redirect('/thaydoi/loaibenh')

#     context = {'form': form}
#     return render(request, 'web_core/thaydoi_loaibenh_them.html', context)

# # @admin_only
# def thaydoi_loaibenh_xoa(request, id):
#     benh = DANHMUC.objects.get(id=id)

#     if request.method == 'POST':
#         benh.delete()
#         return redirect('/thaydoi/loaibenh')

#     context = {'benh': benh}
#     return render(request, 'web_core/thaydoi_loaibenh_xoa.html', context)

# # @admin_only
# def thaydoi_dvt(request):
#     dsdvt = DANHMUC.objects.filter(loai='Đơn vị')
#     context = {'dsdvt': dsdvt}
#     return render(request, 'web_core/thaydoi_dvt.html', context)

# # @admin_only
# def thaydoi_dvt_them(request):
#     dvt = DANHMUC(loai='Đơn vị')
#     form = DanhMucForm()

#     if request.method == 'POST':
#         form = DanhMucForm(request.POST, instance=dvt)
#         if form.is_valid():
#             form.save()
#             return redirect('/thaydoi/donvitinh')

#     context = {'form': form}
#     return render(request, 'web_core/thaydoi_dvt_them.html', context)

# # @admin_only
# def thaydoi_dvt_xoa(request, id):
#     dvt = DANHMUC.objects.get(id=id)

#     if request.method == 'POST':
#         dvt.delete()
#         return redirect('/thaydoi/donvitinh')

#     context = {'dvt': dvt}
#     return render(request, 'web_core/thaydoi_dvt_xoa.html', context)

# # @admin_only
# def thaydoi_cachdung(request):
#     ds_cach_dung = DANHMUC.objects.filter(loai='Cách dùng')
#     context = {'ds_cach_dung': ds_cach_dung}
#     return render(request, 'web_core/thaydoi_cachdung.html', context)

# # @admin_only
# def thaydoi_cachdung_them(request):
#     cach_dung = DANHMUC(loai='Cách dùng')
#     form = DanhMucForm()

#     if request.method == 'POST':
#         form = DanhMucForm(request.POST, instance=cach_dung)
#         if form.is_valid():
#             form.save()
#             return redirect('/thaydoi/cachdung')

#     context = {'form': form}
#     return render(request, 'web_core/thaydoi_cachdung_them.html', context)

# # @admin_only
# def thaydoi_cachdung_xoa(request, id):
#     cach_dung = DANHMUC.objects.get(id=id)

#     if request.method == 'POST':
#         cach_dung.delete()
#         return redirect('/thaydoi/cachdung')

#     context = {'cach_dung': cach_dung}
#     return render(request, 'web_core/thaydoi_cachdung_xoa.html', context)

# # @admin_only
# def thaydoi_thuoc(request):
#     ds_thuoc = DANHMUC.objects.filter(loai='Thuốc')
#     context = {'ds_thuoc': ds_thuoc}
#     return render(request, 'web_core/thaydoi_thuoc.html', context)

# # @admin_only
# def thaydoi_thuoc_them(request):
#     thuoc = DANHMUC(loai='Thuốc')
#     form = ThuocForm()

#     if request.method == 'POST':
#         form = ThuocForm(request.POST, instance=thuoc)
#         if form.is_valid():
#             form.save()
#             return redirect('/thaydoi/thuoc')

#     context = {'form': form}
#     return render(request, 'web_core/thaydoi_thuoc_them.html', context)

# # @admin_only
# def thaydoi_thuoc_xoa(request, id):
#     thuoc = DANHMUC.objects.get(id=id)

#     if request.method == 'POST':
#         thuoc.delete()
#         return redirect('/thaydoi/thuoc')

#     context = {'thuoc': thuoc}
#     return render(request, 'web_core/thaydoi_thuoc_xoa.html', context)

# # @admin_only
# def thaydoi_thuoc_sua(request, id):
#     thuoc = DANHMUC.objects.get(id=id)
#     form = ThuocForm(instance=thuoc, initial={'ten': thuoc.ten, 'gia_tri': thuoc.gia_tri})

#     if request.method == 'POST':
#         form = ThuocForm(request.POST, instance=thuoc)
#         if form.is_valid():
#             form.save()
#             return redirect('/thaydoi/thuoc')

#     context = {'ten_thuoc': thuoc.ten, 'form': form}
#     return render(request, 'web_core/thaydoi_thuoc_sua.html', context)