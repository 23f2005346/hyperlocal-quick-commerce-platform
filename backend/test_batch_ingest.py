import unittest
import os
import shutil
import tempfile
from pathlib import Path
from batch_ingest_images import parse_filename, ingest_batch_photos
from app import create_app
from models import db, Product, ProductVariant

app = create_app()

class TestBatchIngest(unittest.TestCase):
    def test_filename_parsing(self):
        cases = [
            ("toor-daal-190-per-kg.jpg", 190.0, "1kg", True),
            ("chakki-atta-38-1kg.png", 38.0, "1kg", True),
            ("fortune-sunflower-oil-145-1l.jpg", 145.0, "1L", False),
            ("tata-salt-28-1kg.jpg", 28.0, "1kg", False),
            ("maggi-14-70g.jpg", 14.0, "70g", False),
            ("sugar-42-per-kg.jpg", 42.0, "1kg", True),
            ("chana-dal-90-500g.jpg", 90.0, "500g", True),
            ("gehu-34-1kg.jpg", 34.0, "1kg", True),
            ("besan-98-1kg.jpg", 98.0, "1kg", True),
            ("poha-54-1kg.jpg", 54.0, "1kg", True),
        ]
        for fname, expected_price, expected_unit, expected_loose in cases:
            res = parse_filename(fname)
            self.assertEqual(res['price'], expected_price, f"Failed price for {fname}")
            self.assertEqual(res['unit_size'], expected_unit, f"Failed unit for {fname}")
            self.assertEqual(res['is_loose'], expected_loose, f"Failed loose flag for {fname}")

    def test_dry_run_ingest(self):
        temp_dir = tempfile.mkdtemp()
        try:
            # Create a dummy test image file
            sample_img = Path(temp_dir) / "chana-dal-95-1kg.jpg"
            with open(sample_img, "wb") as f:
                f.write(b"fake-image-bytes")

            res = ingest_batch_photos(batch_dir=temp_dir, dry_run=True, verbose=False)
            self.assertTrue(res['success'])
            self.assertEqual(res['processed'], 1)
            self.assertEqual(res['created'], 0)
            self.assertEqual(res['items'][0]['price'], 95.0)
            self.assertEqual(res['items'][0]['status'], 'Dry-Run')
        finally:
            shutil.rmtree(temp_dir)

if __name__ == '__main__':
    unittest.main()
