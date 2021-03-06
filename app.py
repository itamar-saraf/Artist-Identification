from pathlib import Path

import flask
import torch
from flask import request, jsonify

from data_handling.image_handle import load_image
from model.evaluator import Evaluator
from model.vgg import VGG

import numpy as np

app = flask.Flask(__name__)
# app.config["DEBUG"] = True

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
vgg = VGG(device)
path_to_features = Path('data/post_process_data')
if path_to_features.exists():
    evaluator = Evaluator(vgg, device, path_to_features)
else:
    print(f'You have a problem with the path to the features.'
          f'\nYour are looking in {str(path_to_features.absolute())}. Check it out.'
          f'\nI will exit now')
    exit()


@app.route('/', methods=['GET'])
def home():
    return '''<h1>Artist Identification Server</h1>
    <p>You can check which painting can be identify in /paintings path</p>
    <p>You Can Get Prediction for painting on /predict path</p>'''


@app.route('/paintings', methods=['GET'])
def paintings():
    path_to_paintings = Path('data/test_data')
    painting = [painting.name for painting in path_to_paintings.iterdir() if painting.is_file()]
    return jsonify(painting)


@app.route('/predict', methods=['GET'])
def predict():
    path = Path('data/test_data/')
    data = request.json
    if data:
        path = path.joinpath(data['artwork'])
        if path.exists():
            painting = load_image(path, device)
            score = evaluator.classify_image(painting)
            prob = evaluator.score_to_prob(score)
            pred = np.argmax(prob)
            return jsonify({'confidence:': str(prob[pred]), 'prediction:': str(evaluator.classes[pred])})
        else:
            return '''<p>The painting you requested is not in our storage</p>'''
    else:
        return '''<p>You need to send the painting path in the body</p>'''


if __name__ == '__main__':
    app.run()
