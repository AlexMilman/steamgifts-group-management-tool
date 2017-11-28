#!flask/bin/python
from flask import Flask
from flask import request

from BusinessLogic import SGMTBusinessLogic

# API Service of SGMT
# Copyright (C) 2017  Alex Milman

app = Flask(__name__)


@app.route('/GGMT/MissingAfterNGiveaway/', methods=['GET'])
def index():
    group_webpage = request.args.get('group_webpage')
    steam_thread = request.args.get('steam_thread')
    n = request.args.get('n')
    if not group_webpage or not steam_thread or not n:
        SGMTBusinessLogic.print_usage()
        return



if __name__ == '__main__':
    app.run(debug=True)