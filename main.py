import csv
import bcrypt
from abstracted_methods import *
from datetime import datetime
from flask import Flask, render_template, request, session, redirect, url_for
from db_module import Database
import math

app = Flask(__name__)

db = Database("db")

app.secret_key = "Bad Secret Key5"
#defining global character sets
upper_case_character_set = {
    'N', 'O', 'Z', 'I', 'F', 'J', 'L', 'M', 'K', 'C', 'P', 'V', 'S', 'X', 'R',
    'H', 'U', 'Y', 'B', 'A', 'W', 'T', 'E', 'G', 'Q', 'D'
}
lower_case_character_set = {
    'l', 'h', 'k', 'r', 'n', 's', 'v', 'q', 'j', 'u', 'a', 'z', 't', 'c', 'i',
    'f', 'w', 'x', 'm', 'y', 'p', 'o', 'g', 'b', 'e', 'd'
}
digit_character_set = {'1', '6', '4', '7', '8', '5', '2', '9', '3'}
special_character_set = {"!", "£", "$", "*", ".", "?", "@", ":", ";", "#"}


#quickly sign_out_user
def sign_out_user():
  session.pop("Username")
  session.pop("UserID")
  session.pop("UserType")
  session.pop("ParentId")


#quickly sign in user
def setup_session(Username, UserId, UserType, ParentId):
  session["Username"] = Username
  session["UserId"] = UserId
  session["UserType"] = UserType
  session["ParentId"] = ParentId


#remove a session
def remove_session():
  [session.pop(key) for key in list(session.keys()) if not key.staRtswith('_')]


#number of months elapsed
def months(lastApplied, currentDate):
  return currentDate.month - lastApplied.month + 12 * (currentDate.year -
                                                       lastApplied.year)


#number of days elapsed
def days(lastApplied, currentDate):
  return (currentDate - lastApplied).days


#updates interest
def update_interest_rate(UserId, user_type):

  if user_type == "Parent":
    #get accounts from accountData
    accounts = db.select("AccountData", ["id", "LastApplied", "Interest"],
                         [["UserId", "==", UserId]])
    for account in accounts:
      current_date = datetime.now()
      LastApplied = datetime.strptime(account[1], "%d/%m/%Y")
      months_elapsed = months(LastApplied, current_date)
      db.update("AccountData", ["LastApplied"],
                [current_date.strftime("%d/%m/%Y")],
                [["id", "==", account[0]]])
      if months_elapsed > 0:
        #time elapsed apply interest
        #get all children with money in the account
        children = db.select("ChildAccount", ["UserId", "Total", "id"],
                             [["AccountId", "==", account[0]]])
        for child in children:
          #create transaction and update total
          total_interest = child[1] * ((1 + child[2] / 100)**months_elapsed)
          new_id = db.MAX("Transactions", ["id"])[0] + 1
          notes = f"interest applied for {months_elapsed} months"
          db.insert("Transactions", [
              new_id, child[0], account[0], "transaction", "insertion",
              current_date.strftime("%d/%m/%Y"),
              round(total_interest - child[1], 2), notes
          ])
          db.update("ChildAccount", ["Total"], [round(total_interest, 2)],
                    [["id", "==", child[2]]])

  else:
    #get accounts from  ChildAccount
    Totals = db.select("ChildAccount", ["id", "AccountId", "Total"],
                       [["UserId", "==", session["UserId"]]])
    #check if each acocunt has elapsed
    for Total in Totals:
      #find how many months it has been
      account_data = db.select("AccountData", ["LastApplied", "Interest"],
                               [["id", "==", Total[1]]])[0]
      LastApplied = datetime.strptime(account_data[0], "%d/%m/%Y")
      current_date = datetime.now()
      months_elapsed = months(LastApplied, current_date)
      db.update("AccountData", ["LastApplied"],
                [current_date.strftime("%d/%m/%Y")], [["id", "==", Total[1]]])
      if months_elapsed > 0:
        #create transaction and update Total
        total_interest = Total[2] * (
            (1 + account_data[1] / 100)**months_elapsed)
        change = total_interest - Totals[2]
        new_id = db.MAX("Transactions", ["id"])[0] + 1
        notes = f"interest applied for {months_elapsed} months"
        db.insert("Transactions", [
            new_id, session["UserId"], Total[1], "transaction", "insertion",
            current_date.strftime("%d/%m/%Y"),
            round(change, 2), notes
        ])
        db.update("ChildAccount", ["Total"], [round(total_interest, 2)],
                  [["id", "==", Total[0]]])
  db.commit()


