# Import flash and other stuff we will need
import pandas as pd
import numpy as np
import sqlite3
import os
import requests
import json
from flask import Flask, Response, redirect, url_for, request, \
                  session, abort, render_template, escape, jsonify
from flask_login import LoginManager, UserMixin, \
                        login_required, login_user, logout_user

app = Flask(__name__)

# login info
# https://github.com/shekhargulati/flask-login-example/blob/master/flask-login-example.py

# config
app.config.update(
    DEBUG = True,
    SECRET_KEY = 'secret_xxx'
)

# flask-login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"

# silly user model
class User(UserMixin):

    def __init__(self, id):
        self.id = id
        self.name = "user" + str(id)
        self.password = self.name + "_secret"
        
    def __repr__(self):
        return "%d/%s/%s" % (self.id, self.name, self.password)

# create some users with ids 1 to 5      
users = [User(id) for id in range(1, 5)]

def create_sql_conn():
    con = sqlite3.connect("../db/votes.db")
    cur = conn.cursor()
    return con, cur

# Running without any additional route will launch the HTML form
@app.route('/')
@login_required
def form():
    return render_template('form.html')

@app.route('/votes/', methods=["GET", 'POST', "PUT"])
@login_required
def add_vote():
    if request.method == "GET" or request.method == "PUT":
        return "ERROR 404:", 404
    else:
        ijson = dict()
        ijson['county'] = request.form['county']
        ijson['precinct'] = request.form['precinct']
        ijson['round'] = request.form['round']
        ijson['buttigieg_votes'] = request.form['buttigieg_votes']
        ijson['warren_votes'] = request.form['warren_votes']
        ijson['klobuchar_votes'] = request.form['klobuchar_votes']
        ijson['biden_votes'] = request.form['biden_votes']
        ijson['yang_votes'] = request.form['yang_votes']
        ijson['sanders_votes'] = request.form['sanders_votes']
        ijson['steyer_votes'] = request.form['steyer_votes']
        ijson['gabbard_votes'] = request.form['gabbard_votes']
        ijson['other_votes'] = 0
        ijson['uncommitted_votes'] = request.form['uncommitted_votes']
        ijson['uuid'] = str(request.form['county']) + str(request.form['precinct']) + str(request.form['round'])

        # clean up dictionary
        for k,v in ijson.items():
            if v =='' and '_votes' in k:
                ijson[k] = 0

        # validate data
        mdf = submit_logic(ijson)
        try:
            assert mdf.loc[mdf['valid_submit']==0,:].shape[0] == 0
        except:
            return render_template('generic.html', titles = ['Invalid Submission -- candidates under 15% in round 2'])

        # connect to sqlite
        sqlite_insert_query = """INSERT INTO votes
                  (uuid, county, precinct, round, 
                  buttigieg_votes, warren_votes, klobuchar_votes, biden_votes, yang_votes, 
                  sanders_votes, steyer_votes, gabbard_votes, other_votes, uncommitted_votes) 
                  VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);"""
        with sqlite3.connect("../db/votes.db") as conn:
            vote_col_list = list(pd.read_sql("select * from votes", conn).columns)
        recordList = pd.DataFrame(ijson, index=[0]).loc[:, vote_col_list].get_values()
        try: 
            with sqlite3.connect("../db/votes.db") as conn:
                conn.cursor().executemany(sqlite_insert_query, recordList)
        except sqlite3.IntegrityError:
            return render_template('generic.html', titles = ['Duplicate Submission'])
        del mdf['uuid']
        return render_template('view.html',
                           tables=[mdf.to_html(classes=["table-bordered", 
                                                        "table-striped", 
                                                        "table-hover"])],
                           titles = ['Successful Submission'])

def submit_logic(curr_submit):
    # takes in a dictionary of the submission data
    idf = pd.DataFrame(curr_submit, index=[0])
    metric_cols = [i for i in idf.columns if '_votes' in i]
    for m in metric_cols:
        idf.loc[:, m] = pd.to_numeric(idf.loc[:, m], errors='coerce')
    idf.loc[:, metric_cols] = idf.loc[:, metric_cols].fillna(0).astype(float)
    idf.loc[:, metric_cols] = (idf.loc[:, metric_cols] /
                               idf.loc[:, metric_cols].sum(axis=1).values[0])

    mdf = pd.melt(idf, id_vars=['uuid','county','precinct','round'])

    # identify qualified candidates
    thresh = mdf['value'] >= .15
    uncom = mdf['variable'] == 'uncommitted_votes'
    mdf.loc[thresh | uncom, 'qual_cand'] = 1
    mdf.loc[:,'qual_cand'].fillna(0, inplace=True)

    # validate data
    rd1 = mdf['round'].astype(str)=='1'
    qual = mdf['qual_cand']==1
    zero = mdf['value']==0
    mdf.loc[rd1 | qual | zero,'valid_submit'] = 1
    mdf.loc[:,'valid_submit'].fillna(0, inplace=True)

    mdf = mdf.sort_values(['qual_cand', 'value'], ascending=[False, False]).reset_index(drop=True)
    return mdf

