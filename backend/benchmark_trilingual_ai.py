import os
import sys
import time
import json
from dotenv import load_dotenv

# Reconfigure stdout for UTF-8 on Windows
if sys.stdout.encoding != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
load_dotenv(os.path.join(os.path.dirname(os.path.abspath(__file__)), '.env'))

from app import create_app

def run_benchmarks():
    app = create_app()
    client = app.test_client()

    test_cases = [
        # MARATHI TESTS
        {
            "id": "MR_1_SINGLE",
            "lang": "mr",
            "title": "Marathi Test 1: Single Staple Item (साखर)",
            "input": "२ किलो साखर",
            "expected_count": 1,
            "description": "Customer ordering 2 kg sugar in pure Marathi"
        },
        {
            "id": "MR_2_MEDIUM",
            "lang": "mr",
            "title": "Marathi Test 2: Medium Grocery Basket (5 Items)",
            "input": "५ किलो चक्की आटा, १ किलो तूर डाळ, १ लिटर मोहरीचे तेल, ५०० ग्रॅम पोहे, आणि १ डेटॉल साबण",
            "expected_count": 5,
            "description": "5 common household staples with varying weights (5kg, 1kg, 1L, 500g, 1 bar)"
        },
        {
            "id": "MR_3_LARGE",
            "lang": "mr",
            "title": "Marathi Test 3: Full Monthly Ration with Milling (10 Items)",
            "input": "१० किलो गहू दळून द्या, २ किलो साखर, १ लिटर फॉर्च्यून सूर्यफूल तेल, १ किलो मूग डाळ, २५० ग्रॅम हळद, १०० ग्रॅम जिरे, १ टाटा मीठ, २ कोलगेट पेस्ट, १ पॅक लक्स साबण, आणि १ किलो रवा",
            "expected_count": 10,
            "description": "Comprehensive monthly ration list with Chakki pisai, staples, spices, and toiletries"
        },

        # HINDI TESTS
        {
            "id": "HI_1_SINGLE",
            "lang": "hi",
            "title": "Hindi Test 1: Single Staple Item (चीनी)",
            "input": "२ किलो चीनी",
            "expected_count": 1,
            "description": "Customer ordering 2 kg sugar in standard Hindi"
        },
        {
            "id": "HI_2_MEDIUM",
            "lang": "hi",
            "title": "Hindi Test 2: Medium Grocery Basket (5 Items)",
            "input": "५ किलो आटा, १ किलो अरहर दाल, १ लीटर सरसों का तेल, ५०० ग्राम पोहा, और १ डेटॉल साबुन",
            "expected_count": 5,
            "description": "5 common household staples in Hindi (Atta, Arhar dal, Mustard oil, Poha, Dettol)"
        },
        {
            "id": "HI_3_LARGE",
            "lang": "hi",
            "title": "Hindi Test 3: Full Monthly Ration with Milling (10 Items)",
            "input": "१० किलो गेहूं पिसाई करके देना, २ किलो चीनी, १ लीटर फॉर्च्यून रिफाइंड तेल, १ किलो मूंग दाल, २५० ग्राम हल्दी पाउडर, १०० ग्राम जीरा, १ टाटा नमक, २ कोलगेट टूथपेस्ट, १ लक्स साबुन का पैक, और १ किलो सूजी",
            "expected_count": 10,
            "description": "Comprehensive monthly ration in Hindi with grinding service, staples, spices, and personal care"
        },

        # ENGLISH / HINGLISH TESTS
        {
            "id": "EN_1_SINGLE",
            "lang": "en",
            "title": "English Test 1: Single Staple Item (Sugar)",
            "input": "2 kg sugar",
            "expected_count": 1,
            "description": "Customer ordering 2 kg sugar in English"
        },
        {
            "id": "EN_2_MEDIUM",
            "lang": "en",
            "title": "English Test 2: Medium Grocery Basket (5 Items)",
            "input": "5kg chakki fresh atta, 1kg toor dal, 1 litre mustard oil, 500g poha, and 1 dettol soap",
            "expected_count": 5,
            "description": "5 common household staples in Indian English / Hinglish"
        },
        {
            "id": "EN_3_LARGE",
            "lang": "en",
            "title": "English Test 3: Full Monthly Ration with Milling (10 Items)",
            "input": "10kg whole wheat with grinding service, 2kg sugar, 1L fortune sunflower oil, 1kg moong dal, 250g turmeric powder, 100g jeera, 1 tata salt, 2 colgate toothpaste, 1 pack of 4 lux soap, and 1kg sooji",
            "expected_count": 10,
            "description": "Comprehensive monthly ration in English with grinding service, spices, staples, and toiletries"
        }
    ]

    all_results = []
    print("=" * 80)
    print("KOMAL MART (कोमल मार्ट) — TRILINGUAL AI ORDER PARSING BENCHMARK")
    print("Testing Marathi, Hindi, and English with real grocery baskets against kirana.db")
    print("=" * 80)

    for idx, tc in enumerate(test_cases, 1):
        print(f"\n[{idx}/9] Running {tc['id']}: {tc['title']}...")
        print(f"    Input: \"{tc['input']}\"")
        start_t = time.time()
        
        try:
            res = client.post('/api/ai/parse-order', json={
                'text': tc['input'],
                'language': tc['lang']
            })
            duration = round(time.time() - start_t, 2)
            status_code = res.status_code
            data = res.get_json() or {}
        except Exception as e:
            duration = round(time.time() - start_t, 2)
            status_code = 500
            data = {'error': str(e), 'success': False}

        items = data.get('items', [])
        matched = [it for it in items if it.get('match_status') == 'matched']
        ambiguous = [it for it in items if it.get('match_status') == 'ambiguous']
        unavailable = [it for it in items if it.get('match_status') == 'unavailable']

        has_audio = bool(data.get('audio_base64'))
        audio_len = len(data.get('audio_base64') or '')

        calc_total = sum(float(it.get('line_total') or (float(it.get('unit_price', 0)) * float(it.get('quantity', 1)))) for it in matched)

        result_entry = {
            "test_id": tc["id"],
            "title": tc["title"],
            "language": tc["lang"],
            "input": tc["input"],
            "expected_items": tc["expected_count"],
            "actual_items": len(items),
            "matched_count": len(matched),
            "ambiguous_count": len(ambiguous),
            "unavailable_count": len(unavailable),
            "status_code": status_code,
            "latency_sec": duration,
            "estimated_total": round(calc_total, 2),
            "tts_synthesized": has_audio,
            "tts_bytes": audio_len,
            "summary_text": data.get('summary_text', ''),
            "items": items,
            "raw_response": data
        }
        all_results.append(result_entry)

        # Print live summary
        print(f"    Status: {status_code} | Latency: {duration}s | Items: {len(items)} (Matched: {len(matched)}, Ambiguous: {len(ambiguous)}, Out-of-Stock: {len(unavailable)})")
        print(f"    Estimated Total: ₹{round(calc_total, 2)}")
        print(f"    AI Vocal Summary: \"{data.get('summary_text', '')}\"")
        for item_idx, it in enumerate(items, 1):
            q_name = it.get('product_name') or it.get('query_term')
            u_size = it.get('unit_size') or 'N/A'
            qty = it.get('quantity')
            price = it.get('unit_price')
            lt = it.get('line_total')
            st = it.get('match_status')
            print(f"      - [{st.upper()}] Item {item_idx}: {q_name} | {u_size} x {qty} = ₹{lt} (@₹{price})")

        # Brief pause between test calls to respect Gemini API rate limits
        time.sleep(2)

    # Save complete raw benchmark results as JSON
    out_json_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'benchmark_results.json')
    with open(out_json_path, 'w', encoding='utf-8') as f:
        json.dump(all_results, f, ensure_ascii=False, indent=2)

    print("\n" + "=" * 80)
    print(f"BENCHMARK COMPLETE! Full results saved to: {out_json_path}")
    print("=" * 80)

if __name__ == '__main__':
    run_benchmarks()
