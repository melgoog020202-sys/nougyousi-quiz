from flask import Flask, render_template, request, session, redirect, url_for
import pandas as pd
import random
import os

app = Flask(__name__)
app.secret_key = "quiz-secret"

CSV_URL = "https://docs.google.com/spreadsheets/d/1CeOOBmB4URYbQKe0oIhcRmsxp6oFZ3szC4r4k16N7PI/export?format=csv&gid=0"


def load_questions():
    """
    Googleスプレッドシートから問題を取得
    """

    df = pd.read_csv(CSV_URL, dtype=str)
    df = df.fillna("")

    df["回数"] = df["回数"].astype(str).str.strip()
    df["番号"] = df["番号"].astype(str).str.strip()
    df["問題"] = df["問題"].astype(str).str.strip()
    df["答え"] = df["答え"].astype(str).str.strip()

    # 空行を除去
    df = df[df["回数"] != ""]

    return df.to_dict(orient="records")


@app.route("/", methods=["GET", "POST"])
def index():

    # タイトル画面用
    questions = load_questions()

    rounds = sorted(
        {q["回数"] for q in questions},
        key=lambda x: int(x)
    )

    if request.method == "POST":

        rnd = request.form["round"].strip()

        # 選択した回だけ取得
        quiz = [
            q.copy()
            for q in questions
            if q["回数"] == rnd
        ]

        random.shuffle(quiz)

        session.clear()

        session["quiz"] = quiz
        session["round"] = rnd
        session["score"] = 0
        session["correct"] = 0
        session["wrong"] = 0
        session["total"] = len(quiz)

        return redirect(url_for("quiz"))

    return render_template(
        "index.html",
        rounds=rounds
    )


@app.route("/quiz", methods=["GET", "POST"])
def quiz():

    if "quiz" not in session:
        return redirect(url_for("index"))

    quiz = session["quiz"]

    score = session["score"]
    correct_count = session["correct"]
    wrong_count = session["wrong"]

    # 全問終了
    if len(quiz) == 0:

        return render_template(
            "index.html",
            result=True,
            score=score,
            correct=correct_count,
            wrong=wrong_count,
            total=session["total"],
            rounds=[]
        )

    current = quiz[0]

    if request.method == "POST":

        ans = request.form["answer"].strip()
        correct = current["答え"]

        if ans == correct:

            score += 5
            correct_count += 1

            session["score"] = score
            session["correct"] = correct_count

            message = f"〇 正解！ 正解：{correct}"

        else:

            wrong_count += 1

            session["wrong"] = wrong_count

            message = f"× 不正解 正解：{correct}"

        # 今の問題を削除
        quiz.pop(0)

        session["quiz"] = quiz

        # 全問終了
        if len(quiz) == 0:

            return render_template(
                "index.html",
                result=True,
                score=session["score"],
                correct=session["correct"],
                wrong=session["wrong"],
                total=session["total"],
                message=message,
                rounds=[]
            )

        current = quiz[0]

        return render_template(
            "index.html",
            playing=True,
            current=current,
            score=session["score"],
            left=len(quiz),
            message=message,
            rounds=[]
        )

    return render_template(
        "index.html",
        playing=True,
        current=current,
        score=session["score"],
        left=len(quiz),
        rounds=[]
    )


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
