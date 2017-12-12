#!/usr/bin/env python
# -*- coding: utf-8 -*-
#Week13


from flask import Flask, render_template, request, session, g, redirect, url_for, abort, flash
from contextlib import closing
import time, os, sqlite3, re

DATABASE = 'hw13.db'
DEBUG = True
SECRET_KEY = 'development key'
USERNAME = 'admin'
PASSWORD = 'password'

app = Flask(__name__)

app.config.from_object(__name__)
app.config.from_envvar('Flaskr_settings', silent=True)


def connect_db():
    return sqlite3.connect(app.config['DATABASE'])


def init_db():
    with closing(connect_db()) as db:
        with app.open_resource('schema.sql', mode='r') as f:
            db.cursor().executescript(f.read())
        db.commit()


@app.before_request
def before_request():
    g.db = connect_db()


@app.teardown_request
def teardown_request(exception):
    db = getattr(g, 'db', None)
    if db is not None:
        db.close()


@app.route('/')
def index():
    return redirect('/login')


@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        user = request.form['username']
        password = request.form['password']
        if user != app.config['USERNAME']:
            error = 'Invalid username'
        elif password != app.config['PASSWORD']:
            error = 'Invalid password'
        else:
            session['logged_in'] = True
            flash('You were logged in')
            return redirect('/dashboard')
    return render_template('login.html', error=error)


@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    flash('You were logged out')
    return redirect('/login')


@app.route('/dashboard')
def dashboard():
    cur = g.db.execute('select id, first_name, last_name from student order by id asc')
    students = cur.fetchall()

    cur2 = g.db.execute('select id, subject, num_questions, date from quiz order by id asc')
    quizzes = cur2.fetchall()

    return render_template('dashboard.html', students=students, quizzes=quizzes)


@app.route('/student/add', methods=['GET', 'POST'])
def add_student():
    error = None
    name_re = r"(^[a-zA-Z]+)$"
    if not session.get('logged_in'):
        abort(401)
    try:
        if request.method == 'POST':
            first = request.form['first_name']
            last = request.form['last_name']
            test1 = re.search(name_re, first)
            test2 = re.search(name_re, last)
            if test1 and test2:
                g.db.execute('insert into student (first_name, last_name) values (?,?)',
                             [first, last])
                g.db.commit()
                return redirect('/dashboard')
            else:
                error = 'Error'
    except:
        flash('Error')
    return render_template('addstudent.html', error=error)


@app.route('/quiz/add', methods=['GET', 'POST'])
def add_quiz():
    if not session.get('logged_in'):
        abort(401)
    try:
        if request.method == 'POST':
            subject = request.form['subject']
            num_questions = request.form['num_questions']
            g.db.execute('insert into quiz (subject, num_questions, date) values (?,?,?)',
                         [subject, num_questions, request.form['qdate']])
            g.db.commit()
            return redirect('/dashboard')
    except:
        flash('Error')
    return render_template('addquiz.html')


@app.route('/results/add', methods=['GET', 'POST'])
def add_results():
    if not session.get('logged_in'):
        abort(401)
    cur = g.db.execute('select id from student order by id asc')
    students = cur.fetchall()
    cur2 = g.db.execute('select id from quiz order by id asc')
    quizzes = cur2.fetchall()
    try:
        if request.method == 'POST':
            student_id = request.form['sid']
            quiz_id = request.form['qid']
            score = request.form['score']
            g.db.execute('insert into results (score, quiz_id, student_id) values (?,?,?)',
                         [score, quiz_id, student_id])
            g.db.commit()
            return redirect('/dashboard')
    except:
        flash('Error')
    return render_template('addresult.html', students=students, quizzes=quizzes)


@app.route('/student/<username>')
def show_results(username):
    sql = "SELECT score, quiz_id FROM results \
            WHERE student_id=:id"

    cur = g.db.execute(sql, {"id": username})
    results = cur.fetchall()
    return render_template('student.html', results=results)


if __name__ == '__main__':
    app.run()
