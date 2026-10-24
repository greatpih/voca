"""Build Bora's matching 2.5D cat from Tori's editable toy proportions.
Run from Blender: -b --python tools/cat/build_model.py -- --preview /path/cat.png
"""
import bpy, math, argparse, sys, os, json, datetime
from pathlib import Path
HERE=Path(__file__).resolve().parent
p=argparse.ArgumentParser();p.add_argument('--preview',required=True)
opt=p.parse_args(sys.argv[sys.argv.index('--')+1:]);preview=Path(opt.preview).resolve();preview.parent.mkdir(parents=True,exist_ok=True)
(preview.parent/'model-process.json').write_text(json.dumps(dict(pid=os.getpid(),started=datetime.datetime.now(datetime.timezone.utc).isoformat(),executable=bpy.app.binary_path,workingDirectory=str(Path.cwd()),purpose='Build and preview Bora cat model',keepRunning=False),indent=2))
bpy.ops.wm.open_mainfile(filepath=str(HERE.parent/'puppy'/'source.blend'))
bpy.context.scene.frame_set(1)
for o in bpy.data.objects:o.animation_data_clear()
root=bpy.data.objects['PUPPY / squash and jump'];root.name='CAT / squash and jump'
head=bpy.data.objects['Head / curious tilt']
def recolor(name,color):
    m=bpy.data.materials[name];m.diffuse_color=(*color,1);m.node_tree.nodes['Principled BSDF'].inputs['Base Color'].default_value=(*color,1);return m
fur=recolor('Vanilla / warm ivory',(.71,.65,.86))
white=recolor('Face / butter cream',(.95,.92,.90))
milk=recolor('Muzzle / milk',(.99,.97,.94))
purple=recolor('Ears / caramel',(.43,.22,.69))
pink=recolor('Inner ears / warm peach',(.95,.48,.65))
recolor('Bandana / mint',(.45,.25,.75))
recolor('Bandana stitch',(.80,.65,.97))
recolor('Nose / chocolate satin',(.74,.25,.40))
blush=recolor('Cheeks / apricot',(.97,.48,.60))
whisker=bpy.data.materials['Eyes and smile / chocolate'].copy();whisker.name='Cat / whisker lavender'
whisker.node_tree.nodes['Principled BSDF'].inputs['Base Color'].default_value=(.29,.19,.36,1)
stripe=purple.copy();stripe.name='Cat / forehead markings';stripe.node_tree.nodes['Principled BSDF'].inputs['Base Color'].default_value=(.60,.46,.73,1)

def curve(name,pts,r,mat,parent):
    c=bpy.data.curves.new(name,'CURVE');c.dimensions='3D';c.resolution_u=20;c.bevel_depth=r;c.bevel_resolution=4
    s=c.splines.new('BEZIER');s.bezier_points.add(len(pts)-1)
    for v,co in zip(s.bezier_points,pts):v.co=co;v.handle_left_type='AUTO';v.handle_right_type='AUTO'
    o=bpy.data.objects.new(name,c);bpy.context.collection.objects.link(o);o.parent=parent;o.data.materials.append(mat);return o
def prism(name,coords,depth,mat,parent,bevel):
    verts=[(x,y,z) for y in (-depth,depth) for x,z in coords];n=len(coords)
    faces=[tuple(reversed(range(n))),tuple(range(n,2*n))]+[(i,(i+1)%n,(i+1)%n+n,i+n) for i in range(n)]
    m=bpy.data.meshes.new(name);m.from_pydata(verts,[],faces);m.update()
    o=bpy.data.objects.new(name,m);bpy.context.collection.objects.link(o);o.parent=parent;o.data.materials.append(mat)
    b=o.modifiers.new('Soft rounded ear edges','BEVEL');b.width=bevel;b.segments=5
    for f in m.polygons:f.use_smooth=True
    o.modifiers.new('Weighted surface normals','WEIGHTED_NORMAL')
    return o

# New upright, rounded triangular ears replace the floppy puppy ears.
for sign in (-1,1):
    pivot=bpy.data.objects['Ear pivot '+str(sign)]
    for child in list(pivot.children):bpy.data.objects.remove(child,do_unlink=True)
    pivot.location=(sign*.63,0,.82);pivot.rotation_euler=(0,0,0)
    outer=prism('Cat triangular ear '+str(sign),[(-.29,-.13),(.29,-.13),(sign*.11,.65)],.145,purple,pivot,.09)
    inner=prism('Cat pink inner ear '+str(sign),[(-.155,-.015),(.155,-.015),(sign*.08,.47)],.024,pink,pivot,.04);inner.location.y=-.15
for o in list(bpy.data.objects):
    if o.name.startswith('Forehead tuft'):bpy.data.objects.remove(o,do_unlink=True)
# Short, delicate whiskers and soft tabby marks distinguish the face.
for sign in (-1,1):
    for dz,spread in [(.07,.09),(0,0),(-.07,-.07)]:
        curve('Cat whisker',[(sign*.48,-.636,.20+dz),(sign*.64,-.60,.20+dz+spread*.5),(sign*.81,-.50,.20+dz+spread)],.009,whisker,head)
    curve('Cat forehead stripe',[(sign*.12,-.48,.94),(sign*.10,-.55,.86),(sign*.085,-.594,.79)],.027,stripe,head)
for name,x in [('Muzzle left',-.13),('Muzzle right',.13)]:
    o=bpy.data.objects[name];o.location.x=x;o.scale=(.245,.16,.185)
bpy.data.objects['Heart nose'].scale=(.10,.074,.072)
bpy.data.objects['Nose sheen'].location=(-.025,-.830,.31)
bpy.data.objects['Nose sheen'].scale=(.026,.010,.012)
# Keep the face, limbs, eyes and warm lighting in the same family as Tori.
bpy.data.objects['Body / pear silhouette'].data.materials[0]=fur
for o in bpy.data.objects:
    if o.name.startswith('Hind haunch'):o.data.materials[0]=fur
tail=bpy.data.objects['Tail / wag']
for o in list(tail.children):bpy.data.objects.remove(o,do_unlink=True)
curve('Cat long curled tail',[(0,0,0),(.30,.15,.10),(.48,.22,.38),(.50,.22,.72),(.36,.19,.91),(.20,.16,.87)],.115,fur,tail)
bpy.ops.mesh.primitive_uv_sphere_add(segments=40,ring_count=24)
tip=bpy.context.object;tip.name='Cat tail tip';tip.parent=tail;tip.location=(.20,.16,.87);tip.scale=(.115,.115,.115);tip.data.materials.append(purple)
for f in tip.data.polygons:f.use_smooth=True

s=bpy.context.scene;s.frame_set(1);s.cycles.samples=32;s.render.resolution_x=900;s.render.resolution_y=900
try:
    prefs=bpy.context.preferences.addons['cycles'].preferences;prefs.compute_device_type='OPTIX';prefs.get_devices()
    if any(d.type=='OPTIX' for d in prefs.devices):
        for d in prefs.devices:d.use=d.type=='OPTIX'
        s.cycles.device='GPU'
except Exception:pass
bpy.context.preferences.filepaths.save_version=0
bpy.ops.wm.save_as_mainfile(filepath=str(HERE/'source.blend'))
s.render.filepath=str(preview);bpy.ops.render.render(write_still=True)
print('BORA_MODEL_READY',flush=True)
