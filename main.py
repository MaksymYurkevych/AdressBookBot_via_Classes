from collections import UserDict


class Field:
    """Parent class for all fields"""

    def __init__(self, value):
        self.value = value

    def __repr__(self):
        return self.value


class Name(Field):
    """Required field with username"""

    def __init__(self, value):
        super().__init__(value)


class Phone(Field):
    """Optional field with phone numbers"""

    @staticmethod
    def sanitize_number(number):
        """Return phone number that only include digits"""
        clean_phone = (number.strip().replace("-", "").replace("(", "").replace(")", "").replace("+", ""))
        return clean_phone

    def __init__(self, phone):
        clean_number = Phone.sanitize_number(phone)
        super().__init__(clean_number)


class Record:
    """Class for add, remove, change fields"""

    def __init__(self, name: Name, phone: Phone = None):
        self.name = name
        self.phone = phone
        self.phones = []
        if phone:
            self.phones.append(phone)

    def add_phone(self, phone: Phone):
        self.phones.append(phone)

    def change(self, old_p, new_p):
        for phone in self.phones:
            if phone.value == old_p:
                self.phones.remove(phone)
                self.phones.append(Phone(new_p))
                return
        return f"Phone {old_p} was not found in your records"


class AddressBook(UserDict):
    """Class for creating address book"""

    def add_record(self, record: Record):
        self.data[record.name.value] = record

    def remove_record(self, record):
        self.data.pop(record.name.value, None)

    def show_one_record(self, name):
        rec = self.get(name)
        if rec:
            return f"{rec.name} : {','.join([str(p) for p in rec.phones])}"
        return f"There is no contact with the name {name}"

    def show_all_records(self):
        if self.data:
            result = []
            for rec in self.values():
                result.append(f"{rec.name} : {','.join([str(p) for p in rec.phones])}")
            return '\n'.join(result)
        return "Your address book is empty"

    def change_record(self, username, old_n, new_n):
        record = self.data.get(username.value)
        if record:
            record.change(old_n, new_n)

def error_handler(func):
    def wrapper(*args):
        try:
            return func(*args)
        except IndexError:
            return "You didn't provide contact name or phone number"
        except ValueError:
            return "Phone number must include digits only"
        except KeyError:
            return "Username is not in contact list"

    return wrapper


ADDRESSBOOK = AddressBook()

HELP_INSTRUCTIONS = """This contact bot save your contacts
    Global commands:
      'add' - add new contact. Input username and phone
    Example: add User_name 095-xxx-xx-xx
      'change' - change users old phone to new phone. Input username, old phone and new phone
    Example: change User_name 095-xxx-xx-xx 050-xxx-xx-xx
      'phone' - show contacts of input user. Input username
    Example: phone User_name
      'delete' - removes contact from your address book
    Example: delete User_name
      'show all' - show all contacts
    Example: show all
      'exit/'.'/'bye'/'close' - exit bot
    Example: exit"""


@error_handler
def add(*args):
    """Adds new contact, requires name and phone"""
    name = Name(args[0])
    phone = Phone(args[1])
    rec = ADDRESSBOOK.get(name.value)

    if name.value in ADDRESSBOOK.show_all_records():
        while True:
            user_input = input(
                "Contact with this name already exist, do you want to rewrite it or create new record? '1'/'2'\n")
            if user_input == "2":
                name.value += "(1)"
                rec = ADDRESSBOOK.get(name.value)
                break
            elif user_input == "1":
                ADDRESSBOOK.remove_record(rec)
                rec = ADDRESSBOOK.get(name.value)
                break
            else:
                print("Please type '1' or '2' to continue")

    if not phone.value.isnumeric():
        raise ValueError
    if rec:
        rec.add_phone(phone)
    else:
        rec = Record(name, phone)
        ADDRESSBOOK.add_record(rec)
    return f'You just added contact "{name}" with phone "{phone}" to your list of contacts'


@error_handler
def hello(*args):
    """Greets user"""
    return "How can I help you?"


@error_handler
def show_all(*args):
    """Show a list of all contacts that were added before"""
    return ADDRESSBOOK.show_all_records()


@error_handler
def change(*args):
    """Replace phone number for an existing contact"""
    name = Name(args[0])
    old_ph = args[1]
    new_ph = args[2]

    if not new_ph.isnumeric():
        raise ValueError

    ADDRESSBOOK.change_record(name, old_ph, new_ph)
    return f"You just changed number for contact '{name}'. New number is '{new_ph}'"


@error_handler
def phone(*args):
    """Shows a phone number for a chosen contact"""
    return ADDRESSBOOK.show_one_record(args[0])


@error_handler
def helper(*args):
    return HELP_INSTRUCTIONS


@error_handler
def delete_contact(*args):
    name = Name(args[0])
    rec = Record(name)
    if name.value:
        ADDRESSBOOK.remove_record(rec)
        return f"{name} was deleted from your contact list"
    else:
        raise IndexError


COMMANDS = {
    add: "add",
    hello: "hello",
    show_all: "show all",
    change: "change",
    phone: "phone",
    helper: "help",
    delete_contact: "delete"
}


def command_parser(user_input):
    for command, key_word in COMMANDS.items():
        if user_input.startswith(key_word):
            return command, user_input.replace(key_word, "").strip().split(" ")
    return None, None


def main():
    print(
        "Here's a list of available commands: 'Hello', 'Add', 'Change', 'Phone', 'Show all', 'Delete', 'Help', 'Exit'")
    while True:
        user_input = input(">>>")
        end_words = [".", "close", "bye", "exit"]

        if user_input.lower() in end_words:
            print("Goodbye and good luck")
            break

        command, data = command_parser(user_input.lower())

        if not command:
            print("Sorry, unknown command")
        else:
            print(command(*data))


if __name__ == '__main__':
    name = Name('Bill')
    phone = Phone('1234567890')
    rec = Record(name, phone)
    ab = AddressBook()
    ab.add_record(rec)

    assert isinstance(ab['Bill'], Record)
    assert isinstance(ab['Bill'].name, Name)
    assert isinstance(ab['Bill'].phones, list)
    assert isinstance(ab['Bill'].phones[0], Phone)
    assert ab['Bill'].phones[0].value == '1234567890'

    print('All Ok)')
    main()
