import pymysql

def set_defaults():
    print("Connecting to database...")
    conn = pymysql.connect(host='127.0.0.1', user='root', database='question')
    cur = conn.cursor()
    
    print("Updating existing tests to show results and scores by default...")
    cur.execute("UPDATE test_series SET is_result_show = 1, is_score_show = 1")
    conn.commit()
    conn.close()
    
    print("Done!")

if __name__ == "__main__":
    set_defaults()
