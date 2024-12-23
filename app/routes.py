from flask import Blueprint, redirect, render_template, jsonify, request, url_for

from app.utils.drawing import draw_winners, query_winners_records, redraw
from app.utils.query_sqlite import insert_sqlite, query_sqlite

bp = Blueprint('main', __name__)

junior_member_list = [
    {"id": 1, "name": "Mock"}
]

new_member_list = [
    {"id": 1, "name": "Mock"}
]

@bp.context_processor
def inject_drawing_groups():
    sql = '''SELECT id, group_name, color FROM drawing_groups;'''
    drawing_groups = [{'value': row['id'], 'group_name': row['group_name'], 'background_color': row['color']} for row in query_sqlite(sql)]
    return dict(drawing_groups=drawing_groups)

# Add any other related data/models here
@bp.route('/')
def index():
    return render_template('index.html')

@bp.route('/googleicp', methods=['GET', 'POST'])
def googleicp():
    if request.method == 'POST':
        prize_names = request.form.getlist('prizeName[]')
        prize_quantities = request.form.getlist('prizeQuantity[]')

        drawing_group = int(request.form.get('prizeType'))
        lottery_pool = 3
        sql = '''SELECT MAX(order_in_group) AS order_in_group FROM gifts WHERE drawing_group_id = ?;'''
        order_in_group = (query_sqlite(sql, (drawing_group,))[0]['order_in_group'] or 0) + 1

        for name, quantity in zip(prize_names, prize_quantities):
            if not name or not quantity:
                continue

            sql = '''
                INSERT INTO gifts (drawing_group_id, lottery_pool_id, gift_name, gift_description, quantity, order_in_group, drawn) 
                VALUES (?, ?, ?, ?, ?, ?, ?);
            '''
            _ = insert_sqlite(sql, (drawing_group, lottery_pool, name, name, int(quantity), order_in_group, 0))
            order_in_group += 1
            
        return redirect(url_for('main.googleicp', _method='GET'))
    else:
        sql = '''SELECT id, group_name FROM drawing_groups WHERE id > 8;'''
        drawing_groups = [{'id': row['id'], 'name': row['group_name']} for row in query_sqlite(sql)]

        return render_template('add_gift.html', drawing_groups=drawing_groups)

@bp.route('/senior_member')
def senior_member():
    drawing_group = 1  # 預設選中的值
    return render_template('senior_member.html', drawing_group=drawing_group)

@bp.route('/junior_member')
def junior_member():
    drawing_group = 2  # Default selected group
    return render_template('junior_member.html', drawing_group=drawing_group, employees=junior_member_list)

@bp.route('/new_member')
def new_member():
    drawing_group = 3  # Default selected group
    return render_template('new_member.html', drawing_group=drawing_group, employees=new_member_list)

@bp.route('/gifts')
def gift_page():
    # Get drawing_group from query parameters, default to 0 if not provided
    drawing_group = request.args.get('drawing_group', 0, type=int)

    sql = '''
        SELECT id AS 'gift_id', gift_name, quantity, order_in_group, drawn 
        FROM gifts 
        WHERE drawing_group_id = ? 
        ORDER BY order_in_group;
    '''
    gifts = query_sqlite(sql, (drawing_group,))

    return render_template('gifts.html', drawing_group=drawing_group, gifts=gifts)

@bp.route('/draw/<int:gift_id>')
def draw(gift_id):
    # get gift detail
    sql = '''
        SELECT id AS 'gift_id', drawing_group_id AS 'drawing_group', lottery_pool_id, gift_name, gift_description, quantity, order_in_group, drawn
        FROM gifts 
        WHERE id = ?
        LIMIT 1;
    '''
    results = query_sqlite(sql, (gift_id,))
    gift_detail = results[0] if results else None
    
    # 抽過直接撈取人員顯示
    if gift_detail['drawn'] == 1:
        return render_template('draw.html', gift=gift_detail)

    _ = draw_winners(gift_id, gift_detail['lottery_pool_id'], gift_detail['quantity'])

    return render_template('draw.html', gift=gift_detail)

@bp.route('/winners_fragment/<int:gift_id>')
def winners_fragment(gift_id):
    winners_data = query_winners_records(gift_id)

    return render_template('partials/winners_fragment.html', winners=winners_data, gift_id=gift_id)

@bp.route('/redraw', methods=['POST'])
def redraw_winner():
    data = request.json
    employee_code = data.get('employee_code')
    gift_id = data.get('gift_id')

    redraw(gift_id, employee_code)

    return jsonify({'success': True})