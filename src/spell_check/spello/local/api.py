from model import Model
from request import ModelRequest
from quart import Quart, request
import aiohttp

app = Quart(__name__)

model = None

freq_dict_paths = {
    'ory': 'freq_dict.txt',
    'eng': 'freq_dict_eng.txt'
}

spello_model_paths = {
    'ory': 'spello_model.pkl',
    'eng': 'spello_model_eng.pkl'
}


@app.before_serving
async def startup():
    app.client = aiohttp.ClientSession()
    global model
    model = Model(app, freq_dict_paths)

@app.route('/', methods=['POST'])
async def infer():
    global model
    data = await request.get_json()
    req = ModelRequest(**data)
    result = await model.inference(req)
    return result

@app.route('/', methods=['PUT'])
async def update():
    # print("PUT")
    global model
    data = await request.get_json()
    req = ModelRequest(**data)
    result = await model.update(req)
    return result


if __name__ == "__main__":
    app.run()
