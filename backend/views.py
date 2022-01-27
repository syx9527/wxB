# Create your views here.
# from rest_framework.response import JsonResponse
import logging

# from django.core import serializers
from django.http import HttpResponse, HttpResponseRedirect, StreamingHttpResponse
from rest_framework.views import APIView

logger = logging.getLogger('django')


def file_iterator(file_name, chunk_size=512):
    '''
    # 用于形成二进制数据
    :return:
    '''
    with open(file_name, 'rb') as f:
        while True:
            c = f.read(chunk_size)
            if c:
                yield c
            else:
                break


class index(APIView):
    def get(self, request, *args, **kwargs):
        return HttpResponseRedirect("admin/")


class retrieve(APIView):
    def get(self, request, *args, **kwargs):
        path = r"D:\BHYN\wechartdev\backend\.well-known\pki-validation\fileauth.txt"
        file = file_iterator(path)

        print(file)
        return HttpResponse(file)


class retrieves(APIView):
    def get(self, request, *args, **kwargs):
        path = r"D:\BHYN\wechartdev\backend\.well-known\pki-validation\83E0F2FF08612B354FCAF49748CE9CCB.txt"
        file = file_iterator(path)

        response = StreamingHttpResponse(file)
        response['Content-Type'] = 'application/txt'
        # 注意filename 这个是下载后的名字
        response['Content-Disposition'] = 'attachment;filename="{}"'.format("fileauth.txt")
        print(file)
        return StreamingHttpResponse(file)
