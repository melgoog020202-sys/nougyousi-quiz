from flask import Flask, render_template, request, session, redirect, url_for
import pandas as pd
import random
import os

app = Flask(__name__)
app.secret_key = "quiz-secret"

CSV_URL = "https://docs.google.com/spreadsheets/d/1CeOOBmB4URYbQKe0oIhcRmsxp6oFZ3szC4r4k16N7PI/export?format=csv&gid=0"


def load_questions():
    df = pd.read_csv(CSV_URL, dtype=str)
    df = df.fillna("")

    # 回数・番号を文字列として扱う
    df["回数"] = df["回数"].astype(str).str.strip()
    df["番号"] = df["番号"].astype(str).str.strip()

    return df.to_dict(orient="records")


questions = load_questions()

@app.route("/", methods=["GET", "POST"])
def index():


    rounds = sorted(
        {q["回数"] for q in questions},
        key=lambda x: int(x)
    )

    if request.method == "POST":

        rnd = request.form["round"].strip()

        # 選択した回だけ取得
        qs = [q for q in questions if q["回数"] == rnd]

        # 問題番号だけシャッフル
        order = [q["番号"] for q in qs]
        random.shuffle(order)

        session.clear()

        session["round"] = rnd
        session["order"] = order
        session["index"] = 0
        session["score"] = 0
        session["correct"] = 0
        session["wrong"] = 0

        return redirect(url_for("quiz"))

    return render_template(
        "index.html",
        rounds=rounds
    )


@app.route("/quiz", methods=["GET", "POST"])
def quiz():

    if "round" not in session:
        return redirect(url_for("index"))

    questions = load_questions()

    rnd = session["round"]

    qs = [
        q for q in questions
        if q["回数"] == rnd
    ]

    # 番号順に並べる
    qs.sort(key=lambda x: int(x["番号"]))

    order = session["order"]
    idx = session["index"]

    if idx >= len(order):

        total = session["correct"] + session["wrong"]

        return render_template(
            "index.html",
            result=True,
            rounds=sorted(
                {q["回数"] for q in questions},
                key=lambda x: int(x)
            ),
            score=session["score"],
            correct=session["correct"],
            wrong=session["wrong"],
            total=total
        )

    number = order[idx]

    current = next(
        q for q in qs
        if q["番号"] == number
    )

    if request.method == "POST":

        ans = request.form["answer"].strip()
        correct = current["答え"].strip()

        if ans == correct:

            session["score"] += 5
            session["correct"] += 1

            message = f"〇 正解！　正解：{correct}"

        else:

            session["wrong"] += 1

            message = f"× 不正解　正解：{correct}"

        session["index"] += 1

        idx = session["index"]

        if idx >= len(order):

            total = session["correct"] + session["wrong"]

            return render_template(
                "index.html",
                result=True,
                rounds=sorted(
                    {q["回数"] for q in questions},
                    key=lambda x: int(x)
                ),
                score=session["score"],
                correct=session["correct"],
                wrong=session["wrong"],
                total=total,
                message=message
            )

        number = order[idx]

        current = next(
            q for q in qs
            if q["番号"] == number
        )

        return render_template(
            "index.html",
            playing=True,
            rounds=sorted(
                {q["回数"] for q in questions},
                key=lambda x: int(x)
            ),
            current=current,
            score=session["score"],
            left=len(order)-idx,
            message=message
        )

    return render_template(
        "index.html",
        playing=True,
        rounds=sorted(
            {q["回数"] for q in questions},
            key=lambda x: int(x)
        ),
        current=current,
        score=session["score"],
        left=len(order)-idx
    )


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
