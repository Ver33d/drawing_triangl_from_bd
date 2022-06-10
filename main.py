import json
import pymysql
import matplotlib.pyplot as plt
import base64

from io import BytesIO

from flask import Flask, render_template, request
from DB.sql_provider import SQL_Provider
from DB.database import work_with_db

provider = SQL_Provider('sql')
app = Flask(__name__)
app.config['DB_CONFIG'] = json.load(open('configs/db.json', 'r'))


@app.route('/', methods=["GET", "POST"])
def index():
    sql = provider.get('get_ind_nodes.sql')
    img = BytesIO()
    data = []
    fig, ax = plt.subplots()

    try:
        nodes = work_with_db(app.config['DB_CONFIG'], sql)
    except pymysql.Error:
        exit(-1)
    for node in nodes:
        sql = provider.get('get_nodes.sql', id=node['id'])
        try:
            elements = work_with_db(app.config['DB_CONFIG'], sql)
        except pymysql.Error:
            exit(-2)
        _sql = [0] * 3
        _sql[0] = provider.get('get_coord_elem.sql', id=elements[0]['n1'])
        _sql[1] = provider.get('get_coord_elem.sql', id=elements[0]['n2'])
        _sql[2] = provider.get('get_coord_elem.sql', id=elements[0]['n3'])
        try:
            n1_coord = work_with_db(app.config['DB_CONFIG'], _sql[0])[0]
            n2_coord = work_with_db(app.config['DB_CONFIG'], _sql[1])[0]
            n3_coord = work_with_db(app.config['DB_CONFIG'], _sql[2])[0]
            plt.gca().axis('equal')
            plt.plot([n1_coord['x'], n2_coord['x']], [n1_coord['y'], n2_coord['y']])
            plt.plot([n2_coord['x'], n3_coord['x']], [n2_coord['y'], n3_coord['y']])
            plt.plot([n1_coord['x'], n3_coord['x']], [n1_coord['y'], n3_coord['y']])
        except pymysql.Error:
            exit(-3)
        # Найдем центр треугольника по координатам
        X = (n1_coord['x'] + n2_coord['x'] + n3_coord['x']) / 3
        Y = (n1_coord['y'] + n2_coord['y'] + n3_coord['y']) / 3
        data.append({'id': node['id'], 'X': X, 'Y': Y})
    plt.grid()
    if request.method == "GET":
        arrow_width = 0.3
    else:
        arrow_width = int(request.form["width_change"]) * 0.3
    for i in data:
        ax.arrow(x=i['X'], y=i['Y'], dx=-(0.3 * i['X']), dy=-(0.3 * i['Y']), width=arrow_width)
    plt.savefig(img, format='png')
    plot_url = base64.b64encode(img.getvalue()).decode()
    return render_template('base.html', plot_url=plot_url)


if (__name__ == "__main__"):
    app.run(host="127.0.0.1", port=9000, debug=True)
