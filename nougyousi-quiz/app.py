from flask import Flask, render_template, request, session, redirect, url_for
import pandas as pd
import random
import os

app = Flask(__name__)
app.secret_key = "quiz-secret"

CSV_URL = "https://docs.google.com/spreadsheets/d/1CeOOBmB4URYbQKe0oIhcRmsxp6oFZ3szC4r4k16N7PI/export?format=csv&gid=0"

def load_questions():
    df = pd.read_csv(CSV_URL, dtype=str)
    return df.fillna("").to_dict(orient="records")

questions = load_questions()

@app.route("/", methods=["GET", "POST"])
def index():

    # Googleスプレッドシートから回数一覧を自動取得
    rounds = sorted(
        {str(q["回数"]).strip() for q in questions},
        key=lambda x: int(x)
    )

    if request.method == "POST" and "start" in request.form:
        print(request.form)
        rnd = str(request.form["round"]).strip()
        print("受け取った回数:", rnd)

        qs = [
            q.copy()
            for q in questions
            if str(q["回数"]).strip() == rnd
        ]

        random.shuffle(qs)

        session["round"] = rnd
        session["score"] = 0
        session["correct"] = 0
        session["wrong"] = 0
        session["total"] = len(qs)
        session["questions"] = qs

        return redirect(url_for("quiz"))

    return render_template("index.html", rounds=rounds)


@app.route("/quiz", methods=["GET", "POST"])
def quiz():

    if "questions" not in session:
        return redirect(url_for("index"))

    qs = session["questions"]
    score = session["score"]

    rounds = sorted(
        {str(q["回数"]).strip() for q in questions},
        key=lambda x: int(x)
    )

    if not qs:
        return render_template(
            "index.html",
            rounds=rounds,
            result=True,
            score=score,
            total=session["total"],
            correct=session["correct"],
            wrong=session["wrong"]
        )

    current = qs[0]

    if request.method == "POST":

        ans = request.form["answer"].strip()
        correct_answer = current["答え"].strip()

        if ans == correct_answer:
            score += 5
            session["score"] = score
            session["correct"] += 1
            msg = f"〇 正解！ 正解：{correct_answer}"
        else:
            session["wrong"] += 1
            msg = f"× 不正解　正解：{correct_answer}"

        qs.pop(0)
        session["questions"] = qs

        if not qs:
            return render_template(
                "index.html",
                rounds=rounds,
                result=True,
                score=score,
                total=session["total"],
                correct=session["correct"],
                wrong=session["wrong"],
                message=msg
            )

        current = qs[0]

        return render_template(
            "index.html",
            rounds=rounds,
            playing=True,
            current=current,
            score=score,
            correct=session["correct"],
            wrong=session["wrong"],
            left=len(qs),
            message=msg
        )

    return render_template(
        "index.html",
        rounds=rounds,
        playing=True,
        current=current,
        score=score,
        correct=session["correct"],
        wrong=session["wrong"],
        left=len(qs)
    )


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
