# EvalGate + Northpeak kit: setup steps

Run every command in the VS Code Terminal, inside your `evalgate` project folder, with `(.venv)` showing.

## 1. Save your current work first
    git add .
    git commit -m "Week 2 work before Northpeak kit"
    git push

## 2. Copy the kit into your project
Unzip `northpeak_evalgate_kit.zip` (it lands in Downloads), then from your project folder:

    cp -R ~/Downloads/northpeak_evalgate_kit/* .

This adds `data/northpeak/` (619 documents), `evalgate/` (the product), `prompts/northpeak-*.yaml`,
`assistant_config.yaml` and `evalgate.yaml`, and replaces `rag.py`, `ask.py`, `app.py` and `chat_app.py`.
Your old versions are safe in Git.

## 3. Build the Northpeak index and ask one question
    python ask.py northpeak-v1 "What is the daily meal limit for international travel?"

First run builds the index (a minute or two). Expected answer: $90 per day.
Run it again: it should say "Loaded saved 'northpeak' index with ... chunks". Note the number.

## 4. Start the assistant (Terminal 1, leave running)
    uvicorn app:app

## 5. Optional: the chat page (Terminal 2)
    streamlit run chat_app.py

Good demo questions:
- What is the warranty on a Picker robot delivered in March 2026?   (2 years: a date-based exception)
- What does error E104 mean on an NP-300 Hauler?                     (emergency stop, not wheel motor)
- How many unused PTO days can I carry over?                         (5 days; an archived version says 10)
- What is the salary range for a Senior Engineer?                    (must refuse)

## 6. Save the baseline (Terminal 2 or 3)
    python -m evalgate run --version northpeak-v1 --sample 30 --save-baseline

About 5 to 10 minutes. The baseline will probably not be 100%: that is real and fine.
The gate's job is to make sure changes are never worse than the baseline.

## 7. Incident 1: a risky prompt edit
    python -m evalgate run --version northpeak-v2-short --sample 30

Expected: Decision BLOCK, with reasons. Open the report in `evalgate/reports/`
(click the .md file, then Cmd+Shift+V for a formatted preview). If it is not blocked, that is also
a finding: write down what happened.

## 8. Incident 3 preview: what does a policy change affect?
    python -m evalgate impact meal_intl

## 9. Commit and push
    git add .
    git commit -m "Northpeak document set and EvalGate v0.1 (engine, test set, gate, reports)"
    git push

## Screenshots for the status update
1. Step 3 answer with sources.  2. Chat page with one good answer.  3. The baseline result.
4. The BLOCK result in the Terminal.  5. The BLOCK report preview.  6. The impact command output.
