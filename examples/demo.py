from pathlib import Path
import sys,tempfile
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from gate import Gate,Denied
with tempfile.TemporaryDirectory() as folder:
    g=Gate(Path(folder)/'work.db')
    r,s=g.request('PUBLISH_PREVIEW',{'headline':'Research snapshot'},'demo_owner')
    print('request',s)
    try:g.execute_local(r)
    except Denied:print('blocked before human review: PASS')
    g.approve(r,'demo_human','I_EXPLICITLY_APPROVE_THIS_SIMULATION')
    print('result',g.execute_local(r))
    t,ts=g.request('TRADE',{'symbol':'BTC','qty':1},'demo_owner')
    print('trade request',ts)
    try:g.execute_local(t)
    except Denied:print('trading denied: PASS')
    print('audit events:',len(g.history()))
