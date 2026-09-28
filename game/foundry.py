"""Level 04 — The Foundry.

High-precision 1/64 work, manual-entry practice, thermal hazards, heavy weapons,
Project U.T.C.J. signal four and The Crucible.  The level intentionally keeps
math out of the final boss: calibration changes the world, combat proves the
player can survive it.
"""
from copy import deepcopy
from .enemigos import ENEMIES


def foundry():
    grid = [[1] * 78 for _ in range(44)]
    rooms = [
        ('FOUNDRY DESCENT', [1, 16, 9, 25]),
        ('THERMAL PROCESSING', [11, 14, 23, 27]),
        ('HEAVY FABRICATION', [25, 14, 39, 27]),
        ('SLAG PROCESSING', [41, 14, 54, 27]),
        ('PRESSURE REGULATION', [56, 15, 76, 27]),
        ('FORGE ASSEMBLY', [56, 29, 76, 41]),
        ('FORGE PITS', [41, 29, 54, 41]),
        ('PROJECT U.T.C.J. CHAMBER', [41, 2, 54, 12]),
        ('THE FORGE RUN', [25, 29, 39, 41]),
        ('THE CRUCIBLE', [1, 29, 23, 41]),
    ]
    for _, (x1, y1, x2, y2) in rooms:
        for y in range(y1, y2 + 1):
            for x in range(x1, x2 + 1):
                grid[y][x] = 0

    # Main route: Descent -> Thermal -> Fabrication -> Slag -> Pressure ->
    # Assembly -> Pits -> Forge Run -> Crucible.  A vertical branch from Slag
    # hides the final UTCJ signal.
    for x, y in [
        (10, 20), (24, 20), (40, 20), (55, 20),
        (66, 28), (55, 35), (40, 35), (24, 35),
        (48, 13),
    ]:
        grid[y][x] = 0
    # Data-driven gates keep the educational sequence intact without killing FPS freedom inside each zone.
    grid[20][24] = 3  # 1/64 manual calibration -> Heavy Fabrication
    grid[28][66] = 3  # Pressure QC -> Forge Assembly
    grid[35][24] = 3  # Forge Run -> Crucible

    # Industrial cover: heavy machines, slag bins and furnace braces.
    for x, y in [
        (14,17),(18,24),(22,16),(28,17),(34,24),(38,16),
        (43,17),(50,24),(53,16),(59,18),(64,24),(72,17),
        (59,32),(68,38),(74,33),(43,32),(51,38),(46,7),(52,10),
        (28,32),(35,38),(38,31),(5,32),(11,38),(18,32),(21,39),
    ]:
        grid[y][x] = 2

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
    types['furnace_hound'] = dict(
        name='FURNACE HOUND', hp=78, speed=1.42, range=.8, color='#e57945',
        radius=.22, vision=15, search_seconds=9, rear_multiplier=1.3,
        rear_angle=.95, heat_time=.72, leap_time=.50, recovery=1.05,
        leap_speed=5.3, track_delay=1.15,
    )
    types['forge_brute'] = dict(
        name='FORGE BRUTE', hp=185, speed=.62, range=6.2, color='#b86a3c',
        radius=.42, vision=15, search_seconds=10, rear_multiplier=1.35,
        rear_angle=1.0, projectile_speed=4.0, ranged=True,
        frontal_multiplier=.42, weak_multiplier=1.45, shock_radius=2.15,
    )
    types['crucible'] = dict(
        name='THE CRUCIBLE', hp=680, speed=0.0, range=13, color='#e05f32',
        radius=.72, vision=22, search_seconds=30, rear_multiplier=1.0,
        rear_angle=1.0, projectile_speed=4.4, ranged=True,
        protected_multiplier=0.0, lock_hp=90, emergency_lock_hp=120,
        exposure_seconds=8.0,
    )

    def e(i, kind, x, y, group):
        base = dict(id=i, type=kind, x=x, y=y, group=group, active=False)
        if kind == 'furnace_hound':
            base.update(hound_mode='track', phase_time=0, cooldown=0, attack_index=0)
        if kind == 'crucible':
            base.update(
                boss_mode='pressure', phase_time=0, cooldown=0, attack_index=0,
                exposure_cycles=0,
                lock_a_hp=types['crucible']['lock_hp'],
                lock_b_hp=types['crucible']['lock_hp'],
                lock_c_hp=types['crucible']['lock_hp'],
                emergency_a_hp=0, emergency_b_hp=0,
            )
        return base

    classic = [
        e('des_1','worker',5.5,18.5,'descent'), e('des_2','gunner',7.5,23.5,'descent'), e('des_3','crawler',3.5,24,'descent'),
        e('therm_1','worker',14,16,'thermal'), e('therm_2','crawler',20,25,'thermal'), e('therm_3','rivet',22,17,'thermal'), e('therm_4','gunner',13,25,'thermal'),
        e('heavy_1','rivet',28,16,'heavy_first'), e('heavy_2','worker',35,24,'heavy_first'), e('heavy_3','gunner',38,18,'heavy_first'),
        e('heavy_4','crawler',29,25,'heavy_second'), e('heavy_5','rivet',36,16,'heavy_second'), e('heavy_6','worker',38,25,'heavy_second'),
        e('slag_1','furnace_hound',50,18,'slag'), e('slag_2','worker',43,25,'slag'), e('slag_3','gunner',52,24,'slag'), e('slag_4','crawler',44,17,'slag'),
        e('press_1','sentinel',74,18,'pressure'), e('press_2','rivet',61,25,'pressure'), e('press_3','worker',70,25,'pressure'),
        e('assy_1','gunner',60,31,'assembly_first'), e('assy_2','crawler',71,39,'assembly_first'), e('assy_3','worker',74,32,'assembly_first'),
        e('assy_4','furnace_hound',63,39,'assembly_second'), e('assy_5','rivet',72,35,'assembly_second'), e('assy_6','gunner',58,38,'assembly_second'),
        e('pits_1','forge_brute',49,35,'pits'), e('pits_2','furnace_hound',43,39,'pits'), e('pits_3','crawler',53,31,'pits'), e('pits_4','rivet',51,40,'pits'),
        e('run_a1','furnace_hound',36,32,'forge_run_a'), e('run_a2','gunner',31,39,'forge_run_a'), e('run_a3','worker',38,39,'forge_run_a'), e('run_a4','crawler',27,34,'forge_run_a'),
        e('run_b1','forge_brute',29,36,'forge_run_b'), e('run_b2','rivet',37,32,'forge_run_b'), e('run_b3','furnace_hound',35,40,'forge_run_b'), e('run_b4','gunner',26,40,'forge_run_b'),
        e('crucible_support_1','forge_brute',19,39,'crucible_support'), e('crucible_support_2','furnace_hound',7,39,'crucible_support'),
        e('the_crucible','crucible',12,35,'crucible'),
    ]
    doom = deepcopy(classic) + [
        e('doom_des','crawler',8,18,'descent'), e('doom_thermal','gunner',18,16,'thermal'),
        e('doom_heavy1','rivet',32,25,'heavy_first'), e('doom_heavy2','crawler',26,18,'heavy_second'),
        e('doom_slag','furnace_hound',47,25,'slag'), e('doom_press','gunner',66,18,'pressure'),
        e('doom_assy1','furnace_hound',75,39,'assembly_first'), e('doom_assy2','gunner',67,32,'assembly_second'),
        e('doom_pits1','forge_brute',44,35,'pits'), e('doom_pits2','furnace_hound',53,39,'pits'),
        e('doom_run1','gunner',34,31,'forge_run_a'), e('doom_run2','furnace_hound',28,39,'forge_run_b'),
        e('doom_crucible','furnace_hound',20,31,'crucible_support'),
    ]

    items = []
    def item(i, kind, x, y, n=1, **kw):
        items.append(dict(id=i, type=kind, x=x, y=y, amount=n, **kw))

    item('foundry_pistol','ammo',5.5,24.5,24,weapon='pistol')
    item('foundry_armor_a','armor',8.5,17.5,25)
    item('thermal_assault','ammo',21.5,26.5,36,weapon='assault')
    item('lmg_weapon','weapon',32.5,20.5,weapon='lmg',reserve=120)
    item('lmg_ammo_a','ammo',38.5,26.5,60,weapon='lmg')
    item('slag_health','health',53.5,26.5,30)
    item('pressure_sniper','ammo',75.5,26.5,8,weapon='sniper')
    item('pressure_armor','armor',57.5,16.5,30)
    item('rocket_launcher','weapon',67.5,35.5,weapon='rocket',reserve=5)
    item('rocket_ammo_a','ammo',75.5,40.5,2,weapon='rocket')
    item('assembly_lmg','ammo',57.5,40.5,70,weapon='lmg')
    item('pits_health','health',52.5,40.5,30)
    item('pits_assault','ammo',42.5,30.5,42,weapon='assault')
    item('run_lmg','ammo',39.5,40.5,80,weapon='lmg')
    item('run_rocket','ammo',26.5,40.5,2,weapon='rocket')
    item('crucible_med','health',22.5,40.5,35)
    item('crucible_armor','armor',2.5,40.5,35)
    item('crucible_lmg','ammo',21.5,30.5,90,weapon='lmg')
    item('doom_foundry_rocket','ammo',53.5,30.5,1,weapon='rocket',difficulties=['doom'])

    def fixed(prompt, answer, choices, category='to_decimal', explanation='', mode='choice'):
        formats = {
            'to_decimal':'decimal', 'to_fraction':'fraction', 'mixed_to_decimal':'decimal',
            'decimal_to_mixed':'mixed', 'equivalence':'decimal', 'theory':'text',
            'special':'integer', 'simplify':'fraction'
        }
        return dict(
            prompt=prompt, answer=answer, choices=choices if mode=='choice' else [],
            category=category, mode=mode, expected_format=formats.get(category,'text'),
            explanation=explanation or f'Respuesta: {answer}'
        )

    def qpool(*questions, categories=None):
        return dict(
            categories_allowed=categories or sorted({q['category'] for q in questions}),
            denominators_allowed=[2,4,8,16,32,64], multiple_choice_allowed=True,
            manual_allowed=True, fixed_questions=list(questions),
        )

    def st(i, kind, x, y, label, reward, q=None, **kw):
        return dict(
            id=i, kind=kind, x=x, y=y, label=label,
            interaction_point=dict(x=x,y=y), interaction_distance=1.8,
            question=q or {}, reward=reward, **kw
        )

    intro_64 = qpool(
        fixed(
            'MEDICIÓN DE ALTA PRECISIÓN: En Laboratory trabajaste con 1/32″. Si divides 1/32 nuevamente entre dos obtienes 1/64″. ¿Cuál es el equivalente decimal de 1/64″?',
            '.015625', ['.0078125','.015625','.03125'], 'to_decimal',
            '1/32 ÷ 2 = 1/64. En decimal, .03125 ÷ 2 = .015625. Primero entendemos la escala; después la usamos.'
        ),
        fixed(
            'PATRÓN DE PRECISIÓN: 1/64″ = .015625″. ¿Qué decimal corresponde a 3/64″?',
            '.046875', ['.03125','.046875','.09375'], 'to_decimal',
            'Tres veces .015625 = .046875.'
        ),
        fixed(
            'EQUIVALENCIAS: 32/64″ representa media pulgada. ¿Qué decimal equivale a 32/64″?',
            '.5', ['.25','.5','.75'], 'equivalence',
            '32/64 se simplifica a 1/2 y 1/2″ = .5″.'
        ),
    )
    precision_manual = qpool(
        fixed('CALIBRACIÓN FOUNDRY: Convierte 11/64″ a decimal.', '.171875', [], 'to_decimal', '11 × .015625 = .171875.', mode='manual'),
        fixed('CALIBRACIÓN FOUNDRY: Convierte 0.203125″ a fracción simplificada.', '13/64', [], 'to_fraction', '.203125″ = 13/64″.', mode='manual'),
        fixed('CALIBRACIÓN FOUNDRY: Simplifica 24/64.', '3/8', [], 'simplify', 'Divide numerador y denominador entre 8: 24/64 = 3/8.', mode='manual'),
    )
    pressure_questions = qpool(
        fixed(
            'CONTROL DE MECANIZADO: La pieza debe medir entre 0.484375″ y 0.515625″. La pieza inspeccionada mide 0.500″. ¿Está dentro del rango permitido?',
            'DENTRO DEL RANGO', ['DENTRO DEL RANGO','FUERA DEL RANGO','NO SE PUEDE SABER'], 'theory',
            'Sí. 0.500 está entre 0.484375 y 0.515625. Ese margen corresponde a 0.500″ ± 1/64″.'
        ),
        fixed(
            'CONTROL DE MECANIZADO: El rango permitido es 0.734375″ a 0.765625″. La pieza mide 0.78125″. ¿Qué debe hacer Control de Calidad?',
            'RECHAZAR LA PIEZA', ['APROBAR LA PIEZA','RECHAZAR LA PIEZA','CAMBIAR EL RANGO'], 'theory',
            '0.78125 es mayor que 0.765625, así que está fuera del rango permitido.'
        ),
    )
    mixed_questions = qpool(
        fixed('MEDIDA DE FUNDICIÓN: Convierte 1 13/32″ a decimal.', '1.40625', [], 'mixed_to_decimal', '13/32 = .40625; 1 + .40625 = 1.40625″.', mode='manual'),
        fixed('MEDIDA DE FUNDICIÓN: El escáner registra 2.625″. Escríbelo como número mixto simplificado.', '2 5/8', [], 'decimal_to_mixed', '.625 = 5/8; por tanto 2.625″ = 2 5/8″.', mode='manual'),
        fixed('MEDIDA DE FUNDICIÓN: Convierte 1 7/64″ a decimal.', '1.109375', [], 'mixed_to_decimal', '7/64 = .109375; entonces 1 7/64″ = 1.109375″.', mode='manual'),
    )
    mad_questions = qpool(
        fixed('M.A.D. FOUNDRY: Convierte 9/64″ a decimal.', '.140625', ['.109375','.140625','.28125'], 'to_decimal', '9 × .015625 = .140625.'),
        fixed('M.A.D. FOUNDRY: ¿Qué fracción simplificada equivale a .234375″?', '15/64', ['13/64','15/64','15/32'], 'to_fraction', '.234375″ = 15/64″.'),
        fixed('M.A.D. FOUNDRY: ¿Qué decimal equivale a 21/64″?', '.328125', ['.3125','.328125','.65625'], 'equivalence', '21 × .015625 = .328125.'),
    )

    stations = [
        st('foundry_precision_intro','terminal',12.5,15.5,'ALTA PRECISIÓN / 1/64',
           [dict(type='objective',id='precision_64_learned')], intro_64,
           reward_label='Escala 1/64 habilitada'),
        st('foundry_manual_calibration','terminal',22.5,26.5,'CALIBRACIÓN MANUAL / 1/64',
           [dict(type='objective',id='manual_precision_complete'), dict(type='door',id='fabrication_gate')], precision_manual,
           prerequisites={'objective':'precision_64_learned'}, reward_label='Calibración manual confirmada'),
        st('foundry_armory','armory',26.5,26.5,'DDI HEAVY ARMORY / EQUIPO PREVIO',
           [dict(type='recover_weapon',weapon='sniper',reserve=8), dict(type='ensure_ammo',minimum={'sniper':8})]),
        st('pressure_qc','terminal',75.5,16.5,'PRESSURE REGULATION / CONTROL DE MECANIZADO',
           [dict(type='objective',id='pressure_regulated'), dict(type='door',id='assembly_gate')], pressure_questions,
           prerequisites={'objective':'lmg_collected'}, reward_label='Presión estabilizada · rango verificado'),
        st('foundry_mixed','terminal',57.5,26.5,'MEDIDAS DE FUNDICIÓN / NÚMEROS MIXTOS',
           [dict(type='objective',id='foundry_mixed_complete')], mixed_questions,
           prerequisites={'objective':'pressure_regulated'}, reward_label='Medidas mixtas verificadas'),
        st('mad_foundry_01','mad',52.5,25.5,'M.A.D. #1 / SLAG PROCESSING',
           [dict(type='upgrade_next',max_mod=3)], mad_questions, prerequisites={'objective':'precision_64_learned'}),
        st('mad_foundry_02','mad',72.5,26.5,'M.A.D. #2 / PRESSURE REGULATION',
           [dict(type='upgrade_next',max_mod=3)], mad_questions, prerequisites={'objective':'pressure_regulated'}),
        st('mad_foundry_03','mad',53.5,3.5,'M.A.D. #3 / PROJECT CHAMBER',
           [dict(type='upgrade_next',max_mod=3)], mad_questions, hidden_on_minimap=True, prerequisites={'objective':'pressure_regulated'}),
        st('mad_foundry_04','mad',42.5,40.5,'M.A.D. #4 / FORGE PITS',
           [dict(type='upgrade_next',max_mod=3)], mad_questions, prerequisites={'objective':'rocket_collected'}),
        st('core_access_terminal','install',3.5,31.5,'CONVERTER CORE ACCESS / EMERGENCY OVERRIDE',
           [dict(type='objective',id='core_access_unlocked')], prerequisites={'objective':'crucible_defeated'},
           interaction_message='FOUNDRY OUTPUT 0% // CONVERTER CORE ACCESS UNLOCKED',
           interaction_panel=dict(
               title='CONVERTER CORE ACCESS',
               lines=[
                   'FOUNDRY OUTPUT: 0%',
                   'CONVERTER POWER FEED: INTERRUPTED',
                   'EMERGENCY POWER: ACTIVE',
                   'CORE ACCESS: UNLOCKED',
                   'ADVERTENCIA: GEOMETRÍA INTERNA NO ESTABLE',
               ],
           )),
        st('converter_core_access','exit',2.5,35.5,'CONVERTER CORE ACCESS',[]),
    ]

    def obj(i, rule=None):
        return dict(id=i, condition=rule or {})
    objectives = [
        obj('foundry_started',{'trigger':'descent'}),
        obj('precision_64_learned'),
        obj('manual_precision_complete'),
        obj('lmg_collected',{'collected':'lmg_weapon'}),
        obj('pressure_regulated'),
        obj('foundry_mixed_complete'),
        obj('rocket_collected',{'collected':'rocket_launcher'}),
        obj('utcj_4_found',{'secret':'utcj_foundry'}),
        obj('forge_run_started',{'trigger':'forge_run_a'}),
        obj('forge_run_complete',{'trigger':'forge_run_gate'}),
        obj('crucible_spawned',{'wave':'crucible'}),
        obj('crucible_defeated',{'group_defeated':'crucible'}),
        obj('core_access_unlocked'),
        obj('foundry_complete',{'complete':True}),
    ]

    wave_ids = [
        'descent','thermal','heavy_first','heavy_second','slag','pressure',
        'assembly_first','assembly_second','pits','forge_run_a','forge_run_b',
        'crucible','crucible_support'
    ]
    waves = [dict(id=g,groups=[g]) for g in wave_ids]
    def tr(i, rule, actions, **kw): return dict(id=i,condition=rule,actions=actions,**kw)
    def wave(g): return [dict(type='activate_wave',id=g)]
    triggers = [
        tr('descent',{'zone':[3,16,10,26]},wave('descent'),message='FOUNDRY // CORE TEMPERATURE 1147°C · SAFETY LIMIT EXCEEDED'),
        tr('thermal',{'zone':[11,14,24,28]},wave('thermal'),message='THERMAL PROCESSING // PURGE SYSTEM ACTIVE'),
        tr('heavy_first',{'all':[{'objective':'manual_precision_complete'},{'zone':[25,14,40,28]}]},wave('heavy_first'),message='HEAVY FABRICATION // CONTACT'),
        tr('heavy_second',{'collected':'lmg_weapon'},wave('heavy_second'),message='LMG ONLINE // HEAVY FABRICATION BREACH'),
        tr('slag',{'all':[{'objective':'lmg_collected'},{'zone':[41,14,55,28]}]},wave('slag'),message='SLAG PROCESSING // FAST THERMAL SIGNATURE'),
        tr('pressure',{'zone':[56,15,77,28]},wave('pressure'),message='PRESSURE REGULATION // QC CALIBRATION REQUIRED'),
        tr('assembly_first',{'all':[{'objective':'pressure_regulated'},{'zone':[56,29,77,42]}]},wave('assembly_first'),message='FORGE ASSEMBLY // DEMOLITION SYSTEM DETECTED'),
        tr('assembly_second',{'collected':'rocket_launcher'},wave('assembly_second'),message='ROCKET LAUNCHER ONLINE // HOSTILES INBOUND'),
        tr('pits',{'all':[{'objective':'rocket_collected'},{'zone':[41,29,55,42]}]},wave('pits'),message='FORGE PITS // HEAVY UNIT DETECTED'),
        tr('forge_run_a',{'all':[{'objective':'rocket_collected'},{'zone':[25,29,40,42]}]},wave('forge_run_a'),message='THE FORGE RUN // KEEP MOVING'),
        tr('forge_run_b',{'all':[{'trigger':'forge_run_a'},{'zone':[25,29,33,42]}]},wave('forge_run_b'),message='THE FORGE RUN // THERMAL SURGE'),
        tr('forge_run_gate',{'all':[{'trigger':'forge_run_b'},{'zone':[25,29,28,42]}]},[dict(type='door',id='crucible_gate')],message='CORE FURNACE ACCESS // OPEN'),
        tr('crucible',{'all':[{'door_open':'crucible_gate'},{'zone':[1,29,24,42]}]},wave('crucible'),message='THE CRUCIBLE // PRESSURE LOCKS ENGAGED'),
        tr('crucible_support',{'all':[{'enemy_alive':'the_crucible'},{'enemy_hp_below':{'id':'the_crucible','ratio':.5}}]},wave('crucible_support'),message='MELTDOWN // SECONDARY HOSTILES RELEASED'),
        tr('crucible_supply',{'trigger':'forge_run_gate'},[dict(type='ensure_ammo',minimum={'pistol':24,'shotgun':8,'assault':45,'sawed_off':8,'sniper':10,'lmg':90,'rocket':3})],message='EMERGENCY SUPPLY // CORE FURNACE PROTOCOL'),
        tr('el_toro_unlock',{'all':[{'secret':'utcj_foundry'},{'campaign_utcj_count':4}]},[
            dict(type='recover_weapon',weapon='el_toro',reserve=2),
            dict(type='ensure_ammo',minimum={'el_toro':3}),
        ],message='PROJECT U.T.C.J. // ENCRYPTED PAYLOAD 100% · EL TORO AUTHORIZED'),
        tr('core_ready',{'objective':'crucible_defeated'},[],message='THE CRUCIBLE OFFLINE // ACCESS EMERGENCY OVERRIDE'),
    ]

    def cp(i,order,zone,x,y,pre):
        return dict(id=i,order=order,zone=zone,prerequisites=pre,
                    respawn_position=dict(x=x,y=y),respawn_angle=0)
    checkpoints = [
        cp('foundry_descent',0,[1,16,9,25],3.5,20.5,{}),
        cp('foundry_lmg',1,[25,14,39,27],26.5,20.5,{'objective':'lmg_collected'}),
        cp('foundry_pressure',2,[56,15,76,27],57.5,20.5,{'objective':'pressure_regulated'}),
        cp('foundry_rocket',3,[56,29,76,41],57.5,35.5,{'objective':'rocket_collected'}),
        cp('foundry_run',4,[25,29,39,41],39.0,35.5,{'objective':'forge_run_started'}),
        cp('foundry_crucible',5,[1,29,23,41],22.0,35.5,{'objective':'forge_run_complete'}),
    ]

    heat_zones = [
        dict(id='thermal_a',zone=[15,18,19,24],period=8.0,warning=2.6,active=2.0,offset=0.0,damage=14),
        dict(id='thermal_b',zone=[20,15,23,20],period=9.2,warning=2.7,active=2.0,offset=3.1,damage=14),
        dict(id='run_a',zone=[34,29,39,35],period=7.0,warning=2.3,active=1.8,offset=1.4,damage=16),
        dict(id='run_b',zone=[27,35,32,41],period=7.6,warning=2.3,active=1.9,offset=4.0,damage=16),
        dict(id='crucible_left',zone=[2,30,7,40],period=8.2,warning=2.4,active=1.8,offset=1.0,damage=18,boss_only=True),
        dict(id='crucible_right',zone=[17,30,22,40],period=8.2,warning=2.4,active=1.8,offset=5.1,damage=18,boss_only=True),
    ]
    crucible_locks = [
        dict(id='pressure_a',x=5.5,y=31.5,field='lock_a_hp',phase='pressure'),
        dict(id='pressure_b',x=12.0,y=40.0,field='lock_b_hp',phase='pressure'),
        dict(id='pressure_c',x=19.5,y=31.5,field='lock_c_hp',phase='pressure'),
        dict(id='emergency_a',x=5.5,y=39.5,field='emergency_a_hp',phase='meltdown'),
        dict(id='emergency_b',x=19.5,y=39.5,field='emergency_b_hp',phase='meltdown'),
    ]

    return dict(
        id='foundry', revision=1, name='LEVEL 04 / THE FOUNDRY', grid=grid,
        enemy_types=types, encounters={'clasico':classic,'doom':doom}, items=items,
        stations=stations, doors=[dict(id='fabrication_gate',cell=[24,20]), dict(id='assembly_gate',cell=[66,28]), dict(id='crucible_gate',cell=[24,35])],
        checkpoints=checkpoints, triggers=triggers, waves=waves, objectives=objectives,
        secrets=[dict(id='utcj_foundry',kind='utcj',on_shot=True,x=48.5,y=6.5)],
        exit=dict(station='converter_core_access',condition={'objective':'core_access_unlocked'},auto_zone=[1,33,4,38]),
        initial_loadout={'pistol':dict(loaded=12,reserve=24,mods=0)}, scale_resources=False,
        player_config=dict(max_hp=100,max_armor=100),
        respawn_rules=dict(min_hp=60,grace=2.5,ammo={'pistol':18,'shotgun':8,'assault':30,'sawed_off':6,'sniper':8,'lmg':45,'rocket':1}),
        transition_resupply=dict(min_hp=60,ammo={'pistol':24,'shotgun':10,'assault':36,'sawed_off':8,'sniper':10,'lmg':60,'rocket':2}),
        conveyors=[], boss_nodes=[], heat_zones=heat_zones, crucible_locks=crucible_locks,
        zones=[dict(label=n,zone=[x1,y1,x2+1,y2+1]) for n,(x1,y1,x2,y2) in rooms],
        objective_hints=[
            dict(until='precision_64_learned',text='THERMAL PROCESSING → APRENDE LA ESCALA 1/64'),
            dict(until='manual_precision_complete',text='THERMAL PROCESSING → COMPLETA LA CALIBRACIÓN MANUAL'),
            dict(until='lmg_collected',text='HEAVY FABRICATION → RECUPERA LA LMG'),
            dict(until='pressure_regulated',text='PRESSURE REGULATION → VERIFICA EL RANGO DE MECANIZADO'),
            dict(until='rocket_collected',text='FORGE ASSEMBLY → RECUPERA ROCKET LAUNCHER'),
            dict(until='forge_run_complete',text='THE FORGE RUN → AVANZA HASTA CORE FURNACE'),
            dict(until='crucible_defeated',text='THE CRUCIBLE → ROMPE LOCKS Y ATACA EL NÚCLEO'),
            dict(until='core_access_unlocked',text='EMERGENCY OVERRIDE → ABRE CONVERTER CORE ACCESS'),
            dict(until='foundry_complete',text='CONVERTER CORE ACCESS → CONTINÚA'),
        ],
        intro=(
            'LEVEL 04 — THE FOUNDRY. La fuente de energía del Converter atraviesa una fundición fuera de control. '
            'Aprende la escala 1/64 antes de usarla, domina las purgas térmicas, recupera armamento pesado y corta '
            'la alimentación del núcleo. La matemática calibra la instalación; el combate hace el resto.'
        ),
        navigation=[
            dict(until='precision_64_learned',x=12.5,y=15.5),
            dict(until='manual_precision_complete',x=22.5,y=26.5),
            dict(until='lmg_collected',x=32.5,y=20.5),
            dict(until='pressure_regulated',x=75.5,y=16.5),
            dict(until='rocket_collected',x=67.5,y=35.5),
            dict(until='forge_run_complete',x=25.5,y=35.5),
            dict(until='crucible_defeated',x=12,y=35),
            dict(until='core_access_unlocked',x=3.5,y=31.5),
            dict(until='foundry_complete',x=2.5,y=35.5),
        ],
        campaign_secrets=4,
        transfer_label='FOUNDRY SECTOR',
        teaser=(
            'FOUNDRY OUTPUT: 0%\nCONVERTER POWER FEED: INTERRUPTED\nEMERGENCY POWER: ACTIVE\n'
            'CORE ACCESS UNLOCKED\nLEVEL 05 — THE CONVERTER'
        ),
    )
