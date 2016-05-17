from __future__ import print_function
from flask import render_template, flash, redirect, session, url_for, request, g, Flask, send_from_directory
from flask.ext.login import login_user, logout_user, current_user, login_required
from datetime import datetime
from app import app, db, lm
from .models import User
from config import POSTS_PER_PAGE, MAX_SEARCH_RESULTS
from oauth import OAuthSignIn
import sys
import os
from werkzeug import secure_filename

import json
import plotly

import cufflinks as cf
import pandas as pd
import psycopg2
import plotly.graph_objs as go



@lm.user_loader
def load_user(id):
    return User.query.get(int(id))


@app.before_request
def before_request():
    g.user = current_user
    if g.user.is_authenticated:
        g.user.last_seen = datetime.utcnow()
        db.session.add(g.user)
        db.session.commit()


#for very first front page
@app.route('/', methods=['GET', 'POST'])
@app.route('/index', methods=['GET', 'POST'])
@app.route('/index/<int:page>', methods=['GET', 'POST'])
def index(page=1):
    user = g.user
    return render_template('index.html',
                           title='Home')


# for login page
@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if g.user is not None and g.user.is_authenticated:
        return redirect(url_for('index'))
    
    if request.method == 'POST':
        if request.form['username'] != 'admin' or request.form['password'] != 'admin':
            error = 'Invalid Credentials. Please try again.'
        else:
            return redirect(url_for('index'))
    return render_template('login.html', error=error,title='Sign in')


# for logout page
@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))

# for user page
@app.route('/user/<nickname>')
@app.route('/user/<nickname>/<int:page>')
@login_required
def user(nickname, page=1):
    user = User.query.filter_by(nickname=nickname).first()
    if user is None:
        flash('User %s not found.' % nickname)
        return redirect(url_for('index'))
    return render_template('user.html',
                           user=user)

# per year
@app.route('/user/per_year')
@login_required
def per_year():
    
    user = g.user
    con = psycopg2.connect(dbname='energy', \
                           host='146.169.45.110', \
                           port=5432, \
                           user='postgres', \
                           password='password')
                           
    #per year
    sql_01= "SELECT * FROM user_by_day1('2010-05-07', '2011-05-13', 101009) ORDER BY date "
    sql_02= "SELECT * FROM national_by_day_type1('2010-05-07', '2011-05-13', 3) ORDER BY date"
    sql_03= "SELECT * FROM national_by_day1('2010-05-07', '2011-05-13') ORDER BY date"
    
    df_01 = pd.read_sql(sql_01, con)
    df_02 = pd.read_sql(sql_02, con)
    df_03 = pd.read_sql(sql_03, con)

    x = df_01.ix[:,1].sum()
    y = df_03.ix[:,1].sum()
    z = df_02.ix[:,1].sum()
    
    try:
        a = ((x-y)/y)
        b = ((x-z)/z)
        bla = "You used "
        if round((a*100), 2) == 0:
            bla=bla+ "the same as"
        else:
            bla=bla+ repr(round(abs(a*100), 2))
            if round((a*100), 2) < 0:
                bla=bla+ "% less than"
            else:
                bla=bla+ "% more than"
        bla=bla+" the national average and "


  
        if round((b*100), 2) == 0:
            bla=  bla+ " the same as"
        else:
            bla=bla+ repr(round(abs(b*100), 2))
            if round((b*100), 2) < 0:
                bla=bla+ "% less than"
            else:
                bla=bla+ "% more than"
        bla=bla+ " a typical household with similar occupants to you."
    except ZeroDivisionError:
        bla="Oops, something went wrong!"


    trace0= go.Scatter(x=df_01['date'],y=df_01['energy_kwh'],name='You')
    trace1 = go.Scatter(x=df_02['date'],y=df_02['energy_kwh'],name='A Typical Person')
    trace2 = go.Scatter(x=df_03['date'],y=df_03['energy_kwh'],name='National Average')
    #trace3 = go.Scatter(x=df_01['date'], y=[50], name='limination')
    graphs = [
          dict(
              data=[trace0,trace1],
              layout=dict(
                          title='Comparision with a Typical Person Similar to You',
                          xaxis = dict(title = 'Date (year)'),
                          yaxis = dict(title = 'Energy Consumption (kwh)'),
                         
                          
                                                    )
              ),
          dict(
                   data=[trace0,trace2],
                   layout=dict(
                               title='Comparision with a National Average User',
                               xaxis = dict(title = 'Date (year)'),
                               yaxis = dict(title = 'Energy Consumption (kwh)'),
                               
                               )
                   )

          
              ]
        
    # Add "ids" to each of the graphs to pass up to the client
    # for templating
    ids = ['graph-{}'.format(i) for i, _ in enumerate(graphs)]

    # Convert the figures to JSON
    # PlotlyJSONEncoder appropriately converts pandas, datetime, etc
    # objects to their JSON equivalents
    graphJSON = json.dumps(graphs, cls=plotly.utils.PlotlyJSONEncoder)
              
    return render_template('per_year.html',
                           user=user,
                           ids=ids,
                           bla=bla,
                           graphJSON=graphJSON)


