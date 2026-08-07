import pymysql
import tkinter as tk
from tkinter import ttk
from dbconfig import DB_USER, DB_PASSWORD

def get_connect():
    connect = pymysql.connect(
        host='localhost',
        user=DB_USER,
        password=DB_PASSWORD,
        database='pizzadb'
    )
    return connect

def add():
    n = e1.get().strip()
    p = c1.get()
    q = c2.get()
    if not n or (p == 'Select from the menu') or (q == 'Select from the menu'):
        l.config(text='All fields required!', fg='red')
        e1.delete(0, tk.END)
        c1.set('Select from the menu')
        c2.set('Select from the menu')
        return

    connect = None
    try:
        connect = get_connect()
        with connect.cursor() as cursor:
            cursor.execute(
                'insert into pending_orders(customer_name,pizza_type,quantity) values(%s,%s,%s);',
                (n, p, q)
            )
        connect.commit()  # FIX: without this, the insert never saves
        l.config(text='Order added successfully!', fg='green')
        e1.delete(0, tk.END)
        c1.set('Select from the menu')
        c2.set('Select from the menu')
        view()
    except Exception as e:
        l.config(text=f'Error occurred while adding order: {e}', fg='red')
    finally:
        if connect:
            connect.close()

def view():
    connect = None
    try:
        connect = get_connect()
        with connect.cursor() as cursor:
            cursor.execute("SELECT customer_id, customer_name, pizza_type, quantity FROM pending_orders")
            orders = cursor.fetchall()

        t1.delete(1.0, tk.END)
        if not orders:
            t1.insert(tk.END, 'No orders found!')
            l.config(text='No orders found!', fg='blue')
        else:
            # FIX: format rows instead of dumping a raw tuple of tuples
            for order_id, name, pizza, qty in orders:
                t1.insert(tk.END, f'ID: {order_id} | Customer: {name} | Pizza: {pizza} | Qty: {qty}\n')
            l.config(text='All orders successfully found!', fg='blue')
    except Exception as e:  # FIX: was FileNotFoundError, which never matches a DB error
        l.config(text=f'Error occurred while fetching orders: {e}', fg='red')
    finally:
        if connect:
            connect.close()

def delete():
    n = e2.get().strip()  # FIX: Created ID field instead of reusing the name entry
    if not n:
        l.config(text='Enter customer_id to delete!', fg='red')
        return

    connect = None
    try:
        connect = get_connect()
        with connect.cursor() as cursor:
            cursor.execute("DELETE FROM pending_orders where customer_id = %s", (n,))
            connect.commit()
            if cursor.rowcount == 1:
                l.config(text='Order deleted successfully', fg='green')
                e2.delete(0, tk.END)
                view()
            else:
                l.config(text='Order not found', fg='red')
    except Exception as e:
        l.config(text=f'Error occurred while deleting order: {e}', fg='red')
    finally:
        if connect:
            connect.close()

app = tk.Tk()
app.title('Order Management')
style = ttk.Style()
style.configure('TCombobox', font=('Arial', 15))
app.option_add('*TCombobox*Listbox.font', ('Arial', 15))

h1 = tk.Label(app, text='Customer:', font=('Arial', 20))
h1.pack(pady=10)
e1 = tk.Entry(app, width=20, font=('Arial', 15))
e1.pack(pady=1)

h2 = tk.Label(app, text='Pizza type:', font=('Arial', 20))
h2.pack(pady=10)
options = ['S Margerita', 'M Margerita', 'L Margerita', 'S Pepperoni', 'M Pepperoni', 'L Pepperoni']
c1 = ttk.Combobox(app, values=options, font=('Arial', 15), state='readonly')
c1.set('Select from the menu')
c1.pack(pady=1)

h3 = tk.Label(app, text='Quantity:', font=('Arial', 20))
h3.pack(pady=10)
option = [1, 2, 3]
c2 = ttk.Combobox(app, values=option, state='readonly', font=('Arial', 15))
c2.set('Select from the menu')
c2.pack(pady=1)

b1 = tk.Button(app, text='Add order', font=('Arial', 20), command=add)
b1.pack(pady=10)
b2 = tk.Button(app, text='View orders', font=('Arial', 20), command=view)
b2.pack(pady=10)

h4 = tk.Label(app, text='Customer ID (to delete):', font=('Arial', 16))
h4.pack(pady=5)
e2 = tk.Entry(app, width=10, font=('Arial', 15))  # FIX: new field for delete
e2.pack(pady=1)
b3 = tk.Button(app, text='Delete order', font=('Arial', 20), command=delete)
b3.pack(pady=10)

l = tk.Label(app, font=('Arial', 20), text='')
l.pack(pady=10)
t1 = tk.Text(app, width=70, height=40)
t1.pack(pady=10)

app.mainloop()