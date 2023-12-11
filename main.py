from collections import UserDict

class Field:
    def __init__(self, value=None):
        self.value = value

    def __str__(self):
        return str(self.value) or "Undefined"

class Name(Field):
    def __init__(self,value):
        self.value = None
        self.r_id = None
        # Setter
        self.name = value
    
    @property
    def name(self):
        return self.value
    
    @name.setter
    def name(self,value):
        self.value = str(value)



class PhoneCheck:
    def p_check(self,phone:str):
        from re import search
        map = {' ':''}
        phone.translate(map)
        if len(phone) == 10 and search(r'\d{10}', phone) != None:
            return phone
        else:
            print("Incorrect phone number. Must be exactly 10 characters, digits only.")
            raise ValueError

class Birthday:
    def __init__(self, birthday:str):
        self.value = None
        # Setter
        self.birthday = birthday
            
        #raise ValueError("Wrong variable type. Birthday date must be a string with format: MM-DD-YYYY")
    
    @property
    def birthday(self):
        return self.value
    
    @birthday.setter
    def birthday(self,birthday):
        from re import search
        # Format: MM-DD-YYYY
        if birthday == "None":
            self.value = "None"
        elif (search(r'\d{2}\D\d{2}\D\d{4}', birthday) != None and len(birthday) == 10):
            tmp = birthday[0:2]
            if self.month_check(tmp):
                self.value = birthday
        elif search(r'\d{8}', birthday) != None and len(birthday) == 8:
            tmp = birthday[0:2]
            if self.month_check(tmp):
                tmp = birthday[0:2] + "-" + birthday[2:4] + "-" + birthday[4:6] + birthday[6:8]
                self.value = tmp
        else:
            raise ValueError("Wrong birthday format. The correct format would be: MM-DD-YYYY")

    def month_check(self,month:str):
        if len(month) > 2:
            raise ValueError("Wrong month format. Should only contain two symbols.")
        if month[:1] == "0":
            month = month[:1]
        if int(month) <= 12:
            return True
        else:
            raise ValueError("Wrong month format. There can't be more than 12 of them. Correct format: MM-DD-YYYY")

class Phone(Field, PhoneCheck):
    def __init__(self,phone:str):
        self.value = None
        # Setter
        self.phone = phone
    
    @property
    def phone(self):
        return self.value
    
    @phone.setter
    def phone(self,phone):
        if type(self.p_check(phone)) == str:
            self.value = self.p_check(phone)



class Record(PhoneCheck):
    def __init__(self, name, birthday="None"):
        self.birthday = Birthday(birthday)
        self.name = Name(name)
        self.phones = []

    def days_to_birthday(self):
        if self.birthday.value != None:
            from datetime import date,datetime
            TODAY = date.today()
            tmp = self.birthday.value
            BD_DAY = datetime(int(tmp[6:]), int(tmp[0:2]), int(tmp[3:5])).date()
            if (BD_DAY.month < TODAY.month) or ((BD_DAY.month == TODAY.month) and (BD_DAY.day < TODAY.day)):
                BD_DAY = BD_DAY.replace(year = TODAY.year + 1)
            else:
                BD_DAY = BD_DAY.replace(year = TODAY.year)
    
            return (BD_DAY - TODAY)

    def add_phone(self,phone):
        if type(self.p_check(phone)) == str:
            phone_obj = Phone(phone)
            self.phones.append(phone_obj)
            print(f"Added number {phone_obj.value} to the record (named '{self.name.value}')!")
    
    def p_find(self,phone:str):
        for i in self.phones:
            if i.value == phone:
                return i
            
        print(f"No number {phone} in {self.name.value} record!")
        return False

    def edit_phone(self,phone:str,new_phone:str):
        if self.p_find(phone):
            if type(self.p_check(new_phone)) == str:
                self.phones.remove(self.p_find(phone))
                phone_obj = Phone(new_phone)
                self.phones.append(phone_obj)
                return
        
        raise ValueError("Phone not found!")

    def find_phone(self,phone):
        if self.p_find(phone):
            return self.p_find(phone)

    def remove_phone(self,phone):
        if self.p_find(phone):
            self.phones.remove(self.p_find(phone))
        else:
            print(f"No number {phone} in {self.name.value} record!")

    def __str__(self):
        return f"Contact name: {self.name.value}, Birthday: {self.birthday.value}, phones: {'; '.join(p.value for p in self.phones)}"

