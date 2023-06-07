import json
import asyncio

from flask import Flask, render_template, Response, send_file

app = Flask(__name__)


# читаем из файла данные
async def load_data():
    try:
        with open("data.json", "r") as file:
            return json.load(file)
    except FileNotFoundError:
        return {'Данные не найдены': ''}


# главная страница
@app.route('/')
def index():
    data = asyncio.run(load_data())

    return render_template('index.html', data=data)


# обновляем данные на сайте
@app.route('/updates')
def updates():
    def generate():
        data = load_data()
        yield f"data: {json.dumps(data)}\n\n"

    return Response(generate(), mimetype='text/event-stream')


# путь для скачивания файла
@app.route('/download')
def download_file():
    return send_file("data.csv", as_attachment=True)


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(load_data())
    app.run()
