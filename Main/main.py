import os

from kivy.app import App
from kivy.core.window import Window
from kivy.factory import Factory
from kivy.lang import Builder
from kivy.metrics import dp
# noinspection PyUnresolvedReferences
from kivy.properties import NumericProperty, StringProperty
from kivy.uix.behaviors import ButtonBehavior
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.screenmanager import Screen, ScreenManager, SlideTransition

from Db.Db import Database

Window.softinput_mode = "below_target"  # клавиатура не закрывает поле ввода

KV = """
#:import dp kivy.metrics.dp

<WrapLabel@Label>:
    size_hint_y: None
    text_size: self.width, None
    height: self.texture_size[1] + dp(8)
    halign: 'left'
    valign: 'top'

<TopBar@BoxLayout>:
    size_hint_y: None
    height: dp(48)
    padding: dp(6)
    spacing: dp(6)

<BookCard>:
    orientation: 'vertical'
    size_hint_y: None
    height: dp(96)
    padding: dp(10)
    canvas.before:
        Color:
            rgba: (0.24, 0.28, 0.40, 1) if self.state == 'down' else (0.15, 0.17, 0.25, 1)
        Rectangle:
            pos: self.pos
            size: self.size
    Label:
        text: root.title
        bold: True
        font_size: '17sp'
        halign: 'left'
        text_size: self.size
    Label:
        text: root.subtitle
        font_size: '14sp'
        halign: 'left'
        text_size: self.size
    Label:
        text: root.rating_text
        font_size: '13sp'
        color: 1, 0.85, 0.3, 1
        halign: 'left'
        text_size: self.size

<ReviewItem>:
    orientation: 'vertical'
    size_hint_y: None
    height: self.minimum_height
    padding: dp(8)
    canvas.before:
        Color:
            rgba: 0.15, 0.17, 0.25, 1
        Rectangle:
            pos: self.pos
            size: self.size
    WrapLabel:
        text: root.header
        bold: True
        color: 1, 0.85, 0.3, 1
    WrapLabel:
        text: root.comment

<LoginScreen>:
    BoxLayout:
        orientation: 'vertical'
        padding: dp(24)
        spacing: dp(12)
        Label:
            text: 'Библиотека'
            font_size: '30sp'
            size_hint_y: None
            height: dp(80)
        TextInput:
            id: username
            hint_text: 'Логин'
            multiline: False
            size_hint_y: None
            height: dp(46)
        TextInput:
            id: password
            hint_text: 'Пароль'
            password: True
            multiline: False
            size_hint_y: None
            height: dp(46)
            on_text_validate: root.login()
        Label:
            id: message
            color: 1, 0.45, 0.45, 1
            size_hint_y: None
            height: dp(30)
        BoxLayout:
            size_hint_y: None
            height: dp(50)
            spacing: dp(8)
            Button:
                text: 'Войти'
                on_release: root.login()
            Button:
                text: 'Регистрация'
                on_release: root.register()
        Widget:

<CatalogScreen>:
    BoxLayout:
        orientation: 'vertical'
        TopBar:
            Label:
                id: user_label
                halign: 'left'
                valign: 'middle'
                text_size: self.size
            Button:
                text: 'Кабинет'
                size_hint_x: None
                width: dp(110)
                on_release: app.go('profile')
            Button:
                id: admin_btn
                text: 'Админ'
                size_hint_x: None
                width: 0 if self.disabled else dp(100)
                opacity: 0 if self.disabled else 1
                disabled: True
                on_release: app.go('admin')
            Button:
                text: 'Выйти'
                size_hint_x: None
                width: dp(90)
                on_release: app.logout()
        TopBar:
            Label:
                text: 'Жанр:'
                size_hint_x: None
                width: dp(60)
            Spinner:
                id: genre_spinner
                text: 'Все'
                on_text: root.refresh()
        ScrollView:
            BoxLayout:
                id: books_box
                orientation: 'vertical'
                size_hint_y: None
                height: self.minimum_height
                spacing: dp(6)
                padding: dp(8)

<BookScreen>:
    BoxLayout:
        orientation: 'vertical'
        TopBar:
            Button:
                text: 'Назад'
                size_hint_x: None
                width: dp(90)
                on_release: app.go('catalog', 'right')
            Label:
                id: title_label
                bold: True
                shorten: True
                text_size: self.size
                halign: 'left'
                valign: 'middle'
        ScrollView:
            BoxLayout:
                orientation: 'vertical'
                size_hint_y: None
                height: self.minimum_height
                padding: dp(12)
                spacing: dp(8)
                WrapLabel:
                    id: info_label
                    font_size: '15sp'
                    color: 1, 0.85, 0.3, 1
                WrapLabel:
                    id: desc_label
                Button:
                    text: 'Читать книгу'
                    size_hint_y: None
                    height: dp(50)
                    on_release: root.open_reader()
                WrapLabel:
                    text: 'Отзывы'
                    bold: True
                    font_size: '18sp'
                BoxLayout:
                    id: reviews_box
                    orientation: 'vertical'
                    size_hint_y: None
                    height: self.minimum_height
                    spacing: dp(8)
                WrapLabel:
                    text: 'Ваш отзыв'
                    bold: True
                    font_size: '18sp'
                BoxLayout:
                    size_hint_y: None
                    height: dp(44)
                    spacing: dp(8)
                    Label:
                        text: 'Оценка (1-5):'
                        size_hint_x: None
                        width: dp(110)
                    Spinner:
                        id: rating_spinner
                        text: '5'
                        values: ['5', '4', '3', '2', '1']
                TextInput:
                    id: comment_input
                    hint_text: 'Напишите отзыв о книге'
                    size_hint_y: None
                    height: dp(120)
                Label:
                    id: review_msg
                    color: 0.5, 1, 0.5, 1
                    size_hint_y: None
                    height: dp(28)
                Button:
                    text: 'Сохранить отзыв'
                    size_hint_y: None
                    height: dp(50)
                    on_release: root.save_review()

<ReaderScreen>:
    BoxLayout:
        orientation: 'vertical'
        TopBar:
            Button:
                text: 'Назад'
                size_hint_x: None
                width: dp(90)
                on_release: app.go('book', 'right')
            Label:
                id: title_label
                shorten: True
                text_size: self.size
                halign: 'left'
                valign: 'middle'
            Button:
                text: 'A-'
                size_hint_x: None
                width: dp(52)
                on_release: root.change_font(-2)
            Button:
                text: 'A+'
                size_hint_x: None
                width: dp(52)
                on_release: root.change_font(2)
        ScrollView:
            BoxLayout:
                id: text_box
                orientation: 'vertical'
                size_hint_y: None
                height: self.minimum_height
                padding: dp(14)
                spacing: dp(6)

<ProfileScreen>:
    BoxLayout:
        orientation: 'vertical'
        TopBar:
            Button:
                text: 'Назад'
                size_hint_x: None
                width: dp(90)
                on_release: app.go('catalog', 'right')
            Label:
                text: 'Личный кабинет'
                bold: True
                text_size: self.size
                halign: 'left'
                valign: 'middle'
            Button:
                text: 'Выйти'
                size_hint_x: None
                width: dp(90)
                on_release: app.logout()
        WrapLabel:
            id: user_info
            font_size: '16sp'
            color: 1, 0.85, 0.3, 1
        WrapLabel:
            text: 'Мои отзывы'
            bold: True
            font_size: '18sp'
        ScrollView:
            BoxLayout:
                id: my_reviews_box
                orientation: 'vertical'
                size_hint_y: None
                height: self.minimum_height
                padding: dp(8)
                spacing: dp(8)

<AdminScreen>:
    BoxLayout:
        orientation: 'vertical'
        TopBar:
            Button:
                text: 'Назад'
                size_hint_x: None
                width: dp(90)
                on_release: app.go('catalog', 'right')
            Label:
                text: 'Администрирование'
                bold: True
                text_size: self.size
                halign: 'left'
                valign: 'middle'
        WrapLabel:
            id: admin_info
            font_size: '16sp'
            color: 1, 0.85, 0.3, 1
        ScrollView:
            BoxLayout:
                id: admin_users_box
                orientation: 'vertical'
                size_hint_y: None
                height: self.minimum_height
                padding: dp(8)
                spacing: dp(4)
"""


