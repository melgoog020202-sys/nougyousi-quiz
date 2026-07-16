from flask import Flask, render_template, request, session, redirect, url_for
import pandas as pd
import random
import os

app = Flask(__name__)
app.secret_key = "quiz-secret"

CSV_URL = "https://docs.google.com/spreadsheets/d/1CeOOBmB4URYbQKe0oIhcRmsxp6oFZ3szC4r4k16N7PI/export?format=csv&gid=0"

df = pd.read_csv(CSV_URL, dtype=str)
questions = df.fillna("").to_dict(orient="records")

def load_questions():

    CSV_URL = "https://docs.google.com/spreadsheets/d/1CeOOBmB4URYbQKe0oIhcRmsxp6oFZ3szC4r4k16N7PI/export?format=csv&gid=0"

    df = pd.read_csv(CSV_URL, dtype=str)

    return df.fillna("").to_dict(orient="records")

questions = load_questions()

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
    rounds.append("404")
    return render_template("index.html", rounds=rounds)

@app.route("/quiz", methods=["GET","POST"])
def quiz():
    if "questions" not in session:
        return redirect(url_for("index"))
    qs=session["questions"]
    score=session["score"]
    session["correct"] = 0
    session["wrong"] = 0
    if not qs:
        return render_template("index.html", rounds=[str(i) for i in range(1,16)],
                               result=True, score=score, total=session["total"])
    current=qs[0]
    if request.method=="POST":
        ans=request.form["answer"].strip()
        correct= current["答え"]
        if ans==correct:
            score+=5
            session["correct"] += 1
            session["score"]=score
            msg=f"〇 正解！ 正解：{correct}"
        else:
            session["wrong"] += 1
            msg=f"× 不正解 正解：{correct}"
        qs.pop(0)
        session["questions"]=qs
        if not qs:
            return render_template("index.html", rounds=[str(i) for i in range(1,15),rounds.append("404")
                                                        ],
                                   result=True, score=score, total=session["total"], message=msg)correct=session["correct"],wrong=session["wrong"]
            
        current=qs[0]
        return render_template("index.html", rounds=[str(i) for i in range(1,15),rounds.append("404")
                                                    ],
                               playing=True,current=current,score=score,
                               left=len(qs),message=msg)
    return render_template("index.html", rounds=[str(i) for i in range(1,15),rounds.append("404")
                                                ],
                           playing=True,current=current,score=score,left=len(qs))

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
