from pynput.keyboard import Key, Controller, KeyCode
import time

keyboard = Controller()


print(KeyCode(char='v').vk)
# Press and release space
keyboard.press(KeyCode('<162>'))
keyboard.press(KeyCode(char='a'))
time.sleep(1)
keyboard.release(KeyCode('<162>'))
keyboard.release(KeyCode(char='a'))

# Type a lower case A; this will work even if no key on the
# physical keyboard is labelled 'A'

# from pynput.keyboard import Key, KeyCode, Listener

# def on_press(key):
#     try:
#         print(KeyCode(char='<162>').char)
#         print('alphanumeric key {0} pressed'.format(key.char))
#     except AttributeError:
#         print('special key {0} pressed'.format(key))
#         print(key.value.char)

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
#     on_release=on_release)
# listener.start()
