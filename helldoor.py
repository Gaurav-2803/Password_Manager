import os
import platform
import random
import string
import sys
from getpass import getpass

import argon2
import mysql.connector as db


class HelldoorUsers:
    door_opened = False
    want_to_login = True
    master_username = ""

    def __init__(self):
        try:
            self.command = sys.argv[1]
            self.fetch_user_command()
        except IndexError:
            print("Command is required.\nFor more info use 'help'")

    def fetch_user_command(self):
        self.make_db_connection()
        if self.command == "create":
            self.create_user()
        elif self.command == "open":
            if len(sys.argv) == 3:
                self.verify_credentials()
            else:
                print("Flag is missing after the command.\nFor more info use 'help'")
                exit()
        elif self.command == "change":
            self.change_credentials()
        elif self.command == "delete":
            self.delete_user()
        elif self.command == "forgot":
            self.forgot_password()
        elif self.command == "help":
            self.help()
        else:
            print("Unknown Command")
            exit()

    def make_db_connection(self):
        self.mydb = db.connect(
            host="localhost",
            user="root",
            password="root",
            database="password_manager",
        )
        self.cursor = self.mydb.cursor()

    @staticmethod
    def hash_password(plain_pass: str) -> str:
        salt_len = 16
        hashed_fn = argon2.PasswordHasher(
            salt_len=salt_len,
        )
        salt = "".join(
            random.choices(
                string.punctuation + string.digits + string.ascii_letters,
                k=salt_len,
            )
        )
        return hashed_fn.hash(plain_pass + salt), salt

    @staticmethod
    def verify_password(hashed_pass: str, plain_pass: str, salt: str):
        try:
            hash_fn = argon2.PasswordHasher()
            hash_fn.verify(hashed_pass, plain_pass + salt)
            return True
        except Exception:
            return False

    def create_user(self):
        try:
            for chances in range(1, 4):
                self.master_username = input("Username : ")
                self.cursor.execute("SELECT username from master_accounts;")
                username_list = self.cursor.fetchall()
                if self.master_username in username_list:
                    print(f"Username Taken, Try Again({chances}/3)")
                else:
                    break

            for chances in range(1, 4):
                self.master_pass = getpass("Password : ")
                repeat_master_pass = getpass("Repeat Password : ")

                if self.master_pass == repeat_master_pass:
                    hashed_pass, salt = self.hash_password(self.master_pass)
                    self.cursor.execute(
                        f"""
                        INSERT INTO master_accounts
                        VALUES (
                            '{self.master_username}',
                            '{hashed_pass}',
                            '{salt}'
                            );
                        """
                    )
                    self.mydb.commit()
                    print("User Added")
                    self.verify_credentials()
                else:
                    print(f"Passwords do not match. Try Again({chances}/3) !!!")

        except KeyboardInterrupt:
            print("\nExited Successfully")

    # your code here
    def verify_credentials(self):
        try:
            print("Login:")
            self.master_username = input("Username : ")
            self.cursor.execute("SELECT username FROM master_accounts;")
            username_list = self.cursor.fetchall()

            if any(user[0] == self.master_username for user in username_list):
                self.master_password = getpass("Password : ")
                self.cursor.execute(
                    f"""
                    SELECT hashed_pass, salt
                    FROM master_accounts
                    WHERE username='{self.master_username}';
                    """
                )
                db_hashed_pass, salt = list(self.cursor.fetchone())

                if self.verify_password(db_hashed_pass, self.master_password, salt):
                    self.door_opened = True
                    if self.want_to_login:
                        print("Welcome!!!")
                        HelldoorSecrets()
                else:
                    print("Invalid Password")

            else:
                print("No user found")

        except KeyboardInterrupt:
            print("\nExited Successfully")

    def ask_for_login(self, message):
        print("Please Verify Yourself")
        self.verify_credentials()
        if not self.door_opened:
            exit()
        print(message)

    def change_credentials(self):
        try:
            self.want_to_login = False
            self.ask_for_login("Let's Change Your Password")

            for chances in range(1, 4):
                old_master_pass = getpass("Current Password : ")

                if self.master_password == old_master_pass:
                    for chances in range(1, 4):
                        new_master_pass = getpass("New Password : ")
                        repeat_new_master_pass = getpass("Repeat New Password : ")

                        if new_master_pass == repeat_new_master_pass:
                            self.master_password = new_master_pass
                            hashed_pass, salt = self.hash_password(self.master_password)

                            self.cursor.execute(
                                f"""
                                UPDATE master_accounts
                                SET hashed_pass = '{hashed_pass}',salt = '{salt}'
                                WHERE username = '{self.master_username}';
                                """
                            )
                            self.mydb.commit()
                            print("Password Changed Successfully")
                            exit()

                        else:
                            print(f"Passwords do not match. Try Again({chances}/3)")

                    print("Out of Chances. Try Later Sometime.")
                    exit()

                else:
                    print(f"Current Password is Invalid. Try Again({chances}/3)")

            print("Out of Chances. Try Later Sometime.")

        except KeyboardInterrupt:
            print("\nExited Successfully")

    def delete_user(self):
        try:
            self.want_to_login = False
            self.ask_for_login("Sad to see you go :(")

            for chances in range(1, 4):
                ask = input("Really wanna go? (Y/N) : ")
                if ask.lower() == "y":
                    self.cursor.execute(
                        f"""
                        DELETE FROM master_accounts
                        WHERE username = '{self.master_username}';
                        """
                    )
                    self.mydb.commit()
                    print(f"{self.master_username} gone forever :(")
                    exit()
                elif ask.loweer() == "n":
                    print(f"Thank You {self.master_username} for Staying :)")
                    exit()
                else:
                    print(f"Invalid Choice. Try Again({chances}/3)")

            print("Out of Chances. Try Later Sometime.")

        except KeyboardInterrupt:
            print("\nExited Successfully")

    def forgot_password(self):
        pass

    @staticmethod
    def help():
        print("Bringing help to you soon")


