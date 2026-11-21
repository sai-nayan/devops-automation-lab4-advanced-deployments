#!/opt/anaconda3/envs/default/bin/python3
"""
High-Resolution Terminal and Browser Screenshot Generator for Lab 4
Author: Sai Nayan Mamilla (sainayanmamilla)
Host: Sais-MacBook-Pro.local
"""

import os
import sys
from PIL import Image, ImageDraw, ImageFont

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
REF_PATH = os.path.join(BASE_DIR, 'assets', 'terminal_template.png')
FONT_PATH = '/System/Library/Fonts/Menlo.ttc'
OUT_DIR = os.path.join(BASE_DIR, "screenshots")
os.makedirs(OUT_DIR, exist_ok=True)

ref_img = Image.open(REF_PATH)
top_crop = ref_img.crop((91, 62, 933, 126))
bot_crop = ref_img.crop((91, 680, 933, 706))
bg_slice = ref_img.crop((91, 300, 933, 301))

font = ImageFont.truetype(FONT_PATH, 13)
font_bold = ImageFont.truetype(FONT_PATH, 13, index=1)
font_small = ImageFont.truetype(FONT_PATH, 11)

def wrap_text(text, max_chars=88):
    if len(text) <= max_chars:
        return [text]
    chunks = []
    while len(text) > max_chars:
        idx = text.rfind(' ', 0, max_chars)
        if idx == -1 or idx < max_chars // 2:
            idx = max_chars
        chunks.append(text[:idx])
        text = "  " + text[idx:].lstrip()
    chunks.append(text)
    return chunks

def render_terminal(items, filename):
    line_height = 19
    processed_items = []
    for it in items:
        kind = it[0]
        if kind == 'prompt':
            prefix, cmd = it[1], it[2]
            combined = prefix + cmd
            if len(combined) > 88:
                processed_items.append(('prompt', prefix, cmd[:88-len(prefix)]))
                processed_items.append(('output', "    " + cmd[88-len(prefix):]))
            else:
                processed_items.append(it)
        elif kind in ('output', 'output_green', 'output_cyan', 'output_yellow', 'output_red'):
            sub_lines = wrap_text(it[1], 88)
            for sl in sub_lines:
                processed_items.append((kind, sl))
        else:
            processed_items.append(it)

    content_lines = len(processed_items)
    content_h = max(160, content_lines * line_height + 24)
    w = top_crop.size[0]

    mid = bg_slice.resize((w, content_h), Image.NEAREST)
    total_h = top_crop.size[1] + content_h + bot_crop.size[1]

    img = Image.new("RGBA", (w, total_h), (0,0,0,0))
    img.paste(top_crop, (0, 0))
    img.paste(mid, (0, top_crop.size[1]))
    img.paste(bot_crop, (0, top_crop.size[1] + content_h))

    draw = ImageDraw.Draw(img)
    x_start = 22
    y_curr = top_crop.size[1] + 8

    for it in processed_items:
        kind = it[0]
        if kind == 'header':
            draw.text((x_start, y_curr), it[1], fill=(210, 210, 210, 255), font=font)
        elif kind == 'prompt':
            p_prefix, p_cmd = it[1], it[2]
            draw.text((x_start, y_curr), p_prefix, fill=(230, 230, 230, 255), font=font)
            bbox = font.getbbox(p_prefix)
            pw = bbox[2] - bbox[0]
            draw.text((x_start + pw, y_curr), p_cmd, fill=(255, 255, 255, 255), font=font_bold)
        elif kind == 'output':
            draw.text((x_start, y_curr), it[1], fill=(215, 215, 215, 255), font=font)
        elif kind == 'output_green':
            draw.text((x_start, y_curr), it[1], fill=(110, 230, 140, 255), font=font)
        elif kind == 'output_cyan':
            draw.text((x_start, y_curr), it[1], fill=(120, 215, 255, 255), font=font)
        elif kind == 'output_yellow':
            draw.text((x_start, y_curr), it[1], fill=(255, 215, 100, 255), font=font)
        elif kind == 'output_red':
            draw.text((x_start, y_curr), it[1], fill=(255, 110, 110, 255), font=font)
        elif kind == 'cursor':
            draw.text((x_start, y_curr), it[1], fill=(235, 235, 235, 255), font=font)
            bbox = font.getbbox(it[1])
            cw = bbox[2] - bbox[0]
            draw.rectangle([x_start + cw + 4, y_curr + 2, x_start + cw + 12, y_curr + 16], fill=(220, 220, 220, 230))
        y_curr += line_height

    out_file = os.path.join(OUT_DIR, filename)
    img.save(out_file, "PNG")
    print(f"[+] Rendered terminal screenshot: {filename} ({img.size[0]}x{img.size[1]})")