# per month
@app.route('/user/per_month')
@login_required
def per_month():
    user = g.user
    con = psycopg2.connect(dbname='energy', \
                           host='146.169.45.110', \
                           port=5432, \
                           user='postgres', \
                           password='password')

    #per month
    sql_01 = "SELECT * FROM user_by_day1('2011-04-13', '2011-05-13', 101009) ORDER BY date"
    sql_02 = "SELECT * FROM national_by_day_type1('2011-04-13', '2011-05-13', 3) ORDER BY date"
    sql_03 = "SELECT * FROM national_by_day1('2011-04-13', '2011-05-13') ORDER BY date"
    df_01 = pd.read_sql(sql_01, con)
    df_02 = pd.read_sql(sql_02, con)
    df_03 = pd.read_sql(sql_03, con)

    x = df_01.ix[:,1].sum()
    y = df_03.ix[:,1].sum()
    z = df_02.ix[:,1].sum()
    
    try:
        a = ((x-y)/y)
        b = ((x-z)/z)
        bla = "You used "
        if round((a*100), 2) == 0:
            bla=bla+ "the same as"
        else:
            bla=bla+ repr(round(abs(a*100), 2))
            if round((a*100), 2) < 0:
                bla=bla+ "% less than"
            else:
                bla=bla+ "% more than"
        bla=bla+" the national average and "
        if round((b*100), 2) == 0:
            bla=bla+ " the same as"
        else:
            bla=bla+ repr(round(abs(b*100), 2))
            if round((b*100), 2) < 0:
                bla=bla+ "% less than"
            else:
                bla=bla+ "% more than"
        bla=bla+ " a typical household with similar occupants to you."
    except ZeroDivisionError:
        bla="Oops, something went wrong!"

    trace0 = go.Scatter(x=df_01['date'],y=df_01['energy_kwh'],name='You')
    trace1 = go.Scatter(x=df_02['date'],y=df_02['energy_kwh'],name='A Typical Person')
    trace2 = go.Scatter(x=df_03['date'],y=df_03['energy_kwh'],name='National Average')
    graphs = [
              dict(
                   data=[trace0,trace1],
                   layout=dict(
                               title='Comparision with a Typical Person Similar to You',
                               xaxis = dict(title = 'Date (month)'),
                               yaxis = dict(title = 'Energy Consumptio (kwh)'),
                               
                               )
                   ),
              dict(
                   data=[trace0,trace2],
                   layout=dict(
                               title='Comparision with a National Average User',
                               xaxis = dict(title = 'Date (month'),
                               yaxis = dict(title = 'Energy Consumption (kwh)'),
                               
                               )
                   )
              
              
              ]


    # Add "ids" to each of the graphs to pass up to the client
    # for templating
    ids = ['graph-{}'.format(i) for i, _ in enumerate(graphs)]
              
    # Convert the figures to JSON
    # PlotlyJSONEncoder appropriately converts pandas, datetime, etc
    # objects to their JSON equivalents
    graphJSON = json.dumps(graphs, cls=plotly.utils.PlotlyJSONEncoder)
              
    return render_template('per_month.html',
                            ids=ids,
                            user=user,
                            bla=bla,
                            graphJSON=graphJSON)


