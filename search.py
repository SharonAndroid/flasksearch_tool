# -*- coding: UTF-8 -*-
from flask import Flask,request,render_template,redirect
from googleSearchTop20 import *

from flask_wtf import FlaskForm
from wtforms import StringField, validators,SubmitField
from flask import url_for

app = Flask(__name__)
app.config.from_object('config')


class LoginForm(FlaskForm):
    # searchkey = StringField("searchkey",[validators.data_required])
    searchkey = StringField('searchkey', validators=[validators.DataRequired(message=u"查询关键字不能为空")],
                            render_kw={'placeholder': u'输入search key'})
    submit = SubmitField('submit')


#定义处理函数和路由规则，接收GET和POST请求
@app.route('/',methods=('POST','GET'))
def baselogin():
    form = LoginForm(searchkey=r'youtube downloader free')
    #判断是否是验证提交
    if form.validate_on_submit():
        #跳转
        # flash(form.name.data+'|'+form.password.data)
        searchkey = form.searchkey.data
        return redirect(url_for('success',searchkey=searchkey))
    else:
        #渲染
        return render_template('searchkey.html',form=form)

#pass the search key to show in the results page
@app.route('/success?searchkey=<searchkey>')
def success(searchkey):
    #get top20 URLs of this time
    top20result1 = getURLS_writetofile(searchkey)
    print 'urls:',top20result1[0]
    print 'upurls:',top20result1[1]
    print 'downurls:',top20result1[2]
    print 'sameasurls',top20result1[3]

    return render_template('success.html',urls=top20result1[0], downurls=top20result1[2],
                           upurls=top20result1[1], sameasurls=top20result1[3], newaddedurls=top20result1[4],searchkey=searchkey)
    # return render_template('success.html',urls=top20result)


if __name__ == '__main__':
    app.run(debug=True,threaded=True)