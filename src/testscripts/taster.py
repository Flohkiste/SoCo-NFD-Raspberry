from gpiozero import Button

button = Button(16)

while True:
    button.wait_for_press()

    if button.is_pressed:
        print("Button is pressed")
