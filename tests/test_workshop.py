"""Workshop rules and gates. No frontend authority is assumed for progression."""
import copy
import itertools
from collections import deque, Counter
from fractions import Fraction
import re
import pytest
from game.engine import GameEngine
from game.nivel import level_config
from game.world import condition, advance, pickup, solid, entity
from game.save_system import load_save, validate_state, SaveError, SAVE_VERSION
from game.preguntas import generate_question

IDS=itertools.count()
def call(e, action, **data):
    r=e.handle(dict(id=f'w{next(IDS)}',action=action,data=data))
    assert 'error' not in r,r
    return r

def new(diff='clasico'):
    e=GameEngine();call(e,'new',name='Workshop Test',difficulty=diff,level_id='workshop');return e

def solve(e, ident, weapon='pistol', answer=None):
    station=entity(e.level(),'stations',ident)
    e.state['player'].update(station['interaction_point'])
    call(e,'question',station=ident,weapon=weapon)
    return call(e,'answer',question_id=e.question.id,answer=answer or e.question.answer)

def defeat(e, *groups):
    for enemy in e.state['enemies']:
        if enemy['group'] in groups: enemy.update(active=True,hp=0)
    e.state=advance(e.state,e.level())

def collect(e, ident):
    pickup(e.state,entity(e.level(),'items',ident),e.level());e.state['collected'].append(ident)
    e.state=advance(e.state,e.level())

@pytest.mark.parametrize('diff,count',[('clasico',21),('doom',30)])
def test_initial_schema_and_composition(diff,count):
    e=new(diff);s=e.state;l=e.level()
    assert s['level_id']=='workshop' and s['checkpoint']=='reception'
    assert s['weapons']['pistol']==dict(loaded=12,reserve=24,mods=0)
    assert len(s['enemies'])==count and not any(x['active'] for x in s['enemies'])
    assert l['enemy_types']['loader']['hp']==250
    assert validate_state(s)==s
    for cp in l['checkpoints']:
        p=cp['respawn_position'];assert not solid(l,s['progress'],p['x'],p['y'])

@pytest.mark.parametrize('diff',['clasico','doom'])
def test_math_pool_and_formats(diff):
    l=level_config(diff,'workshop');count=0
    for st in l['stations']:
        if st['kind'] in ('exit','install'):continue
        count+=1
        q=generate_question(diff,rules=st['question'])
        assert q.check(q.answer)
        assert set(map(int,re.findall(r'/\s*(\d+)',q.prompt+' '+q.answer+' '+' '.join(q.choices)))) <= {2,4,8}
        assert q.mode==('manual' if diff=='doom' and st['kind'] in ('mad','cache') else 'choice')
        if q.category=='to_decimal':assert not q.check(re.search(r'\d+/\d+',q.prompt)[0])
        else:assert not q.check('0.375') and not q.check('6/16')
    assert count==5

@pytest.mark.parametrize('diff',['clasico','doom'])
def test_gates_and_essential_reachability(diff):
    e=new(diff);l=e.level();p=e.state['progress']
    def flood():
        start=(3,5);seen={start};q=deque([start])
        while q:
            x,y=q.popleft()
            for a,b in [(x+1,y),(x-1,y),(x,y+1),(x,y-1)]:
                if (a,b) not in seen and not solid(l,p,a+.5,b+.5):seen.add((a,b));q.append((a,b))
        return seen
    seen=flood()
    assert (39,4) not in seen and (18,25) not in seen
    for st in l['stations']:
        if st['kind']=='exit':continue
        pos=st['interaction_point'];assert (int(pos['x']),int(pos['y'])) in seen,st['id']
    p['doors']['power_door']=True;seen=flood();assert (39,4) in seen and (18,25) not in seen
    p['doors']['elevator_gate']=True;assert (18,25) in flood()
    for cp in l['checkpoints']:
        pos=cp['respawn_position'];assert (int(pos['x']),int(pos['y'])) in seen
    for x in l['enemies']+l['items']:
        assert not solid(l,p,x['x'],x['y']),x['id']

