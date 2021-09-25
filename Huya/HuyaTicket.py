import requests, hashlib, json
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad
from Crypto.Util.Padding import unpad
from tkinter import * 
import tkinter.font as tkFont
from tkinter import ttk


def md5(raw):
    m = hashlib.md5()
    m.update(raw)
    mpwd = m.hexdigest()
    return mpwd

class TicketServer(object):
    def __init__(self):
        self.s = requests.session()
        self.url = 'https://www.sakuyo.cn/backend/huya/admin.php'
        self.headers = {
            'Content-Type': 'application/json'
        }
        self.token = ''
        self.user_list = []

    def bindUI(self, uiObj):
        self.UI = uiObj

    def launch(self):
        res = self.checkToken()

    def login(self, account, psw):
        psw_md5 = md5(psw.encode('utf-8'))
        data = {'flag':'admin-login', 'account':account, 'psw':psw_md5}
        data_json = json.dumps(data)
        res = self.s.post(self.url, data = data_json, headers=self.headers)
        content = json.loads(res.text)
        if content['code'] == 200:
            self.token = content['msg']
            token = pad(self.token.encode('utf-8'), 64, style='pkcs7')
            obj = AES.new(b'SakuyoAESKeySets', AES.MODE_CBC, b'HuyaKeySakuyoSet')
            token_raw = obj.encrypt(token)
            with open("./token", 'wb') as f:
                f.write(token_raw)
            self.UI.MainUI()

    def register(self, account, psw):
        psw_md5 = md5(psw.encode('utf-8'))
        data = {'flag':'admin-register', 'account':account, 'psw':psw_md5}
        data_json = json.dumps(data)
        res = self.s.post(self.url, data = data_json, headers=self.headers)
        content = json.loads(res.text)
        if content['code'] == 200:
            self.token = content['msg']
            token = pad(self.token.encode('utf-8'), 64, style='pkcs7')
            obj = AES.new(b'SakuyoAESKeySets', AES.MODE_CBC, b'HuyaKeySakuyoSet')
            token_raw = obj.encrypt(token)
            with open("./token", 'wb') as f:
                f.write(token_raw)
            self.UI.MainUI()

    def getUserList(self):
        data = {'flag':'get-user', 'token':self.token}
        data_json = json.dumps(data)
        res = self.s.post(self.url, data = data_json, headers=self.headers)
        content = json.loads(res.text)
        if content['code'] == 200:
            if content['msg'] == False:
                self.user_list = []
            else:
                self.user_list = json.loads(content['msg'])
            
            self.UI.UpdateUserList(self.user_list)

    def checkToken(self):
        try:
            with open("./token", 'rb') as f:
                token_raw = f.read()
            obj = AES.new(b'SakuyoAESKeySets', AES.MODE_CBC, b'HuyaKeySakuyoSet')
            token = obj.decrypt(token_raw)
            self.token = unpad(token, 64).decode()
            data = {'flag':'admin-login', 'token':self.token}
            data_json = json.dumps(data)
            res = self.s.post(self.url, data = data_json, headers=self.headers)
            content = json.loads(res.text)
            if content['code'] == 200:
                self.UI.MainUI()
            elif content['code'] == 503:
                raise Exception('Token Timeout!')
        except Exception as e:
            print(str(e))
            self.UI.LoginUI()

    def editUser(self, mac, description='', is_active=''):
        data = {'flag':'edit-user', 'token':self.token, 'mac':mac, 'description':description, 'is_active':is_active}
        data_json = json.dumps(data)
        res = self.s.post(self.url, data = data_json, headers=self.headers)
        content = json.loads(res.text)
        if content['code'] == 200:
            self.getUserList()
    
    def addUser(self, mac, description):
        data = {'flag':'add-user', 'token':self.token, 'mac':mac, 'description':description}
        data_json = json.dumps(data)
        res = self.s.post(self.url, data = data_json, headers=self.headers)
        content = json.loads(res.text)
        if content['code'] == 200:
            self.getUserList()

    def deleteUser(self, mac):
        data = {'flag':'delete-user', 'token':self.token, 'mac':mac}
        data_json = json.dumps(data)
        res = self.s.post(self.url, data = data_json, headers=self.headers)
        content = json.loads(res.text)
        if content['code'] == 200:
            self.getUserList()


    