#to prevent code duplication
def update_payments_child(UserId):
  #pull directly from PaymentTable
  print("=====updating=======")
  payments = db.select(
      "Payment",
      ["id", "AccountId", "Amount", "Frequency", "Notes", "LastApplied"],
      [["UserId", "==", UserId]])
  for payment in payments:
    current_date = datetime.now()
    days_elapsed = days(datetime.strptime(payment[5], "%d/%m/%Y"),
                        current_date)
    print("====days====")
    print(days_elapsed)
    if days_elapsed >= payment[3]:
      #payment has elapsed, calculate how many where missed
      times_missed = math.floor(days_elapsed / payment[3])
      total = times_missed * payment[2]
      #now update last applied and create request
      db.update("Payment", ["LastApplied"],
                [current_date.strftime("%d/%m/%Y")],
                [["id", "==", payment[0]]])
      new_id = db.MAX("Transactions", ["id"])[0]
      notes = payment[4] + f"appllied {times_missed} times"
      db.insert("Transactions", [
          new_id, UserId, payment[1], "transaction", "insertion",
          current_date.strftime("%d/%m/%Y"),
          round(total, 2), notes
      ])
      #update child total aswell
      curr_total = db.TOTAL("ChildAccount", ["Total"],
                            [["UserId", "==", UserId], "AND",
                             ["AccountId", "==", payment[1]]])[0]
      db.update(
          "ChildAccount", ["Total"], [round(curr_total + total, 2)],
          [["UserId", "==", UserId], "AND", ["AccountId", "==", payment[1]]])
      db.commit()  #


#update recurring payments
#currently only supports insertino
def update_payments(UserId, user_type):

  if user_type == "Parent":
    #either pull all children or pull accounts
    children = db.select(
        "UserData", ["id"],
        [["type", "==", "Child"], "AND", ["ParentId", "==", UserId]])
    for child in children:
      update_payments_child(child[0])
  else:
    update_payments_child(UserId)


def validate_action(UserId, AccountId, Type, Status, Amount, Notes):
  valid_sender = db.select("UserData", [], [["id", "==", UserId]])
  valid_AccountId = db.select("UserData", [], [["id", "==", AccountId]])
  if valid_sender == [] or valid_AccountId == []:
    return {"status": "error", "message": "sender and/or dest do not exist"}
  #do type and status look up
  Type_Check = {"request", "transaction", "insertion"}
  Status_Check = {"pending", "denied", "paid"}
  if Type not in Type_Check or Status not in Status_Check:
    return {"status": "error", "message": "invalid status and/or type"}
  #check amount
  try:
    float(Amount)
  except TypeError:
    return {"status": "error", "message": "amount is not a float"}
  if Amount <= 0:
    return {
        "status": "error",
        "message": "amount cannot be less than or equal to 0"
    }
  #round amount
  Amount = round(Amount, 2)
  #validate notes
  if len(Notes.strip()) == 0:
    return {"status": "error", "message": "Notes cannot be left blank"}
  if len(Notes) > 200:
    return {
        "status": "error",
        "message": "Notes cannot be longer than 200 characters"
    }
  return {"status": "done"}


#create a new action in the transaction table
def add_action(UserId, AccountId, Type, Status, Amount, Notes):
  status = validate_action(UserId, AccountId, Type, Status, Amount, Notes)
  if status["status"] == "error":
    return status
  new_id = db.MAX("Transactions", ["id"])[0] + 1
  date = datetime.now().strftime("%d/%m/%Y")
  db.insert("Transactions",
            [new_id, UserId, AccountId, Type, Status, date, Amount, Notes])
  db.commit()


#self explanatory hashh a plaintext password
def hash_password(inputStr, salt):
  return bcrypt.hashpw(inputStr.encode('utf-8'), salt)