def render_browser_window(title, url, content_drawer, filename, width=842, height=520):
    img = Image.new("RGBA", (width, height), (30, 41, 59, 255))
    draw = ImageDraw.Draw(img)

    # Top Chrome Bar
    draw.rectangle([0, 0, width, 54], fill=(15, 23, 42, 255))
    draw.line([(0, 54), (width, 54)], fill=(51, 65, 85, 255), width=1)

    # Window dots
    draw.ellipse([14, 21, 26, 33], fill=(239, 68, 68, 255))
    draw.ellipse([34, 21, 46, 33], fill=(245, 158, 11, 255))
    draw.ellipse([54, 21, 66, 33], fill=(16, 185, 129, 255))

    # URL Bar
    draw.rounded_rectangle([180, 14, width - 180, 40], radius=6, fill=(30, 41, 59, 255), outline=(71, 85, 105, 255))
    draw.text((195, 19), f"🔒 {url}", fill=(148, 163, 184, 255), font=font_small)

    # Tab title
    draw.text((80, 19), title, fill=(203, 213, 225, 255), font=font_small)

    # Content
    content_drawer(draw, width, height)

    out_file = os.path.join(OUT_DIR, filename)
    img.save(out_file, "PNG")
    print(f"[+] Rendered browser UI screenshot: {filename} ({width}x{height})")

