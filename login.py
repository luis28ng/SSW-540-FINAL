from tkinter import*
from PIL import ImageTk
from tkinter import messagebox
import sqlite3
import os
import email_pass
import smtplib
import time

class Login_System:
    def __init__(self,root):
        self.root = root
        self.root.title("Equipment Checkout System | Developed by Team Group 2 (SSW540 Fall 2022)")
        self.root.geometry("1350x700+0+0")
        self.root.config(bg="#0f4d7d")
        self.otp = ''


        #===============Images====================================

        #==== Not used any images.

        #===============Login Frame=========
        self.UserID = StringVar()
        self.password = StringVar()


        login_frame = Frame(self.root,bd=2,relief=RIDGE,bg="white")
        login_frame.place(x=500,y=90,width=350,height=460)

        title= Label(login_frame,text="Login Screen", font=("Elephant",30,"bold"),bg="white").place(x=0,y=30,relwidth=1)

        lbl_user = Label(login_frame,text="User ID",font=("Andalus",15),bg="white").place(x=50,y=100)

        txt_username = Entry(login_frame,textvariable=self.UserID,font=("times new roman",15),bg="#ECECEC").place(x=50,y=140,width=250)

        lbl_pass = Label(login_frame,text="Password",font=("Andalus",15),bg="white").place(x=50,y=190)
        txt_pass = Entry(login_frame,textvariable=self.password,show="*",font=("times new roman",15),bg="#ECECEC").place(x=50,y=230,width=250)

        btn_login = Button(login_frame,text="Log In",command=self.login,font=("Arial Rounded MT Bold",15),bg="#00B0F0",cursor="hand2").place(x=50,y=300,width=250,height=35)

        hr = Label(login_frame,bg="lightgray").place(x=50,y=370,width=250,height=2)
        or_ = Label(login_frame,text="OR",bg="white",fg="lightgray",font=("times new roman",15,"bold")).place(x=158,y=358)

        btn_forget = Button(login_frame,text="Forget Password?",command=self.forget_window,font=("times new roman",13),bg="white",fg="#00759E",cursor="hand2").place(x=110,y=390)

        
        #===============Frame 2=========
        #register_frame = Frame(self.root,bd=2,relief=RIDGE,bg="white")
        #register_frame.place(x=500,y=570,width=350,height=60)

        #lbl_reg = Label(register_frame,text="Don't have an account ? ",font=("times new roman",13),bg="white").place(x=70,y=15)
        #btn_signup = Button(register_frame,text="Sign Up",font=("times new roman",13),bg="white",fg="#00759E",cursor="hand2").place(x=210,y=12)