def validate_authentication_data(username, password):
  #first check for whitespace in the password

  if password.find(" ") != -1 or password == "":
    #return an error code
    return {"status": "error", "message": "password cannot contain whitespace"}
  #check if username is only whitespace
  character_set = set(username.split())
  if len(username.strip()) == 0:
    return {"status": "error", "message": "username cannot only be whitespace"}
  #create a username character set
  username_character_set = digit_character_set.union(lower_case_character_set)
  username_character_set.update(upper_case_character_set)
  username_character_set.update({" "})

  if CharacterSetCheck(username, username_character_set) == False:
    return {
        "status": "error",
        "message":
        "username can only contain alphabetical characters and digits"
    }
  #change to a password character_set
  password_character_set = username_character_set
  password_character_set.update(special_character_set)
  if CharacterSetCheck(password, password_character_set) == False:
    #invalid character detected
    return {
        "status": "error",
        "message": "password contains invalid characters"
    }
  #check length of the password and username
  if len(password) < 8:
    return {
        "status": "error",
        "message": "password must have 8 or more characters"
    }
  if len(username) > 40:
    return {
        "status": "error",
        "message": "username must be 40 or less characters"
    }
  return {"status": "valid"}


def create_new_user(username, password, type="Parent", parent_id=0):
  status = validate_authentication_data(username, password)
  if status["status"] == "error":
    return status
  #check if user already exists
  result = db.select("UserData", ["id", "HashedPassword", "Salt", "ParentId"],
                     [["Username", "==", username]])
  if result != []:
    return {"status": "error", "message": "username already in use"}

  #now get new id
  new_id = db.MAX("UserData", ["id"])[0] + 1
  salt = bcrypt.gensalt()
  hashed = hash_password(password, salt).decode('utf-8')
  date = datetime.now().strftime("%d/%m/%Y")
  #attempt to create new user whilst catching errors
  try:
    db.insert("UserData", [
        new_id, username, date, hashed,
        salt.decode('utf-8'), type, parent_id, 0.0
    ])
  except:
    return {
        "status": "error",
        "message": "error when creating account please try again later"
    }
  db.commit()

  returndata = {
      "status": "valid",
      "userData": {
          "Username": username,
          "UserId": new_id,
          "UserType": type,
      }
  }

  if type == "Parent":
    returndata["userData"]["ParentId"] = 0
  else:
    returndata["userData"]["ParentId"] = session["UserId"]

  return returndata


#validate user when they attempt to login
def authenticate_user(username, password):

  #now check if a user exists in the table
  result = db.select("UserData",
                     ["id", "HashedPassword", "Salt", "type", "ParentId"],
                     [["Username", "==", username]])
  if result == []:
    return {"status": "error", "message": "username cannot be found"}
  #user exists
  hashed = hash_password(password, result[0][2].encode('utf-8'))

  if hashed != result[0][1].encode("utf-8"):
    return {"status": "error", "message": "invalid password"}

  return {
      "status": "valid",
      "userData": {
          "Username": username,
          "UserId": result[0][0],
          "UserType": result[0][3],
          "ParentId": result[0][4]
      }
  }


@app.route("/")
def main():
  print("doing smth")
  if "UserId" in session:
    data = {}
    #get all accounts associated with this parent
    accounts = db.select("AccountData", ["id"],
                         [["UserId", "==", session["UserId"]]])
    #construct the where condition
    conditions = []
    for account in accounts:
      conditions.append(["AccountId", "==", account[0]])
      conditions.append("AND")

    if session["UserType"] == "Parent":
      #return the Total from all pending transactions
      data["owed"] = round(
          db.TOTAL(
              "Transactions", ["Amount"],
              conditions + [["Type", "==", "transaction"], "AND",
                            ["Status", "==", "pending"]])[0], 2)
    else:
      #return the childs Total owed,pending and total-previous 2
      data["owed"] = round(
          db.TOTAL("Transactions", ["Amount"],
                   [["UserId", "==", session["UserId"]], "AND",
                    ["Type", "==", "transaction"], "AND",
                    ["Status", "==", "pending"]])[0], 2)
      data["pending"] = round(
          db.TOTAL("Transactions", ["Amount"],
                   [["UserId", "==", session["UserId"]], "AND",
                    ["Type", "==", "request"], "AND",
                    ["Status", "==", "pending"]])[0], 2)
      data["total"] = db.TOTAL("ChildAccount", ["Total"],
                               [["UserId", "==", session["UserId"]]
                                ])[0] - data["pending"] - data["owed"]

    return render_template("main.html",
                           user_type=session["UserType"],
                           data=data)
  else:
    return redirect(url_for("authenticate_user_route"))


