import pyxel
from random import random, choice, uniform

WINDOW_WIDTH = 160
WINDOW_HEIGHT = 120

START = 0
PLAY = 1
GAMEOVER = 2

AIRCRAFT_WIDTH = 8
AIRCRAFT_HEIGHT = 8
AIRCRAFT_SPEED = 2

SHOT_WIDTH = 6
SHOT_HEIGHT = 1
SHOT_SPEED = 4
SHOT_COLOR = 8

BEAM_FRAMECOUNT = 30

ENEMY_WIDTH = 8
ENEMY_HEIGHT = 8
ENEMY_SPEED = 1.5
ENEMY_TYPE = [0, 1]

STAR_COOUNT = 100
STAR_COLOR_NEAR = 10
STAR_COLOR_FAR = 1

shot_list = []
enemy_list = []
star_list = []
beam_list = []


#リストに入れたインスタンスの描画、更新、削除
def draw_list(list):
    for elem in list:
        elem.draw()


def update_list(list, aircraft_pos):
    for elem in list:
        if type(elem) == Enemy:
            elem.update(aircraft_pos.y)
        elif type(elem) == Beam:
            elem.update(aircraft_pos)
        else:
            elem.update()


def clean_list(list):
    for i, elem in enumerate(list):
        if not elem.stat:
            list.pop(i)


#座標
class Vec2:
    def __init__(self, x, y):
        self.x = x
        self.y = y


#機体
class Aircraft:
    def __init__(self, x, y):
        self.w = AIRCRAFT_WIDTH
        self.h = AIRCRAFT_HEIGHT
        self.pos = Vec2(x, y)
        self.stat = True
        self.beam_exist = False

    def update(self):
        #プレーヤーのコントロール
        if pyxel.btn(pyxel.KEY_A):
            self.pos.x -= AIRCRAFT_SPEED

        if pyxel.btn(pyxel.KEY_D):
            self.pos.x += AIRCRAFT_SPEED

        if pyxel.btn(pyxel.KEY_W):
            self.pos.y -= AIRCRAFT_SPEED

        if pyxel.btn(pyxel.KEY_S):
            self.pos.y += AIRCRAFT_SPEED

        #画面外に行かない為の処理
        self.pos.x = max(self.pos.x, 0)
        self.pos.x = min(self.pos.x, pyxel.width - self.w)
        self.pos.y = max(self.pos.y, 0)
        self.pos.y = min(self.pos.y, pyxel.height - self.h)

        #スペースキーで弾を打つ
        if pyxel.btnp(pyxel.KEY_SPACE):
            Shot(self.pos.x + 4, self.pos.y + 6)  #砲台から出るように微調整
            pyxel.play(0, 0)

        #bでビーム
        if pyxel.btnp(pyxel.KEY_B):
            Beam(self.pos.x + 6, self.pos.y + 6)
            pyxel.play(0, 0)

    def draw(self):
        #機体の描画
        pyxel.blt(self.pos.x, self.pos.y, 0, 0, 0, self.w, self.h, 0)


#シュート
class Shot:
    def __init__(self, x, y):
        self.pos = Vec2(x, y)
        self.w = SHOT_WIDTH
        self.h = SHOT_HEIGHT
        self.stat = True

        shot_list.append(self)

    def update(self):
        self.pos.x += SHOT_SPEED

        #画面外でステータスをFalse
        if self.pos.x > pyxel.width + 1:
            self.stat = False

    def draw(self):
        pyxel.rect(self.pos.x, self.pos.y, self.w, self.h, SHOT_COLOR)

#ビーム
class Beam:
    def __init__(self, x, y):
        self.pos = Vec2(x, y)
        self.w = pyxel.width - self.pos.x
        self.h = SHOT_HEIGHT
        self.stat = True
        self.beam_framecount = pyxel.frame_count

        beam_list.append(self)

    #設定したframecount秒間ビームを打ったら消す
    def update(self, pos):
        self.pos.x = pos.x + 6
        self.pos.y = pos.y + 6
        self.w = pyxel.width - self.pos.x
        if pyxel.frame_count - self.beam_framecount == BEAM_FRAMECOUNT:
            self.stat = False

    def draw(self):
        pyxel.rect(self.pos.x, self.pos.y, self.w, self.h, SHOT_COLOR + 1)


#敵
class Enemy:
    def __init__(self, x, y):
        self.pos = Vec2(x, y)
        self.w = ENEMY_WIDTH
        self.h = ENEMY_HEIGHT
        self.stat = True
        self.type = choice(ENEMY_TYPE)
        self.Kp = uniform(0, 0.25)

        enemy_list.append(self)

    def update(self, aircraft_y):
        #type0の敵はジグザグに動く
        if self.type == 0:
            if (pyxel.frame_count) % 60 < 30:
                self.pos.y += ENEMY_SPEED
            else:
                self.pos.y -= ENEMY_SPEED

        #type1の敵は機体を追尾するように動く
        if self.type == 1:
            dy = aircraft_y - self.pos.y
            self.pos.y += self.Kp * dy

        #x方向は直進
        self.pos.x -= ENEMY_SPEED

        #画面外で死亡
        if self.pos.x < -ENEMY_WIDTH:
            self.alive = False

    def draw(self):
        if self.type == 0:
            pyxel.blt(self.pos.x, self.pos.y, 0, 8, 0, self.w, self.h, 0)
        elif self.type == 1:
            pyxel.blt(self.pos.x, self.pos.y, 0, 16, 0, self.w, self.h, 0)


