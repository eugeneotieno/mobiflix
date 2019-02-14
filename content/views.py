# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import authentication, permissions
from rest_framework.authtoken.models import Token
from rest_framework_jwt.settings import api_settings
from rest_framework.decorators import api_view, permission_classes
from rest_framework import status


# Create your views here.
from django.contrib.auth.models import update_last_login

from .models import *
from django.shortcuts import render
from .myserializers import *
from .mobflixPermissions import *
from django.db.models import Q
# Create your views here.
from .filter import MovieFilter
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.views import generic
import datetime
class IndexView(generic.ListView):
    model = Content
    template_name = 'index.html'
    context_object_name = 'movies'
    paginate_by = 12
    queryset =  Content.objects.all()

def home(request):
    content=""
    if request.method == "POST":
        if request.POST.get("search"):
            content=Content.objects.filter(Q(name__icontains=request.POST['query'])| Q(description__icontains=request.POST['query']))
    else:
        content =Content.objects.all()

    page = request.GET.get('page', 1)

    paginator = Paginator(content, 2)
    try:
        numbers = paginator.page(page)

    except PageNotAnInteger:
        numbers = paginator.page(1)
    except EmptyPage:
        numbers = paginator.page(paginator.num_pages)

    return render(request, 'index.html', {'articles': numbers})

def checkWorthy(code):
    pass
def getExpiryTime(exp_tym):
    #current_tym
    exp=datetime.datetime.strptime(exp_tym,"%Y-%m-%dT%H:%M:%SZ")
    a=datetime.datetime.strftime(exp, '%Y-%m-%d %H:%M:%S')
    return a
def checkSessionTime(req):
    current_tym=datetime.datetime.now()
    if "expiry_date" in req.session:
        if current_tym >datetime.datetime.strptime(req.session['expiry_date'],'%Y-%m-%d %H:%M:%S'):
            req.session['status']="POSTER"
        else:
            pass #go on ..do nothing
    else:
        pass

def watch(request,pk):
    #check if the user is allowed to watch this video
    status="POSTER"
    state=""
    message=""
    if request.method == "POST":
        if request.POST.get("submit_code"):
            code=request.POST['code']

            l=LocalPermissionClass()
            ex=l.checkIfWatcher(code)
            #exists
            if ex:
                a=l.checkExpiry(ex)
                if a:
                    message="Code has been verified.Enjoy"
                    state="success"
                    request.session['status'] = 'WATCH'
                    t=ex[0].code_expiration

                    tym=getExpiryTime(t.strftime("%Y-%m-%dT%H:%M:%SZ"))

                    request.session['expiry_date']=tym
                else:
                    message="Dear customer,You Code has expired.Please purchase another one to enjoy our services"
                    state="info"
                    request.session['status'] = 'POSTER'

                #check if code has expired
            else:
                #check remotely this is for new codes sana sana
                r=RemotePermissionClass()
                a=r.verify_code(code)
                if "success" in a['status']:
                    message="Code has bee verified"
                    state="success"

                    request.session['expiry_date']=getExpiryTime(a['message']['expire_date'])
                    request.session['status'] = 'WATCH'
                else:
                    message=a['message']
                    state="danger"
                    request.session['status'] = 'POSTER'



    if "status" in request.session:
        checkSessionTime(request)
        status=request.session['status']


    video=Content.objects.get(id=pk)
    return render(request, 'player.html', {'video': video,"status":status,"state":state,"message":message})


@api_view(['GET'])
@permission_classes((permissions.AllowAny,))
def getMoviePosters(request):
    c=Content.objects.all()
    serializer=ContentSerializer(c,many=True)
    return Response(serializer.data)
