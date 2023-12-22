from pathlib import Path

from pynecraft.base import EQ, r, SOUTH, NORTH
from pynecraft.commands import scoreboard, execute, e, Score, MINUS, JsonText, function, clone, tp, s, kill
from pynecraft.enums import ScoreCriteria
from pynecraft.function import DataPack, Function
from pynecraft.simpler import VILLAGER_PROFESSIONS, WallSign

pack = DataPack('megavillage')
f = pack.functions

abbrs = {'Leatherworker': 'LeatherWrkr'}

do_count_f = pack.function_set.add(Function('do_counts'))
count_f = pack.function_set.add(Function('counts').add(
    execute().at(e().tag('accountant')).run(function(do_count_f))))


def sign_line(score):
    name = score.target.name
    if name in abbrs:
        name = abbrs[name]
    return JsonText.text(f'{name}: ').extra(JsonText.score(score))


def sign(lines, pos, dir):
    return WallSign(lines, (function(count_f),)).back(lines).wax(True).place(pos, dir),


total = Score('Total', 'megavillage')
adults = Score('Adults', 'megavillage')
kids = Score('Kids', 'megavillage')
villager = e().type('villager').distance((0, 100))
do_count_f.add(
    scoreboard().objectives().add(total.objective, ScoreCriteria.DUMMY),
    scoreboard().players().set(total, 0),
    execute().as_(villager).run(scoreboard().players().add(total, 1)),
    scoreboard().players().set(adults, 0),
    execute().as_(villager.nbt({'Age': 0})).run(scoreboard().players().add(adults, 1)),
    scoreboard().players().operation(kids, EQ, total),
    scoreboard().players().operation(kids, MINUS, adults),

    sign((None, sign_line(total)), r(-1, 5, -3), SOUTH),
    sign((None, sign_line(adults), sign_line(kids)), r(0, 5, -3), SOUTH),
)
lines = []
x = 1
for pro in VILLAGER_PROFESSIONS:
    score = Score(pro, 'megavillage')
    do_count_f.add(
        scoreboard().players().set(score, 0),
        execute().as_(villager.nbt({'Age': 0, 'VillagerData': {'profession': f'minecraft:{pro.lower()}'}})).run(
            scoreboard().players().add(score, 1))
    )
    lines.append(sign_line(score))
    last = pro == VILLAGER_PROFESSIONS[-1]
    if len(lines) == 4 or last:
        if last:
            lines.append(sign_line(kids))
        do_count_f.add(sign(lines, r(x, 5, 2), NORTH))
        x -= 1
        lines = []
for i in range(1, 8):
    do_count_f.add(clone(r(1, 5, 2), r(-2, 5, -3), r(-2, 5 + i * 4, -3)).filtered('oak_wall_sign'))

pack.function_set.add(Function('none').add(
    tp(s(), villager.limit(1).nbt({'Age': 0, 'VillagerData': {'profession': 'minecraft:none'}}))
))
pack.function_set.add(Function('rescue').add(
    tp(villager.nbt({'Age': 0, 'VillagerData': {'profession': 'minecraft:none'}}), s())
))
pack.function_set.add(Function('purge').add(
    kill(villager.nbt({'Age': 0, 'VillagerData': {'profession': 'minecraft:none'}}))
))

dir = f'{Path.home()}/clarity/home/saves/New World'
print(dir)
pack.save(dir)
