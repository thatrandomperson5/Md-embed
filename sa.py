from flask import Flask, redirect, send_file, request, abort
from threading import Thread

def getc(c):
    global client
    client = c
app = Flask('')
def build(cl, tg, op):
    raise Exception()
@app.route('/')
def home():
    
    return redirect("https://discord.gg/Ja5CvWgmdc")
@app.route("/api")
def api():
    if not "tg" in dict(request.args).keys():
        abort(403)
    target = request.args.get("tg")
    op = dict(request.args)
    del op["tg"]
    try:
        a = build(client, target, op)
    except:
        a = "gens/fail.png"
    return send_file(a, mimetype='image/png')
def run():
  app.run(host='0.0.0.0',port=8080)

def keep_alive():
    t = Thread(target=run)
    t.start()