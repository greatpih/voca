"""Soft toy bakery assets, rendered with the approved pets' Blender lighting."""
import bpy, math, random, argparse, sys, json, os, datetime, ctypes
from pathlib import Path
from mathutils import Vector
p=argparse.ArgumentParser();p.add_argument('--output-dir',required=True)
opt=p.parse_args(sys.argv[sys.argv.index('--')+1:]);OUT=Path(opt.output_dir).resolve();OUT.mkdir(parents=True,exist_ok=True)
HERE=Path(__file__).resolve().parent
record=dict(pid=os.getpid(),executable=bpy.app.binary_path,workingDirectory=str(Path.cwd()),purpose='Render matching bakery room, ceramic plates and cookie assets',keepRunning=False)
class FT(ctypes.Structure):_fields_=[('lo',ctypes.c_uint32),('hi',ctypes.c_uint32)]
k=ctypes.windll.kernel32;k.GetCurrentProcess.restype=ctypes.c_void_p;k.GetProcessTimes.argtypes=[ctypes.c_void_p]+[ctypes.POINTER(FT)]*4
times=[FT() for _ in range(4)];k.GetProcessTimes(k.GetCurrentProcess(),*[ctypes.byref(t) for t in times])
record['startTime']=(datetime.datetime(1601,1,1,tzinfo=datetime.timezone.utc)+datetime.timedelta(microseconds=((times[0].hi<<32)+times[0].lo)//10)).isoformat()
(OUT/'render-process.json').write_text(json.dumps(record,indent=2))
bpy.ops.wm.open_mainfile(filepath=str(HERE.parent/'puppy/source.blend'))
scene=bpy.context.scene;scene.frame_set(1)
for o in list(bpy.data.objects):
    o.animation_data_clear()
    if o.type not in ('LIGHT','CAMERA'):bpy.data.objects.remove(o,do_unlink=True)
scene.render.engine='CYCLES';scene.cycles.samples=48;scene.cycles.use_denoising=True
scene.render.image_settings.file_format='PNG';scene.render.image_settings.color_mode='RGBA';scene.render.resolution_percentage=100
try:
    prefs=bpy.context.preferences.addons['cycles'].preferences;prefs.compute_device_type='OPTIX';prefs.get_devices()
    if any(d.type=='OPTIX' for d in prefs.devices):
        for d in prefs.devices:d.use=d.type=='OPTIX'
        scene.cycles.device='GPU'
except Exception:pass
cam=scene.camera;lights=[(o,o.location.copy(),o.data.energy,o.data.size) for o in bpy.data.objects if o.type=='LIGHT'];made=[]
def mat(name,color,rough=.62):
    m=bpy.data.materials.new(name);m.use_nodes=True;m.diffuse_color=(*color,1);bs=m.node_tree.nodes['Principled BSDF'];bs.inputs['Base Color'].default_value=(*color,1);bs.inputs['Roughness'].default_value=rough;return m
ivory=mat('Glazed oat ceramic',(.91,.86,.74),.32);mint=mat('Pistachio glaze',(.53,.74,.65),.35);lavender=mat('Lavender glaze',(.66,.57,.79),.35)
dough=mat('Golden shortbread',(.66,.35,.115),.8);edge=mat('Baked biscuit edge',(.43,.19,.055),.85);chocolate=mat('Dark chocolate',(.095,.038,.022),.5)
cream=mat('Cream icing',(.96,.84,.62),.5);jam=mat('Strawberry preserve',(.60,.08,.13),.3);rose=mat('Rose icing',(.80,.34,.44),.6)
wood=mat('Pale maple',(.69,.49,.31),.72);plaster=mat('Warm vanilla wall',(.84,.78,.67),.95);sky=mat('Window sky',(.45,.72,.78),.9);leaf=mat('Sage plant',(.25,.49,.34),.7)
def reg(o,name,ma):
    o.name=name;o.data.materials.append(ma);made.append(o)
    if hasattr(o.data,'polygons'):
        for f in o.data.polygons:f.use_smooth=True
    return o
def ball(name,loc,scale,ma):
    bpy.ops.mesh.primitive_uv_sphere_add(segments=32,ring_count=20,location=loc);o=reg(bpy.context.object,name,ma);o.scale=scale;return o
def box(name,loc,scale,ma,bevel=.1):
    bpy.ops.mesh.primitive_cube_add(size=1,location=loc);o=reg(bpy.context.object,name,ma);o.scale=scale;bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
    b=o.modifiers.new('Soft moulded edges','BEVEL');b.width=bevel;b.segments=5;o.modifiers.new('Weighted normals','WEIGHTED_NORMAL');return o
def disc(name,loc,radius,depth,ma):
    bpy.ops.mesh.primitive_cylinder_add(vertices=64,radius=radius,depth=depth,location=loc);o=reg(bpy.context.object,name,ma)
    b=o.modifiers.new('Baked round edge','BEVEL');b.width=min(depth*.3,.07);b.segments=4;o.modifiers.new('Weighted normals','WEIGHTED_NORMAL');return o
def line(name,pts,r,ma):
    c=bpy.data.curves.new(name,'CURVE');c.dimensions='3D';c.bevel_depth=r;c.bevel_resolution=4;s=c.splines.new('BEZIER');s.bezier_points.add(len(pts)-1)
    for a,co in zip(s.bezier_points,pts):a.co=co;a.handle_left_type='AUTO';a.handle_right_type='AUTO'
    o=bpy.data.objects.new(name,c);bpy.context.collection.objects.link(o);o.data.materials.append(ma);made.append(o);return o
def view(loc,target,scale,w,h,transparent=True):
    cam.location=loc;cam.rotation_euler=(Vector(target)-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.type='ORTHO';cam.data.ortho_scale=scale
    scene.render.resolution_x=w;scene.render.resolution_y=h;scene.render.film_transparent=transparent
def render(name):scene.render.filepath=str(OUT/(name+'.png'));bpy.ops.render.render(write_still=True)
def hide():
    for o in made:o.hide_render=True
def cookie(kind,r=.52,z=0,decorate=True):
    base=disc('Cookie '+kind,(0,0,z),r,.16*r/.52,chocolate if kind=='choco' else dough)
    if not decorate:return
    rand=random.Random(11)
    if kind in ('chip','choco'):
        for x,y,size in [(-.23,-.19,.07),(.19,-.22,.063),(.28,.12,.07),(-.12,.25,.06),(.02,.02,.065)]:
            o=ball('Chocolate morsel',(x,y,z+.093),(size,size*.8,.035),cream if kind=='choco' else chocolate);o.rotation_euler.z=rand.random()*3
    elif kind=='jam':
        disc('Cream ring',(0,0,z+.095),.32,.035,cream);ball('Jam heart',(0,0,z+.125),(.24,.23,.045),jam)
    elif kind=='star':
        verts=[(math.sin(i*math.pi/5)*(.32 if i%2==0 else .15),math.cos(i*math.pi/5)*(.32 if i%2==0 else .15),z+.10) for i in range(10)]
        mesh=bpy.data.meshes.new('Icing star');mesh.from_pydata(verts,[],[list(range(10))]);o=bpy.data.objects.new('Soft icing star',mesh);bpy.context.collection.objects.link(o);reg(o,o.name,cream)
        sol=o.modifiers.new('Icing thickness','SOLIDIFY');sol.thickness=.035;b=o.modifiers.new('Icing roundness','BEVEL');b.width=.025;b.segments=3
    else:
        disc('Rose icing',(0,0,z+.095),.39,.035,rose)
        for j in range(12):
            a=rand.random()*math.tau;rr=.32*math.sqrt(rand.random());o=box('Sugar sprinkle',(math.cos(a)*rr,math.sin(a)*rr,z+.13),(.075,.027,.024),[cream,mint,lavender][j%3],.012);o.rotation_euler.z=a
    # A few subtle dimples make a biscuit surface without noisy photo texture.
    for j in range(10):
        a=j*math.tau/10;ball('Biscuit pore',(math.cos(a)*.43,math.sin(a)*.43,z+.079),(.012,.012,.005),edge)
for kind in ['chip','star','jam','choco','sprinkle']:
    hide();cookie(kind);view((.5,-3,2.9),(0,0,.02),1.24,192,144);render('cookie-'+kind)
# Ten discs and a separately animated wrap, aligned in the same image space.
for kind in ['plain','choco']:
    hide()
    for i in range(10):disc('Ten stack '+str(i),(math.sin(i)*.008,0,.10+i*.155),.24,.145,chocolate if kind=='choco' else dough)
    view((.45,-6,2.8),(0,0,.82),2.0,96,320);render('stack-'+kind)
hide();band=disc('Blue paper sleeve',(0,0,.80),.255,.24,mat('Periwinkle paper',(.17,.40,.68),.7));view((.45,-6,2.8),(0,0,.82),2.0,96,320);render('stack-band')
# Lathed porcelain: a thick rounded rim, shallow well and soft undercut.
for kind,glaze in [('mint',mint),('lavender',lavender)]:
    hide();profile=[(.0,.02),(1.55,.02),(1.82,.06),(2.00,.17),(2.13,.26),(2.23,.25),(2.29,.16),(2.25,.06),(2.06,-.04),(.0,-.04)]
    verts=[(r*math.cos(i*math.tau/96),r*math.sin(i*math.tau/96),z) for r,z in profile for i in range(96)]
    faces=[(j*96+i,j*96+(i+1)%96,(j+1)*96+(i+1)%96,(j+1)*96+i) for j in range(len(profile)-1) for i in range(96)]
    m=bpy.data.meshes.new('Porcelain');m.from_pydata(verts,[],faces);o=bpy.data.objects.new('Ceramic serving plate',m);bpy.context.collection.objects.link(o);reg(o,o.name,ivory);o.data.materials.append(glaze)
    for poly in o.data.polygons:poly.material_index=1 if poly.index//96<3 else 0
    sub=o.modifiers.new('Polished ceramic curves','SUBSURF');sub.levels=2
    view((0,-10,5),(0,0,.05),5.0,640,320);render('plate-'+kind)
# A real miniature room replaces the flat striped wallpaper and checkerboard.
hide()
box('Maple table',(0,-2.0,.78),(19,13,.44),wood,.18)
box('Vanilla wall',(0,3.7,4.7),(19,.35,9),plaster,.18)
box('Pale green wainscot',(0,3.45,1.24),(19,.22,.7),mint,.08)
box('Chair rail',(0,3.2,1.62),(19,.28,.12),ivory,.055)
# Gentle wide wood seams, kept away from the learning objects' contrast.
for x in [-6,-3,0,3,6]:line('Maple seam',[(x,-8,1.004),(x+.015,-2,1.004),(x,3.1,1.004)],.008,mat('Wood seam '+str(x),(.60,.41,.27),.85))
box('Window rounded oak frame',(0,3.05,2.58),(3.15,.28,2.15),ivory,.24)
box('Window sky pane',(0,2.87,2.58),(2.85,.12,1.88),sky,.19)
for x in [-.7,.7]:
    ball('Cloud',(x,2.78,2.9),(.48,.045,.13),cream);ball('Cloud top',(x+.12,2.77,3.0),(.23,.045,.15),cream)
box('Window mullion',(0,2.69,2.58),(.075,.12,1.9),wood,.035)
box('Window crossbar',(0,2.67,2.50),(2.85,.13,.075),wood,.035)
box('Rounded window sill',(0,2.65,1.47),(3.55,.55,.14),ivory,.06)
# Tactile bunting in the pets' mint/lavender/cream palette.
line('Bunting string',[(-8,3.0,3.5),(-4,2.95,3.23),(0,2.9,3.45),(4,2.95,3.23),(8,3,3.5)],.016,ivory)
for j in range(19):
    x=-7.6+j*.84;z=3.34-.10*math.cos(x*.8);m=bpy.data.meshes.new('Felt pennant');m.from_pydata([(x-.23,2.93,z),(x+.23,2.93,z),(x,2.93,z-.44)],[],[(0,1,2)]);o=bpy.data.objects.new('Felt pennant',m);bpy.context.collection.objects.link(o);reg(o,o.name,[mint,lavender,cream,rose][j%4]);sol=o.modifiers.new('Felt thickness','SOLIDIFY');sol.thickness=.035;b=o.modifiers.new('Rounded corners','BEVEL');b.width=.035;b.segments=3
# Subdued bakery props at the far edges, outside the main equation.
for x,ma in [(-6.8,lavender),(6.6,mint)]:
    jar=disc('Ceramic cookie jar',(x,2.4,1.52),.43,1.0,ma);disc('Jar lid',(x,2.4,2.06),.47,.12,ivory);ball('Jar knob',(x,2.4,2.18),(.11,.11,.09),wood)
disc('Plant pot',(-4.9,2.7,1.25),.30,.48,ivory)
for j in range(5):
    a=j*math.tau/5;line('Stem',[(-4.9,2.7,1.4),(-4.9+.28*math.cos(a),2.7+.1*math.sin(a),1.9+.12*(j%2))],.018,leaf);o=ball('Soft sage leaf',(-4.9+.28*math.cos(a),2.7+.1*math.sin(a),1.9+.12*(j%2)),(.20,.065,.10),leaf);o.rotation_euler.y=a
for light,loc,energy,size in lights:light.location=loc*2.5;light.data.energy=energy*6.25;light.data.size=size*2.5
view((0,-15,7.45),(0,0,1.45),16,1280,500,False);render('room-play')
view((0,-15,8.3),(0,0,2.3),16,1280,720,False);render('room-wide')
bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'bakery-room.blend'))
record['finishedAt']=datetime.datetime.now(datetime.timezone.utc).isoformat();(OUT/'render-process.json').write_text(json.dumps(record,indent=2))
print('BAKERY_ASSETS_COMPLETE',flush=True)
