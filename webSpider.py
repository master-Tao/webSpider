

from flask import Flask
from flask import render_template
from flask import request
import mysql
import spider


web = Flask(__name__)


@web.route('/', methods=['GET', 'POST'])
def index0():
    if request.method == 'POST':
        spider_id = request.form['spider_id']
        count = mysql.count(spider_id)
        table = mysql.get_table()
        return render_template(
            "database.html",
            flag=1,
            data=count,
            table=table,
        )
    else:
        table = mysql.get_table()
        return render_template(
            "database.html",
            table=table,
    )


@web.route('/table/<spider_id>')
def index1(spider_id):
    items = mysql.get_item(spider_id)
    return render_template(
        "item.html",
        spider_id=spider_id,
        items=items
    )


@web.route('/item/<spider_id>/<item_id>')
def index2(spider_id, item_id):
    comments = mysql.get_comments(spider_id, item_id)
    return render_template(
        "comments.html",
        comments=comments
    )


if __name__ == '__main__':
    # spider.spider("手机", 10, 20)
    web.run(debug=True, threaded=True)



