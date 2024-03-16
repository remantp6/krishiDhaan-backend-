import io
from PIL import Image

from rest_framework.viewsets import ViewSet
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from keras.models import load_model
from keras.preprocessing import image
import json
import tensorflow as tf
import numpy as np

from accounts.models import UserHistory

disease_data = {
    "bacterial_leaf_blight": {
        "description": "Bacterial leaf blight is caused by the bacterium Xanthomonas oryzae pv. oryzae. It is a destructive disease that affects rice plants, particularly in regions with warm and humid climates. Symptoms include water-soaked lesions with yellow margins on the leaves, which can coalesce and lead to extensive damage to the plant. Bacterial leaf blight spreads rapidly through splashing water and infected seeds.",
        "solution": "Controlling bacterial leaf blight requires integrated management strategies. Crop rotation helps break the disease cycle by reducing inoculum buildup in the soil. Planting disease-resistant rice varieties can provide effective protection against the pathogen. Proper drainage minimizes standing water, which is conducive to bacterial growth. Avoiding overhead irrigation reduces leaf wetness and minimizes disease spread. Additionally, applying copper-based fungicides can help suppress bacterial populations and manage the disease."
    },
    "brown_spot": {
        "description": "Brown spot, caused by the fungal pathogen Cochliobolus miyabeanus, is a prevalent disease affecting rice crops worldwide. It is characterized by the development of small, dark brown lesions with yellow halos on the leaves. Brown spot can lead to significant yield losses if left unmanaged.",
        "solution": "Effective management of brown spot involves adopting cultural and chemical control measures. Field sanitation, such as removing infected plant debris and maintaining clean field conditions, can help reduce inoculum levels. Planting resistant rice varieties offers natural protection against the disease. Avoiding excessive nitrogen fertilization minimizes leaf succulence, which can make plants more susceptible to infection. In severe cases, fungicides may be necessary to control brown spot outbreaks."
    },
    "healthy": {
        "description": "Healthy rice leaves are free from any disease symptoms and exhibit normal green coloration.",
        "solution": "Maintaining good agricultural practices is essential for promoting healthy rice growth. This includes providing adequate irrigation, fertilization, and pest management. Regular monitoring of plants for signs of disease or stress can help prevent outbreaks and maintain overall plant health."
    },
    "leaf_blast": {
        "description": "Leaf blast is a fungal disease caused by the pathogen Magnaporthe oryzae. It appears as spindle-shaped lesions with gray centers and dark borders on rice leaves.",
        "solution": "To manage leaf blast effectively, implement cultural and chemical control measures. Crop rotation can help reduce disease pressure in subsequent plantings. Ensuring good drainage minimizes the risk of infection. Avoiding excessive nitrogen application can reduce leaf succulence and susceptibility to blast. Using resistant rice varieties provides natural protection against the disease. Fungicides may be necessary in severe cases."
    },
    "leaf_scaled": {
        "description": "Leaf scald is a fungal disease caused by the pathogen Rhynchosporium oryzae. It results in elongated, yellowish lesions with dark brown margins on rice leaves.",
        "solution": "Controlling leaf scald requires a combination of cultural practices and fungicide application. Improving field drainage helps reduce leaf wetness and minimize disease spread. Avoiding excessive nitrogen fertilization reduces leaf succulence and susceptibility to infection. Planting disease-resistant rice varieties can provide effective protection. Fungicides may be necessary to manage severe outbreaks."
    },
    "narrow_brown_spot": {
        "description": "Narrow brown spot is a fungal disease caused by the pathogen Cercospora janseana. It appears as small, oval-shaped lesions with brown centers and yellow halos on rice leaves.",
        "solution": "To manage narrow brown spot effectively, adopt cultural and chemical control measures. Proper field sanitation, such as removing infected plant debris, helps reduce disease pressure. Planting disease-resistant rice varieties offers natural protection. Avoiding overhead irrigation and minimizing leaf wetness can help prevent disease spread. Fungicides may be necessary to control severe infections."
    },
    "sheath_blight": {
        "description": "Sheath blight is a fungal disease caused by the pathogen Rhizoctonia solani. It results in white, water-soaked lesions on leaf sheaths, leading to wilting and lodging.",
        "solution": "Controlling sheath blight requires integrated management strategies. Proper plant spacing promotes air circulation and reduces disease spread. Improving field drainage minimizes conditions favorable for disease development. Avoiding excessive nitrogen fertilization reduces plant susceptibility. Using disease-resistant rice varieties provides effective protection. Fungicides may be necessary in severe cases."
    },
    "tungro": {
        "description": "Tungro is a viral disease transmitted by the green leafhopper (Nephotettix virescens) and the rice brown plant hopper (Nilaparvata lugens). It causes stunted growth, yellowing, and reddening of rice plants.",
        "solution": "To manage tungro effectively, implement control measures targeting the vectors and reducing viral transmission. Controlling leafhopper and planthopper populations through insecticides can help reduce virus spread. Planting disease-resistant rice varieties provides natural protection. Implementing proper cultural practices, such as clean cultivation and timely planting, can help minimize viral transmission. Early detection and removal of infected plants can also help prevent disease spread."
    }
}


