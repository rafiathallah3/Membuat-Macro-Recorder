
# from pynput.keyboard import Key, Controller, KeyCode
# import time

# keyboard = Controller()

# print(KeyCode(vk=65).char)
# Press and release space
# keyboard.press(KeyCode(vk=0, char='b'))
# time.sleep(1)
# keyboard.release(KeyCode(vk=0, char='b'))

# from pynput.keyboard import Key, KeyCode, Listener

# def on_press(key):
#     try:
#         print('alphanumeric key {0} pressed'.format(key.vk))
#     except AttributeError:
#         print('special key {0} pressed'.format(key))

# def on_release(key):
#     print('{0} released'.format(key))
#     if key == Key.esc:
#         # Stop listener
#         return False

# # Collect events until released
# with Listener(
#         on_press=on_press,
#         on_release=on_release) as listener:
#     listener.join()

# # ...or, in a non-blocking fashion:
# listener = Listener(
#     on_press=on_press,
#     on_release=on_release,
#     suppress=True
#     )
# listener.start()