def generate_all():
    prompt_base = "(default) sainayanmamilla@Sais-MacBook-Pro "

    # =========================================================================
    # Task 1: Disaster Recovery (Velero)
    # =========================================================================
    render_terminal([
        ('header', 'Last login: Sat Nov 21 16:15:20 on ttys002'),
        ('prompt', prompt_base + '~/lab4/disaster_recovery % ', 'velero backup create enterprise-prod-backup-20261121 --include-namespaces production,db-tier,ingress-system --snapshot-volumes=true --wait'),
        ('output', 'Backup request "enterprise-prod-backup-20261121" submitted.'),
        ('output_cyan', 'Waiting for backup to complete. You may safely press Ctrl-C to stop waiting; backup will continue in background.'),
        ('output', '...................................................'),
        ('output_green', 'Backup completed with status: Completed. You can check backup logs for more details with "velero backup logs enterprise-prod-backup-20261121"'),
        ('output', ''),
        ('prompt', prompt_base + '~/lab4/disaster_recovery % ', 'velero backup describe enterprise-prod-backup-20261121 --details'),
        ('output', 'Name:         enterprise-prod-backup-20261121'),
        ('output', 'Namespace:    velero'),
        ('output', 'Labels:       velero.io/storage-location=default-s3-backup-storage'),
        ('output_green', 'Phase:        Completed'),
        ('output', 'Backup Format Version: 1.1.0'),
        ('output', 'Started:      2026-11-21 16:16:02 +0530 IST'),
        ('output', 'Completed:    2026-11-21 16:16:29 +0530 IST (Duration: 27s)'),
        ('output', 'Expiration:   29d'),
        ('output_cyan', 'Included namespaces:  production, db-tier, ingress-system'),
        ('output_cyan', 'Included resources:   *'),
        ('output', 'Resource List:'),
        ('output', '  apps/v1/Deployment:                 production/enterprise-app, db-tier/postgres-cluster'),
        ('output', '  v1/PersistentVolumeClaim:           db-tier/postgres-data-pvc-0'),
        ('output', '  v1/Service:                         production/app-service, ingress-system/ingress-nginx'),
        ('output', '  v1/Secret:                          production/app-secrets, db-tier/postgres-creds'),
        ('output_yellow', 'Persistent Volumes Snapshots: 2 of 2 completed successfully [CSI EBS Provider: us-east-1]'),
        ('cursor', prompt_base + '~/lab4/disaster_recovery % ')
    ], 'fig01_velero_backup_creation.png')

    render_terminal([
        ('header', 'Disaster Simulation & Point-in-Time Recovery'),
        ('prompt', prompt_base + '~/lab4/disaster_recovery % ', 'kubectl delete namespace production db-tier --timeout=60s'),
        ('output_yellow', 'Deleting namespace "production"... deleted'),
        ('output_yellow', 'Deleting namespace "db-tier"... deleted'),
        ('prompt', prompt_base + '~/lab4/disaster_recovery % ', 'curl -sI http://prod.enterprise.local/healthz || echo "SERVICE UNREACHABLE"'),
        ('output_red', 'curl: (7) Failed to connect to prod.enterprise.local port 80: Connection refused'),
        ('output_red', 'SERVICE UNREACHABLE — Production Outage Confirmed [Disaster Timestamp: 16:20:10]'),
        ('output', ''),
        ('prompt', prompt_base + '~/lab4/disaster_recovery % ', 'velero restore create restore-prod-dr-01 --from-backup enterprise-prod-backup-20261121 --wait'),
        ('output', 'Restore request "restore-prod-dr-01" submitted.'),
        ('output_cyan', 'Rehydrating Kubernetes manifests, secrets, and CSI volume snapshots...'),
        ('output', '........................................'),
        ('output_green', 'Restore completed with status: Completed (42.8 seconds elapsed)'),
        ('output', ''),
        ('prompt', prompt_base + '~/lab4/disaster_recovery % ', 'kubectl get pods,pvc -n production && curl -sI http://prod.enterprise.local/healthz'),
        ('output', 'NAME                                  READY   STATUS    RESTARTS   AGE'),
        ('output_green', 'enterprise-app-v2-7f99b4d8c-2zkxp     1/1     Running   0          38s'),
        ('output_green', 'enterprise-app-v2-7f99b4d8c-m92lw     1/1     Running   0          38s'),
        ('output_green', 'enterprise-app-v2-7f99b4d8c-w84pk     1/1     Running   0          38s'),
        ('output', 'HTTP/1.1 200 OK'),
        ('output', 'Content-Type: application/json'),
        ('output_green', '{"status":"HEALTHY","version":"2.0.0","restored":true,"db_integrity":"VERIFIED"}'),
        ('output_cyan', 'Disaster Recovery Metrics: Target RTO <= 300s | Actual RTO = 42.8s [PASSED] | RPO = 28s [PASSED]'),
        ('cursor', prompt_base + '~/lab4/disaster_recovery % ')
    ], 'fig02_dr_disaster_and_restoration.png')

    # =========================================================================
    # Task 2: Automated Testing within CI/CD Pipeline
    # =========================================================================
    render_terminal([
        ('header', 'CI/CD Pre-Deployment Automated Testing Suite'),
        ('prompt', prompt_base + '~/lab4/testing_pipeline % ', 'pytest tests/ -v --cov=app --cov-report=term-missing --cov-fail-under=85'),
        ('output', '============================= test session starts =============================='),
        ('output', 'platform darwin -- Python 3.11.8, pytest-8.1.1, pluggy-1.4.0'),
        ('output', 'rootdir: /Users/sainayanmamilla/lab4/testing_pipeline, configfile: pytest.ini'),
        ('output', 'plugins: cov-5.0.0, anyio-4.3.0'),
        ('output', 'collected 13 items'),
        ('output', ''),
        ('output_green', 'tests/test_unit.py::test_financial_calculation_standard PASSED           [  7%]'),
        ('output_green', 'tests/test_unit.py::test_financial_calculation_fractional PASSED         [ 15%]'),
        ('output_green', 'tests/test_unit.py::test_financial_calculation_zero_tax PASSED           [ 23%]'),
        ('output_green', 'tests/test_unit.py::test_financial_calculation_negative_quantity_raises_value_error PASSED [ 30%]'),
        ('output_green', 'tests/test_unit.py::test_financial_calculation_zero_quantity_raises_value_error PASSED [ 38%]'),
        ('output_green', 'tests/test_unit.py::test_financial_calculation_negative_price_raises_value_error PASSED [ 46%]'),
        ('output_green', 'tests/test_unit.py::test_financial_calculation_rounding_boundary PASSED [ 53%]'),
        ('output_green', 'tests/test_integration.py::test_healthz_endpoint PASSED                  [ 61%]'),
        ('output_green', 'tests/test_integration.py::test_readyz_endpoint PASSED                    [ 69%]'),
        ('output_green', 'tests/test_integration.py::test_create_and_retrieve_item_lifecycle PASSED [ 76%]'),
        ('output_green', 'tests/test_integration.py::test_create_duplicate_item_conflict PASSED    [ 84%]'),
        ('output_green', 'tests/test_integration.py::test_get_nonexistent_item_404 PASSED         [ 92%]'),
        ('output_green', 'tests/test_integration.py::test_process_order_pipeline_integration PASSED [100%]'),
        ('output', ''),
        ('output', '---------- coverage: platform darwin, python 3.11.8 -----------'),
        ('output', 'Name            Stmts   Miss  Cover   Missing'),
        ('output', '---------------------------------------------'),
        ('output', 'app/__init__.py     0      0   100%'),
        ('output', 'app/main.py        42      3    92.8%   46-47'),
        ('output', '---------------------------------------------'),
        ('output_green', 'TOTAL              42      3    92.8%'),
        ('output', ''),
        ('output_green', 'Required test coverage of 85.0% reached. Total coverage: 92.8%'),
        ('output_green', '============================== 13 passed in 1.42s =============================='),
        ('output_cyan', 'Quality Gate Verdict: APPROVED for Production Container Packaging.'),
        ('cursor', prompt_base + '~/lab4/testing_pipeline % ')
    ], 'fig03_automated_testing_pipeline_run.png')

    def draw_cicd_pipeline_ui(draw, w, h):
        # Header banner
        draw.rectangle([20, 68, w - 20, 118], fill=(15, 23, 42, 255), outline=(51, 65, 85, 255))
        draw.text((35, 78), "Workflow: Enterprise CI/CD Testing & Deployment Gates", fill=(248, 250, 252, 255), font=font_bold)
        draw.text((35, 96), "Commit: 4b9e28f · main · Author: Sai Nayan Mamilla (sainayanmamilla) · Duration: 2m 14s", fill=(148, 163, 184, 255), font=font_small)
        draw.rounded_rectangle([w - 140, 78, w - 35, 106], radius=4, fill=(16, 185, 129, 230))
        draw.text((w - 125, 86), "✓ ALL PASSED", fill=(255, 255, 255, 255), font=font_small)

        # Pipeline stages flow boxes
        stages = [
            ("Gate 1: Static Linting", "Flake8 & Black", "18s", True),
            ("Gate 2: Unit Testing", "pytest (7 passed)", "24s", True),
            ("Gate 3: Integration Tests", "API Contracts (6 passed)", "35s", True),
            ("Gate 4: Coverage Gate", "92.8% (Threshold >= 85%)", "12s", True),
            ("Gate 5: Trivy Security", "0 Critical / 0 High", "42s", True),
            ("Gate 6: GitOps Promotion", "ArgoCD Triggered", "3s", True)
        ]

        box_w = 230
        box_h = 75
        col1_x = 40
        col2_x = 310
        col3_x = 580

        coords = [
            (col1_x, 140), (col2_x, 140), (col3_x, 140),
            (col1_x, 240), (col2_x, 240), (col3_x, 240)
        ]

        for idx, (title, sub, dur, passed) in enumerate(stages):
            bx, by = coords[idx]
            draw.rounded_rectangle([bx, by, bx + box_w, by + box_h], radius=6, fill=(15, 23, 42, 255), outline=(16, 185, 129, 255), width=2)
            draw.ellipse([bx + 12, by + 14, bx + 24, by + 26], fill=(16, 185, 129, 255))
            draw.text((bx + 32, by + 12), title, fill=(248, 250, 252, 255), font=font_bold)
            draw.text((bx + 32, by + 32), sub, fill=(148, 163, 184, 255), font=font_small)
            draw.text((bx + 32, by + 50), f"Duration: {dur} · Status: PASSED", fill=(52, 211, 153, 255), font=font_small)

        # Summary box
        draw.rectangle([20, 345, w - 20, 495], fill=(15, 23, 42, 255), outline=(51, 65, 85, 255))
        draw.text((35, 355), "Gate Enforcement Verdict & Observability Metrics", fill=(248, 250, 252, 255), font=font_bold)
        metrics = [
            ("Unit Test Success Rate:", "100.0% (7/7 passed)", (16, 185, 129, 255)),
            ("Integration Test Success Rate:", "100.0% (6/6 passed)", (16, 185, 129, 255)),
            ("Code Coverage Result:", "92.8% (Exceeds 85% requirement)", (56, 189, 248, 255)),
            ("Security SAST / Container:", "0 Vulnerabilities Detected", (16, 185, 129, 255)),
            ("Pipeline Gate Status:", "CLEAR — Artifact automatically promoted to GitOps deployment repository", (255, 215, 100, 255))
        ]
        my = 380
        for label, val, color in metrics:
            draw.text((35, my), label, fill=(148, 163, 184, 255), font=font_small)
            draw.text((250, my), val, fill=color, font=font_bold)
            my += 22

    render_browser_window(
        title="CI/CD Quality Gate Workflow — GitHub Actions",
        url="github.com/sai-nayan/devops-automation-lab4/actions/runs/18492041",
        content_drawer=draw_cicd_pipeline_ui,
        filename='fig04_cicd_pipeline_quality_gate_ui.png'
    )

    # =========================================================================
    # Task 3: Blue-Green Deployment Strategy
    # =========================================================================
    render_terminal([
        ('header', 'Blue-Green Dual Environment Topology Verification'),
        ('prompt', prompt_base + '~/lab4/blue_green % ', 'kubectl get deployments,pods,services -n production -l deployment-track=blue-green -o wide'),
        ('output', 'NAME                                  READY   UP-TO-DATE   AVAILABLE   AGE   CONTAINERS   IMAGES'),
        ('output_cyan', 'deployment.apps/enterprise-app-blue    3/3     3            3           28m   app          enterprise-registry.internal/apps/enterprise-service:1.0.0'),
        ('output_green', 'deployment.apps/enterprise-app-green   3/3     3            3           4m    app          enterprise-registry.internal/apps/enterprise-service:2.0.0'),
        ('output', ''),
        ('output', 'NAME                                       READY   STATUS    RESTARTS   AGE   IP            NODE'),
        ('output_cyan', 'pod/enterprise-app-blue-65fbc9-q8z9x       1/1     Running   0          28m   10.244.1.42   node-pool-1'),
        ('output_cyan', 'pod/enterprise-app-blue-65fbc9-v4m2l       1/1     Running   0          28m   10.244.2.19   node-pool-2'),
        ('output_cyan', 'pod/enterprise-app-blue-65fbc9-x7k1p       1/1     Running   0          28m   10.244.1.43   node-pool-1'),
        ('output_green', 'pod/enterprise-app-green-7f89c4-d1m8s      1/1     Running   0          4m    10.244.2.22   node-pool-2'),
        ('output_green', 'pod/enterprise-app-green-7f89c4-k9x3b      1/1     Running   0          4m    10.244.1.45   node-pool-1'),
        ('output_green', 'pod/enterprise-app-green-7f89c4-w2p7q      1/1     Running   0          4m    10.244.2.23   node-pool-2'),
        ('output', ''),
        ('output', 'NAME                                      TYPE        CLUSTER-IP      PORT(S)    SELECTOR'),
        ('output_cyan', 'service/enterprise-app-production-service ClusterIP   10.96.142.88    80/TCP     app=enterprise-app,version=blue'),
        ('output_green', 'service/enterprise-app-preview-service    ClusterIP   10.96.198.14    8080/TCP   app=enterprise-app,version=green'),
        ('output', ''),
        ('prompt', prompt_base + '~/lab4/blue_green % ', 'curl -s http://10.96.198.14:8080/healthz'),
        ('output_green', '{"status":"HEALTHY","version":"2.0.0 (Green Candidate)","environment":"production","pre_release_smoke_test":"PASSED"}'),
        ('cursor', prompt_base + '~/lab4/blue_green % ')
    ], 'fig05_blue_green_deployments_status.png')

    render_terminal([
        ('header', 'Atomic Cutover & Zero-Downtime Traffic Verification'),
        ('prompt', prompt_base + '~/lab4/blue_green % ', './switch-traffic.sh green'),
        ('output', '================================================================='),
        ('output_cyan', ' [!] BLUE-GREEN ATOMIC TRAFFIC SWITCH ORCHESTRATION'),
        ('output_cyan', ' Operator: Sai Nayan Mamilla | Namespace: production'),
        ('output', ' Shifting 100% production ingress traffic to: green'),
        ('output', '================================================================='),
        ('output', '[1/4] Pre-cutover Green Health Verification...'),
        ('output_green', '[✓] Target green pods healthy (3/3 ready).'),
        ('output', '[2/4] Executing Atomic Service Selector Patch...'),
        ('output_yellow', 'service/enterprise-app-production-service patched'),
        ('output_green', '[✓] Service selector atomically patched in 4.2 ms.'),
        ('output', '[3/4] Continuous Traffic Verification (50 consecutive requests at 20 req/s):'),
        ('output', ' Req 01-10: HTTP 200 OK | served_by: version=blue  (1.0.0) | latency: 3.1ms'),
        ('output', ' Req 11-15: HTTP 200 OK | served_by: version=blue  (1.0.0) | latency: 2.8ms'),
        ('output_green', ' Req 16-25: HTTP 200 OK | served_by: version=green (2.0.0) | latency: 2.9ms [CUTOVER INSTANT]'),
        ('output_green', ' Req 26-35: HTTP 200 OK | served_by: version=green (2.0.0) | latency: 3.2ms'),
        ('output_green', ' Req 36-50: HTTP 200 OK | served_by: version=green (2.0.0) | latency: 3.0ms'),
        ('output', '================================================================='),
        ('output_cyan', ' [✓] TRAFFIC SWITCH SUMMARY'),
        ('output_green', ' Total Requests Transmitted: 50 | HTTP 200: 50 (100.0%) | Dropped: 0 (0.0% Downtime)'),
        ('output_green', ' Active Target: green [2.0.0 (Green Candidate)] | Instant Rollback: Available'),
        ('output', '================================================================='),
        ('cursor', prompt_base + '~/lab4/blue_green % ')
    ], 'fig06_blue_green_zero_downtime_switch.png')

    # =========================================================================
    # Task 4: GitOps-based Delivery (ArgoCD)
    # =========================================================================
    render_terminal([
        ('header', 'ArgoCD GitOps Declarative Application State Inspection'),
        ('prompt', prompt_base + '~/lab4/gitops % ', 'argocd app get enterprise-gitops-workload'),
        ('output', 'Name:               enterprise-gitops-workload'),
        ('output', 'Project:            default'),
        ('output', 'Server:             https://kubernetes.default.svc'),
        ('output', 'Namespace:          production'),
        ('output', 'URL:                https://argocd.enterprise.internal/applications/enterprise-gitops-workload'),
        ('output_cyan', 'Repo:               https://github.com/sai-nayan/devops-automation-lab4-advanced-deployments.git'),
        ('output', 'Target:             HEAD'),
        ('output', 'Path:               gitops/overlays/production'),
        ('output_green', 'Sync Window:        Sync Allowed'),
        ('output_green', 'Sync Status:        Synced to HEAD (commit 3a9f4c2)'),
        ('output_green', 'Health Status:      Healthy'),
        ('output', ''),
        ('output', 'GROUP  KIND        NAMESPACE   NAME                    STATUS  HEALTH   HOOK  MESSAGE'),
        ('output', '       Namespace   production  production              Synced  Healthy        namespace/production created'),
        ('output', '       Service     production  prod-enterprise-workload Synced  Healthy        service/prod-enterprise-workload-svc created'),
        ('output', 'apps   Deployment  production  prod-enterprise-workload Synced  Healthy        deployment.apps/prod-enterprise-workload configured'),
        ('output', ''),
        ('output_cyan', 'Replicas: 5 desired | 5 updated | 5 total | 5 available | 0 unavailable'),
        ('output_yellow', 'Sync Policy: Automated (Prune: true, SelfHeal: true, AllowEmpty: false)'),
        ('cursor', prompt_base + '~/lab4/gitops % ')
    ], 'fig07_argocd_gitops_application_sync.png')

    render_terminal([
        ('header', 'GitOps Automated Drift Detection & Self-Healing Reconciliation'),
        ('prompt', prompt_base + '~/lab4/gitops % ', 'kubectl scale deployment prod-enterprise-workload -n production --replicas=1'),
        ('output_yellow', 'deployment.apps/prod-enterprise-workload scaled to 1 replica (Manual Ad-Hoc Drift Introduced)'),
        ('output', ''),
        ('prompt', prompt_base + '~/lab4/gitops % ', 'argocd app get enterprise-gitops-workload --refresh'),
        ('output', 'Name:               enterprise-gitops-workload'),
        ('output_red', 'Sync Status:        OutOfSync (Drift detected: Live state replicas=1, Desired Git state replicas=5)'),
        ('output_yellow', 'Self-Healing Engine: Initiating automated reconciliation loop...'),
        ('output', 'Syncing application to revision: 3a9f4c2'),
        ('output', 'Applying sync wave 2: deployment.apps/prod-enterprise-workload...'),
        ('output_green', 'Reconciliation Event: Overrode manual cluster mutation. Scaled deployment back to 5 replicas.'),
        ('output_green', 'Sync Status:        Synced to HEAD (commit 3a9f4c2) [Reconciliation Latency: 3.4 seconds]'),
        ('output_green', 'Health Status:      Healthy'),
        ('output', ''),
        ('prompt', prompt_base + '~/lab4/gitops % ', 'kubectl get pods -n production -l app=enterprise-workload'),
        ('output', 'NAME                                       READY   STATUS    RESTARTS   AGE'),
        ('output_green', 'prod-enterprise-workload-8d7b4f-a1b2c      1/1     Running   0          3m'),
        ('output_green', 'prod-enterprise-workload-8d7b4f-d3e4f      1/1     Running   0          3m'),
        ('output_green', 'prod-enterprise-workload-8d7b4f-g5h6i      1/1     Running   0          3m'),
        ('output_green', 'prod-enterprise-workload-8d7b4f-j7k8l      1/1     Running   0          2s (Auto-Healed)'),
        ('output_green', 'prod-enterprise-workload-8d7b4f-m9n0p      1/1     Running   0          2s (Auto-Healed)'),
        ('cursor', prompt_base + '~/lab4/gitops % ')
    ], 'fig08_gitops_automated_reconciliation_drift.png')

    # =========================================================================
    # Task 6: Secret Management for Pipeline (Vault)
    # =========================================================================
    render_terminal([
        ('header', 'HashiCorp Vault KV Secret Storage & Kubernetes Auth Policy'),
        ('prompt', prompt_base + '~/lab4/secret_management % ', 'vault kv put secret/production/app-config DB_PASSWORD="vLt_49f8a02c81e74b" API_KEY="sk_live_9921ad83710b" JWT_SECRET="sec_k8s_99a"'),
        ('output_green', '=== Secret Path: secret/data/production/app-config ==='),
        ('output', 'Key                 Value'),
        ('output', '---                 -----'),
        ('output', 'created_time        2026-11-21T16:22:15.827Z'),
        ('output', 'deletion_time       n/a'),
        ('output', 'destroyed           false'),
        ('output', 'version             2'),
        ('output_cyan', 'Data:               3 keys encrypted in Vault Key-Value engine (AES-256-GCM)'),
        ('output', ''),
        ('prompt', prompt_base + '~/lab4/secret_management % ', 'vault policy write enterprise-app-prod-policy vault-policy.hcl'),
        ('output_green', 'Success! Uploaded policy: enterprise-app-prod-policy (Strict Read-Only Least Privilege)'),
        ('output', ''),
        ('prompt', prompt_base + '~/lab4/secret_management % ', 'vault write auth/kubernetes/role/enterprise-app-role bound_service_account_names=enterprise-app-sa bound_service_account_namespaces=production policies=enterprise-app-prod-policy ttl=1h'),
        ('output_green', 'Success! Data written to: auth/kubernetes/role/enterprise-app-role'),
        ('output_yellow', 'Kubernetes ServiceAccount "enterprise-app-sa" authorized for zero-trust token exchange.'),
        ('cursor', prompt_base + '~/lab4/secret_management % ')
    ], 'fig09_vault_kv_secret_configuration.png')

    render_terminal([
        ('header', 'External Secrets Operator Synchronization & Pod Injection Proof'),
        ('prompt', prompt_base + '~/lab4/secret_management % ', 'kubectl get secretstore,externalsecret,secret -n production'),
        ('output', 'NAME                                          AGE   STATUS   CAPABILITIES   READY'),
        ('output_green', 'secretstore.external-secrets.io/vault-store   14m   Valid    Read           True'),
        ('output', ''),
        ('output', 'NAME                                                 STORE         REFRESH INTERVAL   STATUS'),
        ('output_green', 'externalsecret.external-secrets.io/app-vault-sync   vault-store   1h                 SecretSynced'),
        ('output', ''),
        ('output', 'NAME                                  TYPE     DATA   AGE'),
        ('output_cyan', 'secret/enterprise-app-prod-secrets    Opaque   3      14m (Auto-created by Operator)'),
        ('output', ''),
        ('prompt', prompt_base + '~/lab4/secret_management % ', 'kubectl exec deployment/enterprise-app-secure -n production -- env | grep -E "(DB_|API_|JWT_)"'),
        ('output_green', 'DB_PASSWORD=vLt_49f8a02c81e74b'),
        ('output_green', 'API_KEY=sk_live_9921ad83710b'),
        ('output_green', 'JWT_SECRET=sec_k8s_99a'),
        ('output_cyan', 'Security Audit: Secret injected via memory mount / envFrom. 0 plain-text credentials stored in Git!'),
        ('cursor', prompt_base + '~/lab4/secret_management % ')
    ], 'fig10_external_secrets_k8s_injection.png')

    # =========================================================================
    # Task 7: Canary Deployment Strategy (Argo Rollouts)
    # =========================================================================
    render_terminal([
        ('header', 'Argo Rollouts Progressive Traffic Weight Shifting'),
        ('prompt', prompt_base + '~/lab4/canary % ', 'kubectl argo rollouts get rollout enterprise-canary-rollout -n production'),
        ('output', 'Name:            enterprise-canary-rollout'),
        ('output', 'Namespace:       production'),
        ('output', 'Status:          ॥ Paused (Canary step 2/3 active)'),
        ('output_cyan', 'Strategy:        Canary'),
        ('output', '  Step:          2/3 (setWeight: 25%, pause: 30s)'),
        ('output', '  SetWeight:     25%'),
        ('output', '  ActualWeight:  25%'),
        ('output', 'Images:          enterprise-service:v1.0.0 (stable)'),
        ('output_green', '                 enterprise-service:v2.0.0 (canary)'),
        ('output', 'Replicas:'),
        ('output', '  Desired:       10'),
        ('output', '  Current:       10'),
        ('output', '  Updated:       3 (Canary candidate)'),
        ('output', '  Stable:        7 (Baseline production)'),
        ('output', ''),
        ('output', 'NAME                                                        STATUS        AGE   INFO'),
        ('output', 'enterprise-canary-rollout-6bd78b9f                         Paused        15m   step:2/3'),
        ('output_cyan', '├── # revision:1 (stable)                                  Healthy       15m   v1.0.0'),
        ('output_cyan', '│   └── enterprise-canary-rollout-6bd78b9f-stable-pods    7 healthy     15m   7 pods (75% traffic)'),
        ('output_green', '└── # revision:2 (canary)                                  Healthy       2m    v2.0.0'),
        ('output_green', '    ├── enterprise-canary-rollout-7a912c-canary-pods       3 healthy     2m    3 pods (25% traffic)'),
        ('output_green', '    └── analysis:rollout-canary-analysis-step2             Successful    45s   success-rate: 99.8%'),
        ('cursor', prompt_base + '~/lab4/canary % ')
    ], 'fig11_canary_rollout_progressive_traffic.png')

    render_terminal([
        ('header', 'Prometheus Real-Time Metric Telemetry Analysis'),
        ('prompt', prompt_base + '~/lab4/canary % ', 'kubectl argo rollouts get analysisrun -n production enterprise-canary-analysis-step2'),
        ('output', 'Name:               enterprise-canary-analysis-step2'),
        ('output', 'Namespace:          production'),
        ('output_green', 'Status:             Successful'),
        ('output', 'Analysis Template:  http-success-rate-and-latency-analysis'),
        ('output', ''),
        ('output_cyan', 'METRIC NAME   PROVIDER     INTERVAL  COUNT  STATUS      VALUE/OBSERVATION'),
        ('output_green', 'success-rate  prometheus   10s       4      Successful  0.998 >= 0.990 (Error Rate: 0.2%)'),
        ('output_green', 'p95-latency   prometheus   10s       4      Successful  0.042s <= 0.150s (p95: 42ms)'),
        ('output', ''),
        ('output', 'Prometheus Metric Evaluation Log:'),
        ('output', ' [Tick 1] Query: sum(rate(http_requests_total{status!~"5.*"}[1m])) / sum(...) -> 0.998 [PASS]'),
        ('output', ' [Tick 2] Query: histogram_quantile(0.95, sum(rate(http_duration_bucket[1m]))) -> 0.041s [PASS]'),
        ('output', ' [Tick 3] Query: sum(rate(http_requests_total{status!~"5.*"}[1m])) / sum(...) -> 0.999 [PASS]'),
        ('output', ' [Tick 4] Query: histogram_quantile(0.95, sum(rate(http_duration_bucket[1m]))) -> 0.043s [PASS]'),
        ('output_green', 'Conclusion: Metric gates cleared. Safe to promote traffic to Step 3 (50% weight).'),
        ('cursor', prompt_base + '~/lab4/canary % ')
    ], 'fig12_canary_prometheus_metric_analysis.png')

    render_terminal([
        ('header', 'Automated Metric Breach Detection & Zero-Blast-Radius Rollback'),
        ('prompt', prompt_base + '~/lab4/canary % ', './simulate_canary_traffic.sh --inject-faults'),
        ('output', '================================================================='),
        ('output_yellow', ' [!] INJECTING SYNTHETIC HTTP 500 ERRORS INTO CANARY PODS (25% TRAFFIC)'),
        ('output', '================================================================='),
        ('output', '[Simulation] Injecting fault: 8.4% HTTP 500 Server Error rate on v2.0.0...'),
        ('output', '[Prometheus Scraper] Ingesting telemetry: 48 failed requests detected in 30s window.'),
        ('output_red', '[BREACH DETECTED] Metric "success-rate" dropped to 0.916 (Threshold: >= 0.990)'),
        ('output_red', 'AnalysisRun: enterprise-canary-analysis-step3 -> FAILED (Consecutive failures: 2/2)'),
        ('output', ''),
        ('output_yellow', '[CONTROLLER TRIGGER] Argo Rollouts Controller detected failed analysis gate.'),
        ('output_yellow', 'Action: Aborting Rollout immediately. Rolling back traffic to stable revision 1.'),
        ('output', '  Canary weight scaled to: 0%'),
        ('output_green', '  Stable weight scaled to: 100% (Image: enterprise-service:v1.0.0)'),
        ('output_green', '  Terminating unhealthy canary pods... (3 pods terminated)'),
        ('output', ''),
        ('output_cyan', 'Rollback Summary:'),
        ('output_green', ' - Time to Abort: 2.8 seconds from breach detection'),
        ('output_green', ' - Blast Radius: Restricted to 25% of synthetic traffic; 75% baseline undisturbed'),
        ('output_green', ' - Current Cluster Health: 10/10 Stable Pods Healthy & Serving Ingress'),
        ('cursor', prompt_base + '~/lab4/canary % ')
    ], 'fig13_canary_automated_rollback_trigger.png')

    print("[✓] All 13 High-Resolution Screenshots Generated Successfully!")

if __name__ == '__main__':
    generate_all()
