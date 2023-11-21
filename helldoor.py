import os
import sys
from getpass import getpass

import mysql.connector as db
from dotenv import load_dotenv


class Helldoor:
    def __init__(self):
        self.command = sys.argv[1]
        self.fetch_command()

    def fetch_command(self):
        load_dotenv()
        self.make_db_connection()
        if self.command == "create":
            self.create_user()
        elif self.command == "open":
            self.verify_credentials()
        elif self.command == "change":
            self.change_credentials()
        elif self.command == "delete":
            self.delete_user()
        else:
            print("Unknown Command")

    def make_db_connection(self):
        self.mydb = db.connect(
            host="localhost",
            user=os.getenv("user"),
            password=os.getenv("password"),
            database=os.getenv("database"),
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
                    f"INSERT INTO master_accounts VALUES('{master_username}','{hashed_pass}');"
                )
                self.mydb.commit()
                print("User Added")
                break
            else:
                print(f"Passwords do not match. Try Again({chances}/3) !!!")

    def verify_credentials(self):
        master_username = input("Username : ")
        master_password = getpass("Password : ")

        self.cursor.execute("SELECT username from master_accounts;")
        username_list = self.cursor.fetchall()

        if any(user[0] == master_username for user in username_list):
            hashed_pass = self.hash_me(master_password)
            self.cursor.execute(
                f"SELECT hash_pass from master_accounts where username='{master_username}';"
            )
            db_hashed_pass = self.cursor.fetchone()[0]

            if hashed_pass == db_hashed_pass:
                print("Welcome!!!")
                self.open_door()
            else:
                print("Invalid Credentials")
        else:
            print("No user found")

    @staticmethod
    def change_credentials():
        old_master_pass = getpass("Current Password : ")
        new_master_pass = getpass("New Password : ")
        repeat_new_master_pass = getpass("Repeat New Password : ")
        if (
            os.getenv("master_password") == old_master_pass
            and new_master_pass == repeat_new_master_pass
        ):
            os.environ["master_password"] = new_master_pass
            print("Password Changed Successfully")
        else:
            print("Failed to Change Password")

    def delete_user(self):
        pass

    @staticmethod
    def open_door():
        pass


if __name__ == "__main__":
    door = Helldoor()