#used to login user
@app.route("/authenticate_user", methods=["GET", "POST"])
def authenticate_user_route():
  if "Username" in session:
    return redirect(url_for("main"))

  if request.method == "GET":
    return render_template("authenticate_users.html", err="")

  #retrieve form data
  username = request.form["username"]
  password = request.form["password"]
  status = None
  #check if it is login or sig  up
  if request.form["type"] == "login":
    status = authenticate_user(username, password)
  else:
    status = create_new_user(username, password)
  #only run if valid
  if status["status"] == "valid":
    setup_session(status["userData"]["Username"], status["userData"]["UserId"],
                  status["userData"]["UserType"],
                  status["userData"]["ParentId"])
  else:
    #return error message
    return render_template("authenticate_users.html", err=status["message"])
  return redirect(url_for("main"))


#create a new child account
@app.route("/conceive_child", methods=["GET", "POST"])
def conceive_child():
  #make sure user can accses page
  if "Username" not in session:
    return {"error": "invalid session"}
  if session["UserType"] != "Parent":
    return "error: you do not have permissions to access this page"
  #check if post or get
  if request.method == "POST":
    err = ""
    #want to add a new child
    #first i want to validate the child data
    status = validate_authentication_data(request.form["username"],
                                          request.form["password"])
    if status["status"] != "valid":
      return render_template("conceive_child.html", err=status["message"])
    #data is valid create new user
    status = create_new_user(request.form["username"],
                             request.form["password"],
                             type="Child",
                             parent_id=session["UserId"])
    #handle errors
    if status["status"] == "error":
      return render_template("conceive_child.html", err=status["message"])

    return redirect(url_for("manage"))
  return render_template("conceive_child.html", err="")


#the event handler for creating transactions
@app.route("/append_transactions", methods=["POST"])
def append_transactions():
  if "Username" not in session:
    return {"error": "invalid session"}

  #TODO add more comments
  #set row values
  amount = request.form["amount"]
  notes = request.form["notes"]

  date = datetime.now().strftime("%d/%m/%Y")
  type = ""
  status = ""
  AccountId = 0
  UserId = 0  #will always be the child
  AccountId = int(request.form["account_id"])
  if session["UserType"] == "Parent":
    #this is an insertion
    type = "transaction"
    status = "insertion"
    UserId = int(request.form["child_id"])

    #first i check if child has any records with this account
    records_exist = db.select(
        "ChildAccount", [],
        [["AccountId", "==", AccountId], "AND", ["UserId", "==", UserId]])
    if records_exist:
      #record exists safe to update
      curr_total = db.TOTAL(
          "ChildAccount", ["Total"],
          [["AccountId", "==", AccountId], "AND", ["UserId", "==", UserId]])[0]

      db.update(
          "ChildAccount", ["Total"], [curr_total + float(amount)],
          [["UserId", "==", UserId], "AND", ["AccountId", "==", AccountId]])
    else:

      new_id = db.MAX("ChildAccount", ["id"])[0] + 1
      db.insert("ChildAccount",
                [new_id, UserId, AccountId,
                 round(float(amount), 2)])
    db.commit()
  else:
    #this is a request

    curr_total = db.TOTAL("ChildAccount", ["Total"],
                          [["AccountId", "==", AccountId], "AND",
                           ["UserId", "==", session["UserId"]]])[0]
    #how much they have in pending transactions and requests so i can remove it from total
    to_remove = db.TOTAL(
        "Transactions", ["Amount"],
        [["UserId", "==", session["UserId"]], "AND",
         ["AccountId", "==", AccountId], "AND",
         ["Status", "!=", "denied"], "AND", ["Status", "!=", "paid"], "AND",
         ["Status", "!=", "insertion"]])[0]
    #relative total in acocunt e.g do they have enough funds
    if curr_total - to_remove < float(amount):
      return f"error:not enough funds to request {amount}"
    type = "request"
    status = "pending"
    UserId = session["UserId"]
  try:
    float(amount)
  except:
    return "amount must be a numerical value"
  if float(amount) <= 0:
    return "amount must be greatear than 0"
  #record does not exists create new one
  #create action with data
  new_id = db.MAX("Transactions", ["id"])[0] + 1
  db.insert("Transactions", [
      new_id, UserId, AccountId, type, status, date,
      round(float(amount), 2), notes
  ])
  db.commit()
  return redirect(url_for("view_actions"))


