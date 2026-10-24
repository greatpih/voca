"""Blender 5.2: render the approved puppy as transparent animation cells.

blender -b --python tools/puppy/render.py -- --output-dir /absolute/build/path
The model and lighting are kept in source.blend; no external textures are needed.
"""
import bpy, math, json, sys, argparse, os, datetime, ctypes, importlib.util
from pathlib import Path
from mathutils import Vector

args=argparse.ArgumentParser();args.add_argument('--output-dir',required=True)
args.add_argument('--source');args.add_argument('--character',choices=['puppy','cat'],default='puppy')
opt=args.parse_args(sys.argv[sys.argv.index('--')+1:])
OUT=Path(opt.output_dir).resolve();OUT.mkdir(parents=True,exist_ok=True)
HERE=Path(__file__).resolve().parent
sys.dont_write_bytecode=True
spec=importlib.util.spec_from_file_location('pet_motion',HERE/'motion.py');motion=importlib.util.module_from_spec(spec);spec.loader.exec_module(motion)
record={'pid':os.getpid(),'executable':bpy.app.binary_path,'workingDirectory':str(Path.cwd()),'purpose':'Render transparent '+opt.character+' animation assets','keepRunning':False}
if os.name=='nt':
    class FT(ctypes.Structure):_fields_=[('lo',ctypes.c_uint32),('hi',ctypes.c_uint32)]
    k=ctypes.windll.kernel32;k.GetCurrentProcess.restype=ctypes.c_void_p;k.GetProcessTimes.argtypes=[ctypes.c_void_p]+[ctypes.POINTER(FT)]*4
    times=[FT() for _ in range(4)];k.GetProcessTimes(k.GetCurrentProcess(),*[ctypes.byref(t) for t in times])
    start=datetime.datetime(1601,1,1,tzinfo=datetime.timezone.utc)+datetime.timedelta(microseconds=((times[0].hi<<32)+times[0].lo)//10)
    record['startTime']=start.isoformat()
(OUT/'render-process.json').write_text(json.dumps(record,indent=2))
bpy.ops.wm.open_mainfile(filepath=str(Path(opt.source).resolve() if opt.source else HERE/'source.blend'))
scene=bpy.context.scene;scene.frame_set(1)
root=bpy.data.objects['CAT / squash and jump' if opt.character=='cat' else 'PUPPY / squash and jump'];head=bpy.data.objects['Head / curious tilt']
parts=[root]+list(root.children_recursive)
for o in bpy.data.objects:
    o.animation_data_clear()
    if o not in parts and o.type not in ('LIGHT','CAMERA'):o.hide_render=True
poses={o.name:(o.location.copy(),o.rotation_euler.copy(),o.scale.copy()) for o in parts}
scene.render.film_transparent=True;scene.render.resolution_x=256;scene.render.resolution_y=256;scene.render.resolution_percentage=100
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

cat=opt.character=='cat'
clips=motion.clips(cat)
manifest={'cell':256,'columns':8,'fps':motion.FPS,'version':2,'clips':{},'crop':[35,14,186,175]}
tail=bpy.data.objects['Tail / wag']
ctx=dict(root=root,head=head,tail=tail,eyes=eyes,ears=ears,arms=arms,normal_mouth=normal_mouth,brows=brows,closed=closed,mouth=mouth,tongue=tongue,frown=frown,objects=bpy.data.objects)
if cat:
    ctx['tail_splines']=[]
    for child in tail.children:
        if child.type=='CURVE':
            for spline in child.data.splines:
                ctx['tail_splines'].append((spline,[p.co.copy() for p in spline.bezier_points]))
        elif 'tip' in child.name.lower():ctx['tail_tip']=child
(OUT/'frames').mkdir(exist_ok=True)
frame=0
for mood,count in clips:
    manifest['clips'][mood]={'start':frame,'count':count,'loop':mood=='normal','poster':0 if mood=='normal' else round(count*.38)}
    for i in range(count):
        u=i/count if mood=='normal' else i/(count-1)
        for o in parts:
            p=poses[o.name];o.location=p[0];o.rotation_euler=p[1];o.scale=p[2];o.hide_render=False
        for o in extra:o.hide_render=True
        mouth.scale=(.125,.035,.105);tongue.scale=(.073,.015,.035)
        motion.pose(cat,mood,u,ctx)
        scene.render.filepath=str(OUT/'frames'/f'{opt.character}-{frame:03d}.png');bpy.ops.render.render(write_still=True)
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
print(opt.character.upper()+'_ASSETS_COMPLETE',flush=True)