@pytest.mark.parametrize('diff',['clasico','doom'])
def test_campaign_fuse_wave_power_boss_save_exit(diff):
    e=new(diff)
    collect(e,'pump_shotgun');assert e.state['weapons']['shotgun']['reserve']==12
    defeat(e,'welcome','assembly_first','assembly_second','maintenance')
    solve(e,'power_door_terminal');collect(e,'main_power_fuse')
    assert e.state['inventory']['quest_items']['main_power_fuse']==1
    assert e.state['progress']['waves']['fuse_ambush']
    defeat(e,'fuse_ambush','generator_entry')
    call(e,'sync');loaded,cp=load_save(e.pack()['save']);assert loaded['inventory']['quest_items']['main_power_fuse']==1
    e.state=loaded
    assert all(x['hp']==0 for x in e.state['enemies'] if x['group']=='fuse_ambush')
    assert not e.state['progress']['doors']['elevator_gate']
    e.state['player'].update(x=28.5,y=21.5)
    e.state['weapons']['pistol'].update(loaded=0,reserve=0)
    e.state['weapons']['shotgun'].update(loaded=0,reserve=0)
    call(e,'interact',station='generator_socket')
    assert e.state['inventory']['quest_items']['main_power_fuse']==0
    assert e.state['progress']['objectives']['power_restored']
    assert sum(e.state['weapons']['shotgun'][k] for k in ('loaded','reserve'))>=12
    loader=next(x for x in e.state['enemies'] if x['type']=='loader');assert loader['active']
    loader['hp']=125;e.state=advance(e.state,e.level())
    assert e.state['progress']['triggers']['loader_warning']
    assert not e.state['progress']['waves']['loader_support']
    e.state['stats']['seconds']+=1.9;e.state=advance(e.state,e.level());assert not e.state['progress']['waves']['loader_support']
    e.state['stats']['seconds']+=.2;e.state=advance(e.state,e.level());assert e.state['progress']['waves']['loader_support']
    defeat(e,'loader_support');e.state=advance(e.state,e.level())
    assert all(x['hp']==0 for x in e.state['enemies'] if x['group']=='loader_support')
    defeat(e,'loader');assert e.state['progress']['doors']['elevator_gate']
    e.state['player'].update(x=18.5,y=25.5);call(e,'finish')
    assert e.state['progress']['objectives']['workshop_complete']
    state,_=load_save(e.pack()['save']);assert state['progress']==e.state['progress']
    assert e.pack()['stats']['utcj_display']=='???'


def test_loader_dead_alone_does_not_unlock():
    e=new();defeat(e,'loader');assert not e.state['progress']['doors']['elevator_gate']


def test_two_mads_no_compatible_atomic_retry():
    e=new();r=solve(e,'mad_calibration_01',answer='.50');assert not r['correct']
    assert not e.state['progress']['stations']['mad_calibration_01']
    solve(e,'mad_calibration_01')
    e.state['player'].update(x=20.5,y=16.5)
    before=copy.deepcopy(e.state)
    r=e.handle(dict(id='no-compatible',action='question',data=dict(station='mad_secret_01',weapon='pistol')))
    assert 'error' in r and e.state==before
    collect(e,'pump_shotgun');solve(e,'mad_secret_01','shotgun')
    assert all(a['mods']==1 for a in e.state['weapons'].values())
    assert e.state['progress']['stations']['mad_calibration_01'] and e.state['progress']['stations']['mad_secret_01']


def test_unsafe_station_and_dead_checkpoint():
    e=new();enemy=e.state['enemies'][0];enemy.update(active=True,x=27,y=5,hp=60)
    e.state['player'].update(x=27.5,y=5.5)
    r=e.handle(dict(id='unsafe',action='question',data=dict(station='mad_calibration_01')))
    assert r['error']=='AREA NOT SECURE'
    defeat(e,'welcome','assembly_first','assembly_second');e.state['player']['hp']=0
    r=e.handle(dict(id='dead-cp',action='checkpoint',data=dict(checkpoint='calibration')))
    assert 'error' in r and e.state['checkpoint']=='reception'


