import time
import os
import hashlib
from datetime import datetime
import random
import pytz

from app.utils.query_sqlite import insert_sqlite, query_sqlite

def generate_random_seed() -> int:
    """
    Generates a highly variable seed for random number generation by combining
    multiple sources of entropy: time, process info, and system state.
    
    Returns:
        int: A seed value suitable for random number generation
    """
    # Collect entropy sources
    current_time: int = time.time_ns()  # Nanosecond precision time
    process_id: int = os.getpid()  # Current process ID
    random_bytes: bytes = os.urandom(32)  # System random bytes
    datetime_now: str = datetime.now().strftime('%Y%m%d%H%M%S%f')  # Current datetime with microseconds
    
    # Combine all sources into a string
    entropy_string: str = f"{current_time}{process_id}{random_bytes.hex()}{datetime_now}"
    
    # Create a hash of the combined sources
    hash_object = hashlib.sha256(entropy_string.encode())
    hash_hex: str = hash_object.hexdigest()
    
    # Convert the first 16 characters of the hex hash to an integer
    seed: int = int(hash_hex[:16], 16)
    
    return seed

def draw_employees(employee_ids: list[str], num_winners: int, seed: int | None = None) -> list[str]:
    """
    Randomly selects winners from a list of employee IDs using a specified seed.
    
    Args:
        employee_ids (list): List of employee IDs to draw from
        num_winners (int): Number of winners to select
        seed (int, optional): Random seed for reproducible results
    
    Returns:
        list: Selected employee IDs
    """
    # Add type hint for seed
    if seed is None:
        seed = generate_random_seed()
    
    if num_winners > len(employee_ids):
        raise ValueError("Number of winners cannot exceed number of employees")
    
    # Add type hints for the random operations
    random.seed(seed)
    sorted_ids: list[str] = sorted(employee_ids)
    winners: list[str] = random.sample(sorted_ids, num_winners)
    return winners

def draw_winners(gift_id: int, lottery_pool_id: int, gift_quantity: int) -> list[dict]:
    lottery_attempt, lottery_pool_employee_ids = get_eligible_employees(gift_id, 1 if lottery_pool_id == 1 else 0)
    print(lottery_attempt, lottery_pool_employee_ids)

    # Generate seed for random drawing
    draw_time = datetime.now()
    seed = generate_random_seed()
    # 可以抽的人 >= 要抽的人數
    if len(lottery_pool_employee_ids) >= gift_quantity:
        winners_ids = draw_employees(lottery_pool_employee_ids, gift_quantity, seed)

        # 寫入抽獎紀錄
        sql = '''
            INSERT INTO draw_events (gift_id, lottery_pool_id, lottery_attempt, seed, draw_timestamp, employees) VALUES (?, ?, ?, ?, ?, ?);
        '''
        draw_event_id = insert_sqlite(sql, (gift_id, lottery_pool_id, lottery_attempt, str(seed), draw_time, ','.join(f"'{e}'" for e in lottery_pool_employee_ids)))
        # 寫入抽獎人員
        sql = '''
            INSERT INTO draw_records (draw_event_id, employee_code) VALUES (?, ?);
        '''
        draw_record = [insert_sqlite(sql, (draw_event_id, winner)) for winner in winners_ids]
    
    # 可以抽的人 < 要抽的人數，把可以抽的人都設定為中獎，接著抽獎池全部重來
    else:
        ''' 
        先把這個抽獎池的人都設定為中獎 
        '''
        # 寫入抽獎紀錄，輪數 n
        sql = '''
            INSERT INTO draw_events (gift_id, lottery_pool_id, lottery_attempt, seed, draw_timestamp, employees) VALUES (?, ?, ?, ?, ?, ?);
        '''
        draw_event_id = insert_sqlite(sql, (gift_id, lottery_pool_id, lottery_attempt, str(seed), draw_time, ','.join(f"'{e}'" for e in lottery_pool_employee_ids)))
        # 寫入抽獎人員
        sql = '''
            INSERT INTO draw_records (draw_event_id, employee_code) VALUES (?, ?);
        '''
        draw_record = [insert_sqlite(sql, (draw_event_id, winner)) for winner in lottery_pool_employee_ids]


        '''
        再來挑選剩下還要抽選的人，因為重新來了，所以輪數 n + 1
        會到這邊一定是人少獎項多，表示抽獎池已經不夠人了，輪數 0 + 1。這邊偷懶沒有算第3輪
        '''
        # 不夠幾個人
        insufficient = gift_quantity - len(lottery_pool_employee_ids)
        # 全部的人來抽選 不夠的人
        sql = 'SELECT employee_code FROM employee WHERE status = ?;'
        all_employee_temp = [emp['employee_code'] for emp in query_sqlite(sql, (1 if lottery_pool_id == 1 else 0,))]
        all_employee_ids = all_employee_temp - lottery_pool_employee_ids # 這邊應該要減掉最後強制中獎抽過的人，避免又抽到一樣的人
        winners_ids = draw_employees(all_employee_ids, insufficient, seed)
        # 寫入抽獎紀錄
        sql = '''
            INSERT INTO draw_events (gift_id, lottery_pool_id, lottery_attempt, seed, draw_timestamp, employees) VALUES (?, ?, ?, ?, ?, ?);
        '''
        draw_event_id = insert_sqlite(sql, (gift_id, lottery_pool_id, lottery_attempt + 1, str(seed), draw_time, ','.join(f"'{e}'" for e in all_employee_ids)))
        # 寫入抽獎人員
        sql = '''
            INSERT INTO draw_records (draw_event_id, employee_code) VALUES (?, ?);
        '''
        draw_record = [insert_sqlite(sql, (draw_event_id, winner)) for winner in winners_ids]

    # 更新禮物狀態
    if all(draw_record):  # Check if all records were successful
        sql = 'UPDATE gifts SET drawn = 1 WHERE id = ?;'
        _ = insert_sqlite(sql, (gift_id,))

