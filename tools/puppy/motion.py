"""Character-specific acting. Angles are radians; every action settles to rest."""
import math

FPS = 24

def clips(cat):
    return [('normal',96 if cat else 72), ('curious',54 if cat else 48),
            ('happy',48 if cat else 42), ('sad',36), ('wow',30),
            ('lookLeft',24), ('lookRight',24), ('eat',42 if cat else 36)]

def ease(x):
    x=max(0,min(1,x));return x*x*(3-2*x)

def keys(u,points):
    for (a,x),(b,y) in zip(points,points[1:]):
        if u<=b:return x+(y-x)*ease((u-a)/(b-a))
    return points[-1][1]

def pulse(u,a,b,c,d):
    return ease((u-a)/(b-a))*(1-ease((u-c)/(d-c)))

def pose(cat,mood,u,c):
    root,head,tail=c['root'],c['head'],c['tail']
    eyes,ears,arms=c['eyes'],c['ears'],c['arms']
    tau=math.tau
    # Breathing is small and never lifts the feet. Ear and tail follow-through
    # are separate from body movement, rather than scaling the whole drawing.
    breath=math.sin(tau*u)
    root.scale.z*=1+.009*breath
    root.scale.x*=1-.003*breath
    head.rotation_euler.y=.018*math.sin(tau*u)
    tail.rotation_euler.z=(.12 if cat else .35)*math.sin(tau*u*(1 if cat else 3))
    tail.rotation_euler.y=(.07 if cat else .15)*math.sin(tau*u*(1 if cat else 3))
    # Sculpted cat tail bends from the base to the tip with a delayed wave.
    for spline,base in c.get('tail_splines',[]):
        for j,(p,co) in enumerate(zip(spline.bezier_points,base)):
            w=j/max(1,len(base)-1)
            p.co=co
            p.co.x+=w*w*.09*math.sin(tau*u-w*.9)
    if c.get('tail_tip'):
        c['tail_tip'].location.x+=.09*math.sin(tau*u-.9)

    def blink(center,width=.035,amount=.96):
        v=max(0,1-abs(u-center)/width)
        for e in eyes:e.scale.z*=1-amount*ease(v)

    def expression(kind,amount):
        if amount<.06:return
        for o in c['normal_mouth']:o.hide_render=True
        if kind=='smile':
            for e in eyes:
                for child in e.children:child.hide_render=amount>.5
                e.scale.z*=max(.08,1-amount)
            for o in c['closed']:o.hide_render=amount<=.5
            c['mouth'].hide_render=False;c['tongue'].hide_render=False
            c['mouth'].scale=(.11,.035,.025+.07*amount)
        elif kind=='wow':
            c['mouth'].hide_render=False;c['mouth'].scale=(.06,.035,.025+.07*amount)
            for e in eyes:e.scale*=1+.13*amount
        else:
            c['frown'].hide_render=False
            for e in eyes:e.scale.z*=1-.22*amount

    if mood=='normal':
        if cat:
            blink(.56,.085,.90)
            ears[1].rotation_euler.y=.16*pulse(u,.73,.78,.81,.88)
            head.rotation_euler.z=.028*math.sin(tau*u)
        else:
            blink(.31);blink(.82,.025,.90)
            ears[0].rotation_euler.y=.035*math.sin(tau*u*3-.4)
            ears[1].rotation_euler.y=-.045*math.sin(tau*u*3-.8)
            head.rotation_euler.x=.025*math.sin(tau*u)

    elif mood=='curious':
        if cat:
            # One paw rises towards the cheek; a slow blink, then a quiet settle.
            lift=pulse(u,.08,.35,.64,.94)
            arms[0].rotation_euler.x=-2.1*lift
            arms[0].rotation_euler.y=.25*lift
            arms[0].location.z+=.12*lift
            head.rotation_euler.y=-.16*lift
            head.rotation_euler.z=.10*lift
            blink(.48,.13)
            ears[0].rotation_euler.y=-.18*pulse(u,.28,.36,.43,.58)
        else:
            tilt=keys(u,[(0,0),(.24,-.20),(.47,-.20),(.72,.11),(1,0)])
            head.rotation_euler.y=tilt
            head.rotation_euler.x=.08*pulse(u,.12,.28,.53,.85)
            head.location.y-=.065*pulse(u,.16,.30,.52,.85)
            ears[0].rotation_euler.y=-tilt*.65
            ears[1].rotation_euler.y=-tilt*.30
            blink(.58)

    elif mood=='happy':
        active=pulse(u,.02,.17,.72,.99)
        expression('smile',active)
        if cat:
            # Proud little lean and one-paw wave: deliberately no puppy jump.
            lift=pulse(u,.07,.33,.67,.96)
            root.rotation_euler.y=-.065*lift
            head.rotation_euler.y=.13*lift
            head.rotation_euler.z=-.075*lift
            arms[1].rotation_euler.y=-1.65*lift
            arms[1].rotation_euler.x=-.55*lift
            arms[1].location.z+=.12*lift
            arms[1].rotation_euler.z=.24*math.sin(tau*u*3)*lift
            arms[0].rotation_euler.x=-.35*lift
            tail.rotation_euler.z=.30*math.sin(tau*u)*active
        else:
            # Anticipation, asymmetric leap, soft contact, smaller after-bounce.
            jump=keys(u,[(0,0),(.12,-.06),(.34,.31),(.55,0),(.61,-.035),(.75,.12),(.89,0),(1,0)])
            root.location.z+=jump
            stretch=keys(u,[(0,0),(.12,-.09),(.26,.07),(.46,.015),(.57,-.065),(.72,.035),(.90,-.025),(1,0)])
            root.scale.z*=1+stretch;root.scale.x*=1-stretch*.5
            root.rotation_euler.y=.04*math.sin(tau*u)*active
            head.rotation_euler.x=-.06*active
            head.rotation_euler.y=-.08*math.sin(tau*u)*active
            for j,a in enumerate(arms):a.rotation_euler.y=(1 if j==0 else -1)*(.65 if j==0 else .48)*active
            for j,e in enumerate(ears):e.rotation_euler.y=(1 if j==0 else -1)*.20*math.sin(tau*(u-.12)*2)*active
            tail.rotation_euler.z=.60*math.sin(tau*u*5)*active

    elif mood=='sad':
        active=pulse(u,0,.17,.65,1)
        expression('sad',active)
        if cat:
            head.rotation_euler.z=-.13*active
            head.rotation_euler.y=.10*active
            for j,e in enumerate(ears):e.rotation_euler.y=(1 if j else -1)*.22*active
            blink(.61,.09,.65)
        else:
            head.rotation_euler.x=.11*active
            head.rotation_euler.z=.08*math.sin(tau*u*1.5)*active
            for j,e in enumerate(ears):e.rotation_euler.y=(1 if j else -1)*.12*active
        for j,b in enumerate(c['brows']):b.rotation_euler.y=(1 if j else -1)*.16*active

    elif mood=='wow':
        active=pulse(u,0,.16,.50,1)
        expression('wow',active)
        if cat:
            head.location.z+=.07*active
            head.rotation_euler.z=-.10*active
            ears[0].rotation_euler.y=-.18*active
            ears[1].rotation_euler.y=.12*active
            arms[0].rotation_euler.x=-.55*active
        else:
            head.location.y+=.045*active
            head.rotation_euler.x=-.085*active
            root.scale.z*=1+.035*active
            for j,e in enumerate(ears):e.rotation_euler.y=(1 if j==0 else -1)*.20*active
        for b in c['brows']:b.location.z+=.04*active

    elif mood=='eat':
        active=pulse(u,0,.15,.76,1)
        chew=.5+.5*math.sin(tau*u*(3 if cat else 4))
        expression('smile',active)
        c['mouth'].scale.z=(.024+.035*chew)*max(.1,active)
        c['tongue'].hide_render=cat or active<.2
        head.rotation_euler.x=(.025 if cat else .055)*math.sin(tau*u*3)*active
        head.rotation_euler.y=(.055 if cat else -.025)*active
        for name in ('Cheek volume L','Cheek volume R'):
            c['objects'][name].scale.x*=1+.08*chew*active
        if cat:
            arms[0].rotation_euler.x=-1.65*active
            arms[0].rotation_euler.y=.25*active
            head.rotation_euler.z=.045*active
        else:tail.rotation_euler.z=.48*math.sin(tau*u*5)*active

    else:
        direction=-1 if mood=='lookLeft' else 1
        active=pulse(u,0,.25,.65,1)
        # Eyes lead; the head follows with a softer, smaller turn.
        for e in eyes:e.location.x+=direction*.025*pulse(u,0,.13,.72,1)
        head.rotation_euler.z=direction*(.095 if cat else .15)*active
        head.rotation_euler.y=direction*(.09 if cat else .045)*active
        head.rotation_euler.x=.04*active
        if cat:ears[0 if direction<0 else 1].rotation_euler.z=direction*.13*active