# per week
@app.route('/user/per_week')
@login_required
def per_week():
    user = g.user
    con = psycopg2.connect(dbname='energy', \
                           host='146.169.45.110', \
                           port=5432, \
                           user='postgres', \
                           password='password')
        
   #per week
    sql_01 = "SELECT * FROM user_by_hour1('2011-05-06 00:00:00', '2011-05-13 00:00:00', 101009) ORDER BY tt"
    sql_02 = "SELECT * FROM national_by_hour_type1('2011-05-06 00:00:00', '2011-05-13 00:00:00', 3) ORDER BY tt"
    sql_03 = "SELECT * FROM national_by_hour1('2011-05-06 00:00:00', '2011-05-13 00:00:00') ORDER BY tt"

    df_01 = pd.read_sql(sql_01, con)
    df_02 = pd.read_sql(sql_02, con)
    df_03 = pd.read_sql(sql_03, con)
    
    x = df_01.ix[:,1].sum()
    y = df_03.ix[:,1].sum()
    z = df_02.ix[:,1].sum()
    
    try:
        a = ((x-y)/y)
        b = ((x-z)/z)
        bla = "You used "
        if round((a*100), 2) == 0:
            bla=bla+ "the same as"
        else:
            bla=bla+ repr(round(abs(a*100), 2))
            if round((a*100), 2) < 0:
                bla=bla+ "% less than"
            else:
                bla=bla+ "% more than"
        bla=bla+" the national average and "
        if round((b*100), 2) == 0:
            bla=bla+ " the same as"
        else:
            bla=bla+ repr(round(abs(b*100), 2))
            if round((b*100), 2) < 0:
                bla=bla+ "% less than"
            else:
                bla=bla+ "% more than"
        bla=bla+ " a typical household with similar occupants to you."
    except ZeroDivisionError:
        bla="Oops, something went wrong!"

    
    trace0 = go.Scatter(x=df_01['tt'],y=df_01['energy_kwh'],name='You')
    trace1 = go.Scatter(x=df_02['tt'],y=df_02['energy_kwh'],name='A Typical Person')
    trace2 = go.Scatter(x=df_03['tt'],y=df_03['energy_kwh'],name='National Average')
    graphs = [
              dict(
                   data=[trace0,trace1],
                   layout=dict(
                               title='Comparision with  a Typical User Similar to You',
                               xaxis = dict(title = 'Date (week)'),
                               yaxis = dict(title = 'Energy Consumption (kwh)'),
                               
                               )
                   ),
              dict(
                   data=[trace0,trace2],
                   layout=dict(
                               title='Comparision with a National Average User',
                               xaxis = dict(title = 'Date (week)'),
                               yaxis = dict(title = 'Energy Consumption (kwh)'),
                               
                               )
                   )
              
              
              ]
   
   # Add "ids" to each of the graphs to pass up to the client
   # for templating
    ids = ['graph-{}'.format(i) for i, _ in enumerate(graphs)]
   
   # Convert the figures to JSON
   # PlotlyJSONEncoder appropriately converts pandas, datetime, etc
   # objects to their JSON equivalents
    graphJSON = json.dumps(graphs, cls=plotly.utils.PlotlyJSONEncoder)

    return render_template('per_week.html',
                           ids=ids,
                           user=user,
                           bla=bla,
                           graphJSON=graphJSON)


