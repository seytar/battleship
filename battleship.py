#!/usr/bin/python3.5
import random
import re

# Must be True for debug
print('\nFor DEBUG use D key on keyboard. Shows randomly assigned ship positions.\n')
_DEBUG = False

# Ship Data
SHIPS = {
    'A': {
        'lang': 'Admiral cruiser ship',
        'data': ['A'] * 5,
        'damage': 0,
        'count': 1
    },
    'M': {
        'lang': 'Destroyer',
        'data': ['M'] * 4,
        'damage': 0,
        'count': 1
    },
    'F': {
        'lang': 'Frigate',
        'data': ['F'] * 3,
        'damage': 0,
        'count': 1
    },
    'D': {
        'lang': 'Submarine',
        'data': ['D'] * 2,
        'damage': 0,
        'count': 1
    },
    'W': {
        'lang': 'Minelayer',
        'data': ['W'],
        'damage': 0,
        'count': 1
    }
}

# Action langs
LANG_ACTION_SANK = 'sank'
LANG_ACTION_WOUNDED = 'wounded'
LANG_REPORT_SANK = 'submerged'
LANG_REPORT_WOUNDED = 'wounded'

# Board Dimensions
BOARD_COLUMN_LENGTH = 10
BOARD_ROW_LENGTH = 10

# Slot chars on board
SLOT_EMPTY = 'O'
SLOT_EMPTY_SHIPS = '.'
SLOT_MISS = 'X'
SLOT_SUCCESS = '*'

# Create board coordinates via given dimensions
BOARD_COORDS = [[SLOT_EMPTY] * BOARD_COLUMN_LENGTH for i in range(BOARD_ROW_LENGTH)]

# A copy of the board coordinates is being created to hold the areas where the ships will be placed
SHIPS_COORDS = [[SLOT_EMPTY_SHIPS] * BOARD_COLUMN_LENGTH for i in range(BOARD_ROW_LENGTH)]

# Column names
BOARD_COLUMN_COORD_NAMES = [chr(chrCode) for chrCode in range(65, BOARD_COLUMN_LENGTH + 65)]

# Row names
BOARD_ROW_COORD_NAMES = [(rowNumber + 1) for rowNumber in range(0, BOARD_ROW_LENGTH)]


def print_board(board_data):
    print('   {}'.format(' '.join([colName for colName in BOARD_COLUMN_COORD_NAMES])))

    for index, row in enumerate(board_data):
        print(('{:2d} {}'.format(BOARD_ROW_COORD_NAMES[index], ' '.join(row))))


def random_place_ship(ship):
    # Find ship length
    ship_length = len(ship)

    # Find restrictions
    ship_last_start_coord = BOARD_COLUMN_LENGTH - ship_length

    # Random x coordinate
    x = random.randint(0, ship_last_start_coord)

    # Random y coordinate
    y = random.randint(0, BOARD_ROW_LENGTH - 1)

    # If any of the coordinates have already been filled, re-do the coordinate calculation
    for i in range(ship_length):
        if SHIPS_COORDS[y][x + i] != SLOT_EMPTY_SHIPS:
            random_place_ship(ship)
            return

    for i in range(ship_length):
        SHIPS_COORDS[y][x + i] = ship[i]


def random_place_ships():
    for ship in SHIPS.values():
        # Number of ship are taken into account
        for n in range(ship['count']):
            random_place_ship(ship['data'])


def get_user_coords(guess):
    min_x_coord = 1
    max_x_coord = BOARD_ROW_LENGTH
    min_y_coord = 65
    max_y_coord = BOARD_COLUMN_LENGTH + 65 - 1

    coords = [x for x in re.split('(\d+)', guess) if x]

    if len(coords) != 2:
        print('Enter the coordinates in two blocks. Example: 10J')
        return False
    elif coords[0].isdigit() is False:
        print('The first character of the coordinates must be numeric. Example: 1A')
        return False
    elif (min_x_coord <= int(coords[0]) <= max_x_coord) is False or (min_y_coord <= ord(coords[1].capitalize()) <= max_y_coord) is False:
        print('Error: the number must between ' + str(min_x_coord) + ' and ' + str(max_x_coord) + \
              ', and the char must between ' + chr(min_y_coord) + ' and ' + chr(max_y_coord) + \
              ' Try again.')
        return False
    else:
        x_index = int(coords[0]) - 1
        y_index = ord(coords[1].capitalize()) - 65
        return [x_index, y_index]


def _print_board_debug(ships_coords):
    if _DEBUG:
        print_board(ships_coords)
        print()


def report(index):
    print('\nYou did ' + str(index) + ' shot tests:\n')
    for ship in SHIPS.values():
        lang_state = ''
        if ship['damage'] == len(ship['data']):
            lang_state = LANG_REPORT_SANK
        elif ship['damage'] > 0:
            lang_state = LANG_REPORT_WOUNDED

        print('  {} {} ({} fields)[{}] {}'.format(
            ship['count'],
            ship['lang'],
            len(ship['data']),
            ('+' * (len(ship['data']) - ship['damage'])) + ('-' * ship['damage']),
            lang_state)
        )


def finished(index):
    for ship in SHIPS.values():
        if ship['damage'] != len(ship['data']):
            return False

    print('\nCongratulations! You sink the entire navy after ' + str(index) + ' shots.\n')
    return True


def start():
    # Shows ship positions on debug environment.
    _print_board_debug(SHIPS_COORDS)

    # Print board
    print_board(BOARD_COORDS)
    print()


# Ships are randomly placed
random_place_ships()
start()

# User estimates and results are being retained
USER_DATA = {}
index = 0
is_finished = False
while True:
    print('==============================')
    if is_finished:
        lang_q = 'Game over. Use R for report, Q for Quit: '
    else:
        lang_q = str(index + 1) + '. enter your estimate: '

    guess = input(lang_q).strip().upper()

    if guess == 'R':
        report(index)
    elif guess == 'Q':
        exit()
    elif guess == 'D':
        _DEBUG = False if _DEBUG else True
        start()
    elif is_finished is False:
        # Coordinates entered by the user are checked against the board
        coords = get_user_coords(guess)
        if coords:
            # Did the user make this prediction in advance?
            check_coords = USER_DATA.get(guess)
            if check_coords:
                print('\n  [' + guess + '] It was shot earlier. Try again.\n')
            else:
                _print_board_debug(SHIPS_COORDS)

                if is_finished is False:
                    index = index + 1

                USER_DATA[guess] = {'coords': coords}

                # Ship damage control
                ship_key = SHIPS_COORDS[coords[0]][coords[1]]
                if ship_key == SLOT_EMPTY_SHIPS:
                    BOARD_COORDS[coords[0]][coords[1]] = SLOT_MISS
                    print('\n  [' + guess + '] Miss\n')
                else:
                    BOARD_COORDS[coords[0]][coords[1]] = SLOT_SUCCESS
                    SHIPS[ship_key]['damage'] += 1

                    lang_action = LANG_ACTION_WOUNDED

                    if SHIPS[ship_key]['damage'] == len(SHIPS[ship_key]['data']):
                        lang_action = LANG_ACTION_SANK

                    print('\n  [' + guess + '] {} {}\n'.format(SHIPS[ship_key]['lang'], lang_action))

                USER_DATA[guess]['state'] = BOARD_COORDS[coords[0]][coords[1]]

                print_board(BOARD_COORDS)
                print()

                is_finished = finished(index)

