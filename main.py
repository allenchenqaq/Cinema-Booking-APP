import random
import string
import sqlite3
from fpdf import FPDF


class User:

    def __init__(self, name):
        self.name = name

    def buy(self, seat, card):
        if seat.is_empty():
            if card.validate(seat.get_price()):
                seat.occupy()
                ticket = Ticket(self, seat.get_price(), seat_id)
                ticket.to_pdf()
                return "Purchase successful!"
            else:
                return "There was a problem with your card!"
        else:
            return "Seat is unavailable!"


class Seat:

    database = "cinema.db"

    def __init__(self, seat_id):
        self.seat_id = seat_id

    def get_price(self):
        connect = sqlite3.connect(self.database)
        cursor = connect.cursor()
        cursor.execute("""
        SELECT "price" FROM "Seat" WHERE "seat_id" = ?
        """, [self.seat_id])
        price = cursor.fetchall()[0][0]
        return price

    def is_empty(self):
        connect = sqlite3.connect(self.database)
        cursor = connect.cursor()
        cursor.execute("""
        SELECT "taken" FROM "Seat" WHERE "seat_id" = ?
        """, [self.seat_id])
        res = cursor.fetchall()[0][0]
        if res != 0:
            return False
        else:
            return True

    def occupy(self):
        if self.is_empty():
            connect = sqlite3.connect(self.database)
            connect.execute("""
            UPDATE "Seat" SET "taken"=? WHERE "seat_id"=?
            """, [1, self.seat_id])
            connect.commit()
            connect.close()


class Card:

    database = "banking.db"

    def __init__(self, type, number, cvc, holder):
        self.type = type
        self.number = number
        self.cvc = cvc
        self.holder = holder

    def validate(self, price):
        connect = sqlite3.connect(self.database)
        cursor = connect.cursor()
        cursor.execute("""
        SELECT "balance" FROM "Card" WHERE "number"=? and "cvc"=?
        """, [self.number, self.cvc])
        res = cursor.fetchall()
        if res:
            balance = res[0][0]
            if balance >= price:
                connect.execute("""
                UPDATE "Card" SET "balance" = ? WHERE "number"=? and "cvc"=?
                """, [balance-price, self.number, self.cvc])
                connect.commit()
                connect.close()
                return True


class Ticket:

    def __init__(self, user, price, seat_number):
        self.user = user
        self.price = price
        self.id = "".join([random.choice(string.ascii_letters) for i in range(8)])
        self.seat_number = seat_number

    def to_pdf(self):
        pdf = FPDF('P', 'pt', 'A4')
        pdf.add_page()
        pdf.set_font("Times", "B", 24)
        pdf.cell(0, 80, "Your Cinema Ticket", 1, 1, "C")

        pdf.set_font("Times", "B", 14)
        pdf.cell(100, 25, "Name: ", 1)
        pdf.set_font("Times", "", 12)
        pdf.cell(0, 25, self.user.name, 1, 1)
        pdf.cell(0, 5, "", 0, 1)

        pdf.set_font("Times", "B", 14)
        pdf.cell(100, 25, "Ticket ID: ", 1)
        pdf.set_font("Times", "", 12)
        pdf.cell(0, 25, self.id, 1, 1)
        pdf.cell(0, 5, "", 0, 1)

        pdf.set_font("Times", "B", 14)
        pdf.cell(100, 25, "Price: ", 1)
        pdf.set_font("Times", "", 12)
        pdf.cell(0, 25, str(self.price), 1, 1)
        pdf.cell(0, 5, "", 0, 1)

        pdf.set_font("Times", "B", 14)
        pdf.cell(100, 25, "Seat Number: ", 1)
        pdf.set_font("Times", "", 12)
        pdf.cell(0, 25, str(self.seat_number), 1, 1)
        pdf.cell(0, 5, "", 0, 1)

        pdf.output("ticket.pdf", 'F')


if __name__ == "__main__":
    name = input("Your full name: ")
    seat_id = input("Preferred seat: ")
    card_type = input("Your card type: ")
    card_number = input("Your card number: ")
    card_cvc = input("Your card cvc: ")
    card_holder = input("Cardholder name: ")
    user = User(name)
    seat = Seat(seat_id)
    card = Card(card_type, card_number, card_cvc, card_holder)
    print(user.buy(seat, card))