class VerifyVoucher(APIView):
    def get(self,request,voucher):
        code = voucher
        session={}

        l=LocalPermissionClass()
        ex=l.checkIfWatcher(code)
        #exists
        if ex:
            a=l.checkExpiry(ex)
            if a:
                message="Code has been verified.Enjoy"
                state="success"
                session['status'] = 'WATCH'
                t=ex[0].code_expiration

                tym=getExpiryTime(t.strftime("%Y-%m-%dT%H:%M:%SZ"))

                session['expiry_date']=tym
            else:
                session['message']="Dear customer,You Code has expired.Please purchase another one to enjoy our services"
                session['state']="info"
                session['status'] = 'POSTER'

            #check if code has expired
        else:
            #check remotely this is for new codes sana sana
            r=RemotePermissionClass()
            a=r.verify_code(code)
            if "success" in a['status']:
                session['message']="Code has bee verified"
                session['state']="success"

                session['expiry_date']=getExpiryTime(a['message']['expire_date'])
                session['status'] = 'WATCH'
            else:
                session['message']=a['message']
                session['state']="danger"
                session['status'] = 'POSTER'

        return Response(session)
def localVerify(code):
    l=LocalPermissionClass()
    ex=l.checkIfWatcher(code)
    #exists
    session={"message":"Please verify code or purchase code to continue enjoying","status":"POSTER","state":""}
    if ex:
        a=l.checkExpiry(ex)
        if a:
            session['message']="Code has been verified.Enjoy"
            session['state']="success"
            session['status'] = 'WATCH'
            t=ex[0].code_expiration

            tym=getExpiryTime(t.strftime("%Y-%m-%dT%H:%M:%SZ"))

            session['expiry_date']=tym
        else:
            session['message']="Dear customer,You Code has expired.Please purchase another one to enjoy our services"
            session['state']="info"
            session['status'] = 'POSTER'


    return session

class UploadContent(APIView):
    def post(self,request):
        serializer = ContentSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(serializer.data)
            return Response(serializer.data)
        else:
            return Response(serializer.errors)
    def get(self,request):
        data=Content.objects.all()
        serializer = ContentDisplaySerializer(data,many=True)
        return Response(serializer.data)


class UploadContentVerifyView(APIView):
    def get_object(self,id):
        try:
            return Content.objects.get(id=id)
        except Content.DoesNotExist:
            raise Http404

    def get(self,request,id,voucher):
        #check if user has paid,,,,return with a different url  ContentDisplaySerializer
        v=localVerify(voucher)
        print (v)
        print ("======")

        data=self.get_object(id)
        if "WATCH" in v['status']:
            print ("hhhh")
            serializer = ContentSerializer(data)

        else:
            serializer = ContentDisplaySerializer(data)
        return Response({"response":serializer.data,"status":v})

class UploadContentDetailView(APIView):
    def get_object(self,id):
        try:
            return Content.objects.get(id=id)
        except Content.DoesNotExist:
            raise Http404

    def get(self,request,id):
        #check if user has paid,,,,return with a different url  ContentDisplaySerializer

        data=self.get_object(id)
        serializer = ContentSerializer(data)
        return Response(serializer.data)
    def put(self,request,id):
        #check if admin permission
        serializer = ContentSerializer(data=request.data,instance=self.get_object(id))
        return Response(serializer.data)
    def delete(self,request,id):
        #check if admin to delete
        status=self.get_object(id).delete()
        return Response({"status":status})

class ContentCategory(APIView):
    def post(self,request):
        serializer = ContentCategorySerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        else:
            return Response(serializer.errors)
    def get(self,request):
        data=Content.objects.all()
        serializer = ContentSerializer(data,many=True)
        return Response(serializer.data)

class ContentCategoryDetailView(APIView):
    def get_object(self,id):
        try:
            return Category.objects.get(id=id)
        except Category.DoesNotExist:
            raise Http404

    def get(self,request,id):
        data=self.get_object(id)
        serializer = ContentCategorySerializer(data,many=True)
        return Response(serializer.data)
    def put(self,request,id):
        #check if admin permission
        serializer = ContentCategorySerializer(data=request.data,instance=self.get_object(id))
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        else:
            return Response(serializer.errors)
    def delete(self,request,id):
        #check if admin to delete
        status=self.get_object(id).delete()
        return Response({"status":status})


class ContentSearchCategory(APIView):
    """

    """
    def get(self,request,category):
        data=Content.objects.filter(category__name__icontains=category)
        print (data)
        serializer=ContentSerializer(data,many=True)
        return Response(serializer.data)
