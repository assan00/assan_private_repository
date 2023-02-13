import logging

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.urls import reverse_lazy
from django.views import generic
from django.shortcuts import get_object_or_404

from .forms import InquiryForm, DiaryCreateForm, TitleSerchInquiryForm
from .models import Diary

from .mycode import query_class


logger = logging.getLogger(__name__)

#========================================================================================
#ログイン認証処理
class OnlyYouMixin(UserPassesTestMixin):
    raise_exception = True

    def test_func(self):
        # URLに埋め込まれた主キーから日記データを1件取得。取得できなかった場合は404エラー
        diary = get_object_or_404(Diary, pk=self.kwargs['pk'])
        # ログインユーザーと日記の作成ユーザーを比較し、異なればraise_exceptionの設定に従う
        return self.request.user == diary.user

#========================================================================================
#ログインが不要なクラスベースビュータイプ
class Base_All_Type_View_Class():
    def Base_function_type(self):
        return 0

#ログインが必要なクラスベースビュータイプ
class Base_Auth_Type_View_Class(LoginRequiredMixin,Base_All_Type_View_Class):
    def Base_function_type(self):
        return 0

    def get_context_data(self):
        return 0

#    def get(self):
#        return 0
#        return render(request,template_name=self.template_name,context=context)

#   def post(self):
#       return 0

#@login_required
#def test_index(request):
#    context={ 'test_data': Diary.objects.filter(user=request.user).all(),}
#    return render(request,'diary_serch.html',context)

#========================================================================================

class IndexView(Base_All_Type_View_Class,generic.TemplateView):
    template_name = "index.html"


class InquiryView(generic.FormView):
    template_name = "inquiry.html"
    form_class = InquiryForm
    success_url = reverse_lazy('diary:inquiry')

    def form_valid(self, form):
        form.send_email()
        messages.success(self.request, 'メッセージを送信しました。')
        logger.info('Inquiry sent by {}'.format(form.cleaned_data['name']))
        return super().form_valid(form)


class DiaryListView(LoginRequiredMixin,generic.ListView):
    model = Diary
    template_name = 'diary_list.html'
    paginate_by = 2

    def get_queryset(self):
        diaries = Diary.objects.filter(user=self.request.user).order_by('-created_at')
        return diaries


class DiaryDetailView(LoginRequiredMixin, OnlyYouMixin, generic.DetailView):
    model = Diary
    template_name = 'diary_detail.html'


class DiaryCreateView(LoginRequiredMixin, generic.CreateView):
    model = Diary
    template_name = 'diary_create.html'
    form_class = DiaryCreateForm
    success_url = reverse_lazy('diary:diary_serch')

    def form_valid(self, form):
        diary = form.save(commit=False)
        diary.user = self.request.user
        diary.save()
        messages.success(self.request, '日記を作成しました。')
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, "日記の作成に失敗しました。")
        return super().form_invalid(form)


class DiaryUpdateView(LoginRequiredMixin, OnlyYouMixin, generic.UpdateView):
    model = Diary
    template_name = 'diary_update.html'
    form_class = DiaryCreateForm

    def get_success_url(self):
        return reverse_lazy('diary:diary_detail', kwargs={'pk': self.kwargs['pk']})

    def form_valid(self, form):
        messages.success(self.request, '日記を更新しました。')
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, "日記の更新に失敗しました。")
        return super().form_invalid(form)


class DiaryDeleteView(LoginRequiredMixin, OnlyYouMixin, generic.DeleteView):
    model = Diary
    template_name = 'diary_delete.html'
    success_url = reverse_lazy('diary:diary_serch')

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, "日記を削除しました。")
        return super().delete(request, *args, **kwargs)


#========================================================================================
#タイトル検索処理
class DiarySerchListView(Base_Auth_Type_View_Class, TitleSerchInquiryForm,query_class.a, generic.ListView):
    model = Diary
    template_name = 'diary_serch.html'
    paginate_by = 2
    form_data = TitleSerchInquiryForm
    serch_data = None
    post_data = None

    def Set_Diary_data(self):
        if self.post_data == None:
            return self.get_user_diary_list_all()
        else :
            return self.get_serch_title_diary_list(self.post_data)



    def post(self,request):
        post_form_value=self.request.POST.get('title',None)
        self.post_data = post_form_value
        return self.get(request)

    def get_user_diary_list_all(self):
        super().Base_function_type()
        diaries = Diary.objects.filter(user=self.request.user).order_by('-created_at')
        return diaries

    def get_serch_title_diary_list(self,title_name):
        super().Base_function_type()
        diaries = Diary.objects.filter(user=self.request.user, title=title_name).order_by('-created_at')
        return diaries

    def get_context_data(self):
        serch_data = self.Set_Diary_data()
        #self.b(self.post_data)
        context = {
            'test_data': Diary.objects.filter(user=self.request.user).all(),
            'diaries': self.get_user_diary_list_all(),
            'form_data': self.form_data,
            'form_data2':   serch_data,
        }
        #messages.success(self.request,self.form_data2)
        return context


#========================================================================================
