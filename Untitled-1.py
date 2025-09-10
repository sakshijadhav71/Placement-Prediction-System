# Password Validation: Create a program that checks if the entered password meets the following criteria:

# At least 8 characters long
# Contains at least one uppercase letter
# Contains at least one number

user=eval(input('enter a username: '))
password=eval(input("enter a password:"))

if password<8:
    print("At least 8 characters long")
    if password.islower():
        print("Contains at least one uppercase letter")
        if password.isalpha():
            print("Contains at least one number")
            