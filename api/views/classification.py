import io
from PIL import Image
from rest_framework.viewsets import ViewSet
from rest_framework.response import Response
from rest_framework import status
from keras.models import load_model
from keras.preprocessing import image
import json
import tensorflow as tf
import numpy as np

disease_data = {
    "bacterial_leaf_blight": {
        "description": "Bacterial leaf blight is a common disease in rice caused by the bacterium Xanthomonas oryzae pv. oryzae. It appears as water-soaked lesions with yellow margins on leaves.",
        "solution": "To control bacterial leaf blight, practice crop rotation, use disease-resistant rice varieties, ensure proper drainage, avoid overhead irrigation, and apply copper-based fungicides."
    },
    "brown_spot": {
        "description": "Brown spot is a fungal disease caused by the pathogen Cochliobolus miyabeanus. It manifests as small, dark brown lesions with yellow halos on leaves.",
        "solution": "To manage brown spot, practice field sanitation, use resistant rice varieties, avoid excessive nitrogen fertilization, and apply fungicides if necessary."
    },
    "healthy": {
        "description": "Healthy rice leaves are free from any disease symptoms and exhibit normal green coloration.",
        "solution": "Maintain good agricultural practices, including proper irrigation, fertilization, and pest management, to ensure healthy rice growth."
    },
    "leaf_blast": {
        "description": "Leaf blast is a fungal disease caused by the pathogen Magnaporthe oryzae. It appears as spindle-shaped lesions with gray centers and dark borders on rice leaves.",
        "solution": "To manage leaf blast, practice crop rotation, ensure good drainage, avoid excessive nitrogen application, use resistant varieties, and apply fungicides if necessary."
    },
    "leaf_scaled": {
        "description": "Leaf scald is a fungal disease caused by the pathogen Rhynchosporium oryzae. It results in elongated, yellowish lesions with dark brown margins on rice leaves.",
        "solution": "Control leaf scald by improving field drainage, avoiding excessive nitrogen fertilization, planting disease-resistant varieties, and applying appropriate fungicides."
    },
    "narrow_brown_spot": {
        "description": "Narrow brown spot is a fungal disease caused by the pathogen Cercospora janseana. It appears as small, oval-shaped lesions with brown centers and yellow halos on rice leaves.",
        "solution": "To manage narrow brown spot, implement proper field sanitation, use disease-resistant rice varieties, avoid overhead irrigation, and apply fungicides if necessary."
    },
    "sheath_blight": {
        "description": "Sheath blight is a fungal disease caused by the pathogen Rhizoctonia solani. It results in white, water-soaked lesions on leaf sheaths, leading to wilting and lodging.",
        "solution": "Control sheath blight by maintaining proper plant spacing, improving field drainage, avoiding excessive nitrogen fertilization, using resistant varieties, and applying fungicides as needed."
    },
    "tungro": {
        "description": "Tungro is a viral disease transmitted by the green leafhopper (Nephotettix virescens) and the rice brown plant hopper (Nilaparvata lugens). It causes stunted growth, yellowing, and reddening of rice plants.",
        "solution": "To manage tungro, control the populations of leafhoppers and planthoppers through insecticides, plant disease-resistant rice varieties, and implement proper cultural practices to reduce viral transmission."
    }
}


img_height, img_width = 224, 224

with open('././models/custom_cnn_model.json', 'r') as f:
    labelInfo = f.read()

labelInfo = json.loads(labelInfo)

# Load the model without explicit graph and session
model = load_model('././models/custom_cnn_model.h5')

class ClassificationViewSet(ViewSet):
    def dispatch(self, request, *args, **kwargs):
        self.payload = {}
        return super().dispatch(request, *args, **kwargs)
    
    def create(self, request, *args, **kwargs):
        if 'image' not in request.FILES:
            return Response({'error': 'No image file provided.'}, status=status.HTTP_400_BAD_REQUEST)

        image_file = request.FILES['image']

        # Create a BytesIO object and load the image
        image_data = io.BytesIO(image_file.read())
        img = Image.open(image_data)
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
        self.payload['solution'] = disease_data[predictedLabel]['solution']
        return Response(self.payload, status=status.HTTP_200_OK)
