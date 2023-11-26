import os
import platform
import random
import string
import sys
from getpass import getpass

import argon2
import mysql.connector as db
from cryptography.fernet import Fernet
from prettytable import from_db_cursor


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
        salt_len = 32
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
                HelldoorUsers.master_username = input("Username : ")
                self.cursor.execute("SELECT username from master_accounts;")
                username_list = self.cursor.fetchall()

                if any(
                    user[0] == HelldoorUsers.master_username for user in username_list
                ):
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
                            '{HelldoorUsers.master_username}',
                            '{hashed_pass}',
                            '{salt}'
                            );
                        """
                    )
                    self.mydb.commit()
                    print("User Added")
                    break
                else:
                    print(f"Passwords do not match. Try Again({chances}/3) !!!")

        except KeyboardInterrupt:
            print("\nExited Successfully")
        except Exception as error:
            print(f"Error : {error.__class__.__name__}")

    # your code here
    def verify_credentials(self):
        try:
            print("Login:")
            HelldoorUsers.master_username = input("Username : ")
            self.cursor.execute("SELECT username FROM master_accounts;")
            username_list = self.cursor.fetchall()

            if any(user[0] == HelldoorUsers.master_username for user in username_list):
                self.master_password = getpass("Password : ")
                self.cursor.execute(
                    f"""
                    SELECT hashed_pass, salt
                    FROM master_accounts
                    WHERE username='{HelldoorUsers.master_username}';
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
                                WHERE username = '{HelldoorUsers.master_username}';
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
                        WHERE username = '{HelldoorUsers.master_username}';
                        """
                    )
                    self.mydb.commit()
                    print(f"{HelldoorUsers.master_username} gone forever :(")
                    exit()
                elif ask.loweer() == "n":
                    print(f"Thank You {HelldoorUsers.master_username} for Staying :)")
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
        self.clear_screen()
        self.make_db_connection()
        if self.flag in {"-a", "-add", "-am", "-addmuliple"}:
            self.add_credentials()
        elif self.flag in {"-v", "-view", "-vs", "viewselect", "-va", "-viewall"}:
            self.view_credentials()
        elif self.flag in {"-d", "-del", "-ds", "-delselect", "-da", "-delall"}:
            self.delete_credentials()
        elif self.flag in {"-u", "-update"}:
            self.update_credentials()
        else:
            print(f"'{self.flag}' is Invalid Flag.\nFor more info use 'help'")

    def fetch_encrpytion_key(self):
        # self.cursor.execute(
        #     f"SELECT salt FROM master_accounts WHERE username = '{super().master_username}'"
        # )
        # return self.cursor.fetchone()[0].encode("utf-8")
        return Fernet.generate_key()

    def add_credentials(self):
        try:
            print("Exit -> ctrl + c")
            credential_count = 20 if self.flag in {"-am", "-addmultiple"} else 1
            for cred_count in range(credential_count):
                cred_count = "" if credential_count == 1 else f"{cred_count+1})"
                print(f"\n{cred_count} Add Credentials\n-------------------")

                for chances in range(1, 4):
                    self.site_name = input("*Enter Site/App Name : ")
                    if self.site_name == "":
                        print(f"Site/App Name is Required Field ({chances}/3)")
                    else:
                        break

                for chances in range(1, 4):
                    self.password = getpass("*Enter Password : ")
                    if self.password == "":
                        print(f"Password is Required Field ({chances}/3)")
                    else:
                        break

                self.site_url = input("Enter Site/App URL : ")
                self.contact_no = input("Enter Contact No. : ")
                self.email_id = input("Enter Email Id : ")
                self.linked_with = input("Enter Linked Account : ")

                fernet = Fernet(self.fetch_encrpytion_key())
                self.encrypted_pass = fernet.encrypt(self.password.encode())

                self.cursor.execute(
                    "INSERT INTO user_credentials VALUES(%s,%s,%s,%s,%s,%s,%s)",
                    (
                        super().master_username,
                        self.site_name,
                        self.encrypted_pass,
                        self.site_url,
                        self.contact_no,
                        self.email_id,
                        self.linked_with,
                    ),
                )
                self.mydb.commit()
                if self.cursor.rowcount == 1:
                    print(f"\nCredentials added auccessfully for {self.site_name}")
                else:
                    print(f"\n Failed!!!")

            if credential_count == 20:
                print("Limit reached. Login again to add more.")
        except KeyboardInterrupt:
            print("\nExited Successfully")

    def view_credentials(self):
        def fetch_queries(condition):
            self.cursor.execute(
                f"""
                SELECT site_name, encrypted_pass, site_url, contact_num, email_id, linked_with
                FROM user_credentials
                WHERE {condition};
                """
            )

        try:
            if self.flag in {"-va", "viewall"}:
                fetch_queries(f"username = '{super().master_username}'")

            elif self.flag in {"-v", "view"}:
                site_name = input("Enter Site Name : ")
                fetch_queries(f"site_name = '{site_name}'")

            else:
                print(
                    """
                      Filter
                      ---------
                      1. Site/App Name
                      2. Site/App URL
                      3. Contact Number
                      4. Email ID
                      5. Linked Accounts
                      """
                )
                filter_choice = int(input("Which Filter (1-5) : "))
                filter_input = input("Enter Value : ")
                filter_to_column = {
                    1: "site_name",
                    2: "site_url",
                    3: "contact_num",
                    4: "email_id",
                    5: "linked_with",
                }
                fetch_queries(
                    f"{filter_to_column.get(filter_choice)} = '{filter_input}'"
                )

            # if self.cursor.rowcount >= 1:
            print(from_db_cursor(self.cursor))
            # else:
            #     print("0 Credentials Found")

        except KeyboardInterrupt:
            print("\nExited Successfully")

    def delete_credentials(self):
        pass

    def update_credentials(self):
        pass


if __name__ == "__main__":
    door = HelldoorUsers()
