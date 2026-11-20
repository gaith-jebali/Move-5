from http.server import ThreadingHTTPServer,SimpleHTTPRequestHandler
from pathlib import Path
from urllib.parse import urlparse
import json,time,socket,threading,io,qrcode,random,os
ROOT=Path(__file__).parent; PORT=int(os.environ.get('PORT','8000')); lock=threading.Lock()
MOVES=[{'t':'Dumbbell Curls','i':'💪','n':'12 controlled reps','tip':'Keep elbows close to your sides. Do not swing the dumbbell.'},{'t':'Overhead Triceps','i':'🏋️','n':'10 controlled reps','tip':'Use one light dumbbell with both hands. Keep elbows forward.'},{'t':'Squats','i':'🦵','n':'15 reps','tip':'Sit back, keep chest lifted, and use a chair if needed.'},{'t':'Wall Push-Ups','i':'🧱','n':'15 reps','tip':'Use a stable wall and keep your body straight.'},{'t':'High Knees','i':'⚡','n':'20 alternating reps','tip':'Stay tall. March instead if needed.'},{'t':'Calf Raises','i':'🦶','n':'20 reps','tip':'Hold a stable surface and lower with control.'}]
ALLOWED={'index.html','icon.svg','manifest.webmanifest'}
state={'phase':'lobby','players':[],'challenge':None,'startedAt':None}
def ip():
 s=socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
 try:s.connect(('8.8.8.8',80));return s.getsockname()[0]
 except:return '127.0.0.1'
 finally:s.close()
PUBLIC_URL=os.environ.get('PUBLIC_URL','').rstrip('/')
JOIN=(PUBLIC_URL if PUBLIC_URL else f'http://{ip()}:{PORT}')+'/?join=1'
def public():
 with lock:return {'phase':state['phase'],'players':[dict(x) for x in state['players']],'challenge':state['challenge'],'startedAt':state['startedAt'],'joinUrl':JOIN}
class H(SimpleHTTPRequestHandler):
 def translate_path(self,path):
  name=urlparse(path).path.lstrip('/') or 'index.html'
  return str(ROOT/(name if name in ALLOWED else '__not_found__'))
 def reply(self,obj,code=200):
  b=json.dumps(obj,ensure_ascii=False).encode();self.send_response(code);self.send_header('Content-Type','application/json; charset=utf-8');self.send_header('Cache-Control','no-store');self.send_header('Content-Length',len(b));self.end_headers();self.wfile.write(b)
 def do_GET(self):
  if self.path.startswith('/api/state'):return self.reply(public())
  if self.path.startswith('/qr.png'):
   img=qrcode.make(JOIN);buf=io.BytesIO();img.save(buf,'PNG');b=buf.getvalue();self.send_response(200);self.send_header('Content-Type','image/png');self.send_header('Content-Length',len(b));self.end_headers();return self.wfile.write(b)
  return super().do_GET()
 def do_POST(self):
  n=min(int(self.headers.get('Content-Length','0')),20000);data=json.loads(self.rfile.read(n) or b'{}');p=urlparse(self.path).path
  with lock:
   if p=='/api/join':
    if state['phase']!='lobby':return self.reply({'ok':False,'error':'The match has already started.'},409)
    name=''.join(c for c in str(data.get('name','')) if c.isalnum() or c in ' _-')[:18].strip()
    if not name:return self.reply({'ok':False,'error':'Invalid nickname.'},400)
    old=next((x for x in state['players'] if x['id']==data.get('id')),None)
    if old:old['name']=name
    else:state['players'].append({'id':data.get('id'),'name':name,'finished':False,'finishMs':None})
    return self.reply({'ok':True,'name':name})
   if p=='/api/start':
    if not state['players']:return self.reply({'ok':False,'error':'No players joined.'},400)
    state['challenge']=random.choice(MOVES);state['startedAt']=int(time.time()*1000)+3500;state['phase']='countdown'
    for x in state['players']:x.update(finished=False,finishMs=None)
    threading.Timer(3.5,lambda:state.update(phase='running')).start();return self.reply({'ok':True})
   if p=='/api/finish':
    x=next((x for x in state['players'] if x['id']==data.get('id')),None)
    if not x or state['phase'] not in ('running','results'):return self.reply({'ok':False},400)
    if not x['finished']:x['finished']=True;x['finishMs']=max(0,int(time.time()*1000)-state['startedAt'])
    if all(y['finished'] for y in state['players']):state['phase']='results'
    return self.reply({'ok':True})
   if p=='/api/reset':state.update(phase='lobby',players=[],challenge=None,startedAt=None);return self.reply({'ok':True})
  self.reply({'ok':False},404)
 def log_message(self,fmt,*args):pass
print('\nMOVE 5 MULTI MATCH\nHost: '+f'http://localhost:{PORT}'+'\nPlayers: '+JOIN+'\nKeep this terminal open. All phones must use the same Wi-Fi.\n')
ThreadingHTTPServer(('0.0.0.0',PORT),H).serve_forever()
