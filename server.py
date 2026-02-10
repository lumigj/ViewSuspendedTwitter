from typing import Annotated
from contextlib import asynccontextmanager

from fastapi import FastAPI, status, Query
from fastapi.responses import JSONResponse
import script
import snapshot
import threading

import psycopg
import config

global conn
cursor = None

class FetchTask:
    username: str
    current: int
    total: int
running_tasks: list[FetchTask] = []

@asynccontextmanager
async def lifespan(app: FastAPI):
    global conn
    conn = psycopg.connect(
            f"dbname={config.DATABASE_NAME} user={config.DATABASE_USERNAME} password={config.DATABASE_PASSWORD} host={config.DATABASE_HOST} port=5432",
            autocommit=True
            )

    global cursor
    cursor = conn.cursor()
    yield

def fetch_tweet_contents_worker(username: str, task: FetchTask):
    global conn
    # rows = cursor.fetchall(
    with conn.cursor() as cur:
        cur.execute(
            """
            SELECT timestamp, original FROM snapshots
            WHERE username = %s AND status = 0
            """,
            (username,))
        rows = cur.fetchall()
        task.total = len(rows)
        task.current = 0

        for row in rows:
            timestamp = row[0]
            original = row[1]

            try:
                iframe_html = snapshot.fetch_snapshot_content_iframe(timestamp, original)
                data = snapshot.extract_iframe_data(iframe_html)

                cur.execute(
                    """
                    UPDATE snapshots
                    SET status = 1
                    WHERE timestamp = %s AND original = %s
                    """,
                    (timestamp, original)
                )

                # TODO: 将剩余的元数据添加到meta字段中
                cur.execute(
                    """
                    INSERT INTO data (username, timestamp, original, author_name, text)
                    VALUES (%s, %s, %s, %s, %s)
                    """,
                    (username, timestamp, original, data["name"], data["text"])
                )
            except Exception as exc:
                cur.execute(
                    """
                    UPDATE snapshots
                    SET status = 2, error = %s
                    WHERE timestamp = %s AND original = %s
                    """,
                    (str(exc), timestamp, original)
                )
            task.current += 1

app = FastAPI(lifespan=lifespan)

@app.get("/GetTweets/{username}")
def get_tweets(username: str, timestamp: str | None = None):
    global conn
    timestamp_con = timestamp if timestamp != None else '99999999999999'
    with conn.cursor() as cur:
        cur.execute(
            """
            SELECT text, author_name FROM data
            WHERE username = %s AND timestamp < %s
            ORDER BY timestamp
            DESC
            LIMIT 50
            """,
            (username, timestamp_con)
        )
        rows = cur.fetchall()
        data = []
        
        for row in rows:
            data.append(dict(zip(
                ["text", "author_name"],
                row
            )))

        return {"status": "success", "data": data}

@app.get("/GetAllTasks")
def get_all_tasks():
    ts = []
    for t in running_tasks:
        ts.append({"username": t.username, "current": t.current, "total": t.total})
    return {"status": "success", "tasks": ts}

@app.get("/GetFetchTaskProgress/{username}")
def get_fetch_task_progress(username: str):
    task = None
    for t in running_tasks:
        if t.username == username:
            task = t
            break
    if task == None:
        return {"status": "no_task"}
    else:
        return {"status": "running", "current": task.current, "total": task.total}

@app.post("/Admin/FetchTweetsIndex/{username}")
def fetch_tweets_index(username: str):
    # return JSONResponse(status_code=status.HTTP_202_ACCEPTED, content={})
    rows = []
    try:
        rows = script.fetch_cdx_rows(username)
    except:
        return JSONResponse(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, content={"status": "failed"})
    
    if len(rows) == 0:
        return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST, content={"status": "no_user"})
    else:
        global conn
        with conn.cursor() as cur:
            cur.executemany(
                """
                INSERT INTO snapshots (username, timestamp, original)
                VALUES (%s, %s, %s)
                ON CONFLICT DO NOTHING;
                """,
                [(username, row[0], row[1]) for row in rows]
            )
        return {"status": "success"}

@app.post("/Admin/FetchTweetContents/{username}")
def fetch_tweet_contents(username: str):
    running = False
    for t in running_tasks:
        if t.username == username:
            running = True
            break
    if running:
        return JSONResponse(status_code=status.HTTP_202_ACCEPTED, content={"status": "running"})
    
    task = FetchTask()
    task.username = username
    running_tasks.append(task)

    worker = threading.Thread(target=fetch_tweet_contents_worker, args=(username,task))
    worker.start()

    return JSONResponse(status_code=status.HTTP_202_ACCEPTED, content={"status": "launched"})
