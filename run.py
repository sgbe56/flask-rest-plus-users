from app import app
from app.apis import api

api.init_app(app)
app.run(host='127.0.0.1', port=5000)
