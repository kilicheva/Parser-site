import json
import asyncio
from flask import Flask, render_template, Response, send_file

app = Flask(__name__)


async def load_data():
    with open("data.json", "r") as file:
        return json.load(file)


@app.route('/')
def index():
    data = asyncio.run(load_data())
    print(data)
    return render_template('index.html', data=data)


@app.route('/updates')
def updates():
    async def generate():
        data = await load_data()
        yield f"data: {json.dumps(data)}\n\n"

    return Response(generate(), mimetype='text/event-stream')


@app.route('/download')
def download_file():
    return send_file("data.json", as_attachment=True)


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(load_data())
    app.run()