#change status of pending request to pending transaction
@app.route("/accept_request", methods=["POST"])
def accept_request():
  if "Username" not in session:
    return {"error": "invalid session"}
  if session["UserType"] != "Parent":
    return "you do not have permision to accses this page"
  conditions = db.select("Transactions", ["Type", "Status"],
                         [["id", "==", request.form["id"]]])[0]
  if conditions[1] != "pending" or conditions[0] != "request":
    return "invalid request"
  #valid to change
  #pending request goes to pending transaction so only update the Type
  db.update("Transactions", ["Type"], ["transaction"],
            [["id", "==", request.form["id"]]])

  db.commit()
  return redirect(url_for("view_actions"))


#to deny pending requests
@app.route("/deny_request", methods=["POST"])
def deny_request():

  if "Username" not in session:
    return {"error": "invalid session"}
  if session["UserType"] != "Parent":
    return "invalid permisions"
  #user has valid permisions now update table
  db.update("Transactions", ["Status"], ["denied"],
            [["id", "==", request.form["id"]]])
  db.commit()
  return redirect(url_for("view_actions"))


#user wants to mark pending transaction as paid
@app.route("/pay_pending", methods=["POST"])
def pay_pending():

  #remember to subtract amount from total
  if "Username" not in session:
    return {"error": "invalid session"}
  if session["UserType"] != "Parent":
    return "you do not have permision to accses this page"
  conditions = db.select("Transactions",
                         ["Type", "Status", "Amount", "UserId", "AccountId"],
                         [["id", "==", request.form["id"]]])[0]
  if conditions[1] != "pending" or conditions[0] != "transaction":
    return "invalid request"
  #update amount
  curr_total = db.TOTAL("ChildAccount", ["Total"],
                        [["AccountId", "==", conditions[4]], "AND",
                         ["UserId", "==", conditions[3]]])[0]

  #update childs total
  db.update("ChildAccount", ["Total"], [round(curr_total - conditions[2], 2)],
            [["AccountId", "==", conditions[4]], "AND",
             ["UserId", "==", conditions[3]]])
  #updatae transaction status
  db.update("Transactions", ["Status"], ["paid"],
            [["id", "==", request.form["id"]]])
  db.commit()
  return redirect(url_for("view_actions"))


#used to edit already existing requests
@app.route("/edit_request", methods=["POST"])
def edit_request():
  if "Username" not in session:
    return {"error": "invalid session"}
  #get relevant data for update
  amount = request.form["amount"]
  notes = request.form["notes"]
  account_id = int(request.form["account_id"])
  date = datetime.now().strftime("%d/%m/%Y")
  curr_total = db.TOTAL("ChildAccount", ["Total"],
                        [["AccountId", "==", account_id], "AND",
                         ["UserId", "==", session["UserId"]]])[0]
  #check if the "new total" is also valid
  to_remove = db.TOTAL(
      "Transactions", ["Amount"],
      [["UserId", "==", session["UserId"]], "AND", ["Status", "!=", "denied"],
       "AND", ["Status", "!=", "paid"], "AND", ["Status", "!=", "insertion"],
       "AND", ["id", "!=", request.form["request_id"]], "AND",
       ["AccountId", "==", account_id]])[0]
  if curr_total - to_remove < float(amount):
    return {"error": f"not enough funds to request {amount}"}
  #update request

  db.update("Transactions", ["Amount", "Notes", "Date", "AccountId"],
            [round(float(amount), 2), notes, date, account_id],
            [["id", "==", request.form["request_id"]]])
  db.commit()
  return redirect(url_for("view_actions"))


