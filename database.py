import json,sqlite3
from datetime import datetime,timezone
class SummaryDB:
    def __init__(self,path): self.path=path; self._init_db()
    def _connect(self):
        c=sqlite3.connect(self.path); c.row_factory=sqlite3.Row; return c
    def _init_db(self):
        c=self._connect(); c.execute('CREATE TABLE IF NOT EXISTS summaries (id INTEGER PRIMARY KEY AUTOINCREMENT,title TEXT NOT NULL,original_text TEXT NOT NULL,summary TEXT NOT NULL,engine TEXT NOT NULL,summary_length TEXT NOT NULL,word_count INTEGER NOT NULL,metrics_json TEXT NOT NULL,sentence_details_json TEXT NOT NULL,created_at TEXT NOT NULL)'); c.commit(); c.close()
    def save_summary(self,r):
        c=self._connect(); cur=c.execute('INSERT INTO summaries(title,original_text,summary,engine,summary_length,word_count,metrics_json,sentence_details_json,created_at) VALUES(?,?,?,?,?,?,?,?,?)',(r['title'],r['original_text'],r['summary'],r['engine'],r['summary_length'],r['metrics']['original_words'],json.dumps(r['metrics']),json.dumps(r['sentence_details']),datetime.now(timezone.utc).isoformat())); c.commit(); rid=cur.lastrowid; c.close(); return rid
    def list_summaries(self,limit=8):
        c=self._connect(); rows=c.execute('SELECT id,title,word_count,engine,created_at FROM summaries ORDER BY id DESC LIMIT ?',(limit,)).fetchall(); c.close(); return [dict(x) for x in rows]
    def get_summary(self,rid):
        c=self._connect(); row=c.execute('SELECT * FROM summaries WHERE id=?',(rid,)).fetchone(); c.close()
        if not row:return None
        d=dict(row); d['metrics']=json.loads(d.pop('metrics_json')); d['sentence_details']=json.loads(d.pop('sentence_details_json')); return d
