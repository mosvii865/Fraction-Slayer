"""Level 01. Original procedural layout; campaign rules remain declarative."""
from copy import deepcopy
from .enemigos import ENEMIES


def workshop():
    grid = [[1] * 46 for _ in range(30)]
    rooms = [
        ('RECEPTION / INSPECTION', [1, 1, 9, 8]),
        ('TOOL STORAGE', [1, 10, 8, 16]),
        ('ASSEMBLY FLOOR', [11, 1, 23, 12]),
        ('CALIBRATION ROOM', [25, 1, 32, 8]),
        ('MAINTENANCE TUNNELS', [25, 10, 32, 17]),
        ('POWER CONTROL', [34, 10, 43, 18]),
        ('FUSE STORAGE', [36, 2, 42, 8]),
        ('GENERATOR HALL', [22, 20, 32, 28]),
        ('EXIT ELEVATOR', [16, 23, 20, 27]),
        ('SERVICE ALCOVE', [18, 15, 23, 17]),
    ]
    for _, (x1, y1, x2, y2) in rooms:
        for y in range(y1, y2 + 1):
            for x in range(x1, x2 + 1):
                grid[y][x] = 0
    for x, y in [(4,9),(10,5),(24,5),(28,9),(33,14),(39,9),(28,18),(28,19),(24,16),(21,25)]:
        grid[y][x] = 0
    for x, y in [(16,5),(16,6),(20,8),(20,9),(28,13),(29,13),(26,24),(30,24)]:
        grid[y][x] = 2
    grid[9][39] = grid[25][21] = 3
    types = deepcopy(ENEMIES)
    types['loader'] = dict(name='LOADER MK-I', hp=250, speed=.9, range=1.25,
        radius=.42, vision=16, search_seconds=10, rear_multiplier=1.65,
        rear_angle=1.0, charge_speed=6.5, stun_seconds=1.75,
        charge_prepare=.9, charge_duration=1.1, recovery=1.1,
        slam_prepare=.85, slam_radius=2.6, damage_multiplier=1.5)

    def e(i, kind, x, y, group):
        return dict(id=i, type=kind, x=x, y=y, group=group, active=False)
    classic = [
        e('welcome_1','worker',8,3,'welcome'), e('welcome_2','worker',8,7,'welcome'),
        e('assembly_1','worker',14,3,'assembly_first'), e('assembly_2','worker',15,10,'assembly_first'),
        e('assembly_3','crawler',18,3,'assembly_first'),
        e('assembly_4','worker',21,3,'assembly_second'), e('assembly_5','worker',22,10,'assembly_second'),
        e('assembly_6','crawler',19,11,'assembly_second'), e('assembly_7','rivet',22,6,'assembly_second'),
        e('tunnel_1','worker',26,15,'maintenance'), e('tunnel_2','worker',31,16,'maintenance'),
        e('tunnel_3','rivet',31,11,'maintenance'),
        e('ambush_1','rivet',35,12,'fuse_ambush'), e('ambush_2','rivet',42,16,'fuse_ambush'),
        e('ambush_3','worker',36,16,'fuse_ambush'), e('ambush_4','worker',41,12,'fuse_ambush'),
        e('generator_1','worker',24,21,'generator_entry'), e('generator_2','crawler',31,22,'generator_entry'),
        e('loader_mk1','loader',28,26,'loader'),
        e('support_1','crawler',23,27,'loader_support'), e('support_2','crawler',31,27,'loader_support'),
    ]
    doom = deepcopy(classic) + [
        e('doom_a1','crawler',12,10,'assembly_first'), e('doom_a2','worker',17,11,'assembly_first'),
        e('doom_a3','rivet',23,2,'assembly_second'),
        e('doom_t1','crawler',26,11,'maintenance'), e('doom_t2','worker',30,17,'maintenance'),
        e('doom_f1','crawler',35,17,'fuse_ambush'), e('doom_f2','worker',42,11,'fuse_ambush'),
        e('doom_g1','crawler',23,22,'generator_entry'), e('doom_b1','rivet',32,27,'loader_support'),
    ]
    items = []
    def item(i, kind, x, y, n=1, **kw):
        items.append(dict(id=i, type=kind, x=x, y=y, amount=n, **kw))
    item('tool_ammo','ammo',3.5,12.5,6,weapon='pistol')
    item('tool_med','health',6.5,14.5,10)
    item('pump_shotgun','weapon',14.5,6.5,weapon='shotgun',reserve=12)
    item('assembly_ammo','ammo',12.5,11.5,12,weapon='pistol')
    item('assembly_med','health',22.5,11.5,25)
    item('tunnel_armor','armor',26.5,16.5,25)
    item('tunnel_shells','ammo',30.5,16.5,8,weapon='shotgun')
    item('main_power_fuse','quest_item',39.5,4.5,item_id='main_power_fuse',label='MAIN POWER FUSE')
    item('power_med','health',42.5,18.5,25)
    item('generator_med','health',23.5,28.5,25)
    item('doom_pistol','ammo',35.5,18.5,12,weapon='pistol',difficulties=['doom'])
    item('doom_shells','ammo',32.5,21.5,4,weapon='shotgun',difficulties=['doom'])

    def qv(prompt, answer, choices, category='to_decimal', explanation=None):
        formats = {'to_fraction':'fraction', 'special':'integer', 'theory':'text'}
        return dict(
            prompt=prompt, answer=answer, choices=choices, category=category, mode='choice',
            expected_format=formats.get(category, 'decimal'),
            explanation=explanation or f'{prompt} Respuesta: {answer}.'
        )
    def question_pool(*variants):
        return dict(
            categories_allowed=sorted({v['category'] for v in variants}),
            denominators_allowed=[2,4,8], multiple_choice_allowed=True, manual_allowed=False,
            fixed_questions=list(variants),
        )
    def st(i, kind, x, y, label, reward, q=None, **kw):
        return dict(id=i,kind=kind,x=x,y=y,label=label,interaction_point=dict(x=x,y=y),
            interaction_distance=1.7,question=q or {},reward=reward,**kw)
    stations = [
        st('tool_storage_terminal','terminal',2.5,14.5,'QC / CALIBRACIÓN BÁSICA → MUNICIÓN',
           [dict(type='ammo',weapon='pistol',amount=12)],
           question_pool(
               qv('Convierte 1/2″ a decimal.', '.5', ['.25','.5','.75'], 'to_decimal', '1/2″ equivale a .5″.'),
               qv('¿Qué decimal equivale a 1/4″?', '.25', ['.125','.25','.5'], 'equivalence', '1/4″ equivale a .25″.'),
               qv('Una medida de 3/4″ equivale a…', '.75', ['.5','.75','.875'], 'equivalence', '3/4″ equivale a .75″.'),
           ), reward_label='+12 municiones de pistola'),
        st('mad_calibration_01','mad',27.5,5.5,'M.A.D. #1 / CALIBRATION',
           [dict(type='upgrade',mod=1)],
           question_pool(
               qv('Convierte 3/4″ a decimal.', '.75', ['.25','.5','.75']),
               qv('¿Qué decimal equivale a 5/8″?', '.625', ['.375','.625','.875'], 'equivalence'),
               qv('Convierte 1/8″ a decimal.', '.125', ['.125','.25','.5']),
           )),
        st('power_door_terminal','door',39.5,9.5,'MAIN POWER FUSE MISSING / ACCESS',
           [dict(type='door',id='power_door')],
           question_pool(
               qv('Convierte .375″ a fracción simplificada.', '3/8', ['1/4','3/8','1/2'], 'to_fraction', '.375″ equivale a 3/8″.'),
               qv('Convierte .625″ a fracción simplificada.', '5/8', ['3/8','5/8','7/8'], 'to_fraction', '.625″ equivale a 5/8″.'),
               qv('¿Qué fracción equivale a .25″?', '1/4', ['1/8','1/4','1/2'], 'to_fraction', '.25″ equivale a 1/4″.'),
           ),door_id='power_door'),
        st('secure_cache_01','cache',42.5,14.5,'SECURE CACHE / SHELLS',
           [dict(type='ammo',weapon='shotgun',amount=12),dict(type='secret',id='cache_found')],
           question_pool(
               qv('¿Qué decimal equivale a 5/8″?', '.625', ['.375','.625','.875'], 'equivalence'),
               qv('Convierte 7/8″ a decimal.', '.875', ['.625','.75','.875']),
               qv('En la fracción 3/8, ¿cuál es el denominador?', '8', ['3','8','16'], 'special', 'El denominador es el número inferior de la fracción: 8.'),
           ), reward_label='+12 cartuchos · Secreto encontrado'),
        st('mad_secret_01','mad',20.5,16.5,'M.A.D. #2 / SERVICE',
           [dict(type='upgrade',mod=1),dict(type='secret',id='service_found')],
           question_pool(
               qv('Convierte 7/8″ a decimal.', '.875', ['.625','.75','.875']),
               qv('¿Qué decimal equivale a 3/8″?', '.375', ['.125','.375','.625'], 'equivalence'),
               qv('En la fracción 5/8, ¿cuál es el denominador?', '8', ['5','8','16'], 'special', 'El denominador de 5/8 es 8.'),
           )),
        st('generator_socket','install',28.5,21.5,'INSTALL MAIN POWER FUSE',
           [dict(type='consume_item',item_id='main_power_fuse'),dict(type='objective',id='power_restored'),
            dict(type='ensure_ammo',minimum={'pistol':24,'shotgun':12})],
           prerequisites={'item':'main_power_fuse'}),
        st('elevator','exit',18.5,25.5,'EXIT ELEVATOR',[]),
    ]
    stations[2]['interaction_point'] = dict(x=39.5,y=10.5)
    def obj(i, rule=None): return dict(id=i,condition=rule or {})
    objectives = [
        obj('workshop_started',{'trigger':'welcome'}), obj('shotgun_collected',{'collected':'pump_shotgun'}),
        obj('assembly_cleared',{'all':[{'group_defeated':'assembly_first'},{'group_defeated':'assembly_second'}]}),
        obj('mad1_used',{'station_used':'mad_calibration_01'}),
        obj('main_power_fuse_collected',{'collected':'main_power_fuse'}),
        obj('fuse_ambush_triggered',{'trigger':'fuse_ambush'}),
        obj('fuse_ambush_cleared',{'group_defeated':'fuse_ambush'}), obj('power_restored'),
        obj('loader_spawned',{'wave':'loader'}), obj('loader_half_health_event',{'trigger':'loader_warning'}),
        obj('loader_defeated',{'group_defeated':'loader'}), obj('utcj_1_found',{'secret':'utcj_workshop'}),
        obj('elevator_unlocked',{'all':[{'objective':'power_restored'},{'objective':'loader_defeated'}]}),
        obj('workshop_complete',{'complete':True}),
    ]
    waves = [dict(id=g,groups=[g]) for g in ['welcome','assembly_first','assembly_second','maintenance','fuse_ambush','generator_entry','loader','loader_support']]
    def tr(i, rule, actions, **kw): return dict(id=i,condition=rule,actions=actions,**kw)
    def wave(g): return [dict(type='activate_wave',id=g)]
    triggers = [
        tr('welcome',{'zone':[5,1,10,9]},wave('welcome'),message='WORKSHOP 01 // Personal fuera de servicio'),
        tr('assembly_first',{'zone':[11,1,24,13]},wave('assembly_first'),message='ASSEMBLY FLOOR // Busca la Pump Shotgun'),
        tr('assembly_second',{'collected':'pump_shotgun'},wave('assembly_second'),message='REFUERZOS // Pump Shotgun disponible'),
        tr('maintenance',{'zone':[25,10,33,18]},wave('maintenance')),
        tr('fuse_ambush',{'collected':'main_power_fuse'},wave('fuse_ambush'),message='FUSE RECOVERED // Emboscada en Power Control'),
        tr('generator_entry',{'zone':[22,20,33,29]},wave('generator_entry')),
        tr('generator_supply',{'all':[{'zone':[22,20,33,29]},{'group_defeated':'generator_entry'}]},[dict(type='ensure_ammo',minimum={'pistol':24,'shotgun':12})],message='EMERGENCY SUPPLY // Munición mínima antes del Loader'),
        tr('loader',{'objective':'power_restored'},wave('loader'),message='POWER RESTORED // LOADER MK-I ONLINE'),
        tr('loader_warning',{'enemy_hp_below':{'id':'loader_mk1','ratio':.5}},[],message='ALERTA // Compuertas de servicio: refuerzos en 2 segundos',priority=10),
        tr('loader_support',{'all':[{'trigger':'loader_warning'},{'trigger_elapsed':{'id':'loader_warning','seconds':2}}]},wave('loader_support'),message='REFUERZOS // Crawlers en Generator Hall'),
        tr('elevator_unlock',{'objective':'elevator_unlocked'},[dict(type='door',id='elevator_gate')],message='POWER RESTORED // REACH THE ELEVATOR'),
    ]
    def cp(i, order, zone, x, y, pre):
        return dict(id=i,order=order,zone=zone,prerequisites=pre,respawn_position=dict(x=x,y=y),respawn_angle=0)
    return dict(id='workshop', revision=1, name='LEVEL 01 / THE WORKSHOP',grid=grid,
        enemy_types=types,encounters={'clasico':classic,'doom':doom},items=items,stations=stations,
        doors=[dict(id='power_door',cell=[39,9]),dict(id='elevator_gate',cell=[21,25])],
        checkpoints=[cp('reception',0,[1,1,5,8],3.5,5.5,{}),
            cp('calibration',1,[25,1,33,9],26.5,5.5,{'objective':'assembly_cleared'}),
            cp('fuse_recovered',2,[34,10,44,19],39.5,14.5,{'objective':'fuse_ambush_cleared'}),
            cp('before_loader',3,[22,20,33,29],28.5,20.5,{'all':[{'objective':'fuse_ambush_cleared'},{'group_defeated':'generator_entry'}]})],
        triggers=triggers,waves=waves,objectives=objectives,
        secrets=[dict(id='utcj_workshop',kind='utcj',on_shot=True,x=18.5,y=15.5),dict(id='cache_found',kind='cache'),dict(id='service_found',kind='cache')],
        exit=dict(station='elevator',condition={'objective':'elevator_unlocked'},auto_zone=[16,23,20.8,28]),
        initial_loadout={'pistol':dict(loaded=12,reserve=24,mods=0)},scale_resources=False,
        player_config=dict(max_hp=100,max_armor=100),respawn_rules=dict(min_hp=50,grace=2.5,ammo={'pistol':12,'shotgun':8}),
        zones=[dict(label=n,zone=[x1,y1,x2+1,y2+1]) for n,(x1,y1,x2,y2) in rooms],
        objective_hints=[
            dict(until='workshop_started',text='REPORT TO WORKSHOP 01 → ASSEMBLY'),
            dict(until='shotgun_collected',text='ASSEMBLY FLOOR → RECOGE LA ESCOPETA'),
            dict(until='assembly_cleared',text='DESPEJA ASSEMBLY → CALIBRATION / M.A.D.'),
            dict(until='main_power_fuse_collected',text='MAINTENANCE → POWER CONTROL / RECUPERA FUSIBLE'),
            dict(until='fuse_ambush_cleared',text='SOBREVIVE A LA EMBOSCADA DEL FUSIBLE'),
            dict(until='power_restored',text='GENERATOR HALL → INSTALL MAIN POWER FUSE'),
            dict(until='loader_defeated',text='DETIENE AL LOADER / ESQUIVA SU CARGA'),
            dict(until='workshop_complete',text='POWER RESTORED → REACH THE ELEVATOR')],
        intro='LEVEL 01 — THE WORKSHOP. Cruza Assembly Floor y recoge la escopeta. Calibration → Maintenance → Power Control: recupera el fusible y llévalo a Generator Hall. Restaura la energía, detén al Loader y alcanza el elevador. Las flechas del minimapa señalan el siguiente destino.',
        navigation=[dict(until='shotgun_collected',x=14.5,y=6.5),dict(until='assembly_cleared',x=20,y=6),dict(until='main_power_fuse_collected',x=39.5,y=10.5),dict(until='power_restored',x=28.5,y=21.5),dict(until='loader_defeated',x=28,y=26),dict(until='workshop_complete',x=18.5,y=25.5)],
        campaign_secrets=4,next_level='factory',
        teaser='PRODUCTION OUTPUT: 212%\nSHUTDOWN REQUEST: DENIED\nLEVEL 02 — THE FACTORY')