#returns the web page to display all the actions
@app.route("/view_actions", methods=["GET"])
def view_actions():

  if "UserId" not in session:
    return {"error": "invalid session"}
  update_interest_rate(session["UserId"], session["UserType"])
  update_payments(session["UserId"], session["UserType"])
  actions = {"requests": [], "transactions": []}
  children_id_to_name_dic = {}
  account_id_to_name_dic = {}
  parent_name = None
  #if parent pull all children associated with them
  if session["UserType"] == "Parent":
    parent_name = session["Username"]
    all_children = db.select("UserData", ["id", "Username"],
                             [["type", "==", "Child"], "AND",
                              ["ParentId", "==", session["UserId"]]])
    all_accounts = db.select("AccountData", ["id", "AccountName"],
                             [["UserId", "==", session["UserId"]]])

    #for each child pull the transactions associated with them
    #also turn all accounts and children into (id,name) key,val pair dictionaries
    for child in all_children:
      children_id_to_name_dic[child[0]] = child[1]
      actions["requests"] += db.select(
          "Transactions", [],
          [["UserId", "==", child[0]], "AND", ["Type", "==", "request"]])
      #replace UserId and AccountId with their respective names
      actions["transactions"] += db.select(
          "Transactions", [],
          [["UserId", "==", child[0]], "AND", ["Type", "==", "transaction"]])

    for account in all_accounts:
      account_id_to_name_dic[account[0]] = account[1]
  else:
    #pull all accounts and transactions associated with this child
    parent_name = db.select("UserData", ["Username"],
                            [["id", "==", session["ParentId"]]])[0][0]
    #put child details in (key,val) pair format
    children_id_to_name_dic[session["UserId"]] = session["Username"]
    #also put accounts in (key,val) pair format
    accounts = db.select("ChildAccount", ["AccountId"],
                         [["UserId", "==", session["UserId"]]])
    #pull the name of each account
    for account in accounts:
      account_id_to_name_dic[account[0]] = db.select(
          "AccountData", ["AccountName"], [["id", "==", account[0]]])[0][0]
    #pull all transactoins
    actions["requests"] = db.select("Transactions", [],
                                    [["UserId", "==", session["UserId"]],
                                     "AND", ["Type", "==", "request"]])
    actions["transactions"] = db.select("Transactions", [],
                                        [["UserId", "==", session["UserId"]],
                                         "AND", ["Type", "==", "transaction"]])

  return render_template("view_actions.html",
                         user_type=session["UserType"],
                         actions=actions,
                         children=children_id_to_name_dic,
                         parent=parent_name,
                         accounts=account_id_to_name_dic)


#displays the users settings/details
@app.route("/settings", methods=["GET", "POST"])
def settings():
  if "Username" not in session:
    return {"error": "invalid sesssion"}
  #retreive their details(slightly different for parent and child)
  user_details = [session["Username"]] + db.select(
      "UserData", ["Date"], [["id", "==", session["UserId"]]])[0]
  if session["UserType"] == "Child":
    user_details += db.select("UserData", ["Username"],
                              [["id", "==", session["ParentId"]]])[0]
    user_details += db.TOTAL("ChildAccount", ["Total"],
                             [["UserId", "==", session["UserId"]]])

  return render_template("settings.html", user_details=user_details)


#event handler for changing the users password
@app.route("/change_password", methods=["POST"])
def change_password():
  #make sure the 2 passwords match
  if request.form["p1"] != request.form["p2"]:
    return {"error": "inputed passwords do not match"}
  #validate the users new password
  status = validate_authentication_data(session["Username"],
                                        request.form["p1"])
  if status["status"] == "error":
    return status["message"]
  #hash new password
  salt = bcrypt.gensalt()
  hashed = hash_password(request.form["p1"], salt).decode('utf-8')
  #update details
  db.update("UserData", ["HashedPassword", "Salt"], [
      hashed,
      salt.decode('utf-8'),
  ], [["id", "==", session["UserId"]]])
  db.commit()
  return redirect(url_for("settings"))


#for changing the users details(so far only name)
@app.route("/change_details", methods=["POST"])
def change_details():
  #validate new username using a placeholder password
  status = validate_authentication_data(request.form["username"],
                                        "temppassword123")
  if status["status"] == "error":
    return status["message"]
  #update db

  db.update("UserData", ["Username"], [request.form["username"]],
            [["id", "==", session["UserId"]]])
  #update session
  session["Username"] = request.form["username"]
  db.commit()
  return redirect(url_for("settings"))