def plural(n, one, few, many):
    n10, n100 = n % 10, n % 100
    if n10 == 1 and n100 != 11:
        return one
    if 2 <= n10 <= 4 and not 12 <= n100 <= 14:
        return few
    return many


def rating_text(avg, count):
    if not count:
        return "Оценок пока нет"
    return "Рейтинг: %.1f / 5 (%d %s)" % (
        avg, count, plural(count, "отзыв", "отзыва", "отзывов"))


class BookCard(ButtonBehavior, BoxLayout):
    book_id = NumericProperty(0)
    title = StringProperty("")
    subtitle = StringProperty("")
    rating_text = StringProperty("")

    def on_release(self):
        App.get_running_app().open_book(self.book_id)


class ReviewItem(BoxLayout):
    header = StringProperty("")
    comment = StringProperty("")


class LoginScreen(Screen):
    def _enter(self, user):
        app = App.get_running_app()
        app.current_user = user
        self.ids.password.text = ""
        self.ids.message.text = ""
        app.go("catalog")

    def login(self):
        app = App.get_running_app()
        user = app.db.login(self.ids.username.text, self.ids.password.text)
        if user:
            self._enter(user)
        else:
            self.ids.message.text = "Неверный логин или пароль"

    def register(self):
        app = App.get_running_app()
        user, msg = app.db.register(self.ids.username.text, self.ids.password.text)
        if user:
            self._enter(user)
        else:
            self.ids.message.text = msg