@app.route('/results/', methods=["GET", 'POST', "PUT"])
@login_required
def get_results():
    generate_results()
    fnl = pollster_performance()
    best = fnl.head(3).reset_index(drop=True).round(2)
    worst = fnl.tail(3).reset_index(drop=True).round(2)
    try:
        with sqlite3.connect("../db/votes.db") as conn:
            res = pd.read_sql("select * from results", conn)
    except sqlite3.IntegrityError:
        return render_template('generic.html', titles = ['Error Displaying Data'])

    # aggregate df
    cols = [c for c in res.columns if '_sde' in c]
    agg = res.loc[:,cols].sum().reset_index()
    agg.rename(columns={'index':'Candidate', 0:'Statewide Delegates'}, inplace=True)
    agg.loc[:,'Candidate'] = agg.loc[:,'Candidate'].map(lambda s: s[:-4])

    return render_template('view.html',
                           tables=[agg.round(2).to_html(classes=["table-bordered", 
                                                        "table-striped", 
                                                        "table-hover"]),
                           		   res.to_html(classes=["table-bordered", 
                                                        "table-striped", 
                                                        "table-hover"]),
                                   best.to_html(classes=["table-bordered", 
                                                        "table-striped", 
                                                        "table-hover"]),
                                   worst.to_html(classes=["table-bordered", 
                                                        "table-striped", 
                                                        "table-hover"])],
                           titles = ['Aggregate', 'Results','Best Pollster','Worst Pollster'])


def generate_results():
    with sqlite3.connect("../db/votes.db") as conn:
        # delete all previous results
        conn.cursor().execute('DELETE FROM results')
        
        # merge
        df = pd.read_sql_query("SELECT * from votes WHERE round = 2", conn)
        cd_map = pd.read_sql_query("SELECT * from precinct_d", conn)
        rdf = df.merge(cd_map, how='left', on=['county','precinct'])
        vote_cols = [c for c in rdf.columns if '_votes' in c]
        rdf.loc[:,'total_votes'] = rdf.loc[:, vote_cols].sum(axis=1)
        for c in vote_cols:
            rdf.loc[:,c[:-6]+'_sdes'] = rdf.loc[:, c] / rdf['total_votes'] * rdf['CD2SDE']
        
        del rdf['CD2SDE']
        del rdf['round']
        del rdf['total_votes']
        del rdf['uuid']

        sqlite_insert_query = """INSERT INTO results
                          (county, precinct, 
                          buttigieg_votes, warren_votes, klobuchar_votes, biden_votes, yang_votes, 
                          sanders_votes, steyer_votes, gabbard_votes, other_votes, uncommitted_votes,
                          buttigieg_sde, warren_sde, klobuchar_sde, biden_sde, yang_sde, 
                          sanders_sde, steyer_sde, gabbard_sde, other_sde, uncommitted_sde)
                          VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?,
                                  ?, ?, ?, ?, ?, ?, ?, ?);"""

        recordList = rdf.get_values()
        conn.cursor().executemany(sqlite_insert_query, recordList)

def pollster_performance():
    with sqlite3.connect("../db/votes.db") as conn:
        df = pd.read_sql_query("SELECT * from votes WHERE round = 1", conn)

    iowa = pd.read_csv('../data/538_iowa_poll.csv')
    metrics = [m for m in df.columns if '_votes' in m]
    data = df.groupby('round')[metrics].sum().reset_index()
    data = data.loc[data['round']==1,:]

    dat = pd.melt(data, id_vars='round', var_name='candidate')
    dat.loc[:,'candidate'] = dat.loc[:,'candidate'].map(lambda s: (s[:-6]).title())
    dat.loc[:,'share'] = dat.groupby('round')['value'].transform(lambda x: x/x.sum())

    res = iowa.merge(dat, how='inner', left_on=['mapped_candidate'], right_on=['candidate'])
    fnl = (res.groupby(['display_name','poll_id'])
              .apply(lambda row: rmse(row['share'], row['pct']/100))
              .reset_index())
    fnl.rename(columns={0:'rmse'}, inplace=True)
    del fnl['poll_id']

    fnl = fnl.sort_values('rmse')
    return fnl

# exploratory analysis
def rmse(pred, act):
    return np.sqrt(np.mean((pred - act)**2))

# somewhere to login
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if password == username + "_secret":
            id = username.split('user')[1]
            user = User(id)
            login_user(user)
            return redirect(request.args.get("next"))
        else:
            return abort(401)
    else:
        return render_template('login.html')

# somewhere to logout
@app.route("/logout")
# @login_required
def logout():
    logout_user()
    return render_template('generic.html', titles = ['Logged out'])

# handle login failed
@app.errorhandler(401)
def page_not_found(e):
    return render_template('generic.html', titles = ['Login failed'])
        
# callback to reload the user object        
@login_manager.user_loader
def load_user(userid):
    return User(userid)

# Report error if they pass us a string for year
@app.route("/api/v1/<string:rd>")
def foo(rd):
    return render_template('generic.html', titles = ['Sorry I can only handle integers'])

# build api
# handle /api/total and /airplane/round
@app.route("/api/v1", methods=["GET"])
@app.route("/api/v1/<int:rd>", methods=["GET"])
def results(rd=False):
    with sqlite3.connect("../db/votes.db") as conn:
        if rd is False:
            df = pd.read_sql_query("SELECT * from votes", conn)
        else:
            df = pd.read_sql_query("SELECT * from votes WHERE round = {0}".format(rd), conn)
    return jsonify(df.reset_index(drop=True).to_dict(orient='records'))


if __name__ == "__main__":
    app.run()