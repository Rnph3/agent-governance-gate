#!/usr/bin/env python3
"""Local-only agent governance prototype: durable requests, human gate, audit trail.

This tool NEVER sends network requests or executes external actions. Approval tokens here are
manual demo strings, NOT production authentication. No real publication, trade or payment.
"""
from __future__ import annotations
import json,sqlite3,time,uuid
from pathlib import Path

SAFE={'READ','DRAFT'}
NEEDS_REVIEW={'PUBLISH_PREVIEW'}
FORBIDDEN={'TRADE','PAYMENT','WRITE_SHARED_COMMITMENT','EXTERNAL_MESSAGE'}
ALL=SAFE|NEEDS_REVIEW|FORBIDDEN

class Denied(Exception):pass
class Gate:
    def __init__(self,path):
        self.path=str(path)
        with self.connect() as d:
            d.execute('''CREATE TABLE IF NOT EXISTS requests(id TEXT PRIMARY KEY, type TEXT NOT NULL, payload TEXT NOT NULL, status TEXT NOT NULL, owner TEXT NOT NULL, created_at REAL NOT NULL, updated_at REAL NOT NULL)''')
            d.execute('''CREATE TABLE IF NOT EXISTS audit(seq INTEGER PRIMARY KEY AUTOINCREMENT, request_id TEXT, event TEXT NOT NULL, detail TEXT, happened REAL NOT NULL)''')
    def connect(self):return sqlite3.connect(self.path,timeout=20)
    def audit(self,conn,request_id,event,detail=''):
        conn.execute('INSERT INTO audit(request_id,event,detail,happened) VALUES (?,?,?,?)',(request_id,event,detail,time.time()))
    def request(self,kind,payload,owner):
        if kind not in ALL:raise ValueError('Unknown action type; fail closed')
        if not owner.strip():raise ValueError('Owner required')
        request_id=str(uuid.uuid4());status='BLOCKED' if kind in FORBIDDEN else ('REVIEW_REQUIRED' if kind in NEEDS_REVIEW else 'READY_LOCAL')
        with self.connect() as d:
            t=time.time();d.execute('INSERT INTO requests VALUES(?,?,?,?,?,?,?)',(request_id,kind,json.dumps(payload),status,owner,t,t))
            self.audit(d,request_id,'REQUESTED',kind)
            if status=='BLOCKED':self.audit(d,request_id,'DENIED','Action is structurally forbidden')
        return request_id,status
    def approve(self,request_id,reviewer,assertion):
        # In a production system identity must be verified by an external IdP. This is a DEMO only.
        if not reviewer.strip() or assertion!='I_EXPLICITLY_APPROVE_THIS_SIMULATION':raise Denied('Explicit human review assertion required')
        with self.connect() as d:
            row=d.execute('SELECT status FROM requests WHERE id=?',(request_id,)).fetchone()
            if not row:raise KeyError('Unknown request')
            if row[0]!='REVIEW_REQUIRED':raise Denied('Only review-required previews can be approved')
            d.execute('UPDATE requests SET status=?,updated_at=? WHERE id=?',('APPROVED_FOR_SIMULATION',time.time(),request_id))
            self.audit(d,request_id,'HUMAN_APPROVED_DEMO',reviewer)
    def execute_local(self,request_id):
        with self.connect() as d:
            row=d.execute('SELECT type,status,payload FROM requests WHERE id=?',(request_id,)).fetchone()
            if not row:raise KeyError('Unknown request')
            kind,status,payload=row
            if kind in FORBIDDEN or status not in ('READY_LOCAL','APPROVED_FOR_SIMULATION'):
                self.audit(d,request_id,'EXECUTION_BLOCKED',f'{kind} status={status}')
                raise Denied('No permitted local operation')
            # The only result is a local JSON preview, never an API call or a shared-state write.
            response={'simulation':True,'action':kind,'payload':json.loads(payload),'external_effects':False}
            d.execute('UPDATE requests SET status=?,updated_at=? WHERE id=?',('SIMULATED_ONLY',time.time(),request_id))
            self.audit(d,request_id,'SIMULATED_ONLY',kind)
            return response
    def history(self):
        with self.connect() as d:
            return [dict(seq=seq,id=rid,event=ev,detail=detail) for seq,rid,ev,detail in d.execute('SELECT seq,request_id,event,detail FROM audit ORDER BY seq')]