# per day
@app.route('/user/per_day')
@login_required
def per_day():
    user = g.user
    con = psycopg2.connect(dbname='energy', \
                           host='146.169.45.110', \
                           port=5432, \
                           user='postgres', \
                           password='password')
        
        
    #per day
    sql_01 = "SELECT * FROM user_by_min1('2011-05-12 00:00:00', '2011-05-13 00:00:00', 101009) ORDER BY tt"
    sql_02 = "SELECT * FROM national_by_min_type1('2011-05-12 00:00:00', '2011-05-13 00:00:00', 3) ORDER BY tt"
    sql_03 = "SELECT * FROM national_by_min1('2011-05-12 00:00:00', '2011-05-13 00:00:00') ORDER BY tt"

    df_01 = pd.read_sql(sql_01, con)
    df_02 = pd.read_sql(sql_02, con)
    df_03 = pd.read_sql(sql_03, con)
    
    x = df_01.ix[:,1].sum()
    y = df_03.ix[:,1].sum()
    z = df_02.ix[:,1].sum()
    
    try:
        a = ((x-y)/y)
        b = ((x-z)/z)
        bla = "You used "
        if round((a*100), 2) == 0:
            bla=bla+ "the same electricity as"
        else:
            bla=bla+ repr(round(abs(a*100), 2))
            if round((a*100), 2) < 0:
                bla=bla+ "% less electricity than"
            else:
                bla=bla+ "% more electricity than"
        bla=bla+" the national average and "
        if round((b*100), 2) == 0:
            bla=bla+ " the same electricity as"
        else:
            bla=bla+ repr(round(abs(b*100), 2))
            if round((b*100), 2) < 0:
                bla=bla+ "% less electricity than"
            else:
                bla=bla+ "% more electricity than"
        bla=bla+ " a typical household with similar occupants to you."
    except ZeroDivisionError:
        bla="Oops, something went wrong!"

    trace0 = go.Scatter(x=df_01['tt'],y=df_01['energy_kwh'],name='You')
    trace1 = go.Scatter(x=df_02['tt'],y=df_02['energy_kwh'],name='A Typical Person')
    trace2 = go.Scatter(x=df_03['tt'],y=df_03['energy_kwh'],name='National Average')
    graphs = [
              dict(
                   data=[trace0,trace1],
                   layout=dict(
                               title='Comparision with a Typical User Similar to You',
                               xaxis = dict(title = 'Date (Day)'),
                               yaxis = dict(title = 'Energy Consumption (kwh)'),
                               
                               )
                   ),
              dict(
                   data=[trace0,trace2],
                   layout=dict(
                               title='Comparision with a National Average User',
                               xaxis = dict(title = 'Date (Day)'),
                               yaxis = dict(title = 'Energy Consumption (kwh)'),
                               
                               )
                   )
              
              
              ]


    # Add "ids" to each of the graphs to pass up to the client
    # for templating
    ids = ['graph-{}'.format(i) for i, _ in enumerate(graphs)]

    # Convert the figures to JSON
    # PlotlyJSONEncoder appropriately converts pandas, datetime, etc
    # objects to their JSON equivalents
    graphJSON = json.dumps(graphs, cls=plotly.utils.PlotlyJSONEncoder)
        
    return render_template('per_day.html',
                           ids=ids,
                           user=user,
                           bla=bla,
                           graphJSON=graphJSON)