class HelldoorSecrets(HelldoorUsers):
    def __init__(self):
        try:
            self.flag = sys.argv[2]
            self.flag_check()
        except IndexError:
            print("Flag is required.\nFor more info use 'help'")

    @staticmethod
    def clear_screen():
        current_os = platform.system()
        if current_os == "Windows":
            os.system("cls")

        elif current_os == "Linux":
            os.system("clear")

    def flag_check(self):
        # self.clear_screen()
        self.make_db_connection()
        if self.flag in {"-a", "-add"}:
            self.add_credentials()
        elif self.flag in {"-v", "-view", "-va", "-viewall"}:
            self.view_credentials()
        elif self.flag in {"-d", "-delete", "-da", "-deleteall"}:
            self.delete_credentials()
        elif self.flag in {"-u", "-update"}:
            self.update_credentials()
        else:
            print("Invalid Flag")

    def add_credentials(self):
        try:
            self.site_name = input("Enter Site/App Name : ")
            self.password = getpass("Enter Password : ")
            self.site_url = input("Enter Site/App URL : ")
            self.contact_no = input("Enter Contact No. : ")
            self.email_id = input("Enter Email Id : ")
            self.recovery_email = input("Enter Recovery Mail Id : ")
            self.recovery_question = input("Enter Recovery Question : ")
            self.recovery_answer = input("Enter Recovery Answer :")
            self.hashed_pass, salt = self.hash_password(self.password)
            self.cursor.execute(
                f"""
                INSERT INTO user_credentials
                VALUES(
                    '{self.master_username}',
                    '{self.site_name}',
                    '{self.hashed_pass}',
                    '{self.site_url}',
                    '{self.contact_no}',
                    '{self.email_id}',
                    '{self.recovery_email}',
                    '{self.recovery_question}',
                    '{self.recovery_answer}'
                    );
                """
            )

        except KeyboardInterrupt:
            print("\nExited Successfully")

    def view_credentials(self):
        pass

    def delete_credentials(self):
        pass

    def update_credentials(self):
        pass


if __name__ == "__main__":
    door = HelldoorUsers()
