"""Level 02 — The Factory. Campaign escalation with conveyors, rush waves and Foreman MK-II."""
from copy import deepcopy
from .enemigos import ENEMIES


def factory():
    grid = [[1] * 56 for _ in range(34)]
    rooms = [
        ('FREIGHT ELEVATOR / RECEIVING', [1, 1, 8, 7]),
        ('PRODUCTION LINE A', [10, 1, 22, 10]),
        ('TOOLING BAY', [1, 10, 8, 16]),
        ('QUALITY CONTROL', [24, 1, 33, 10]),
        ('CONVEYOR NETWORK', [24, 12, 36, 19]),
        ('PRODUCTION LINE B', [38, 12, 53, 22]),
        ('MAINTENANCE CATWALKS', [38, 1, 53, 9]),
        ('CENTRAL MANUFACTURING FLOOR', [18, 22, 39, 32]),
        ('LAB TRANSIT', [41, 25, 53, 31]),
        ('SERVICE LINK', [10, 13, 18, 15]),
    ]
    for _, (x1, y1, x2, y2) in rooms:
        for y in range(y1, y2 + 1):
            for x in range(x1, x2 + 1):
                grid[y][x] = 0
    # Corridors between the major spaces.
    for x, y in [
        (9,4),(4,8),(4,9),(9,14),(23,5),(29,11),(29,20),(29,21),
        (37,16),(45,10),(45,11),(39,23),(40,27),(41,27),
    ]:
        grid[y][x] = 0
    # Cover / machinery.
    for x, y in [
        (14,4),(18,7),(20,3),(27,4),(31,7),(27,15),(33,16),(41,15),(46,18),
        (50,14),(43,5),(48,4),(52,7),(22,25),(26,28),(31,24),(35,29),
    ]:
        grid[y][x] = 2
    # Lab Transit is a true end-of-level gate, not a combat escape corridor.
    grid[27][40] = 3

    types = deepcopy(ENEMIES)
    types['sentinel'] = dict(
        name='SENTINEL', hp=90, speed=0.0, range=8.5, color='#8f78c9',
        radius=.24, vision=14, search_seconds=2.5, rear_multiplier=1.25,
        rear_angle=.95, projectile_speed=6.0, ranged=True,
    )
    types['gunner'] = dict(
        name='CORRUPTED GUNNER', hp=95, speed=.85, range=7.2, color='#d85d72',
        radius=.23, vision=15, search_seconds=8, rear_multiplier=1.2,
        rear_angle=.95, projectile_speed=5.5, ranged=True, strafe=.55,
    )
    types['foreman'] = dict(
        name='FOREMAN MK-II', hp=360, speed=.82, range=7.4, color='#e08f45',
        radius=.46, vision=18, search_seconds=12, rear_multiplier=1.15,
        rear_angle=.9, projectile_speed=6.2, ranged=True,
        ram_speed=5.5, ram_prepare=.7, ram_duration=.8,
        slam_prepare=.7, slam_radius=2.7, recovery=.75,
        node_hp=55, protected_multiplier=0.0,
    )

    def e(i, kind, x, y, group):
        base = dict(id=i, type=kind, x=x, y=y, group=group, active=False)
        if kind == 'foreman':
            base.update(boss_mode='offensive', shielded=False, shield_cycles=0,
                        node_a_hp=0, node_b_hp=0, phase_time=0, attack_index=0,
                        cooldown=0, support_deployed=False)
        return base

    classic = [
        e('recv_1','worker',6.5,2.5,'receiving'), e('recv_2','worker',7,6,'receiving'), e('recv_3','rivet',5.5,6.5,'receiving'),
        e('linea_1','worker',12,3,'line_a_first'), e('linea_2','crawler',17,9,'line_a_first'), e('linea_3','rivet',21,5,'line_a_first'),
        e('linea_4','worker',18,3,'line_a_second'), e('linea_5','crawler',21,9,'line_a_second'), e('linea_6','worker',12,9,'line_a_second'),
        e('conv_1','sentinel',34,14,'conveyor'), e('conv_2','crawler',26,18,'conveyor'), e('conv_3','worker',33,18,'conveyor'),
        e('lineb_1','gunner',49,15,'line_b'), e('lineb_2','worker',41,20,'line_b'), e('lineb_3','crawler',52,20,'line_b'), e('lineb_4','rivet',45,13,'line_b'),
        e('cat_1','sentinel',51,4,'catwalks'), e('cat_2','worker',40,7,'catwalks'),
        e('rush1_1','worker',22,25,'rush_1'), e('rush1_2','crawler',28,30,'rush_1'), e('rush1_3','worker',36,25,'rush_1'),
        e('rush2_1','rivet',20,29,'rush_2'), e('rush2_2','sentinel',36,29,'rush_2'), e('rush2_3','crawler',30,24,'rush_2'),
        e('rush3_1','gunner',23,24,'rush_3'), e('rush3_2','crawler',34,31,'rush_3'), e('rush3_3','worker',31,27,'rush_3'),
        e('foreman_mk2','foreman',29,27,'foreman'),
        e('foreman_support_1','crawler',20,31,'foreman_support'), e('foreman_support_2','rivet',38,24,'foreman_support'),
    ]
    doom = deepcopy(classic) + [
        e('doom_r1','crawler',3,6,'receiving'), e('doom_a1','worker',15,7,'line_a_first'), e('doom_a2','rivet',19,2,'line_a_second'),
        e('doom_c1','crawler',35,18,'conveyor'), e('doom_c2','sentinel',25,13,'conveyor'),
        e('doom_b1','gunner',52,16,'line_b'), e('doom_b2','crawler',39,14,'line_b'),
        e('doom_cat','rivet',46,8,'catwalks'),
        e('doom_w1','crawler',38,31,'rush_1'), e('doom_w2','worker',25,31,'rush_2'), e('doom_w3','gunner',35,24,'rush_3'),
        e('doom_fs','crawler',34,24,'foreman_support'),
    ]

    items = []
    def item(i, kind, x, y, n=1, **kw):
        items.append(dict(id=i, type=kind, x=x, y=y, amount=n, **kw))
    item('factory_pistol_ammo','ammo',4.5,6.5,18,weapon='pistol')
    item('assault_rifle','weapon',16.5,5.5,weapon='assault',reserve=54)
    item('assault_ammo_a','ammo',21.5,9.5,36,weapon='assault')
    item('tooling_armor','armor',6.5,14.5,20)
    item('quality_med','health',31.5,9.5,20)
    item('conveyor_assault','ammo',25.5,18.5,30,weapon='assault')
    item('sawed_off','weapon',45.5,17.5,weapon='sawed_off',reserve=14)
    item('sawed_shells','ammo',51.5,21.5,10,weapon='sawed_off')
    item('catwalk_armor','armor',41.5,3.5,25)
    item('rush_supply_assault','ammo',19.5,23.5,42,weapon='assault')
    item('rush_supply_shells','ammo',20.5,24.5,12,weapon='shotgun')
    item('rush_supply_sawed','ammo',21.5,23.5,10,weapon='sawed_off')
    item('foreman_med','health',38.5,31.5,30)
    item('doom_factory_ammo','ammo',48.5,8.5,24,weapon='assault',difficulties=['doom'])

    def question(prompt, answer, choices, category='to_decimal', manual=False, explanation=None):
        return dict(
            categories_allowed=[category], denominators_allowed=[2,4,8,16],
            multiple_choice_allowed=not manual, manual_allowed=manual,
            fixed_question=dict(
                prompt=prompt, answer=answer, choices=[] if manual else choices,
                category=category, mode='manual' if manual else 'choice',
                expected_format='fraction' if category=='to_fraction' else 'text' if category=='theory' else 'decimal',
                explanation=explanation or f'{prompt.replace(" = ?", "")} = {answer}'
            )
        )
    def st(i, kind, x, y, label, reward, q=None, **kw):
        return dict(id=i,kind=kind,x=x,y=y,label=label,
                    interaction_point=dict(x=x,y=y),interaction_distance=1.75,
                    question=q or {},reward=reward,**kw)

    stations = [
        st('tooling_terminal','terminal',3.5,13.5,'TOOL OFFSET / 5/16',
           [dict(type='ammo',weapon='assault',amount=30)],
           question('5/16" = ?', '.3125', ['.1875','.3125','.625']), prerequisites={'collected':'assault_rifle'}, reward_label='+30 municiones de rifle'),
        st('factory_armory','armory',7.0,11.5,'DDI EMERGENCY ARMORY / PREVIOUS-SECTOR EQUIPMENT',
           [dict(type='recover_weapon',weapon='shotgun',reserve=10),dict(type='ensure_ammo',minimum={'shotgun':10})]),
        st('quality_tolerance','terminal',25.5,3.5,'CONTROL DE CALIDAD / RANGO PERMITIDO',
           [dict(type='armor',amount=20)],
           question(
               'CONTROL DE CALIDAD: El rango permitido es de 0.4375″ a 0.5625″. La pieza inspeccionada mide 0.500″. ¿La pieza está dentro del rango permitido?',
               'DENTRO DEL RANGO', ['DENTRO DEL RANGO','FUERA DEL RANGO'], 'theory',
               explanation='Correcto: 0.500″ está entre 0.4375″ y 0.5625″. En industria, este mismo rango puede escribirse como 0.500″ ± 0.0625″. Primero aprende a identificar el rango; la notación compacta se introducirá poco a poco.'
           ), reward_label='+20 armadura'),
        st('mad_factory_01','mad',31.5,5.5,'M.A.D. #1 / QUALITY',
           [dict(type='upgrade',mod=1)], question('7/16" = ?', '.4375', ['.3125','.4375','.5625'])),
        st('mad_factory_02','mad',48.5,7.5,'M.A.D. #2 / CATWALK SERVICE',
           [dict(type='upgrade',mod=1)], question('11/16" = ?', '.6875', ['.5625','.6875','.8125']), hidden_on_minimap=True),
        st('mad_factory_03','mad',52.5,20.5,'M.A.D. #3 / LINE B SERVICE',
           [dict(type='upgrade',mod=1)], question('15/16" = ?', '.9375', ['.8125','.875','.9375'])),
        st('production_control_a','terminal',21.5,27.5,'PRODUCTION CONTROL A',
           [dict(type='objective',id='production_control_a')],
           question('.6875" = ?', '11/16', ['9/16','11/16','13/16'],'to_fraction'), prerequisites={'objective':'rush_complete'}),
        st('production_control_b','terminal',36.5,27.5,'PRODUCTION CONTROL B',
           [dict(type='objective',id='production_control_b')],
           question('13/16" = ?', '.8125', ['.6875','.8125','.9375']), prerequisites={'objective':'rush_complete'}),
        st('lab_transit','exit',49.5,28.5,'LAB TRANSIT',[]),
    ]

    def obj(i, rule=None): return dict(id=i, condition=rule or {})
    objectives = [
        obj('factory_started',{'trigger':'receiving'}),
        obj('assault_collected',{'collected':'assault_rifle'}),
        obj('quality_reached',{'trigger':'quality'}),
        obj('sawed_off_collected',{'collected':'sawed_off'}),
        obj('rush_wave_1_cleared',{'group_defeated':'rush_1'}),
        obj('rush_wave_2_cleared',{'group_defeated':'rush_2'}),
        obj('rush_complete',{'group_defeated':'rush_3'}),
        obj('production_control_a'), obj('production_control_b'),
        obj('production_controls_disabled',{'all':[{'objective':'production_control_a'},{'objective':'production_control_b'}]}),
        obj('foreman_spawned',{'wave':'foreman'}),
        obj('foreman_defeated',{'group_defeated':'foreman'}),
        obj('utcj_2_found',{'secret':'utcj_factory'}),
        obj('lab_transit_unlocked',{'all':[{'objective':'production_controls_disabled'},{'objective':'foreman_defeated'}]}),
        obj('factory_complete',{'complete':True}),
    ]

    wave_ids=['receiving','line_a_first','line_a_second','conveyor','line_b','catwalks','rush_1','rush_2','rush_3','foreman','foreman_support']
    waves=[dict(id=g,groups=[g]) for g in wave_ids]
    def tr(i, rule, actions, **kw): return dict(id=i,condition=rule,actions=actions,**kw)
    def wave(g): return [dict(type='activate_wave',id=g)]
    triggers = [
        tr('receiving',{'zone':[4,1,9,8]},wave('receiving'),message='PRODUCTION FLOOR // OUTPUT 212%'),
        tr('line_a_first',{'zone':[10,1,23,11]},wave('line_a_first'),message='PRODUCTION LINE A // ASSAULT RIFLE AHEAD'),
        tr('line_a_second',{'collected':'assault_rifle'},wave('line_a_second'),message='LINE A // HOSTILE RESPONSE ESCALATING'),
        tr('quality',{'zone':[24,1,34,11]},[],message='QUALITY CONTROL // DIMENSIONAL INSPECTION ONLINE'),
        tr('conveyor',{'zone':[24,12,37,20]},wave('conveyor'),message='CONVEYOR NETWORK // SENTINEL CONTACT'),
        tr('line_b',{'zone':[38,12,54,23]},wave('line_b'),message='PRODUCTION LINE B // CLOSE-RANGE EQUIPMENT'),
        tr('catwalks',{'zone':[38,1,54,10]},wave('catwalks')),
        tr('rush_1',{'all':[{'zone':[18,22,40,33]},{'objective':'assault_collected'},{'objective':'sawed_off_collected'}]},wave('rush_1'),message='PRODUCTION OVERRIDE // WAVE 1'),
        tr('rush_2',{'all':[{'wave':'rush_1'},{'group_defeated':'rush_1'}]},wave('rush_2'),message='PRODUCTION OVERRIDE // WAVE 2'),
        tr('rush_3',{'all':[{'wave':'rush_2'},{'group_defeated':'rush_2'}]},wave('rush_3'),message='PRODUCTION OVERRIDE // FINAL WAVE'),
        tr('rush_supply',{'objective':'rush_complete'},[dict(type='ensure_ammo',minimum={'pistol':24,'shotgun':10,'assault':54,'sawed_off':10})],message='EMERGENCY SUPPLY // FOREMAN PROTOCOL'),
        tr('foreman',{'all':[{'objective':'production_controls_disabled'},{'zone':[26,24,32,30]}]},wave('foreman'),message='FOREMAN MK-II // SUPERVISOR OVERRIDE'),
        tr('foreman_support',{'all':[{'enemy_alive':'foreman_mk2'},{'enemy_hp_below':{'id':'foreman_mk2','ratio':.5}}]},wave('foreman_support'),message='FOREMAN // SUPPORT DEPLOYMENT'),
        tr('lab_transit_unlock',{'objective':'lab_transit_unlocked'},[dict(type='door',id='lab_transit_gate')],message='PRODUCTION CONTROL RESTORED // LAB TRANSIT ACCESS GRANTED'),
    ]

    def cp(i,order,zone,x,y,pre):
        return dict(id=i,order=order,zone=zone,prerequisites=pre,
                    respawn_position=dict(x=x,y=y),respawn_angle=0)
    checkpoints=[
        cp('factory_receiving',0,[1,1,5,7],3.5,4.5,{}),
        cp('factory_quality',1,[24,1,34,11],25.5,8.5,{'objective':'assault_collected'}),
        cp('factory_line_b',2,[38,12,54,23],39.5,20.5,{'objective':'sawed_off_collected'}),
        cp('factory_central',3,[18,22,24,32],19.5,27.5,{'objective':'rush_complete'}),
        cp('factory_foreman',4,[18,24,39,32],35.5,30.5,{'objective':'production_controls_disabled'}),
    ]

    conveyors=[
        dict(id='line_a_belt',zone=[11,7,21.5,9.5],dx=1,dy=0,speed=.75,kind='normal'),
        dict(id='network_fast',zone=[26,13,35,15.5],dx=0,dy=1,speed=1.35,kind='fast'),
        dict(id='line_b_belt',zone=[40,18,52,20.5],dx=-1,dy=0,speed=.8,kind='normal'),
    ]
    boss_nodes=[
        dict(id='foreman_node_a',x=22.5,y=24.5),
        dict(id='foreman_node_b',x=36.5,y=30.5),
    ]

    return dict(
        id='factory',revision=2,name='LEVEL 02 / THE FACTORY',grid=grid,
        enemy_types=types,encounters={'clasico':classic,'doom':doom},items=items,stations=stations,
        doors=[dict(id='lab_transit_gate',cell=[40,27])],checkpoints=checkpoints,triggers=triggers,waves=waves,objectives=objectives,
        secrets=[dict(id='utcj_factory',kind='utcj',on_shot=True,x=50.5,y=2.5)],
        exit=dict(station='lab_transit',condition={'objective':'lab_transit_unlocked'},auto_zone=[47,26,53,31]),
        initial_loadout={'pistol':dict(loaded=12,reserve=24,mods=0)},scale_resources=False,
        player_config=dict(max_hp=100,max_armor=100),
        respawn_rules=dict(min_hp=55,grace=2.5,ammo={'pistol':16,'shotgun':8,'assault':30,'sawed_off':6}),
        transition_resupply=dict(min_hp=60,ammo={'pistol':24,'shotgun':10,'assault':36,'sawed_off':8}),
        conveyors=conveyors,boss_nodes=boss_nodes,
        zones=[dict(label=n,zone=[x1,y1,x2+1,y2+1]) for n,(x1,y1,x2,y2) in rooms],
        objective_hints=[
            dict(until='factory_started',text='FREIGHT ELEVATOR → ENTER PRODUCTION FLOOR'),
            dict(until='assault_collected',text='PRODUCTION LINE A → RECOVER ASSAULT RIFLE'),
            dict(until='quality_reached',text='QUALITY CONTROL → INSPECT PRODUCTION'),
            dict(until='sawed_off_collected',text='CONVEYOR NETWORK → PRODUCTION LINE B'),
            dict(until='rush_complete',text='CENTRAL FLOOR → SURVIVE PRODUCTION OVERRIDE'),
            dict(until='production_controls_disabled',text='CALIBRATE BOTH PRODUCTION CONTROLS'),
            dict(until='foreman_defeated',text='DEFEAT FOREMAN MK-II / BREAK INDUSTRIAL NODES'),
            dict(until='factory_complete',text='PRODUCTION CONTROL RESTORED → REACH LAB TRANSIT'),
        ],
        intro='LEVEL 02 — THE FACTORY. Production output is locked at 212%. Follow the line through Quality Control, survive the central override, disable both production controls and stop Foreman MK-II. Conveyors affect movement but never remove control.',
        navigation=[
            dict(until='assault_collected',x=16.5,y=5.5),dict(until='quality_reached',x=28,y=5),
            dict(until='sawed_off_collected',x=45.5,y=17.5),dict(until='rush_complete',x=29,y=27),
            dict(until='production_control_a',x=21.5,y=27.5),dict(until='production_controls_disabled',x=36.5,y=27.5),
            dict(until='foreman_defeated',x=29,y=27),
            dict(until='factory_complete',x=49.5,y=28.5),
        ],
        campaign_secrets=4,
        teaser='PRODUCTION OUTPUT: 0%\nEXTERNAL OVERRIDE TERMINATED\nSIGNAL SOURCE: RESEARCH LABORATORY\nLEVEL 03 — THE LABORATORY',
    )
