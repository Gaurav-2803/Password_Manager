import os
import platform
import sys
from getpass import getpass

import mysql.connector as db


class HelldoorUsers:
    door_opened = False

    def __init__(self):
        self.command = sys.argv[1]
        self.fetch_user_command()

    def fetch_user_command(self):
        self.make_db_connection()
        if self.command == "create":
            self.create_user()
        elif self.command == "open":
            if len(sys.argv) == 3:
                self.verify_credentials()
            else:
                print("Flag is missing after the command.\nFor more info use 'help'")
        elif self.command == "change":
            self.change_credentials()
        elif self.command == "delete":
            self.delete_user()
        elif self.command == "help":
            self.help()
        else:
            print("Unknown Command")

    def make_db_connection(self):
        self.mydb = db.connect(
            host="localhost",
            user="root",
            password="root",
            database="password_manager",
        )
        self.cursor = self.mydb.cursor()

    @staticmethod
    def hash_me(plain_pass: str) -> str:
        return plain_pass + "123"

    def create_user(self):
        for chances in range(1, 4):
            master_username = input("Username : ")
            self.cursor.execute("SELECT username from master_accounts;")
            username_list = self.cursor.fetchall()
            if master_username in username_list:
                print(f"Username Taken, Try Again({chances}/3)")
            else:
                break

        for chances in range(1, 4):
            master_pass = getpass("Password : ")
            repeat_master_pass = getpass("Repeat Password : ")

            if master_pass == repeat_master_pass:
                hashed_pass = self.hash_me(master_pass)
                self.cursor.execute(
                    f"""
                    INSERT INTO master_accounts
                    VALUES ('{master_username}','{hashed_pass}');
                    """
                )
                self.mydb.commit()
                print("User Added")
                self.verify_credentials()
            else:
                print(f"Passwords do not match. Try Again({chances}/3) !!!")

    def verify_credentials(self):
        print("Login:")
        self.master_username = input("Username : ")
        self.master_password = getpass("Password : ")

        self.cursor.execute("SELECT username FROM master_accounts;")
        username_list = self.cursor.fetchall()

        if any(user[0] == self.master_username for user in username_list):
            hashed_pass = self.hash_me(self.master_password)
            self.cursor.execute(
                f"""
                SELECT hash_pass
                FROM master_accounts
                WHERE username='{self.master_username}';
                """
            )
            db_hashed_pass = self.cursor.fetchone()[0]

            if hashed_pass == db_hashed_pass:
                print("Welcome!!!")
                self.door_opened = True
                HelldoorSecrets()
            else:
                print("Invalid Credentials")

        else:
            print("No user found")

    def ask_for_login(self, message):
        print("You Must Login First!!!")
        self.verify_credentials()
        if not self.door_opened:
            exit()
        print(message)

    def change_credentials(self):
        self.ask_for_login("Let's Change Your Password")

        for chances in range(1, 4):
            old_master_pass = getpass("Current Password : ")

            if self.master_password == old_master_pass:
                for chances in range(1, 4):
                    new_master_pass = getpass("New Password : ")
                    repeat_new_master_pass = getpass("Repeat New Password : ")

                    if new_master_pass == repeat_new_master_pass:
                        self.master_password = new_master_pass
                        hashed_pass = self.hash_me(self.master_password)

                        self.cursor.execute(
                            f"""
                            UPDATE master_accounts
                            SET hash_pass = '{hashed_pass}'
                            WHERE username = '{self.master_username}';
                            """
                        )
                        self.mydb.commit()
                        print("Password Changed Successfully")

                    else:
                        print(f"Passwords do not match. Try Again({chances}/3)")

                print("Out of Chances. Try Later Sometime.")
                exit()

            else:
                print(f"Current Password is Invalid. Try Again({chances}/3)")

        print("Out of Chances. Try Later Sometime.")

    def delete_user(self):
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

    @staticmethod
    def help():
        print("Bringing help to you soon")


class HelldoorSecrets(HelldoorUsers):
    def __init__(self):
        self.flag = sys.argv[2]
        self.flag_check()

    @staticmethod
    def clear_screen():
        current_os = platform.system()
        if current_os == "Windows":
            os.system("cls")

        elif current_os == "Linux":
            os.system("clear")

    def flag_check(self):
        self.clear_screen()
        if self.flag in {"-a", "-add"}:
            self.add_credentials()
        elif self.flag in {"-v", "-view", "-va", "-viewall"}:
            self.view_credentials()
        elif self.flag in {"-d", "-delete", "-da", "-deleteall"}:
            self.delete_credentials()
        elif self.flag in {"-u", "-update"}:
            self.view_credentials()
        else:
            print("Invalid Flag")


if __name__ == "__main__":
    door = HelldoorUsers()
