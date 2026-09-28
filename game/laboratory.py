"""Level 03 — The Laboratory.

The first level that explicitly teaches 1/32 and mixed measurements before
assessing them.  Combat escalates through Stalkers and ends with Specimen K-32,
a movement/adaptation boss rather than another shield puzzle.
"""
from copy import deepcopy
from .enemigos import ENEMIES


def laboratory():
    grid = [[1] * 66 for _ in range(38)]
    rooms = [
        ('LAB TRANSIT / DECONTAMINATION', [1, 15, 8, 22]),
        ('PRECISION METROLOGY', [10, 12, 22, 23]),
        ('BALLISTICS TESTING RANGE', [24, 12, 38, 23]),
        ('CONTAINMENT WING A', [40, 2, 53, 11]),
        ('SPECIMEN OBSERVATION', [40, 13, 53, 23]),
        ('CONTAINMENT WING B / CRYOGENIC', [55, 14, 64, 23]),
        ('RESEARCH ARCHIVES / RESTRICTED', [55, 2, 64, 12]),
        ('CORE ANALYSIS / CONTAINMENT C', [28, 25, 43, 35]),
        ('SPECIMEN VAULT', [45, 25, 64, 35]),
    ]
    for _, (x1, y1, x2, y2) in rooms:
        for y in range(y1, y2 + 1):
            for x in range(x1, x2 + 1):
                grid[y][x] = 0

    # Main route plus a loop through Archives.  Doors remain data-driven.
    for x, y in [
        (9,18), (23,18),                 # Transit -> Precision -> Ballistics
        (39,16), (39,15), (39,14), (39,13), (39,12), (39,11), (39,10), (39,9), (39,8),
        (46,12),                         # Wing A -> Observation
        (54,18),                         # Observation -> Wing B
        (59,13),                         # Wing B -> Archives
        (42,24),                         # Observation -> Core
        (44,30),                         # Core -> Vault (containment gate)
        (59,24),                         # Archives -> Vault loop (sealed until containment 100%)
    ]:
        grid[y][x] = 0

    # Ballistics access is locked until the introductory 1/32 lesson is completed.
    grid[18][23] = 3
    # The specimen vault remains sealed until all three containment nodes are calibrated.
    grid[30][44] = 3
    grid[24][59] = 3

    # Lab benches, observation equipment and containment cover.
    for x, y in [
        (14,15),(18,20),(21,14),(28,15),(32,19),(36,14),
        (42,5),(47,8),(51,4),(43,17),(49,21),(52,15),
        (57,17),(62,20),(57,5),(62,9),(31,28),(36,33),(40,27),
        (48,28),(53,32),(59,27),(62,33),
    ]:
        grid[y][x] = 2

    types = deepcopy(ENEMIES)
    # Carry forward the specialized ranged enemies from Factory without coupling level modules.
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
    types['stalker'] = dict(
        name='STALKER', hp=82, speed=1.28, range=.85, color='#65b9b2',
        radius=.22, vision=15, search_seconds=9, rear_multiplier=1.25,
        rear_angle=.95, reveal_time=.85, lunge_time=.48, recovery=1.15,
        lunge_speed=4.8, stalk_delay=1.35,
    )
    types['k32'] = dict(
        name='SPECIMEN K-32', hp=450, speed=1.14, range=1.05, color='#b96d86',
        radius=.50, vision=19, search_seconds=14, rear_multiplier=1.1,
        rear_angle=.9, projectile_speed=4.8, ranged=True,
        overload_seconds=5.8, exhausted_seconds=3.2,
        overload_multiplier=.30, exhausted_multiplier=1.50,
        ram_speed=5.1, energy_speed=4.5,
    )

    def e(i, kind, x, y, group):
        base = dict(id=i, type=kind, x=x, y=y, group=group, active=False)
        if kind == 'stalker':
            base.update(stalker_mode='stalk', phase_time=0, cooldown=0, attack_index=0)
        if kind == 'k32':
            base.update(boss_mode='hunting', overload_cycles=0, phase_time=0,
                        attack_index=0, cooldown=0, support_deployed=False)
        return base

    classic = [
        e('lab_t1','worker',6.5,16.5,'transit'), e('lab_t2','worker',7,21,'transit'), e('lab_t3','gunner',5.5,21.5,'transit'),
        e('met_1','worker',13,14,'precision'), e('met_2','crawler',19,21,'precision'), e('met_3','rivet',21,16,'precision'),
        e('bal_1','rivet',27,14,'ballistics_first'), e('bal_2','sentinel',36,16,'ballistics_first'), e('bal_3','worker',30,22,'ballistics_first'),
        e('bal_4','crawler',36,22,'ballistics_second'), e('bal_5','rivet',25,21,'ballistics_second'), e('bal_6','gunner',33,14,'ballistics_second'),
        e('a_1','stalker',49,5,'wing_a'), e('a_2','worker',43,9,'wing_a'), e('a_3','crawler',52,10,'wing_a'), e('a_4','rivet',42,4,'wing_a'),
        e('obs_1','gunner',51,16,'observation'), e('obs_2','worker',43,21,'observation'), e('obs_3','crawler',49,22,'observation'), e('obs_4','rivet',42,15,'observation'),
        e('b_1','stalker',61,16,'wing_b'), e('b_2','gunner',57,21,'wing_b'), e('b_3','crawler',63,21,'wing_b'), e('b_4','crawler',56,16,'wing_b'), e('b_5','sentinel',63,16,'wing_b'),
        e('arc_1','stalker',62,5,'archives'), e('arc_2','worker',57,10,'archives'), e('arc_3','rivet',63,10,'archives'),
        e('core_1','gunner',31,27,'core'), e('core_2','stalker',40,32,'core'), e('core_3','crawler',35,34,'core'), e('core_4','rivet',41,27,'core'),
        e('vault_1','worker',48,27,'vault_intro'), e('vault_2','crawler',55,34,'vault_intro'), e('vault_3','gunner',62,29,'vault_intro'),
        e('k32_support_1','stalker',62,34,'k32_support'),
        e('specimen_k32','k32',55,30,'k32'),
    ]
    doom = deepcopy(classic) + [
        e('doom_t','crawler',3,21,'transit'), e('doom_met','gunner',17,13,'precision'),
        e('doom_bal1','sentinel',25,16,'ballistics_first'), e('doom_bal2','rivet',37,20,'ballistics_second'),
        e('doom_a','stalker',52,6,'wing_a'), e('doom_obs','gunner',46,15,'observation'),
        e('doom_b1','stalker',58,18,'wing_b'), e('doom_b2','crawler',62,22,'wing_b'),
        e('doom_arc','gunner',56,4,'archives'), e('doom_core1','stalker',30,33,'core'), e('doom_core2','sentinel',39,26,'core'),
        e('doom_k32_support','stalker',47,34,'k32_support'),
    ]

    items = []
    def item(i, kind, x, y, n=1, **kw):
        items.append(dict(id=i, type=kind, x=x, y=y, amount=n, **kw))

    item('lab_pistol_ammo','ammo',4.5,20.5,20,weapon='pistol')
    item('lab_assault_ammo','ammo',19.5,13.5,30,weapon='assault')
    item('lab_precision_armor','armor',21.5,22.5,20)
    item('sniper_rifle','weapon',31.5,18.5,weapon='sniper',reserve=15)
    item('sniper_ammo_a','ammo',37.5,22.5,10,weapon='sniper')
    item('wing_a_med','health',51.5,9.5,25)
    item('observation_shells','ammo',42.5,22.5,8,weapon='shotgun')
    item('wing_b_assault','ammo',56.5,22.5,36,weapon='assault')
    item('wing_b_sniper','ammo',63.5,15.5,8,weapon='sniper')
    item('archives_armor','armor',56.5,3.5,30)
    item('core_sawed','ammo',29.5,34.5,8,weapon='sawed_off')
    item('core_sniper','ammo',41.5,34.5,10,weapon='sniper')
    item('vault_med','health',46.5,34.5,30)
    item('vault_assault','ammo',49.5,34.5,42,weapon='assault')
    item('vault_sniper','ammo',52.5,34.5,10,weapon='sniper')
    item('doom_lab_sniper','ammo',63.5,11.5,6,weapon='sniper',difficulties=['doom'])

    def fixed(prompt, answer, choices, category='to_decimal', explanation='', mode='choice'):
        formats = {
            'to_decimal':'decimal', 'to_fraction':'fraction', 'mixed_to_decimal':'decimal',
            'decimal_to_mixed':'mixed', 'equivalence':'decimal', 'theory':'text', 'special':'integer'
        }
        return dict(prompt=prompt, answer=answer, choices=choices if mode=='choice' else [],
                    category=category, mode=mode, expected_format=formats.get(category,'text'),
                    explanation=explanation or f'Respuesta: {answer}')

    def qpool(*questions, categories=None):
        return dict(
            categories_allowed=categories or sorted({q['category'] for q in questions}),
            denominators_allowed=[2,4,8,16,32], multiple_choice_allowed=True,
            manual_allowed=True, fixed_questions=list(questions),
        )

    def st(i, kind, x, y, label, reward, q=None, **kw):
        return dict(id=i, kind=kind, x=x, y=y, label=label,
                    interaction_point=dict(x=x,y=y), interaction_distance=1.8,
                    question=q or {}, reward=reward, **kw)

    precision_questions = qpool(
        fixed(
            'CALIBRACIÓN DE PRECISIÓN: Hasta ahora trabajaste con divisiones de hasta 1/16″. Si 1/16 se divide nuevamente entre dos obtenemos 1/32″. ¿Cuál es el equivalente decimal de 1/32″?',
            '.03125', ['.015625','.03125','.0625'], 'to_decimal',
            '1/16 ÷ 2 = 1/32. En decimal, .0625 ÷ 2 = .03125. El laboratorio usa esta precisión adicional.'
        ),
        fixed(
            'NUEVA ESCALA: 1/32″ equivale a .03125″. Si una lectura muestra 3/32″, ¿qué decimal corresponde?',
            '.09375', ['.0625','.09375','.1875'], 'to_decimal',
            'Cada treintaidosavo vale .03125. Tres veces .03125 = .09375.'
        ),
        fixed(
            'EQUIVALENCIAS: 16/32″ representa exactamente la mitad de una pulgada. ¿Qué decimal equivale a 16/32″?',
            '.5', ['.25','.5','.75'], 'equivalence',
            '16/32 se simplifica a 1/2 y 1/2″ = .5″.'
        ),
    )
    node_a_questions = qpool(
        fixed('CONTAINMENT NODE A: El sensor marca 5/32″. ¿Cuál es su equivalente decimal?', '.15625', ['.125','.15625','.3125'], 'to_decimal', '5 × .03125 = .15625.'),
        fixed('CONTAINMENT NODE A: ¿Qué decimal equivale a 7/32″?', '.21875', ['.1875','.21875','.4375'], 'equivalence', '7 × .03125 = .21875.'),
        fixed('CONTAINMENT NODE A: La lectura es .28125″. ¿Qué fracción simplificada representa?', '9/32', ['7/32','9/32','11/32'], 'to_fraction', '.28125″ = 9/32″.'),
    )
    mixed_intro_questions = qpool(
        fixed(
            'MEDIDAS MAYORES A UNA PULGADA: 1 3/8″ significa 1 pulgada completa + 3/8″. Como 3/8 = .375, ¿cuál es la medida decimal total?',
            '1.375', ['1.125','1.375','1.625'], 'mixed_to_decimal',
            '1 + .375 = 1.375″. La parte entera se conserva y solo convertimos la fracción.'
        ),
        fixed(
            'NÚMERO MIXTO: 1 1/2″ significa 1 pulgada + .500″. ¿Cuál es su equivalente decimal?',
            '1.5', ['.5','1.5','2.5'], 'mixed_to_decimal',
            '1 + .5 = 1.5″.'
        ),
        fixed(
            'NÚMERO MIXTO: Sabemos que 5/16 = .3125. Entonces 1 5/16″ equivale a…',
            '1.3125', ['1.15625','1.3125','1.625'], 'mixed_to_decimal',
            'Una pulgada completa + .3125″ = 1.3125″.'
        ),
    )
    node_b_questions = qpool(
        fixed('CONTAINMENT NODE B: Una pieza mide 1 5/8″. Como 5/8 = .625, ¿cuál es su medida decimal?', '1.625', ['1.3125','1.625','1.875'], 'mixed_to_decimal', '1 + .625 = 1.625″.'),
        fixed('CONTAINMENT NODE B: 1 7/16″ equivale a…', '1.4375', ['1.21875','1.4375','1.875'], 'mixed_to_decimal', '7/16 = .4375; por tanto 1 7/16″ = 1.4375″.'),
        fixed('CONTAINMENT NODE B: 1 3/32″ equivale a…', '1.09375', ['1.03125','1.09375','1.1875'], 'mixed_to_decimal', '3/32 = .09375; 1 + .09375 = 1.09375″.'),
    )
    node_c_questions = qpool(
        fixed('CONTAINMENT NODE C: El escáner registra 1.625″. La parte decimal .625 equivale a 5/8. ¿Cuál es el número mixto?', '1 5/8', ['1 3/8','1 5/8','1 5/16'], 'decimal_to_mixed', '1.625″ = 1 + .625 = 1 5/8″.'),
        fixed('CONTAINMENT NODE C: El escáner registra 1.21875″. Sabemos que .21875 = 7/32. ¿Cuál es el número mixto?', '1 7/32', ['1 5/32','1 7/32','1 7/16'], 'decimal_to_mixed', '1.21875″ = 1 7/32″.'),
        fixed('CONTAINMENT NODE C: ¿Cuál medida mixta equivale a 1.3125″?', '1 5/16', ['1 3/16','1 5/16','1 5/8'], 'decimal_to_mixed', '.3125 = 5/16; por tanto 1.3125″ = 1 5/16″.'),
    )

    mad_questions = qpool(
        fixed('M.A.D. LAB: Convierte 11/32″ a decimal.', '.34375', ['.3125','.34375','.6875'], 'to_decimal', '11 × .03125 = .34375.'),
        fixed('M.A.D. LAB: ¿Qué decimal equivale a 13/32″?', '.40625', ['.375','.40625','.8125'], 'equivalence', '13 × .03125 = .40625.'),
        fixed('M.A.D. LAB: Convierte .46875″ a fracción simplificada.', '15/32', ['13/32','15/32','15/16'], 'to_fraction', '.46875″ = 15/32″.'),
    )

    stations = [
        st('precision_training','terminal',12.5,13.5,'CALIBRACIÓN DE PRECISIÓN / 1/32',
           [dict(type='objective',id='precision_training_complete'), dict(type='door',id='ballistics_gate')], precision_questions,
           reward_label='Nueva escala 1/32 habilitada · acceso a Ballistics'),
        st('lab_armory','armory',20.5,22.5,'DDI RESEARCH ARMORY / EQUIPO PREVIO',
           [dict(type='recover_weapon',weapon='shotgun',reserve=10), dict(type='ensure_ammo',minimum={'shotgun':10})]),
        st('containment_node_a','terminal',51.5,9.5,'CONTAINMENT NODE A / PRECISIÓN',
           [dict(type='objective',id='containment_a')], node_a_questions, prerequisites={'objective':'sniper_collected'}, reward_label='CONTAINMENT STABILITY 33%'),
        st('mixed_measurement_intro','terminal',42.5,21.5,'METROLOGÍA / NÚMEROS MIXTOS',
           [dict(type='objective',id='mixed_numbers_learned')], mixed_intro_questions, prerequisites={'objective':'containment_a'}, reward_label='Números mixtos habilitados'),
        st('mad_lab_01','mad',51.5,15.5,'M.A.D. #1 / SPECIMEN OBSERVATION',
           [dict(type='upgrade_next',max_mod=2)], mad_questions, prerequisites={'objective':'mixed_numbers_learned'}),
        st('containment_node_b','terminal',63.5,22.5,'CONTAINMENT NODE B / MEDIDA MIXTA',
           [dict(type='objective',id='containment_b')], node_b_questions, prerequisites={'objective':'mixed_numbers_learned'}, reward_label='CONTAINMENT STABILITY 66%'),
        st('mad_lab_02','mad',62.5,4.5,'M.A.D. #2 / RESTRICTED ARCHIVES',
           [dict(type='upgrade_next',max_mod=2)], mad_questions, hidden_on_minimap=True, prerequisites={'objective':'containment_b'}),
        st('mad_lab_03','mad',30.5,33.5,'M.A.D. #3 / CORE ANALYSIS',
           [dict(type='upgrade_next',max_mod=2)], mad_questions, prerequisites={'objective':'containment_b'}),
        st('containment_node_c','terminal',41.5,33.5,'CONTAINMENT NODE C / RECONSTRUCCIÓN',
           [dict(type='objective',id='containment_c'), dict(type='door',id='vault_gate'),
            dict(type='door',id='vault_gate_archive')], node_c_questions,
           prerequisites={'objective':'containment_b'}, reward_label='CONTAINMENT STABILITY 100% · SPECIMEN VAULT UNLOCKED'),
        st('research_archive_terminal','install',58.5,3.5,'RESEARCH ARCHIVES / PROJECT CONVERTER', [],
           prerequisites={'objective':'containment_b'},
           interaction_message='ARCHIVES // ORGANIC RECONSTRUCTION: UNAUTHORIZED',
           interaction_panel=dict(
               title='PROJECT CONVERTER — ARCHIVOS RESTRINGIDOS',
               lines=[
                   'SISTEMA: RECONSTRUCCIÓN DIMENSIONAL DE MATERIA',
                   'AUTORIZADO: METALES / POLÍMEROS / MATERIALES SINTÉTICOS',
                   'RECONSTRUCCIÓN ORGÁNICA: NO AUTORIZADA',
                   'REGISTRO K-32: CONTENCIÓN COMPROMETIDA',
               ],
           )),
        st('core_analysis_terminal','install',62.5,26.5,'CORE ANALYSIS / SOURCE TRACE',
           [dict(type='objective',id='source_trace_complete')], prerequisites={'objective':'k32_defeated'},
           interaction_message='ANÁLISIS COMPLETO // FUENTE: FOUNDRY SECTOR',
           interaction_panel=dict(
               title='CORE ANALYSIS — SOURCE TRACE',
               lines=[
                   'CONTENCIÓN RESTAURADA',
                   'SEÑAL ANÓMALA: TODAVÍA ACTIVA',
                   'FUENTE DE ENERGÍA PRIMARIA: FOUNDRY SECTOR',
                   'CONVERTER POWER REQUEST: 417%',
                   'SAFETY LIMITER: DISABLED',
               ],
           )),
        st('foundry_transit','exit',63.5,34.5,'FOUNDRY TRANSIT',[]),
    ]
    # Door stations are not required; doors are opened by terminal rewards.

    def obj(i, rule=None): return dict(id=i, condition=rule or {})
    objectives = [
        obj('laboratory_started',{'trigger':'transit'}),
        obj('precision_training_complete'),
        obj('sniper_collected',{'collected':'sniper_rifle'}),
        obj('containment_a'),
        obj('mixed_numbers_learned'),
        obj('containment_b'),
        obj('utcj_3_found',{'secret':'utcj_laboratory'}),
        obj('containment_c'),
        obj('containment_stability_100',{'all':[{'objective':'containment_a'},{'objective':'containment_b'},{'objective':'containment_c'}]}),
        obj('k32_spawned',{'wave':'k32'}),
        obj('k32_defeated',{'group_defeated':'k32'}),
        obj('source_trace_complete'),
        obj('laboratory_complete',{'complete':True}),
    ]

    wave_ids = ['transit','precision','ballistics_first','ballistics_second','wing_a','observation','wing_b','archives','core','vault_intro','k32','k32_support']
    waves = [dict(id=g,groups=[g]) for g in wave_ids]
    def tr(i, rule, actions, **kw): return dict(id=i,condition=rule,actions=actions,**kw)
    def wave(g): return [dict(type='activate_wave',id=g)]
    triggers = [
        tr('transit',{'zone':[4,15,9,23]},wave('transit'),message='LABORATORY // CONTAINMENT INTEGRITY 41%'),
        tr('precision',{'zone':[10,12,23,24]},wave('precision'),message='PRECISION METROLOGY // CALIBRATION REQUIRED'),
        tr('ballistics_first',{'all':[{'door_open':'ballistics_gate'},{'zone':[24,12,39,24]}]},wave('ballistics_first'),message='BALLISTICS RANGE // LONG-RANGE CONTACT'),
        tr('ballistics_second',{'collected':'sniper_rifle'},wave('ballistics_second'),message='SNIPER RIFLE ONLINE // TESTING RANGE COMPROMISED'),
        tr('wing_a',{'zone':[40,2,54,12]},wave('wing_a'),message='CONTAINMENT WING A // MOTION DETECTED'),
        tr('containment_a_feedback',{'objective':'containment_a'},[],message='CONTAINMENT STABILITY // 33%'),
        tr('observation',{'all':[{'objective':'containment_a'},{'zone':[40,13,54,24]}]},wave('observation'),message='SPECIMEN OBSERVATION // ORGANIC TESTING RECORDS FOUND'),
        tr('wing_b',{'all':[{'objective':'mixed_numbers_learned'},{'zone':[55,14,65,24]}]},wave('wing_b'),message='CRYOGENIC STORAGE // CONTAINMENT FAILURE'),
        tr('containment_b_feedback',{'objective':'containment_b'},[],message='CONTAINMENT STABILITY // 66%'),
        tr('archives',{'all':[{'objective':'containment_b'},{'zone':[55,2,65,13]}]},wave('archives'),message='RESTRICTED ARCHIVES // ORGANIC RECONSTRUCTION: UNAUTHORIZED'),
        tr('core',{'all':[{'objective':'containment_b'},{'zone':[28,25,44,36]}]},wave('core'),message='CORE ANALYSIS // FINAL CONTAINMENT CALIBRATION'),
        tr('containment_c_feedback',{'objective':'containment_stability_100'},[],message='CONTAINMENT STABILITY // 100% · SPECIMEN VAULT UNLOCKED'),
        tr('vault_intro',{'all':[{'objective':'containment_stability_100'},{'zone':[45,25,65,36]}]},wave('vault_intro'),message='SPECIMEN VAULT // K-32 CHAMBER BREACHED'),
        tr('k32',{'all':[{'objective':'containment_stability_100'},{'group_defeated':'vault_intro'},{'zone':[48,27,63,35]}]},wave('k32'),message='SPECIMEN K-32 // CONTAINMENT LOST'),
        tr('k32_support',{'all':[{'enemy_alive':'specimen_k32'},{'enemy_hp_below':{'id':'specimen_k32','ratio':.5}}]},wave('k32_support'),message='SPECIMEN K-32 // SECONDARY MOTION DETECTED'),
        tr('k32_supply',{'objective':'containment_stability_100'},[dict(type='ensure_ammo',minimum={'pistol':24,'shotgun':8,'assault':45,'sawed_off':8,'sniper':12})],message='EMERGENCY SUPPLY // SPECIMEN PROTOCOL'),
        tr('analysis_ready',{'objective':'k32_defeated'},[],message='K-32 NEUTRALIZED // ACCESS CORE ANALYSIS TERMINAL'),
    ]

    def cp(i,order,zone,x,y,pre):
        return dict(id=i,order=order,zone=zone,prerequisites=pre,
                    respawn_position=dict(x=x,y=y),respawn_angle=0)
    checkpoints = [
        cp('lab_transit',0,[1,15,8,22],3.5,18.5,{}),
        cp('lab_ballistics',1,[24,12,38,23],25.5,18.5,{'objective':'sniper_collected'}),
        cp('lab_containment_a',2,[40,2,53,23],42.5,18.5,{'objective':'containment_a'}),
        cp('lab_containment_b',3,[55,2,64,23],56.5,18.5,{'objective':'containment_b'}),
        cp('lab_before_k32',4,[28,25,43,35],41.5,30.5,{'objective':'containment_stability_100'}),
    ]

    return dict(
        id='laboratory', revision=1, name='LEVEL 03 / THE LABORATORY', grid=grid,
        enemy_types=types, encounters={'clasico':classic,'doom':doom}, items=items,
        stations=stations, doors=[
            dict(id='ballistics_gate',cell=[23,18]),
            dict(id='vault_gate',cell=[44,30]),
            dict(id='vault_gate_archive',cell=[59,24]),
        ], checkpoints=checkpoints, triggers=triggers, waves=waves, objectives=objectives,
        secrets=[dict(id='utcj_laboratory',kind='utcj',on_shot=True,x=63.5,y=3.5)],
        exit=dict(station='foundry_transit',condition={'objective':'source_trace_complete'},auto_zone=[60,31,65,36]),
        initial_loadout={'pistol':dict(loaded=12,reserve=24,mods=0)}, scale_resources=False,
        player_config=dict(max_hp=100,max_armor=100),
        respawn_rules=dict(min_hp=60,grace=2.5,ammo={'pistol':18,'shotgun':8,'assault':30,'sawed_off':6,'sniper':8}),
        transition_resupply=dict(min_hp=60,ammo={'pistol':24,'shotgun':10,'assault':36,'sawed_off':8,'sniper':10}),
        conveyors=[], boss_nodes=[],
        zones=[dict(label=n,zone=[x1,y1,x2+1,y2+1]) for n,(x1,y1,x2,y2) in rooms],
        objective_hints=[
            dict(until='precision_training_complete',text='PRECISION METROLOGY → APRENDE LA ESCALA 1/32'),
            dict(until='sniper_collected',text='BALLISTICS RANGE → RECUPERA SNIPER RIFLE'),
            dict(until='containment_a',text='CONTAINMENT WING A → CALIBRA NODE A'),
            dict(until='mixed_numbers_learned',text='SPECIMEN OBSERVATION → APRENDE NÚMEROS MIXTOS'),
            dict(until='containment_b',text='CRYOGENIC STORAGE → CALIBRA NODE B'),
            dict(until='containment_stability_100',text='CORE ANALYSIS → CALIBRA NODE C'),
            dict(until='k32_defeated',text='SPECIMEN VAULT → SOBREVIVE A K-32'),
            dict(until='source_trace_complete',text='CORE ANALYSIS TERMINAL → LOCALIZA LA FUENTE'),
            dict(until='laboratory_complete',text='SOURCE: FOUNDRY → REACH TRANSIT'),
        ],
        intro=(
            'LEVEL 03 — THE LABORATORY. La señal de Factory termina en un laboratorio de metrología y '
            'reconstrucción dimensional. Aprende la escala 1/32 antes de usarla, restaura los tres sistemas '
            'de contención y descubre qué salió de la cámara K-32.'
        ),
        navigation=[
            dict(until='precision_training_complete',x=12.5,y=13.5),
            dict(until='sniper_collected',x=31.5,y=18.5),
            dict(until='containment_a',x=51.5,y=9.5),
            dict(until='mixed_numbers_learned',x=42.5,y=21.5),
            dict(until='containment_b',x=63.5,y=22.5),
            dict(until='containment_stability_100',x=41.5,y=33.5),
            dict(until='k32_defeated',x=55,y=30),
            dict(until='source_trace_complete',x=62.5,y=26.5),
            dict(until='laboratory_complete',x=63.5,y=34.5),
        ],
        campaign_secrets=4, next_level='foundry',
        transfer_label='RESEARCH LABORATORY',
        teaser=(
            'CONTAINMENT RESTORED\nANOMALOUS SIGNAL REMAINS\nPRIMARY ENERGY SOURCE: FOUNDRY SECTOR\n'
            'CONVERTER POWER REQUEST: 417%\nSAFETY LIMITER: DISABLED\nLEVEL 04 — THE FOUNDRY'
        ),
    )
