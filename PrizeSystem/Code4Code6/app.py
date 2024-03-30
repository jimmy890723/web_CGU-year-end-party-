from flask import Flask, render_template, request, redirect, url_for
import mysql.connector
import logging
import datetime

app = Flask(__name__)

global shutdown 
shutdown = False

# MySQL 設定
mysql_config = {
    'host': "rtx2080ti3.widelab.org",    #"rtx2080ti3.widelab.org:3306"'localhost'
    'port': 3306,
    'user': "root",         #"widelab"'root'
    'password': "widelab35795639",         #"widelab35795639"
    'database': 'widelab',   #"widelab"
    'auth_plugin': 'mysql_native_password'
}


# 設置 Flask 的日誌級別為 WARNING 或 ERROR，這樣只有重要的錯誤信息會被記錄
log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)

# 設置日誌級別
#logging.basicConfig(level=logging.DEBUG)
# 設定 logging
logging.basicConfig(filename='access_log.txt', level=logging.INFO)

@app.route('/')
def index():
    app.logger.debug("這是一條 debug 級別的日誌訊息")
    return "Hello World"

@app.route('/code_5/')
def code_5():
    user_input = request.args.get('ID', '')
    seqNum = user_input
    # 初始化變數
    data = []

    # 建立 MySQL 連線
    conn = mysql.connector.connect(**mysql_config)

    try:
        with conn.cursor() as cursor:
            sql_sel = "SELECT winning.seqNum , participants.departName, participants.name, prize.prizeName FROM winning INNER JOIN prize ON prize.prizeId = winning.prizeId INNER JOIN participants ON winning.seqNum = participants.seqNum WHERE winning.seqNum = %s and winning.claimed = 0"
            
            cursor.execute(sql_sel, (seqNum,))
            data = cursor.fetchall()
            print(data)
            sql_sel_finish = "SELECT winning.seqNum , participants.departName, participants.name, prize.prizeName FROM winning INNER JOIN prize ON prize.prizeId = winning.prizeId INNER JOIN participants ON winning.seqNum = participants.seqNum WHERE winning.seqNum = %s and winning.claimed = 1"
            cursor.execute(sql_sel_finish, (seqNum,))
            data_2 = cursor.fetchall()
            print(data_2)
            sql_update = "UPDATE `winning` SET `claimed` = 1 WHERE `seqNum` = %s"
            cursor.execute(sql_update, (seqNum,))
            # 提交變更
            conn.commit()
    except mysql.connector.Error as err:
        # 處理 MySQL 錯誤
        print(f"MySQL Error: {err}")
    except Exception as e:
        # 處理其他例外情況
        print(f"Error: {e}")
    finally:
        # 關閉連線
        if conn.is_connected():
            conn.close()

    return render_template('code_5.html', data=data,data_2=data_2)
@app.route('/code_2/')
def code_2():
    user_input = request.args.get('ID', '')
    seqNum = user_input
    # 初始化變數
    data = []

    # 建立 MySQL 連線
    conn = mysql.connector.connect(**mysql_config)

    try:
        with conn.cursor() as cursor:
            sql_update = "UPDATE `participants` SET `enter` = 1 WHERE `seqNum` = %s"
            cursor.execute(sql_update, (seqNum,))
            # 提交變更
            conn.commit()
            sql_sel = "SELECT `seqNum`,`departName`,`name` FROM `participants` WHERE `seqNum` = %s"
            cursor.execute(sql_sel, (seqNum,))
            data = cursor.fetchall()
    except mysql.connector.Error as err:
        # 處理 MySQL 錯誤
        print(f"MySQL Error: {err}")
    except Exception as e:
        # 處理其他例外情況
        print(f"Error: {e}")
    finally:
        # 關閉連線
        if conn.is_connected():
            conn.close()

    return render_template('code_2.html', data=data)

@app.route('/code_3/<int:user_id>/')
def code_3(user_id):
    # 記錄開始時間
    start_time = datetime.datetime.now()
    global shutdown
    def find_A2(x,y):
      for A2 in range(1000,2000): 
          calculated_x = (A2 % 29) + (A2 % 3) * 2 + (A2 % 5) + 29
          if calculated_x == x and A2 == y:
              return A2
      return None
    
    # 初始化變數
    data = []
    check = True
    
    if shutdown == False:  
      if int(user_id) == 9999:
        log_seq_num = user_id
        log_prizeid = 0
        response_time = datetime.datetime.now() - start_time  # 計算響應時間
        # 記錄日誌
        log_entry = f'SeqNum: {log_seq_num}, 訪問時間: {start_time}, 連入時間: {response_time}, PrizeId: {log_prizeid}'
        logging.info(log_entry)
        return render_template('code_3.html', shutdown=False, data=data, check2=True)
      else:
        tmp_seqNum_x = int(user_id)%100
        tmp_seqNum_y = int(int(user_id)/100)
        seqNum = find_A2(tmp_seqNum_x,tmp_seqNum_y)
    else:
      return render_template('code_3.html', shutdown=True)

    # 建立 MySQL 連線
    conn = mysql.connector.connect(**mysql_config)

    try:
        with conn.cursor() as cursor:
            #sql = "SELECT * FROM `winning` WHERE `seqNum` = %s"
            sql = "SELECT winning.seqNum , participants.departName, participants.name, prize.prizeName , winning.claimed, winning.prizeId FROM winning INNER JOIN prize ON prize.prizeId = winning.prizeId INNER JOIN participants ON winning.seqNum = participants.seqNum WHERE winning.seqNum = %s"
            cursor.execute(sql, (seqNum,))
            data = cursor.fetchall()
            print(data)
             
            if data == []:
              sql = "SELECT participants.name, participants.seqNum FROM participants WHERE participants.seqNum = %s"
              cursor.execute(sql, (seqNum,))
              data = cursor.fetchall() 
              print(data)
              check = False
              if data:
                log_seq_num = data[0][1]
                log_prizeid = 0
            else:
              log_seq_num = data[0][0]
              log_prizeid = data[0][5]
    except mysql.connector.Error as err:
        # 處理 MySQL 錯誤
        print(f"MySQL Error: {err}")
    except Exception as e:
        # 處理其他例外情況
        print(f"Error: {e}")
    finally:
        # 關閉連線
        if conn.is_connected():
            conn.close()
    
    if seqNum == None:
        data = None
    
    response_time = datetime.datetime.now() - start_time  # 計算響應時間
    
    # 記錄日誌
    if data:
      log_entry = f'SeqNum: {log_seq_num}, 訪問時間: {start_time}, 連入時間: {response_time}, PrizeId: {log_prizeid}'
      logging.info(log_entry)
     
    return render_template('code_3.html', data=data,check=check,shutdown=False,check2=False)