class CatalogScreen(Screen):
    def on_pre_enter(self, *args):
        app = App.get_running_app()
        spinner = self.ids.genre_spinner
        spinner.values = ["Все"] + app.db.genres()
        if app.current_user:
            self.ids.user_label.text = "Вы вошли как: " + app.current_user["username"]
            self.ids.admin_btn.disabled = app.current_user["role"] != "admin"
        self.refresh()

    def refresh(self):
        app = App.get_running_app()
        box = self.ids.books_box
        box.clear_widgets()
        for b in app.db.books(self.ids.genre_spinner.text):
            box.add_widget(BookCard(
                book_id=b["id"],
                title=b["title"],
                subtitle="%s · %s" % (b["author"], b["genre"]),
                rating_text=rating_text(b["avg_rating"], b["reviews_count"]),
            ))


class AdminScreen(Screen):
    def on_pre_enter(self, *args):
        app = App.get_running_app()
        users = app.db.users()
        self.ids.admin_info.text = "Всего пользователей: %d" % len(users)
        box = self.ids.admin_users_box
        box.clear_widgets()
        for u in users:
            row = BoxLayout(size_hint_y=None, height=dp(42), spacing=dp(6))
            name = Label(text=u["username"], size_hint_x=0.6,
                         halign='left', valign='middle')
            name.bind(size=lambda inst, val: setattr(inst, "text_size", val))
            row.add_widget(name)
            row.add_widget(Label(text="отзывов: %d" % u["reviews_count"],
                                 size_hint_x=0.25))
            if u["role"] == "admin" or u["id"] == app.current_user["id"]:
                row.add_widget(Label(text="—", size_hint_x=0.15))
            else:
                btn = Button(text="Удалить", size_hint_x=0.15)
                btn.bind(on_release=lambda inst, uid=u["id"]: self.delete_user(uid))
                row.add_widget(btn)
            box.add_widget(row)

    def delete_user(self, user_id):
        App.get_running_app().db.delete_user(user_id)
        self.on_pre_enter()


