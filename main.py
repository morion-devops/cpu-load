from flask import Flask, render_template
from cpu_load_generator import load_all_cores
from dotenv import load_dotenv
import psycopg2
from psycopg2.extras import RealDictCursor

load_dotenv()

app = Flask(__name__)
connection = psycopg2.connect(cursor_factory=RealDictCursor) # variables for connect reads from environment variables, include .env-file
cursor = connection.cursor()

# Check last_run
def check_last_load():
  cursor.execute("\
    SELECT last.last_run + INTERVAL '1 minutes' as wait_until, can.can_load \
    FROM ( \
      SELECT max(last_run) as last_run \
      FROM cpu_load_table \
      HAVING count(*) > 0 \
    ) as last \
    left join ( \
      SELECT max(last_run) as last_run, 1 as can_load \
      FROM cpu_load_table \
      WHERE current_timestamp > ( \
        select max(last_run) + INTERVAL '1 minutes' \
        from cpu_load_table \
      ) \
      limit 1 \
    ) as can \
    on last.last_run = can.last_run \
    ; \
  ")
  connection.commit() # need for properly work current_timestamp

  return cursor.fetchone()

# generate cpu-load and write timestamp to db
def generate_load():
  cursor.execute("\
    insert into cpu_load_table \
    values (current_timestamp); \
  ")
  connection.commit()
  load_all_cores(duration_s=20, target_load=0.7)

@app.route("/")
def index():
  return render_template('index.html')

@app.route('/generate/')
def generate():
  result = check_last_load()
  if (result is None or result['can_load']):
    generate_load()
    return render_template('generated.html')
  else:
    return render_template('need_wait.html', wait_until = result['wait_until'].strftime("%H:%M:%S"))
if __name__ == "__main__":
  app.run(host='0.0.0.0')