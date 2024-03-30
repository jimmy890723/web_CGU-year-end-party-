from flask import Flask, request, render_template, session, redirect, url_for
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SECRET_KEY'] = 'widelab'
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:widelab35795639@rtx2080ti3.widelab.org/widelab'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# 定義模型
class Participants(db.Model):
    __tablename__ = 'participants'
    seqNum = db.Column(db.Integer, primary_key=True)
    departName = db.Column(db.String(50))
    name = db.Column(db.String(40))
    enter = db.Column(db.Boolean, default=False)

class Prize(db.Model):
    __tablename__ = 'prize'
    prizeId = db.Column(db.Integer, primary_key=True)
    prizeName = db.Column(db.String(50))
    quantity = db.Column(db.Integer)

class Winning(db.Model):
    __tablename__ = 'winning'
    seqNum = db.Column(db.Integer, primary_key=True)
    prizeId = db.Column(db.Integer, primary_key=True)
    claimed = db.Column(db.Boolean, default=False)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        # 使用者是 'widelab' 且密码是 'widelab35795639'
        if username == 'widelab' and password == 'widelab':
            session['logged_in'] = True
            return redirect(url_for('index'))
        else:
            return '使用者名稱或密碼錯誤！'
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    return redirect(url_for('login'))

@app.route('/', methods=['GET', 'POST'])
def index():
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    message = None
    error = False
    if request.method == 'POST':
        # 從表單中獲取數據
        seqNum = request.form.get('seqNum')
        prizeId = request.form.get('prizeId')

        # 檢查是否為空字串
        seqNum = int(seqNum) if seqNum.isdigit() else None
        prizeId = int(prizeId) if prizeId.isdigit() else None

        # 檢查是否為空
        if seqNum is None or prizeId is None:
            message = '得獎人或獎品不得為空'
            error = True
        else:
            winning = Winning.query.filter_by(seqNum=seqNum).first()
            # 將數據寫入資料庫
            winning = Winning(seqNum=seqNum, prizeId=prizeId, claimed=False)
            db.session.add(winning)
            db.session.commit()
            message = '新增成功'
                    
    # 從數據庫中獲取數據
    participants_list = Participants.query.all()
    prize_list = Prize.query.all()
    winning_list = Winning.query.all()
    return render_template('winning.html', 
                           participants=participants_list, 
                           prizes=prize_list, 
                           winnings=winning_list, 
                           message=message, 
                           error=error)

@app.route('/winning_list', methods=['GET', 'POST'])
def winning_list():
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    
    # 執行聯合查詢並按照 prizeId 排序
    # 顯示資訊包含: seqNum, name, prizeId, prizeName, claimed
    winnings_query = db.session.query(
        Winning.seqNum,
        Winning.prizeId,
        Winning.claimed,
        Participants.name,
        Prize.prizeName
    ).join(Participants, Winning.seqNum == Participants.seqNum) \
    .join(Prize, Winning.prizeId == Prize.prizeId) \
    .order_by(Winning.prizeId) \
    .all()

    return render_template('winning_list.html', winnings_query=winnings_query)

@app.route('/handle_actions', methods=['POST'])
def handle_actions():
    print("Action route triggered")
    action = request.form.get('action')
    selected_ids = request.form.getlist('selected')
    print("Action:", action)
    print("Selected IDs:", selected_ids)

    for selected_id in selected_ids:
        seqNum, prizeId = map(int, selected_id.split('-'))
        winning_entry = Winning.query.filter_by(seqNum=seqNum, prizeId=prizeId).first()
        if not winning_entry:
            continue
        if action == '領獎':
            winning_entry.claimed = True
        elif action == '刪除':
            db.session.delete(winning_entry)
    db.session.commit()
    return redirect(url_for('winning_list'))

if __name__ == '__main__':
    app.run()
