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
        x = x / 255
        x = np.expand_dims(x, axis=0)  # Add batch axis

        # Make predictions
        predi = model.predict(x)
        print(predi)
        print(str(np.argmax(predi[0])))
        predictedLabel = labelInfo[str(np.argmax(predi[0]))]
        self.payload['classification'] = predictedLabel
        confidence = predi[0][np.argmax(predi[0])]
        self.payload['confidence'] = str(round(confidence * 100, 2)) + '%'
        return Response(self.payload, status=status.HTTP_200_OK)
