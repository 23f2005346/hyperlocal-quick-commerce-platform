#!/usr/bin/env python3
"""
Standalone automated database backup utility for Komal Mart Kirana Store.
Can be executed via cron, Windows Task Scheduler, or manual CLI.

Usage:
    python backup_db.py
    python backup_db.py --compress
    python backup_db.py --list
"""
import sys
import argparse
from backup_service import create_hot_backup, list_backups, verify_backup

def main():
    parser = argparse.ArgumentParser(description="Komal Mart SQLite Hot Backup Utility")
    parser.add_argument("--compress", action="store_true", help="GZIP compress the snapshot (.db.gz)")
    parser.add_argument("--list", action="store_true", help="List existing backups and exit")
    parser.add_argument("--verify", type=str, help="Verify integrity of a specific backup file")

    args = parser.parse_args()

    if args.list:
        backups = list_backups()
        print(f"\nFound {len(backups)} backup snapshots:")
        for idx, b in enumerate(backups, start=1):
            print(f" {idx}. {b['filename']} ({b['size_kb']} KB) - Created: {b['created_at']}")
        print()
        return

    if args.verify:
        print(f"Verifying backup integrity: {args.verify}...")
        ok, msg = verify_backup(args.verify)
        if ok:
            print(f"SUCCESS: {msg}")
        else:
            print(f"FAILED: {msg}", file=sys.stderr)
            sys.exit(1)
        return

    print("Initiating crash-safe SQLite hot backup...")
    try:
        meta = create_hot_backup(compress=args.compress)
        print(f"Hot backup completed successfully!")
        print(f" - File: {meta['filename']}")
        print(f" - Size: {meta['size_kb']} KB")
        print(f" - Path: {meta['filepath']}")
        
        # Verify integrity of newly created snapshot
        ok, msg = verify_backup(meta['filepath'])
        if ok:
            print(f" - Integrity Check: PASSED ({msg})")
        else:
            print(f" - Integrity Check: FAILED ({msg})", file=sys.stderr)
            sys.exit(1)
    except Exception as e:
        print(f"ERROR: Backup failed: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == '__main__':
    main()
