from flask import Flask, render_template, request, session, redirect, url_for
import pandas as pd
import random
import os

app = Flask(__name__)
app.secret_key = "quiz-secret"

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
excel_path = os.path.join(BASE_DIR, "nougyousi-quiz.xlsx")

df = pd.read_excel(excel_path, dtype=str)

questions = df.to_dict(orient="records")

@app.route("/", methods=["GET","POST"])
def index():
    if request.method=="POST" and "start" in request.form:
        rnd = request.form["round"]
        qs=[q.copy() for q in questions if q["回数"]==rnd]
        random.shuffle(qs)
        session["round"]=rnd
        session["score"]=0
        session["total"]=len(qs)
        session["questions"]=qs
        return redirect(url_for("quiz"))
    rounds=[str(i) for i in range(1,15)]
    return render_template("index.html", rounds=rounds)

@app.route("/quiz", methods=["GET","POST"])
def quiz():
    if "questions" not in session:
        return redirect(url_for("index"))
    qs=session["questions"]
    score=session["score"]
    if not qs:
        return render_template("index.html", rounds=[str(i) for i in range(1,15)],
                               result=True, score=score, total=session["total"])
    current=qs[0]
    if request.method=="POST":
        ans=request.form["answer"].strip()
        correct= current["答え"]
        if ans==correct:
            score+=5
            session["score"]=score
            msg=f"〇 正解！ 正解：{correct}"
        else:
            msg=f"× 不正解 正解：{correct}"
        qs.pop(0)
        session["questions"]=qs
        if not qs:
            return render_template("index.html", rounds=[str(i) for i in range(1,15)],
                                   result=True, score=score, total=session["total"], message=msg)
        current=qs[0]
        return render_template("index.html", rounds=[str(i) for i in range(1,15)],
                               playing=True,current=current,score=score,
                               left=len(qs),message=msg)
    return render_template("index.html", rounds=[str(i) for i in range(1,15)],
                           playing=True,current=current,score=score,left=len(qs))

if __name__=="__main__":
    app.run(debug=True)
