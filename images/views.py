from django.conf import settings
from django.shortcuts import render
from django.http import HttpResponse

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import UploadedImage
import boto3
from botocore.exceptions import ClientError
from django.core import serializers

# Create your views here.
class GetImages(APIView):
    def get(self, request):
        # Upload image to S3 bucket
        try:
         data  = serializers.serialize('json', UploadedImage.objects.all()) 
         print(data)
        except ClientError as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        return Response({'image_data': data}, status=status.HTTP_200_OK)

def deleteImage(request):
    return HttpResponse('Delete Images')

class ImageUploadView(APIView):
    def post(self, request):
        image_file = request.FILES.get('image')
        if not image_file:
            return Response({'error': 'No image file provided'}, status=status.HTTP_400_BAD_REQUEST)

        # Upload image to S3 bucket
        try:
            s3 = boto3.client('s3', 
                              aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
                              aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY)
            s3_filename = f"images/{image_file.name}"
            s3.upload_fileobj(image_file, settings.AWS_STORAGE_BUCKET_NAME, s3_filename)
            s3_url = f"https://{settings.AWS_STORAGE_BUCKET_NAME}.s3.amazonaws.com/{s3_filename}"
        except ClientError as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        # Save image URL to the database
        uploaded_image = UploadedImage.objects.create(image_url=s3_url)

        return Response({'image_url': s3_url, 'id': uploaded_image.id}, status=status.HTTP_201_CREATED)

        # https://rloy2np7xe.execute-api.ap-south-1.amazonaws.com/upload-image