"""Blender 5.2: render the approved puppy as transparent animation cells.

blender -b --python tools/puppy/render.py -- --output-dir /absolute/build/path
The model and lighting are kept in source.blend; no external textures are needed.
"""
import bpy, math, json, sys, argparse, os, datetime, ctypes
from pathlib import Path
from mathutils import Vector

args=argparse.ArgumentParser();args.add_argument('--output-dir',required=True)
opt=args.parse_args(sys.argv[sys.argv.index('--')+1:])
OUT=Path(opt.output_dir).resolve();OUT.mkdir(parents=True,exist_ok=True)
HERE=Path(__file__).resolve().parent
record={'pid':os.getpid(),'executable':bpy.app.binary_path,'workingDirectory':str(Path.cwd()),'purpose':'Render transparent puppy animation assets','keepRunning':False}
if os.name=='nt':
    class FT(ctypes.Structure):_fields_=[('lo',ctypes.c_uint32),('hi',ctypes.c_uint32)]
    k=ctypes.windll.kernel32;k.GetCurrentProcess.restype=ctypes.c_void_p;k.GetProcessTimes.argtypes=[ctypes.c_void_p]+[ctypes.POINTER(FT)]*4
    times=[FT() for _ in range(4)];k.GetProcessTimes(k.GetCurrentProcess(),*[ctypes.byref(t) for t in times])
    start=datetime.datetime(1601,1,1,tzinfo=datetime.timezone.utc)+datetime.timedelta(microseconds=((times[0].hi<<32)+times[0].lo)//10)
    record['startTime']=start.isoformat()
(OUT/'render-process.json').write_text(json.dumps(record,indent=2))
bpy.ops.wm.open_mainfile(filepath=str(HERE/'source.blend'))
scene=bpy.context.scene;scene.frame_set(1)
root=bpy.data.objects['PUPPY / squash and jump'];head=bpy.data.objects['Head / curious tilt']
parts=[root]+list(root.children_recursive)
for o in bpy.data.objects:
    o.animation_data_clear()
    if o not in parts and o.type not in ('LIGHT','CAMERA'):o.hide_render=True
poses={o.name:(o.location.copy(),o.rotation_euler.copy(),o.scale.copy()) for o in parts}
scene.render.film_transparent=True;scene.render.resolution_x=320;scene.render.resolution_y=320;scene.render.resolution_percentage=100
scene.render.image_settings.file_format='PNG';scene.render.image_settings.color_mode='RGBA';scene.cycles.samples=24
scene.camera.data.ortho_scale=4.3
scene.camera.location=(2.1,-10,4.0)
scene.camera.rotation_euler=(Vector((0,0,1.78))-scene.camera.location).to_track_quat('-Z','Y').to_euler()
try:
    prefs=bpy.context.preferences.addons['cycles'].preferences;prefs.compute_device_type='OPTIX';prefs.get_devices()
    if any(d.type=='OPTIX' for d in prefs.devices):
        for d in prefs.devices:d.use=d.type=='OPTIX'
        scene.cycles.device='GPU'
except Exception:pass

dark=bpy.data.materials['Eyes and smile / chocolate'];tongue_mat=bpy.data.materials['Cheeks / apricot']
extra=[]
def curve(name,pts,r):
    c=bpy.data.curves.new(name,'CURVE');c.dimensions='3D';c.resolution_u=16;c.bevel_depth=r;c.bevel_resolution=3
    s=c.splines.new('BEZIER');s.bezier_points.add(len(pts)-1)
    for p,co in zip(s.bezier_points,pts):p.co=co;p.handle_left_type='AUTO';p.handle_right_type='AUTO'
    o=bpy.data.objects.new(name,c);bpy.context.collection.objects.link(o);o.parent=head;o.data.materials.append(dark);extra.append(o);return o
closed=[]
for sign in (-1,1):
    x=sign*.335;closed.append(curve('Happy closed eye '+str(sign),[(x-.10,-.650,.49),(x,-.675,.57),(x+.10,-.650,.49)],.022))
frown=curve('Gentle try again mouth',[(-.13,-.766,.09),(0,-.789,.16),(.13,-.766,.09)],.018)
def oval(name,loc,scale,mat):
    bpy.ops.mesh.primitive_uv_sphere_add(segments=40,ring_count=24)
    o=bpy.context.object;o.name=name;o.parent=head;o.location=loc;o.scale=scale;o.data.materials.append(mat)
    for p in o.data.polygons:p.use_smooth=True
    extra.append(o);return o
mouth=oval('Open smile',(0,-.779,.085),(.125,.035,.105),dark)
tongue=oval('Little pink tongue',(0,-.814,.035),(.073,.015,.035),tongue_mat)
eyes=[bpy.data.objects['Eye blink '+str(s)] for s in (-1,1)]
ears=[bpy.data.objects['Ear pivot '+str(s)] for s in (-1,1)]
arms=[bpy.data.objects['Front paw pivot '+str(s)] for s in (-1,1)]
normal_mouth=[o for o in parts if o.name.startswith('Smile ') or o.name=='Philtrum']
brows=[o for o in parts if o.name.startswith('Eyebrow ')]

clips=[('normal',24),('happy',20),('sad',16),('wow',12),('lookLeft',12),('lookRight',12)]
manifest={'cell':320,'columns':8,'fps':15,'clips':{},'crop':[44,18,232,218]}
(OUT/'frames').mkdir(exist_ok=True)
frame=0
for mood,count in clips:
    manifest['clips'][mood]={'start':frame,'count':count}
    for i in range(count):
        u=i/max(1,count-1);wave=math.sin(u*math.tau)
        for o in parts:
            p=poses[o.name];o.location=p[0];o.rotation_euler=p[1];o.scale=p[2];o.hide_render=False
        for o in extra:o.hide_render=True
        root.scale.z=1+.006*wave
        bpy.data.objects['Tail / wag'].rotation_euler.y=.15*math.sin(u*math.tau*2)
        bpy.data.objects['Tail / wag'].rotation_euler.z=.23*math.sin(u*math.tau*2)
        for j,e in enumerate(ears):e.rotation_euler.y=(-1 if j else 1)*.025*wave
        if mood=='normal':
            head.rotation_euler.y=.025*wave
            blink=max(.07,1-abs(i-14)*.93) if abs(i-14)<2 else 0
            if 13<=i<=15:
                for e in eyes:e.scale.z=.08 if i==14 else .55
        elif mood=='happy':
            for e in eyes:
                for child in e.children:child.hide_render=True
            for o in normal_mouth:o.hide_render=True
            for o in closed+[mouth,tongue]:o.hide_render=False
            jump=math.sin(math.pi*max(0,min(1,(u-.15)/.62))) if .15<u<.77 else 0
            root.location.z=.29*jump
            head.rotation_euler.y=-.055*wave
            for j,a in enumerate(arms):a.rotation_euler.y=(1 if j==0 else -1)*(.15+.50*jump)
            for j,e in enumerate(ears):e.rotation_euler.y=(1 if j==0 else -1)*(.12*jump+.06*wave)
            if .02<u<.15:root.scale=(1.035,1.035,.96)
            if .77<u<.90:root.scale=(1.04,1.04,.95)
        elif mood=='sad':
            for o in normal_mouth:o.hide_render=True
            frown.hide_render=False
            head.rotation_euler.z=.075*math.sin(u*math.tau*2)*math.sin(u*math.pi)
            head.rotation_euler.x=.035
            for j,b in enumerate(brows):b.rotation_euler.y=(1 if j else -1)*.20
            for e in eyes:e.scale.z=.84
        elif mood=='wow':
            for o in normal_mouth:o.hide_render=True
            mouth.hide_render=False;mouth.scale=(.072,.035,.10)
            for e in eyes:e.scale=(1.12,1,1.12)
            head.rotation_euler.x=-.035
            for b in brows:b.location.z=.055
        else:
            direction=-1 if mood=='lookLeft' else 1
            head.rotation_euler.z=direction*.16
            head.rotation_euler.x=.07
            head.rotation_euler.y=direction*.025*wave
        if mood!='wow':mouth.scale=(.125,.035,.105)
        scene.render.filepath=str(OUT/'frames'/f'puppy-{frame:03d}.png');bpy.ops.render.render(write_still=True)
        frame+=1

# Table paw: the same cream material and soft studio lighting as the character.
for o in parts+extra:o.hide_render=True
bpy.ops.mesh.primitive_uv_sphere_add(segments=48,ring_count=32)
paw=bpy.context.object;paw.name='Table paw';paw.scale=(.34,.25,.18);paw.data.materials.append(bpy.data.materials['Face / butter cream'])
for p in paw.data.polygons:p.use_smooth=True
for x in (-.09,.09):
    o=curve('Paw toe',[(x,-.225,.02),(x,-.24,.075),(x,-.205,.12)],.009);o.parent=None
    o.data.materials.clear();o.data.materials.append(bpy.data.materials['Vanilla / warm ivory']);o.hide_render=False
scene.camera.location=(0,-4,2.4);scene.camera.rotation_euler=(Vector((0,0,0))-scene.camera.location).to_track_quat('-Z','Y').to_euler();scene.camera.data.ortho_scale=.86
scene.render.resolution_x=160;scene.render.resolution_y=96
scene.render.filepath=str(OUT/'paw.png');bpy.ops.render.render(write_still=True)
manifest['frames']=frame;manifest['rows']=math.ceil(frame/8)
(OUT/'manifest.json').write_text(json.dumps(manifest,indent=2))
print('PUPPY_ASSETS_COMPLETE',flush=True)