img_height, img_width = 224, 224

with open('././models/custom_cnn_model.json', 'r') as f:
    labelInfo = f.read()

labelInfo = json.loads(labelInfo)

# Load the model without explicit graph and session
model = load_model('././models/custom_cnn_model.h5')


class ClassificationViewSet(ViewSet):
    permission_classes = (IsAuthenticated, )

    def dispatch(self, request, *args, **kwargs):
        self.payload = {}
        return super().dispatch(request, *args, **kwargs)
    
    def create(self, request, *args, **kwargs):
        if 'image' not in request.FILES:
            return Response({'error': 'No image file provided.'}, status=status.HTTP_400_BAD_REQUEST)

        image_file = request.FILES['image']

        # check if the file is an image
        print(image_file.content_type)
        if not image_file.content_type.startswith('image'):
            return Response({'error': 'Invalid file format.'}, status=status.HTTP_400_BAD_REQUEST)
        
        # check if the size is less than 10MB
        print(image_file.size)
        if image_file.size > 10 * 1024 * 1024:
            return Response({'error': 'Image size exceed the limit. Please upload image smaller than 10MB.'}, status=status.HTTP_400_BAD_REQUEST)

        # Create a BytesIO object and load the image
        image_data = io.BytesIO(image_file.read())
        img = Image.open(image_data)
        img = img.convert('RGB')
        img = img.resize((img_height, img_width))
        x = image.img_to_array(img)
        x = x / 255.0
        x = np.expand_dims(x, axis=0)  # Add batch axis

        # Make predictions
        predi = model.predict(x)
        print(predi)
        print(str(np.argmax(predi[0])))
        predictedLabel = labelInfo[str(np.argmax(predi[0]))]
        self.payload['classification'] = predictedLabel
        confidence = predi[0][np.argmax(predi[0])]
        self.payload['confidence'] = str(round(confidence * 100, 2)) + '%'
        self.payload['description'] = disease_data[predictedLabel]['description']
        # split solution into array of sentences
        solutions = disease_data[predictedLabel]['solution'].split('.')
        # remove empty strings from the array
        solutions = list(filter(lambda x: x != '', solutions))
        self.payload['solution'] = solutions

        # save the result to UserHistory model
        UserHistory.objects.create(
            user=request.user,
            image=image_file,
            classification=predictedLabel,
            confidence=str(round(confidence * 100, 2)) + '%',
            description=disease_data[predictedLabel]['description'],
            solution=disease_data[predictedLabel]['solution']
        )
        return Response(self.payload, status=status.HTTP_200_OK)