class Space:
    def __init__(self):
        self.star_list = []
        for i in range(STAR_COOUNT):
            self.star_list.append(
                (random() * pyxel.width, random() * pyxel.height,
                 random() * 1.5 + 1))

    def update(self):
        for i, (x, y, speed) in enumerate(self.star_list):
            x -= speed
            if x <= 0:
                x += pyxel.width
            self.star_list[i] = (x, y, speed)

    def draw(self):
        for (x, y, speed) in self.star_list:
            pyxel.pset(x, y, STAR_COLOR_FAR if speed > 2 else STAR_COLOR_NEAR)


#当たり判定 enemyに対してobj(弾や機体)の当たり判定を処理する
def col_ditect(obj, enemy):

    if (enemy.pos.x < obj.pos.x + obj.w and obj.pos.x < enemy.pos.x + enemy.w
            and enemy.pos.y < obj.pos.y + obj.h
            and obj.pos.y < enemy.pos.y + enemy.h):
        obj.stat = False
        enemy.stat = False

        return 10


def col_ditect_beam(beam, enemy):
    add_score = 0

    if enemy.stat == True:
        if (enemy.pos.x < beam.pos.x + beam.w
                and beam.pos.x < enemy.pos.x + enemy.w
                and enemy.pos.y < beam.pos.y + beam.h
                and beam.pos.y < enemy.pos.y + enemy.h):
            enemy.stat = False
            add_score += 10
            pyxel.play(1, 1)
    return add_score


class App:
    def __init__(self):
        pyxel.init(WINDOW_WIDTH, WINDOW_HEIGHT, caption="My_Shooting_Game")
        pyxel.load("assets/my_shooting_game.pyxres")
        pyxel.sound(0).set("a2a2c2c2", "p", "7", "s", 5)
        pyxel.sound(1).set("a2a2c2c2", "n", "7624", "s", 10)

        self.scene = START
        self.score = 0  # GAMESCORE
        self.aircraft = Aircraft(pyxel.width / 10, pyxel.height / 2)  #機体初期位置
        self.background = Space()

        pyxel.run(self.update, self.draw)

    def update(self):
        if pyxel.btnp(pyxel.KEY_Q):
            pyxel.quit()

        self.update_scene(self.scene)
        self.background.update()

    def update_scene(self, scene):
        if scene == START:
            if pyxel.btnp(pyxel.KEY_SPACE):
                self.scene = PLAY

        elif scene == PLAY:
            #敵の座標を与える
            if pyxel.frame_count % 6 == 0:
                Enemy(pyxel.width, random() * pyxel.height)

            #敵と弾の衝突を処理
            for shot in shot_list:
                for enemy in enemy_list:
                    col_ditect(shot, enemy)
                    if (shot.stat or enemy.stat) is False:
                        self.score += 10
                        pyxel.play(1, 1)

            for beam in beam_list:
                for enemy in enemy_list:
                    self.score += col_ditect_beam(beam, enemy)

            #敵と機体の衝突を処理
            for enemy in enemy_list:
                col_ditect(self.aircraft, enemy)
                if self.aircraft.stat is False:
                    self.scene = GAMEOVER

            self.aircraft.update()

            update_list(shot_list, self.aircraft.pos)
            update_list(enemy_list, self.aircraft.pos)
            update_list(beam_list, self.aircraft.pos)

            clean_list(shot_list)
            clean_list(enemy_list)
            clean_list(beam_list)

        elif scene == GAMEOVER:
            if pyxel.btnp(pyxel.KEY_SPACE):
                self.scene = PLAY
                self.score = 0  # GAMESCORE
                self.aircraft = Aircraft(pyxel.width / 10,
                                         pyxel.height / 2)  #機体初期位置

                enemy_list.clear()
                shot_list.clear()
                beam_list.clear()

    def draw(self):
        pyxel.cls(0)

        self.draw_scene(self.scene)
        self.background.draw()

    def draw_scene(self, scene):
        if scene == START:
            pyxel.text(38, 50, 'PRESS SPACE TO START!', pyxel.frame_count % 16)
        elif scene == PLAY:
            self.aircraft.draw()
            draw_list(enemy_list)
            draw_list(shot_list)
            draw_list(beam_list)

            pyxel.text(5, 5, 'score:{}'.format(self.score), 5)
        elif scene == GAMEOVER:
            #pyxel.text(pyxel.width / 2, 10, 'l', 8)
            pyxel.text(64, 40, 'GAMEOVER!', pyxel.frame_count % 16)
            pyxel.text(36, 50, 'PRESS SPACE TO RESTART!',
                       pyxel.frame_count % 16)


App()