class UI(object):
    def __init__(self, obj):
        self.obj = obj
        self.loginWindow = None

    def FormatWindow(self, obj, w=1500, h=1200):
        sw = obj.winfo_screenwidth()
        sh = obj.winfo_screenheight()
        x = (sw - w) / 2
        y = (sh - h) / 2
        obj.geometry("%dx%d+%d+%d" % (w, h, x, y))

    def selectItem(self, row, col):
        curItem = self.tree.item(row)
        print ('curItem = ', curItem)

        if col == '#0':
            cell_value = curItem['text']
        elif col == '#1':
            cell_value = curItem['values'][0]
        elif col == '#2':
            cell_value = curItem['values'][1]
        elif col == '#3':
            cell_value = curItem['values'][2]
        print ('cell_value = ', cell_value)
        return cell_value

    def MainUI(self):
        if self.loginWindow == None:
            pass
        else:
            self.loginWindow.destroy()
        self.mainWindow = Tk()
        self.mainWindow.title('控制台')
        # w = 1500
        # h = 1200
        # sw = self.mainWindow.winfo_screenwidth()
        # sh = self.mainWindow.winfo_screenheight()
        # x = (sw - w) / 2
        # y = (sh - h) / 2
        # self.mainWindow.geometry("%dx%d+%d+%d" % (w, h, x, y))
        self.FormatWindow(self.mainWindow, 550, 800)
        # User List Tree
        height = 18
        width = 150
        columns = ('Mac', '备注', '状态')
        self.tree = ttk.Treeview(self.mainWindow, height=height, show="headings", columns=columns)

        for item in columns:
            self.tree.column(item, width=width, anchor='center')
            self.tree.heading(item, text=item)
        
        self.tree.pack(side=LEFT, fill=BOTH)

        def SetCell(event): # 双击进入编辑状态
            if len(self.tree.get_children()) > 0:
                pass
            else:
                return
            nonlocal width, height
            column = self.tree.identify_column(event.x)  # 列
            row = self.tree.identify_row(event.y)  # 行
            cn = int(str(column).replace('#','')) - 1
            column_name = columns[cn]
            rn = self.tree.index(row)
            entryedit = Text(self.mainWindow, width = 18,height = 1)
            entryedit.place(x = cn * width + 1, y = 6 + (rn+1) * (height + 2))
            def saveedit(event):
                new_val = entryedit.get(0.0, "end")
                if new_val == '':
                    return
                elif column_name == 'Mac':
                    pass
                elif column_name == '备注':
                    mac = self.selectItem(row, '#1')
                    self.obj.editUser(mac, new_val)
                    
                # self.tree.set(row, column=column, value=new_val)      
                entryedit.destroy()
            entryedit.bind('<Return>', saveedit)

        self.tree.bind('<Double-1>', SetCell)
        
        def addUser():
            addUserWindow = Tk()
            addUserWindow.title('添加用户')
            self.FormatWindow(addUserWindow, 300, 100)
            Label(addUserWindow, text='用户Mac').grid(row=0, column=0)
            mac = Entry(addUserWindow, bd=5)
            mac.grid(row=0, column=1)
            Label(addUserWindow, text='用户描述').grid(row=1, column=0)
            description = Entry(addUserWindow, bd=5)
            description.grid(row=1, column=1)
            Button(addUserWindow, text='确定', width=5, command=lambda :enterAddUser(mac.get(),description.get())).grid(row=2, column=0)
            Button(addUserWindow, text='取消', width=5, command=lambda :addUserWindow.destroy()).grid(row=2, column=1)
            def enterAddUser(mac, description):
                self.obj.addUser(mac, description)
                addUserWindow.destroy()
                


        def editUser():
            pass

        def deleteUser():
            if len(self.tree.selection()) > 0:
                pass
            else:
                return
            item = self.tree.selection()[0]
            mac = self.selectItem(item, '#1')
            self.obj.deleteUser(mac)

        def bindUser():
            if len(self.tree.selection()) > 0:
                pass
            else:
                return
            item = self.tree.selection()[0]
            mac = self.selectItem(item, '#1')
            self.obj.editUser(mac, is_active=1)

        def unbindUser():
            if len(self.tree.selection()) > 0:
                pass
            else:
                return
            item = self.tree.selection()[0]
            mac = self.selectItem(item, '#1')
            self.obj.editUser(mac, is_active=0)

        btnFrame = Frame(self.mainWindow)
        Button(btnFrame, text='新增', font=('Fixdsys', 12, 'bold'), width=5,fg='white',bg="#5F9EA0",command=addUser).pack(side=TOP, expand = NO, pady=10)
        Button(btnFrame, text='删除', font=('Fixdsys', 12, 'bold'), width=5,fg='white',bg="#C71585",command=deleteUser).pack(side=TOP, expand = NO, pady=10)
        Button(btnFrame, text='绑定', font=('Fixdsys', 12, 'bold'), width=5,fg='white',bg="#6495ED",command=bindUser).pack(side=TOP, expand = NO, pady=10)
        Button(btnFrame, text='解绑', font=('Fixdsys', 12, 'bold'), width=5,fg='white',bg="#708090",command=unbindUser).pack(side=TOP, expand = NO, pady=10)
        btnFrame.pack(side=TOP, expand = NO, pady=50)
        self.obj.getUserList()
        self.mainWindow.mainloop()

    def LoginUI(self):
        self.loginWindow = Tk()
        self.loginWindow.title('控制台登录')
        background_color="white"
        self.loginWindow.configure(background=background_color)
        ft = tkFont.Font(family='Fixdsys', size=16, weight=tkFont.BOLD)
        Label(self.loginWindow, text="虎牙脚本控制台",font=ft, bg=background_color).place(x=100,y=44)
        entryBackGroundColor="#F3F3F4"
        userNameFont = tkFont.Font(family='Fixdsys', size=12)
        Label(self.loginWindow, text='用户名',font=userNameFont, bg=background_color, fg='#696969').place(x=20, y=150)
        userName = StringVar()
        Entry(self.loginWindow, highlightthickness=1,bg=entryBackGroundColor,textvariable =userName).place(x=20, y=180,width=320, height=30)
        passWordFont = tkFont.Font(family='Fixdsys', size=12)
        passWord = StringVar() 
        Label(self.loginWindow, text='密码',font=passWordFont, bg=background_color, fg='#696969').place(x=20, y=220)
        Entry(self.loginWindow, highlightthickness=1, bg=entryBackGroundColor,textvariable =passWord, show='*').place(x=20, y=250,width=320, height=30)
        # remeberMeFont = tkFont.Font(family='Fixdsys', size=10)
        # Checkbutton(loginWindow, text="记住我", fg="#7B68EE", variable="0", font=remeberMeFont, bg=background_color).place(x=20, y=300)
        btnLogin = Button(self.loginWindow, text='立即登录', font=('Fixdsys', 14, 'bold'), width=29,fg='white',bg="#7B68EE",command=lambda :self.obj.login(userName.get(),passWord.get()))
        btnLogin.place(x=20, y=330)
        btnRegister = Button(self.loginWindow, text='立即注册', font=('Fixdsys', 14, 'bold'), width=29,fg='white',bg="#4169E1",command=lambda :self.obj.register(userName.get(),passWord.get()))
        regester_info=tkFont.Font(family='Fixdsys', size=10)
        def on_enter(event):
            regester_info.configure(underline=True)
        def on_leave(event):
            regester_info.configure(underline=False)
        def to_login(event):
            btnRegister.place_forget()
            lbRegister.place(x=150,y=375)
            lbLogin.place_forget()
            btnLogin.place(x=20, y=330)
        def to_register(event):
            btnLogin.place_forget()
            lbLogin.place(x=150,y=375)
            lbRegister.place_forget()
            btnRegister.place(x=20, y=330)
            
        #Label(loginWindow, text='还没有账号？', font=regester_info, bg=background_color).place(x=102,y=375)
        lbRegister = Label(self.loginWindow, text='立即注册', font=regester_info, bg=background_color,fg="#FFA500")
        lbRegister.place(x=150,y=375)
        lbLogin = Label(self.loginWindow, text='立即登录', font=regester_info, bg=background_color,fg="#FFA500")
        lbRegister.bind("<Enter>", on_enter)
        lbRegister.bind("<Leave>", on_leave)
        lbRegister.bind("<ButtonRelease-1>", to_register)
        lbLogin.bind("<Enter>", on_enter)
        lbLogin.bind("<Leave>", on_leave)
        lbLogin.bind("<ButtonRelease-1>", to_login)
        
        self.FormatWindow(self.loginWindow, 370, 480)
        self.loginWindow.mainloop()

    def UpdateUserList(self, user_list):
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        for i in range(len(user_list)):
            if user_list[i]['is_active'] == '0':
                status = '未绑定'
            elif user_list[i]['is_active'] == '1':
                status = '已绑定'
            self.tree.insert('', i, values=(user_list[i]['user_mac'], user_list[i]['user_description'], status))
        self.tree.update()

if __name__ == '__main__':#执行层
    ts = TicketServer()
    ui = UI(ts)
    ts.bindUI(ui)
    ts.launch()
