#!/opt/anaconda3/envs/default/bin/python3
"""
Automated Upload Script for Zosima.ai Lab 4 Assessment
Student: Sai Nayan Mamilla (sainayanmamilla)
Host: Sais-MacBook-Pro.local
"""

import os
import sys
import time
import base64
import subprocess
import json

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PDF_DIR = os.path.join(BASE_DIR, "individual_task_pdfs")

FILES_TO_UPLOAD = [
    {
        "index": 0,
        "question": "Question 1: Design and demonstrate a disaster recovery mechanism",
        "filename": "Task_01_Disaster_Recovery_Mechanism_Velero.pdf",
        "path": os.path.join(PDF_DIR, "Task_01_Disaster_Recovery_Mechanism_Velero.pdf")
    },
    {
        "index": 1,
        "question": "Question 2: Implement automated testing within a CI/CD pipeline",
        "filename": "Task_02_Automated_Testing_CICD_Pipeline.pdf",
        "path": os.path.join(PDF_DIR, "Task_02_Automated_Testing_CICD_Pipeline.pdf")
    },
    {
        "index": 2,
        "question": "Question 3: Implement a Blue-Green deployment strategy",
        "filename": "Task_03_Blue_Green_Deployment_Strategy.pdf",
        "path": os.path.join(PDF_DIR, "Task_03_Blue_Green_Deployment_Strategy.pdf")
    },
    {
        "index": 3,
        "question": "Question 4: Implement GitOps-based delivery",
        "filename": "Task_04_GitOps_Based_Delivery_ArgoCD.pdf",
        "path": os.path.join(PDF_DIR, "Task_04_GitOps_Based_Delivery_ArgoCD.pdf")
    },
    {
        "index": 4,
        "question": "Question 5: Prepare an advanced deployment strategies report",
        "filename": "Task_05_Advanced_Deployment_Strategies_Report.pdf",
        "path": os.path.join(PDF_DIR, "Task_05_Advanced_Deployment_Strategies_Report.pdf")
    },
    {
        "index": 5,
        "question": "Question 6: Implement secret management for the pipeline",
        "filename": "Task_06_Secret_Management_Vault_Pipeline.pdf",
        "path": os.path.join(PDF_DIR, "Task_06_Secret_Management_Vault_Pipeline.pdf")
    },
    {
        "index": 6,
        "question": "Question 7: Implement a Canary deployment strategy",
        "filename": "Task_07_Canary_Deployment_Strategy_ArgoRollouts.pdf",
        "path": os.path.join(PDF_DIR, "Task_07_Canary_Deployment_Strategy_ArgoRollouts.pdf")
    }
]

def upload_file(idx, fname, fpath):
    if not os.path.exists(fpath):
        print(f"[!] File not found: {fpath}")
        return False

    with open(fpath, "rb") as f:
        b64_str = base64.b64encode(f.read()).decode("ascii")

    print(f"[*] Uploading Q{idx+1}: {fname} ({os.path.getsize(fpath):,} bytes)...")

    inject_js = f"""(function() {{
        try {{
            const b64 = {json.dumps(b64_str)};
            const bin = atob(b64);
            const bytes = new Uint8Array(bin.length);
            for (let i = 0; i < bin.length; i++) bytes[i] = bin.charCodeAt(i);
            const file = new File([bytes], {json.dumps(fname)}, {{ type: 'application/pdf' }});
            const inps = document.querySelectorAll('input[type=file]');
            if (!inps[{idx}]) return 'ERROR: input not found';
            const dt = new DataTransfer();
            dt.items.add(file);
            inps[{idx}].files = dt.files;
            inps[{idx}].dispatchEvent(new Event('change', {{ bubbles: true }}));
            return 'OK: ' + file.name + ' (' + file.size + ' bytes)';
        }} catch(e) {{
            return 'ERROR: ' + e.message;
        }}
    }})()"""

    jxa = f"""
    const Chrome = Application('Google Chrome');
    let targetTab = null;
    for (const w of Chrome.windows()) {{
        for (const t of w.tabs()) {{
            if (t.url().includes('lab-assessment')) {{
                targetTab = t;
                break;
            }}
        }}
        if (targetTab) break;
    }}

    if (!targetTab) {{
        'ERROR_NO_ZOSIMA_TAB';
    }} else {{
        targetTab.execute({{ javascript: {json.dumps(inject_js)} }});
    }}
    """

    proc = subprocess.run(['osascript', '-l', 'JavaScript'], input=jxa, text=True, capture_output=True)
    out = proc.stdout.strip()
    print(f"    -> Response: {out}")
    return "OK:" in out

def check_portal_status():
    jxa = """
    const Chrome = Application('Google Chrome');
    let targetTab = null;
    for (const w of Chrome.windows()) {
        for (const t of w.tabs()) {
            if (t.url().includes('lab-assessment')) {
                targetTab = t;
                break;
            }
        }
        if (targetTab) break;
    }

    if (!targetTab) {
        JSON.stringify([]);
    } else {
        const inspectJs = `(function() {
            const results = [];
            const text = document.body.innerText;
            for (let i = 1; i <= 7; i++) {
                const match = text.match(new RegExp("Task_0" + i + "[^\\\\s]+\\\\.pdf"));
                results.push({
                    q: i,
                    fileName: match ? match[0] : ("Task_0" + i + ".pdf"),
                    uploaded: text.includes("Task_0" + i) && text.includes("Uploaded")
                });
            }
            return JSON.stringify(results);
        })()`;
        targetTab.execute({ javascript: inspectJs });
    }
    """
    proc = subprocess.run(['osascript', '-l', 'JavaScript'], input=jxa, text=True, capture_output=True)
    out = proc.stdout.strip()
    try:
        data = json.loads(out)
        return data if isinstance(data, list) else []
    except Exception as e:
        print(f"Status check parsing error: {e}, raw: {out}")
        return []

def main():
    print("================================================================")
    print(" 🚀 AUTOMATED FILE UPLOADER FOR ZOSIMA.AI LAB 4 ASSESSMENT")
    print(" Candidate: Sai Nayan Mamilla | Host: Sais-MacBook-Pro.local")
    print("================================================================")

    for item in FILES_TO_UPLOAD:
        upload_file(item["index"], item["filename"], item["path"])
        time.sleep(3.5) # Wait for network ingestion / Cloudflare R2 upload

    print("\n[*] Waiting 5 seconds for portal state consolidation...")
    time.sleep(5.0)

    print("\n[*] Checking uploaded status across all questions:")
    status = check_portal_status()
    for s in status:
        idx = s.get("idx")
        fname = s.get("matchedFile") or "Pending/Detecting"
        badge = "✅ CONFIRMED" if s.get("hasPdf") else "⏳ PENDING"
        print(f"  Q{idx+1}: {badge} -> {fname}")

if __name__ == '__main__':
    main()
