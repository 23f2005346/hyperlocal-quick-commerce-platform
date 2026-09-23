import os
import gzip
import shutil
import sqlite3
from datetime import datetime

BACKUP_DIR_DEFAULT = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'backups')

def get_backup_dir(custom_dir=None):
    b_dir = custom_dir or os.environ.get('BACKUP_DIR') or BACKUP_DIR_DEFAULT
    os.makedirs(b_dir, exist_ok=True)
    return b_dir

def create_hot_backup(db_path=None, custom_dir=None, compress=False, max_backups=30):
    """
    Performs a crash-safe, online hot backup using SQLite's native backup API.
    Guarantees zero database locks and captures uncheckpointed WAL frames cleanly.
    """
    if not db_path:
        db_path = os.environ.get('DB_PATH') or os.path.join(os.path.dirname(os.path.abspath(__file__)), 'kirana.db')

    if not os.path.exists(db_path):
        raise FileNotFoundError(f"Database file not found at: {db_path}")

    backup_dir = get_backup_dir(custom_dir)
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    raw_filename = f"kirana_backup_{timestamp}.db"
    raw_filepath = os.path.join(backup_dir, raw_filename)

    # 1. Atomic Hot Backup via SQLite C-API wrapper
    src_conn = sqlite3.connect(db_path)
    dst_conn = sqlite3.connect(raw_filepath)
    try:
        with dst_conn:
            src_conn.backup(dst_conn, pages=100) # Copy in 100-page chunks
    finally:
        dst_conn.close()
        src_conn.close()

    final_filepath = raw_filepath
    final_filename = raw_filename

    # 2. Optional GZIP Compression
    if compress:
        gz_filename = f"{raw_filename}.gz"
        gz_filepath = os.path.join(backup_dir, gz_filename)
        with open(raw_filepath, 'rb') as f_in:
            with gzip.open(gz_filepath, 'wb') as f_out:
                shutil.copyfileobj(f_in, f_out)
        os.remove(raw_filepath) # Remove raw uncompressed file
        final_filepath = gz_filepath
        final_filename = gz_filename

    # 3. Rotate Old Backups (keep latest N)
    rotate_backups(backup_dir, max_keep=max_backups)

    size_bytes = os.path.getsize(final_filepath)
    return {
        'filename': final_filename,
        'filepath': final_filepath,
        'size_bytes': size_bytes,
        'size_kb': round(size_bytes / 1024, 2),
        'created_at': datetime.now().strftime('%d %b %Y, %I:%M %p')
    }

def list_backups(custom_dir=None):
    """Lists all stored database snapshots sorted from newest to oldest."""
    backup_dir = get_backup_dir(custom_dir)
    files = []
    for fname in os.listdir(backup_dir):
        if fname.startswith('kirana_backup_') and (fname.endswith('.db') or fname.endswith('.db.gz')):
            fpath = os.path.join(backup_dir, fname)
            stat = os.stat(fpath)
            files.append({
                'filename': fname,
                'filepath': fpath,
                'size_bytes': stat.st_size,
                'size_kb': round(stat.st_size / 1024, 2),
                'created_at': datetime.fromtimestamp(stat.st_mtime).strftime('%d %b %Y, %I:%M %p'),
                'timestamp': stat.st_mtime
            })
    files.sort(key=lambda x: x['timestamp'], reverse=True)
    return files

def rotate_backups(backup_dir, max_keep=30):
    """Deletes the oldest backup files if total exceeds max_keep."""
    backups = list_backups(backup_dir)
    if len(backups) > max_keep:
        to_delete = backups[max_keep:]
        for item in to_delete:
            try:
                os.remove(item['filepath'])
                print(f"[BACKUP ROTATION] Pruned old backup: {item['filename']}")
            except Exception as e:
                print(f"[BACKUP ROTATION WARNING] Could not remove {item['filename']}: {e}")

def verify_backup(backup_filepath):
    """Executes PRAGMA integrity_check on the backup file to guarantee zero corruption."""
    if not os.path.exists(backup_filepath):
        return False, "File does not exist"

    test_path = backup_filepath
    is_temp = False

    if backup_filepath.endswith('.gz'):
        # Decompress to temporary file for check
        test_path = backup_filepath[:-3] + '.temp_check.db'
        is_temp = True
        with gzip.open(backup_filepath, 'rb') as f_in:
            with open(test_path, 'wb') as f_out:
                shutil.copyfileobj(f_in, f_out)

    try:
        conn = sqlite3.connect(test_path)
        cur = conn.cursor()
        cur.execute("PRAGMA integrity_check")
        res = cur.fetchone()
        conn.close()
        is_ok = (res and res[0] == 'ok')
        return is_ok, "Integrity OK" if is_ok else f"Integrity failed: {res}"
    except Exception as e:
        return False, str(e)
    finally:
        if is_temp and os.path.exists(test_path):
            try:
                os.remove(test_path)
            except Exception:
                pass