def test_utcj_secret_no_kill_and_save_respawn():
    e=new();e.state['player'].update(x=20.5,y=15.5)
    snap=copy.deepcopy(e.state);snap['secret_hits']=['utcj_workshop'];call(e,'sync',snapshot=snap)
    assert e.state['stats']['kills']==0 and e.pack()['stats']['utcj_display']=='1/4'
    defeat(e,'assembly_first','assembly_second');e.state['player'].update(x=26.5,y=5.5)
    call(e,'checkpoint',checkpoint='calibration')
    e.state['player']['hp']=0;call(e,'restart')
    assert e.state['player']['hp']>=50 and e.state['player']['grace']>0
    assert e.state['progress']['utcj_found']==['utcj_workshop']
    assert load_save(e.pack()['save'])[0]['progress']['utcj_found']==['utcj_workshop']


def test_old_v2_still_loads_and_v1_rejected():
    e=GameEngine();call(e,'new',name='Legacy',difficulty='clasico')
    old=e.pack()['save'];assert old['version']==SAVE_VERSION
    assert 'trigger_times' not in old['state']['progress']
    assert load_save(old)[0]['level_id']=='industrial_test'
    legacy=copy.deepcopy(old);legacy['version']=2
    legacy['state'].pop('campaign',None);legacy['checkpoint_state'].pop('campaign',None)
    assert load_save(legacy)[0]['campaign']['current_level']=='industrial_test'
    legacy['version']=1
    with pytest.raises(SaveError):load_save(legacy)


def test_install_requires_fuse_and_is_not_math():
    e=new();e.state['player'].update(x=28.5,y=21.5)
    before=copy.deepcopy(e.state)
    r=e.handle(dict(id='no-fuse',action='interact',data=dict(station='generator_socket')))
    assert 'error' in r and e.state==before
    r=e.handle(dict(id='bad-question',action='question',data=dict(station='generator_socket')))
    assert 'error' in r


def test_generator_supply_is_one_time_and_before_loader():
    e=new();collect(e,'pump_shotgun');defeat(e,'generator_entry')
    for a in e.state['weapons'].values():a.update(loaded=0,reserve=0)
    e.state['player'].update(x=28.5,y=20.5);e.state=advance(e.state,e.level())
    assert e.state['progress']['triggers']['generator_supply']
    assert e.state['weapons']['pistol']['reserve']==24
    assert e.state['weapons']['shotgun']['reserve']==12
    assert not e.state['progress']['objectives']['loader_spawned']
    e.state['weapons']['shotgun']['reserve']=0;e.state=advance(e.state,e.level())
    assert e.state['weapons']['shotgun']['reserve']==0


@pytest.mark.parametrize('phase',['preparing','charging','blocked','slamming','recovering'])
def test_loader_phase_and_warning_timestamp_survive_save(phase):
    e=new();e.state['progress']['objectives']['power_restored']=True;e.state=advance(e.state,e.level())
    loader=next(x for x in e.state['enemies'] if x['type']=='loader')
    loader.update(hp=120,charge_state=phase,phase_time=.7,attack_index=3,cooldown=.6,stun_time=1.75 if phase=='blocked' else 0)
    e.state['stats']['seconds']=20;e.state=advance(e.state,e.level());stamp=e.state['progress']['trigger_times']['loader_warning']
    e.state,_=load_save(e.pack()['save']);e.state['stats']['seconds']=21;e.state=advance(e.state,e.level())
    assert e.state['progress']['trigger_times']['loader_warning']==stamp
    assert not e.state['progress']['waves']['loader_support']
    loader=next(x for x in e.state['enemies'] if x['type']=='loader')
    assert loader['charge_state']==phase and loader['phase_time']==.7


def test_delayed_sync_cannot_skip_half_health_event():
    e=new();e.state['progress']['objectives']['power_restored']=True;e.state=advance(e.state,e.level())
    # Network latency can put multiple hits (including the killing hit) in one sync.
    snap=copy.deepcopy(e.state);next(x for x in snap['enemies'] if x['type']=='loader')['hp']=0
    call(e,'sync',snapshot=snap)
    assert e.state['progress']['triggers']['loader_warning']
    assert not e.state['progress']['waves']['loader_support']
    e.state['stats']['seconds']+=2.1;e.state=advance(e.state,e.level())
    assert e.state['progress']['waves']['loader_support']
