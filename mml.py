# =================================================
import FoxDot as fd

def parse_int(s):
    '''
    Args
        s (str)
    Returns
        val (int): the number read from s
        offs (int): number of letters read from s
    '''
    val, offs = 0, 0
    try:
        for offs in range(len(s)):
            val = int(s[:1+offs])
        offs = len(s)
    except:
        pass
    return val, offs


macro_dict = {}
def generate_chord_macro():
    chromatic_scale = ['c','c+','d','d+','e','f','f+','g','g+','a','a+','b']
    major_pitch = [0,2,4,5,7,9,11]
    for i,base in enumerate('CDEFGAB'):
        for j,sign in enumerate(['-', '', '+']):
            base_pitch = major_pitch[i] + j + 11

            chord_info = [
                ('', [0, 4, 7]), # Major
                ('P', [0, 7, 16]), # Major (distributed)
                ('m', [0, 3, 7]), # minor
                ('mP', [0, 7, 15]), # minor (distributed)
                ('6', [0, 4, 7, 9]),
                ('m6', [0, 3, 7, 9]),
                ('7', [0, 4, 7, 10]),
                ('37', [0, 4, 10]),
                ('57', [0, 7, 10]),
                ('M7', [0, 4, 7, 11]),
                ('M57', [0, 7, 11]),
                ('m7', [0, 3, 7, 10]),
                ('m57', [0, 7, 10]),
                ('dim', [0, 3, 6]),
                ('aug', [0, 4, 8]),
                ('sus4', [0, 5, 7]),
            ]
            for chord_symbol, chord_pitch in chord_info:
                for l in range(len(chord_pitch)): # number of rotation
                    name = base + sign + chord_symbol + '^' * l                
                    chord_string = '"' + ''.join([
                        chromatic_scale[(base_pitch + p)%12] for p in chord_pitch[l:]+chord_pitch[:l]
                    ]) + '"'
                    macro_dict[name] = chord_string

generate_chord_macro()


def extend_macro(mml):
    ret = ''
    offs = 0
    while offs < len(mml):
        c = mml[offs]
        if 'A' <= c <= 'Z':
            accepted_offs = offs+1
            for offs2 in range(offs+1, len(mml)+1):
                if mml[offs2-1] == ' ': break # name of macro must not contain space.
                if mml[offs:offs2] in macro_dict:
                    c = macro_dict[mml[offs:offs2]]
                    accepted_offs = offs2
            offs = accepted_offs
            ret += c
            continue
        ret += c
        offs += 1
    return ret

def extend_chord(mml):
    return mml
    # TODO
    ret = ''
    offs = 0
    while offs < len(mml):
        c = mml[offs]
        n = 'CDEFGAB'.find(c)
        if n >= 0:
            n = [0,2,4,5,7,9,11][n]
            if mml[offs+1] == 'b': n -= 1
            if mml[offs+1] == '#': n += 1
        ret += c
        offs += 1
    return ret

def read_mml(mml):
    mml = extend_chord(mml)
    mml = extend_macro(mml)
    print('macro extended: {}'.format(mml))
    pitch_list, dur_list = [], []
    val_l = 4
    val_o = 4
    offs = 0
    futen = 0
    chord = []
    in_chord = False
    while offs < len(mml):
        c = mml[offs]
        if c == 'l' and not in_chord:
            offs += 1
            val_l, delta_offs = parse_int(mml[offs:])
            offs += delta_offs
            continue
        if c == 'o':
            offs += 1
            val, delta_offs = parse_int(mml[offs:])
            if in_chord:
                chord_val_o = val
            else:
                val_o = val
            offs += delta_offs
            continue
        n = 'cdefgabr'.find(c)
        if n >= 0: # new note!
            if futen > 0:
                dur_list[-1] *= 2 - 0.5**futen; futen = 0 # clear futen
            if in_chord:
                chord.append([0,2,4,5,7,9,11,0][n] + (chord_val_o-4)*12)
                if len(chord) > 1 and chord[-2] >= chord[-1]:
                    chord[-1] = 12 - (chord[-2] - chord[-1]) % 12 + chord[-2]
            else:
                pitch_list.append([0,2,4,5,7,9,11,0][n] + (val_o-4)*12)
                dur_list.append(4/val_l if n<7 else fd.rest(4/val_l))
            offs += 1
            continue
        if c in ['"', "'"]:
            if in_chord: # end of chord
                pitch_list.append(tuple(chord))
                in_chord = False
                chord = []
                dur_list.append(4/val_l)
                offs += 1
                continue
            else: # start of chord
                in_chord = True
                chord_val_o = val_o
                offs += 1
                continue                
        if '0' <= c <= '9' and not in_chord: # temporary l-setting
            l, delta_offs = parse_int(mml[offs:])
            dur_list[-1] = fd.rest(4/l) if isinstance(dur_list[-1], fd.lib.Players.rest) else 4/l
            offs += delta_offs
            continue
        # other commands
        if c == '+':
            if in_chord:
                chord[-1] += 1
            else:
                pitch_list[-1] += 1
        elif c == '-':
            if in_chord:
                chord[-1] -= 1
            else:
                pitch_list[-1] -= 1
        elif c == '>':
            if in_chord:
                chord_val_o += 1
            else:
                val_o += 1
        elif c == '<':
            if in_chord:
                chord_val_o -= 1
            else:
                val_o -= 1
        elif c == '.':
            futen += 1
        offs += 1
    # end of mml
    if futen > 0:
        dur_list[-1] *= 2 - 0.5**futen; futen = 0 # clear futen
    return pitch_list, dur_list

def play_mml(obj, mml, synth=fd.saw, **kwargs):
    pitch_list, dur_list = read_mml(mml)
    obj >> synth(pitch_list, dur=dur_list, scale=fd.Scale.chromatic, **kwargs)

def def_macro(key, value):
    if ' ' in key:
        raise ValueError('Macro keys must not contain spaces.')
    macro_dict[key] = value
    # いずれもう少し便利なインタフェースにしたい

# =================================================


if __name__ == '__main__':
    print(read_mml('l4 C C < G^ G^ > Am^ Am^ F^^ F^^'))

    print(macro_dict)