class ProfileScreen(Screen):
    def on_pre_enter(self, *args):
        app = App.get_running_app()
        user = app.current_user
        role = "Администратор" if user["role"] == "admin" else "Пользователь"
        self.ids.user_info.text = "Логин: %s · ID: %d · %s" % (
            user["username"], user["id"], role)
        box = self.ids.my_reviews_box
        box.clear_widgets()
        reviews = app.db.user_reviews(user["id"])
        if not reviews:
            box.add_widget(Factory.WrapLabel(text="Вы ещё не оставили ни одного отзыва."))
        for r in reviews:
            box.add_widget(ReviewItem(
                header="%s · %d/5 · %s" % (r["title"], r["rating"], r["created"]),
                comment=r["comment"] or "(без текста)",
            ))


class BookScreen(Screen):
    book_id = NumericProperty(0)

    def load(self, book_id):
        app = App.get_running_app()
        self.book_id = book_id
        b = app.db.book(book_id)
        self.ids.title_label.text = b["title"]
        self.ids.info_label.text = "%s · %s\n%s" % (
            b["author"], b["genre"], rating_text(b["avg_rating"], b["reviews_count"]))
        self.ids.desc_label.text = b["description"]

        box = self.ids.reviews_box
        box.clear_widgets()
        reviews = app.db.reviews(book_id)
        if not reviews:
            box.add_widget(Factory.WrapLabel(text="Пока нет отзывов. Будьте первым!"))
        for r in reviews:
            box.add_widget(ReviewItem(
                header="%s: %d/5 · %s" % (r["username"], r["rating"], r["created"]),
                comment=r["comment"] or "(без текста)",
            ))

        mine = app.db.my_review(book_id, app.current_user["id"])
        self.ids.rating_spinner.text = str(mine["rating"]) if mine else "5"
        self.ids.comment_input.text = mine["comment"] if mine else ""
        self.ids.review_msg.text = ""

    def save_review(self):
        app = App.get_running_app()
        app.db.save_review(
            self.book_id,
            app.current_user["id"],
            int(self.ids.rating_spinner.text),
            self.ids.comment_input.text,
        )
        self.load(self.book_id)
        self.ids.review_msg.text = "Отзыв сохранён"

    def open_reader(self):
        app = App.get_running_app()
        app.sm.get_screen("reader").load(self.book_id)
        app.go("reader")


class ReaderScreen(Screen):
    font_size = NumericProperty(18)

    def load(self, book_id):
        app = App.get_running_app()
        self.ids.title_label.text = app.db.book(book_id)["title"]
        box = self.ids.text_box
        box.clear_widgets()
        # по одному Label на абзац: у очень длинного текста иначе не хватит текстуры
        for para in app.db.book_text(book_id).split("\n\n"):
            para = para.strip()
            if para:
                box.add_widget(Factory.WrapLabel(text=para, font_size=self.font_size))

    def change_font(self, delta):
        self.font_size = max(12, min(40, self.font_size + delta))
        for child in self.ids.text_box.children:
            child.font_size = self.font_size


class LibraryApp(App):
    title = "Библиотека"
    current_user = None

    def build(self):
        Builder.load_string(KV)
        self.db = Database(os.path.join(self.user_data_dir, "library.db"))
        self.db.import_texts(os.path.join(os.path.dirname(os.path.abspath(__file__)), "books"))
        self.sm = ScreenManager(transition=SlideTransition())
        for name, cls in (("login", LoginScreen), ("catalog", CatalogScreen),
                          ("book", BookScreen), ("reader", ReaderScreen),
                          ("profile", ProfileScreen), ("admin", AdminScreen)):
            self.sm.add_widget(cls(name=name))
        Window.bind(on_keyboard=self._on_keyboard)
        return self.sm

    def go(self, name, direction="left"):
        self.sm.transition.direction = direction
        self.sm.current = name

    def open_book(self, book_id):
        self.sm.get_screen("book").load(book_id)
        self.go("book")

    def logout(self):
        self.current_user = None
        self.go("login", "right")

    def _on_keyboard(self, window, key, *args):
        # кнопка «Назад» на Android (код 27)
        if key == 27:
            if self.sm.current == "reader":
                self.go("book", "right")
                return True
            if self.sm.current == "book":
                self.go("catalog", "right")
                return True
        return False


if __name__ == "__main__":
    LibraryApp().run()