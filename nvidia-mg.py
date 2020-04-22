from time import sleep
import subprocess
import curses
import sys

percent_blocks_10 = ['▁', '▂', '▃', '▄', '▄', '▅', '▆', '▇']

refresh_rate = 500


def get_smi():
    sp = subprocess.Popen(['nvidia-smi', '-q'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    out_str = sp.communicate()
    out_list = out_str[0].decode("utf-8").split('\n')

    out_dict = {}

    header = ''
    for item in out_list:
        if ':' not in item:
            header = item.strip()
        else:
            try:
                key, val = item.split(' :')
                if item.startswith('    '):
                    key, val = header + '_' + key.strip(), val.strip()
                else:
                    key, val = key.strip(), val.strip()
                out_dict[key] = val
            except:
                pass
    return out_dict


# 50 chars width
def get_percent_bar(percent):
    big = percent / 2
    small = percent % 2
    bar = '█' * int(big)
    if small == 1:
        bar += '▌'
    return bar


def draw_menu(stdscr):
    k = 0
    cursor_x = 0
    cursor_y = 0

    # Clear and refresh the screen for a blank canvas
    stdscr.clear()
    stdscr.refresh()

    # Start colors in curses
    curses.start_color()
    curses.init_pair(1, curses.COLOR_CYAN, curses.COLOR_BLACK)
    curses.init_pair(2, curses.COLOR_RED, curses.COLOR_BLACK)
    curses.init_pair(3, curses.COLOR_BLACK, curses.COLOR_WHITE)

    history = []
    mem_history = []
    # Loop where k is the last character pressed
    while True:
        # Initialization
        stdscr.clear()
        height, width = stdscr.getmaxyx()

        if k == curses.KEY_DOWN:
            cursor_y = cursor_y + 1
        elif k == curses.KEY_UP:
            cursor_y = cursor_y - 1
        elif k == curses.KEY_RIGHT:
            cursor_x = cursor_x + 1
        elif k == curses.KEY_LEFT:
            cursor_x = cursor_x - 1

        cursor_x = max(0, cursor_x)
        cursor_x = min(width - 1, cursor_x)

        cursor_y = max(0, cursor_y)
        cursor_y = min(height - 1, cursor_y)

        # Turning on attributes for title
        stdscr.attron(curses.color_pair(2))
        stdscr.attron(curses.A_BOLD)

        # Rendering title
        stdscr.addstr(0, 0, 'NVIDIA Monitor Graph')

        # Turning off attributes for title
        stdscr.attroff(curses.color_pair(2))
        stdscr.attroff(curses.A_BOLD)

        stat = get_smi()
        stdscr.addstr(1, 0, 'Power   : ' + str(stat['Power Readings_Power Draw']) + '/' + str(
            stat['Power Readings_Max Power Limit']))
        stdscr.addstr(2, 60, '▏')
        stdscr.addstr(2, 0, 'GPU Util: ' + get_percent_bar(int(str(stat['Utilization_Gpu']).split(' ')[0])))
        stdscr.addstr(2, 61, str(stat['Utilization_Gpu']))
        stdscr.addstr(3, 0, 'GPU Clk : ' + str(stat['Clocks_Graphics']))
        history.append(int(str(stat['Utilization_Gpu']).split(' ')[0]))
        stdscr.addstr(4, 60, '▏')
        stdscr.addstr(4, 0, 'GPU Mem : ' + get_percent_bar(int(str(stat['Utilization_Memory']).split(' ')[0])))
        stdscr.addstr(4, 61, str(stat['Utilization_Memory']))
        stdscr.addstr(5, 0, 'Mem Clk : ' + str(stat['Clocks_Memory']))
        mem_history.append(int(str(stat['Utilization_Memory']).split(' ')[0]))

        mem_base_y = 2
        stdscr.addstr(height - mem_base_y - 22, 0, 'Memory Utilization')
        for i in range(width):
            stdscr.addstr(height - mem_base_y, i, '▔')
        for i in range(width):
            stdscr.addstr(height - mem_base_y - 21, i, '▁')
        if len(mem_history) > width:
            mem_history.pop(0)
        for tt, gh in enumerate(mem_history[::-1]):
            for percent in range(gh // 5):
                stdscr.addstr(height - percent - mem_base_y - 1, width - tt - 1, '█')
            if gh % 5 != 0:
                stdscr.addstr(height - gh // 5 - mem_base_y - 1, width - tt - 1, percent_blocks_10[gh % 5 * 2 - 1])

        gpu_base_y = 25
        stdscr.addstr(height - gpu_base_y - 22, 0, 'GPU Utilization')
        for i in range(width):
            stdscr.addstr(height - gpu_base_y, i, '▔')
        for i in range(width):
            stdscr.addstr(height - gpu_base_y - 21, i, '▁')
        if len(history) > width:
            history.pop(0)
        for tt, gh in enumerate(history[::-1]):
            for percent in range(gh // 5):
                stdscr.addstr(height - percent - gpu_base_y - 1, width - tt - 1, '█')
            if gh % 5 != 0:
                stdscr.addstr(height - gh // 5 - gpu_base_y - 1, width - tt - 1, percent_blocks_10[gh % 5 * 2 - 1])

        stdscr.move(0, width - 1)

        # Refresh the screen
        stdscr.refresh()

        sleep(refresh_rate / 1000)


def main():
    print(sys.argv)
    if len(sys.argv) > 1:
        global refresh_rate
        refresh_rate = int(sys.argv[1])

    curses.wrapper(draw_menu)


if __name__ == "__main__":
    main()