#returns page that displays accounts,payments and for parents children
@app.route("/manage", methods=["GET"])
def manage():
  update_interest_rate(session["UserId"], session["UserType"])
  update_payments(session["UserId"], session["UserType"])
  #TODO add more comments
  if "Username" not in session:
    return {"error": "invalid permission"}
  #first i want to pull child data
  data = {}
  data["payment"] = []
  if session["UserType"] == "Parent":
    #TODO?test
    #TODO Change html and js code
    #grab all children associated with this parent
    data["children"] = db.select("UserData", ["id", "Username", "Date"],
                                 [["ParentId", "==", session["UserId"]], "AND",
                                  ["type", "==", "Child"]])
    parent_name = session["Username"]
    #update child data to be more usefull
    #also grab any payments the child may have
    final_children = []
    for child in data["children"]:
      #turn into dictionary for easier accses
      child = {"id": child[0], "Username": child[1], "Date": child[2]}
      #grab Total accross all accounts
      total = round(
          db.TOTAL("ChildAccount", ["Total"],
                   [["UserId", "==", child["id"]]])[0], 2)
      child["Total"] = total
      child["Parent"] = parent_name
      child_accounts = db.select("ChildAccount", ["AccountId", "Total"],
                                 [["UserId", "==", child["id"]]])
      #replace all account id's with account names
      for account in child_accounts:
        account[0] = db.select("AccountData", ["AccountName"],
                               [["id", "==", account[0]]])
      child["Accounts"] = child_accounts
      final_children.append(child)
      #get payment data
      payments = db.select("Payment", [], [["UserId", "==", child["id"]]])
      for payment in payments:
        username = db.select("UserData", ["Username"],
                             [["id", "==", child["id"]]])[0][0]

        account_name = db.select("AccountData", ["AccountName"],
                                 [["id", "==", payment[3]]])[0][0]
        payment[2] = username
        payment[3] = account_name

      data["payment"] += payments
    data["children"] = final_children
  else:
    #just so the key exists
    data["children"] = [[]]
  #then account data
  #grab correct id
  id = 0
  id = session["ParentId"] if session["UserType"] == "Child" else session[
      "UserId"]
  data["accounts"] = db.select(
      "AccountData",
      ["id", "UserId", "AccountName", "Date", "Notes", "Interest"],
      [["UserId", "==", id]])
  #and now payment data

  if session["UserType"] == "Child":
    #grab all payments
    data["payment"] = db.select("Payment", [],
                                [["UserId", "==", session["UserId"]]])
    print(data)
    #loop through payments and replace user id and acocunt id with names
    for payment in data["payment"]:
      username = db.select("UserData", ["Username"],
                           [["id", "==", session["UserId"]]])[0][0]
      account_name = db.select("AccountData", ["AccountName"],
                               [["id", "==", payment[3]]])[0][0]
      payment[2] = username
      payment[3] = account_name
  #replace Account Id and UserID with the names
  #also add an account total for each account
  #for each account also grab each child
  print(id)
  for account in data["accounts"]:

    username = db.select("UserData", ["Username"], [["id", "==", id]])[0][0]
    account[1] = username
    account_total = round(
        db.TOTAL("ChildAccount", ["Total"],
                 [["AccountId", "==", account[0]]])[0], 2)
    account.append(account_total)
    children_id = db.select("ChildAccount", ["UserId"],
                            [["AccountId", "==", account[0]]])
    children = []
    #replace the id with username
    for child_id in children_id:
      children.append(
          db.select("UserData", ["Username"],
                    [["id", "==", child_id[0]]])[0][0])
    print(children)
    print("====")
    account.append(children)

  return render_template("manage.html", data=data)


#validate details for a new account
def authenticate_account_details(name, notes, interest):
  character_set = set(name.split())
  if len(name.strip()) == 0:
    return {"status": "error", "message": "username cannot only be whitespace"}
  #create a name character set
  name_character_set = digit_character_set.union(lower_case_character_set)
  name_character_set.update(upper_case_character_set)
  name_character_set.update({" "})

  #VALIDATE data using character set
  if CharacterSetCheck(name, name_character_set) == False:
    return {
        "status": "error",
        "message": "name can only contain alphabetical characters and digits"
    }
  try:
    float(interest)
  except:
    return {"status": "error", "message": "interest can only be numerical"}
  if float(interest) <= 0:
    return {
        "status": "error",
        "message": "interst must be greater than or equal to 0"
    }
  if len(name) > 40:
    return {
        "status": "error",
        "message": "name cannot be longer than 40 characters"
    }
  if notes.find(",") != -1:
    return {"status": "error", "message": "notes cannot contain comma"}
  if len(notes) == 0:
    return {"status": "error", "message": "notes cannot be left blank"}

  if len(notes) > 200:
    return {
        "status": "error",
        "message": "notes can be no longer than 200 characters"
    }
  return {"status": "done", "message": "done"}


