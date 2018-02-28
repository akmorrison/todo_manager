from uuid import uuid4
import os
import shlex
import dateutil.parser
import dateutil.tz
import datetime
import fileinput
uid_map = {}
todos = []

class todo:
    text = ""
    tag = None
    end_date = None
    warning = 1
    uid = None
    done = False
    def __init__(self, text, tag = None, end_date = None, warning = None, uid = None, done = False, filename = None):
        self.text = text
        self.tag = tag
        self.end_date = end_date
        self.warning = warning
        self.filename = filename
        if uid == None:
            self.uid = str(uuid4())
            while self.uid in uid_map:
                self.uid = str(uuid4())
        else:
            self.uid = uid
        self.done = True if done.lower() == "yes" else False
        uid_map[self.uid] = self

def startup():
    parse_files()

def get_todos_upcoming():
    return filter(lambda x: not x.done, sorted(todos, key=lambda x:x.end_date))

def get_time_to_due_pretty(d):
    delta = d - datetime.datetime.now(dateutil.tz.tzoffset('EST', -60*60*5))
    due_time = d.strftime("(%-I:%M %p)")
    due_weekday = d.strftime("(%A)")
    if delta.days > 30:
        return "more than a month %s" % d.strftime("(%A)")
    elif delta.days > 21:
        return "in 3 weeks %s" % due_weekday
    elif delta.days > 14:
        return "in 2 weeks %s" % due_weekday
    elif delta.days > 7:
        return "next week %s" % due_weekday
    elif delta.days > 2:
        return "due some time this week %s" % due_weekday
    elif delta.days > 1:
        return "due tomorrow %s" % due_time
    elif delta.days == 0:
        if delta.seconds < 24 * 60 * 60 and delta.seconds > 2*60*60:
            return "in %i hours %s" % (delta.seconds / 60 / 60, due_time)
        elif delta.seconds > 45*60:
            return "in an hour %s" % due_time
        elif delta.seconds > 30 * 60:
            return "in a half-hour %s" % due_time
        else:
            return "right fucking now %s" % due_time
    else:
        return "it's already late"

def get_todos_for_api():
    retval = [{"todo":i.text,"uid":i.uid, "time":get_time_to_due_pretty(i.end_date), "done":i.done} for i in get_todos_upcoming()]
    return retval

def remove_todo_by_uid(uid):
    if not uid in uid_map:
        return "UID not recognized: %s" % str(uid_map)
    todo = uid_map[uid]
    with open('/var/www/html/flaskapp/todo/' + todo.filename, 'r') as f:
        r = f.read()
    r = r.split('\n')
    for i in range(len(r)):
        q = shlex.split(r[i], ',')
        uid = q[4]
        if todo.uid == uid:
            r[i]  = ("\"%s\" \"%s\" %s %s %s yes" % (q[0], q[1], q[2], q[3], uid))
            todo.done = True
            with open('/var/www/html/flaskapp/todo/' + todo.filename, 'w') as f:
                f.write('\n'.join(r))
            return "marked item as complete"
    return "could not locate item in file"

def parse_files():
    os.chdir('/home/ubuntu/flaskapp/todo')
    global todos
    for i in os.listdir('.'):
        if not i.endswith('.txt'):
            continue
        with open(i) as f:
            for line in f:
                if line.strip().startswith('#'):
                    continue
                q = shlex.split(line, ',')
                todos.append(todo(q[0],tag=q[1],warning=q[2],end_date=dateutil.parser.parse(q[3]), uid=q[4], done=q[5], filename=i))

def new_item(text, tags, warning, due):
    uid = str(uuid4())
    while uid in uid_map:
        uid = str(uuid4())
    with open('/var/www/html/flaskapp/todo/api.txt', 'a') as f:
        f.write("\"%s\" \"%s\" %i %s %s no\n" % (text, tags, int(warning), due, uid))
    global todos
    todos.append(todo(text, tag=tags, end_date=dateutil.parser.parse(due), warning=warning, uid=uid, done="no", filename='api.txt'))
    return "done"