def query_winners_records(gift_id: int) -> list[dict]:
    sql = '''
        SELECT employee.employee_code, employee.name_chinese, employee.name_english, 
            draw_records.created_at AS 'draw_time', draw_records.redraw 
        FROM draw_events
        INNER JOIN draw_records ON draw_events.id = draw_records.draw_event_id
        LEFT JOIN employee ON draw_records.employee_code = employee.employee_code 
        WHERE draw_events.gift_id = ? AND draw_records.cancel = 0;
    '''
    winners_data = query_sqlite(sql, (gift_id,))
    
    # 設定時區為 UTC+8
    tz = pytz.timezone('Asia/Taipei')
    
    # 轉換時間為 UTC+8 時區
    for winner in winners_data:
        if 'draw_time' in winner and winner['draw_time']:
            utc_time = datetime.strptime(winner['draw_time'], '%Y-%m-%d %H:%M:%S')
            local_time = utc_time.replace(tzinfo=pytz.utc).astimezone(tz)
            winner['draw_time'] = local_time.strftime('%H:%M:%S')
    
    return winners_data

def get_eligible_employees(gift_id: int, employee_status: int) -> tuple[int, list[str]]:
    sql = '''
        SELECT employee_code FROM employee WHERE status >= ?;
    '''
    all_employee_ids = [emp['employee_code'] for emp in query_sqlite(sql, (employee_status,))]

    sql = '''
        SELECT lottery_attempt, employee_code
        FROM draw_events
        LEFT JOIN draw_records ON draw_events.id = draw_records.draw_event_id 
        WHERE lottery_pool_id = (
            SELECT lottery_pool_id 
            FROM gifts
            WHERE id = ?
        )
    '''
    results = query_sqlite(sql, (gift_id,))

    if not results:
        return 0, all_employee_ids

    # Group results by lottery attempt and exclude previously drawn employees
    grouped_results = {
        attempt: [r['employee_code'] for r in results if r['lottery_attempt'] == attempt]
        for attempt in set(r['lottery_attempt'] for r in results)
    }
    current_attempt = max(grouped_results.keys())
    excluded_employee_codes = grouped_results[current_attempt]
    lottery_pool_employee_ids = list(set(all_employee_ids) - set(excluded_employee_codes))

    return current_attempt, lottery_pool_employee_ids

def redraw(gift_id: int, employee_code: str) -> None:
    draw_time = datetime.now()

    # 把重抽的人 cancel 設 1
    sql = '''
        UPDATE draw_records
        SET cancel = 1
        WHERE draw_event_id IN (
            SELECT id 
            FROM draw_events
            WHERE draw_events.gift_id = ?
        )
        AND employee_code = ?;
    '''
    _ = insert_sqlite(sql, (gift_id, employee_code))

    sql = '''
        SELECT lottery_pool_id, lottery_attempt
        FROM draw_events
        WHERE gift_id = ?
        ORDER BY id DESC
        LIMIT 1;
    '''
    results = query_sqlite(sql, (gift_id,))
    lottery_pool_id = results[0]['lottery_pool_id']
    seed = generate_random_seed()

    lottery_attempt, lottery_pool_employee_ids = get_eligible_employees(gift_id, 1 if lottery_pool_id == 1 else 0)
    redraw_employee_code = draw_employees(lottery_pool_employee_ids, 1, seed)[0]

    # 寫入抽獎紀錄
    sql = '''
        INSERT INTO draw_events (gift_id, lottery_pool_id, lottery_attempt, seed, draw_timestamp, employees) VALUES (?, ?, ?, ?, ?, ?);
    '''
    draw_event_id = insert_sqlite(sql, (gift_id, lottery_pool_id, lottery_attempt, str(seed), draw_time, ','.join(f"'{e}'" for e in lottery_pool_employee_ids)))
    # 寫入抽獎人員
    sql = '''
        INSERT INTO draw_records (draw_event_id, employee_code, redraw) VALUES (?, ?, 1);
    '''
    _ = insert_sqlite(sql, (draw_event_id, redraw_employee_code))