@app.route("/create_account", methods=["GET", "POST"])
def create_account():

  if request.method == "POST":

    name = request.form["accountName"]
    notes = request.form["accountNotes"]
    interest = request.form["accountInterest"]
    status = authenticate_account_details(name, notes, interest)
    if status["status"] == "error":
      return status["message"]
    #get current date
    date = datetime.now().strftime("%d/%m/%Y")
    #get id
    id = db.MAX("AccountData", ["id"])[0] + 1
    LastApplied = date
    db.insert("AccountData", [
        id, session["UserId"], name, date, notes,
        float(interest), LastApplied
    ])
    db.commit()
    return redirect(url_for("manage"))
  return render_template("create_account.html")


@app.route("/manage_account", methods=["GET", "POST"])
def manage_account():
  update_interest_rate(session["UserId"], session["UserType"])
  if "Username" not in session:
    return {"error": "invalid session"}
  if session["UserType"] != "Parent":
    return {"error": "invalid permisions"}
  #get the id so i can pull data from db
  print("TESTING THIS FUNCTION")
  id = request.args.get(
      'id') if request.method == "GET" else request.form["id"]
  print("TESTING THIS FUNCTION")
  if id is None:
    return {"error": "invalid id"}
  if request.method == "POST":
    #user made changes save changes

    new_name = request.form["name"]
    new_notes = request.form["notes"]
    status = authenticate_account_details(new_name, new_notes, 0)
    if status["status"] == "error":
      return status["message"]
    db.update("AccountData", ["AccountName", "Notes"], [new_name, new_notes],
              [["id", "==", int(id)]])
    db.commit()
  data = db.select("AccountData", [], [["id", "==", int(id)]])[0]

  data[1] = db.select("UserData", ["Username"], [["id", "==", data[1]]])[0][0]
  #grabs children that have money in the account

  children = db.select("ChildAccount", ["UserId", "Total"],
                       [["AccountId", "==", int(id)]])

  #get username aswell

  for child in children:

    child += db.select("UserData", ["Username", "Date"],
                       [["id", "==", child[0]]])[0]

  #grab all of the parents children
  all_children = db.select("UserData", ["id", "Username"],
                           [["ParentId", "==", session["UserId"]]])

  account_total = round(
      db.TOTAL("ChildAccount", ["Total"], [["AccountId", "==", id]])[0], 2)
  print(children)
  account_details = {
      "data": data,
      "children": children,
      "total": account_total,
      "all_children": all_children,
  }

  return render_template("manage_account.html",
                         account_details=account_details)


@app.route("/create_payment", methods=["GET", "POST"])
def create_payment():
  if "Username" not in session:
    return {"error": "invalid session"}
  if session["UserType"] != "Parent":
    return {"error": "invalid permisions"}
  if request.method == "POST":
    #create_new_payment

    #validate data
    try:
      float(request.form["amount"])
      int(request.form["frequency"])
    except:
      return {"error": "frequency and amount must be int and float"}
    if len(request.form["notes"]) > 200:
      return {"error": "notes cannot be longer than 200 characters"}

    LastApplied = datetime.now().strftime("%d/%m/%Y")
    new_id = db.MAX("Payment", ["id"])[0]
    db.insert("Payment", [
        new_id, request.form["paymentName"],
        int(request.form["childId"]),
        int(request.form["accountId"]),
        round(float(request.form["amount"]), 2),
        int(request.form["frequency"]), request.form["notes"], "insertion",
        LastApplied
    ])
    db.commit()
    return redirect(url_for("manage"))
  #retreive all children and accounts
  children = db.select(
      "UserData", ["id", "Username"],
      [["type", "==", "Child"], "AND", ["ParentId", "==", session["UserId"]]])
  accounts = db.select("AccountData", ["id", "AccountName"],
                       [["UserId", "==", session["UserId"]]])
  return render_template("create_payment.html",
                         accounts=accounts,
                         children=children)


@app.after_request
def after_request(response):
  response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
  return response


if __name__ == '__main__':
  db.setup_from_csv("schema")
  print("=========DB SETUP===========")
  #print("=========Create User Test=========")
  #username = "Oliver"
  #password = "password"
  #print(
  #    f"attempting to create account using username: {username} and a password of {password}"
  #)
  #print(create_new_user(username, password))
  #print("=========Testing Login=========")
  #username = "Oliver"
  #password = "password"
  #print(
  #    f"attempting to login using username:{username} and a password of {password}"
  #)
  #print(authenticate_user(username, password))

  print("===========Running Server==========")
  #app.run(host='0.0.0.0')
