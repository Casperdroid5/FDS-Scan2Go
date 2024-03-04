from button import Button  # Importing the Button class from your code

if __name__ == "__main__":
    button = Button(pin_number=17)

    while True:
        if button.is_pressed():
            print("Button is pressed!")
        elif button.is_not_pressed():
            print("Button is not pressed!")