#====================Functions============================
    def login(self):
        con= sqlite3.connect(database=r'ems.db')
        cur = con.cursor()
        try:
            if self.UserID.get()=="" or self.password.get()=="":
                messagebox.showerror("Error","All fields are required",parent=self.root)
            else:
                cur.execute("select utype from suppliers where sid=? AND pass=? ",(self.UserID.get(),self.password.get()))
                user = cur.fetchone()
                if user == None:
                    messagebox.showerror("Error","Invalid User ID or Password",parent=self.root)
                else:
                    if user[0] == "Admin":
                        self.root.destroy()
                        os.system("python dashboard.py")
                    else:
                        self.root.destroy()
                        os.system("python checkingout.py")
        except Exception as ex:
            messagebox.showerror("Error",f"Error due to : {str(ex)}")
  
    def forget_window(self):
        con= sqlite3.connect(database=r'ems.db')
        cur = con.cursor()
        try:
            if self.UserID.get()=="":
                messagebox.showerror("Error","User ID is required",parent=self.root)
            else:
                cur.execute("select email from suppliers where sid=? ",(self.UserID.get(),))
                email = cur.fetchone()
                if email == None:
                    messagebox.showerror("Error","Invalid User ID",parent=self.root)
                else:
                    #===========Forget Window==============
                    self.var_otp = StringVar()
                    self.var_new_password= StringVar()
                    self.var_conf_password= StringVar()
                    #call send_email_function()
                    chk = self.send_email(email[0])
                    if chk!= 'f':
                        messagebox.showerror("Error","Connection Error, try again",parent = self.root)
                    else:
                        self.forget_win=Toplevel(self.root)
                        self.forget_win.title('RESET PASSWORD')
                        self.forget_win.geometry('400x350+500+100')
                        self.forget_win.focus_force()

                        title = Label(self.forget_win,text='Reset Password',font=("goudy old style",15,'bold'),bg="#3f51b5",fg="white").pack(side=TOP,fill=X)
                        lbl_reset = Label(self.forget_win,text="Enter OTP Sent on Registered Email",font=("times new roman",15)).place(x=20,y=60)
                        txt_reset = Entry(self.forget_win,textvariable=self.var_otp,font=("times new roman",15),bg='lightyellow').place(x=20,y=100,width=250,height=30)
                        self.btn_reset=Button(self.forget_win,text="SUBMIT",command=self.validate_otp,font=("times new roman",15),bg='lightblue',cursor="hand2")
                        self.btn_reset.place(x=280,y=100,width=100,height=30)

                        lbl_new_pass = Label(self.forget_win,text="New Password",font=("times new roman",15)).place(x=20,y=160)
                        txt_new_pass = Entry(self.forget_win,textvariable=self.var_new_password,font=("times new roman",15),bg='lightyellow').place(x=20,y=190,width=250,height=30)
                        
                        lbl_c_pass = Label(self.forget_win,text="Confirm Password",font=("times new roman",15)).place(x=20,y=225)
                        txt_c_pass = Entry(self.forget_win,textvariable=self.var_conf_password,font=("times new roman",15),bg='lightyellow').place(x=20,y=255,width=250,height=30)
                        
                        self.btn_update=Button(self.forget_win,text="Update",command=self.update_password,state=DISABLED,font=("times new roman",15),bg='lightblue',cursor="hand2")
                        self.btn_update.place(x=150,y=300,width=100,height=30)
        except Exception as ex:
            messagebox.showerror("Error",f"Error due to : {str(ex)}")

    def update_password(self):
        if self.var_new_password.get()=="" or self.var_conf_password.get()=="":
            messagebox.showerror("Error","All password fields are required",parent = self.forget_win)
        elif self.var_new_password.get()!=self.var_conf_password.get():
            messagebox.showerror("Error","Both new and confirmed password must be same",parent = self.forget_win)
        else:
            con= sqlite3.connect(database=r'ems.db')
            cur = con.cursor()
            try:
                cur.execute("Update suppliers set pass=? where sid=?",(self.var_new_password.get(),self.UserID.get()))
                con.commit()
                messagebox.showinfo("Success","Password updated successfully",parent = self.forget_win)
                self.forget_win.destroy()
            except Exception as ex:
                messagebox.showerror("Error",f"Error due to : {str(ex)}")


    def validate_otp(self):
        if int(self.otp)==int(self.var_otp.get()):
            self.btn_update.config(state=NORMAL)
            self.btn_reset.config(state=DISABLED)
        else:
            messagebox.showerror("Error","Invalid OTP, Try again",parent =self.forget_win )

    def send_email(self,to_):
        s=smtplib.SMTP('smtp.gmail.com',587)
        s.starttls()
        email_ = email_pass.email_
        pass_ = email_pass.pass_

        s.login(email_,pass_)

        self.otp= int(time.strftime("%H%M%S"))+int(time.strftime("%S"))
        subj='EMS-Reset Password OTP'
        msg=f'Dear Sir/Madam,\n\nYour Reset OTP is {str(self.otp)}.\n\nWith Regards, \nEMS Team'
        msg="Subject: {}\n\n{}".format(subj,msg)
        s.sendmail(email_,to_,msg)
        chk=s.ehlo()
        result = chk[0]
        if result == "250":
            return 's'
        else:
            return 'f'
        

if __name__=="__main__":
    con= sqlite3.connect(database=r'ems.db')
    cur = con.cursor()
    try:
        cur.execute("select * from suppliers")
        row = cur.fetchall()
        if len(row)==0:
            os.system("python newregistration.py")
            print(row)
        else:
            root = Tk()
            obj = Login_System(root)
            root.mainloop()
    except Exception as ex:
        messagebox.showerror("Error",f"Error due to : {str(ex)}")


