import webbrowser
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.gridlayout import GridLayout
from kivy.uix.image import Image
from kivy.uix.label import Label
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.graphics import Color, Rectangle



class InfoScreen(Screen):
    def __init__(self, **kwargs):
        super(InfoScreen, self).__init__(**kwargs)

        info_text = (
            "[b]Welcome to the Rock, Paper, Scissors, Lizard, Spock Game![/b]\n\n\n"
            "[u]Instructions:[/u]\n\n"
            "1. Choose your gesture using the buttons provided.\n\n"
            "2. You have 3 seconds to choose your gesture. If you don't choose in time, the computer will get 1 mark.\n\n"
            "3. The winner will be determined after 7 rounds.\n\n"
            "4. Marks and the computer's gestures will be indicated using corresponding LEDs.\n\n"
            "5. To end the game, press the Start/End button.\n\n\n"
            "Enjoy the game and good luck!"
        )

        layout = BoxLayout(orientation="vertical")

        help_label = Label(
            text=info_text,
            font_size=20,
            markup=True,
            color=(1, 1, 1, 1),
            text_size=(self.width - 40, None),
            halign="left",
            valign="top"
        )
        help_label.bind(size=self._update_text_size)

        button_layout = BoxLayout(size_hint=(1, 0.2), spacing=10)

        back_button = Button(text="Back", background_color=(0, 191 / 255, 165 / 255, 1))
        back_button.bind(on_press=self.go_back)

        pdf_button = Button(text="Open design choice document", background_color=(0, 191 / 255, 165 / 255, 1))
        pdf_button.bind(on_press=self.open_pdf)

        button_layout.add_widget(back_button)
        button_layout.add_widget(pdf_button)

        layout.add_widget(help_label)
        layout.add_widget(button_layout)
        self.add_widget(layout)

    def _update_text_size(self, instance, value):
        instance.text_size = (instance.width - 40, None)

    def go_back(self, instance):
        self.manager.current = "main"

    def open_pdf(self, instance):
        webbrowser.open("Group_A4.pdf")

class MainApp(App):
    title = "Rock, Paper, Scissors, Lizard, Spock Game"

    def build(self):
        screen_manager = ScreenManager()

        main_screen = self.build_main_screen()
        screen_manager.add_widget(main_screen)

        help_screen = InfoScreen(name="help")
        screen_manager.add_widget(help_screen)

        return screen_manager

    def build_main_screen(self):
        screen = Screen(name="main")
        layout = BoxLayout(orientation="vertical")

        header = BoxLayout(size_hint_y=0.1, padding=10)  # Reduced height of score labels

        # Adding the new "Round" label
        self.round_label = Label(text="Round: 0", font_size=30, halign="center", valign="center", size_hint_x=0.33,
                                 color=(1, 1, 1, 1))

        self.user_score_label = Label(text="Your Score: 0", font_size=30, halign="left", valign="center",
                                      size_hint_x=0.33, color=(1, 1, 1, 1))
        self.computer_score_label = Label(text="Computer Score: 0", font_size=30, halign="right", valign="center",
                                          size_hint_x=0.33, color=(1, 1, 1, 1))

        header.add_widget(self.user_score_label)
        header.add_widget(self.round_label)  # Adding the "Round" label to the header
        header.add_widget(self.computer_score_label)
        layout.add_widget(header)

        self.image_section = GridLayout(cols=2, size_hint_y=0.5)
        self.image1 = Image(source="assets/gesture.png")
        self.image2 = Image(source="assets/gesture.png")
        self.image_section.add_widget(self.image1)
        self.image_section.add_widget(self.image2)
        layout.add_widget(self.image_section)

        image_labels_layout = GridLayout(cols=2, size_hint_y=0.1)  # Reduced height of image labels
        self.image1_label = Label(text="What is your gesture?", font_size=24, halign="center", valign="center",
                                  color=(1, 1, 1, 1))
        self.image2_label = Label(text="What is computer's gesture?", font_size=24, halign="center", valign="center",
                                  color=(1, 1, 1, 1))
        image_labels_layout.add_widget(self.image1_label)
        image_labels_layout.add_widget(self.image2_label)
        layout.add_widget(image_labels_layout)

        self.result_label = Label(text="Press start/end button to start the game", font_size=32, halign="center",
                                  valign="center", size_hint_y=0.1, color=(1, 1, 1, 1))
        layout.add_widget(self.result_label)

        buttons = BoxLayout(size_hint_y=0.2)

        help_button = Button(text="Info", size_hint_x=0.5, size_hint_y=0.5, background_color=(0, 191 / 255, 165 / 255, 1))
        help_button.bind(on_press=self.show_help_screen)
        buttons.add_widget(help_button)

        layout.add_widget(buttons)

        self.primary_color = (46 / 255, 46 / 255, 46 / 255, 1)  # Dark Gray
        self.secondary_color = (204 / 255, 204 / 255, 204 / 255, 1)  # Light Gray
        self.accent_color = (0, 191 / 255, 165 / 255, 1)  # Teal
        self.text_color = (1, 1, 1, 1)  # White

        with layout.canvas.before:
            Color(*self.primary_color)
            self.rect = Rectangle(size=layout.size, pos=layout.pos)
            layout.bind(size=self._update_rect, pos=self._update_rect)

        for widget in layout.children:
            if isinstance(widget, BoxLayout) or isinstance(widget, GridLayout):
                for child in widget.children:
                    if isinstance(child, Label):
                        child.color = self.text_color

        screen.add_widget(layout)
        return screen

    def _update_rect(self, instance, value):
        self.rect.size = instance.size
        self.rect.pos = instance.pos

    def show_help_screen(self, instance):
        self.root.current = "help"

    def change_gesture_images(self, user, computer):
        source1 = "assets/player1_" + user + ".png"
        source2 = "assets/player2_" + computer + ".png"
        self.image1.source = source1
        self.image2.source = source2
        self.image1.reload()
        self.image2.reload()

    def change_images(self, img1, img2):
        source1 = "assets/" + img1 + ".png"
        source2 = "assets/" + img2 + ".png"
        self.image1.source = source1
        self.image2.source = source2
        self.image1.reload()
        self.image2.reload()

    def change_label(self, text_input):
        self.result_label.text = text_input

    def change_score(self, user_score, computer_score):
        self.user_score_label.text = f"Your Score:   {user_score}"
        self.computer_score_label.text = f"Computer Score:   {computer_score}"

    def change_imgtxt(self, user_gesture, computer_gesture):
        self.image1_label.text = user_gesture
        self.image2_label.text = computer_gesture

    def change_round(self, round):
        self.round_label.text = f"Round  : {round}"



if __name__ == "__main__":
    MainApp().run()