@app.route('/enter')
def home_enter():
    return render_template('index_enter.html')

# 定义 A 网站的表单处理视图
@app.route('/process_form_enter', methods=['POST'])
def process_form_enter():
    # 获取表单中用户输入的数据
    user_input = request.form['user_input']
    
    # 在这里可以对用户输入进行处理
    
    # 跳转到 B 网站的 index 页面，并将用户输入作为参数传递过去
    return redirect(url_for('code_2', ID=user_input))


@app.route('/Redeem')
def home_Redeem():
    return render_template('index_Redeem.html')

# 定义 A 网站的表单处理视图
@app.route('/process_form_Redeem', methods=['POST'])
def process_form_Redeem():
    # 获取表单中用户输入的数据
    user_input = request.form['user_input']
    
    # 在这里可以对用户输入进行处理
    
    # 跳转到 B 网站的 index 页面，并将用户输入作为参数传递过去
    return redirect(url_for('code_5', ID=user_input))

@app.route('/selfsearch')
def home_selfsearch():
    return render_template('index_selfsearch.html')

@app.route('/process_form_selfsearch', methods=['POST'])
def process_form_selfsearch():
    # 获取表单中用户输入的数据
    user_input = request.form['user_input']
    
    # 在这里可以对用户输入进行处理
    
    # 跳转到 B 网站的 index 页面，并将用户输入作为参数传递过去
    return redirect(url_for('code_3', ID=user_input))

@app.route('/control')
def control_shutdown():
    global shutdown
    # 初始化變數
    data_prize = []
    data_winning = []
    data = []
    # 建立 MySQL 連線
    conn = mysql.connector.connect(**mysql_config)

    try:
        with conn.cursor() as cursor:
            app.logger.debug("check")
            sql = "SELECT * FROM prize"
            cursor.execute(sql)
            data_prize = cursor.fetchall()
            #app.logger.debug(data_prize)
            sql = "SELECT winning.prizeId, winning.claimed FROM winning"
            cursor.execute(sql)
            data_winning = cursor.fetchall()
            #app.logger.debug(data_winning)
            
            # 計算每個獎品的未領獎數量
            unclaimed_counts = {prize[0]: 0 for prize in data_prize}
            if data_winning:
                for win in data_winning:
                    if win[1] == 0:
                        unclaimed_counts[win[0]] += 1

            # 更新 data_prize 中的每個獎品
            for prize in data_prize:
                # 計算更新後的總和
                total = prize[2] + unclaimed_counts[prize[0]]
            
                # 將獎品名稱和更新後的總和存儲到新的列表中
                data.append([prize[1], total])
            #app.logger.debug(data)
            data.sort(key=lambda x: x[1], reverse=True)

    except mysql.connector.Error as err:
        # 處理 MySQL 錯誤
        print(f"MySQL Error: {err}")
    except Exception as e:
        # 處理其他例外情況
        print(f"Error: {e}")
    finally:
        # 關閉連線
        if conn.is_connected():
            conn.close()
            
    # 讀取 access_log.txt
    last_access_time = None
    try:
        with open('access_log.txt', 'r') as file:
            for line in reversed(file.readlines()):
                if 'SeqNum: 9999,' in line:
                    # 解析連入時間
                    parts = line.split(',')
                    if len(parts) >= 3:
                        last_access_time = parts[2].split(':')[3].strip()
                    break

    except Exception as e:
        print(f"Error reading log file: {e}")
    
    if last_access_time!= None:
      last_access_time = float(last_access_time)
    else:
      last_access_time = 0
    
    return render_template('control.html', data_prize=data, last_access_time=last_access_time, shutdown=shutdown)

@app.route('/set_shutdown', methods=['POST'])
def set_shutdown():
    global shutdown
    shutdown_value = request.form.get('shutdown')
    if shutdown_value == "True":
        shutdown = True
    elif shutdown_value == "False":
        shutdown = False
    return redirect('/control')

if __name__ == '__main__':
    #app.run(debug=True)
    app.run(debug=True, port=5000)