# per hour
@app.route('/user/per_hour')
@login_required
def per_hour():
    user = g.user
    con = psycopg2.connect(dbname='energy', \
                           host='146.169.45.110', \
                           port=5432, \
                           user='postgres', \
                           password='password')
    #per hour
    sql_01 = "SELECT * FROM user_by_min1('2011-05-12 12:00:00', '2011-05-12 13:00:00', 101009) ORDER BY tt"
    sql_02 = "SELECT * FROM national_by_min_type1('2011-05-12 12:00:00', '2011-05-12 13:00:00', 3) ORDER BY tt"
    sql_03 = "SELECT * FROM national_by_min1('2011-05-12 12:00:00', '2011-05-12 13:00:00') ORDER BY tt"

    df_01 = pd.read_sql(sql_01, con)
    df_02 = pd.read_sql(sql_02, con)
    df_03 = pd.read_sql(sql_03, con)
    
    x = df_01.ix[:,1].sum()
    y = df_03.ix[:,1].sum()
    z = df_02.ix[:,1].sum()
    
    try:
        a = ((x-y)/y)
        b = ((x-z)/z)
        bla = "Over the past one hour, you used "
        if round((a*100), 2) == 0:
            bla=bla+ "the same electricity as"
        else:
            bla=bla+ repr(round(abs(a*100), 2))
            if round((a*100), 2) < 0:
                bla=bla+ "% less electricity than"
            else:
                bla=bla+ "% more electricity than"
        bla=bla+" the national average and "
        if round((b*100), 2) == 0:
            bla=bla+ " the same electricity as"
        else:
            bla=bla+ repr(round(abs(b*100), 2))
            if round((b*100), 2) < 0:
                bla=bla+ "% less electricity than"
            else:
                bla=bla+ "% more electricity than"
        bla=bla+ " a typical household with similar occupants to you."
    except ZeroDivisionError:
        bla="Oops, something went wrong!"

    trace0 = go.Scatter(x=df_01['tt'],y=df_01['energy_kwh'],name='you')
    trace1 = go.Scatter(x=df_02['tt'],y=df_02['energy_kwh'],name='typical-type')
    trace2 = go.Scatter(x=df_03['tt'],y=df_03['energy_kwh'],name='national')
    graphs = [
              dict(
                   data=[trace0,trace1],
                   layout=dict(
                               title='comparision with typical type user per hour (average)',
                               xaxis = dict(title = 'tt'),
                               yaxis = dict(title = 'energy_kwh'),
                               
                               )
                   ),
              dict(
                   data=[trace0,trace2],
                   layout=dict(
                               title='comparision with national average user per hour (average)',
                               xaxis = dict(title = 'tt'),
                               yaxis = dict(title = 'energy_kwh'),
                               
                               )
                   )
              
              
              ]
              
    
    # Add "ids" to each of the graphs to pass up to the client
    # for templating
    ids = ['graph-{}'.format(i) for i, _ in enumerate(graphs)]
        
    # Convert the figures to JSON
    # PlotlyJSONEncoder appropriately converts pandas, datetime, etc
    # objects to their JSON equivalents
    graphJSON = json.dumps(graphs, cls=plotly.utils.PlotlyJSONEncoder)
        
    return render_template('per_hour.html',
                           ids=ids,
                           user=user,
                           bla=bla,
                           graphJSON=graphJSON)


@app.route('/user/appliance')
@login_required
def appliance():
    user = g.user
    return render_template('appliance.html',user=user)




# the ranking page
@app.route('/user/ranking')
@login_required
def ranking():
    user = g.user
    return render_template('ranking.html',user=user)

# the advice page
@app.route('/user/advises')
@login_required
def advises():
    user = g.user
    return render_template('advises.html',user=user)

# the overview page
@app.route('/user/overview')
@login_required
def overview():
    user = g.user
    return render_template('overview.html',user=user)

# related to the one in oauth.py, the authorization of provider
@app.route('/authorize/<provider>')
def oauth_authorize(provider):
    if not current_user.is_anonymous:
        return redirect(url_for('index'))
    oauth = OAuthSignIn.get_provider(provider)
    return oauth.authorize()

# related to the one in oauth.py, the callback of provider
@app.route('/callback/<provider>')
def oauth_callback(provider):
    if not current_user.is_anonymous:
        return redirect(url_for('index'))
    oauth = OAuthSignIn.get_provider(provider)
    username, email = oauth.callback()
    if email is None:
        flash('Authentication failed.')
        return redirect(url_for('index'))
    user = User.query.filter_by(email=email).first()
    if not user:
        
        nickname = username
        if nickname is None or nickname == "":
            nickname = email.split('@')[0]
        
        user = User(nickname=username, email=email)
        db.session.add(user)
        db.session.commit()
    login_user(user, True)
    return redirect(url_for('index'))

# the error handler, i.e, user will not be able to see the real error pages
@app.errorhandler(404)
def internal_error(error):
    return render_template('404.html'), 404

# the error handler, i.e, user will not be able to see the real error pages
@app.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    return render_template('500.html'), 500

# For a given file, return whether it's an allowed type or not
def allowed_file(filename):
    user = g.user
    return '.' in filename and \
        filename.rsplit('.', 1)[1] in app.config['ALLOWED_EXTENSIONS']


# Route that will process the file upload
@app.route('/upload', methods=['GET', 'POST'])
def upload_file():
    user = g.user
    if request.method == 'POST':
        file = request.files['file']
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            return redirect(url_for('uploaded_file',
                                    filename=filename,user=user))
    return render_template('upload_file.html',user=user)

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    user = g.user
    return send_from_directory(app.config['UPLOAD_FOLDER'],
                               filename)