class AddressBook(UserDict):
    def __init__(self):
        self.data = {}
        self.priority_ids = []
        self.record_cnt = 0
        self.size_check = False
        self.file = "storage.bin"

        self.update_file("load",0)

    def find_in_contacts(self,text:str):
        switch = 0
        for name,record in self.data.items():
            if name.find(text) or record.birthday.value.find(text):
                print(record.__str__())
                switch = 1
            for item in record.phones:
                if item.value.find(text):
                    print(record.__str__())
                switch = 1
        if switch == 0:
            print('Not found!')

    #Saves self.data and some technical variables. Can be used, although everything should be saved automatically. may be used to ensure, that nothing will be lost.
    def save_changes(self):
        self.update_file("ed",0)

    # Prepares self.data to be saved.
    def prepare_data(self,mode:str,record_id:int):
        new_data = {} #{'Record_id':{'Record_name': name.value,'Name':value,'Phone':[values], 'Birthday':value},'Init_mem':{'Record_cnt':value,'Priority_ids':[]} }
        if mode == "add":
            for k,record in self.data.items():
                if record.name.r_id == record_id:
                    new_data[record.name.r_id] = {'Name':record.name.value,'Phone':record.phones,'Birthday':record.birthday.value}
        else:
            new_data['Init_mem'] = {'Record_cnt':self.record_cnt,'Priority_ids':self.priority_ids}
            for k,records in self.data.items():
                new_data[records.name.r_id] = {'Name':records.name.value,'Phone':records.phones,'Birthday':records.birthday.value}

        return new_data
    
    # Dynamicly adds new records, deletes records, creates file.bin, etc.
    def update_file(self,mode:str,r_id:int):
        import pickle
        from pathlib import Path
        file = Path(self.file)
        if not file.exists():
            with open(file, 'wb') as storage:
                new_data = self.prepare_data("del",r_id)
                pickle.dump(new_data,storage)
                print("No data to load! Creating new file!")
                return
        if file.stat().st_size == 0 and not self.size_check:
            self.size_check = True
            self.save_changes()
            return
        
        if mode == "add":
            with open(file, 'ab') as storage:
                new_data = self.prepare_data("add",r_id)
                pickle.dump(new_data,storage)
        elif mode == "del":
            with open(file, 'wb') as storage:
                new_data = self.prepare_data("del",r_id)
                print(new_data)
                if r_id in new_data:
                    del new_data[r_id]
                    pickle.dump(new_data,storage)
                else:
                    print("ERROR!\nNo such record exists!")
        elif mode == "ed":
            with open(file, 'wb') as storage:
                new_data = self.prepare_data("del",r_id)
                pickle.dump(new_data,storage)
                self.size_check = False
        elif mode == "load":
            with open(file, 'rb') as storage:
                tmp_data = pickle.load(storage)
                # print(tmp_data)
                for ids,data in tmp_data.items():
                    if ids == 'Init_mem':
                        self.record_cnt = data['Record_cnt']
                        self.priority_ids = data['Priority_ids']
                    else:
                        self.data[data['Name']] = Record(data['Name'],data['Birthday'])
                        self.data[data['Name']].name.r_id = int(ids)
                        self.data[data['Name']].phones = data['Phone']
        # If mode == add, adding record to file (with correct id). If del, finding record by id and removing the line. With "ed", replacing the line/removing and adding a new one with the same id.

    def numeration(self,mode:str,record:Record):
        if mode == "add":
            new_id = None
            if len(self.priority_ids) > 0:
                new_id = self.priority_ids[0]
                print(new_id)
                del self.priority_ids[0]
            else:
                new_id = self.record_cnt
                self.record_cnt += 1
            
            record.name.r_id = new_id
            return record
        elif mode == "del":
            self.priority_ids.append(record.name.r_id)
        

    def iterator(self, num):
        counter = 0
        result = ""
        for item, record in self.data.items():
            result += f'{record}\n'
            counter += 1
            if counter >= num:
                yield result
                counter = 0
                result = ""

    def add_record(self,record:Record):
        if not record.name.value in self.data.keys():
            record = self.numeration("add",record)
            self.update_file("add",self.record_cnt)
            self.data[record.name.value] = record
            print(f"Record {record.name.value} with phone numbers {'; '.join(p.value for p in record.phones)} added!")
        else:
            print(f"This record already exists! Delete it first, then re-add.")
    
    def find(self,name:str):
        if name in self.data.keys():
            return self.data[name]
        else:
            print(f"Record {name} not found!")
            return None

    def delete(self,name:str):
        if name in self.data.keys():
            self.numeration("del",self.data[name])
            self.update_file("del",self.data[name].name.r_id)
            del self.data[name]
            print(f"Record {name} deleted!")
        else:
            print(f"Record {name} not found!")
            return None

# Створення нової адресної книги
book = AddressBook()


book.find_in_contacts("J")

# print(book.data)
# print(book.record_cnt)


# # Створення запису для John
# john_record = Record("John","12-08-2023")
# john_record.add_phone("1234567890")
# john_record.add_phone("5555555555")
# print(john_record.days_to_birthday())
# # Додавання запису John до адресної книги
# book.add_record(john_record)

# # Створення та додавання нового запису для Jane
# jane_record = Record("Jane")
# jane_record.add_phone("9876543210")
# book.add_record(jane_record)

# # Виведення всіх записів у книзі
# for name, record in book.data.items():
#     print(record)

# # Знаходження та редагування телефону для John
# john = book.find("John")
# jane = book.find("Jane")
# print(john.name.r_id)
# print(jane.name.r_id)
# john.edit_phone("1234567890", "1112223333")

# print(john)  # Виведення: Contact name: John, phones: 1112223333; 5555555555

# # Пошук конкретного телефону у записі John
# found_phone = john.find_phone("5555555555")
# print(f"{john.name}: {found_phone}")  # Виведення: 5555555555

# # for rec in book.iterator(2):
# #     print(rec)

# # book.update_file("ed",0)
# # import pickle
# # from pathlib import Path
# # file = Path("storage.bin")
# # with open(file, 'rb') as storage:
# #     tmp_data = pickle.load(storage)
# #     print(tmp_data)
# # print(book.data)
# # Видалення запису Jane
# book.save_changes()
# book.delete("Jane")